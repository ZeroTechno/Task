import json
import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from openai import OpenAI

from src.llm.schema import TriageRequest, TriageResponse, CategoryEnum, UrgencyEnum

load_dotenv()

app = FastAPI(title="Support Message Triage API")

PROMPT_FILE = Path("prompts/triage-v1.md")

def get_client() -> OpenAI:
    return OpenAI(
        base_url=os.environ.get("LLM_BASE_URL", "https://openrouter.ai/api/v1"),
        api_key=os.environ.get("LLM_API_KEY"),
        timeout=30.0,
    )

def load_system_prompt() -> str:
    if not PROMPT_FILE.exists():
        raise RuntimeError(f"Prompt file not found: {PROMPT_FILE}")
    return PROMPT_FILE.read_text(encoding="utf-8")

@app.post("/triage")
def triage_message(request: TriageRequest):
    if os.environ.get("LLM_STUB") == "1":
        return TriageResponse(
            category=CategoryEnum.BUG,
            urgency=UrgencyEnum.HIGH,
            confidence=0.95,
            reason="Stub mode active: hardcoded safe fallback response."
        )

    system_prompt = load_system_prompt()
    client = get_client()

    try:
        response = client.chat.completions.create(
            model=os.environ.get("LLM_MODEL", "openrouter/free"),
            temperature=0.0,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps({"text": request.text})},
            ],
        )
        raw_content = response.choices[0].message.content
        return {"raw_response": raw_content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM call failed: {str(e)}")
