import uuid
from fastapi import HTTPException
from Backend.DBMS.db_operations import add_relief_request
from Backend.DBMS.db_operations import (get_all_requests,get_resources_by_category,allocate_resource,get_allocation_history,)
from Backend.NLP.src.keyword_extraction import(
    classify_relief_need,
    extract_people_affected,
)
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
    location: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Location of the flood-affected area",
    )
class ResourceAllocationRequest(BaseModel):
    request_id: str
    resource_name: str
    quantity: int=Field(gt=0)


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
@app.post("/schedule-saved")
def schedule_saved_requests(algorithm: str = "Priority"):
    # Fetch requests saved in PostgreSQL
    saved_requests = get_all_requests()

    # Convert database rows into ReliefRequest objects
    requests = [
        ReliefRequest(
            request_id=str(row["request_id"]),
            location=row["location"],
            need=row["need"],
            urgency_score=float(row["urgency_score"]),
            people_affected=int(row["people_affected"]),
            arrival_time=int(row["arrival_time"]),
        )
        for row in saved_requests
    ]

    # Schedule the requests using the selected algorithm
    scheduled_requests = schedule_requests(requests, algorithm)

    # Calculate scheduling metrics
    average_waiting_time = calculate_average_waiting_time(
        scheduled_requests
    )
    average_response_time = calculate_average_response_time(
        scheduled_requests
    )

    return {
        "algorithm": algorithm,
        "total_requests": len(requests),
        "scheduled_requests": scheduled_requests,
        "average_waiting_time": average_waiting_time,
        "average_response_time": average_response_time,
    }
@app.get("/suggest-resources/{request_id}")
def suggest_resources(request_id: str):
    # Find the saved request
    saved_requests = get_all_requests()

    request = next(
        (
            row for row in saved_requests
            if str(row["request_id"]) == request_id
        ),
        None,
    )

    if request is None:
        raise HTTPException(
            status_code=404,
            detail="Relief request not found.",
        )

    # Choose a suggested resource category from the NLP keywords
    keywords = [
        str(keyword).casefold()
        for keyword in (request["extracted_keywords"] or [])
    ]

    category = None

    if any(word in keywords for word in ["rescue", "trapped", "urgent"]):
        category = "Rescue"
    elif any(word in keywords for word in ["injured", "medicine", "medical"]):
        category = "Medical"
    elif any(word in keywords for word in ["food", "meal", "hungry"]):
        category = "Food"
    elif any(word in keywords for word in ["water", "drinking"]):
        category = "Water"
    elif any(word in keywords for word in ["shelter", "blanket", "clothes"]):
        category = "Shelter"

    if category is None:
        return {
            "request_id": request_id,
            "suggested_category": None,
            "message": "No resource category could be confidently suggested.",
            "available_resources": [],
        }

    # Check the inventory without changing stock
    resources = get_resources_by_category(category)

    return {
        "request_id": request_id,
        "urgency_level": request["urgency_level"],
        "suggested_category": category,
        "available_resources": resources,
        "message": (
            "Resources are available for consideration."
            if resources
            else "No resources are currently available in this category."
        ),
    }
@app.post("/allocate-resource")
def allocate_resource_endpoint(data: ResourceAllocationRequest):
    try:
        result = allocate_resource(
            request_id=data.request_id,
            resource_name=data.resource_name,
            quantity=data.quantity,
        )

        return {
            "success": True,
            "message": "Resource allocated successfully.",
            "allocation": result,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )
@app.get("/allocation-history")
def allocation_history():
    try:
        history = get_allocation_history()

        return {
            "success": True,
            "total_allocations": len(history),
            "allocation_history": history,
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch allocation history: {str(error)}",
        )
@app.post("/analyze-flood")
def analyze_flood(message: FloodMessage):
    result = analyze_flood_message(message.text)
    request_id = str(uuid.uuid4())
    location=message.location.strip()
    need=classify_relief_need(message.text)
    people_affected=extract_people_affected(message.text)
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
            extracted_keywords=result["extracted_keywords"],
            urgency_level=result["urgency_level"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Flood message was analyzed but could not save to the database",) from e
    return{
            "request_id":saved_request_id,
            "message": message.text,
            "saved_to_database":True, **result,
        }

    return {
        "message": message.text,
        **result,
    }