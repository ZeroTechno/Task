import uuid
import logging
from datetime import timedelta
from typing import Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, field_validator
import inngest
import inngest.fast_api

# Set up logging so heartbeat messages show in the console
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("report-service")

app = FastAPI(title="Background Job API")

inngest_client = inngest.Inngest(
    app_id="report-api",
    is_production=False,
)

reports_db = {}

class CreateReportRequest(BaseModel):
    topic: str

    @field_validator("topic")
    @classmethod
    def validate_topic(cls, v: str):
        if not v or not v.strip():
            raise ValueError("Topic cannot be empty")
        return v.strip()

# 1. say-hello function
@inngest_client.create_function(
    fn_id="say-hello",
    trigger=inngest.TriggerEvent(event="test/hello"),
)
async def say_hello(ctx: inngest.Context):
    await ctx.step.sleep("wait-a-bit", timedelta(seconds=5))
    return "Hello from the background!"

# 2. make-report background function
@inngest_client.create_function(
    fn_id="make-report",
    trigger=inngest.TriggerEvent(event="report/requested"),
    retries=2,
)
async def make_report(ctx: inngest.Context):
    data = ctx.event.data or {}
    report_id = data.get("id")
    topic = data.get("topic", "general")

    await ctx.step.sleep("do-the-slow-work", timedelta(seconds=8))

    def build_report():
        if topic.lower() == "fail":
            if report_id and report_id in reports_db:
                reports_db[report_id]["status"] = "failed"
            raise Exception("The report oven is broken!")

        result = f"Detailed analysis and summary report for topic: {topic}"
        if report_id and report_id in reports_db:
            reports_db[report_id]["status"] = "done"
            reports_db[report_id]["result"] = result
        return result

    await ctx.step.run("build-report", build_report)
    return {"status": "done", "id": report_id}

# 3. Scheduled cron heartbeat (runs every minute)
@inngest_client.create_function(
    fn_id="heartbeat",
    trigger=inngest.TriggerCron(cron="* * * * *"),
)
async def heartbeat(ctx: inngest.Context):
    pending_count = sum(1 for r in reports_db.values() if r.get("status") == "pending")
    done_count = sum(1 for r in reports_db.values() if r.get("status") == "done")
    failed_count = sum(1 for r in reports_db.values() if r.get("status") == "failed")

    summary = (
        f"[HEARTBEAT] Reports summary -> "
        f"Pending: {pending_count}, Done: {done_count}, Failed: {failed_count}"
    )
    logger.info(summary)
    return summary

# Serve all three functions
inngest.fast_api.serve(
    app,
    inngest_client,
    [say_hello, make_report, heartbeat],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/reports", status_code=status.HTTP_202_ACCEPTED)
async def create_report(req: Optional[dict] = None):
    if not req or "topic" not in req:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required field: topic",
        )

    topic = str(req.get("topic", "")).strip()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Topic cannot be empty",
        )

    report_id = str(uuid.uuid4())[:8]

    reports_db[report_id] = {
        "id": report_id,
        "topic": topic,
        "status": "pending",
        "result": None,
    }

    await inngest_client.send(
        inngest.Event(
            name="report/requested",
            data={"id": report_id, "topic": topic},
        )
    )

    return {"id": report_id, "status": "pending"}

@app.get("/reports/{report_id}")
def get_report(report_id: str):
    report = reports_db.get(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report
