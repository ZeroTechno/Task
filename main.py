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
