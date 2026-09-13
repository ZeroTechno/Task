import { NextResponse } from "next/server";
import { inngest } from "@/inngest/client";
import OpenAI from "openai";

interface WorkflowNode {
  id: string;
  type?: string;
  data: {
    label: string;
    prompt?: string;
    actionType?: string;
  };
}

interface WorkflowEdge {
  id: string;
  source: string;
  target: string;
  sourceHandle: "yes" | "no";
}

export async function POST(req: Request) {
  try {
    const { inputContext, nodes, edges } = await req.json();

    if (!inputContext) {
      return NextResponse.json({ error: "Input context is required" }, { status: 400 });
    }

    inngest.send({
      name: "workflow/execute",
      data: { inputContext, nodes, edges },
    }).catch((err) => console.error("Inngest dispatch error:", err));

    const client = new OpenAI({
      apiKey: process.env.GROQ_API_KEY || "",
      baseURL: "https://api.groq.com/openai/v1",
    });

    const targetNodeIds = new Set(edges.map((e: WorkflowEdge) => e.target));
    let currentNode = nodes.find((n: WorkflowNode) => !targetNodeIds.has(n.id)) || nodes[0];

    const executionLog: Array<{
      nodeId: string;
      label: string;
      type: string;
      decision?: "YES" | "NO";
      action?: string;
    }> = [];

    while (currentNode) {
      const activeNode = currentNode;

      // Check if it's an Action Node
      if (activeNode.type === "actionNode") {
        executionLog.push({
          nodeId: activeNode.id,
          label: activeNode.data.label,
          type: "action",
          action: activeNode.data.actionType || "slack",
        });
        break; // Terminal node reached
      }

      // Otherwise evaluate Decision Node
      const response = await client.chat.completions.create({
        model: "qwen/qwen3.6-27b",
        temperature: 0,
        max_completion_tokens: 10,
        messages: [
          {
            role: "system",
            content:
              "You are an AI decision engine in a workflow. You must answer ONLY with 'YES' or 'NO'. No explanations, no punctuation, strictly YES or NO.",
          },
          {
            role: "user",
            content: `Context / User Input:\n"""${inputContext}"""\n\nQuestion / Condition:\n${activeNode.data.prompt}`,
          },
        ],
      });

      const raw = response.choices[0]?.message?.content?.trim().toUpperCase() || "NO";
      const decision = raw.includes("YES") ? "YES" : "NO";

      executionLog.push({
        nodeId: activeNode.id,
        label: activeNode.data.label,
        type: "decision",
        decision,
      });

      const targetHandle = decision.toLowerCase();
      const nextEdge = edges.find(
        (e: WorkflowEdge) => e.source === activeNode.id && e.sourceHandle === targetHandle
      );

      if (nextEdge) {
        currentNode = nodes.find((n: WorkflowNode) => n.id === nextEdge.target) || null;
      } else {
        currentNode = null;
      }
    }

    return NextResponse.json({
      success: true,
      history: executionLog,
    });
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message || "Failed to execute workflow" },
      { status: 500 }
    );
  }
}
