import json
import os
import random
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status
from openai import OpenAI, APIError, APITimeoutError, AuthenticationError, BadRequestError, PermissionDeniedError
from pydantic import ValidationError

from src.llm.schema import TriageRequest, TriageResponse, CategoryEnum, UrgencyEnum

load_dotenv()

app = FastAPI(title="Support Message Triage API")

PROMPT_FILE = Path("prompts/triage-v1.md")
QUARANTINE_FILE = Path("logs/quarantine.jsonl")
PROMPT_VERSION = "triage-v1"

def get_client() -> OpenAI:
    # Explicit 30.0s timeout and max_retries=0 so custom backoff handles transient failures explicitly
    return OpenAI(
        base_url=os.environ.get("LLM_BASE_URL", "https://openrouter.ai/api/v1"),
        api_key=os.environ.get("LLM_API_KEY"),
        timeout=30.0,
        max_retries=0,
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
        "prompt_version": PROMPT_VERSION,
        "input": user_input,
        "raw_output": raw_output,
        "error": error_msg,
    }
    with open(QUARANTINE_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def call_llm_with_retry(client: OpenAI, model_name: str, messages: list, max_attempts: int = 3):
    """Executes completions with exponential backoff and jitter on 429/5xx/timeouts only."""
    attempt = 0
    while attempt < max_attempts:
        attempt += 1
        try:
            return client.chat.completions.create(
                model=model_name,
                temperature=0.0,
                messages=messages,
            )
        except (AuthenticationError, BadRequestError, PermissionDeniedError) as client_err:
            # 400, 401, 403: Permanent client failures must fail fast with zero retries
            print(f"[FATAL AUTH/CLIENT ERROR] Non-retryable status: {client_err}")
            raise client_err
        except (APITimeoutError, APIError) as transient_err:
            if attempt >= max_attempts:
                raise transient_err
            # Exponential backoff (1s, 2s, 4s) with random jitter
            delay = (2 ** (attempt - 1)) + random.uniform(0.1, 0.5)
            print(f"[RETRY] Transient error {transient_err}. Retrying attempt {attempt + 1} in {delay:.2f}s...")
            time.sleep(delay)

@app.post("/triage", response_model=TriageResponse)
def triage_message(request: TriageRequest):
    # 1. Kill Switch Check (LLM_ENABLED=false)
    if os.environ.get("LLM_ENABLED", "true").lower() == "false":
        return TriageResponse(
            category=CategoryEnum.OTHER,
            urgency=UrgencyEnum.NORMAL,
            confidence=0.0,
            reason="Kill switch active: LLM disabled, safe fallback returned."
        )

    # 2. Stub Mode Check
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

    start_time = time.time()
    repairs_needed = 0
    prompt_tokens = 0
    completion_tokens = 0
    raw_response_1 = ""

    # Initial Attempt
    try:
        res1 = call_llm_with_retry(client, model_name, messages)
        if res1.usage:
            prompt_tokens += res1.usage.prompt_tokens or 0
            completion_tokens += res1.usage.completion_tokens or 0
        raw_response_1 = res1.choices[0].message.content or ""
        parsed_1 = clean_and_parse_json(raw_response_1)
        result = TriageResponse.model_validate(parsed_1)

        duration_ms = int((time.time() - start_time) * 1000)
        print(f"[METRICS] version={PROMPT_VERSION} model={model_name} prompt_tokens={prompt_tokens} "
              f"completion_tokens={completion_tokens} duration_ms={duration_ms} repairs={repairs_needed}")
        return result
    except APITimeoutError:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="Upstream LLM timed out.")
    except (AuthenticationError, BadRequestError, PermissionDeniedError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as err1:
        first_error = str(err1)

    # Repair Retry (Only once)
    repairs_needed = 1
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
        res2 = call_llm_with_retry(client, model_name, repair_messages)
        if res2.usage:
            prompt_tokens += res2.usage.prompt_tokens or 0
            completion_tokens += res2.usage.completion_tokens or 0
        raw_response_2 = res2.choices[0].message.content or ""
        parsed_2 = clean_and_parse_json(raw_response_2)
        result = TriageResponse.model_validate(parsed_2)

        duration_ms = int((time.time() - start_time) * 1000)
        print(f"[METRICS] version={PROMPT_VERSION} model={model_name} prompt_tokens={prompt_tokens} "
              f"completion_tokens={completion_tokens} duration_ms={duration_ms} repairs={repairs_needed}")
        return result
    except Exception as err2:
        final_error = str(err2)
        log_quarantine(
            user_input=request.text,
            raw_output=raw_response_2 or raw_response_1,
            error_msg=final_error,
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Model output could not be validated against schema after repair attempt.",
                "error": final_error,
            },
        )
