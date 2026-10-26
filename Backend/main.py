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
from fastapi import FastAPI,UploadFile,File
from Backend.OS.models import ReliefRequest
from Backend.OS.scheduler import schedule_requests
from Backend.OS.metrics import (
    calculate_average_waiting_time,
    calculate_average_response_time,
)

from Backend.NLP.src.urgency_score import analyze_flood_message
from Backend.NLP.src.ocr import extract_text_from_image
from fastapi import UploadFile,File,HTTPException
import os
import uuid
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(title="FloodSense")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB per image
MAX_IMAGES = 50

os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/extract-image-text")
async def extract_multiple_image_text(
    files: list[UploadFile] = File(...)
):
    if not files:
        raise HTTPException(
            status_code=400,
            detail="Please upload at least one image."
        )

    if len(files) > MAX_IMAGES:
        raise HTTPException(
            status_code=400,
            detail=f"You can upload a maximum of {MAX_IMAGES} images at once."
        )

    allowed_types = {"image/jpeg", "image/png", "image/webp"}
    allowed_extensions = {".jpg", ".jpeg", ".png", ".webp"}

    results = []

    for file in files:
        image_path = None

        try:
            extension = os.path.splitext(file.filename or "")[1].lower()

            if (
                file.content_type not in allowed_types
                or extension not in allowed_extensions
            ):
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "text": "",
                    "message": "Unsupported file. Upload JPG, JPEG, PNG, or WEBP images."
                })
                continue

            contents = await file.read()

            if not contents:
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "text": "",
                    "message": "The uploaded file is empty."
                })
                continue

            if len(contents) > MAX_FILE_SIZE:
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "text": "",
                    "message": "Image exceeds the 10 MB size limit."
                })
                continue

            image_path = os.path.join(
                UPLOAD_DIR,
                f"{uuid.uuid4().hex}{extension}"
            )

            with open(image_path, "wb") as image_file:
                image_file.write(contents)

            result = extract_text_from_image(image_path)

            results.append({
                "filename": file.filename,
                **result
            })

        except Exception as error:
            results.append({
                "filename": file.filename,
                "success": False,
                "text": "",
                "message": f"Could not process image: {str(error)}"
            })

        finally:
            if image_path and os.path.exists(image_path):
                os.remove(image_path)

            await file.close()

    successful = sum(1 for item in results if item["success"])

    return {
        "total_images": len(results),
        "successful_images": successful,
        "failed_images": len(results) - successful,
        "results": results
    }


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
    elif any(word in keywords for word in [
        # English
        "first aid",
        "first aid kit",
        "first aid kits",
        "bandages",
        "bleeding",
        "injured",
        "injury",
    ]):
        category = "first_aid"
    elif any(word in keywords for word in [
        # English
        "medicine",
        "medicines",
        "medical supply",
        "medical supplies",
        "doctor",
        "ambulance",
        "fever",

        # Hindi
        "चिकित्सा", "डॉक्टर", "दवाइयाँ", "दवाई",
        "घायल", "एम्बुलेंस", "बुखार",

        # Assamese
        "চিকিৎসা", "চিকিৎসক", "আহত",
        "এম্বুলেন্স", "জৰুৰী চিকিৎসা",

        # Roman Hindi
        "dawai", "dawaiyan", "doctor chahiye",
    ]):
        category = "medical"

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
        text = message.text.strip()
        location = message.location.strip()

        try:
            urgency_result = analyze_flood_message(text)
            relief_result = classify_relief_need(text)
            people_affected = extract_people_affected(text)

            urgency_categories = relief_result["categories"]
            message_text = text.casefold()

            # Identify the specific resource needed.
            if any(phrase in message_text for phrase in [
                "first aid",
                "first aid kit",
                "first aid kits",
                "bandage",
                "bandages",
            ]):
                need = "first_aid"
                resource_suggestions = ["First Aid Kits"]

            elif any(phrase in message_text for phrase in [
                "medical supplies",
                "medical supply",
                "medicine",
                "medicines",
            ]):
                need = "medical"
                resource_suggestions = ["Medical supplies"]

            else:
                need = (
                    ", ".join(category.lower() for category in urgency_categories)
                    if urgency_categories
                    else "Needs Review"
                )
                resource_suggestions = relief_result["resources"]

            request_id = str(uuid.uuid4())

            saved_request_id = add_relief_request(
                request_id=request_id,
                location=location,
                need=need,
                urgency_score=float(urgency_result["urgency_score"]),
                people_affected=people_affected,
                arrival_time=0,
                source_text=text,
                extracted_keywords=urgency_result["extracted_keywords"],
                urgency_level=urgency_result["urgency_level"],
            )

            results.append({
                "request_id": saved_request_id,
                "message": text,
                "location": location,
                "extracted_keywords": urgency_result["extracted_keywords"],
                "urgency_score": urgency_result["urgency_score"],
                "urgency_level": urgency_result["urgency_level"],
                "matched_urgency_categories": urgency_result["matched_categories"],
                "urgency_category": urgency_result["urgency_level"],
                "resource_suggestions": resource_suggestions,
                "people_affected": people_affected,
                "need": need,
                "saved_to_database": True,
            })

        except Exception as e:
            results.append({
                "message": text,
                "location": location,
                "saved_to_database": False,
                "error": str(e),
            })

    return {
        "total_messages": len(bulk_message.messages),
        "successfully_saved": sum(
            1 for item in results
            if item["saved_to_database"]
        ),
        "failed_messages": sum(
            1 for item in results
            if not item["saved_to_database"]
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
        if str(row.get("status", "")).lower() == "pending"
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

    # 3. Schedule requests
    scheduled_requests = schedule_requests(requests, algorithm)

    # 4. Prepare inventory and results
    inventory = get_resource_inventory()
    allocation_results = []

    # Recognize relief needs and urgency categories
    resource_mapping = {
        "food": ("Food packets", "food"),
        "water": ("Drinking water", "water"),
        "rescue": ("Rescue boat", "rescue"),
        "medical": ("Medical supplies", "medical"),
        "first_aid":("First Aid Kits","medical"),
        "shelter": ("Blankets", "shelter"),

        "rescue_emergency": ("Rescue boat", "rescue"),
        "medical_emergency": ("Medical supplies", "medical"),
        "shelter_relief": ("Blankets", "shelter"),

        # These categories are broad and cannot reliably identify
        # one particular resource.
        "essential_supplies": (None, None),
        "general_information": (None, None),
        "evacuation": ("Rescue boat", "rescue"),
    }

    for scheduled in scheduled_requests:

        request_id = str(scheduled["request_id"])

        request = next(
            (
                row for row in pending_requests
                if str(row["request_id"]) == request_id
            ),
            None,
        )

        if request is None:
            continue

        raw_need = str(request["need"]).strip().lower()
        people = int(request["people_affected"])

        # Accept either a single need or comma-separated needs
        needs = [
            part.strip()
            for part in raw_need.replace(";", ",").split(",")
            if part.strip()
        ]

        # Resolve each need independently
        resolved_needs = []
        for need_item in needs:
            mapped = resource_mapping.get(need_item)

            if mapped and mapped[0] is not None:
                if mapped not in resolved_needs:
                    resolved_needs.append(mapped)

        if not resolved_needs:
            allocation_results.append({
                "request_id": request_id,
                "status": "skipped",
                "message": f"No resource mapping for {raw_need}.",
            })
            continue

        request_allocations = []

        # Allocate each resource independently
        for resource_name, calculation_need in resolved_needs:

            try:
                quantity = calculate_quantity(
                    need=calculation_need,
                    people_affected=people,
                )
            except (ValueError, KeyError) as error:
                request_allocations.append({
                    "resource": resource_name,
                    "status": "skipped",
                    "message": str(error),
                })
                continue

            resource = next(
                (
                    item for item in inventory
                    if item["resource_name"].strip().lower()
                    == resource_name.lower()
                ),
                None,
            )

            if resource is None:
                request_allocations.append({
                    "resource": resource_name,
                    "status": "skipped",
                    "message": f"{resource_name} not found in inventory.",
                })
                continue

            available = int(resource["available_quantity"])

            if available < quantity:
                request_allocations.append({
                    "resource": resource_name,
                    "status": "insufficient_stock",
                    "required_quantity": quantity,
                    "available_quantity": available,
                })
                continue

            try:
                result = allocate_resource(
                    request_id=request_id,
                    resource_name=resource_name,
                    quantity=quantity,
                )

                # Update the local inventory for subsequent allocations
                resource["available_quantity"] -= quantity

                request_allocations.append({
                    "resource": resource_name,
                    "status": "allocated",
                    "quantity": quantity,
                    "allocation": result,
                })

            except ValueError as error:
                request_allocations.append({
                    "resource": resource_name,
                    "status": "failed",
                    "message": str(error),
                })

        successful = [
            item for item in request_allocations
            if item["status"] == "allocated"
        ]

        if successful and len(successful) == len(request_allocations):
            overall_status = "allocated"
        elif successful:
            overall_status = "partially_allocated"
        else:
            overall_status = "skipped"

        allocation_results.append({
            "request_id": request_id,
            "status": overall_status,
            "allocations": request_allocations,
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
    location = message.location.strip()
    need = classify_relief_need(message.text)
    relief_result = classify_relief_need(message.text)

    priority_order = ["Rescue", "Medical", "Water", "Food", "Shelter"]
    message_text = message.text.casefold()

    if any(
        phrase in message_text
        for phrase in [
            "first aid",
            "first aid kit",
            "first aid kits",
            "bandage",
            "bandages",
        ]
    ):
        need = "first_aid"
    elif any(
        phrase in message_text
        for phrase in [
            "medical supplies",
            "medical supply",
            "medicine",
            "medicines",
        ]
    ):
        need = "medical"
    else:
        need = next(
            (
                category.lower()
                for category in priority_order
                if category in relief_result.get("categories", [])
            ),
            "information",
        )

    people_affected = extract_people_affected(message.text)
    arrival_time = 0
    try:
        saved_request_id = add_relief_request(
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
        raise HTTPException(
            status_code=500,
            detail="Flood message was analyzed but could not save to the database",
        ) from e

    return {
        "request_id": saved_request_id,
        "message": message.text,
        "saved_to_database": True,
        **result,
    }