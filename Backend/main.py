import uuid
import math
from fastapi import HTTPException
from Backend.DBMS.db_operations import add_relief_request
from Backend.DBMS.db_operations import (get_all_requests,get_resources_by_category,allocate_resource,get_allocation_history,get_resource_inventory)
from Backend.resource_requirements import (calculate_required_quantity as calculate_quantity,)
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
class BulkFloodMessage(BaseModel):
    messages:list[FloodMessage]=Field(
        ...,
        min_length=1,
        max_length=100,
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
    keywords = [
        str(keyword).casefold()
        for keyword in (request["extracted_keywords"] or [])
    ]
    category = None

    # Rescue — English, Hindi, Assamese, and Roman Hindi
    if any(word in keywords for word in [
        # English
        "rescue", "trapped", "urgent", "stranded",
        "boat", "boats", "evacuate", "evacuation",

        # Hindi
        "बचाव", "फँसे", "फंसे", "फँस", "फंस",
        "रेस्क्यू", "नाव", "नौका", "उद्धार",

        # Assamese
        "উদ্ধাৰ", "আবদ্ধ", "আৱদ্ধ", "নাও",
        "নাৱেৰে", "উদ্ধাৰ দল",

        # Roman Hindi
        "bachao", "fase", "fasse", "phas",
        "naav", "nao", "rescue boat",
    ]):
        category = "Rescue"

    # Medical
    elif any(word in keywords for word in [
        # English
        "injured", "medicine", "medicines", "medical",
        "doctor", "ambulance", "fever",

        # Hindi
        "चिकित्सा", "डॉक्टर", "दवाइयाँ", "दवाई",
        "घायल", "एम्बुलेंस", "बुखार",

        # Assamese
        "চিকিৎসা", "চিকিৎসক", "আহত",
        "এম্বুলেন্স", "জৰুৰী চিকিৎসা",

        # Roman Hindi
        "dawai", "dawaiyan", "doctor chahiye",
    ]):
        category = "Medical"

    # Food
    elif any(word in keywords for word in [
        # English
        "food", "meal", "hungry", "food packet",
        "food packets",

        # Hindi
        "खाना", "भोजन", "भोजन के पैकेट",
        "खाद्य",

        # Assamese
        "খাদ্য", "খাদ্যৰ পেকেট", "ভোকত",

        # Roman Hindi
        "khana", "bhojan", "food packets",
    ]):
        category = "Food"

    # Drinking water
    elif any(word in keywords for word in [
        # English
        "water", "drinking", "drinking water",
        "water shortage",

        # Hindi
        "पानी", "पीने का पानी", "जल",

        # Assamese
        "পানী", "খোৱাপানী", "খোৱা পানী",

        # Roman Hindi
        "paani", "pani", "peene ka paani",
    ]):
        category = "Water"

    # Shelter
    elif any(word in keywords for word in [
        # English
        "shelter", "blanket", "blankets", "clothes",
        "tarpaulin", "relief camp",

        # Hindi
        "कंबल", "आश्रय", "राहत शिविर",
        "तिरपाल", "कपड़े",

        # Assamese
        "কম্বল", "আশ্ৰয়", "নিৰাপদ স্থান",
        "ত্ৰাণ শিবিৰ", "গৰম কাপোৰ",

        # Roman Hindi
        "kambal", "rahat shivir", "kapde",
    ]):
        category = "Shelter"
    if category is None:
        return {
            "request_id": request_id,
            "suggested_category": None,
            "message": "No resource category could be confidently suggested.",
            "available_resources": [],
        }

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
@app.get("/suggest-resources-bulk")
def suggest_resources_bulk():
    saved_requests = get_all_requests()

    results = []

    for request in saved_requests:
        keywords = [
            str(keyword).casefold()
            for keyword in (request["extracted_keywords"] or [])
        ]

        category = None

        if any(word in keywords for word in [
        "rescue", "trapped", "urgent","बचाव", "फँसे", "फंसे","উদ্ধাৰ", "আবদ্ধ", "নাও" ]):
            category = "Rescue"

        elif any(word in keywords for word in ["injured", "medicine", "medical","चिकित्सा","चिकित्सा सहायता","চিকিৎসা"]):
            category = "Medical"
        elif any(word in keywords for word in [
    "food", "meal", "hungry",
    "food packets", "भोजन", "भोजन के पैकेट",
    "খাদ্য", "খাদ্যৰ পেকেট"
]):
            category = "Food"

        elif any(word in keywords for word in [
    "water", "drinking", "drinking water",
    "पानी", "पीने का पानी",
    "পানী", "খোৱা পানী"
]):
            category = "Water"

        elif any(word in keywords for word in [
    "shelter", "blanket", "clothes",
    "कंबल", "आश्रय",
    "কম্বল", "আশ্ৰয়"
]):
            category = "Shelter"

        if category is None:
            results.append({
                "request_id": request["request_id"],
                "location": request["location"],
                "urgency_level": request["urgency_level"],
                "suggested_category": None,
                "available_resources": [],
                "message": "No resource category could be confidently suggested."
            })
            continue

        resources = get_resources_by_category(category)

        results.append({
            "request_id": request["request_id"],
            "location": request["location"],
            "urgency_level": request["urgency_level"],
            "suggested_category": category,
            "available_resources": resources,
            "message": (
                "Resources are available for consideration."
                if resources
                else "No resources are currently available in this category."
            )
        })

    return {
        "total_requests": len(results),
        "suggestions": results
    }

@app.get("/calculate-resource-requirements")
def calculate_resource_requirements_endpoint(
    need: str,
    people_affected: int,
):
    try:
        quantity = calculate_quantity(
            need=need,
            people_affected=people_affected,
        )

        return {
            "need": need,
            "people_affected": people_affected,
            "required_quantity": quantity,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )
@app.post("/analyze-flood-bulk")
def analyze_flood_bulk(bulk_message: BulkFloodMessage):
    results = []
    for message in bulk_message.messages:
        result = analyze_flood_message(message.text)
        request_id = str(uuid.uuid4())
        need = classify_relief_need(message.text)
        people_affected = extract_people_affected(message.text)
        try:
            saved_request_id = add_relief_request(
                request_id=request_id,
                location=message.location.strip(),
                need=need,
                urgency_score=float(result["urgency_score"]),
                people_affected=people_affected,
                arrival_time=0,
                source_text=message.text,
                extracted_keywords=result["extracted_keywords"],
                urgency_level=result["urgency_level"],
            )
            results.append({
                "request_id": saved_request_id,
                "location": message.location,
                "need": need,
                "people_affected": people_affected,
                "saved_to_database": True,
                **result,
            })
        except Exception as e:
            results.append({
                "location": message.location,
                "saved_to_database": False,
                "error": str(e),
            })
    return {
        "total_messages": len(bulk_message.messages),
        "successfully_saved": sum(
            1 for item in results
            if item["saved_to_database"]
        ),
        "results": results,
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
@app.post("/allocate-resources-by-schedule")
def allocate_resources_by_schedule(algorithm: str = "Priority"):

    # 1. Get all requests
    saved_requests = get_all_requests()

    # Only process pending requests
    pending_requests = [
        row for row in saved_requests
        if row["status"] == "pending"
    ]

    # 2. Convert pending requests into scheduler objects
    requests = [
        ReliefRequest(
            request_id=str(row["request_id"]),
            location=row["location"],
            need=row["need"],
            urgency_score=float(row["urgency_score"]),
            people_affected=int(row["people_affected"]),
            arrival_time=int(row["arrival_time"]),
        )
        for row in pending_requests
    ]

    # 3. Schedule requests using selected algorithm
    scheduled_requests = schedule_requests(requests, algorithm)

    # 4. Prepare inventory and allocation report
    inventory = get_resource_inventory()
    allocation_results = []

    for scheduled in scheduled_requests:

        request_id = str(scheduled["request_id"])

        # Find the original database request
        request = next(
            (
                row for row in pending_requests
                if str(row["request_id"]) == request_id
            ),
            None,
        )

        if request is None:
            continue

        need = str(request["need"]).strip().lower()
        people = request["people_affected"]

        # 5. Match request to a resource
        resource_mapping = {
            "food": "Food packets",
            "rescue": "Rescue boat",
            "medical": "First Aid Kits",
            "water": "Drinking water",
            "shelter": "Blankets",
        }

        resource_name = resource_mapping.get(need)

        if resource_name is None:
            allocation_results.append({
                "request_id": request_id,
                "status": "skipped",
                "message": f"No resource mapping for {need}.",
            })
            continue

        # 6. Calculate required quantity
        try:
            quantity = calculate_quantity(
                need=need,
                people_affected=people,
            )

        except ValueError as error:
            allocation_results.append({
                "request_id": request_id,
                "status": "skipped",
                "message": str(error),
            })
            continue

        # Check available stock before allocation
        resource = next(
            (
                item for item in inventory
                if item["resource_name"] == resource_name
            ),
            None,
        )

        if resource is None:
            allocation_results.append({
                "request_id": request_id,
                "status": "skipped",
                "message": f"{resource_name} not found in inventory.",
            })
            continue

        if resource["available_quantity"] < quantity:
            allocation_results.append({
                "request_id": request_id,
                "status": "insufficient_stock",
                "resource": resource_name,
                "required_quantity": quantity,
                "available_quantity": resource["available_quantity"],
            })
            continue

        # 7. Allocate and deduct inventory
        try:
            result = allocate_resource(
                request_id=request_id,
                resource_name=resource_name,
                quantity=quantity,
            )

            # Update local inventory for the next request
            resource["available_quantity"] -= quantity

            allocation_results.append({
                "request_id": request_id,
                "status": "allocated",
                "allocation": result,
            })

        except ValueError as error:
            allocation_results.append({
                "request_id": request_id,
                "status": "failed",
                "message": str(error),
            })

    return {
        "algorithm": algorithm,
        "total_pending_requests": len(pending_requests),
        "allocation_results": allocation_results,
    }
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