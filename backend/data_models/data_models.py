from pydantic import BaseModel

class MessageRequest(BaseModel):
    message: str
    language: str

class Corrections(BaseModel):
    original: str
    corrected: str
    explanation: str