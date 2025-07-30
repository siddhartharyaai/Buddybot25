"""
Conversation and Session Models
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

class ConversationMessage(BaseModel):
    """Individual conversation message"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    user_id: str
    message_type: str  # 'user_text', 'user_voice', 'ai_response'
    content: str
    audio_base64: Optional[str] = None
    metadata: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    safety_checked: bool = False
    flagged: bool = False

class ConversationSession(BaseModel):
    """Conversation session model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    session_name: str = "Chat Session"
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    message_count: int = 0
    total_duration: int = 0  # in seconds
    session_status: str = "active"  # active, ended, paused
    context: Dict[str, Any] = {}
    
class ConversationSessionCreate(BaseModel):
    """Conversation session creation model"""
    user_id: str
    session_name: str = "Chat Session"
    
class VoiceInput(BaseModel):
    """Voice input model"""
    session_id: str
    user_id: str
    audio_base64: str
    
class TextInput(BaseModel):
    """Text input model"""
    session_id: str
    user_id: str
    message: str

class AIResponse(BaseModel):
    """AI response model"""
    response_text: str
    response_audio: Optional[str] = None
    content_type: str = "conversation"
    metadata: Dict[str, Any] = {}
    processing_time: float = 0.0
    
class ConversationHistory(BaseModel):
    """Conversation history model"""
    session_id: str
    messages: List[ConversationMessage] = []
    session_info: ConversationSession
    total_messages: int = 0
    safety_summary: Dict[str, Any] = {}