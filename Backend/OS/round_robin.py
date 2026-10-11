def round_robin_scheduling(requests,time_quantum):
    remaining= requests.copy()
    scheduled= []
    current_time= 0
    
    while remaining:
        request= remaining.pop(0)
        
        #move if req not arrived
        if current_time < request.arrival_time:
            current_time= request.arrival_time
            
        waiting_time= current_time - request.arrival_time
        
        scheduled.append({
            "request_id": request.request_id,
            "location": request.location,
            "need": request.need,
            "urgency_score": request.urgency_score,
            "waiting_time": waiting_time
        })
        
        #process req for one tym quantum
        current_time+= time_quantum
        
    return scheduled
