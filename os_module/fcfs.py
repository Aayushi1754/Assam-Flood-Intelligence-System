def priority_scheduling(requests):
    remaining = requests.copy()
    scheduled = []
    current_time= 0
    
    while remaining:
        #finding arrived requests
        
        available= []
        
        for request in remaining:
            if request.arrival_time <= current_time:
             available.append(request)
            
        #no request came
        if not available:
            current_time+= 1
            continue
        
        #find the request with highest priority
        selected= available[0]
        
        for request in available:
            if request.urgency_score > selected.urgency_score:
                selected = request
                
        waiting_time = current_time - selected.arrival_time
        priority_score = (selected.urgency_score*10 + waiting_time)
        
        scheduled.append({
            "request_id": selected.request_id,
            "location": selected.location,
            "need": selected.need,
            "urgency_score": selected.urgency_score,
            "priority_score": priority_score,
            "waiting_time": waiting_time
        })
        
        current_time+= 1
        
        #removing completed request
        remaining.remove(selected)
        
    return scheduled