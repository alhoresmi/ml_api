from fastapi import Body, FastAPI, Form, Request
from fastapi.responses import JSONResponse
from tasks import create_task
from celery.result import AsyncResult


app = FastAPI()


@app.post("/predict", status_code=201)
def run_task(payload = Body(...)):
    task = create_task.delay(payload)

    return JSONResponse({"task_id": task.id})


@app.get("/tasks/{task_id}")
def get_status(task_id):
    task = AsyncResult(task_id)
    if not task.ready():
        return JSONResponse(status_code=202, content={'task_id': str(task_id), 'status': 'Processing'})

    result = task.get()

    return JSONResponse(str(result))

