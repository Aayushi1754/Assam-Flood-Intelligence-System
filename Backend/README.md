#FloodSense - Intelligent Flood Relief Management System
##Backend- OS Scheduling Module
This backend has OS scheduling modules of our project.

The OS module receives structured flood relief requests and schedules them using different scheduling algorithms.There is a metrics module in which we calculate average waiting time and average response time


#Features 
1 FCFS(First Come First Serve)
2 Priority Scheduling 
3 Round Robin Scheduling
4 Average waiting time calculation
5 Average Response time calculation
6 FastAPI 
7 Pydantic data validation
8 Pytest test cases

backend/
│
|--- app/
│   |--- __init__.py
│   |-- main.py
│   │
│   |---os_module/
│       |---__init__.py
│       |--- models.py
│       |--- fcfs.py
│       |--- priority.py
│       |---priority_scheduling.py
│       |--- round_robin.py
│       |--- metrics.py
│       |--- scheduler.py
|---- tests/
│   |-- test_os_scheduler.py
│
|--- requirements.txt
|---README.md


Relief Request Model

The OS module uses Pydantic model to define structure of relief request.

Each request contains:
1 request-id- Unique ID of request
2 location- Flood-affected location
3 need- Required relief item or service 
4 urgency_score- Urgency value provided to the scheduler
5 people_affected- no of people affected
6 arrival_time- time at which request arrives

Ex:
{
    request_id: "REQ001",
    "location": "Dibrugarh",
    "need": "water",
    "urgency_score": 7
    "people_affected": 100
    "arrival_time": 0
}


Scheduling Algorithms:

FCFS 
First Come First Serve processes relief requests according to their arrival time.

Priority Scheduling
It selects an available relief request based on its urgency score.

Round Robind
It processes requests using a fixed time quantum.
The current implementation is a simplified representation where each request receives one time quantum.


Scheduling Metrics

The module contains:

Average Waiting Time
Measures average amount of time requests wait before being processed

Average Response Time
The current implementation uses waiting time as the response-time value.


FastAPI 
FastAPI is used to expose the scheduling module through REST API endpoints.

Available Endpoints

GET/ 
Checks whether the FloodSense API is running.

GET /health
Checks the health of the backend.
Ex response:
{
    "status": "healthy"
}

POST / schedule
Schedules relief requests using the selected algorithm.
Ex:
POST /schedule?algorithm=Priority

Request body:
[
    {
    request_id: "REQ001",
    "location": "Dibrugarh",
    "need": "water",
    "urgency_score": 7,
    "people_affected": 100,
    "arrival_time": 0
    },
    {
    request_id: "REQ002",
    "location": "Guwahati",
    "need": "medical",
    "urgency_score": 9,
    "people_affected": 80,
    "arrival_time": 1
    },
    {
    request_id: "REQ003",
    "location": "Jorhat",
    "need": "food",
    "urgency_score": 5,
    "people_affected": 120,
    "arrival_time": 0
    }
]

Supported algorithms:
FCFS 
Priority 
Round Robin



Installation 
Navigate to backend directory:
cd backend


Install the required packages:
python -m pip install -r requirements.txt


Running the Backend
Start the FastAPI server:
python -m uvicorn app.main:app --reload
The backend will run at:
http://127.0.0.1:8000
FastAPI documentation:
http://127.0.0.1:8000/docs
OpenaAPI specification:
http://127.0.0.1:8000/openapi.json


Running Tests
From the backend directory:
python -m pytest

The current test suite contains 8 tests covering:
1 FCFS scheduling 
2 Priority scheduling 
3 Round Robin Scheduling
4 Average waiting time calculation
5 Average Response time calculation
6 Scheduler interface for all three algorithms 




Integration
The OS scheduling module is designed to be integrated with the other FloodSense components.The planned data flow is:

    NLP Module->Extracted Flood Relief Request-> DBMS/PostgreSQL->Structured Relief Request->FastAPI-> OS Scheduling Module-> FCFS/Priority/Round Robin-> Scheduling Metrics-> Dashboard

The NLP and DBMS  modules will provide the required the required request information to the backend during final system integration

Current Status
The OS scheduling module has been implemented and tested independently.

Current test result:
8 passed

The module can currently run without NLP and DBMS components by using sample relief requests through FASTAPI endpoint.

Note
The current implementation is intended as the OS scheduling component of the larger FloodSense system. Final integration with NLP, PostgreSQL/DBMS and the dashboard will be performed as part of the complete system integration.






