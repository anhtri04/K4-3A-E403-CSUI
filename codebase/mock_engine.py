"""Rule-based MOCK engine — KHÔNG gọi mạng. Mọi output gắn engine=mock."""
import itertools

MOTIVATIONS = [
    "Cứ đều chân mỗi ngày, sức bền sẽ lên lúc nào không hay!",
    "Chậm mà chắc — hôm nay tốt hơn hôm qua 1% là thắng!",
    "Nghỉ đủ cũng là tập. Lắng nghe cơ thể nhé!",
]
_cycle = itertools.cycle(MOTIVATIONS)

DISCLAIMER = "Lưu ý: đây là gợi ý tập luyện chung, không thay thế tư vấn y tế. Nếu đau/choáng, dừng tập và hỏi ý kiến bác sĩ/HLV."

def generate_plan(level="beginner", goal="chạy 5km", sessions=3, constraints="", lang="vi"):
    sessions = max(1, min(7, sessions))
    days = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]
    plan = []
    if level == "beginner":
        focuses = [("Đi bộ nhanh + chạy nhẹ 1-1", 30, 5), ("Nghỉ / giãn cơ", 15, 2),
                   ("Chạy nhẹ xen kẽ đi bộ", 25, 6), ("Nghỉ", 0, 1)]
    elif level == "intermediate":
        focuses = [("Tempo nhẹ", 30, 7), ("Chạy nền easy", 40, 6), ("Long run nhẹ", 50, 6)]
    else:
        focuses = [("Interval nhẹ", 30, 7), ("Tempo", 35, 7), ("Long run", 60, 6)]

    k = 0
    for i, d in enumerate(days):
        if k < sessions and i % 2 == 0:
            f, dur, rpe = focuses[k % len(focuses)]
            if "Nghỉ" not in f:
                plan.append({"day": d, "focus": f, "duration_min": dur,
                             "intensity_rpe": min(rpe, 7 if level == "beginner" else 8),
                             "notes": f"Hướng tới: {goal}"})
                k += 1
            else:
                plan.append({"day": d, "focus": "Nghỉ", "duration_min": 0,
                             "intensity_rpe": 1, "notes": "Phục hồi"})
        else:
            plan.append({"day": d, "focus": "Nghỉ", "duration_min": 0,
                         "intensity_rpe": 1, "notes": "Phục hồi"})

    safety = ["Khởi động 5-10 phút trước buổi tập.", "Tăng khối lượng <=10%/tuần."]
    if constraints:
        safety.append(f"Lưu ý theo thể trạng của bạn: {constraints}. Giảm cường độ nếu đau.")
    if "marathon" in goal.lower() and level == "beginner":
        safety.append("Cảnh báo: marathon trong ngắn hạn là quá sức cho beginner — hãy dời mục tiêu 12-16 tuần.")

    return {
        "weekly_plan": plan,
        "safety_notes": safety,
        "motivation": next(_cycle),
        "disclaimer": DISCLAIMER,
        "engine": "mock",
        "mock": True,
    }
