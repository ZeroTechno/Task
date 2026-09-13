import { inngest } from "./client";

export const dummyWorkflow = inngest.createFunction(
  { id: "test-workflow" },
  { event: "workflow/test" },
  async ({ event, step }) => {
    return { status: "ready" };
  }
);
