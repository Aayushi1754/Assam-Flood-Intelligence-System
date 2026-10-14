import uuid
from fastapi import HTTPException
from Backend.DBMS.db_operations import add_relief_request
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
    request_id = str(uuid.uuid4())
    location="unknown"
    need="Flood assistance"
    people_affected=0
    arrival_time=0
    try:
        saved_request_id=add_relief_request(
            request_id=request_id,
            location=location,
            need=need,
            urgency_score=float(result["urgency_score"]),
            people_affected=people_affected,
            arrival_time=arrival_time,
            source_text=message.text,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Flood message was analyzed but could not save to the database",) from error
    return{
            "request_id":saved_request_id,
            "message": message.text,
            "saved_to_database":True, **result,
        }

    return {
        "message": message.text,
        **result,
    }