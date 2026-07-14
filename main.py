from fastapi import FastAPI, HTTPException

app = FastAPI()

# In-memory database
tasks = [
    {"id": 1, "title": "Finish Stage 1", "done": True},
    {"id": 2, "title": "Build Stage 2 of CRUD", "done": False},
    {"id": 3, "title": "Go for a run", "done": False}
]

@app.get("/")
def get_api_info():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health")
def get_health():
    return {"status": "ok"}

# GET all tasks
@app.get("/tasks")
def get_tasks():
    return tasks

# GET single task via path parameter
@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
