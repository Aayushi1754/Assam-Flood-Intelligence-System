from fastapi import FastAPI
from pydantic import BaseModel, Field

from Backend.OS.models import ReliefRequest
from Backend.OS.scheduler import schedule_requests
from Backend.OS.metrics import (
    calculate_average_waiting_time,
    calculate_average_response_time,
)

from Backend.NLP.src.urgency_score import analyze_flood_message


app = FastAPI(title="FloodSense")


class FloodMessage(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Flood-related message in English, Hindi, Assamese, or Roman Hindi",
    )


@app.get("/")
def home():
    return {"message": "FloodSense API is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/schedule")
def schedule(
    requests: list[ReliefRequest],
    algorithm: str = "Priority",
):
    scheduled_requests = schedule_requests(requests, algorithm)

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
        "average_response_time": average_response_time,
    }


@app.post("/analyze-flood")
def analyze_flood(message: FloodMessage):
    result = analyze_flood_message(message.text)

    return {
        "message": message.text,
        **result,
    }