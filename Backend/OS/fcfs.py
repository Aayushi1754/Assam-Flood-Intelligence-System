def fcfs_scheduling(requests):
    remaining = requests.copy()
    scheduled = []
    current_time = 0

    while remaining:

        # Find the request that arrived first
        first_request = remaining[0]

        for request in remaining:
            if request.arrival_time < first_request.arrival_time:
                first_request = request

        # Move time forward if necessary
        if current_time < first_request.arrival_time:
            current_time = first_request.arrival_time

        # Calculate waiting time
        waiting_time = current_time - first_request.arrival_time

        scheduled.append({
            "request_id": first_request.request_id,
            "location": first_request.location,
            "need": first_request.need,
            "urgency_score": first_request.urgency_score,
            "waiting_time": waiting_time
        })

        # Process the request
        current_time += 1

        # Remove completed request
        remaining.remove(first_request)

    return scheduled
