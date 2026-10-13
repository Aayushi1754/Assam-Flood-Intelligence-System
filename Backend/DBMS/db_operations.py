
from psycopg.rows import dict_row
from db import get_connection


def get_all_requests():
    """Retrieve all flood-relief requests."""
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
                    status
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
    source_text=None
):
    """Insert a new flood-relief request."""
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
                    source_text
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING request_id;
            """, (
                request_id,
                location,
                need,
                urgency_score,
                people_affected,
                arrival_time,
                source_text
            ))

            return cur.fetchone()[0]


def get_resource_inventory():
    """Retrieve the available resource inventory."""
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT
                    resource_id,
                    resource_name,
                    available_quantity,
                    unit,
                    warehouse_location
                FROM resource_inventory
                ORDER BY resource_name ASC;
            """)
            return cur.fetchall()


def allocate_resource(request_id, resource_name, quantity):
    """
    Allocate a resource to a relief request.
    Record the allocation and deduct available stock.
    """
    if not isinstance(quantity, int) or isinstance(quantity, bool):
        raise ValueError("Quantity must be a whole number.")

    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero.")

    with get_connection() as conn:
        with conn.cursor() as cur:

            # Lock the resource row to protect stock from
            # simultaneous allocation attempts.
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

            # Verify that the request exists.
            cur.execute("""
                SELECT status
                FROM relief_requests
                WHERE request_id = %s;
            """, (request_id,))

            request = cur.fetchone()

            if request is None:
                raise ValueError("Relief request not found.")

            # Record the allocation.
            cur.execute("""
                INSERT INTO resource_allocations (
                    request_id,
                    resource_id,
                    quantity
                )
                VALUES (%s, %s, %s);
            """, (request_id, resource_id, quantity))

            # Deduct stock.
            cur.execute("""
                UPDATE resource_inventory
                SET available_quantity = available_quantity - %s
                WHERE resource_id = %s;
            """, (quantity, resource_id))

            # Mark the request as allocated.
            cur.execute("""
                UPDATE relief_requests
                SET status = 'allocated'
                WHERE request_id = %s;
            """, (request_id,))

            return {
                "request_id": request_id,
                "resource": resource_name,
                "quantity_allocated": quantity
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
                    status
                FROM relief_requests
                WHERE status = 'pending'
                ORDER BY urgency_score DESC, arrival_time ASC;
            """)
            return cur.fetchall()


def update_request_status(request_id, new_status):
    """Update a request's status and report whether it exists."""
    allowed_statuses = {
        "pending",
        "allocated",
        "completed"
    }

    if new_status not in allowed_statuses:
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
# function of history

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
    # Read-only smoke test: this does not allocate resources.
    try:
        print("All relief requests:")
        for request in get_all_requests():
            print(request)

        print("\nPending requests:")
        for request in get_pending_requests():
            print(request)

        print("\nResource inventory:")
        for resource in get_resource_inventory():
            print(resource)

        print("\nAllocation history:")
        for allocation in get_allocation_history():
            print(allocation)

    except Exception as error:
        print("Database operation failed:")
        print(error)