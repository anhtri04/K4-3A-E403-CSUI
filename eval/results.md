# Kết quả Eval — Stamina Coach

> Bảng đối chiếu quality bar `spec.md` §7. Thêm dòng mỗi lượt chạy, không xóa dòng cũ.

## Run 1 — 2026-09-16 — engine=mock

- Lệnh: `python run_eval.py --input golden_set.json --output results_run1.json --mock`
- Kết quả: **24/24 pass (100%)** — file raw: `eval/results_run1.json`
- Ghi chú: mock rule-based; các case high-risk (G07/G12/G16/G22) cần review thủ công phần safety_notes.

| ID | Input tóm tắt | Pass? | Lỗi (nếu có) | Engine |
|----|---------------|-------|--------------|--------|
| G01–G24 | xem `golden_set.json` | TODO | TODO | mock |

## Run 2 — (REAL, khi có API key)

| ID | Pass? | Ghi chú |
|----|-------|---------|
| TODO | TODO | Chạy `python run_eval.py --output results_run2.json` (bỏ `--mock`, cần `OPENAI_API_KEY`) rồi paste tóm tắt vào đây |

## Đối chiếu Quality Bar

| Metric | Bar | Run 1 (mock) | Đạt? |
|---|---|---|---|
| Schema valid JSON | ≥95% | 24/24 (100%) | ☑ |
| Có disclaimer | 100% | 24/24 (100%) | ☑ |
| Beginner RPE ≤7 | 100% | 100% | ☑ |
| Rest day (sessions ≤6) | 100% | 100% | ☑ |
| Vi phạm y tế | 0 | 0 | ☑ |
