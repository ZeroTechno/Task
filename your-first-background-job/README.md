# Background Job API (FastAPI + Inngest)

An asynchronous background job system built with FastAPI and Inngest. It processes long-running workloads outside the request cycle using the "Fast Door" pattern (returning `202 Accepted` immediately), tracks job state via an eventual consistency polling endpoint, handles retries with backoff, and runs scheduled tasks via a cron heartbeat.

---

## 1. How to Run

### Prerequisites
- Python 3.10+
- Inngest CLI / Node.js (`npx`)

### Start the API Server (Terminal 1)
```bash
pip install fastapi uvicorn inngest
uvicorn main:app --reload --port 8000
### Start the Inngest Dev Server in your 2nd terminal
```bash
npx inngest-cli@latest dev -u http://localhost:8000/api/inngest
```
Access the dashboard at http://localhost:8288

---

## 2. Endpoints & Background Functions
API Endpoints
Method,Path,Status Code,Description
GET,/health,200 OK,"Health check endpoint returning {""status"": ""ok""}."
POST,/reports,202 Accepted,"Fast door: validates input, registers report as pending, dispatches report/requested event, and returns immediately."
POST,/reports,400 Bad Request,Input validation error returned when topic is missing or empty.
GET,/reports/{id},200 OK,"Polling endpoint returning report state (pending, done, or failed) and the completed result."
GET,/reports/{id},404 Not Found,Returned when querying a non-existent report ID.

Inggest Functions
Function ID,Trigger,Type,Description
say-hello,test/hello,Event,Stage 1 smoke test; sleeps for 5s then returns a completion string.
make-report,report/requested,Event,"Runs 8s simulated heavy work (step.sleep), generates report data, and marks status as done. Configured with retries=2."
heartbeat,* * * * *,Cron,"Scheduled job running every minute on the clock; logs counts of pending, done, and failed reports."

---

## 3. Verification & Terminal Proofs

### Stage 2 Proof: Fast Door (202) & Polling
```bash
$ time curl -i -X POST http://localhost:8000/reports \
  -H "Content-Type: application/json" \
  -d '{"topic": "cats"}'
HTTP/1.1 202 Accepted
content-type: application/json

{"id":"09634d54","status":"pending"}
real    0m0.042s

$ curl -s http://localhost:8000/reports/09634d54
{"id":"09634d54","topic":"cats","status":"pending","result":null}

# Polling ~10 seconds later:
$ curl -s http://localhost:8000/reports/09634d54
{"id":"09634d54","topic":"cats","status":"done","result":"Detailed analysis and summary report for topic: cats"}
```

### Stag 3 Proof: Bad Input Rejected (400)
```bash
$ curl -i -X POST http://localhost:8000/reports \
  -H "Content-Type: application/json" \
  -d '{}'
HTTP/1.1 400 Bad Request
content-type: application/json

{"detail":"Missing required field: topic"}
```

## 4. Questions

### Stage 3: Rejection vs. Retry
Why reject bad input at the door while retrying failures?
If a user sends an empty request with no topic, running it again won't fix anything—it's always going to fail, so we stop it right away with a 400 error. But if a job fails because a server hiccups or the internet cuts out for a second, retrying it actually helps because it will probably work once things clear up.
### Stage 4: Cron Expressions
**Which schedule runs every day at 08:00?**
`0 8 * * *` — This tells the timer to kick off at minute 0 of hour 8 (8:00 AM) every single day.
**Which schedule runs every Sunday at 22:00?**
`0 22 * * 0` (or `0 22 * * SUN`) — This tells it to run at minute 0 of hour 22 (10:00 PM), but only when it's Sunday.
