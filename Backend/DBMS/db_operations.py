#updated
from psycopg.rows import dict_row
try:
    from .db import get_connection
except ImportError:
    from db import get_connection


ALLOWED_RESOURCE_CATEGORIES = {
    "Medical",
    "Food",
    "Water",
    "Rescue",
    "Shelter",
}

ALLOWED_REQUEST_STATUSES = {
    "pending",
    "allocated",
    "completed",
}


def get_all_requests():
    """Retrieve all relief requests, including NLP results."""
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT
                    request_id,
                    location,
                    need,
                    urgency_score,
                    people_affected,
                    arrival_time,
                    status,
                    source_text,
                    extracted_keywords,
                    urgency_level
                FROM relief_requests
                ORDER BY arrival_time ASC;
            """)
            return cur.fetchall()


def add_relief_request(
    request_id,
    location,
    need,
    urgency_score,
    people_affected,
    arrival_time,
    source_text=None,
    extracted_keywords=None,
    urgency_level=None,
):
    """Insert a relief request and its NLP results."""
    if extracted_keywords is not None and not isinstance(
        extracted_keywords, (list, tuple)
    ):
        raise ValueError("extracted_keywords must be a list or tuple.")

    keywords = (
        list(extracted_keywords)
        if extracted_keywords is not None
        else None
    )

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO relief_requests (
                    request_id,
                    location,
                    need,
                    urgency_score,
                    people_affected,
                    arrival_time,
                    source_text,
                    extracted_keywords,
                    urgency_level
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING request_id;
            """, (
                request_id,
                location,
                need,
                urgency_score,
                people_affected,
                arrival_time,
                source_text,
                extracted_keywords,
                urgency_level,
            ))

            result = cur.fetchone()
            return result[0]


def get_resource_inventory():
    """Retrieve all resources in the inventory."""
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT
                    resource_id,
                    resource_name,
                    resource_category,
                    available_quantity,
                    unit,
                    warehouse_location
                FROM resource_inventory
                ORDER BY resource_name ASC;
            """)
            return cur.fetchall()


def get_resources_by_category(category):
    """Retrieve available resources belonging to a category."""
    if not isinstance(category, str) or category not in ALLOWED_RESOURCE_CATEGORIES:
        raise ValueError(
            "Category must be Medical, Food, Water, Rescue, or Shelter."
        )

    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT
                    resource_id,
                    resource_name,
                    resource_category,
                    available_quantity,
                    unit,
                    warehouse_location
                FROM resource_inventory
                WHERE resource_category = %s
                  AND available_quantity > 0
                ORDER BY resource_name ASC;
            """, (category,))
            return cur.fetchall()


def allocate_resource(request_id, resource_name, quantity):
    """Allocate a resource, record the allocation, and deduct stock."""
    if (
        not isinstance(quantity, int)
        or isinstance(quantity, bool)
        or quantity <= 0
    ):
        raise ValueError("Quantity must be a positive whole number.")

    with get_connection() as conn:
        with conn.cursor() as cur:
            # Lock the inventory row to prevent concurrent over-allocation.
            cur.execute("""
                SELECT resource_id, available_quantity
                FROM resource_inventory
                WHERE resource_name = %s
                FOR UPDATE;
            """, (resource_name,))

            resource = cur.fetchone()

            if resource is None:
                raise ValueError("Resource not found.")

            resource_id, available = resource

            if available < quantity:
                raise ValueError(
                    f"Insufficient stock. Available: {available}"
                )

            # Check that the request exists and is eligible for allocation.
            cur.execute("""
                SELECT status
                FROM relief_requests
                WHERE request_id = %s
                FOR UPDATE;
            """, (request_id,))

            request = cur.fetchone()

            if request is None:
                raise ValueError("Relief request not found.")

            if request[0] == "completed":
                raise ValueError(
                    "Cannot allocate resources to a completed request."
                )

            # Record the allocation.
            cur.execute("""
                INSERT INTO resource_allocations (
                    request_id,
                    resource_id,
                    quantity
                )
                VALUES (%s, %s, %s);
            """, (request_id, resource_id, quantity))

            # Deduct allocated stock.
            cur.execute("""
                UPDATE resource_inventory
                SET available_quantity = available_quantity - %s
                WHERE resource_id = %s;
            """, (quantity, resource_id))

            # Update the request status.
            cur.execute("""
                UPDATE relief_requests
                SET status = 'allocated'
                WHERE request_id = %s;
            """, (request_id,))

            return {
                "request_id": request_id,
                "resource": resource_name,
                "quantity_allocated": quantity,
            }


def get_pending_requests():
    """Retrieve pending requests, highest urgency first."""
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT
                    request_id,
                    location,
                    need,
                    urgency_score,
                    people_affected,
                    arrival_time,
                    status,
                    extracted_keywords,
                    urgency_level
                FROM relief_requests
                WHERE status = 'pending'
                ORDER BY urgency_score DESC, arrival_time ASC;
            """)
            return cur.fetchall()


def update_request_status(request_id, new_status):
    """Update a request status and report whether the request exists."""
    if new_status not in ALLOWED_REQUEST_STATUSES:
        raise ValueError(
            "Status must be pending, allocated, or completed."
        )

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE relief_requests
                SET status = %s
                WHERE request_id = %s;
            """, (new_status, request_id))

            return cur.rowcount > 0


def get_allocation_history():
    """Retrieve allocation history with request and resource details."""
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT
                    ra.allocation_id,
                    ra.request_id,
                    rr.location,
                    rr.need,
                    ri.resource_name,
                    ri.resource_category,
                    ra.quantity,
                    ri.unit,
                    ri.warehouse_location,
                    ra.allocated_at
                FROM resource_allocations AS ra
                JOIN relief_requests AS rr
                    ON ra.request_id = rr.request_id
                JOIN resource_inventory AS ri
                    ON ra.resource_id = ri.resource_id
                ORDER BY ra.allocated_at DESC;
            """)
            return cur.fetchall()


if __name__ == "__main__":
    # Read-only smoke test; this does not allocate resources.
    try:
        print("All relief requests:")
        for request in get_all_requests():
            print(request)

        print("\nPending requests:")
        for request in get_pending_requests():
            print(request)

        print("\nAll resources:")
        for resource in get_resource_inventory():
            print(resource)

        print("\nAvailable Water resources:")
        for resource in get_resources_by_category("Water"):
            print(resource)

        print("\nAllocation history:")
        for allocation in get_allocation_history():
            print(allocation)

    except Exception as error:
        print("Database operation failed:")
        print(error)