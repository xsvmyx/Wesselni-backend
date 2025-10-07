from pydantic import BaseModel

class UserCreate(BaseModel):
    nom: str
    prenom: str
    password: str
    wilaya: str
    commune: str
    phone : str
    doc: str | None = None  

    model_config = {
        "from_attributes": True
    }


class UserOut(BaseModel):
    id: int
    nom: str
    prenom: str
    phone : str
    wilaya: str
    commune: str

    model_config = {
        "from_attributes": True
    }


class UserLogin(BaseModel):
    phone : str
    password: str

    model_config = {
        "from_attributes": True
    }

