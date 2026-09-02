An automated backend pipeline that queries an SQLite transactional database, computes aggregation metrics using pure SQL, renders a multi-page PDF document via headless Chromium (Playwright), and serves the resulting artifact by link with built-in daily idempotency.

---

## 1. Dataset Selection

- **Chosen Dataset:** Option A — The Little Shop
- **Schema:** `orders` table (`id`, `customer`, `product`, `amount`, `created_at`).
- **Volume:** 200 random orders spanning the last 30 days across 6 distinct product catalog items.

---

## 2. Aggregation SQL Queries

The report is powered by four primary SQL aggregations:

```sql
-- 1. Total number of orders
SELECT COUNT(*) FROM orders;

-- 2. Total revenue
SELECT ROUND(COALESCE(SUM(amount), 0), 2) FROM orders;

-- 3. Top 5 products by revenue
SELECT product, ROUND(SUM(amount), 2) AS revenue, COUNT(*) AS count
FROM orders
GROUP BY product
ORDER BY revenue DESC
LIMIT 5;

-- 4. Orders per day for the last 7 days
SELECT created_at, COUNT(*) AS order_count, ROUND(SUM(amount), 2) AS revenue
FROM orders
GROUP BY created_at
ORDER BY created_at DESC
LIMIT 7;

## 3. How to Run
Prerequisites
- Python 3.10+
- Playwright Chromium installed (playwright install chromium)
Insitallation:
pip install fastapi uvicorn playwright
playwright install chromium

# Seed the database (~200 orders, safe to run repeatedly)
python3 seed.py
Start the API Server:
uvicorn main:app --reload --port 8000


## 4. Verification & Terminal Proofs
stage 4 proof: Generate and Serve by Link:
$ time curl -i -X POST http://localhost:8000/reports
HTTP/1.1 201 Created
content-type: application/json

{"id":1,"file":"/reports/1/file"}
real    0m2.140s

$ curl -o downloaded-report.pdf http://localhost:8000/reports/1/file
# File downloaded successfully and verified as a multi-page PDF.
stage 5 proof: Idempotency (Ask Twice, Get One)
$ curl -s -X POST http://localhost:8000/reports
{"id":1,"file":"/reports/1/file","message":"Report already generated today (idempotent result)"}

$ curl -s -X POST http://localhost:8000/reports
{"id":1,"file":"/reports/1/file","message":"Report already generated today (idempotent result)"}

# Forced re-generation:
$ curl -s -X POST http://localhost:8000/reports -H "Content-Type: application/json" -d '{"force": true}'
{"id":2,"file":"/reports/2/file"}

## 5. Architectural Reflection Questions
Stage 4: Moving Work to Background Jobs
At what point would you move this work out of the request?
I would move PDF generation out of the request into an asynchronous background job worker the moment average generation latency exceeds 500 milliseconds—or when dataset sizes grow beyond a few hundred rows—because holding open synchronous HTTP connections ties up server worker threads and degrades user experience under concurrent load.

Stage 5: Idempotency Protection & Cost of Failure
What does your check protect against, and where could a missing check cost money?
This check protects against redundant compute and disk storage usage caused by users double-clicking the report button or automated network retry loops. In a real-world system with downstream side effects (such as automated billing statement generation or paid third-party SMS/email dispatch), missing this idempotency guard would directly incur unnecessary transactional processing costs and send duplicate charges or notifications to customers.

## 6. Generated Report Preview
Multi-page document layout rendering all 200 orders without split rows.
Table headers (<thead>) repeat automatically on every page break via print CSS.
