import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from openai import OpenAI

from src.llm.schema import TriageRequest, TriageResponse, CategoryEnum, UrgencyEnum

load_dotenv()

app = FastAPI(title="Support Message Triage API")

PROMPT_FILE = Path("prompts/triage-v1.md")
QUARANTINE_FILE = Path("logs/quarantine.jsonl")

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

def clean_and_parse_json(raw_text: str) -> dict:
    text = raw_text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    text = text.strip()
    return json.loads(text)

def log_quarantine(user_input: str, raw_output: str, error_msg: str):
    QUARANTINE_FILE.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "prompt_version": "triage-v1",
        "input": user_input,
        "raw_output": raw_output,
        "error": error_msg,
    }
    with open(QUARANTINE_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

@app.post("/triage", response_model=TriageResponse)
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
    model_name = os.environ.get("LLM_MODEL", "openrouter/free")

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": json.dumps({"text": request.text})},
    ]

    # Attempt 1: Standard generation
    raw_response_1 = ""
    try:
        res1 = client.chat.completions.create(
            model=model_name,
            temperature=0.0,
            messages=messages,
        )
        raw_response_1 = res1.choices[0].message.content or ""
        parsed_1 = clean_and_parse_json(raw_response_1)
        return TriageResponse.model_validate(parsed_1)
    except Exception as err1:
        first_error = str(err1)

    # Attempt 2: Repair retry (runs exactly once)
    repair_messages = list(messages)
    repair_messages.append({"role": "assistant", "content": raw_response_1})
    repair_messages.append({
        "role": "user",
        "content": (
            f"Your previous response failed validation with this error: {first_error}. "
            "Fix the issue and return ONLY valid JSON matching the exact schema."
        ),
    })

    try:
        res2 = client.chat.completions.create(
            model=model_name,
            temperature=0.0,
            messages=repair_messages,
        )
        raw_response_2 = res2.choices[0].message.content or ""
        parsed_2 = clean_and_parse_json(raw_response_2)
        return TriageResponse.model_validate(parsed_2)
    except Exception as err2:
        final_error = str(err2)
        log_quarantine(
            user_input=request.text,
            raw_output=raw_response_2 or raw_response_1,
            error_msg=final_error,
        )
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Model output could not be validated against schema after repair attempt.",
                "error": final_error,
            },
        )
