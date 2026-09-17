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
