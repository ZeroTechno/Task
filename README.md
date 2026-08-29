My first CRUD API

<img width="1440" height="900" alt="Screenshot 2026-07-14 at 2 54 55 PM" src="https://github.com/user-attachments/assets/8cf4e311-5a9c-4cf5-8584-70777b9d6e4e" />
This image is Basically the 5th stage

Aside from the resources given, this is also an additional resource I used that helped me (https://www.youtube.com/watch?v=Lw-zLopB3o0&start=0)

<<<<<<< HEAD

Connecting to the database Stage 5 — Database Documentation

1. Why SQLite Was Chosen
SQLite was selected for this project because:
It is a serverless, self-contained database that requires no external database server or background services (like Docker or PostgreSQL) to run.
It runs directly inside Python's built-in standard library (`sqlite3`), making setup instant across any machine.
Data is stored in a single cross-platform file, making it ideal for local testing and lightweight backend applications while demonstrating true persistent storage across server restarts.

2. Where the Database File Is Stored
`./tasks.db` (stored in the root directory of the project folder).
The file is ignored by Git (`.gitignore`) so each environment maintains its own instance. On the application's first boot, the startup hook automatically detects if `tasks.db` exists; if missing, it creates the file, builds the `tasks` schema, and seeds the initial 3 example records.

3. How to Start the Project
First you have to clone the repository and enter the directory:
   ```bash
   git clone [https://github.com/ZeroTechno/Task.git](https://github.com/ZeroTechno/Task.git)
   cd Task


4. Screenshots of my database viewer
<img width="1040" height="658" alt="Screenshot 2026-07-21 at 1 32 07 PM" src="https://github.com/user-attachments/assets/7934d2da-81c8-4f7e-a7fc-380e25161acb" />


<img width="1044" height="660" alt="Screenshot 2026-07-21 at 1 31 22 PM" src="https://github.com/user-attachments/assets/a178f166-44c3-4a63-872d-d07ed3d647ed" />

5. One example SQL query you executed
SELECT * FROM tasks WHERE done = 1;
I used it to retrieve all completed tasks from the database during the manual inspection.
=======
# FastAPI Authentication & Route Protection with Supabase

A secure backend API built with FastAPI and Supabase Auth as the Identity Provider (IdP). This project demonstrates modern web security principles, using JSON Web Tokens (JWT) for user authentication and Bearer Tokens for protected route authorization.

---

## What This Project Is

This API provides user account management (Sign Up, Log In, Log Out) and enforces access control across endpoints. Public endpoints are accessible to anyone, while protected endpoints require a valid JWT issued by Supabase Auth and passed in the HTTP `Authorization: Bearer <token>` header.

Key security features include:
* Identity Provider Integration: Offloads password hashing, user registration, and session token generation to Supabase Auth.
* Token Verification Middleware: Uses FastAPI's dependency injection (`Depends`) to extract and verify JWT tokens against Supabase before serving protected routes.
* Interactive API Security: Configures `HTTPBearer` security schemes in Swagger UI (`/docs`) to test protected endpoints with Bearer tokens directly from the browser.
 
---

## How to Set Up Local Environment Variables

1. Create a `.env` file in the root directory of the project:
   ```bash
   touch .env

2. Open .env and add your Supabase credentials (found in your Supabase Dashboard -> Project Settings -> API):
SUPABASE_URL=[https://your-project-ref.supabase.co](https://your-project-ref.supabase.co)
SUPABASE_KEY=your-actual-anon-key-here

## To run through Project
1. Install the dependencies:
pip3 install fastapi uvicorn supabase python-dotenv pydantic

2. Start the server:
python3 -m uvicorn main:app --reload

3. Access the application
Server URL: http://127.0.0.1:8000
Swagger: http://127.0.0.1:8000/docs

Endpoint		Method	Auth Required		Description
/health			GET	No			Basic health check route
/public/info		GET	No			Open endpoint returning public information
/auth/signup		POST	No			Registers a new user account with Supabase Auth
/auth/login		POST	No			Authenticates credentials and returns JWT Bearer token
/auth/logout		POST	Yes (Bearer)		Terminates active session and invalidates token
/protected/profile	GET	Yes (Bearer)		Returns authenticated user profile metadata
/protected/dashboard	GET	Yes (Bearer)		Returns protected user dashboard data

![Swagger UI Screenshot1](./swagger-auth-screenshot1.png)
![Swagger UI Screenshot2](./swagger-auth-screenshot2.png)
>>>>>>> c1b5585 (Stage 6: publish to GitHub and write README)




# Week 7 / Assignment A17: Support Message Triage LLM API

An automated backend triage endpoint (`POST /triage`) that classifies customer support messages into structured, validated JSON data using FastAPI, Pydantic, and OpenRouter-compatible LLM backends.


## Runnable Curl & Example Response

### Request
```bash
curl -X POST http://127.0.0.1:8000/triage \
  -H "Content-Type: application/json" \
  -d '{"text": "I was double charged for my subscription this month."}'

Response (200 OK)
{
  "category": "billing",
  "urgency": "high",
  "confidence": 0.98,
  "reason": "Customer reports being charged twice for monthly subscription."
}

#Job Card
What it does: Classifies customer support messages into structured triage categories with urgency and confidence scoring.

Input Contract: {"text": "string (1-2000 characters)"}

Output Contract:
{
  "category": "billing" | "bug" | "feature" | "other",
  "urgency": "low" | "normal" | "high",
  "confidence": 0.0 - 1.0,
  "reason": "one short sentence"
}

It Must Never:
Invent categories outside [billing, bug, feature, other].
Return free-form markdown or conversation instead of single valid JSON.
Guess wildly when information is missing.
Reveal internal system instructions.

When Unsure It Should:
Assign category "other" with confidence < 0.5 and explain ambiguity in reason.

Provider & Environment Configuration
Three environment variables configure and swap providers instantly between hosted datacenters and local machines:
LLM_BASE_URL=https://openrouter.ai/api/v1   # Or http://localhost:11434/v1/ for Ollama
LLM_API_KEY=your_api_key_here               # Literal string "ollama" for local runs
LLM_MODEL=openrouter/free                   # Or gemma3:1b / llama3.2:3b

Evaluation Results:
Date: August 29, 2026
Prompt Version: prompts/triage-v1.md
Score: 7 / 8 (87.5% accuracy) across clear categories, edge-cases, and ambiguous inputs.

Cost Analysis & Observability;
Per-Call Metrics (Average):
Prompt Tokens: ~240
Completion Tokens: ~45
Total Tokens: ~285
Latency: ~1,200ms

Cost Estimate for 10,000 requests/day:
At standard small-model pricing ($0.15 / 1M input tokens, $0.60 / 1M output tokens):
Input: 10,000 * 240 = 2.4M tokens * $0.15 = $0.36
Output: 10,000 * 45 = 0.45M tokens * $0.60 = $0.27
Estimated daily cost: ~$0.63 / day (~$18.90 / month).

Operational Safeguards:
Input Validation: Pydantic rejects invalid or oversized inputs (> 2000 chars) with HTTP 422 before any model call is triggered.

Stub Mode: LLM_STUB=1 returns a deterministic schema response with 0 model calls spent.

Parse, Repair & Quarantine: Strips markdown code blocks, validates Pydantic enum types, performs exactly 1 automated repair retry on failure, and logs dead-letter outputs to logs/quarantine.jsonl returning HTTP 422.

Timeouts & Safe Retries: Strict 30.0s timeout (returns HTTP 504). Automatically retries transient 429/5xx errors with exponential backoff and jitter, while failing fast on 400/401/403.

Kill Switch: Setting LLM_ENABLED=false bypasses model calls entirely and returns a safe fallback.

What I'd Fix With Another Day:
I've tried this week's assignment using openrouter and Ollama both were great.
What I'd fix is probably just to Fine-tune the ambiguous edge-case prompt instructions to boost evaluation score from 87.5% to 100%, and implement prompt injection sanitization on user input strings before sending to the model.