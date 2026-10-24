import json

import pytest
from fastapi.testclient import TestClient

import app as app_module

client = TestClient(app_module.app)

SAMPLE = """Traceback (most recent call last):
  File "app.py", line 12, in <module>
    print(user["name"])
KeyError: 'name'"""


class FakeCompletions:
    def create(self, model, messages, temperature):
        payload = {
            "root_cause": "The dict 'user' has no key 'name'.",
            "explanation": "You asked for a key that does not exist in the dictionary.",
            "fix_steps": ["Check the keys with user.keys()", "Use user.get('name') for a safe lookup"],
        }

        class Msg:
            content = json.dumps(payload)

        class Choice:
            message = Msg()

        class Resp:
            choices = [Choice()]

        return Resp()


class FakeClient:
    class chat:
        completions = FakeCompletions()


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_index_served():
    r = client.get("/")
    assert r.status_code == 200
    assert "DebugDost" in r.text


def test_explain_without_key_is_503(monkeypatch):
    monkeypatch.delenv("BHARATCODE_API_KEY", raising=False)
    r = client.post("/api/explain", json={"traceback": SAMPLE, "language": "en"})
    assert r.status_code == 503


def test_explain_with_fake_client(monkeypatch):
    monkeypatch.setattr(app_module, "get_client", lambda: FakeClient())
    r = client.post("/api/explain", json={"traceback": SAMPLE, "language": "hi"})
    assert r.status_code == 200
    body = r.json()
    assert body["root_cause"].startswith("The dict")
    assert len(body["fix_steps"]) == 2


def test_explain_rejects_too_short(monkeypatch):
    monkeypatch.setattr(app_module, "get_client", lambda: FakeClient())
    r = client.post("/api/explain", json={"traceback": "x", "language": "en"})
    assert r.status_code == 422
