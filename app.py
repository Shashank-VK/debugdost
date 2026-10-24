"""DebugDost — paste a traceback, get the root cause + a plain-language fix.

FastAPI backend calling BharatCode's OpenAI-compatible model API
(base https://bharatcode.ai/api/model/v1, model qwen-3.8-27b).
The API key comes from the BHARATCODE_API_KEY env var — never hardcoded.
"""
import json
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

BASE_URL = os.environ.get("BHARATCODE_BASE_URL", "https://bharatcode.ai/api/model/v1")
MODEL = os.environ.get("BHARATCODE_MODEL", "qwen-3.8-27b")
STATIC_DIR = Path(__file__).parent / "static"

LANGUAGES = {"en": "English", "hi": "Hindi", "kn": "Kannada"}

SYSTEM_PROMPT = """You are DebugDost, a friendly debugging mentor for beginner Python developers.
The user pastes a Python traceback or error message. Respond with ONLY a JSON object:
{"root_cause": "...", "explanation": "...", "fix_steps": ["...", "..."]}
- root_cause: one short sentence naming the actual cause (file/line/function when visible).
- explanation: plain-language explanation a beginner understands, in the requested language.
- fix_steps: 2-5 concrete steps to fix it, in the requested language.
Explain in {language}. If the traceback is not enough to tell, say so in the explanation instead of guessing.
Never invent library behaviour. Keep code identifiers and error names in English."""


class ExplainRequest(BaseModel):
    traceback: str = Field(min_length=3, max_length=12000)
    language: str = "en"


def get_client():
    """Build the OpenAI client lazily so tests can run without a key."""
    api_key = os.environ.get("BHARATCODE_API_KEY")
    if not api_key:
        return None
    from openai import OpenAI

    return OpenAI(api_key=api_key, base_url=BASE_URL)


def explain_with_model(traceback_text: str, language: str, client) -> dict:
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT.replace("{language}", LANGUAGES[language])},
            {"role": "user", "content": traceback_text},
        ],
        temperature=0.2,
    )
    raw = resp.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        raw = raw[raw.find("{"):]
    data = json.loads(raw)
    return {
        "root_cause": str(data["root_cause"]),
        "explanation": str(data["explanation"]),
        "fix_steps": [str(s) for s in data["fix_steps"]],
    }


app = FastAPI(title="DebugDost")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/api/explain")
def explain(req: ExplainRequest):
    language = req.language if req.language in LANGUAGES else "en"
    client = get_client()
    if client is None:
        raise HTTPException(status_code=503, detail="Model API key not configured on the server.")
    try:
        return explain_with_model(req.traceback, language, client)
    except Exception:
        raise HTTPException(status_code=502, detail="The model could not explain this error. Please try again.")
