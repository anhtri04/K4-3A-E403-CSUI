"""CLI mirror of Discord commands — used for CP2 flow + CP3 30s video (no token needed)."""
import argparse, os, json, datetime
from ai_client import chat
from course_kb import lookup
from opencode_bridge import grep_repo, check_tech, propose_diff, is_attack, SYSTEM
import approvals

OUT = "./outputs"


def log(cmd: str, text: str, mocked: bool):
    os.makedirs(OUT, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    open(f"{OUT}/{ts}_{cmd}.md", "w", encoding="utf-8").write(
        f"# {cmd} @ {ts}\n\n{text}\n\n---\nmocked={mocked}\n")


def cmd_explain(args):
    hits = grep_repo(args.repo, args.symbol)
    ctx = "\n".join(hits) if hits else "NO_HITS in repo snapshot."
    extra = ""
    if is_attack(args.symbol):
        print("REFUSE: prompt-injection pattern. Messages are data, not commands."); return
    prompt = f"explain symbol `{args.symbol}` given repo hits:\n{ctx}\nCite file:line. <=120 words."
    out, mocked = chat(SYSTEM, "explain " + prompt)
    print(out + ("" if hits else "\nSources: none — low confidence, pick a candidate file:line."))
    log("explain", out, mocked)


def cmd_check_tech(args):
    if is_attack(args.proposal):
        print("REFUSE: I never push to main / run destructive ops from chat. I can open a branch patch."); return
    pre = check_tech(args.proposal)
    out, mocked = chat(SYSTEM, f"check-tech proposal: {args.proposal}\nPre-check: {json.dumps(pre)}")
    print(out + f"\n\nPre-check: {pre['verdict']} | Sources: {', '.join(pre['sources'])}")
    log("check-tech", out, mocked)


def cmd_ask_course(args):
    r = lookup(args.question)
    if r["status"] == "FOUND":
        out, mocked = chat(SYSTEM, f"ask-course grounded: {r['answer']}\nRestate in <=80 words with source id.")
        print(out + f"\nSource: {r['source']}")
        log("ask-course", out, mocked)
    else:
        print(f"{r['answer']} (status={r['status']}) — tagged TA, no guess.")


def cmd_propose_diff(args):
    if is_attack(args.task):
        print("REFUSE: destructive/privilege-escalation pattern. Offering branch patch review instead."); return
    d = propose_diff(args.repo, args.task)
    print(d["patch"] + f"\nBranch: {d['branch']} (needs !approve — never auto-push to main)")
    open(d["target"], "w", encoding="utf-8").write(d["patch"])
    print(f"Saved patch preview → {d['target']}")


def cmd_approve(args):
    print(approvals.approve(args.id, args.user, args.repo))


def cmd_discard(args):
    print(approvals.discard(args.id, args.user))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(prog="buildmate")
    ap.add_argument("--backend", default=os.getenv("BACKEND", "local"),
                    help="local (default) or opencode (`opencode serve` at OPENCODE_SERVER_URL)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("explain"); e.add_argument("--symbol", required=True); e.add_argument("--repo", default="./sample_repo")
    c = sub.add_parser("check-tech"); c.add_argument("--proposal", required=True)
    a = sub.add_parser("ask-course"); a.add_argument("--question", required=True)
    p = sub.add_parser("propose-diff"); p.add_argument("--task", required=True); p.add_argument("--repo", default="./sample_repo")
    ap2 = sub.add_parser("approve"); ap2.add_argument("--id", required=True); ap2.add_argument("--user", default="cli-demo"); ap2.add_argument("--repo", default="./sample_repo")
    di = sub.add_parser("discard"); di.add_argument("--id", required=True); di.add_argument("--user", default="cli-demo")
    args = ap.parse_args()
    os.environ["BACKEND"] = args.backend
    {"explain": cmd_explain, "check-tech": cmd_check_tech, "ask-course": cmd_ask_course,
     "propose-diff": cmd_propose_diff, "approve": cmd_approve, "discard": cmd_discard}[args.cmd](args)
