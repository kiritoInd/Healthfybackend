from pydantic import BaseModel

class PromptRequest(BaseModel):
    prompt: str

class User(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    
class HealthData(BaseModel):
    condition: str
    level: str

class MedicalReport(BaseModel):
    username: str
    health_data: list[HealthData]