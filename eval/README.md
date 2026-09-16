# Eval (`eval/`)

- `golden_set.json`: 24 case (≥20 theo quy chế).
- `run_eval.py`: chấm tự động theo quality bar `spec.md` §7 (JSON hợp lệ, disclaimer, RPE cap, rest-day, must_contain / must_not_contain).
- `results.md`: bảng kết quả các lượt chạy (ghi rõ engine real/mock).

```bash
python run_eval.py --input golden_set.json --output results_run1.json --mock
# có key thì bỏ --mock để chấm REAL
```
