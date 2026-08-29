import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from src.llm.schema import TriageRequest, TriageResponse, CategoryEnum, UrgencyEnum

load_dotenv()

app = FastAPI(title="Support Message Triage API")

@app.post("/triage", response_model=TriageResponse)
def triage_message(request: TriageRequest):
    # Check if Stub Mode is active
    if os.environ.get("LLM_STUB") == "1":
        return TriageResponse(
            category=CategoryEnum.BUG,
            urgency=UrgencyEnum.HIGH,
            confidence=0.95,
            reason="Stub mode active: hardcoded safe fallback response."
        )

    # In Stage 2+, real model integration will be called here
    return TriageResponse(
        category=CategoryEnum.OTHER,
        urgency=UrgencyEnum.LOW,
        confidence=0.0,
        reason="Real LLM call not yet configured in Stage 1."
    )
