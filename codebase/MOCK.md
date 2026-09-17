# MOCK.md — what is fake and how to tell

- Mock trigger: no `OPENAI_API_KEY` or AI call exception. Every mock line starts with `[MOCK]`.
- `ai_client.mock_reply`: rule templates for check-tech/explain/ask-course/refusal.
- `course_kb.json`: 2 FAKE announcements (ANN-001/002). Replace with real official ids before measuring.
- `sample_repo/`: tiny fake repo for `explain` grep demo.
- `propose-diff`: writes a `.patch.txt` preview, does NOT git push.
- Traces: `codebase/outputs/*.md` record `mocked=true/false` per call. CP3 video must show at least one `mocked=false`.
