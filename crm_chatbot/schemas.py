from pydantic import BaseModel

class LoginRequest(BaseModel):
    email: str
    password: str
    session_id: str

class ChatRequest(BaseModel):
    message: str
    session_id: str

class ChatResponse(BaseModel):
    reply: str
