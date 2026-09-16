# Demo Slides — Stamina Coach (nguồn nội dung, xuất PDF 6 trang)

> File PDF nộp: `demo-slides.pdf` (đúng 6 trang). File này là nguồn text để chỉnh sửa rồi regenerate.

## Trang 1 — Bìa
- K4-3A-E403-CSUI | Stamina Coach — HLV sức bền AI
- Nhóm CSUI, Phòng E403 | Thành viên: TODO
- One-liner: Nhập trình độ + mục tiêu → nhận giáo án tuần an toàn, cá nhân hóa.

## Trang 2 — Vấn đề & Người dùng
- Vấn đề: người mới tập thiếu giáo án cá nhân, dễ chấn thương/bỏ cuộc.
- 3 persona: mới tập / quay lại sau nghỉ / bận 3 buổi/tuần.
- Non-goals: không chẩn đoán y khoa, không thay PT/BS.

## Trang 3 — Giải pháp & UX Flow
- Input: level, goal, sessions/tuần, constraints → Output JSON: weekly_plan + safety_notes + motivation + disclaimer.
- Flow: nhập profile → validate → gọi AI (REAL/MOCK minh bạch) → render bảng → điều chỉnh khi mệt/đau.
- REAL: OpenAI-compatible; MOCK: rule-based, gắn nhãn rõ.

## Trang 4 — Prompt, Model & Guardrails
- System prompt khóa (spec §5), temp 0.7, schema JSON.
- Guardrails: RPE ≤7 (beginner), ≥1 rest day, block kê thuốc/liều, cảnh báo goal quá sức (vd marathon 7 ngày).
- Validator tự động + review tay case high-risk.

## Trang 5 — Eval & Validation (R6)
- Golden set 24 case (G01–G24), quality bar: JSON ≥95%, disclaimer 100%, RPE/rest 100%, 0 vi phạm y tế.
- Kết quả Run 1 (mock): TODO — xem eval/results.md. Run 2 (real): TODO khi có key.
- Validation ngoài nhóm ≥2 buổi + quote nguyên văn (validation/user_testing_log.md).

## Trang 6 — Demo & Phân công
- Demo: `cd codebase && python app.py plan --level beginner --goal "chạy 5km trong 30 phút" --sessions 3`
- Bảng phân công (README §2) + link repo.
- Next: UI web, lưu lịch sử, tích hợp wearable. Cảm ơn BGK!
