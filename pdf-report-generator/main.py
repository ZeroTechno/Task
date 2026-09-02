import os
import sqlite3
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, Response, status
from fastapi.responses import FileResponse
from pydantic import BaseModel

from renderer import generate_pdf

DB_PATH = "report.db"
REPORTS_DIR = "reports"
os.makedirs(REPORTS_DIR, exist_ok=True)

app = FastAPI(title="PDF Report Generator")

def init_reports_table():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_reports_table()

class GenerateReportRequest(BaseModel):
    force: Optional[bool] = False

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/reports")
async def create_report(req: GenerateReportRequest = GenerateReportRequest(), response: Response = None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    today_str = datetime.now().strftime("%Y-%m-%d")

    # Stage 5 Idempotency: Check if a report was already created today
    if not req.force:
        cur.execute("SELECT id, path FROM reports WHERE date(created_at) = ? ORDER BY id DESC LIMIT 1", (today_str,))
        existing = cur.fetchone()
        if existing and os.path.exists(existing[1]):
            conn.close()
            response.status_code = status.HTTP_200_OK
            return {
                "id": existing[0],
                "file": f"/reports/{existing[0]}/file",
                "message": "Report already generated today (idempotent result)"
            }

    # Generate new report entry
    now = datetime.now()
    cur.execute("INSERT INTO reports (path, created_at) VALUES (?, ?)", ("pending", now))
    report_id = cur.lastrowid
    conn.commit()

    # Render PDF file
    file_path = os.path.join(REPORTS_DIR, f"{report_id}.pdf")
    await generate_pdf(output_path=file_path)

    # Update path in database
    cur.execute("UPDATE reports SET path = ? WHERE id = ?", (file_path, report_id))
    conn.commit()
    conn.close()

    response.status_code = status.HTTP_201_CREATED
    return {
        "id": report_id,
        "file": f"/reports/{report_id}/file"
    }

@app.get("/reports/{report_id}")
def get_report_metadata(report_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, path, created_at FROM reports WHERE id = ?", (report_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Report not found")

    return {
        "id": row[0],
        "created_at": row[2],
        "file": f"/reports/{row[0]}/file"
    }

@app.get("/reports/{report_id}/file")
def download_report_file(report_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT path FROM reports WHERE id = ?", (report_id,))
    row = cur.fetchone()
    conn.close()

    if not row or not os.path.exists(row[0]):
        raise HTTPException(status_code=404, detail="Report file not found")

    return FileResponse(
        path=row[0],
        media_type="application/pdf",
        filename=f"report_{report_id}.pdf"
    )
