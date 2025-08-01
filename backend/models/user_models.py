"""
User and Profile Models
"""
from pydantic import BaseModel, Field, validator, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

class UserProfile(BaseModel):
    """User profile model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    age: int
    location: str
    timezone: str = "UTC"
    language: str = "english"
    voice_personality: str = "friendly_companion"
    interests: List[str] = []
    learning_goals: List[str] = []
    parent_email: Optional[str] = None
    # New fields from ProfileSetup
    gender: str = "prefer_not_to_say"
    avatar: str = "bunny"
    speech_speed: str = "normal"
    energy_level: str = "balanced"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('age')
    def validate_age(cls, v):
        if v < 3 or v > 12:
            raise ValueError('Age must be between 3 and 12')
        return v
    
    @validator('voice_personality')
    def validate_voice_personality(cls, v):
        valid_personalities = ['friendly_companion', 'story_narrator', 'learning_buddy']
        if v not in valid_personalities:
            raise ValueError(f'Voice personality must be one of: {valid_personalities}')
        return v

class UserProfileCreate(BaseModel):
    """User profile creation model"""
    name: str
    age: int
    location: str
    timezone: str = "UTC"
    language: str = "english"
    voice_personality: str = "friendly_companion"
    interests: List[str] = []
    learning_goals: List[str] = []
    parent_email: Optional[str] = None
    # New fields from ProfileSetup
    gender: str = "prefer_not_to_say"
    avatar: str = "bunny"
    speech_speed: str = "normal"
    energy_level: str = "balanced"

class UserProfileUpdate(BaseModel):
    """User profile update model"""
    name: Optional[str] = None
    age: Optional[int] = None
    location: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    voice_personality: Optional[str] = None
    interests: Optional[List[str]] = None
    learning_goals: Optional[List[str]] = None
    parent_email: Optional[str] = None
    # New fields from ProfileSetup
    gender: Optional[str] = None
    avatar: Optional[str] = None
    speech_speed: Optional[str] = None
    energy_level: Optional[str] = None

class ParentalControls(BaseModel):
    """Parental controls model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    time_limits: Dict[str, int] = {}  # day: minutes
    content_restrictions: List[str] = []
    allowed_content_types: List[str] = ["story", "song", "rhyme", "educational"]
    quiet_hours: Dict[str, Any] = {}  # start/end times
    monitoring_enabled: bool = True
    notification_preferences: Dict[str, bool] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ParentalControlsCreate(BaseModel):
    """Parental controls creation model"""
    user_id: str
    time_limits: Dict[str, int] = {}
    content_restrictions: List[str] = []
    allowed_content_types: List[str] = ["story", "song", "rhyme", "educational"]
    quiet_hours: Dict[str, Any] = {}
    monitoring_enabled: bool = True
    notification_preferences: Dict[str, bool] = {}

class ParentalControlsUpdate(BaseModel):
    """Parental controls update model"""
    time_limits: Optional[Dict[str, int]] = None
    content_restrictions: Optional[List[str]] = None
    allowed_content_types: Optional[List[str]] = None
    quiet_hours: Optional[Dict[str, Any]] = None
    monitoring_enabled: Optional[bool] = None
    notification_preferences: Optional[Dict[str, bool]] = None

# Authentication Models
class AuthUser(BaseModel):
    """User model for authentication"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    hashed_password: str
    profile_id: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserSignUp(BaseModel):
    """User sign up model"""
    email: EmailStr
    password: str
    name: str
    age: int
    location: str = "Unknown"
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v
    
    @validator('age')
    def validate_age(cls, v):
        if v < 3 or v > 12:
            raise ValueError('Age must be between 3 and 12')
        return v

class UserSignIn(BaseModel):
    """User sign in model"""
    email: EmailStr
    password: str

class Token(BaseModel):
    """JWT Token model"""
    access_token: str
    token_type: str
    user_id: str
    profile_id: Optional[str] = None

class TokenData(BaseModel):
    """Token data model"""
    email: Optional[str] = None
    user_id: Optional[str] = None