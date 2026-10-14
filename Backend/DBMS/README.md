# FloodSense — DBMS Module
#updated

## 1. Overview

The Database Management System (DBMS) module stores and manages flood-relief requests, resource inventory, and resource allocation records for the FloodSense Assam Flood Intelligence System.

It uses PostgreSQL for persistent data storage and Psycopg 3 for Python database connectivity. The module supports relief-request management, NLP result storage, resource availability checks, and transactional resource allocation.

## 2. Technologies Used

- Python
- PostgreSQL
- Psycopg 3
- SQL
- `unittest` and `unittest.mock` for automated testing

## 3. Project Files

- `db.py` — establishes the PostgreSQL database connection.
- `db_operations.py` — implements relief-request operations, resource inventory retrieval, category-based filtering, resource allocation, status updates, and allocation history.
- `schema.sql` — defines database tables, constraints, indexes, and the allocation-summary view.
- `seed.sql` — provides sample relief requests and resource inventory records.
- `test_db_operations.py` — contains automated tests for DBMS operations, including resource-category validation.

## 4. Database Tables

### 4.1 `relief_requests`

Stores flood-relief requests and their processing status.

Important fields:

- `request_id` — unique identifier for each request.
- `location` — location requiring assistance.
- `need` — requested relief resource or assistance.
- `urgency_score` — numeric urgency score from 0 to 10.
- `people_affected` — number of people affected.
- `arrival_time` — request arrival time or associated time value, as defined by the application.
- `status` — request status: `pending`, `allocated`, or `completed`.
- `source_text` — original request text.
- `extracted_keywords` — keywords extracted from the request by the NLP component.
- `urgency_level` — urgency classification produced by the NLP component.
- `created_at` — timestamp when the request was created.

### 4.2 `resource_inventory`

Stores available relief resources and their warehouse details.

Important fields:

- `resource_id` — unique resource identifier.
- `resource_name` — resource name.
- `resource_category` — category of resource.
- `available_quantity` — quantity currently available.
- `unit` — measurement unit, such as litres, packets, or kits.
- `warehouse_location` — location of the warehouse storing the resource.

Supported resource categories:

- Medical
- Food
- Water
- Rescue
- Shelter

The database enforces non-negative inventory quantities.

### 4.3 `resource_allocations`

Maintains the allocation history.

Important fields:

- `allocation_id` — unique allocation identifier.
- `request_id` — reference to the relief request.
- `resource_id` — reference to the allocated resource.
- `quantity` — quantity allocated.
- `allocated_at` — allocation timestamp.

Foreign keys link allocation records to their corresponding requests and resources.

## 5. Database Features

- Primary keys and foreign-key relationships.
- Constraints for urgency scores, quantities, request statuses, and resource categories.
- Indexes to support common request and inventory searches.
- The `relief_allocation_summary` view for viewing request and allocation information together.
- Parameterized SQL queries to help prevent SQL injection.
- Transaction-based resource allocation.
- Inventory row locking to reduce the risk of concurrent allocations exceeding available stock.
- Resource filtering by category and available quantity.
- Storage of NLP-extracted keywords and urgency classifications.
- Automated tests for DBMS operations and resource-category validation.

## 6. Main Database Operations

The `db_operations.py` module provides functions for:

- Retrieving existing relief requests.
- Inserting a relief request with its source text and NLP results.
- Retrieving resource inventory.
- Retrieving available resources by category.
- Retrieving pending relief requests.
- Allocating resources to relief requests.
- Updating request status.
- Retrieving resource allocation history.

Resource allocation records the allocation, deducts the allocated quantity from inventory, and updates the request status within a database transaction.

The database module stores NLP results supplied by the application. NLP processing itself is handled by the relevant application or NLP component.

## 7. Setup Instructions

### Prerequisites

Install Python and PostgreSQL. Ensure the PostgreSQL database server is running.

### Step 1: Create the database

Create a database named `floodsense_db` using pgAdmin or the PostgreSQL command line.

### Step 2: Configure the database connection

Configure the connection settings expected by `db.py`. Use environment variables for credentials where supported by the implementation.

Do not commit database passwords or other sensitive credentials to GitHub.

### Step 3: Create the schema

Execute `schema.sql` against `floodsense_db`.

If the database already exists, ensure its schema has been migrated to include the latest columns and constraints. `CREATE TABLE IF NOT EXISTS` does not automatically add missing columns to existing tables.

### Step 4: Insert sample data

Execute `seed.sql` against `floodsense_db`.

Run the seed script only when appropriate for the current database state, since sample data may conflict with existing primary keys or unique resource names.

### Step 5: Install the database dependency

```powershell
python -m pip install "psycopg[binary]"
```

### Step 6: Run the DBMS tests

From the DBMS directory, run:

```powershell
python -m unittest test_db_operations.py -v
```

Alternatively, run the tests with pytest:

```powershell
python -m pytest -v test_db_operations.py
```

The tests use mocks where appropriate, so a passing unit-test suite does not necessarily verify a live PostgreSQL connection. Follow the test configuration in `test_db_operations.py`.

## 8. Security and Reliability

- Never commit database passwords or other credentials to version control.
- Use parameterized SQL queries.
- Validate resource categories and allocation quantities before performing operations.
- Use database transactions for related allocation updates.
- Handle database errors in the application integration layer and provide suitable error messages.
- Verify database migrations before deploying schema changes.

## 9. Integration

Other project modules can import functions from `db_operations.py` to create or retrieve relief requests, access inventory, filter available resources, allocate resources, update request status, and retrieve allocation history.

The application or NLP integration layer is responsible for processing incoming text and supplying the extracted keywords and urgency classification when inserting a relief request.

The application integration layer should handle database errors and return appropriate messages to users.