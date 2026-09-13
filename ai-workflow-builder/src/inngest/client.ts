import { Inngest } from "inngest";

export const inngest = new Inngest({
  id: "visual-ai-workflow",
  isProduction: process.env.NODE_ENV === "production",
});
