import sqlite3
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional

DB_FILE = "tasks.db"

app = FastAPI()

def get_db_connection():
    """Establishes a connection to the SQLite database file."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

@app.on_event("startup")
def setup_database():
    """Initializes the database table and seeds 3 initial tasks if empty."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT 0
        );
    """)
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM tasks;")
    count = cursor.fetchone()[0]
    
    if count == 0:
        initial_tasks = [
            ("Finish Stage 0 setup", True),
            ("Build SQLite read endpoints", False),
            ("Test database persistence", False)
        ]
        cursor.executemany(
            "INSERT INTO tasks (title, done) VALUES (?, ?);",
            initial_tasks
        )
        conn.commit()
        
    cursor.close()
    conn.close()

@app.get("/")
def get_api_info():
    return {"name": "Task API", "version": "3.0", "storage": "SQLite"}

@app.get("/health")
def get_health():
    return {"status": "ok"}

# This is the Helper to convert SQLite Row objects to Python dictionaries
def row_to_dict(row):
    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}

@app.get("/tasks")
def get_tasks():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks ORDER BY id ASC;")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [row_to_dict(row) for row in rows]

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?;", (task_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Task not found")
    return row_to_dict(row)
