from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any

class ChatTurn(BaseModel):
    conversation_id: Optional[str] = None
    channel: str = "web"
    message: str
    contact_hint: Optional[Dict[str, Any]] = None  # {email, phone, role}

class ChatReply(BaseModel):
    conversation_id: str
    reply: str
    extracted: Dict[str, Any]
