import { inngest } from "./client";
import OpenAI from "openai";

interface WorkflowNode {
  id: string;
  data: {
    label: string;
    prompt: string;
  };
}

interface WorkflowEdge {
  id: string;
  source: string;
  target: string;
  sourceHandle: "yes" | "no";
}

interface ExecutionEventData {
  inputContext: string;
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
}

export const executeWorkflow = inngest.createFunction(
  { id: "execute-ai-workflow", triggers: [{ event: "workflow/execute" }] },
  async ({ event, step }) => {
    const { inputContext, nodes, edges } = event.data as ExecutionEventData;

    const apiKey = process.env.GROQ_API_KEY || "";
    const client = new OpenAI({
      apiKey,
      baseURL: "https://api.groq.com/openai/v1",
    });

    const targetNodeIds = new Set(edges.map((e) => e.target));
    let currentNode = nodes.find((n) => !targetNodeIds.has(n.id)) || nodes[0];

    const executionLog: Array<{
      nodeId: string;
      label: string;
      prompt: string;
      decision: "YES" | "NO";
    }> = [];

    while (currentNode) {
      const activeNode = currentNode;

      const decision = await step.run(`evaluate-${activeNode.id}`, async () => {
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
        return raw.includes("YES") ? "YES" : "NO";
      });

      executionLog.push({
        nodeId: activeNode.id,
        label: activeNode.data.label,
        prompt: activeNode.data.prompt,
        decision,
      });

      const targetHandle = decision.toLowerCase() as "yes" | "no";
      const nextEdge = edges.find(
        (e) => e.source === activeNode.id && e.sourceHandle === targetHandle
      );

      if (nextEdge) {
        currentNode = nodes.find((n) => n.id === nextEdge.target) || (null as any);
      } else {
        currentNode = null as any;
      }
    }

    return {
      status: "completed",
      stepsExecuted: executionLog.length,
      history: executionLog,
    };
  }
);
