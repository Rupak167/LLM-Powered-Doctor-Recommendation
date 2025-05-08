from pydantic import BaseModel

class UserQuery(BaseModel):
    symptom: str
    location: str
    specialization: str = None