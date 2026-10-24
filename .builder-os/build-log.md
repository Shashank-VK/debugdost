# DebugDost build log

- 2026-10-24 (scaffold): FastAPI app + one-page UI + 5 mocked tests written; py_compile OK.
- 2026-10-24 13:12 IST: test_explain_with_fake_client failed 502 — SYSTEM_PROMPT.format() choked on literal JSON braces (KeyError 'root_cause'). Fixed with .replace("{language}", ...). All 5 tests pass.
- 2026-10-24: BharatCode student tier verified (0 of 10M tokens), API key verified live on qwen-3.8-27b (probe: 91 tokens).
- 2026-10-24: HF Space shashankvkaramudi/debugdost created (Gradio + zero-a10g, public), BHARATCODE_API_KEY set as Space secret, app pushed, stage RUNNING. Fix along the way: README colorFrom "orange" rejected (must be red/yellow/green/blue/indigo/purple/pink/gray) — changed to red.
- Secret scan: source-only scan, PASS (no keys/tokens in repo files; key lives only in ~/.config/provider-keys/bharatcode.key and the Space secret store).
