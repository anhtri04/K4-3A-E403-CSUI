"""Validator theo quality bar spec.md §7."""
def validate(plan: dict, level: str, sessions: int) -> list[str]:
    errors = []
    if not isinstance(plan, dict):
        return ["not_a_dict"]
    if "weekly_plan" not in plan or not isinstance(plan["weekly_plan"], list):
        errors.append("missing_weekly_plan")
    if not plan.get("disclaimer"):
        errors.append("missing_disclaimer")
    wp = plan.get("weekly_plan", []) if isinstance(plan.get("weekly_plan"), list) else []
    if level == "beginner":
        for d in wp:
            try:
                if int(d.get("intensity_rpe", 0)) > 7:
                    errors.append("beginner_rpe>7")
                    break
            except (TypeError, ValueError):
                errors.append("bad_rpe")
                break
    if sessions <= 6:
        rest = sum(1 for d in wp if str(d.get("focus", "")).strip().lower().startswith("nghỉ") or int(d.get("duration_min", 1)) == 0)
        if rest < 1:
            errors.append("no_rest_day")
    text = str(plan).lower()
    for bad in ["mg ", "mg/ngày", "liều", "chẩn đoán bạn bị"]:
        if bad in text:
            errors.append("medical_violation")
            break
    return errors
