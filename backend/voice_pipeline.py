"""
Camb.ai TTS Pipeline - Complete voice integration with MARS model
Handles voice fetching, filtering, selection, and TTS generation
"""
import asyncio
import logging
import time
import httpx
import os
from typing import Dict, List, Optional, Any
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

class CambAIVoicePipeline:
    """Complete Camb.ai voice pipeline for Buddy Bot MVP"""
    
    def __init__(self, mongo_client: AsyncIOMotorClient):
        self.api_key = os.getenv("CAMB_AI_API_KEY")
        if not self.api_key:
            raise ValueError("CAMB_AI_API_KEY environment variable is required")
        
        self.base_url = "https://client.camb.ai/apis"
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        # MongoDB setup
        self.mongo_client = mongo_client
        self.db = mongo_client.ai_companion_db
        self.voices_collection = self.db.camb_voices
        
        # HTTP client with optimized settings
        self.http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(20.0),
            limits=httpx.Limits(max_connections=5, max_keepalive_connections=2)
        )
        
        # Voice mapping for personalities
        self.personality_voice_map = {}
        self.fallback_voices = {
            "english_female": None,
            "hindi_female": None
        }
        
        # SSML templates for personalities
        self.ssml_templates = {
            "friendly_companion": {
                "prosody": '<prosody rate="medium" pitch="+5%" volume="medium">',
                "fillers": ["um", "you know", "well"],
                "expressions": ["*chuckles*", "*giggles softly*"]
            },
            "story_narrator": {
                "prosody": '<prosody rate="slow" pitch="+0%" volume="soft">',
                "fillers": ["now", "and then", "you see"],
                "expressions": ["*whispers*", "*with wonder*"]
            },
            "learning_buddy": {
                "prosody": '<prosody rate="medium" pitch="+8%" volume="medium">',
                "fillers": ["so", "let's see", "interesting"],
                "expressions": ["*excited*", "*encouragingly*"]
            }
        }
        
        logger.info("✅ Camb.ai Voice Pipeline initialized")

    async def initialize(self):
        """Initialize voice pipeline - fetch and cache voices"""
        try:
            await self.fetch_and_cache_voices()
            await self.setup_voice_mappings()
            logger.info("✅ Camb.ai Voice Pipeline ready")
        except Exception as e:
            logger.error(f"❌ Voice Pipeline initialization failed: {str(e)}")
            await self.setup_fallback_voices()

    async def fetch_and_cache_voices(self):
        """Fetch voices from Camb.ai and cache in MongoDB"""
        try:
            logger.info("🎵 Fetching voices from Camb.ai...")
            
            response = await self.http_client.get(
                f"{self.base_url}/list-voices",
                headers=self.headers
            )
            response.raise_for_status()
            
            voices_data = response.json()
            logger.info(f"🎵 Retrieved {len(voices_data)} voices from Camb.ai")
            
            # Clear existing cache
            await self.voices_collection.delete_many({})
            
            # Filter and cache suitable voices
            suitable_voices = []
            for voice in voices_data:
                # We'll use all female voices for now, regardless of published status
                if voice.get("gender") == 2:  # Female voices
                    voice["cached_at"] = time.time()
                    voice["suitability_score"] = self._calculate_voice_suitability(voice)
                    suitable_voices.append(voice)
            
            if suitable_voices:
                await self.voices_collection.insert_many(suitable_voices)
                logger.info(f"✅ Cached {len(suitable_voices)} suitable voices")
            else:
                logger.warning("⚠️ No suitable voices found, using fallback strategy")
                await self.setup_fallback_voices()
            
            # Create indexes
            await self.voices_collection.create_index([("gender", 1), ("age", 1), ("language", 1)])
            
        except Exception as e:
            logger.error(f"❌ Error fetching voices: {str(e)}")
            await self.setup_fallback_voices()

    def _calculate_voice_suitability(self, voice: Dict) -> float:
        """Calculate suitability score for kid-friendly voices"""
        score = 0.0
        age = voice.get("age", 50)
        description = voice.get("description", "").lower()
        
        # Age preference (younger is better for kids)
        if age <= 30:
            score += 3.0
        elif age <= 40:
            score += 2.0
        elif age <= 50:
            score += 1.0
        
        # Description keywords for kid-friendly voices
        positive_keywords = [
            "warm", "friendly", "cheerful", "gentle", "soft", "pleasant",
            "engaging", "enthusiastic", "lively", "vibrant", "clear",
            "expressive", "dynamic", "captivating"
        ]
        
        negative_keywords = [
            "serious", "monotone", "deep", "grave", "stern", "harsh",
            "rough", "intimidating", "authoritative", "formal"
        ]
        
        for keyword in positive_keywords:
            if keyword in description:
                score += 1.0
        
        for keyword in negative_keywords:
            if keyword in description:
                score -= 1.0
        
        return max(0.0, score)

    async def setup_voice_mappings(self):
        """Setup personality-to-voice mappings"""
        try:
            # Get cached voices sorted by suitability
            voices = await self.voices_collection.find(
                {"gender": 2}  # Female voices
            ).sort("suitability_score", -1).to_list(length=None)
            
            if not voices:
                logger.warning("⚠️ No voices available for mapping")
                return
            
            # Map personalities to best voices
            english_voices = [v for v in voices if v.get("language") == 1]  # English
            hindi_voices = [v for v in voices if v.get("language") == 2]  # Hindi
            
            # If no Hindi voices, use English voices
            if not hindi_voices:
                hindi_voices = english_voices
            
            # Setup mappings
            for personality in ["friendly_companion", "story_narrator", "learning_buddy"]:
                self.personality_voice_map[personality] = {}
                
                # English mapping
                if english_voices:
                    if personality == "friendly_companion":
                        # Look for warm, friendly voices
                        suitable_voice = self._find_voice_by_traits(english_voices, ["warm", "friendly", "cheerful"])
                    elif personality == "story_narrator":
                        # Look for gentle, narrative voices
                        suitable_voice = self._find_voice_by_traits(english_voices, ["gentle", "soft", "captivating"])
                    else:  # learning_buddy
                        # Look for energetic, clear voices
                        suitable_voice = self._find_voice_by_traits(english_voices, ["energetic", "lively", "clear"])
                    
                    self.personality_voice_map[personality]["en"] = suitable_voice or english_voices[0]
                
                # Hindi mapping (same logic)
                if hindi_voices:
                    if personality == "friendly_companion":
                        suitable_voice = self._find_voice_by_traits(hindi_voices, ["warm", "friendly", "cheerful"])
                    elif personality == "story_narrator":
                        suitable_voice = self._find_voice_by_traits(hindi_voices, ["gentle", "soft", "captivating"])
                    else:
                        suitable_voice = self._find_voice_by_traits(hindi_voices, ["energetic", "lively", "clear"])
                    
                    self.personality_voice_map[personality]["hi"] = suitable_voice or hindi_voices[0]
            
            # Set fallback voices
            if english_voices:
                self.fallback_voices["english_female"] = english_voices[0]
            if hindi_voices:
                self.fallback_voices["hindi_female"] = hindi_voices[0]
            
            logger.info("✅ Voice mappings configured successfully")
            
            # Log mappings for debugging
            for personality, mapping in self.personality_voice_map.items():
                for lang, voice in mapping.items():
                    if voice:
                        logger.info(f"🎵 {personality} ({lang}): {voice['voice_name']} (ID: {voice['id']})")
            
        except Exception as e:
            logger.error(f"❌ Error setting up voice mappings: {str(e)}")

    def _find_voice_by_traits(self, voices: List[Dict], preferred_traits: List[str]) -> Optional[Dict]:
        """Find voice that matches preferred traits"""
        for voice in voices:
            description = voice.get("description", "").lower()
            if any(trait in description for trait in preferred_traits):
                return voice
        return None

    async def setup_fallback_voices(self):
        """Setup fallback voices when Camb.ai is not available"""
        fallback_voice = {
            "id": 99999,
            "voice_name": "Fallback Female",
            "gender": 2,
            "age": 25,
            "language": 1,
            "description": "Fallback voice for when Camb.ai is unavailable",
            "is_published": True,
            "suitability_score": 1.0
        }
        
        # Use fallback for all mappings
        for personality in ["friendly_companion", "story_narrator", "learning_buddy"]:
            self.personality_voice_map[personality] = {
                "en": fallback_voice,
                "hi": fallback_voice
            }
        
        self.fallback_voices["english_female"] = fallback_voice
        self.fallback_voices["hindi_female"] = fallback_voice
        
        logger.info("✅ Fallback voices configured")

    async def get_voice_for_personality(self, personality: str = "friendly_companion", language: str = "en") -> Dict:
        """Get appropriate voice for personality and language"""
        try:
            # Get from mapping
            if personality in self.personality_voice_map:
                voice = self.personality_voice_map[personality].get(language)
                if voice:
                    return voice
            
            # Fallback to any suitable voice
            fallback_key = f"{language}_female" if language in ["en", "hi"] else "english_female"
            fallback_voice = self.fallback_voices.get(fallback_key)
            
            if fallback_voice:
                return fallback_voice
            
            # Final fallback
            return {
                "id": 99999,
                "voice_name": "Default",
                "gender": 2,
                "age": 25,
                "language": 1,
                "description": "Default fallback voice"
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting voice: {str(e)}")
            return {"id": 99999, "voice_name": "Error Fallback"}

    def _enhance_text_with_ssml(self, text: str, personality: str) -> str:
        """Add SSML and natural expressions to text"""
        if not text.strip():
            return text
        
        template = self.ssml_templates.get(personality, self.ssml_templates["friendly_companion"])
        
        # Add natural pauses
        enhanced_text = text.replace(". ", "... ")
        enhanced_text = enhanced_text.replace("! ", "!... ")
        enhanced_text = enhanced_text.replace("? ", "?... ")
        
        # Add occasional fillers (10% chance)
        import random
        if random.random() < 0.1:
            filler = random.choice(template["fillers"])
            words = enhanced_text.split()
            if len(words) > 5:
                insert_pos = len(words) // 2
                words.insert(insert_pos, f"{filler},")
                enhanced_text = " ".join(words)
        
        # Add occasional expressions (5% chance)
        if random.random() < 0.05:
            expression = random.choice(template["expressions"])
            enhanced_text = f"{expression} {enhanced_text}"
        
        return enhanced_text

    async def generate_tts(self, text: str, personality: str = "friendly_companion", language: str = "en") -> Optional[bytes]:
        """Generate TTS using Camb.ai with proper voice selection"""
        try:
            start_time = time.time()
            logger.info(f"🎵 CAMB.AI TTS: Generating audio for '{text[:50]}...' ({personality}, {language})")
            
            # Get appropriate voice
            voice = await self.get_voice_for_personality(personality, language)
            voice_id = voice.get("id")
            
            if voice_id == 99999:  # Fallback voice
                logger.warning("⚠️ Using fallback voice, Camb.ai may not be working properly")
                return None
            
            logger.info(f"🎵 Selected voice: {voice.get('voice_name')} (ID: {voice_id})")
            
            # Enhance text with SSML and natural expressions
            enhanced_text = self._enhance_text_with_ssml(text, personality)
            
            # Submit TTS task
            task_id = await self._submit_tts_task(enhanced_text, voice_id, language)
            if not task_id:
                return None
            
            # Poll for completion
            run_id = await self._poll_task_status(task_id)
            if not run_id:
                return None
            
            # Retrieve audio
            audio_data = await self._retrieve_audio(run_id)
            
            processing_time = time.time() - start_time
            if audio_data:
                logger.info(f"✅ CAMB.AI TTS successful: {len(audio_data)} bytes in {processing_time:.2f}s")
                return audio_data
            else:
                logger.error("❌ CAMB.AI TTS failed: No audio data received")
                return None
            
        except Exception as e:
            logger.error(f"❌ CAMB.AI TTS error: {str(e)}")
            return None

    async def _submit_tts_task(self, text: str, voice_id: int, language: str) -> Optional[str]:
        """Submit TTS task to Camb.ai"""
        try:
            language_id = 1 if language == "en" else 2  # English=1, Hindi=2
            
            payload = {
                "text": text,
                "voice_id": voice_id,
                "language": language_id
            }
            
            response = await self.http_client.post(
                f"{self.base_url}/tts",
                json=payload,
                headers=self.headers
            )
            
            if response.status_code == 200:
                result = response.json()
                task_id = result.get("task_id")
                logger.info(f"🎵 TTS task submitted: {task_id}")
                return task_id
            else:
                logger.error(f"❌ TTS submission failed: {response.status_code} - {response.text}")
                return None
            
        except Exception as e:
            logger.error(f"❌ Error submitting TTS task: {str(e)}")
            return None

    async def _poll_task_status(self, task_id: str, max_attempts: int = 15) -> Optional[str]:
        """Poll task status until completion"""
        attempt = 0
        delay = 1.0
        
        while attempt < max_attempts:
            try:
                response = await self.http_client.get(
                    f"{self.base_url}/tts/{task_id}",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    result = response.json()
                    status = result.get("status")
                    
                    if status == "SUCCESS":
                        return result.get("run_id")
                    elif status in ["FAILED", "TIMEOUT", "PAYMENT_REQUIRED"]:
                        logger.error(f"❌ TTS task {status}: {result.get('error_message', '')}")
                        return None
                    
                    # Continue polling
                    await asyncio.sleep(delay)
                    delay = min(delay * 1.1, 3.0)  # Increase delay gradually
                    attempt += 1
                else:
                    logger.error(f"❌ Polling failed: {response.status_code}")
                    return None
                
            except Exception as e:
                logger.error(f"❌ Polling error: {str(e)}")
                attempt += 1
                await asyncio.sleep(delay)
        
        logger.error(f"❌ Task {task_id} timeout after {max_attempts} attempts")
        return None

    async def _retrieve_audio(self, run_id: str) -> Optional[bytes]:
        """Retrieve generated audio"""
        try:
            response = await self.http_client.get(
                f"{self.base_url}/tts-result/{run_id}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.content
            else:
                logger.error(f"❌ Audio retrieval failed: {response.status_code} - {response.text}")
                return None
            
        except Exception as e:
            logger.error(f"❌ Error retrieving audio: {str(e)}")
            return None

    async def close(self):
        """Close HTTP client"""
        await self.http_client.aclose()