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

class StorySession(BaseModel):
    """Story session tracking for continuation"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str  # Conversation session ID
    user_id: str
    story_type: str  # e.g., "adventure", "fairy_tale", "educational"
    story_title: Optional[str] = None
    total_chunks: int = 0
    completed_chunks: int = 0
    last_chunk_index: int = -1
    full_story_text: str = ""
    current_state: str = "active"  # active, paused, completed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    continuation_context: Dict[str, Any] = {}  # For story continuation

class StorySessionCreate(BaseModel):
    """Story session creation model"""
    session_id: str
    user_id: str
    story_type: str = "adventure"
    story_title: Optional[str] = None

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