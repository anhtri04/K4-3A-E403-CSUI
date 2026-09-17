# K4-3A-E403-CSUI — BuildMate (Track E · Làn mở)

> Discord-native team coding companion for AI20K build phase. Vibe-code with your team inside a Discord room instead of alone.

**Lớp:** 3A · **Phòng:** E403 · **Cụm:** ____ · **Track:** E — Làn mở (trong phạm vi AI20k)

Old direction (`Stamina Coach`, fitness app for outside market) was invalid for Track E → archived on branch `legacy/stamina-coach`. This `main` is the Track E pivot.

| Họ và Tên | Mã Học Viên | Vai trò chính | Phần việc đảm nhiệm trong dự án |
|---|---|---|---|
| TODO_Name1 | TODO_MSHV1 | Leader + Spec | spec.md §1-§2, canvas, CP forms |
| TODO_Name2 | TODO_MSHV2 | AI Engineer (codebase) | codebase/bot.py, ai_client.py, opencode_bridge.py |
| TODO_Name3 | TODO_MSHV3 | Eval + Validation | eval/golden_set.json, run_eval.py, validation/ logs |
| TODO_Name4 | TODO_MSHV4 | Slide + Demo | demo-slides.md/pdf, dry run, video dự phòng |
|  |  |  |  |

> Fill this table + `TEAMMATES.md` before CP1. Captain's MSSV must be identical on all CP1–CP5 forms.

## 1. What this is (30s)

A bot that lives in a team's Discord room/server, backed by a coding agent (Opencode-compatible) scoped to that team's repo snapshot + an official-only AI20K course KB:

- `@buildmate check-tech <proposal>` — is this tech viable for our project? (grounded, with limits)
- `@buildmate explain <function|class|file>` — what does this code do?
- `@buildmate ask-course <question>` — logistics/course answers **only from official announcements**, else tag TA
- `@buildmate propose-diff <task>` — proposes a unified diff on a **branch**, never pushes to main; human runs `!approve` (human-in-loop)

Safety default: chat messages are **data, not commands**. No auto-push to main, no auto-DM, no personal data answers, no deanonymization.

## 2. Repo structure (per challenge README)

```
K4-3A-E403-CSUI/
├── README.md          ← this file (member table at top)
├── TEAMMATES.md       ← names + MSSV + roles
├── canvas.md          ← CP1 canvas 7 lines
├── spec.md            ← AI Spec (locks at CP4 21:00 17/9, quality bar frozen)
├── demo-slides.md     ← source for 6-page slide → export to demo-slides.pdf at CP5
├── demo-slides.pdf    ← 6-page PDF (submit at CP5 13:00 18/9)
├── codebase/          ← prototype (REAL vs MOCK labelled)
├── eval/              ← golden_set.json (≥20) + run tables
├── validation/        ← outsider trial logs (R6 bonus)
└── reflection/        ← 1 file per member
```

## 3. Quickstart prototype

```bash
cd codebase
pip install -r requirements.txt
cp .env.example .env   # fill OPENAI_API_KEY (OpenAI-compatible) + DISCORD_TOKEN for live bot
# CLI demo (no Discord needed, works for CP2/CP3 video):
python app.py explain --symbol "buildmate_propose_diff" --repo ./sample_repo
python app.py check-tech --proposal "Use SQLite for team MVP with 4 concurrent editors"
python app.py ask-course --question "hạn nộp lab 2 là khi nào"
python app.py propose-diff --task "Add input validation to propose-diff" --repo ./sample_repo
# Without API key → transparent [MOCK] fallback (see codebase/MOCK.md)
```

Live Discord (after CP3, optional):

```bash
python bot.py  # needs DISCORD_TOKEN + OPENAI_API_KEY in .env
```

## 4. Eval

```bash
cd eval
python run_eval.py --input golden_set.json --output results_run1.json
```

See `eval/results.md` for run table vs quality bar.

## 5. Submission checklist

- [ ] `TEAMMATES.md` real names + MSSV
- [ ] `spec.md` §§1–9 complete, quality bar numeric, frozen at CP4
- [ ] `codebase/` runs end-to-end on slice, REAL vs MOCK labelled, ≥1 real AI call trace kept
- [ ] `eval/golden_set.json` ≥20 cases (≥2 per difficulty layer, ≥10 from real chat), ≥1 full run table
- [ ] `validation/` ≥2 outsiders (aim 5, 2 from CP1) + verbatim quotes + Changelog entry
- [ ] `reflection/` 1 file per member
- [ ] `demo-slides.pdf` 6 pages, opens, no broken links
- [ ] No `data/` pack committed, no `.env`/keys, no personal info
