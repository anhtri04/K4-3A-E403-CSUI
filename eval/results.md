# eval — golden set + runs

- `golden_set.json`: 24 cases (≥20 required). Coverage: ≥2 per layer ① grounding / ② ambiguity / ③ authority / ④ domain + 8–10 normal + 2–4 rare. ≥10 paraphrased from real chat (tagged `source`).
- `run_eval.py`: offline stub first pass (deterministic, zero keys). Replace `simulate()` with real `app.py` calls before CP3 and keep both logs.
- Quality bar (frozen CP4): **≥75% (≥18/24) AND 100% on safety (INJ-* + KB-03), 0 push-main.**

## Run 1 (stub — replace with real at CP3)

```
python run_eval.py --input golden_set.json --output results_run1.json
```

| Run | Date | Pass | Safety | Bar met? | Top failure |
|---|---|---|---|---|---|
| run1 (stub simulator, 17/9) | 100% (24/24) | 100% (4/4) | YES vs bar | Stub only — real `app.py` + LLM run pending at CP3; then re-run full set, pick 1 painful failure + fix |

Full per-case table: `results_run1.json`. Never edit fails away — analyze in slide 4.
