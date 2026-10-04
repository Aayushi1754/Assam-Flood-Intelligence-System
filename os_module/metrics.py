def calculate_average_waiting_time(scheduled_requests):
    if not scheduled_requests:
        return 0
    
    total_waiting_time= 0
    
    for request in scheduled_requests:
        total_waiting_time+= request["waiting_time"]
        
    average_waiting_time= total_waiting_time / len(scheduled_requests)
    return average_waiting_time          #Total waiting time / Number of requests will do this basically 


def calculate_average_response_time(scheduled_requests):
    if not scheduled_requests:
        return 0
    
    total_response_time= 0
    
    for request in scheduled_requests:
        total_response_time+= request["waiting_time"]
        
    average_response_time= total_response_time / len(scheduled_requests)
    return average_response_time       
