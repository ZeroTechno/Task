import { NextResponse } from "next/server";
import { inngest } from "@/inngest/client";

export async function POST(req: Request) {
  try {
    const { inputContext, nodes, edges } = await req.json();

    if (!inputContext) {
      return NextResponse.json(
        { error: "Input context is required" },
        { status: 400 }
      );
    }

    const { ids } = await inngest.send({
      name: "workflow/execute",
      data: {
        inputContext,
        nodes,
        edges,
      },
    });

    return NextResponse.json({
      success: true,
      eventId: ids[0],
      message: "Workflow dispatched to Inngest",
    });
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message || "Failed to dispatch workflow" },
      { status: 500 }
    );
  }
}
