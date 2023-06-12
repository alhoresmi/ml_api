from fastapi import Body, FastAPI, Form, Request
from fastapi.responses import JSONResponse
from worker import create_task
from celery.result import AsyncResult


app = FastAPI()


@app.post("/predict", status_code=201)
def run_task(payload = Body(...)):
    """can we just send response here?
    """
    #task_type = payload["type"]
    #feature_array = payload["features"]
    #task = create_task.delay(int(task_type))
    task = create_task.delay(payload)

    return JSONResponse({"task_id": task.id})


@app.get("/tasks/{task_id}")
def get_status(task_id):
    task_result = AsyncResult(task_id)
    #result = {
    #    "task_id": task_id,
    #    "task_status": task_result.status,
    #    "task_result": task_result.result
    #}
    return JSONResponse(task_result.result)

