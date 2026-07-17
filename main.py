import os
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

app = FastAPI()

def get_db_connection():
    # Establishes a raw network connection to the Postgres container
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

@app.on_event("startup")
def setup_database():
    """Executes when the app turns on, ensuring our database table exists."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            done BOOLEAN DEFAULT FALSE
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()

class TaskCreate(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

@app.get("/")
def get_api_info():
    return {"name": "Task API", "version": "2.0", "storage": "PostgreSQL"}

@app.get("/health")
def get_health():
    return {"status": "ok"}

@app.get("/tasks")
def get_tasks():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks ORDER BY id ASC;")
    all_tasks = cursor.fetchall()
    cursor.close()
    conn.close()
    return all_tasks

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = %s;", (task_id,))
    task = cursor.fetchone()
    cursor.close()
    conn.close()
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task

@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(task_data: TaskCreate):
    clean_title = task_data.title.strip()
    if not clean_title:
        raise HTTPException(status_code=400, detail="Title cannot be empty")
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING id, title, done;",
        (clean_title, False)
    )
    new_task = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    return new_task

@app.put("/tasks/{task_id}")
def update_task(task_id: int, task_data: TaskUpdate):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM tasks WHERE id = %s;", (task_id,))
    task = cursor.fetchone()
    if not task:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        
    title = task_data.title.strip() if task_data.title is not None else task["title"]
    done = task_data.done if task_data.done is not None else task["done"]
    
    if not title:
        raise HTTPException(status_code=400, detail="Title cannot be empty")

    cursor.execute(
        "UPDATE tasks SET title = %s, done = %s WHERE id = %s RETURNING id, title, done;",
        (title, done, task_id)
    )
    updated_task = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    return updated_task

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM tasks WHERE id = %s;", (task_id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        
    cursor.execute("DELETE FROM tasks WHERE id = %s;", (task_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return
