from app.os_module.models import ReliefRequest
from app.os_module.fcfs import fcfs_scheduling
from app.os_module.priority_scheduling import priority_scheduling
from app.os_module.round_robin import round_robin_scheduling
from app.os_module.metrics import (calculate_average_waiting_time,calculate_average_response_time)
from app.os_module.scheduler import schedule_requests

def create_requests():
    request1 = ReliefRequest(
        request_id= "REQ001",
        location= "Dibrugarh",
        need= "water",
        urgency_score= 7,
        people_affected= 100,
        arrival_time= 0
    )
    
    request2= ReliefRequest(
        request_id= "REQ002",
        location= "Guwahati",
        need= "medical",
        urgency_score= 9,
        people_affected= 80,
        arrival_time= 1
    )
    
    request3= ReliefRequest(
        request_id= "REQ003",
        location= "Jorhat",
        need= "food",
        urgency_score= 5,
        people_affected= 120,
        arrival_time= 2
    )
    
    return [request1,request2,request3]

def test_fcfs_scheduling():
    requests= create_requests()
    
    result= fcfs_scheduling(requests)
    
    assert len(result) == 3
    assert result[0]["request_id"] == "REQ001"
    assert result[1]["request_id"] == "REQ002"
    assert result[2]["request_id"] == "REQ003"
    
def test_priority_scheduling():
    requests= create_requests()
    
    result= priority_scheduling(requests)
    
    assert len(result) == 3
    assert result[0]["request_id"] == "REQ001"
    assert result[1]["request_id"] == "REQ002"
    
def test_round_robin_scheduling():
     requests= create_requests()
     
     result= round_robin_scheduling(requests,2)
     
     assert len(result) == 3
     assert result[0]["request_id"] == "REQ001"
     assert result[1]["request_id"] == "REQ002"
     assert result[2]["request_id"] == "REQ003"
     
def test_average_waiting_time():
    scheduled_requests= [
        {"request_id": "REQ001","waiting_time":0},
        {"request_id": "REQ002","waiting_time":1},
        {"request_id": "REQ003","waiting_time":2}
    ]
    
    result= calculate_average_waiting_time(scheduled_requests)
    
    assert result == 1
    
def test_average_response_time():
    scheduled_requests=[
        {"request_id": "REQ001","waiting_time":0},
        {"request_id": "REQ002","waiting_time":1},
        {"request_id": "REQ003","waiting_time":2},
    ]
    
    result= calculate_average_response_time(scheduled_requests)
    
    assert result == 1
    
def test_scheduler_fcfs():
    requests= create_requests()
    
    result= schedule_requests(requests,"FCFS")
    
    assert len(result) == 3
    
def test_scheduler_priority():
    requests= create_requests()
    
    result= schedule_requests(requests,"Priority")
    
    assert len(result) == 3
    
def test_scheduler_round_robin():
    requests= create_requests()
    
    result= schedule_requests(requests,"Round Robin",2)
    
    assert len(result) == 3
    
    
     
     
     
     
     
    
    
    