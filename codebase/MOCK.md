# Phần MOCK — khai báo minh bạch

File này liệt kê **chính xác** phần nào là mock để BGK đối chiếu.

## 1. Khi nào dùng mock?

- Không có `OPENAI_API_KEY`, hoặc truyền `--mock`, hoặc gọi REAL timeout/lỗi → fallback.
- `mock_engine.py::generate_plan()` — rule-based, **không gọi mạng**.

## 2. Logic mock

- Beginner: 3 buổi — đi bộ nhanh / chạy nhẹ xen kẽ, RPE ≤6, ≥2 rest days.
- Intermediate: xen kẽ tempo + long run nhẹ, RPE ≤7.
- Luôn chèn `safety_notes` + `disclaimer` tiếng Việt.
- `motivation` xoay vòng 3 mẫu cố định (để dễ phát hiện trong eval).

## 3. Cách nhận biết trong output

- JSON có `"engine": "mock"`, `"mock": true`.
- Log stdout bắt đầu bằng `[MOCK]`.
- File trong `outputs/` có hậu tố `_mock.json`.

## 4. Cam kết

- Không giả vờ mock là AI thật trong demo / eval / validation.
- Bảng `eval/results.md` tách cột `engine=real|mock`.
