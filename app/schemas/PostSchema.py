from pydantic import BaseModel
from datetime import datetime

class PostBase(BaseModel):
    title: str
    content: str

class PostCreate(PostBase):
    pass



class PostResponse(PostBase):
    id: int
    user_id: int
    created_at: datetime

    