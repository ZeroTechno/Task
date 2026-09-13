import { NextResponse } from "next/server";

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  const eventId = searchParams.get("eventId");

  try {
    // 1. Try finding by event ID
    if (eventId) {
      const eventRes = await fetch(`http://localhost:8288/v1/events/${eventId}/runs`, {
        cache: "no-store",
      });
      if (eventRes.ok) {
        const body = await eventRes.json();
        const runs = Array.isArray(body) ? body : body.data || body.runs || [];
        if (runs.length > 0) {
          return NextResponse.json({
            status: runs[0].status,
            output: runs[0].output,
          });
        }
      }
    }

    // 2. Fallback: inspect the most recent run from global runs
    const globalRes = await fetch(`http://localhost:8288/v1/runs`, {
      cache: "no-store",
    });

    if (globalRes.ok) {
      const globalBody = await globalRes.json();
      const runs = Array.isArray(globalBody)
        ? globalBody
        : globalBody.data || globalBody.runs || [];

      // Find the latest run for execute-ai-workflow
      const latestRun = runs.find(
        (r: any) =>
          r.function_id === "execute-ai-workflow" ||
          r.function_name === "execute-ai-workflow" ||
          r.functionID === "execute-ai-workflow"
      ) || runs[0];

      if (latestRun) {
        return NextResponse.json({
          status: latestRun.status,
          output: latestRun.output,
        });
      }
    }

    return NextResponse.json({ status: "Pending" });
  } catch (err: any) {
    return NextResponse.json({ status: "Pending", error: err.message });
  }
}
