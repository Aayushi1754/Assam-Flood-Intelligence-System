
from psycopg.rows import dict_row
from db import get_connection


def get_all_requests():
    """Retrieve all flood-relief requests from PostgreSQL."""
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT request_id, location, need,
                       urgency_score, people_affected,
                       arrival_time, status
                FROM relief_requests
                ORDER BY arrival_time;
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
    """Insert a new flood-relief request into PostgreSQL."""
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
    """Retrieve available relief resources from PostgreSQL."""
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT resource_id, resource_name,
                       available_quantity, unit,
                       warehouse_location
                FROM resource_inventory
                ORDER BY resource_name;
            """)
            return cur.fetchall()


def allocate_resource(request_id, resource_name, quantity):
    """Allocate resources and reduce stock safely."""
    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero.")

    with get_connection() as conn:
        with conn.cursor() as cur:
            # Lock the inventory row to prevent overspending stock.
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

            # Confirm the relief request exists.
            cur.execute("""
                SELECT 1 FROM relief_requests
                WHERE request_id = %s;
            """, (request_id,))

            if cur.fetchone() is None:
                raise ValueError("Relief request not found.")

            # Record the allocation.
            cur.execute("""
                INSERT INTO resource_allocations
                    (request_id, resource_id, quantity)
                VALUES (%s, %s, %s);
            """, (request_id, resource_id, quantity))

            # Reduce the available stock.
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
   

   
if __name__ == "__main__":
    try:
        result = allocate_resource("REQ001", "water", 10)
        print("Allocation successful!")
        print(result)

        print("\nUpdated inventory:")
        for resource in get_resource_inventory():
            print(resource)

        print("\nUpdated request:")
        for request in get_all_requests():
            if request["request_id"] == "REQ001":
                print(request)

    except Exception as e:
        print("Allocation failed:")
        print(e)