"""Gọi AI THẬT qua OpenAI-compatible Chat Completions API (urllib, không cần SDK)."""
import json
import os
import urllib.request

def call_real_ai(system: str, user: str, timeout_s: int = 30) -> dict:
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        raise RuntimeError("Thiếu OPENAI_API_KEY")
    base = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.getenv("MODEL_NAME", "gpt-4o-mini")
    body = {
        "model": model,
        "temperature": 0.7,
        "max_tokens": 800,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    req = urllib.request.Request(
        f"{base}/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
    )
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    text = payload["choices"][0]["message"]["content"]
    # Bóc JSON trong markdown code fence nếu có
    t = text.strip()
    if "```" in t:
        t = t.split("```")[1]
        if t.startswith("json"):
            t = t[4:]
    data = json.loads(t.strip())
    data["engine"] = f"real:{model}"
    data["mock"] = False
    return data
