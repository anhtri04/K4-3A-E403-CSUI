# Stamina Coach — Prototype (`codebase/`)

Prototype CLI sinh giáo án sức bền tuần, **tích hợp gọi AI thật**, fallback mock minh bạch.

## Phân biệt REAL vs MOCK

| Chế độ | Khi nào | Dấu hiệu |
|---|---|---|
| `REAL` | Có `OPENAI_API_KEY` trong `.env` | Log `[REAL] model=...`, gọi HTTP OpenAI-compatible |
| `MOCK` | Không có key / `--mock` / lỗi mạng | Log `[MOCK]`, dùng `mock_engine.py` (rule-based) |

> Quy chế: **ghi rõ phần mock** — mọi output mock đều có field `"engine": "mock"` và banner text.

## Cài đặt

```bash
pip install -r requirements.txt
cp .env.example .env
# sửa .env: OPENAI_API_KEY=sk-... (bỏ trống để test mock)
```

## Chạy

```bash
python app.py plan --level beginner --goal "chạy 5km trong 30 phút" --sessions 3
python app.py plan --level beginner --goal "test" --sessions 3 --mock
python app.py demo   # chạy 3 ví dụ mẫu
```

Output: bảng text + file JSON trong `outputs/` (vd `outputs/plan_*.json`).

## Cấu trúc

```
codebase/
├── app.py            # CLI chính
├── ai_client.py      # gọi AI thật (OpenAI-compatible), timeout + retry 1 lần
├── mock_engine.py    # rule-based fallback, gắn engine=mock
├── prompt.py         # system/user prompt (đồng bộ spec.md §5)
├── validator.py      # kiểm tra RPE cap, rest-day, disclaimer
├── requirements.txt
├── .env.example
└── MOCK.md           # mô tả chi tiết phần mock
```

## Biến môi trường

- `OPENAI_API_KEY` (bắt buộc cho REAL), `OPENAI_BASE_URL` (mặc định `https://api.openai.com/v1`), `MODEL_NAME` (mặc định `gpt-4o-mini`).
