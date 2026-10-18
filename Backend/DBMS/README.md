# FloodSense — DBMS Module

## 1. Overview

The Database Management System (DBMS) module is responsible for storing and managing flood-relief requests, resource inventory, and resource allocation records in the FloodSense Assam Flood Intelligence System.

The module uses PostgreSQL as its relational database and Psycopg 3 for connectivity between Python and PostgreSQL. It supports relief-request management, storage of Natural Language Processing (NLP) results, resource availability checks, and transactional resource allocation.

The main objective of this module is to maintain structured, consistent, and accessible data to support flood-relief operations.

## 2. Technologies Used

- **Python:** Implements database connectivity and database operations.
- **PostgreSQL:** Stores application data in a relational database.
- **Psycopg 3:** Connects the Python application to PostgreSQL.
- **SQL:** Defines database structures and performs data operations.
- **unittest:** Supports automated testing.
- **unittest.mock:** Allows database-related functions to be tested using mocks.

## 3. Project Files

The DBMS module contains the following files:

| File | Description |
|---|---|
| `db.py` | Establishes the PostgreSQL database connection. |
| `db_operations.py` | Implements database operations for relief requests, resource inventory, resource allocation, status updates, and allocation history. |
| `schema.sql` | Defines database tables, constraints, indexes, and the allocation-summary view. |
| `seed.sql` | Provides sample relief requests and resource inventory records. |
| `test_db_operations.py` | Contains automated tests for DBMS operations and resource-category validation. |
| `README.md` | Documents the database module, setup instructions, features, and testing procedure. |

## 4. Database Design

The database organizes flood-relief information into three main tables: `relief_requests`, `resource_inventory`, and `resource_allocations`.

### 4.1 Relief Requests Table

The `relief_requests` table stores information about requests for flood-relief assistance.

Important fields include:

- `request_id`: Identifies each relief request.
- `location`: Specifies the location requiring assistance.
- `need`: Describes the requested resource or assistance.
- `urgency_score`: Stores the numeric urgency score, intended to range from 0 to 10.
- `people_affected`: Records the number of people affected.
- `arrival_time`: Stores the request's arrival-time information.
- `status`: Represents the request's processing status, such as pending, allocated, or completed.
- `source_text`: Stores the original text of the relief request.
- `extracted_keywords`: Stores keywords extracted by the NLP component.
- `urgency_level`: Stores the urgency classification produced by the NLP component.
- `created_at`: Records when the request was created.

This table helps the application organize requests and track their processing status.

### 4.2 Resource Inventory Table

The `resource_inventory` table stores information about relief resources and their availability.

Important fields include:

- `resource_id`: Identifies each resource record.
- `resource_name`: Specifies the name of the resource.
- `resource_category`: Identifies the category of the resource.
- `available_quantity`: Stores the quantity currently available.
- `unit`: Specifies the measurement unit, such as litres, packets, or kits.
- `warehouse_location`: Records the location where the resource is stored.

The supported resource categories are:

- Medical
- Food
- Water
- Rescue
- Shelter

Inventory constraints help prevent invalid negative quantities when enforced by the database schema.

### 4.3 Resource Allocations Table

The `resource_allocations` table maintains a record of resources allocated to relief requests.

Important fields include:

- `allocation_id`: Identifies each allocation record.
- `request_id`: References the related relief request.
- `resource_id`: References the allocated resource.
- `quantity`: Records the quantity allocated.
- `allocated_at`: Records the allocation timestamp.

Foreign-key relationships connect allocation records with their corresponding relief requests and resources. These relationships help maintain referential integrity.

## 5. Database Relationships

The database uses relational links between requests, resources, and allocations.

- A relief request can be associated with allocation records.
- A resource can appear in allocation records.
- Each allocation record references a relief request and a resource through foreign keys.

These relationships allow the application to track which resources were allocated to which requests and retrieve allocation history.

## 6. DBMS Concepts Used

### 6.1 Relational Database Model

PostgreSQL stores the application's structured information in tables containing rows and columns. Related tables are connected through keys.

### 6.2 Primary Keys

Primary keys uniquely identify records in their respective tables. For example, request, resource, and allocation identifiers distinguish individual records.

### 6.3 Foreign Keys and Referential Integrity

Foreign keys connect related records across tables. In the allocation table, the request and resource references help ensure that an allocation is associated with corresponding database records.

### 6.4 Constraints and Data Validation

Database constraints can restrict invalid values and improve data consistency. Relevant examples in this project include urgency-score limits, non-negative quantities, request-status values, and supported resource categories, as defined by the schema.

### 6.5 Indexing

Indexes can improve the performance of frequently used searches. The schema defines indexes intended to support common request and inventory queries.

### 6.6 Database Views

