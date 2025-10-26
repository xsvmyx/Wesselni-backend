from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str
    id: int
    model_config = {
        "from_attributes": True
    }


class TokenInput(BaseModel):
    token: str