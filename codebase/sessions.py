"""Thread → opencode session mapping. JSON file, stdlib only."""
import json, os

def _path() -> str:
    d = os.getenv("BUILDMATE_STATE_DIR", "./state")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, "sessions.json")

def _load() -> dict:
    try:
        return json.load(open(_path(), encoding="utf-8"))
    except Exception:
        return {}

def _save(data: dict):
    json.dump(data, open(_path(), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

def get(thread_id: str) -> str | None:
    return _load().get(str(thread_id))

def set(thread_id: str, session_id: str):
    data = _load()
    data[str(thread_id)] = session_id
    _save(data)


# ---------------------------------------------------------------------------
# Lifecycle store (§4c): explicit /join → /quit sessions. Default-deaf: the bot
# only tracks context inside an OPEN session keyed by thread/channel id.
# Raw chat is never dumped across sessions — /context renders filtered
# summaries (task + status + closing note + approved proposal refs) only.
# ---------------------------------------------------------------------------
import datetime as _dt
import re as _re


def _life_path() -> str:
    d = os.getenv("BUILDMATE_STATE_DIR", "./state")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, "lifecycle.json")


def _life_load() -> dict:
    try:
        return json.load(open(_life_path(), encoding="utf-8"))
    except Exception:
        return {"seq": 0, "items": {}}


def _life_save(data: dict):
    json.dump(data, open(_life_path(), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def _slug(task: str, limit: int = 30) -> str:
    s = _re.sub(r"[^a-z0-9]+", "-", task.lower()).strip("-")
    return s[:limit] or "task"


def open_session(key: str, task: str, opener: str) -> tuple[dict | None, str | None]:
    """Open a session on key. Returns (record, None) or (None, error)."""
    db = _life_load()
    for it in db["items"].values():
        if it["key"] == str(key) and it["status"] == "open":
            return None, f"Session {it['id']} đang mở trong thread này — `/quit` để đóng hoặc `/new` để mở việc khác."
    db["seq"] += 1
    sid = f"S{db['seq']:03d}"
    rec = {"id": sid, "key": str(key), "task": task[:200],
           "status": "open", "branch": f"vibebot/{sid.lower()}-{_slug(task)}",
           "note": "", "opener": str(opener),
           "opened_at": _dt.datetime.now().isoformat(timespec="seconds"),
           "closed_at": None}
    db["items"][sid] = rec
    _life_save(db)
    return rec, None


def close_session(key: str, note: str = "") -> tuple[dict | None, str | None]:
    db = _life_load()
    for it in db["items"].values():
        if it["key"] == str(key) and it["status"] == "open":
            it["status"] = "closed"
            it["note"] = (note or "")[:500]
            it["closed_at"] = _dt.datetime.now().isoformat(timespec="seconds")
            _life_save(db)
            return it, None
    return None, "Không có session đang mở trong thread này — `/join <task>` để mở."


def get_open(key: str) -> dict | None:
    for it in _life_load()["items"].values():
        if it["key"] == str(key) and it["status"] == "open":
            return it
    return None


def get_by_id(sid: str) -> dict | None:
    return _life_load()["items"].get(sid.upper())


def list_sessions(limit: int = 10) -> list[dict]:
    items = sorted(_life_load()["items"].values(), key=lambda r: r["id"])
    return items[-limit:]


def summarize(rec: dict) -> str:
    """Filtered summary only — never raw chat. Safe to pull via /context."""
    note = rec["note"] or "(chưa có kết luận)"
    return (f"**{rec['id']}** [{rec['status']}] task: {rec['task']} | "
            f"branch: `{rec['branch']}` | kết luận: {note}")
