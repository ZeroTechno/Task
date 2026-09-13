import OpenAI from "openai";

export const llm = new OpenAI({
  apiKey: process.env.GROQ_API_KEY || process.env.OPENAI_API_KEY,
  baseURL: "https://api.groq.com/openai/v1",
});

export const LLM_MODEL = "llama-3.1-8b-instant";
