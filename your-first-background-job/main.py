import uuid
from datetime import timedelta
from typing import Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import inngest
import inngest.fast_api

app = FastAPI(title="Background Job API")

inngest_client = inngest.Inngest(
    app_id="report-api",
    is_production=False,
)

reports_db = {}

class CreateReportRequest(BaseModel):
    topic: str

@inngest_client.create_function(
    fn_id="say-hello",
    trigger=inngest.TriggerEvent(event="test/hello"),
)
async def say_hello(ctx: inngest.Context):
    await ctx.step.sleep("wait-a-bit", timedelta(seconds=5))
    return "Hello from the background!"

@inngest_client.create_function(
    fn_id="make-report",
    trigger=inngest.TriggerEvent(event="report/requested"),
)
async def make_report(ctx: inngest.Context):
    data = ctx.event.data or {}
    report_id = data.get("id")
    topic = data.get("topic", "general")

    # Step 1: Simulate 8s delay
    await ctx.step.sleep("do-the-slow-work", timedelta(seconds=8))

    # Step 2: Update status
    def build_report():
        result = f"Detailed analysis and summary report for topic: {topic}"
        if report_id and report_id in reports_db:
            reports_db[report_id]["status"] = "done"
            reports_db[report_id]["result"] = result
        return result

    await ctx.step.run("build-report", build_report)
    return {"status": "done", "id": report_id}

inngest.fast_api.serve(
    app,
    inngest_client,
    [say_hello, make_report],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/reports", status_code=status.HTTP_202_ACCEPTED)
async def create_report(req: CreateReportRequest):
    report_id = str(uuid.uuid4())[:8]

    reports_db[report_id] = {
        "id": report_id,
        "topic": req.topic,
        "status": "pending",
        "result": None,
    }

    await inngest_client.send(
        inngest.Event(
            name="report/requested",
            data={"id": report_id, "topic": req.topic},
        )
    )

    return {"id": report_id, "status": "pending"}

@app.get("/reports/{report_id}")
def get_report(report_id: str):
    report = reports_db.get(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report
