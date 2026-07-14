from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

class TaskCreate(BaseModel):
    title: str

tasks = [
    {"id": 1, "title": "Finish Stage 1", "done": True},
    {"id": 2, "title": "Build Stage 2 of CRUD", "done": False},
    {"id": 3, "title": "Go for a run", "done": False}
]
next_id = 4

@app.get("/")
def get_api_info():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health")
def get_health():
    return {"status": "ok"}

@app.get("/tasks")
def get_tasks():
    return tasks

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

# POST a new task
@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(task_data: TaskCreate):
    global next_id
    clean_title = task_data.title.strip()
    if not clean_title:
        raise HTTPException(status_code=400, detail="Title cannot be empty")
        
    new_task = {"id": next_id, "title": clean_title, "done": False}
    tasks.append(new_task)
    next_id += 1
    return new_task
