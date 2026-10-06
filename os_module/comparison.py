from .fcfs import fcfs_scheduling
from .priority_scheduling import priority_scheduling
from .round_robin import round_robin_scheduling

from .metrics import (
    calculate_average_waiting_time,
    calculate_average_response_time
)

def compare_algorithms(requests, time_quantum=2):

    # Run FCFS
    fcfs_result = fcfs_scheduling(requests)

    # Run Priority Scheduling
    priority_result = priority_scheduling(requests)

    # Run Round Robin
    round_robin_result = round_robin_scheduling(
        requests,
        time_quantum
    )

    # Calculate FCFS metrics
    fcfs_waiting_time = calculate_average_waiting_time(
        fcfs_result
    )

    fcfs_response_time = calculate_average_response_time(
        fcfs_result
    )

    # Calculate Priority metrics
    priority_waiting_time = calculate_average_waiting_time(
        priority_result
    )

    priority_response_time = calculate_average_response_time(
        priority_result
    )

    # Calculate Round Robin metrics
    round_robin_waiting_time = calculate_average_waiting_time(
        round_robin_result
    )

    round_robin_response_time = calculate_average_response_time(
        round_robin_result
    )

    # Store comparison results
    results = {
        "FCFS": {
            "average_waiting_time": fcfs_waiting_time,
            "average_response_time": fcfs_response_time
        },

        "Priority": {
            "average_waiting_time": priority_waiting_time,
            "average_response_time": priority_response_time
        },

        "Round Robin": {
            "average_waiting_time": round_robin_waiting_time,
            "average_response_time": round_robin_response_time
        }
    }

    # Find the algorithm with the lowest
    # average waiting time
    best_algorithm = min(
        results,
        key=lambda algorithm:
            results[algorithm]["average_waiting_time"]
    )

    return {
        "results": results,
        "best_algorithm": best_algorithm
    }