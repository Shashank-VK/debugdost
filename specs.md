# DebugDost — BharatCode Build League entry (LEAN)

**What:** paste a Python traceback / error message → root cause + plain-language explanation (English / Hindi / Kannada) + concrete fix steps. Built on BharatCode's model API for the Build League (SDE Intern entry route). Deadline: Oct 25, 2026, 23:59 IST (entry + submission).

**Stack (per main's order):** FastAPI backend + one-page HTML UI. OpenAI Python SDK pointed at `https://bharatcode.ai/api/model/v1`, model `qwen-3.8-27b`, Bearer key from the BharatCode account dashboard (env `BHARATCODE_API_KEY`, never committed).

**Submission:** public GitHub repo `debugdost`, `BharatCode.txt` in repo root (exact required contents to be confirmed from the logged-in BharatCode submission flow), repo link submitted on their page. Hosting: HF Spaces.

**API contract:**
- `GET /` → one-page UI
- `GET /health` → {"status": "ok"}
- `POST /api/explain` {"traceback": str, "language": "en"|"hi"|"kn"} → {"root_cause": str, "explanation": str, "fix_steps": [str]}
- No key configured → 503 with a clear message (never a stack trace leak).

**Guardrails:** explanation is for the pasted error only; no generic code generation; the model is instructed to answer in the chosen language and to say when the traceback is insufficient instead of guessing.

**Test fix (2026-10-24 13:12 IST):** `test_explain_with_fake_client` failed with 502 — `SYSTEM_PROMPT.format()` choked on the prompt's literal JSON braces (KeyError 'root_cause'). Fixed by using `.replace("{language}", ...)` instead of `.format()`. All 5 tests pass (pytest, 1.03s).
