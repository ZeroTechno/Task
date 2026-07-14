from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def get_api_info():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }

@app.get("/health")
def get_health():
    return {"status": "ok"}
