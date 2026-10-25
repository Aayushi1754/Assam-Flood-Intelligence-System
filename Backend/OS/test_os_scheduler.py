from Backend.OS.models import ReliefRequest
from Backend.OS.fcfs import fcfs_scheduling
from Backend.OS.priority_scheduling import priority_scheduling
from Backend.OS.round_robin import round_robin_scheduling
from Backend.OS.metrics import (
    calculate_average_waiting_time,
    calculate_average_response_time
)
from Backend.OS.scheduler import schedule_requests


def create_requests():
    request1 = ReliefRequest(
        request_id="REQ001",
        location="Dibrugarh",
        need="water",
        urgency_score=7,
        people_affected=100,
        arrival_time=0
    )

    request2 = ReliefRequest(
        request_id="REQ002",
        location="Guwahati",
        need="medical",
        urgency_score=9,
        people_affected=80,
        arrival_time=1
    )

    request3 = ReliefRequest(
        request_id="REQ003",
        location="Jorhat",
        need="food",
        urgency_score=5,
        people_affected=120,
        arrival_time=2
    )

    return [request1, request2, request3]


def test_fcfs_scheduling():
    requests = create_requests()

    result = fcfs_scheduling(requests)

    assert len(result) == 3
    assert result[0]["request_id"] == "REQ001"
    assert result[1]["request_id"] == "REQ002"
    assert result[2]["request_id"] == "REQ003"


def test_priority_scheduling():
    requests = create_requests()

    result = priority_scheduling(requests)

    assert len(result) == 3
    assert result[0]["request_id"] == "REQ001"
    assert result[1]["request_id"] == "REQ002"


def test_round_robin_scheduling():
    requests = create_requests()

    result = round_robin_scheduling(requests, 2)

    assert len(result) == 3
    assert result[0]["request_id"] == "REQ001"
    assert result[1]["request_id"] == "REQ002"
    assert result[2]["request_id"] == "REQ003"


def test_average_waiting_time():
    scheduled_requests = [
        {"request_id": "REQ001", "waiting_time": 0},
        {"request_id": "REQ002", "waiting_time": 1},
        {"request_id": "REQ003", "waiting_time": 2}
    ]

    result = calculate_average_waiting_time(scheduled_requests)

    assert result == 1


def test_average_response_time():
    scheduled_requests = [
        {"request_id": "REQ001", "waiting_time": 0},
        {"request_id": "REQ002", "waiting_time": 1},
        {"request_id": "REQ003", "waiting_time": 2}
    ]

    result = calculate_average_response_time(scheduled_requests)

    assert result == 1


def test_scheduler_fcfs():
    requests = create_requests()

    result = schedule_requests(requests, "FCFS")

    assert len(result) == 3


def test_scheduler_priority():
    requests = create_requests()

    result = schedule_requests(requests, "Priority")

    assert len(result) == 3


def test_scheduler_round_robin():
    requests = create_requests()

    result = schedule_requests(requests, "Round Robin", 2)

    assert len(result) == 3


def test_priority_aging_prevents_starvation():
    requests = []

    # A lower-urgency request arrives first
    low_request = ReliefRequest(
        request_id="LOW001",
        location="Dibrugarh",
        need="food",
        urgency_score=5,
        people_affected=100,
        arrival_time=0
    )

    requests.append(low_request)

    # Higher-urgency requests keep arriving
    for i in range(11):
        request = ReliefRequest(
            request_id=f"HIGH{i}",
            location="Guwahati",
            need="medical",
            urgency_score=6,
            people_affected=50,
            arrival_time=i
        )

        requests.append(request)

    result = priority_scheduling(requests)

    # The waiting request should eventually be selected
    assert result[10]["request_id"] == "LOW001"
    assert result[10]["waiting_time"] == 10


