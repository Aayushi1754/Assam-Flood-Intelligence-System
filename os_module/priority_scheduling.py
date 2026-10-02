def priority_scheduling(requests):
    remaining = requests.copy()
    scheduled = []
    current_time = 0

    while remaining:

        # Finding arrived requests
        available = []

        for request in remaining:
            if request.arrival_time <= current_time:
                available.append(request)

        # No request has arrived
        if not available:
            current_time += 1
            continue

        # Find the request with highest urgency
        selected = available[0]

        for request in available:
            if request.urgency_score > selected.urgency_score:
                selected = request

        waiting_time = current_time - selected.arrival_time
        priority_score = (selected.urgency_score * 10) + waiting_time

        scheduled.append({
            "request_id": selected.request_id,
            "location": selected.location,
            "need": selected.need,
            "urgency_score": selected.urgency_score,
            "priority_score": priority_score,
            "waiting_time": waiting_time
        })

        current_time += 1

        # Remove completed request
        remaining.remove(selected)

    return scheduled
