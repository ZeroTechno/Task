from fastapi import FastAPI
import inngest
import inngest.fast_api
from datetime import timedelta

app = FastAPI(title="Background Job API")

inngest_client = inngest.Inngest(
    app_id="report-api",
    is_production=False,
)

@inngest_client.create_function(
    fn_id="say-hello",
    trigger=inngest.TriggerEvent(event="test/hello"),
)
async def say_hello(ctx: inngest.Context):
    # Pass duration using timedelta
    await ctx.step.sleep("wait-a-bit", timedelta(seconds=5))
    return "Hello from the background!"

inngest.fast_api.serve(
    app,
    inngest_client,
    [say_hello],
)

@app.get("/health")
def health():
    return {"status": "ok"}
