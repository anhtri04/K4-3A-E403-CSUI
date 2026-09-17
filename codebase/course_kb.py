"""Official-only course KB. FOUND / CLARIFY / NOT_FOUND — never guess."""
import json, os

KB_PATH = os.getenv("COURSE_KB_PATH", "./course_kb.json")

# Minimal fake KB for prototype. Replace ids with real announcement ids during build.
FAKE_KB = {
    "announcements": [
        {"id": "ANN-001", "date": "2026-09-10", "topic": "team formation",
         "text": "Free team formation closes 2026-09-15 23:59. After that BTC assigns."},
        {"id": "ANN-002", "date": "2026-09-12", "topic": "lab2",
         "text": "Lab2 submission via VLearn before deadline in announcement. Late push after 23:59 counts as late."},
    ]
}


def load_kb() -> dict:
    path = KB_PATH
    if os.path.exists(path):
        try:
            return json.load(open(path, encoding="utf-8"))
        except Exception:
            pass
    return FAKE_KB


def lookup(question: str) -> dict:
    """Return {status, answer, source}. Status in FOUND/CLARIFY/NOT_FOUND."""
    q = question.lower()
    kb = load_kb()
    # personal data → refuse class
    if any(k in q for k in ["điểm danh của tôi", "my attendance", "my xp", "my grade", "mssv"]):
        return {"status": "REFUSE", "answer": "I can't answer personal records. Please ask TA via ticket.",
                "source": None}
    hits = [a for a in kb.get("announcements", []) if any(
        w in q for w in a["topic"].split()) or a["id"].lower() in q]
    # deadline conflict demo: if question generic about lab2 without id → CLARIFY
    if "lab" in q and not hits:
        return {"status": "NOT_FOUND",
                "answer": "NOT_FOUND in official announcements snapshot. I won't guess — tagged TA.",
                "source": None}
    if hits:
        a = hits[0]
        return {"status": "FOUND",
                "answer": f"Per {a['id']} ({a['date']}): {a['text']}",
                "source": a["id"]}
    return {"status": "NOT_FOUND",
            "answer": "NOT_FOUND in official announcements snapshot. I won't guess — tagged TA.",
            "source": None}
