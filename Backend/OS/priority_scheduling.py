def priority_scheduling(requests):
    remaining = requests.copy()
    scheduled = []

    if not remaining:
        return scheduled

    current_time = min(
        request.arrival_time for request in remaining
    )

    while remaining:

        # Find requests that have already arrived
        available = []

        for request in remaining:
            if request.arrival_time <= current_time:
                available.append(request)

        # Move time forward if no request has arrived yet
        if not available:
            current_time = min(
                request.arrival_time for request in remaining
            )
            continue

        # Select the request with the highest effective priority
        selected = available[0]
        selected_waiting_time = (
            current_time - selected.arrival_time
        )
        highest_priority = (
            selected.urgency_score * 10
            + selected_waiting_time
        )

        for request in available[1:]:
            waiting_time = current_time - request.arrival_time

            # Aging: priority increases as waiting time increases
            priority_score = (
                request.urgency_score * 10
                + waiting_time
            )

            if priority_score > highest_priority:
                selected = request
                selected_waiting_time = waiting_time
                highest_priority = priority_score

        # Add the selected request to the schedule
        scheduled.append({
            "request_id": selected.request_id,
            "location": selected.location,
            "need": selected.need,
            "urgency_score": selected.urgency_score,
            "priority_score": highest_priority,
            "waiting_time": selected_waiting_time
        })

        # Process one request in this simplified simulation
        current_time += 1

        # Remove the completed request
        remaining.remove(selected)

    return scheduled
