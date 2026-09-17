"""BuildMate Discord gateway (thin). Policy lives in app/opencode_bridge/course_kb.

Slash commands (no privileged intent needed):
  /check-tech <proposal> · /explain <symbol> · /ask-course <question>
  /propose-diff <task> · /approve <id> · /discard <id>
  Session lifecycle (§4c, default-deaf — bot only tracks inside an OPEN session):
  /join <task> · /quit [note] · /new <task> · /context <ids> · /sessions
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


DEAF_MSG = ("Bot đang điếc trong thread này — chưa có session mở. "
            "Gõ `/join <task>` để mở session trước (1 session = 1 việc = 1 branch).")


def _require_session(channel_id: str | None) -> tuple[dict | None, str | None]:
    """Default-deaf gate. channel_id=None (CLI-style direct call) skips gating."""
    if channel_id is None:
        return None, None
    rec = thread_sessions.get_open(channel_id)
    if rec is None:
        return None, DEAF_MSG
    return rec, None


def run_explain(symbol: str, channel_id: str | None = None) -> tuple[str, str | None]:
    """Returns (message, patch_attachment_or_None)."""
    _, deaf = _require_session(channel_id)
    if deaf:
        return (deaf, None)
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


def run_check_tech(proposal: str, channel_id: str | None = None) -> str:
    _, deaf = _require_session(channel_id)
    if deaf:
        return deaf
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


def run_ask_course(question: str, channel_id: str | None = None) -> str:
    _, deaf = _require_session(channel_id)
    if deaf:
        return deaf
    r = lookup(question)
    if r["status"] != "FOUND":
        return f"{r['answer']} _(status={r['status']}) — tagged TA, no guess._"
    out, mocked = chat(SYSTEM, f"ask-course grounded: {r['answer']}\nRestate <=80 words with source id.")
    tag = " `[MOCK]`" if mocked else ""
    return out + f"\n_Source: {r['source']}_{tag}"


def run_propose(channel_id: str, author: str, task: str) -> tuple[str, str | None]:
    sess, deaf = _require_session(channel_id)
    if deaf:
        return (deaf, None)
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
    branch = sess["branch"] if sess else "buildmate/proposal"
    if patch is None:
        d = propose_diff(REPO, task)
        patch = d["patch"]
        if not sess:
            branch = d.get("branch", branch)
    prop = approvals.submit(channel_id, author, task, patch, branch=branch)
    msg = (f"Proposal **{prop['id']}** (session {sess['id'] if sess else 'n/a'}) on branch `{branch}` — needs human review.\n"
           f"`/approve {prop['id']}` to open a PR · `/discard {prop['id']}` to drop.\n"
           f"Never pushes to main from chat.")
    return (msg, patch if len(patch) > 1200 else None)


# ---------------------------------------------------------------------------
# Session lifecycle (§4c). Default-deaf: work commands above only run inside
# an OPEN session on this thread/channel key.
# ---------------------------------------------------------------------------

def run_join(channel_id: str, user: str, task: str) -> str:
    rec, err = thread_sessions.open_session(channel_id, task, user)
    if err:
        return err
    return (f"Session **{rec['id']}** mở cho: {rec['task']}\n"
            f"Branch: `{rec['branch']}` · bot bắt đầu nghe trong thread này.\n"
            f"`/quit [ghi chú]` để đóng · `/new <task>` để đổi việc.")


def run_quit(channel_id: str, note: str = "") -> str:
    rec, err = thread_sessions.close_session(channel_id, note)
    if err:
        return err
    tail = f" Kết luận đã lưu: {rec['note']}" if rec["note"] else " (chưa có kết luận)"
    return f"Session **{rec['id']}** đã đóng — context đóng băng.{tail}"


def run_new(channel_id: str, user: str, task: str) -> str:
    old, _ = thread_sessions.close_session(channel_id, "superseded by /new")
    head = f"(đã đóng {old['id']}) " if old else ""
    rec, err = thread_sessions.open_session(channel_id, task, user)
    if err:
        return err
    return (f"{head}Session mới **{rec['id']}** trắng hoàn toàn cho: {rec['task']}\n"
            f"Branch: `{rec['branch']}`.")


def run_context(channel_id: str, ids: str) -> str:
    sess, deaf = _require_session(channel_id)
    if deaf:
        return deaf
    wanted = [w.upper() for w in ids.replace(",", " ").split()][:3]
    if not wanted:
        return "Dùng: `/context S001 [S002 S003]` (tối đa 3, xem id bằng `/sessions`)."
    lines = []
    for sid in wanted:
        rec = thread_sessions.get_by_id(sid)
        if rec is None:
            lines.append(f"**{sid}**: không tìm thấy.")
            continue
        props = [f"{p['id']}({p['status']})" for p in approvals._load()["items"].values()
                 if p.get("channel") == rec["key"] and p.get("branch_hint") == rec["branch"]]
        extra = f" | proposals: {', '.join(props)}" if props else ""
        lines.append(thread_sessions.summarize(rec) + extra)
    return ("Context đã kéo (tóm tắt đã lọc, có ghi nguồn):\n" + "\n".join(lines))


def run_sessions() -> str:
    recs = thread_sessions.list_sessions()
    if not recs:
        return "Chưa có session nào — `/join <task>` để mở."
    return "\n".join(
        f"**{r['id']}** [{r['status']}] {r['task']} (branch `{r['branch']}`)"
        for r in recs)


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"BuildMate live as {bot.user} (backend={BACKEND}, opencode_up={backend_available()}).")


@bot.tree.command(name="explain", description="Explain a function/class (cites file:line)")
async def sl_explain(it: discord.Interaction, symbol: str):
    await it.response.defer()
    msg, _ = run_explain(symbol, str(it.channel_id))
    for c in chunk(msg):
        await it.followup.send(c)


@bot.tree.command(name="check-tech", description="Is this tech viable for our MVP?")
async def sl_check(it: discord.Interaction, proposal: str):
    await it.response.defer()
    for c in chunk(run_check_tech(proposal, str(it.channel_id))):
        await it.followup.send(c)


@bot.tree.command(name="ask-course", description="Course question (official sources only)")
async def sl_ask(it: discord.Interaction, question: str):
    await it.response.defer()
    for c in chunk(run_ask_course(question, str(it.channel_id))):
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


@bot.tree.command(name="join", description="Open a session: bot starts listening (1 session = 1 task = 1 branch)")
async def sl_join(it: discord.Interaction, task: str):
    await it.response.defer()
    await it.followup.send(run_join(str(it.channel_id), str(it.user), task))


@bot.tree.command(name="quit", description="Close the session, freeze context log")
async def sl_quit(it: discord.Interaction, note: str = ""):
    await it.response.defer()
    await it.followup.send(run_quit(str(it.channel_id), note))


@bot.tree.command(name="new", description="Close current session and open a fresh one")
async def sl_new(it: discord.Interaction, task: str):
    await it.response.defer()
    await it.followup.send(run_new(str(it.channel_id), str(it.user), task))


@bot.tree.command(name="context", description="Pull filtered summaries from up to 3 past sessions")
async def sl_context(it: discord.Interaction, ids: str):
    await it.response.defer()
    for c in chunk(run_context(str(it.channel_id), ids)):
        await it.followup.send(c)


@bot.tree.command(name="sessions", description="List open/closed sessions")
async def sl_sessions(it: discord.Interaction):
    await it.response.defer()
    for c in chunk(run_sessions()):
        await it.followup.send(c)


if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    assert token, "Set DISCORD_TOKEN in .env (see .env.example)"
    bot.run(token)
