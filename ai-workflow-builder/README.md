# Visual AI Workflow Builder

A node-based visual workflow engine that evaluates natural language inputs against AI decision steps (`YES`/`NO`), routes branching paths dynamically, and orchestrates executions with Inngest and Groq LLMs.

---

## Tech Stack

- **Framework**: Next.js 15 (App Router, React 19, TypeScript, Tailwind CSS)
- **Canvas / Flow**: `@xyflow/react` (React Flow v12)
- **Workflow Orchestration**: Inngest (Durable functions, step retries, run traces)
- **LLM Inference**: Groq API (`qwen/qwen3.6-27b` via OpenAI SDK)

---

## Core Features

1. **Interactive Graph Canvas**:
   - Add, edit, connect, and delete **Decision Nodes** and **Terminal Action Nodes**.
   - Distinct source handles for `YES` (emerald) and `NO` (rose) branches with smoothstep bezier connections.
2. **AI-Powered Branching**:
   - Evaluates input scenarios step-by-step against node prompts.
   - Strictly enforces binary `YES` or `NO` completions with constrained output tokens.
3. **Live Execution Feedback**:
   - Traversed edges animate dynamically along the selected path.
   - Visited nodes illuminate in green (`YES`), red (`NO`), or amber (`Action`).
4. **Execution Logs & Inspection**:
   - Built-in slide-out trace drawer displaying timestamps, prompts, and evaluation outputs.
   - Direct integration link to the Inngest execution dashboard.
5. **Portability & Persistence**:
   - Auto-save to `localStorage`.
   - Export and import graphs as formatted JSON files.

---

## Getting Started

### 1. Environment Configuration

Create a `.env.local` file in the root directory:

```env
GROQ_API_KEY=your_groq_api_key
INNGEST_DEV=1
## 2. Install Dependencies
'''
npm install
'''
## 3. Start Development Servers
In your terminal run:
```
npm run dev
```
And in a second terminal for the Inngest Dev Server:
```
npx inngest-cli@latest dev
```
The web UI is at: http://localhost:3000
The Inngest Dashboard is at: http://localhost:8288
