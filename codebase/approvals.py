"""Human-in-loop approval queue: propose → !approve → branch + PR, or !discard.

Safety: approvers allowlisted via APPROVERS env (Discord user IDs, CSV).
Empty APPROVERS = demo mode (anyone may approve, loudly logged).
Never touches main: all work happens on buildmate/proposal-* branches.
"""
import json, os, subprocess, datetime

def _path() -> str:
    d = os.getenv("BUILDMATE_STATE_DIR", "./state")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, "approvals.json")

def _load() -> dict:
    try:
        return json.load(open(_path(), encoding="utf-8"))
    except Exception:
        return {"seq": 0, "items": {}}

def _save(data: dict):
    json.dump(data, open(_path(), "w", encoding="utf-8"), ensure_ascii=False, indent=2)

def is_approver(user_id: str) -> tuple[bool, str]:
    raw = os.getenv("APPROVERS", "").strip()
    if not raw:
        return True, "demo-mode: APPROVERS unset, allowing with warning"
    return (str(user_id) in [x.strip() for x in raw.split(",")],
            "allowlisted" if str(user_id) in [x.strip() for x in raw.split(",")] else "not in APPROVERS")

def submit(channel_id: str, author: str, task: str, patch: str, branch: str | None = None) -> dict:
    db = _load()
    db["seq"] += 1
    pid = f"P{db['seq']:03d}"
    db["items"][pid] = {"id": pid, "channel": str(channel_id), "author": str(author),
                        "task": task[:500], "patch": patch[:8000], "status": "pending",
                        "branch_hint": branch,
                        "ts": datetime.datetime.now().isoformat(timespec="seconds")}
    _save(db)
    return db["items"][pid]

def get(pid: str) -> dict | None:
    return _load()["items"].get(pid.upper())

def discard(pid: str, user_id: str) -> str:
    db = _load()
    it = db["items"].get(pid.upper())
    if not it:
        return f"{pid}: not found."
    if it["status"] != "pending":
        return f"{pid}: already {it['status']}."
    it["status"] = "discarded"
    it["by"] = str(user_id)
    _save(db)
    return f"{it['id']} discarded. Thread continues — nothing was changed."

def _run(args: list[str], cwd: str, timeout: int = 30) -> tuple[bool, str]:
    try:
        r = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        ok = r.returncode == 0
        return ok, (r.stdout + r.stderr)[-1000:]
    except Exception as e:
        return False, str(e)[:500]

def approve(pid: str, user_id: str, repo: str) -> str:
    """Create branch, apply-or-attach patch, commit, push branch, open PR. Never main."""
    ok, note = is_approver(user_id)
    if not ok:
        return f"Refused: <@{user_id}> is {note}. Ask an allowlisted approver."
    db = _load()
    it = db["items"].get(pid.upper())
    if not it:
        return f"{pid}: not found."
    if it["status"] != "pending":
        return f"{pid}: already {it['status']}."
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    hint = (it.get("branch_hint") or "").strip()
    branch = f"{hint}-{ts}" if hint else f"buildmate/proposal-{it['id'].lower()}-{ts}"
    ok, out = _run(["git", "checkout", "-b", branch], repo)
    if not ok:
        return f"git checkout -b failed: {out}"
    patch = it["patch"]
    applied = False
    if patch.lstrip().startswith(("diff --git", "--- ")):
        with open(os.path.join(repo, ".buildmate.patch"), "w", encoding="utf-8") as f:
            f.write(patch)
        ok, out = _run(["git", "apply", "--check", ".buildmate.patch"], repo)
        if ok:
            ok, out = _run(["git", "apply", ".buildmate.patch"], repo)
            applied = ok
        os.remove(os.path.join(repo, ".buildmate.patch"))
    artifact = os.path.join(repo, f".buildmate-{it['id'].lower()}.patch.txt")
    with open(artifact, "w", encoding="utf-8") as f:
        f.write(f"# {it['id']} task: {it['task']}\n# approved by {user_id} (human-in-loop)\n\n{patch}")
    _run(["git", "add", os.path.basename(artifact)], repo)
    _run(["git", "commit", "-m", f"BuildMate {it['id']}: {it['task'][:72]} (needs review)"], repo)
    ok, out = _run(["git", "push", "-u", "origin", branch], repo)
    if not ok:
        it["status"] = "approved-branch-local"
        it["branch"] = branch
        _save(db)
        return (f"{it['id']} approved → branch `{branch}` ready LOCALLY "
                f"(applied={applied}). Push failed (no origin/creds?): {out[:300]}")
    ok, out = _run(["gh", "pr", "create", "--title", f"BuildMate {it['id']}: {it['task'][:60]}",
                    "--body", f"Proposed from Discord by {it['author']}, approved by {user_id}."],
                   repo)
    it["status"] = "approved-pr" if ok else "approved-pushed"
    it["branch"] = branch
    _save(db)
    suffix = f" PR: {out.strip()[:200]}" if ok else f" (gh pr create skipped: {out[:200]})"
    return f"{it['id']} approved → branch `{branch}` (applied={applied}).{suffix}"
