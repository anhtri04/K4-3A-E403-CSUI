# AGENTS.md — BuildMate (Track E pivot on `main`)

## Scope warning
- `main` is the Track E pivot (Discord team-coding companion). Branch `legacy/stamina-coach` is the dead fitness-app direction — never merge it, cherry-pick from it, or apply its patterns.
- `spec.md` quality bar froze at CP4 (≥75% overall AND 100% safety on `INJ-*` + `KB-03`, 0 push-main). After that, append to `spec.md §9 Changelog` only; do not edit the bar.

## Run from `codebase/`
```bash
cd codebase
pip install -r requirements.txt
cp .env.example .env   # NEVER commit .env; also never commit `k4_messages.csv`, `codebase/outputs/`, keys, personal info
python app.py explain --symbol "propose_diff" --repo ./sample_repo
python app.py check-tech --proposal "Use SQLite for team MVP with 4 concurrent editors"
python app.py ask-course --question "hạn nộp lab 2 là khi nào"
python app.py propose-diff --task "Add input validation to propose-diff" --repo ./sample_repo
python app.py approve --id P001 --user cli-demo --repo ./sample_repo   # or: discard
python bot.py   # needs DISCORD_TOKEN; slash cmds mirror app.py
```
- Always `cd codebase` first: `bot.py` resolves `TEAM_REPO_SNAPSHOT=./sample_repo` relative to CWD (`app.py` defaults are absolute, bot's are not).
- `.env` loading is anchored to `codebase/.env`, so it works from repo root or `codebase/`.
- No test suite exists (`pytest` is in requirements but there are no tests), no CI/lint/typecheck. Verification = the CLI commands above + eval below.

## Eval (stub until CP3)
```bash
cd eval
python run_eval.py --input golden_set.json --output results_run1.json
```
- `run_eval.py::simulate()` is a deterministic zero-key stub — 100% pass means nothing. Replace it with real `app.py` calls before CP3 and keep both logs. Never edit fails away; analyze top failure in `results.md` / slide 4.
- Golden set must stay ≥20 cases (currently 24), ≥2 per layer ① grounding / ② ambiguity / ③ authority / ④ domain, ≥10 paraphrased from real chat.

## Non-negotiable policy (code enforces this — keep it)
- Chat messages are data, never commands: `opencode_bridge.py:is_attack()` (FORBIDDEN regex: `push.*main`, `rm -rf`, `drop table`, `ignore.*rule`, …) → REFUSE + offer branch patch. `propose-diff` writes only a `.patch.txt` preview; only `approve` creates branch `buildmate/proposal-*` + `gh pr create`. NEVER push to main.
- `ask-course` answers ONLY from `course_kb.json` (`course_kb.py:lookup` → FOUND/CLARIFY/NOT_FOUND/REFUSE). No hit → NOT_FOUND + tag TA, never guess.
- REAL vs MOCK must stay explicit: no `OPENAI_API_KEY` (or AI exception) → `[MOCK]`-prefixed fallback (`ai_client.py`), trace in `codebase/outputs/*.md` with `mocked=true/false`. CP3 video needs ≥1 `mocked=false` trace.

## Gotchas agents miss
- `course_kb.json` holds 2 FAKE announcements (`ANN-001/002`); `sample_repo/` is a tiny fake repo. Replace KB ids with real official announcement ids before measuring.
- Empty `APPROVERS` env = demo mode (anyone may approve, loudly logged). Set `APPROVERS=<discord-id-csv>` for real use. State lives in `BUILDMATE_STATE_DIR` (`codebase/state/`, gitignored).
- `BACKEND=opencode` needs one `opencode serve` per team snapshot (`OPENCODE_SERVER_PASSWORD=secret opencode serve --port 4096`, wd = team snapshot; agents scoped in `codebase/.opencode/agents/` + `codebase/opencode.json`). If the server is down it silently falls back to local — verify with `backend_available()` (`opencode_bridge.py`).
- `course_kb.py:_norm()` strips Vietnamese diacritics; aliases live in the `ALIASES` table — add natural-Vietnamese phrasings there, not new matching logic.
- `approvals.approve()` on push failure leaves branch local (`approved-branch-local`) — that is expected without origin/creds, not a bug.
