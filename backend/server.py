"""
AI Companion Device Backend - Multi-Agent Architecture
"""
from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Form, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
import logging
from pathlib import Path
import base64
import json
from typing import Dict, List, Any
from datetime import datetime
import time

# Import models
from models.user_models import UserProfile, UserProfileCreate, UserProfileUpdate, ParentalControls, ParentalControlsCreate, ParentalControlsUpdate
from models.conversation_models import ConversationSession, ConversationSessionCreate, VoiceInput, TextInput, AIResponse, ConversationHistory
from models.content_models import ContentCreate, ContentUpdate, ContentSuggestion, ContentLibrary

# Import agents
from agents.orchestrator import OrchestratorAgent

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Environment variables
MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
DEEPGRAM_API_KEY = os.environ.get('DEEPGRAM_API_KEY')

# Validate API keys
if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_key_here":
    logger.warning("GEMINI_API_KEY not set properly. Please add your key to .env file.")
if not DEEPGRAM_API_KEY or DEEPGRAM_API_KEY == "your_deepgram_key_here":
    logger.warning("DEEPGRAM_API_KEY not set properly. Please add your key to .env file.")

# MongoDB connection
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# Create FastAPI app
app = FastAPI(
    title="AI Companion Device API",
    description="Multi-agent AI companion system for children",
    version="1.0.0"
)

# Create API router
api_router = APIRouter(prefix="/api")

# Initialize orchestrator agent
orchestrator = None

@app.on_event("startup")
async def startup_event():
    """Initialize the multi-agent system"""
    global orchestrator
    try:
        orchestrator = OrchestratorAgent(
            db=db,
            gemini_api_key=GEMINI_API_KEY,
            deepgram_api_key=DEEPGRAM_API_KEY
        )
        logger.info("Multi-agent system initialized successfully")
        
        # Initialize default content if database is empty
        await init_default_content()
        
    except Exception as e:
        logger.error(f"Failed to initialize multi-agent system: {str(e)}")

# User Profile Management
@api_router.post("/users/profile", response_model=UserProfile)
async def create_user_profile(profile_data: UserProfileCreate):
    """Create a new user profile"""
    try:
        profile = UserProfile(**profile_data.dict())
        await db.user_profiles.insert_one(profile.dict())
        
        # Create default parental controls
        parental_controls = ParentalControls(
            user_id=profile.id,
            time_limits={"monday": 60, "tuesday": 60, "wednesday": 60, "thursday": 60, "friday": 60, "saturday": 90, "sunday": 90},
            content_restrictions=[],
            allowed_content_types=["story", "song", "rhyme", "educational"],
            quiet_hours={"start": "20:00", "end": "07:00"},
            monitoring_enabled=True,
            notification_preferences={"activity_summary": True, "safety_alerts": True}
        )
        await db.parental_controls.insert_one(parental_controls.dict())
        
        logger.info(f"Created user profile: {profile.id}")
        return profile
        
    except Exception as e:
        logger.error(f"Error creating user profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create user profile")

@api_router.get("/users/profile/{user_id}", response_model=UserProfile)
async def get_user_profile(user_id: str):
    """Get user profile by ID"""
    try:
        profile = await db.user_profiles.find_one({"id": user_id})
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        return UserProfile(**profile)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve user profile")

