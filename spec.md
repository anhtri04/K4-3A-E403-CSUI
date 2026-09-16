# spec.md — AI Spec: Stamina Coach (Đã khóa Quality Bar)

- **Nhóm:** CSUI — Phòng E403
- **Phiên bản:** v1.0-locked
- **Ngày khóa:** TODO_YYYY-MM-DD
- **Người khóa:** TODO (Leader)

> Quy tắc: sau khi khóa, mọi chỉnh sửa phải ghi vào §9 Changelog, không sửa nội dung §1–§8 mà không bump version.

---

## 1. Bài toán (Problem Statement)

**Vấn đề:** Người mới chạy bộ / tập thể lực thiếu giáo án cá nhân hóa theo sức bền hiện tại, dễ chấn thương hoặc bỏ cuộc.

**Mục tiêu:** Prototype AI nhận đầu vào (trình độ, mục tiêu, số buổi/tuần, chấn thương, thiết bị) → sinh giáo án tuần + lời động viên + cảnh báo an toàn, kèm giải thích ngắn gọn.

**Non-goals (không làm):** Không chẩn đoán y khoa, không thay PT/BS, không tracking GPS realtime, không bán thiết bị.

## 2. Người dùng & Kịch bản (Users & Use Cases)

| Persona | Nhu cầu | Kịch bản chính |
|---|---|---|
| P1. Người mới (chạy <5km) | Giáo án dễ theo, không chấn thương | UC1: Nhập profile → nhận plan 7 ngày |
| P2. Người quay lại sau nghỉ | Phục hồi dần, kiểm soát cường độ | UC2: Điều chỉnh plan khi mệt / đau |
| P3. Người bận (3 buổi/tuần) | Plan ngắn, linh hoạt | UC3: Rút gọn plan còn 3 buổi |

**Out-of-scope user:** VĐV chuyên nghiệp cần periodization nâng cao.

## 3. Phạm vi AI (AI Scope)

- **Input:** level (beginner/intermediate/advanced), goal (text), sessions_per_week (1–7), constraints (chấn thương, thời gian/buổi), ngôn ngữ (vi/en).
- **Output (JSON + text):** `weekly_plan[day, focus, duration_min, intensity(RPE 1-10), notes]`, `safety_notes[]`, `motivation` (≤280 ký tự), `disclaimer`.
- **Model:** OpenAI-compatible chat model (mặc định `gpt-4o-mini`, cấu hình qua `MODEL_NAME`). Temperature 0.7, max_tokens 800.
- **Mock:** khi thiếu API key → `codebase/mock_engine.py` trả plan mẫu theo rule (ghi log `[MOCK]`).

## 4. Luồng UX (UX Flow)

```
[1] Nhập profile (form/CLI) → [2] Validate (sessions 1-7, duration 10-120p)
→ [3] Gọi AI (real/mock) → [4] Render plan dạng bảng + cảnh báo
→ [5] Nút "Điều chỉnh khi mệt/đau" → [6] Regenerate với constraint mới
→ [7] Lưu JSON + hiển thị disclaimer y tế
```

Lỗi: thiếu field → hỏi lại; AI timeout → retry 1 lần → fallback mock + banner "đang dùng bản mẫu".

## 5. Thiết kế Prompt & Model

**System prompt (khóa):**
> Bạn là HLV sức bền. Luôn trả JSON hợp lệ theo schema. Ưu tiên an toàn: RPE ≤7 cho beginner, có ngày nghỉ, cảnh báo khi goal quá sức. Thêm disclaimer y tế tiếng Việt. Ngắn gọn, động viên.

**User prompt template:**
```
Level: {level} | Goal: {goal} | Sessions: {sessions_per_week}
Constraints: {constraints} | Lang: {lang}
Trả JSON: weekly_plan, safety_notes, motivation, disclaimer.
```

**Giải thích lựa chọn:** temp 0.7 cân bằng sáng tạo/ổn định; schema-constrained để eval tự động được.

## 6. Dữ liệu & Golden Set (Data)

- File: `eval/golden_set.json` — 24 case (≥20 theo quy chế), phủ: beginner/intermediate, chấn thương đầu gối, ít thời gian, mục tiêu phi thực tế, tiếng Anh, input thiếu.
- Mỗi case: `id, input, expected_behavior, must_contain[], must_not_contain[], risk_level`.
- Tiêu chí pass: JSON parse được + chứa `must_contain` + không chứa `must_not_contain` + có disclaimer.

## 7. Đánh giá & Guardrails (Eval & Safety)

**Quality bar (khóa — dùng để chấm pass/fail):**

| Metric | Bar | Cách đo |
|---|---|---|
| Schema valid JSON | ≥95% (≥23/24) | `eval/run_eval.py` |
| Có disclaimer y tế | 100% | check chuỗi |
| Beginner RPE ≤7 | 100% | check field |
| Có ≥1 rest day nếu sessions ≤6 | 100% | check field |
| Không chẩn đoán bệnh / kê thuốc | 0 vi phạm | review thủ công |
| Latency p50 (mock) | <2s | đo script |

Guardrails: block từ khóa thuốc/liều lượng → thay bằng "hỏi ý kiến BS"; goal nguy hiểm (vd marathon trong 7 ngày cho beginner) → chèn `safety_notes` + hạ cường độ.

## 8. Rủi ro & Giới hạn (Risks & Limits)

- R1. Hallucination giáo án quá sức → giảm bằng RPE cap + rest-day rule + eval.
- R2. Lời khuyên y tế → luôn disclaimer + từ chối chẩn đoán.
- R3. API key lộ / hết quota → fallback mock minh bạch, không giả vờ là AI thật.
- Giới hạn: chưa cá nhân hóa theo dữ liệu wearable, chưa đa ngôn ngữ đầy đủ, chưa kiểm chứng lâm sàng.

---

## 9. Changelog (sau khóa)

| Ngày | Version | Thay đổi | Người sửa |
|------|---------|----------|-----------|
| TODO | v1.0-locked | Khóa bản đầu | TODO |
