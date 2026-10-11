from .fcfs import fcfs_scheduling
from .priority_scheduling import priority_scheduling
from .round_robin import round_robin_scheduling

def schedule_requests(requests,algorithm,time_quantum=2):
    
    if algorithm == "FCFS":
        return fcfs_scheduling(requests)
    
    elif algorithm == "Priority":
        return priority_scheduling(requests)
    
    elif algorithm == "Round Robin":
        return round_robin_scheduling(requests,time_quantum)
    
    else:
        return []
    
        