@api_router.put("/users/profile/{user_id}", response_model=UserProfile)
async def update_user_profile(user_id: str, profile_data: UserProfileUpdate):
    """Update user profile"""
    try:
        update_data = {k: v for k, v in profile_data.dict().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        result = await db.user_profiles.update_one(
            {"id": user_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        updated_profile = await db.user_profiles.find_one({"id": user_id})
        return UserProfile(**updated_profile)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update user profile")

@api_router.delete("/users/profile/{user_id}")
async def delete_user_profile(user_id: str):
    """Delete user profile and all associated data"""
    try:
        # Delete user profile
        profile_result = await db.user_profiles.delete_one({"id": user_id})
        
        if profile_result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Delete associated parental controls
        await db.parental_controls.delete_many({"user_id": user_id})
        
        # Delete conversation sessions
        await db.conversation_sessions.delete_many({"user_id": user_id})
        
        # Delete memory snapshots
        await db.memory_snapshots.delete_many({"user_id": user_id})
        
        logger.info(f"Successfully deleted user profile and all data for user: {user_id}")
        return {"message": "Profile deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete user profile")

# Parental Controls
@api_router.get("/users/{user_id}/parental-controls", response_model=ParentalControls)
async def get_parental_controls(user_id: str):
    """Get parental controls for user"""
    try:
        controls = await db.parental_controls.find_one({"user_id": user_id})
        if not controls:
            raise HTTPException(status_code=404, detail="Parental controls not found")
        
        return ParentalControls(**controls)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting parental controls: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve parental controls")

@api_router.put("/users/{user_id}/parental-controls", response_model=ParentalControls)
async def update_parental_controls(user_id: str, controls_data: ParentalControlsUpdate):
    """Update parental controls"""
    try:
        update_data = {k: v for k, v in controls_data.dict().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        result = await db.parental_controls.update_one(
            {"user_id": user_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Parental controls not found")
        
        updated_controls = await db.parental_controls.find_one({"user_id": user_id})
        return ParentalControls(**updated_controls)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating parental controls: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update parental controls")

# Conversation Management
@api_router.post("/conversations/session", response_model=ConversationSession)
async def create_conversation_session(session_data: ConversationSessionCreate):
    """Create a new conversation session"""
    try:
        session = ConversationSession(**session_data.dict())
        await db.conversation_sessions.insert_one(session.dict())
        
        logger.info(f"Created conversation session: {session.id}")
        return session
        
    except Exception as e:
        logger.error(f"Error creating conversation session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create conversation session")

@api_router.get("/content/stories", response_model=Dict[str, Any])
async def get_stories():
    """Get all available stories"""
    try:
        stories = await orchestrator.enhanced_content_agent.get_stories()
        return {"stories": stories}
    except Exception as e:
        logger.error(f"Error fetching stories: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch stories")

@api_router.post("/content/stories/{story_id}/narrate")
async def narrate_story(story_id: str, user_id: str = Form(...)):
    """OPTIMIZED: Serve pre-cached story audio - No real-time generation"""
    try:
        logger.info(f"🎵 SERVING CACHED STORY AUDIO: {story_id} for user {user_id}")
        
        # Get story data from enhanced_content_agent
        story_result = await orchestrator.enhanced_content_agent.get_story_narration(story_id, user_id)
        
        if "error" in story_result:
            logger.error(f"❌ Story not found: {story_result['error']}")
            return {
                "status": "error",
                "error": story_result["error"],
                "message": "Story not available"
            }
        
        # Check if we have cached audio for this story
        cached_audio = story_result.get("cached_audio", "")
        story_title = story_result.get("title", "Story")
        story_text = story_result.get("complete_text", "")
        
        if cached_audio:
            logger.info(f"✅ SERVING CACHED AUDIO: {story_title} ({len(cached_audio)} chars)")
            return {
                "status": "success",
                "response_text": story_text,
                "response_audio": cached_audio,
                "story_title": story_title,
                "source": "cached",
                "word_count": len(story_text.split())
            }
        else:
            logger.warning(f"⚠️ NO CACHED AUDIO for {story_title} - audio not pre-generated")
            return {
                "status": "error", 
                "error": "Audio not available",
                "message": "Story audio is being prepared. Please try again later.",
                "response_text": story_text,  # Still provide text
                "response_audio": ""
            }
        
    except Exception as e:
        logger.error(f"❌ Story narration error: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "message": "Could not load story"
        }

# Cache Management Endpoints
@api_router.post("/admin/clear-content-cache")
async def clear_content_cache():
    """Admin endpoint to clear all cached content"""
    try:
        logger.info("🗑️ ADMIN REQUEST: Clearing content cache...")
        
        # Clear database cache
        db_result = await db.cached_content.delete_many({})
        
        # Clear in-memory cache
        orchestrator.enhanced_content_agent.content_cache.clear()
        orchestrator.enhanced_content_agent.story_audio_cache.clear()
        
        return {
            "status": "success",
            "message": f"Content cache cleared",
            "deleted_records": db_result.deleted_count if db_result else 0
        }
        
    except Exception as e:
        logger.error(f"❌ Admin cache clear error: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "message": "Cache clear failed"
        }

@api_router.get("/admin/cache-stats")
async def get_cache_stats():
    """Admin endpoint to get cache statistics"""
    try:
        # Get database cache stats
        total_cached = await db.cached_content.count_documents({})
        cache_by_type = await db.cached_content.aggregate([
            {"$group": {"_id": "$content_type", "count": {"$sum": 1}}}
        ]).to_list(100)
        
        # Get in-memory cache stats
        memory_cache_size = len(orchestrator.enhanced_content_agent.content_cache)
        audio_cache_size = len(orchestrator.enhanced_content_agent.story_audio_cache)
        
        return {
            "status": "success",
            "database_cache": {
                "total_records": total_cached,
                "by_type": {item["_id"]: item["count"] for item in cache_by_type}
            },
            "memory_cache": {
                "content_cache_size": memory_cache_size,
                "audio_cache_size": audio_cache_size
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Admin cache stats error: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "message": "Cache stats failed"
        }

# Voice Processing Endpoints
@api_router.post("/admin/generate-story-audio")
async def generate_story_audio_cache(force_regenerate: bool = False):
    """Admin endpoint to pre-generate and cache all story audio"""
    try:
        logger.info("🎵 ADMIN REQUEST: Starting story audio cache generation...")
        
        result = await orchestrator.enhanced_content_agent.pre_generate_story_audio(
            orchestrator.voice_agent, 
            force_regenerate=force_regenerate
        )
        
        if result.get("success"):
            return {
                "status": "success",
                "message": f"Story audio cache generation completed",
                "generated": result.get("generated", 0),
                "skipped": result.get("skipped", 0),
                "total": result.get("total", 0)
            }
        else:
            return {
                "status": "error", 
                "error": result.get("error", "Unknown error"),
                "message": "Story audio cache generation failed"
            }
            
    except Exception as e:
        logger.error(f"❌ Admin story audio generation error: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "message": "Story audio cache generation failed"
        }

# Voice Processing Endpoints
# Voice Processing Endpoints
@api_router.post("/voice/tts")
async def text_to_speech_simple(request: dict):
    """Simple TTS endpoint for initial greetings and basic text-to-speech"""
    try:
        if not orchestrator:
            raise HTTPException(status_code=500, detail="Multi-agent system not initialized")
        
        text = request.get("text", "")
        personality = request.get("personality", "friendly_companion")
        
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        logger.info(f"🔊 TTS Request: '{text[:50]}...' with personality '{personality}'")
        
        # Generate TTS audio using voice agent with proper chunking for long texts
        voice_agent = orchestrator.voice_agent
        
        # Use chunked processing for texts over 1500 characters
        if len(text) > 1500:
            response_audio = await voice_agent.text_to_speech_chunked(text, personality)
        else:
            response_audio = await voice_agent.text_to_speech(text, personality)
        
        if response_audio:
            return {
                "status": "success", 
                "audio_base64": response_audio,
                "text": text,
                "personality": personality
            }
        else:
            return {
                "status": "error",
                "error": "TTS generation failed",
                "text": text
            }
            
    except Exception as e:
        logger.error(f"❌ TTS error: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "text": request.get("text", "")
        }

@api_router.post("/voice/tts/streaming")
async def text_to_speech_streaming(request: dict):
    """Streaming TTS endpoint for long content like stories"""
    try:
        if not orchestrator:
            raise HTTPException(status_code=500, detail="Multi-agent system not initialized")
        
        text = request.get("text", "")
        personality = request.get("personality", "friendly_companion")
        
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        logger.info(f"🎵 Streaming TTS Request: {len(text)} chars with personality '{personality}'")
        
        # Generate streaming TTS
        voice_agent = orchestrator.voice_agent
        result = await voice_agent.text_to_speech_streaming(text, personality)
        
        return result
            
    except Exception as e:
        logger.error(f"❌ Streaming TTS error: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }

@api_router.post("/voice/tts/chunk")
async def generate_audio_chunk(request: dict):
    """Generate audio for a specific text chunk"""
    try:
        if not orchestrator:
            raise HTTPException(status_code=500, detail="Multi-agent system not initialized")
        
        text = request.get("text", "")
        personality = request.get("personality", "friendly_companion")
        
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        # Generate audio for chunk
        voice_agent = orchestrator.voice_agent
        audio_base64 = await voice_agent.generate_chunk_audio(text, personality)
        
        if audio_base64:
            return {
                "status": "success",
                "audio_base64": audio_base64
            }
        else:
            return {
                "status": "error",
                "error": "Failed to generate chunk audio"
            }
            
    except Exception as e:
        logger.error(f"❌ Chunk TTS error: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }

@api_router.post("/voice/process_audio")
async def process_voice_input(
    session_id: str = Form(...),
    user_id: str = Form(...),
    audio_base64: str = Form(...)
):
    """ULTRA-LOW LATENCY: Process voice input with streaming pipeline"""
    try:
        import time
        start_time = time.time()
        logger.info(f"🚀 ULTRA-FAST voice processing started for session {session_id}")
        
        # Convert base64 to bytes
        audio_data = base64.b64decode(audio_base64)
        logger.info(f"📥 Audio data received: {len(audio_data)} bytes")
        
        # Get user profile
        user_profile = await get_user_profile(user_id)
        if not user_profile:
            user_profile = {"id": user_id, "name": "Demo Kid", "age": 7}
        else:
            # Convert UserProfile object to dictionary for compatibility
            if hasattr(user_profile, 'dict'):
                user_profile = user_profile.dict()
            elif hasattr(user_profile, '__dict__'):
                user_profile = user_profile.__dict__
            else:
                # Ensure it has required fields
                user_profile = {
                    "id": getattr(user_profile, 'id', user_id),
                    "name": getattr(user_profile, 'name', 'Demo Kid'),
                    "age": getattr(user_profile, 'age', 7)
                }
        
        # Use ULTRA-LOW LATENCY streaming pipeline
        try:
            result = await orchestrator.process_voice_streaming(session_id, audio_data, user_profile)
            
            if "error" in result:
                logger.error(f"❌ Streaming pipeline error: {result['error']}")
                # Fallback to regular processing
                result = await orchestrator.process_voice_input_enhanced(session_id, audio_data, user_profile)
        except Exception as e:
            logger.error(f"❌ Streaming pipeline failed: {str(e)}")
            # Fallback to regular processing - FIXED METHOD NAME
            result = await orchestrator.process_voice_input_enhanced(session_id, audio_data, user_profile)
        
        # Measure total latency
        total_latency = time.time() - start_time
        logger.info(f"⚡ TOTAL VOICE PROCESSING LATENCY: {total_latency:.2f}s")
        
        # Add latency info to response
        result["total_latency"] = f"{total_latency:.2f}s"
        result["pipeline_type"] = "streaming" if "pipeline" in result else "regular"
        
        return {
            "status": "success",
            "transcript": result.get("transcript", ""),
            "response_text": result.get("response_text", "I heard you!"),
            "response_audio": result.get("response_audio"),
            "content_type": result.get("content_type", "conversation"),
            "metadata": result.get("metadata", {}),
            "latency": result.get("total_latency", "unknown"),
            "pipeline": result.get("pipeline_type", "regular")
        }
        
    except Exception as e:
        logger.error(f"❌ Voice processing error: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "message": "Voice processing failed"
        }

@api_router.post("/conversations/voice", response_model=AIResponse)
async def process_voice_input(voice_input: VoiceInput):
    """Process voice input through the multi-agent system"""
    try:
        if not orchestrator:
            raise HTTPException(status_code=500, detail="Multi-agent system not initialized")
        
        # Get user profile
        user_profile = await db.user_profiles.find_one({"id": voice_input.user_id})
        if not user_profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Decode audio data
        audio_data = base64.b64decode(voice_input.audio_base64)
        
        # Process through orchestrator
        result = await orchestrator.process_voice_input(
            voice_input.session_id,
            audio_data,
            user_profile
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return AIResponse(
            response_text=result["response_text"],
            response_audio=result.get("response_audio"),
            content_type=result.get("content_type", "conversation"),
            metadata=result.get("metadata", {})
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing voice input: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process voice input")

@api_router.post("/conversations/text", response_model=AIResponse)
async def process_text_input(text_input: TextInput):
    """Process text input through the multi-agent system"""
    try:
        if not orchestrator:
            raise HTTPException(status_code=500, detail="Multi-agent system not initialized")
        
        # Get user profile or create a default one
        user_profile = await db.user_profiles.find_one({"id": text_input.user_id})
        if not user_profile:
            # Create a default user profile for testing/new users
            default_profile = {
                "id": text_input.user_id,
                "user_id": text_input.user_id,  # Add both for compatibility
                "name": "Test User",
                "age": 7,
                "preferences": {
                    "voice_personality": "friendly_companion",
                    "learning_goals": ["general_knowledge"],
                    "favorite_topics": []
                },
                "created_at": datetime.now().isoformat()
            }
            
            # Store the profile
            try:
                await db.user_profiles.insert_one(default_profile)
                logger.info(f"Created default profile for user {text_input.user_id}")
            except Exception as e:
                logger.warning(f"Could not store user profile: {e}")
            
            user_profile = default_profile
        
        # Process through orchestrator
        result = await orchestrator.process_text_input(
            text_input.session_id,
            text_input.message,
            user_profile
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return AIResponse(
            response_text=result["response_text"],
            response_audio=result.get("response_audio"),
            content_type=result.get("content_type", "conversation"),
            metadata=result.get("metadata", {})
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing text input: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process text input")

# Content Management
@api_router.get("/content/suggestions/{user_id}", response_model=List[ContentSuggestion])
async def get_content_suggestions(user_id: str):
    """Get content suggestions for user"""
    try:
        if not orchestrator:
            raise HTTPException(status_code=500, detail="Multi-agent system not initialized")
        
        # Get user profile
        user_profile = await db.user_profiles.find_one({"id": user_id})
        if not user_profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Get suggestions from content agent
        suggestions = await orchestrator.content_agent.get_content_suggestions(user_profile)
        
        return [ContentSuggestion(**suggestion) for suggestion in suggestions]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting content suggestions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get content suggestions")

@api_router.post("/conversations/voice")
async def process_voice_input(request: dict):
    """Process voice input - simple like ChatGPT/Gemini voice bots"""
    try:
        if not orchestrator:
            raise HTTPException(status_code=500, detail="Multi-agent system not initialized")
        
        session_id = request.get("session_id")
        user_id = request.get("user_id", "test_user")
        audio_base64 = request.get("audio_base64")
        
        if not audio_base64:
            raise HTTPException(status_code=400, detail="audio_base64 is required")
        
        logger.info(f"🎤 Processing voice input: session={session_id}, audio_length={len(audio_base64)}")
        
        # Decode audio data
        try:
            audio_data = base64.b64decode(audio_base64)
            logger.info(f"✅ Decoded audio: {len(audio_data)} bytes")
        except Exception as decode_error:
            logger.error(f"❌ Base64 decode error: {str(decode_error)}")
            raise HTTPException(status_code=400, detail="Invalid base64 audio data")
        
        # Get or create user profile
        user_profile = await db.user_profiles.find_one({"id": user_id})
        if not user_profile:
            # Create a default user profile
            user_profile = {
                "id": user_id,
                "name": "Test Child",
                "age": 8,
                "language": "english",
                "voice_personality": "friendly_companion",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            await db.user_profiles.insert_one(user_profile)
            logger.info(f"✅ Created default user profile: {user_id}")
        
        # Process through voice agent (STT)
        voice_agent = orchestrator.voice_agent
        transcript = await voice_agent.speech_to_text(audio_data)
        
        if not transcript:
            return {
                "status": "no_speech",
                "response_text": "I didn't catch that. Could you please repeat?",
                "response_audio": None,
                "transcript": ""
            }
        
        logger.info(f"🎤 STT result: '{transcript}'")
        
        # Process through conversation agent (LLM)
        conversation_agent = orchestrator.conversation_agent
        response = await conversation_agent.generate_response(
            user_input=transcript,
            user_profile=user_profile,
            conversation_context=[]  # Simple context for now
        )
        
        # Generate TTS audio
        response_audio = await voice_agent.text_to_speech(
            response['text'],
            user_profile.get('voice_personality', 'friendly_companion')
        )
        
        result = {
            "status": "success",
            "response_text": response['text'],
            "response_audio": response_audio,
            "transcript": transcript,
            "content_type": response.get('content_type', 'conversation'),
            "processing_time": response.get('processing_time', 0.0)
        }
        
        logger.info(f"✅ Voice processing complete: '{response['text'][:100]}...'")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Voice processing error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Voice processing failed: {str(e)}")

# Voice Personalities
@api_router.get("/voice/personalities")
async def get_voice_personalities():
    """Get available voice personalities"""
    try:
        if not orchestrator:
            raise HTTPException(status_code=500, detail="Multi-agent system not initialized")
        
        personalities = orchestrator.voice_agent.get_available_voices()
        return personalities
        
    except Exception as e:
        logger.error(f"Error getting voice personalities: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get voice personalities")

# Memory Management Endpoints
@api_router.post("/memory/snapshot/{user_id}")
async def generate_memory_snapshot(user_id: str):
    """Generate daily memory snapshot for a user"""
    try:
        if not orchestrator:
            raise HTTPException(status_code=500, detail="Multi-agent system not initialized")
        
        snapshot = await orchestrator.generate_daily_memory_snapshot(user_id)
        return snapshot
        
    except Exception as e:
        logger.error(f"Error generating memory snapshot: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate memory snapshot")

@api_router.get("/memory/context/{user_id}")
async def get_memory_context(user_id: str, days: int = 7):
    """Get memory context for a user"""
    try:
        if not orchestrator:
            raise HTTPException(status_code=500, detail="Multi-agent system not initialized")
        
        memory_context = await orchestrator.memory_agent.get_user_memory_context(user_id, days)
        return memory_context
        
    except Exception as e:
        logger.error(f"Error getting memory context: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get memory context")

@api_router.get("/memory/snapshots/{user_id}")
async def get_memory_snapshots(user_id: str, days: int = 30):
    """Get memory snapshots for a user"""
    try:
        from datetime import timedelta
        
        # Get memory snapshots from database
        start_date = datetime.utcnow() - timedelta(days=days)
        
        snapshots = await db.memory_snapshots.find({
            "user_id": user_id,
            "created_at": {"$gte": start_date}
        }).sort("created_at", -1).to_list(length=days)
        
        return {"user_id": user_id, "snapshots": snapshots, "count": len(snapshots)}
        
    except Exception as e:
        logger.error(f"Error getting memory snapshots: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get memory snapshots")

# Telemetry and Analytics Endpoints
@api_router.get("/analytics/dashboard/{user_id}")
async def get_analytics_dashboard(user_id: str, days: int = 7):
    """Get analytics dashboard for a user"""
    try:
        if not orchestrator:
            raise HTTPException(status_code=500, detail="Multi-agent system not initialized")
        
        dashboard = await orchestrator.get_user_analytics_dashboard(user_id, days)
        return dashboard
        
    except Exception as e:
        logger.error(f"Error getting analytics dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get analytics dashboard")

@api_router.get("/analytics/global")
async def get_global_analytics(days: int = 7):
    """Get global analytics dashboard"""
    try:
        if not orchestrator:
            raise HTTPException(status_code=500, detail="Multi-agent system not initialized")
        
        dashboard = await orchestrator.telemetry_agent.get_analytics_dashboard(None, days)
        return dashboard
        
    except Exception as e:
        logger.error(f"Error getting global analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get global analytics")

@api_router.get("/flags/{user_id}")
async def get_user_flags(user_id: str):
    """Get feature flags for a user"""
    try:
        if not orchestrator:
            raise HTTPException(status_code=500, detail="Multi-agent system not initialized")
        
        flags = await orchestrator.get_user_flags(user_id)
        return {"user_id": user_id, "flags": flags}
        
    except Exception as e:
        logger.error(f"Error getting user flags: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user flags")

@api_router.put("/flags/{user_id}")
async def update_user_flags(user_id: str, flags: Dict[str, Any]):
    """Update feature flags for a user"""
    try:
        if not orchestrator:
            raise HTTPException(status_code=500, detail="Multi-agent system not initialized")
        
        await orchestrator.update_user_flags(user_id, flags)
        return {"user_id": user_id, "flags": flags, "status": "updated"}
        
    except Exception as e:
        logger.error(f"Error updating user flags: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update user flags")

@api_router.post("/session/end/{session_id}")
async def end_session(session_id: str):
    """End a session and get telemetry summary"""
    try:
        if not orchestrator:
            raise HTTPException(status_code=500, detail="Multi-agent system not initialized")
        
        summary = await orchestrator.end_session(session_id)
        return summary
        
    except Exception as e:
        logger.error(f"Error ending session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to end session")

@api_router.get("/agents/status")
async def get_agents_status():
    """Get status of all agents including memory and telemetry statistics"""
    try:
        if not orchestrator:
            raise HTTPException(status_code=500, detail="Multi-agent system not initialized")
        
        status = await orchestrator.get_agent_status()
        return status
        
    except Exception as e:
        logger.error(f"Error getting agents status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get agents status")

@api_router.post("/maintenance/cleanup")
async def cleanup_old_data(memory_days: int = 30, telemetry_days: int = 90):
    """Clean up old memory snapshots and telemetry data"""
    try:
        if not orchestrator:
            raise HTTPException(status_code=500, detail="Multi-agent system not initialized")
        
        result = await orchestrator.cleanup_old_data(memory_days, telemetry_days)
        return result
        
    except Exception as e:
        logger.error(f"Error cleaning up old data: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to cleanup old data")

# Health Check
@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agents": {
            "orchestrator": orchestrator is not None,
            "gemini_configured": GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_key_here",
            "deepgram_configured": DEEPGRAM_API_KEY and DEEPGRAM_API_KEY != "your_deepgram_key_here"
        },
        "database": "connected"
    }

# Content API Endpoints
@api_router.get("/content/stories")
async def get_stories():
    """Get all available stories"""
    try:
        if not orchestrator:
            raise HTTPException(status_code=500, detail="Multi-agent system not initialized")
        
        # Get stories from the enhanced content agent's local library
        enhanced_content_agent = orchestrator.enhanced_content_agent
        local_content = enhanced_content_agent.local_content
        
        stories = []
        for story_data in local_content.get("stories", []):
            story = {
                "id": story_data["id"],
                "title": story_data["title"],
                "description": story_data.get("description", ""),
                "content": story_data["content"],
                "category": story_data.get("category", "general"),
                "duration": story_data.get("duration", "5 min"),
                "age_group": story_data.get("age_groups", ["3-12"])[0] if story_data.get("age_groups") else "3-12",
                "tags": story_data.get("tags", []),
                "moral": story_data.get("moral", "")
            }
            stories.append(story)
        
        return {"stories": stories}
        
    except Exception as e:
        logger.error(f"Error fetching stories: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch stories")

@api_router.get("/content/{content_type}")
async def get_content_by_type(content_type: str):
    """Get content by type (jokes, riddles, facts, songs, rhymes, stories, games)"""
    try:
        if not orchestrator:
            raise HTTPException(status_code=500, detail="Multi-agent system not initialized")
        
        enhanced_content_agent = orchestrator.enhanced_content_agent
        local_content = enhanced_content_agent.local_content
        
        if content_type not in local_content:
            raise HTTPException(status_code=404, detail=f"Content type '{content_type}' not found")
        
        content_list = local_content[content_type]
        
        return {
            "content_type": content_type,
            "count": len(content_list),
            "content": content_list
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching {content_type}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch {content_type}")

@api_router.post("/content/generate")
async def generate_content(request: dict):
    """Generate content using enhanced content agent"""
    try:
        if not orchestrator:
            raise HTTPException(status_code=500, detail="Multi-agent system not initialized")
        
        content_type = request.get("content_type")
        user_input = request.get("user_input", "")
        user_id = request.get("user_id")
        
        if not content_type or not user_id:
            raise HTTPException(status_code=400, detail="content_type and user_id are required")
        
        # Get user profile
        user_profile = await db.user_profiles.find_one({"id": user_id})
        if not user_profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        enhanced_content_agent = orchestrator.enhanced_content_agent
        result = await enhanced_content_agent.get_content_with_3tier_sourcing(
            content_type, user_profile, user_input
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating content: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate content")

# WebSocket for real-time communication
@api_router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time communication"""
    await websocket.accept()
    
    try:
        # Get user profile
        user_profile = await db.user_profiles.find_one({"id": user_id})
        if not user_profile:
            await websocket.send_text(json.dumps({"error": "User profile not found"}))
            await websocket.close()
            return
        
        while True:
            # Receive message
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data.get("type") == "text":
                # Process text message
                result = await orchestrator.process_text_input(
                    message_data["session_id"],
                    message_data["message"],
                    user_profile
                )
                
                await websocket.send_text(json.dumps(result))
                
            elif message_data.get("type") == "voice":
                # Process voice message
                audio_data = base64.b64decode(message_data["audio_base64"])
                result = await orchestrator.process_voice_input(
                    message_data["session_id"],
                    audio_data,
                    user_profile
                )
                
                await websocket.send_text(json.dumps(result))
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user: {user_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.send_text(json.dumps({"error": "Connection error"}))

async def init_default_content():
    """Initialize default content if database is empty"""
    try:
        # Check if content exists
        story_count = await db.stories.count_documents({})
        
        if story_count == 0:
            logger.info("Initializing default content...")
            
            # Add default stories
            default_stories = [
                {
                    "id": "story_001",
                    "title": "The Happy Little Bear",
                    "content": "Once there was a little bear who loved to play. He played with his friends every day in the forest. The bear was always happy and kind to everyone. The end!",
                    "age_group": "toddler",
                    "language": "english",
                    "tags": ["animals", "friendship", "happiness"],
                    "difficulty_level": 1,
                    "content_type": "story",
                    "story_type": "fairy_tale",
                    "reading_time": 2
                },
                {
                    "id": "story_002", 
                    "title": "The Brave Little Mouse",
                    "content": "A small mouse lived in a big house. One day, he helped his family by being very brave and clever. Everyone was proud of him and celebrated his courage!",
                    "age_group": "child",
                    "language": "english",
                    "tags": ["courage", "family", "problem-solving"],
                    "difficulty_level": 2,
                    "content_type": "story",
                    "story_type": "moral",
                    "reading_time": 3
                }
            ]
            
            await db.stories.insert_many(default_stories)
            
            # Add default songs
            default_songs = [
                {
                    "id": "song_001",
                    "title": "Twinkle Twinkle Little Star",
                    "content": "Twinkle, twinkle, little star, How I wonder what you are! Up above the world so high, Like a diamond in the sky!",
                    "age_group": "toddler",
                    "language": "english",
                    "tags": ["stars", "wonder", "night"],
                    "difficulty_level": 1,
                    "content_type": "song",
                    "song_type": "lullaby",
                    "lyrics": "Twinkle, twinkle, little star, How I wonder what you are!",
                    "duration": 60
                }
            ]
            
            await db.songs.insert_many(default_songs)
            
            logger.info("Default content initialized successfully")
            
    except Exception as e:
        logger.error(f"Error initializing default content: {str(e)}")

# Include router in main app
app.include_router(api_router)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================================================================
# NEW ULTRA-LOW LATENCY API ENDPOINTS (ADDED - NO EXISTING ENDPOINTS MODIFIED)
# ========================================================================

@api_router.post("/voice/process_audio_fast")
async def process_voice_input_fast(
    session_id: str = Form(...),
    user_id: str = Form(...),
    audio_base64: str = Form(...)
):
    """NEW FAST ENDPOINT: Ultra-low latency voice processing (< 3 seconds target)"""
    try:
        import time
        start_time = time.time()
        logger.info(f"🚀 FAST VOICE API: Starting ultra-low latency processing for session {session_id}")
        
        # Convert base64 to bytes
        audio_data = base64.b64decode(audio_base64)
        logger.info(f"📥 Audio data received: {len(audio_data)} bytes")
        
        # Get user profile (simple lookup)
        user_profile = await get_user_profile(user_id)
        if not user_profile:
            user_profile = {"id": user_id, "name": "Demo Kid", "age": 7}
        else:
            # Convert UserProfile object to dictionary for compatibility
            if hasattr(user_profile, 'dict'):
                user_profile = user_profile.dict()
            elif hasattr(user_profile, '__dict__'):
                user_profile = user_profile.__dict__
            else:
                user_profile = {
                    "id": getattr(user_profile, 'id', user_id),
                    "name": getattr(user_profile, 'name', 'Demo Kid'),
                    "age": getattr(user_profile, 'age', 7)
                }
        
        # Use NEW fast processing pipeline
        result = await orchestrator.process_voice_input_fast(session_id, audio_data, user_profile)
        
        # Measure total latency
        total_latency = time.time() - start_time
        logger.info(f"⚡ FAST VOICE API COMPLETE: {total_latency:.2f}s total latency")
        
        # Add latency info to response
        result["api_latency"] = f"{total_latency:.2f}s"
        result["pipeline_type"] = "fast"
        
        return {
            "status": "success",
            "transcript": result.get("transcript", ""),
            "response_text": result.get("response_text", "I heard you!"),
            "response_audio": result.get("response_audio"),
            "content_type": result.get("content_type", "conversation"),
            "metadata": result.get("metadata", {}),
            "latency": result.get("api_latency", "unknown"),
            "pipeline": "fast"
        }
        
    except Exception as e:
        logger.error(f"❌ Fast voice processing error: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "message": "Fast voice processing failed"
        }

@api_router.post("/conversations/text_fast")
async def process_text_input_fast(text_input: dict):
    """NEW FAST ENDPOINT: Ultra-low latency text processing (< 2 seconds target)"""
    try:
        import time
        start_time = time.time()
        logger.info(f"🚀 FAST TEXT API: Starting ultra-low latency processing")
        
        if not orchestrator:
            raise HTTPException(status_code=500, detail="Multi-agent system not initialized")
        
        # Extract parameters
        session_id = text_input.get("session_id")
        user_id = text_input.get("user_id") 
        message = text_input.get("message")
        
        if not all([session_id, user_id, message]):
            raise HTTPException(status_code=400, detail="Missing required fields: session_id, user_id, message")
        
        # Get user profile (simple lookup)
        user_profile = await db.user_profiles.find_one({"id": user_id})
        if not user_profile:
            # Create a minimal default profile for speed
            user_profile = {
                "id": user_id,
                "user_id": user_id,
                "name": "Test User", 
                "age": 7,
                "preferences": {"voice_personality": "friendly_companion"}
            }
        
        # Use NEW fast processing pipeline
        result = await orchestrator.process_text_input_fast(session_id, message, user_profile)
        
        # Measure total latency
        total_latency = time.time() - start_time
        logger.info(f"⚡ FAST TEXT API COMPLETE: {total_latency:.2f}s total latency")
        
        # Add latency info to response
        result["api_latency"] = f"{total_latency:.2f}s"
        
        return {
            "status": "success",
            "response_text": result.get("response_text", "Hello!"),
            "response_audio": result.get("response_audio"),
            "content_type": result.get("content_type", "conversation"),
            "metadata": result.get("metadata", {}),
            "latency": result.get("api_latency", "unknown"),
            "pipeline": "fast_text"
        }
        
    except Exception as e:
        logger.error(f"❌ Fast text processing error: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "message": "Fast text processing failed"
        }

@app.on_event("shutdown")
async def shutdown_db_client():
    """Cleanup on shutdown"""
    client.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
