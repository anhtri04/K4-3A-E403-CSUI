"""BuildMate Discord gateway (thin). Policy lives in app/opencode_bridge/course_kb.

Slash commands (no privileged intent needed):
  /check-tech <proposal> · /explain <symbol> · /ask-course <question>
  /propose-diff <task> · /approve <id> · /discard <id>
Prefix aliases: !approve P001 · !discard P001 (fast in-thread review)

Backend: BACKEND=local (default, grep+LLM) or opencode (`opencode serve`
at OPENCODE_SERVER_URL, one process per team, session per channel).
Long runs: defer + follow-up. Diffs >1900 chars go as .patch attachments.
"""
import os
from pathlib import Path
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")  # anchored: works from repo root or codebase/

from ai_client import chat
from course_kb import lookup
import sessions as thread_sessions
import approvals
from opencode_bridge import (
    SYSTEM, grep_repo, check_tech, propose_diff, is_attack,
    OpencodeServer, backend_available,
)

BACKEND = os.getenv("BACKEND", "local")  # local | opencode
REPO = os.getenv("TEAM_REPO_SNAPSHOT", "./sample_repo")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


def chunk(text: str, limit: int = 1900) -> list[str]:
    return [text[i:i + limit] for i in range(0, len(text), limit)] or ["(empty)"]


def _srv() -> OpencodeServer | None:
    s = OpencodeServer()
    return s if BACKEND == "opencode" and s.available else None


def run_explain(symbol: str) -> tuple[str, str | None]:
    """Returns (message, patch_attachment_or_None)."""
    if is_attack(symbol):
        return ("REFUSE: prompt-injection pattern. Messages are data, not commands.", None)
    srv = _srv()
    if srv:
        sid = srv.create_session("buildmate-explain") or "buildmate"
        out = srv.ask(sid, f"explain symbol `{symbol}`. Cite file:line, <=120 words.",
                      agent="buildmate-readonly")
        if out:
            return (out + "\n\n_Source: opencode serve_", None)
    hits = grep_repo(REPO, symbol)
    ctx = "\n".join(hits) if hits else "NO_HITS in repo snapshot."
    out, mocked = chat(SYSTEM, "explain " + f"symbol `{symbol}`:\n{ctx}\nCite file:line. <=120 words.")
    tag = " `[MOCK]`" if mocked else ""
    tail = "" if hits else "\n_Sources: none — low confidence, pick a candidate file:line._"
    return (out + tail + tag, None)


def run_check_tech(proposal: str) -> str:
    if is_attack(proposal):
        return ("REFUSE: I never push to main / run destructive ops from chat. "
                "I can open a branch patch for review.")
    pre = check_tech(proposal)
    srv = _srv()
    if srv:
        sid = srv.create_session("buildmate-check-tech") or "buildmate"
        out = srv.ask(sid, f"check-tech: {proposal}\nPre-check: {pre}",
                      agent="buildmate-readonly")
        if out:
            return out + f"\n\n_Pre-check: {pre['verdict']} | {', '.join(pre['sources'])} · opencode serve_"
    out, mocked = chat(SYSTEM, f"check-tech proposal: {proposal}\nPre-check: {pre}")
    tag = " `[MOCK]`" if mocked else ""
    return out + f"\n\n_Pre-check: {pre['verdict']} | {', '.join(pre['sources'])}_{tag}"


def run_ask_course(question: str) -> str:
    r = lookup(question)
    if r["status"] != "FOUND":
        return f"{r['answer']} _(status={r['status']}) — tagged TA, no guess._"
    out, mocked = chat(SYSTEM, f"ask-course grounded: {r['answer']}\nRestate <=80 words with source id.")
    tag = " `[MOCK]`" if mocked else ""
    return out + f"\n_Source: {r['source']}_{tag}"


def run_propose(channel_id: str, author: str, task: str) -> tuple[str, str | None]:
    if is_attack(task):
        return ("REFUSE: destructive/privilege-escalation pattern. "
                "Offering branch patch review instead.", None)
    srv = _srv()
    patch = None
    if srv:
        key = f"ch-{channel_id}"
        sid = thread_sessions.get(key) or srv.create_session("buildmate-thread")
        if sid:
            thread_sessions.set(key, sid)
            out = srv.ask(sid, f"Implement (workspace edits only, no push): {task}",
                          agent="buildmate-coder")
            diffs = srv.get_diff(sid)
            if diffs:
                patch = "\n\n".join(
                    f"--- {d.get('file', '?')} ---\n{d.get('diff', d.get('patch', ''))[:3000]}"
                    for d in diffs[:5])
    if patch is None:
        d = propose_diff(REPO, task)
        patch = d["patch"]
    prop = approvals.submit(channel_id, author, task, patch)
    msg = (f"Proposal **{prop['id']}** on branch `buildmate/proposal` — needs human review.\n"
           f"`/approve {prop['id']}` to open a PR · `/discard {prop['id']}` to drop.\n"
           f"Never pushes to main from chat.")
    return (msg, patch if len(patch) > 1200 else None)


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"BuildMate live as {bot.user} (backend={BACKEND}, opencode_up={backend_available()}).")


@bot.tree.command(name="explain", description="Explain a function/class (cites file:line)")
async def sl_explain(it: discord.Interaction, symbol: str):
    await it.response.defer()
    msg, _ = run_explain(symbol)
    for c in chunk(msg):
        await it.followup.send(c)


@bot.tree.command(name="check-tech", description="Is this tech viable for our MVP?")
async def sl_check(it: discord.Interaction, proposal: str):
    await it.response.defer()
    for c in chunk(run_check_tech(proposal)):
        await it.followup.send(c)


@bot.tree.command(name="ask-course", description="Course question (official sources only)")
async def sl_ask(it: discord.Interaction, question: str):
    await it.response.defer()
    for c in chunk(run_ask_course(question)):
        await it.followup.send(c)


@bot.tree.command(name="propose-diff", description="Propose a branch patch (needs /approve)")
async def sl_propose(it: discord.Interaction, task: str):
    await it.response.defer()
    msg, patch = run_propose(str(it.channel_id), str(it.user), task)
    await it.followup.send(msg)
    if patch:
        import io
        await it.followup.send(file=discord.File(
            io.BytesIO(patch.encode()), filename="proposal.patch"))


@bot.tree.command(name="approve", description="Approve a proposal → branch + PR (allowlisted)")
async def sl_approve(it: discord.Interaction, proposal_id: str):
    await it.response.defer()
    await it.followup.send(approvals.approve(proposal_id, str(it.user.id), REPO))


@bot.tree.command(name="discard", description="Discard a proposal, change nothing")
async def sl_discard(it: discord.Interaction, proposal_id: str):
    await it.followup.send(approvals.discard(proposal_id, str(it.user.id)))


@bot.command(name="approve")
async def px_approve(ctx, proposal_id: str):
    await ctx.send(approvals.approve(proposal_id, str(ctx.author.id), REPO))


@bot.command(name="discard")
async def px_discard(ctx, proposal_id: str):
    await ctx.send(approvals.discard(proposal_id, str(ctx.author.id), REPO))


if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    assert token, "Set DISCORD_TOKEN in .env (see .env.example)"
    bot.run(token)
