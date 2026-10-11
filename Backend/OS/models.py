from pydantic import BaseModel

class ReliefRequest(BaseModel):
    request_id: str
    location: str
    need: str
    urgency_score: float
    people_affected: int
    arrival_time: int
    
class ScheduledRequest(BaseModel):
    request_id: str
    location: str
    need: str
    urgency_score: float
    priority_score: float
    priority_rank: int
    algorithm: str
    
    