"""System + user prompt — đồng bộ spec.md §5 (khóa v1.0)."""
SYSTEM_PROMPT = (
    "Bạn là HLV sức bền. Luôn trả JSON hợp lệ theo schema. "
    "Ưu tiên an toàn: RPE <=7 cho beginner, có ngày nghỉ, cảnh báo khi goal quá sức. "
    "Thêm disclaimer y tế tiếng Việt. Ngắn gọn, động viên."
)

SCHEMA_HINT = (
    "Trả JSON duy nhất với keys: weekly_plan (list of {day, focus, duration_min, intensity_rpe, notes}), "
    "safety_notes (list), motivation (<=280 ky tu), disclaimer (string), engine (string)."
)

def build_user_prompt(level: str, goal: str, sessions: int, constraints: str = "", lang: str = "vi") -> str:
    return (
        f"Level: {level} | Goal: {goal} | Sessions: {sessions}\n"
        f"Constraints: {constraints or 'none'} | Lang: {lang}\n"
        f"{SCHEMA_HINT}"
    )
