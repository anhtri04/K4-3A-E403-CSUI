# K4-3A-E403-CSUI — Stamina Coach

> Repository nộp bài chuẩn quy chế: sẵn sàng để BGK / trợ giảng đối chiếu từng hạng mục điểm số.

**Phòng:** E403 | **Nhóm:** CSUI | **Đề tài:** Stamina Coach — Prototype AI huấn luyện sức bền (chạy bộ / thể lực)

## 1. Cấu trúc repository

```
K4-3A-E403-CSUI/
├── README.md          # File này: bản sao README đề bài + bảng phân công vai trò
├── TEAMMATES.md       # Họ tên, mã số học viên, vai trò từng thành viên
├── spec.md            # AI Spec 8 phần đã khóa quality bar
├── demo-slides.pdf    # Slide báo cáo đúng 6 trang, định dạng PDF
├── codebase/          # Mã nguồn prototype có tích hợp gọi AI thật (ghi rõ phần mock)
├── eval/              # Golden set (≥20 case) + bảng kết quả các lượt chạy
├── validation/        # Nhật ký kiểm thử người dùng ngoài nhóm (R6) kèm quote nguyên văn
└── reflection/        # Thu hoạch cá nhân từng thành viên (reflection/<MSHV>_HoTen.md)
```

## 2. Bảng phân công vai trò (đối chiếu điểm)

| Hạng mục chấm | File đối chiếu | Phụ trách (điền tên) | Trạng thái |
|---|---|---|---|
| README + tổng hợp | `README.md`, `TEAMMATES.md` | TODO | ☐ |
| AI Spec 8 phần + quality bar | `spec.md` | TODO | ☐ |
| Prototype + gọi AI thật | `codebase/` | TODO | ☐ |
| Golden set ≥20 + eval runs | `eval/` | TODO | ☐ |
| Kiểm thử người dùng ngoài nhóm (R6) | `validation/` | TODO | ☐ |
| Slide demo 6 trang | `demo-slides.pdf` | TODO | ☐ |
| Thu hoạch cá nhân | `reflection/<MSHV>_*.md` | Từng thành viên | ☐ |

> Cách điền: thay `TODO` bằng `Tên — MSHV`, tick ☐ → ☑ khi xong.

## 3. Chạy nhanh prototype

```bash
cd codebase
pip install -r requirements.txt
cp .env.example .env   # điền OPENAI_API_KEY (hoặc để trống để chạy mock)
python app.py --help
python app.py plan --level beginner --goal "chạy 5km trong 30 phút"
```

- Có API key → gọi AI thật (OpenAI-compatible).
- Không có key → tự fallback sang mock (xem `codebase/MOCK.md`, log ghi rõ `[MOCK]`).

## 4. Chạy eval

```bash
cd eval
python run_eval.py --input golden_set.json --output results_run1.json
```

Kết quả tổng hợp xem tại `eval/results.md`.

## 5. Quy ước nộp bài

- `spec.md` đã khóa quality bar — mọi thay đổi sau khóa phải ghi vào mục Changelog cuối file.
- `validation/` chỉ chứa test với người **ngoài nhóm** (R6). Ghi nguyên văn quote, không paraphrase.
- `reflection/<MSHV>_HoTen.md`: mỗi thành viên 1 file, nêu rõ vai trò, phần việc, cách dùng AI, 1 bài học từ case thất bại.
- `demo-slides.pdf` đúng 6 trang. Nguồn chỉnh sửa: `demo-slides.md` (nếu có).

## 6. Checklist trước khi nộp

- [ ] `TEAMMATES.md` đủ họ tên + MSHV + vai trò
- [ ] `spec.md` đủ 8 phần + quality bar + changelog
- [ ] `codebase/` chạy được, phân biệt rõ REAL vs MOCK
- [ ] `eval/golden_set.json` ≥ 20 case, có bảng kết quả ≥ 1 lượt chạy
- [ ] `validation/` ≥ 1 buổi test ngoài nhóm + quote nguyên văn
- [ ] `reflection/` đủ số file = số thành viên
- [ ] `demo-slides.pdf` mở được, đúng 6 trang
