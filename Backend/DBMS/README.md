# FloodSense — DBMS Module

## 1. Overview

The Database Management System (DBMS) module stores and manages flood-relief requests, available relief resources, and resource allocation records for the FloodSense Assam Flood Intelligence System.

It uses PostgreSQL for data storage and Psycopg 3 for Python database connectivity.

## 2. Technologies Used

* Python
* PostgreSQL
* Psycopg 3
* SQL

## 3. Project Files

* `db.py` — establishes the PostgreSQL database connection.
* `db_operations.py` — implements relief-request retrieval and insertion, resource inventory retrieval, resource allocation, pending-request retrieval, status updates, and allocation history.
* `schema.sql` — creates the database tables, constraints, indexes, and allocation-summary view.
* `seed.sql` — inserts sample relief requests and inventory records.
* `test_db_operations.py` — contains automated unit tests for DBMS operations.

## 4. Database Tables

### relief_requests

Stores relief requests, including request ID, location, required resource, urgency score, people affected, arrival time, status, source text, and creation timestamp.

### resource_inventory

Stores resource names, available quantities, measurement units, and warehouse locations.

### resource_allocations

Records which resource was allocated to which request, the allocated quantity, and the allocation timestamp.

## 5. Database Features

* Primary keys and foreign keys.
* Constraints to validate urgency scores, quantities, and request statuses.
* Indexes to support common request searches.
* A view named `relief_allocation_summary`.
* Parameterized SQL queries.
* Transaction-based resource allocation with inventory row locking.
* Automated unit tests.

## 6. Setup Instructions

1. Install PostgreSQL and create a database named `floodsense_db`.

2. Configure the connection settings required by `db.py`.

3. Execute `schema.sql` against `floodsense_db`.

4. Execute `seed.sql` to insert sample data.

5. Install the Python dependency:

   `python -m pip install "psycopg[binary]"`

6. Run the tests from this directory:

   `python -m unittest test_db_operations.py -v`

## 7. Security

Do not commit database passwords or other credentials to GitHub. Use environment variables for sensitive configuration.

## 8. Integration

Other project modules can import the functions from `db_operations.py` to retrieve relief requests, add requests, access inventory, allocate resources, update request status, and retrieve allocation history.

The application integration layer should handle database errors and return appropriate messages to users.