The `relief_allocation_summary` view provides a combined representation of relief-request and allocation information. It makes related information easier to retrieve without repeatedly writing the same joins.

### 6.7 SQL Queries

SQL is used to insert, retrieve, and update database records. Parameterized queries help protect against SQL injection by separating query structure from supplied values.

### 6.8 Transactions

Resource allocation involves related database changes. A transaction helps ensure that these changes are handled together, reducing the risk of partially completed allocations.

### 6.9 Concurrency Control

Inventory row locking, when used during allocation, helps prevent concurrent operations from allocating more resources than are available.

### 6.10 Normalization

Normalization is a database-design technique used to reduce unnecessary data duplication and prevent insertion, update, and deletion anomalies.

The FloodSense database separates relief requests, resource inventory, and allocation records into related tables. This separation supports organized data management and reduces the need to repeat request and resource details in every allocation record.

The exact normal form, such as First Normal Form (1NF), Second Normal Form (2NF), or Third Normal Form (3NF), should be established by examining the complete table definitions, attributes, keys, and functional dependencies. It should not be assumed solely from the number of tables.

## 7. Main Database Operations

The `db_operations.py` module provides functions for managing database information.

The main operations include:

- Retrieving existing relief requests.
- Inserting relief requests with their source text and NLP results.
- Retrieving resource inventory.
- Filtering available resources by category.
- Retrieving pending relief requests.
- Allocating resources to relief requests.
- Updating request status.
- Retrieving resource allocation history.

During resource allocation, the application records the allocation, adjusts the available inventory quantity, and updates the request status as part of a database transaction, according to the implemented allocation logic.

The DBMS module stores NLP results supplied by the application. The NLP component is responsible for processing text and producing extracted keywords and urgency classifications.

## 8. Setup Instructions

### Prerequisites

Install the following software:

- Python
- PostgreSQL
- pip, the Python package installer

Ensure that the PostgreSQL server is running before attempting to connect.

### Step 1: Create the Database

Create a PostgreSQL database named `floodsense_db` using pgAdmin or the PostgreSQL command line.

### Step 2: Configure the Connection

Configure the connection settings expected by `db.py`.

Use environment variables or another appropriate configuration method for database credentials when supported by the implementation. Do not commit database passwords or other sensitive information to version control.

### Step 3: Create the Database Schema

Execute `schema.sql` against the `floodsense_db` database.

If the database already exists, ensure that its schema includes the latest table definitions, columns, constraints, indexes, and views. A statement such as `CREATE TABLE IF NOT EXISTS` does not automatically add missing columns to an existing table.

### Step 4: Insert Sample Data

Execute `seed.sql` against `floodsense_db` when sample data is required.

Review the existing database state before rerunning the seed script because duplicate identifiers or unique values may cause conflicts.

### Step 5: Install the Python Database Dependency

Run the following command in the terminal:

```powershell
python -m pip install "psycopg[binary]"
```

### Step 6: Run the Tests

Navigate to the DBMS directory:

```powershell
cd Backend/DBMS
```

Run the tests using Python's unittest framework:

```powershell
python -m unittest test_db_operations.py -v
```

Alternatively, if pytest is installed, run:

```powershell
python -m pytest -v test_db_operations.py
```

The test suite may use mocks to isolate database operations. Therefore, passing unit tests does not necessarily confirm that a live PostgreSQL connection works correctly. Check the test implementation and database configuration when verifying live integration.

## 9. Security and Reliability

The DBMS module follows important database-security and reliability practices:

- Use parameterized SQL queries to help prevent SQL injection.
- Avoid committing passwords, credentials, or other sensitive configuration to GitHub.
- Validate resource categories and allocation quantities.
- Use transactions for related resource-allocation updates.
- Use appropriate concurrency controls when modifying shared inventory.
- Handle database errors and provide suitable application-level error messages.
- Keep the database schema consistent with the application's expected structure.
- Test database operations after modifying queries or schema definitions.

## 10. Application Integration

Other project components can use functions from `db_operations.py` to create and retrieve relief requests, access inventory, filter available resources, allocate resources, update request statuses, and retrieve allocation history.

The application or NLP component processes incoming text and supplies the extracted keywords and urgency classification when creating a relief request.

The integration layer is responsible for handling database errors and communicating appropriate results or error messages to the user.

## 11. Conclusion

The FloodSense DBMS module provides structured storage and management of flood-relief requests, resource inventory, and allocation history. PostgreSQL provides relational data storage, while Python and Psycopg 3 support database connectivity and application operations.

Primary keys, foreign keys, constraints, indexes, views, parameterized queries, transactions, and automated tests support data integrity, security, and maintainability. Together, these features help the FloodSense system organize relief information and support resource-allocation workflows during flood emergencies.

#added normalisation part
