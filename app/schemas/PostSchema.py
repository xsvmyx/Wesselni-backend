from pydantic import BaseModel
from datetime import datetime
from datetime import time

class PostBase(BaseModel):
    departure: str
    destination: str
    departure_time: time
    details: str
    



class PostCreate(PostBase):
    pass

class PostResponse(PostBase):
    id: int
    user_id: int
    created_at: datetime

    


class PostUserResponse(BaseModel):
    id_user: int
    departure: str
    destination: str
    departure_time: time
    phone: str
    details: str
    doc: str | None  