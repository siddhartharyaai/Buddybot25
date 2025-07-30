"""
Content Models - Stories, Songs, Rhymes, Games, Educational Content
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

class ContentBase(BaseModel):
    """Base content model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str
    age_group: str  # toddler, child, preteen
    language: str = "english"
    tags: List[str] = []
    difficulty_level: int = 1  # 1-5 scale
    audio_base64: Optional[str] = None
    metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('age_group')
    def validate_age_group(cls, v):
        valid_groups = ['toddler', 'child', 'preteen']
        if v not in valid_groups:
            raise ValueError(f'Age group must be one of: {valid_groups}')
        return v
    
    @validator('difficulty_level')
    def validate_difficulty(cls, v):
        if v < 1 or v > 5:
            raise ValueError('Difficulty level must be between 1 and 5')
        return v

class Story(ContentBase):
    """Story content model"""
    content_type: str = "story"
    story_type: str = "fairy_tale"  # fairy_tale, educational, adventure, moral
    characters: List[str] = []
    moral_lesson: Optional[str] = None
    reading_time: int = 5  # minutes
    
class Song(ContentBase):
    """Song content model"""
    content_type: str = "song"
    song_type: str = "lullaby"  # lullaby, learning, action, folk
    lyrics: str
    melody_data: Optional[str] = None
    duration: int = 120  # seconds
    
class NurseryRhyme(ContentBase):
    """Nursery rhyme content model"""
    content_type: str = "rhyme"
    rhyme_type: str = "traditional"  # traditional, modern, educational
    rhythm_pattern: Optional[str] = None
    actions: List[str] = []  # physical actions for the rhyme
    
class Game(ContentBase):
    """Game content model"""
    content_type: str = "game"
    game_type: str = "educational"  # educational, puzzle, trivia, creative
    instructions: str
    rules: List[str] = []
    expected_duration: int = 10  # minutes
    
class EducationalContent(ContentBase):
    """Educational content model"""
    content_type: str = "educational"
    subject: str  # math, science, language, social
    learning_objectives: List[str] = []
    quiz_questions: List[Dict[str, Any]] = []
    
class ContentCreate(BaseModel):
    """Content creation model"""
    title: str
    content: str
    content_type: str  # story, song, rhyme, game, educational
    age_group: str
    language: str = "english"
    tags: List[str] = []
    difficulty_level: int = 1
    metadata: Dict[str, Any] = {}
    
class ContentUpdate(BaseModel):
    """Content update model"""
    title: Optional[str] = None
    content: Optional[str] = None
    age_group: Optional[str] = None
    language: Optional[str] = None
    tags: Optional[List[str]] = None
    difficulty_level: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    
class ContentSuggestion(BaseModel):
    """Content suggestion model"""
    content_id: str
    title: str
    content_type: str
    description: str
    relevance_score: float = 1.0
    age_appropriate: bool = True
    
class ContentLibrary(BaseModel):
    """Content library model"""
    stories: List[Story] = []
    songs: List[Song] = []
    rhymes: List[NurseryRhyme] = []
    games: List[Game] = []
    educational: List[EducationalContent] = []
    total_items: int = 0
    last_updated: datetime = Field(default_factory=datetime.utcnow)