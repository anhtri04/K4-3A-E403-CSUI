"""Real vs Mock AI client. REAL when OPENAI_API_KEY present, else transparent MOCK."""
import os

MOCK_MARKER = "[MOCK]"


def is_mock() -> bool:
    return not os.getenv("OPENAI_API_KEY")


def chat(system: str, user: str, max_tokens: int = 800, temperature: float = 0.3) -> tuple[str, bool]:
    """Returns (text, used_mock). Keeps a trace-friendly contract for eval."""
    if is_mock():
        return mock_reply(system, user), True
    try:
        from openai import OpenAI
        client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        )
        r = client.chat.completions.create(
            model=os.getenv("MODEL_NAME", "gpt-4o-mini"),
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return r.choices[0].message.content or "", False
    except Exception as e:  # transparent fallback, never pretend
        return f"{MOCK_MARKER} AI call failed ({e}); fallback answer.\n" + mock_reply(system, user), True


def mock_reply(system: str, user: str) -> str:
    low = user.lower()
    if "sqlite" in low or "check-tech" in low or "viable" in low:
        return (f"{MOCK_MARKER} check-tech: SQLite fits a 4-person MVP (single file, zero ops, "
                "enough for low concurrency). Revisit Postgres when you need concurrent writes "
                "or row-level security. Source: repo scope (MVP, 4 editors) + KB:MVP-rubric.")
    if "explain" in low:
        return (f"{MOCK_MARKER} explain: symbol does input validation then opens a PR-ready diff "
                "on a branch. See sample_repo/bot_logic.py. Ask `!revise` to dig deeper.")
    if "deadline" in low or "lab 2" in low or "hạn nộp" in low:
        return (f"{MOCK_MARKER} ask-course: NOT_FOUND in official announcements snapshot. "
                "I won't guess — tagged TA. Provide announcement id to proceed.")
    if "push" in low and "main" in low:
        return (f"{MOCK_MARKER} refusal: I never push to main. I'll create a branch patch for review. Use `!approve`.")
    return f"{MOCK_MARKER} generic: noted. Provide repo symbol or official announcement id for a grounded answer."
