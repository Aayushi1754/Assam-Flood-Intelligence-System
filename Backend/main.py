from fastapi import FastAPI
from app.os_module.models import ReliefRequest
from app.os_module.scheduler import schedule_requests
from app.os_module.metrics import (
    calculate_average_waiting_time,
    calculate_average_response_time
)

app = FastAPI(title="FloodSense")


@app.get("/")
def home():
    return {"message": "FloodSense API is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/schedule")
def schedule(
    requests: list[ReliefRequest],
    algorithm: str = "Priority"
):
    scheduled_requests = schedule_requests(
        requests,
        algorithm
    )

    average_waiting_time = calculate_average_waiting_time(
        scheduled_requests
    )

    average_response_time = calculate_average_response_time(
        scheduled_requests
    )

    return {
        "algorithm": algorithm,
        "scheduled_requests": scheduled_requests,
        "average_waiting_time": average_waiting_time,
        "average_response_time": average_response_time
    }