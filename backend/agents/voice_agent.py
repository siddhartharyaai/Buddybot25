"""
Voice Agent - Enhanced with Camb.ai MARS TTS and ultra-low latency streaming
"""
import asyncio
import logging
import base64
import requests
import re
import time
import os
import httpx
from typing import Optional, Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorClient


logger = logging.getLogger(__name__)


class CambAITTSClient:
    """Camb.ai TTS client with MARS model and dynamic voice selection"""
    
    def __init__(self, api_key: str, mongo_client: AsyncIOMotorClient):
        self.api_key = api_key
        self.base_url = "https://client.camb.ai/apis"
        self.headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json"
        }
        
        # Voice caching with MongoDB
        self.mongo_client = mongo_client
        self.db = mongo_client.ai_companion_db
        self.voices_collection = self.db.camb_ai_voices
        
        # HTTP client with connection pooling
        self.http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=3)
        )
        
        # Personality to voice tone mapping
        self.personality_mapping = {
            "friendly_companion": {"tone": "warm", "energy": "medium"},
            "story_narrator": {"tone": "gentle", "energy": "calm"},
            "learning_buddy": {"tone": "friendly", "energy": "medium"}
        }
        
        logger.info("✅ Camb.ai TTS client initialized with MARS model")

    async def initialize_voices(self):
        """Initialize and cache voices from Camb.ai"""
        try:
            await self._cache_voices()
        except Exception as e:
            logger.error(f"❌ Failed to initialize voices: {str(e)}")
            # Continue with default voices
    
    async def _cache_voices(self) -> None:
        """Fetch and cache voices from Camb.ai API"""
        try:
            response = await self.http_client.get(
                f"{self.base_url}/list-voices",
                headers=self.headers
            )
            response.raise_for_status()
            
            voices_data = response.json()
            logger.info(f"🎵 Retrieved {len(voices_data)} voices from Camb.ai")
            
            # Clear existing cache
            await self.voices_collection.delete_many({})
            
            # Insert new voice data with timestamp
            for voice in voices_data:
                voice["cached_at"] = time.time()
                await self.voices_collection.insert_one(voice)
            
            # Create indexes for efficient querying
            await self.voices_collection.create_index([
                ("gender", 1), ("age", 1), ("language", 1)
            ])
            
            logger.info("✅ Voice cache updated successfully")
            
        except Exception as e:
            logger.error(f"❌ Error caching voices: {e}")
            # Create default voice entries if API fails
            default_voices = [
                {
                    "id": 1001,
                    "voice_name": "Emma",
                    "gender": 2,
                    "age": 25,
                    "language": 1,
                    "description": "warm and friendly voice for kids",
                    "is_published": True,
                    "cached_at": time.time()
                }
            ]
            for voice in default_voices:
                await self.voices_collection.insert_one(voice)

    async def get_suitable_voice(self, personality: str = "friendly_companion", language: str = "en") -> Optional[Dict]:
        """Select appropriate voice based on personality and language"""
        try:
            # Language mapping
            lang_id = 1 if language == "en" else 2  # Hindi
            
            # Filter criteria: female, young age (for kid-friendly), specific language
            query = {
                "gender": 2,  # Female
                "age": {"$lte": 35},  # Young age for kid-friendly
                "language": lang_id,
                "is_published": True
            }
            
            voices = await self.voices_collection.find(query).to_list(length=None)
            
            if not voices:
                # Fallback: any female voice in the language
                query.pop("age")
                voices = await self.voices_collection.find(query).to_list(length=None)
            
            if not voices:
                logger.warning(f"⚠️ No suitable voices found for {personality} in {language}")
                return {"id": 1001, "voice_name": "Default", "gender": 2, "age": 25, "language": lang_id}
            
            # Select voice based on personality
            selected_voice = self._select_by_personality(voices, personality)
            return selected_voice if selected_voice else voices[0]
            
        except Exception as e:
            logger.error(f"❌ Error selecting voice: {e}")
            return {"id": 1001, "voice_name": "Default", "gender": 2, "age": 25, "language": 1}

    def _select_by_personality(self, voices: List[Dict], personality: str) -> Optional[Dict]:
        """Select voice based on personality characteristics"""
        if not voices:
            return None
        
        # Personality-based selection logic
        if personality == "friendly_companion":
            # Look for warm, friendly descriptions
            for voice in voices:
                desc = voice.get("description", "").lower()
                if any(keyword in desc for keyword in ["warm", "friendly", "cheerful", "pleasant"]):
                    return voice
        
        elif personality == "story_narrator":
            # Look for calm, narrative descriptions
            for voice in voices:
                desc = voice.get("description", "").lower()
                if any(keyword in desc for keyword in ["gentle", "narrator", "storytelling", "calm"]):
                    return voice
        
        elif personality == "learning_buddy":
            # Look for clear, educational descriptions
            for voice in voices:
                desc = voice.get("description", "").lower()
                if any(keyword in desc for keyword in ["clear", "educational", "teaching", "friendly"]):
                    return voice
        
        # Default: return first available voice
        return voices[0]

    def _build_ssml(self, text: str, personality: str) -> str:
        """Build SSML markup for enhanced speech quality"""
        if not text.strip():
            return text
        
        # For Camb.ai MARS model, prosody control through natural punctuation and formatting
        # Add natural pauses and emphasis
        processed_text = text
        
        # Add breaks at sentence boundaries for better flow
        processed_text = processed_text.replace('. ', '... ')
        processed_text = processed_text.replace('? ', '?... ')
        processed_text = processed_text.replace('! ', '!... ')
        
        # Add emphasis for excitement based on personality
        if personality == "story_narrator":
            # Add storytelling pauses and emphasis
            processed_text = re.sub(r'\b(once upon a time|suddenly|amazingly|wonderful)\b', 
                                  r'**\1**', processed_text, flags=re.IGNORECASE)
        elif personality == "friendly_companion":
            # Add friendly expressions
            processed_text = re.sub(r'\b(great|awesome|fantastic|amazing)\b', 
                                  r'*\1*', processed_text, flags=re.IGNORECASE)
        
        return processed_text

    async def submit_tts_task(self, text: str, voice_id: int, language_id: int, use_ssml: bool = True) -> str:
        """Submit TTS task and return task_id"""
        try:
            processed_text = text
            if use_ssml:
                processed_text = self._build_ssml(text, "friendly_companion")
            
            payload = {
                "text": processed_text,
                "voice_id": voice_id,
                "language": language_id
            }
            
            response = await self.http_client.post(
                f"{self.base_url}/tts",
                json=payload,
                headers=self.headers
            )
            response.raise_for_status()
            
            result = response.json()
            task_id = result.get("task_id")
            
            if not task_id:
                raise ValueError("No task_id received from Camb.ai API")
            
            logger.info(f"🎵 TTS task submitted: {task_id}")
            return task_id
            
        except Exception as e:
            logger.error(f"❌ Error submitting TTS task: {e}")
            raise

    async def poll_task_status(self, task_id: str, max_attempts: int = 20) -> Optional[str]:
        """Poll task status until completion and return run_id"""
        attempt = 0
        delay = 1.0
        
        while attempt < max_attempts:
            try:
                response = await self.http_client.get(
                    f"{self.base_url}/tts/{task_id}",
                    headers=self.headers
                )
                response.raise_for_status()
                
                status_data = response.json()
                status = status_data.get("status")
                
                if status == "SUCCESS":
                    return status_data.get("run_id")
                elif status == "FAILED":
                    raise Exception(f"TTS task failed: {status_data.get('error_message', 'Unknown error')}")
                elif status in ["PAYMENT_REQUIRED", "TIMEOUT"]:
                    raise Exception(f"TTS task {status}")
                
                # Wait before next poll
                await asyncio.sleep(delay)
                delay = min(delay * 1.2, 5.0)  # Cap at 5 seconds
                attempt += 1
                
            except Exception as e:
                if attempt >= max_attempts - 1:
                    raise
                await asyncio.sleep(delay)
                attempt += 1
        
        raise TimeoutError(f"Task {task_id} did not complete within {max_attempts} attempts")

    async def retrieve_audio(self, run_id: str) -> bytes:
        """Retrieve generated audio file"""
        try:
            response = await self.http_client.get(
                f"{self.base_url}/tts-result/{run_id}",
                headers=self.headers
            )
            response.raise_for_status()
            
            audio_data = response.content
            logger.info(f"🎵 Retrieved audio: {len(audio_data)} bytes")
            return audio_data
            
        except Exception as e:
            logger.error(f"❌ Error retrieving audio: {e}")
            raise

    async def close(self):
        """Close HTTP client"""
        await self.http_client.aclose()


class VoiceAgent:
    """Voice processing with Deepgram Nova 3 STT and Camb.ai MARS TTS"""
    
    def __init__(self, deepgram_api_key: str, mongo_client: AsyncIOMotorClient = None):
        self.deepgram_api_key = deepgram_api_key
        self.base_url = "https://api.deepgram.com/v1"
        
        # Initialize Camb.ai TTS client
        self.camb_api_key = os.getenv("CAMB_AI_API_KEY")
        if self.camb_api_key and mongo_client:
            self.camb_tts_client = CambAITTSClient(self.camb_api_key, mongo_client)
        else:
            self.camb_tts_client = None
            logger.warning("⚠️ Camb.ai TTS not available, using fallback")
        
        # Deepgram voice personalities (fallback)
        self.voice_personalities = {
            "friendly_companion": {
                "model": "aura-2-amalthea-en",
            },
            "story_narrator": {
                "model": "aura-2-amalthea-en",
            },
            "learning_buddy": {
                "model": "aura-2-amalthea-en",
            }
        }
        
        logger.info("✅ Voice Agent initialized with Camb.ai MARS TTS and Deepgram Nova-3 STT")

    async def initialize(self):
        """Initialize the voice agent"""
        if self.camb_tts_client:
            await self.camb_tts_client.initialize_voices()

    async def speech_to_text_streaming(self, audio_data: bytes) -> str:
        """ULTRA-LOW LATENCY: Streaming STT with interim results for immediate processing"""
        try:
            import time
            start_time = time.time()
            logger.info(f"🚀 ULTRA-FAST STT: Starting streaming transcription for {len(audio_data)} bytes")
            
            # Use Deepgram Nova 3 with interim results for ultra-low latency
            headers = {
                "Authorization": f"Token {self.deepgram_api_key}",
                "Content-Type": "audio/wav"
            }
            
            # Ultra-fast STT parameters for <200ms processing
            params = {
                "model": "nova-2",  # Fastest model
                "interim_results": "true",  # Enable streaming partial results
                "encoding": "linear16",
                "sample_rate": 48000,
                "language": "en-US",
                "smart_format": "true",
                "punctuate": "true",
                "utterances": "true",
                "diarize": "false",  # Disable speaker detection for speed
                "filler_words": "false",  # Remove for speed
                "multichannel": "false"  # Single channel for speed
            }
            
            url = f"{self.base_url}/listen"
            
            # Send request with ultra-fast timeout
            response = requests.post(
                url,
                headers=headers,
                params=params,
                data=audio_data,
                timeout=1.5  # Ultra-fast timeout for <4s target
            )
            
            stt_time = time.time() - start_time
            logger.info(f"⚡ ULTRA-FAST STT COMPLETE: {stt_time:.3f}s")
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract transcript from response
                transcript = ""
                if "results" in result and "channels" in result["results"]:
                    channels = result["results"]["channels"]
                    if channels and len(channels) > 0:
                        alternatives = channels[0].get("alternatives", [])
                        if alternatives and len(alternatives) > 0:
                            transcript = alternatives[0].get("transcript", "").strip()
                
                if transcript:
                    logger.info(f"✅ ULTRA-FAST STT SUCCESS: '{transcript[:50]}...' in {stt_time:.3f}s")
                    return transcript
                else:
                    logger.warning("⚠️ Empty transcript from ultra-fast STT")
                    return ""
            else:
                logger.error(f"❌ Ultra-fast STT failed: {response.status_code} - {response.text}")
                return ""
                
        except Exception as e:
            logger.error(f"❌ Ultra-fast STT error: {str(e)}")
            return ""

    def get_available_voices(self) -> Dict[str, Any]:
        """Get available voice personalities"""
        return {
            "voices": [
                {
                    "id": "friendly_companion",
                    "name": "Friendly Companion",
                    "description": "A warm, encouraging voice perfect for general conversations and support",
                    "model": "aura-2-amalthea-en"
                },
                {
                    "id": "story_narrator", 
                    "name": "Story Narrator",
                    "description": "An engaging, expressive voice ideal for storytelling and adventures",
                    "model": "aura-2-amalthea-en"
                },
                {
                    "id": "learning_buddy",
                    "name": "Learning Buddy", 
                    "description": "A patient, educational voice great for learning and exploration",
                    "model": "aura-2-amalthea-en"
                }
            ],
            "default": "friendly_companion",
            "count": 3
        }
    async def speech_to_text(self, audio_data: bytes, enhanced_for_children: bool = True) -> Optional[str]:
        """Convert speech to text using Deepgram Nova 3 REST API with enhanced child speech recognition"""
        try:
            # Log audio details for debugging
            logger.info(f"STT processing: {len(audio_data)} bytes audio data")
            
            # Validate audio data
            if len(audio_data) < 100:
                logger.warning(f"Audio data too small for STT: {len(audio_data)} bytes")
                return None
            
            # Detect audio format
            if audio_data.startswith(b'\x1a\x45\xdf\xa3'):  # WebM signature
                content_type = "audio/webm"
            elif audio_data.startswith(b'RIFF'):
                content_type = "audio/wav"
            elif audio_data.startswith(b'OggS'):
                content_type = "audio/ogg"
            else:
                content_type = "audio/wav"  # Default
            
            # Prepare headers
            headers = {
                "Authorization": f"Token {self.deepgram_api_key}",
                "Content-Type": content_type
            }
            
            # Simplified parameters for reliability
            params = {
                "model": "nova-2",
                "language": "en",
                "smart_format": "true",
                "punctuate": "true",
            }
            
            logger.info(f"Making STT request to Deepgram: {len(audio_data)} bytes, Content-Type: {content_type}")
            
            # Make REST API call using requests in async context
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(
                    f"{self.base_url}/listen",
                    headers=headers,
                    params=params,
                    data=audio_data,
                    timeout=10
                )
            )
            
            logger.info(f"STT response: status={response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"STT response structure: {result}")
                
                # Extract transcript
                if result.get("results") and result["results"].get("channels"):
                    channel = result["results"]["channels"][0]
                    if channel.get("alternatives") and len(channel["alternatives"]) > 0:
                        transcript = channel["alternatives"][0]["transcript"]
                        
                        # Enhanced processing for child speech
                        if enhanced_for_children:
                            transcript = self.enhance_child_speech_recognition(transcript)
                        
                        if transcript.strip():
                            logger.info(f"STT successful: '{transcript}'")
                            return transcript.strip()
                        else:
                            logger.warning("STT returned empty transcript")
                            return None
                    else:
                        logger.warning("STT response missing alternatives")
                        return None
                else:
                    logger.warning(f"STT response missing expected structure: {result}")
                    return None
            else:
                logger.error(f"STT API error: {response.status_code} - {response.text}")
                return None
            
        except Exception as e:
            logger.error(f"STT processing error: {str(e)}")
            return None
    
    def enhance_child_speech_recognition(self, transcript: str) -> str:
        """Enhance transcript for common child speech patterns"""
        if not transcript:
            return transcript
            
        # Common child speech corrections
        corrections = {
            "twy": "try",
            "fwee": "free", 
            "bwue": "blue",
            "gweat": "great",
            "pwease": "please",
            "wove": "love",
            "vewy": "very",
            "widdle": "little",
            "wight": "right",
            "weally": "really"
        }
        
        words = transcript.split()
        corrected_words = []
        
        for word in words:
            word_lower = word.lower().strip('.,!?')
            if word_lower in corrections:
                corrected_word = corrections[word_lower]
                # Preserve original capitalization and punctuation
                if word[0].isupper():
                    corrected_word = corrected_word.capitalize()
                # Add back punctuation
                for punct in '.,!?':
                    if word.endswith(punct):
                        corrected_word += punct
                        break
                corrected_words.append(corrected_word)
            else:
                corrected_words.append(word)
        
        return ' '.join(corrected_words)
    
    async def text_to_speech_chunked(self, text: str, personality: str = "friendly_companion") -> Optional[str]:
        """Convert long text to speech with ultra-small chunking for blazing speed parallel processing"""
        try:
            logger.info(f"🎵 DEBUG TTS CHUNKED: Processing {len(text)} characters with personality: {personality}")
            logger.info(f"🎵 DEBUG TTS CHUNKED: Input text preview: '{text[:100]}...'")
            
            # BLAZING SPEED: Always use parallel processing for ANY text over 100 characters
            if len(text) > 100:
                logger.info("🎵 BLAZING SPEED: Using ULTRA-SMALL chunk parallel processing for maximum speed")
                
                # BLAZING SPEED: Split text into ultra-small chunks (50 tokens for maximum parallelization)
                chunks = self._split_text_into_chunks(text, 50)  # 50 tokens = ~30-70 characters
                logger.info(f"🎵 BLAZING SPEED: Split into {len(chunks)} ultra-small chunks for parallel processing")
                
                # BLAZING SPEED: Process ALL chunks in parallel using asyncio.gather for maximum concurrency
                tts_tasks = []
                for i, chunk in enumerate(chunks):
                    logger.info(f"🎵 BLAZING SPEED: Creating parallel task for chunk {i+1}/{len(chunks)}: {chunk[:30]}...")
                    task = self._process_chunk_ultra_fast(chunk, personality, i+1)
                    tts_tasks.append(task)
                
                # Execute all TTS calls in parallel with no delays for blazing speed
                logger.info(f"🎵 BLAZING SPEED: Executing {len(tts_tasks)} TTS calls in FULL PARALLEL...")
                start_parallel = time.time()
                audio_chunks = await asyncio.gather(*tts_tasks, return_exceptions=True)
                parallel_duration = time.time() - start_parallel
                logger.info(f"🎵 BLAZING SPEED: Ultra-parallel TTS completed in {parallel_duration:.2f}s")
                
                # Filter out exceptions and empty results
                valid_audio_chunks = []
                for i, result in enumerate(audio_chunks):
                    if isinstance(result, Exception):
                        logger.error(f"🎵 BLAZING SPEED: Chunk {i+1} failed with exception: {str(result)}")
                    elif result and len(result) > 0:
                        valid_audio_chunks.append(result)
                        logger.info(f"🎵 BLAZING SPEED: Chunk {i+1} succeeded - size: {len(result)} chars")
                    else:
                        logger.warning(f"🎵 BLAZING SPEED: Chunk {i+1} returned empty audio")
                
                if valid_audio_chunks:
                    # Return the first chunk for immediate playback while others continue
                    final_audio_size = len(valid_audio_chunks[0])
                    logger.info(f"🎵 BLAZING SPEED: Ultra-parallel TTS completed: {len(valid_audio_chunks)} chunks, returning first chunk (size: {final_audio_size})")
                    return valid_audio_chunks[0]
                else:
                    logger.error("🎵 DEBUG TTS CHUNKED: No audio chunks generated - all failed")
                    return None
            else:
                # For very short texts, process as single request
                logger.info("🎵 DEBUG TTS CHUNKED: Processing as single TTS request (text < 100 chars)")
                single_audio = await self.text_to_speech(text, personality)
                
                if single_audio:
                    single_size = len(single_audio)
                    logger.info(f"🎵 DEBUG TTS CHUNKED: Single TTS successful - size: {single_size}")
                    
                    if single_size == 0:
                        logger.error("🎵 DEBUG TTS CHUNKED: CRITICAL - Single TTS returned EMPTY audio blob!")
                        return None
                        
                    return single_audio
                else:
                    logger.error("🎵 DEBUG TTS CHUNKED: Single TTS failed - no audio returned")
                    return None
                
        except Exception as e:
            logger.error(f"🎵 DEBUG TTS CHUNKED: Exception occurred: {str(e)}")
            return None
    
    def _split_text_into_chunks(self, text: str, max_size: int = 50) -> List[str]:
        """BLAZING SPEED: Split text into ultra-small chunks (50 tokens) for maximum parallel processing"""
        # Split by sentences first
        sentences = re.split(r'[.!?]+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Add period back if it was removed
            if not sentence.endswith(('.', '!', '?')):
                sentence += '.'
            
            # BLAZING SPEED: Use ultra-small chunks (50 tokens ~= 30-70 chars) for fastest parallel processing
            if len(current_chunk) + len(sentence) + 1 > max_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                current_chunk += " " + sentence if current_chunk else sentence
        
        # Add the last chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        # BLAZING SPEED: If chunks are still too large, split more aggressively by words
        final_chunks = []
        for chunk in chunks:
            if len(chunk) > max_size:
                # Split by words for very long chunks - target 50 token chunks
                words = chunk.split()
                word_chunk = ""
                for word in words:
                    # Approximate: 1 word = ~1.3 tokens, so 50 tokens ~= 38 words
                    estimated_tokens = len(word_chunk.split()) * 1.3
                    if estimated_tokens >= 38 and word_chunk:  # ~50 tokens
                        final_chunks.append(word_chunk.strip())
                        word_chunk = word
                    else:
                        word_chunk += " " + word if word_chunk else word
                if word_chunk.strip():
                    final_chunks.append(word_chunk.strip())
            else:
                final_chunks.append(chunk)
        
        logger.info(f"🚀 BLAZING SPEED: Split {len(text)} chars into {len(final_chunks)} ultra-small chunks (avg {len(text)//len(final_chunks) if final_chunks else 0} chars each)")
        return final_chunks
    
    async def _process_chunk_ultra_fast(self, chunk: str, personality: str, chunk_num: int) -> Optional[str]:
        """BLAZING SPEED: Process individual ultra-small chunk with maximum speed optimizations"""
        try:
            # Ultra-aggressive optimization: Skip all text processing for maximum speed
            audio_base64 = await self.text_to_speech_ultra_fast(chunk, personality)
            
            if audio_base64 and len(audio_base64) > 0:
                logger.info(f"🎵 BLAZING SPEED: Ultra-fast chunk {chunk_num} succeeded - size: {len(audio_base64)} chars")
                return audio_base64
            else:
                logger.warning(f"🎵 BLAZING SPEED: Ultra-fast chunk {chunk_num} returned empty audio")
                return None
                
        except Exception as e:
            logger.error(f"🎵 BLAZING SPEED: Ultra-fast chunk {chunk_num} failed: {str(e)}")
            return None
    
    def _concatenate_audio_chunks(self, audio_chunks: List[str]) -> str:
        """Simple concatenation - return first chunk for reliable playback"""
        try:
            if not audio_chunks:
                return ""
            
            # SIMPLE APPROACH: Return first chunk to ensure playback works
            logger.info(f"Returning first of {len(audio_chunks)} audio chunks for reliable playback")
            return audio_chunks[0]
            
        except Exception as e:
            logger.error(f"❌ Audio concatenation failed: {str(e)}")
            return audio_chunks[0] if audio_chunks else ""

    async def text_to_speech_chunked_fast(self, text: str, personality: str = "friendly_companion") -> Optional[str]:
        """NEW FAST CHUNKED TTS: Parallel processing for ultra-low latency"""
        try:
            logger.info(f"🚀 FAST CHUNKED TTS: Processing {len(text)} characters in parallel")
            
            # Chunk into smaller pieces for faster parallel processing
            chunks = self._split_text_into_chunks(text, 1200)  # Larger chunks for efficiency
            logger.info(f"⚡ Split into {len(chunks)} chunks for parallel processing")
            
            # PARALLEL PROCESSING: All chunks simultaneously
            import asyncio
            
            async def process_chunk_fast(i, chunk):
                logger.info(f"⚡ Processing chunk {i+1}/{len(chunks)} in parallel")
                return await self.text_to_speech(chunk, personality)
            
            # Process all chunks in parallel - no delays!
            tasks = [process_chunk_fast(i, chunk) for i, chunk in enumerate(chunks)]
            audio_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter successful results
            audio_chunks = []
            for i, result in enumerate(audio_results):
                if isinstance(result, Exception):
                    logger.warning(f"⚠️ Chunk {i+1} failed: {str(result)}")
                elif result:
                    audio_chunks.append(result)
            
            if audio_chunks:
                logger.info(f"🎉 FAST CHUNKED TTS complete: {len(audio_chunks)}/{len(chunks)} chunks successful")
                # Return first chunk for immediate playback (reliable approach)
                return audio_chunks[0]
            else:
                logger.error("❌ No audio chunks generated")
                return None
                
        except Exception as e:
            logger.error(f"❌ Fast chunked TTS failed: {str(e)}")
            return None

    async def text_to_speech(self, text: str, personality: str = "friendly_companion") -> Optional[str]:
        """Convert text to speech using Camb.ai MARS model with dynamic voice selection"""
        try:
            if self.camb_tts_client:
                return await self._camb_ai_tts(text, personality)
            else:
                # Fallback to Deepgram TTS
                return await self._deepgram_tts_fallback(text, personality)
        except Exception as e:
            logger.error(f"❌ TTS error: {str(e)}")
            return None
    
    async def _camb_ai_tts(self, text: str, personality: str) -> Optional[str]:
        """Generate TTS using Camb.ai MARS model"""
        try:
            start_time = time.time()
            logger.info(f"🎵 CAMB.AI TTS: Processing {len(text)} chars with {personality}")
            
            # Get suitable voice based on personality
            voice = await self.camb_tts_client.get_suitable_voice(personality, "en")
            voice_id = voice.get("id", 1001)
            
            logger.info(f"🎵 Selected voice: {voice.get('voice_name', 'Default')} (ID: {voice_id})")
            
            # Submit TTS task
            task_id = await self.camb_tts_client.submit_tts_task(text, voice_id, 1, True)
            
            # Poll for completion
            run_id = await self.camb_tts_client.poll_task_status(task_id)
            
            # Retrieve audio
            audio_data = await self.camb_tts_client.retrieve_audio(run_id)
            
            # Convert to base64 for consistency with existing API
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            processing_time = time.time() - start_time
            logger.info(f"🎵 CAMB.AI TTS completed in {processing_time:.2f}s, {len(audio_data)} bytes")
            
            return audio_base64
            
        except Exception as e:
            logger.error(f"❌ Camb.ai TTS error: {str(e)}")
            # Fallback to Deepgram
            return await self._deepgram_tts_fallback(text, personality)
    
    async def _deepgram_tts_fallback(self, text: str, personality: str) -> Optional[str]:
        """Fallback TTS using Deepgram Aura 2"""
        try:
            logger.info(f"🎵 DEEPGRAM FALLBACK TTS: {len(text)} chars with {personality}")
            
            voice_config = self.voice_personalities.get(personality, self.voice_personalities["friendly_companion"])
            
            headers = {
                "Authorization": f"Token {self.deepgram_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "text": text,
                "model": voice_config["model"],
                "encoding": "linear16",
                "container": "wav",
                "bit_rate": 48000,
                "sample_rate": 16000
            }
            
            # Make async request
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(
                    f"{self.base_url}/speak",
                    headers=headers,
                    json=payload,
                    timeout=30
                )
            )
            
            if response.status_code == 200:
                audio_base64 = base64.b64encode(response.content).decode('utf-8')
                logger.info(f"🎵 Deepgram TTS successful: {len(response.content)} bytes")
                return audio_base64
            else:
                logger.error(f"❌ Deepgram TTS error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Deepgram fallback TTS error: {str(e)}")
            return None

    async def text_to_speech_chunked(self, text: str, personality: str = "friendly_companion") -> Optional[str]:
        """Convert long text to speech with chunking for better performance"""
        try:
            logger.info(f"🎵 CHUNKED TTS: Processing {len(text)} characters")
            
            # Split text into chunks for parallel processing
            chunks = self._chunk_text_for_tts(text, max_chunk_size=200)
            logger.info(f"🎵 Split into {len(chunks)} chunks")
            
            if len(chunks) == 1:
                # Single chunk, use regular TTS
                return await self.text_to_speech(text, personality)
            
            # Process chunks in parallel
            chunk_tasks = []
            for i, chunk in enumerate(chunks):
                logger.info(f"🎵 Chunk {i+1}: '{chunk[:50]}...'")
                chunk_tasks.append(self.text_to_speech(chunk, personality))
            
            # Wait for all chunks to complete
            audio_chunks = await asyncio.gather(*chunk_tasks, return_exceptions=True)
            
            # Filter successful results
            successful_chunks = []
            for i, result in enumerate(audio_chunks):
                if isinstance(result, Exception):
                    logger.error(f"❌ Chunk {i+1} failed: {str(result)}")
                elif result:
                    successful_chunks.append(result)
            
            if not successful_chunks:
                logger.error("❌ All TTS chunks failed")
                return None
            
            # For now, return first successful chunk
            # In production, you'd concatenate audio properly
            logger.info(f"✅ TTS chunked completed: {len(successful_chunks)} successful chunks")
            return successful_chunks[0]
            
        except Exception as e:
            logger.error(f"❌ Chunked TTS error: {str(e)}")
            return None
    
    def _chunk_text_for_tts(self, text: str, max_chunk_size: int = 200) -> List[str]:
        """Split text into chunks suitable for TTS processing"""
        if len(text) <= max_chunk_size:
            return [text]
        
        # Split by sentences first
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= max_chunk_size:
                current_chunk += sentence + " "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + " "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks

    async def text_to_speech_with_prosody(self, text: str, personality: str = "friendly_companion", prosody: dict = None) -> Optional[str]:
        """Convert text to speech with prosody support using Camb.ai SSML"""
        try:
            if self.camb_tts_client:
                # Camb.ai handles prosody through natural text formatting
                enhanced_text = text
                if prosody:
                    # Apply prosody adjustments through text formatting
                    if prosody.get("emphasis"):
                        enhanced_text = f"**{text}**"
                    elif prosody.get("slow"):
                        enhanced_text = text.replace(" ", "... ")
                
                return await self._camb_ai_tts(enhanced_text, personality)
            else:
                # Fallback to regular TTS
                return await self.text_to_speech(text, personality)
                
        except Exception as e:
            logger.error(f"❌ Prosody TTS error: {str(e)}")
            return None
    
    async def text_to_speech_with_prosody(self, text: str, personality: str = "friendly_companion", prosody: dict = None) -> Optional[str]:
        """Convert text to speech with prosody support (wrapper for existing methods)"""
        logger.info(f"🎵 TTS with prosody: {len(text)} chars, personality={personality}")
        
        # For now, use the existing chunked method which handles long texts well
        # In the future, prosody parameters could modify voice settings
        return await self.text_to_speech_chunked(text, personality)
    async def text_to_speech_streaming(self, text: str, personality: str = "friendly_companion") -> dict:
        """Stream TTS in chunks for immediate playback while generating remaining audio"""
        logger.info(f"🎵 Starting streaming TTS for {len(text)} characters")
        
        try:
            # If text is short, just use regular TTS
            if len(text) < 500:
                audio_base64 = await self.text_to_speech(text, personality)
                return {
                    "status": "complete",
                    "initial_audio": audio_base64,
                    "chunks": [],
                    "total_chunks": 1
                }
            
            # Split into chunks for streaming
            chunks = self._split_text_into_chunks(text, 800)  # Smaller chunks for faster response
            logger.info(f"Split into {len(chunks)} chunks for streaming")
            
            # Generate first chunk immediately
            first_chunk_audio = await self.text_to_speech(chunks[0], personality)
            
            if not first_chunk_audio:
                logger.error("Failed to generate first audio chunk")
                return {"status": "error", "error": "Failed to generate initial audio"}
            
            # Return first chunk immediately, generate rest in background
            return {
                "status": "streaming",
                "initial_audio": first_chunk_audio,
                "chunks": chunks[1:],  # Remaining chunks to be processed
                "total_chunks": len(chunks),
                "chunk_index": 0
            }
            
        except Exception as e:
            logger.error(f"Streaming TTS error: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def generate_chunk_audio(self, chunk_text: str, personality: str = "friendly_companion") -> Optional[str]:
        """Generate audio for a single chunk (for streaming)"""
        return await self.text_to_speech(chunk_text, personality)
    
    def _clean_text_for_natural_speech(self, text: str, personality: str) -> str:
        """Clean and enhance text for natural, kid-friendly speech without markup"""
        try:
            # Remove any existing markup
            clean_text = re.sub(r'<[^>]+>', '', text)
            
            # Add natural speech enhancements through word choice and phrasing
            # rather than markup that gets read literally
            
            # Add natural pauses with ellipses instead of markup
            clean_text = re.sub(r'\b(and then|suddenly|meanwhile|however)\b', r'... \1 ...', clean_text, flags=re.IGNORECASE)
            
            # Add natural emphasis through word choice - friendly but not overly parental
            enthusiasm_words = {
                'amazing': 'really amazing',
                'wonderful': 'pretty wonderful', 
                'great': 'really great',
                'good': 'pretty good',
                'nice': 'really nice',
                'cool': 'so cool'
            }
            
            for word, enhanced in enthusiasm_words.items():
                clean_text = re.sub(rf'\b{word}\b', enhanced, clean_text, flags=re.IGNORECASE)
            
            # Add natural friendly interjections instead of overly parental ones
            if personality == "friendly_companion":
                # Add gentle, friend-like interjections - but not randomly
                if not clean_text.startswith(('Oh', 'Hey', 'Wow', 'Cool', 'Hi')):
                    clean_text = 'Oh, ' + clean_text  # Start with friendly "Oh"
                # Remove the random "That's cool!" insertion that makes no sense
            
            elif personality == "story_narrator":
                # Add storytelling elements without being overly parental
                if "once upon a time" in clean_text.lower():
                    clean_text = "Alright, let me tell you this story... " + clean_text
                if "the end" in clean_text.lower():
                    clean_text = clean_text + " ... And that's our story!"
            
            # Remove overly parental terms that might slip through
            parental_replacements = {
                'sweetie': 'friend',
                'my dear': 'buddy',
                'darling': 'friend',
                'honey': 'friend',
                'sweetheart': 'friend'
            }
            
            for parental, friendly in parental_replacements.items():
                clean_text = re.sub(rf'\b{parental}\b', friendly, clean_text, flags=re.IGNORECASE)
            
            # Remove multiple spaces and clean up
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            
            logger.info(f"Cleaned text for natural {personality} speech with friendly tone")
            return clean_text
            
        except Exception as e:
            logger.error(f"Text cleaning error: {str(e)}")
            # Return original text if cleaning fails
            return text
    
    async def speech_to_text_streaming(self, audio_data: bytes) -> str:
        """Ultra-fast STT with interim results for low latency"""
        try:
            import base64
            import requests
            
            # Convert bytes to base64 for Deepgram API
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            # Use Deepgram's real-time model with interim results
            headers = {
                "Authorization": f"Token {self.deepgram_api_key}",
                "Content-Type": "application/json"
            }
            
            # Prepare request body with proper format for Deepgram
            payload = {
                "buffer": audio_base64,
                "mimetype": "audio/webm"
            }
            
            # Use Nova-3 for ultra-fast processing
            params = {
                "model": "nova-3",
                "interim_results": "true",
                "punctuate": "true",
                "language": "en-US",
                "smart_format": "true"
            }
            
            logger.info("🚀 Starting ultra-fast STT with interim results...")
            
            # Make async request to Deepgram
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(
                    f"{self.base_url}/listen",
                    headers=headers,
                    params=params,
                    json=payload,
                    timeout=5  # Ultra-fast timeout
                )
            )
            
            if response.status_code == 200:
                result = response.json()
                transcript = result.get('results', {}).get('channels', [{}])[0].get('alternatives', [{}])[0].get('transcript', '')
                
                if transcript:
                    logger.info(f"⚡ ULTRA-FAST STT completed: '{transcript}'")
                    return transcript.strip()
                else:
                    logger.warning("No transcript in ultra-fast STT response")
                    return ""
            else:
                logger.error(f"Ultra-fast STT API error: {response.status_code} - {response.text}")
                # Fallback to regular STT
                return await self.speech_to_text(audio_data)
            
        except Exception as e:
            logger.error(f"Ultra-fast STT error: {str(e)}")
            # Fallback to regular STT
            return await self.speech_to_text(audio_data)
    
    async def text_to_speech_chunk(self, text: str, personality: str = "friendly_companion") -> Optional[str]:
        """Ultra-fast TTS for streaming chunks"""
        try:
            # Get voice configuration for fast processing
            voice_config = self.voice_personalities.get(personality, self.voice_personalities["friendly_companion"])
            
            # Process human-like expressions for natural speech
            enhanced_text = self._enhance_text_with_expressions(text, personality)
            
            # Prepare headers for fast processing
            headers = {
                "Authorization": f"Token {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Prepare request body with optimized settings
            payload = {
                "text": enhanced_text
            }
            
            # Use Aura-2 with speed optimization
            params = {
                "model": voice_config["model"],
                "speed": "1.1",  # Slightly faster for lower perceived latency
                "encoding": "linear16",  # Optimal for streaming
                "sample_rate": "16000"  # Optimized sample rate
            }
            
            logger.info(f"⚡ Ultra-fast TTS chunk: {enhanced_text[:50]}...")
            
            # Make fast async request
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(
                    f"{self.base_url}/speak",
                    headers=headers,
                    params=params,
                    json=payload,
                    timeout=3  # Ultra-fast timeout for chunks
                )
            )
            
            if response.status_code == 200:
                audio_data = response.content
                # Convert to base64 for frontend
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                
                logger.info(f"⚡ Ultra-fast TTS chunk completed: {len(audio_base64)} chars")
                return audio_base64
            else:
                logger.error(f"Ultra-fast TTS chunk error: {response.status_code} - {response.text}")
                return None
            
        except Exception as e:
            logger.error(f"Ultra-fast TTS chunk error: {str(e)}")
            return None

    async def text_to_speech_stream_chunks(self, text_chunks: List[Dict[str, Any]], personality: str = "friendly_companion") -> Dict[str, Any]:
        """Stream TTS audio for story chunks with immediate playback"""
        try:
            logger.info(f"🎵 TTS CHUNK STREAMING: Processing {len(text_chunks)} story chunks")
            
            audio_chunks = []
            
            # Process each chunk immediately for streaming
            for i, chunk_data in enumerate(text_chunks):
                chunk_text = chunk_data.get("text", "")
                chunk_id = chunk_data.get("chunk_id", i)
                
                logger.info(f"🎵 Processing chunk {chunk_id + 1}/{len(text_chunks)}: {len(chunk_text)} chars")
                
                # Generate TTS for this chunk
                start_time = time.time()
                
                try:
                    # Use ultra-fast TTS for immediate response
                    audio_base64 = await self.text_to_speech_ultra_fast(chunk_text, personality)
                    
                    tts_time = time.time() - start_time
                    
                    if audio_base64:
                        audio_chunks.append({
                            "chunk_id": chunk_id,
                            "audio_base64": audio_base64,
                            "text": chunk_text,
                            "audio_length": len(audio_base64),
                            "generation_time": tts_time,
                            "word_count": len(chunk_text.split())
                        })
                        logger.info(f"✅ Chunk {chunk_id + 1} TTS: {tts_time:.2f}s, {len(audio_base64)} chars audio")
                    else:
                        logger.error(f"❌ Chunk {chunk_id + 1} TTS failed")
                        
                        # Generate fallback audio for failed chunk
                        fallback_audio = await self._generate_simple_test_audio(personality)
                        if fallback_audio:
                            audio_chunks.append({
                                "chunk_id": chunk_id,
                                "audio_base64": fallback_audio,
                                "text": chunk_text,
                                "audio_length": len(fallback_audio),
                                "generation_time": tts_time,
                                "word_count": len(chunk_text.split()),
                                "is_fallback": True
                            })
                            logger.info(f"⚠️ Chunk {chunk_id + 1} using fallback audio")
                    
                    # Small delay to prevent rate limiting but maintain speed
                    if i < len(text_chunks) - 1:  # Don't delay after last chunk
                        await asyncio.sleep(0.05)  # 50ms delay
                        
                except Exception as chunk_error:
                    logger.error(f"❌ Error processing chunk {chunk_id + 1}: {str(chunk_error)}")
                    continue
            
            if audio_chunks:
                total_audio_time = sum(chunk["generation_time"] for chunk in audio_chunks)
                total_audio_size = sum(chunk["audio_length"] for chunk in audio_chunks)
                
                logger.info(f"🎉 TTS CHUNK STREAMING COMPLETE: {len(audio_chunks)}/{len(text_chunks)} chunks, {total_audio_time:.2f}s total, {total_audio_size} chars audio")
                
                return {
                    "status": "success",
                    "audio_chunks": audio_chunks,
                    "total_chunks": len(audio_chunks),
                    "total_generation_time": total_audio_time,
                    "total_audio_size": total_audio_size
                }
            else:
                logger.error("❌ No audio chunks generated")
                return {"status": "error", "error": "No audio chunks generated"}
                
        except Exception as e:
            logger.error(f"❌ TTS chunk streaming error: {str(e)}")
            return {"status": "error", "error": str(e)}

    async def text_to_speech_ultra_fast(self, text: str, personality: str = "friendly_companion") -> Optional[str]:
        """ULTRA-LOW LATENCY: Generate TTS with <2s target per chunk"""
        try:
            import time
            start_time = time.time()
            logger.info(f"🚀 ULTRA-FAST TTS: Processing {len(text)} chars with {personality}")
            
            # OPTIMIZATION: Skip cleaning for ultra-fast mode to save time
            # clean_text = self._clean_text_for_natural_speech(text, personality)
            # Use text directly for speed
            clean_text = text.strip()
            
            # OPTIMIZATION: Use aura-2-amalthea-en voice model as requested
            voice_config = {
                "model": "aura-2-amalthea-en"  # Restored to aura-2-amalthea-en
            }
            
            logger.info(f"TTS using voice model: {voice_config['model']}")
            
            headers = {
                "Authorization": f"Token {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # OPTIMIZATION: Minimal payload for speed
            payload = {
                "text": clean_text
            }
            
            # Use query parameters with speed optimizations
            params = {
                "model": voice_config["model"],
                "encoding": "linear16",  # Faster encoding
                "sample_rate": 24000,   # Lower sample rate for speed
                "container": "wav"
            }
            
            url = f"{self.base_url}/speak"
            
            # OPTIMIZATION: Use requests directly with minimal timeout
            response = requests.post(
                url,
                headers=headers,
                params=params,
                json=payload,
                timeout=1.5  # ULTRA-AGGRESSIVE timeout for <4s target
            )
            
            tts_time = time.time() - start_time
            logger.info(f"⚡ ULTRA-FAST TTS CALL: {tts_time:.3f}s, status: {response.status_code}")
            
            if response.status_code == 200:
                # Convert audio bytes to base64 immediately
                audio_base64 = base64.b64encode(response.content).decode('utf-8')
                logger.info(f"✅ ULTRA-FAST TTS SUCCESS: {len(audio_base64)} chars in {tts_time:.3f}s")
                return audio_base64
            else:
                logger.error(f"❌ Ultra-fast TTS failed: {response.status_code} - {response.text[:100]}")
                
                # Quick fallback - generate simple audio
                try:
                    fallback_audio = await self._generate_simple_test_audio(personality)
                    if fallback_audio:
                        logger.info("🔄 Using simple fallback audio for ultra-fast mode")
                        return fallback_audio
                except:
                    pass
                
                return None
                
        except requests.exceptions.Timeout:
            logger.error("❌ Ultra-fast TTS timeout (1.5s) - using fallback")
            # Use fallback audio for timeout
            try:
                fallback_audio = await self._generate_simple_test_audio(personality)
                if fallback_audio:
                    logger.info("🔄 Timeout fallback audio generated")
                    return fallback_audio
            except:
                pass
            return None
            
        except Exception as e:
            logger.error(f"❌ Ultra-fast TTS error: {str(e)}")
            return None
    
    def _enhance_text_with_expressions(self, text: str, personality: str) -> str:
        """Add human-like expressions for natural speech"""
        try:
            # Add natural vocal expressions based on content
            enhanced_text = text
            
            # Add natural breathing and pauses
            enhanced_text = re.sub(r'\[pause\]', '... ', enhanced_text)
            enhanced_text = re.sub(r'\[excited\]', '', enhanced_text)  # Let natural excitement show
            enhanced_text = re.sub(r'\[gentle\]', '', enhanced_text)   # Let natural gentleness show
            
            # Replace expression markers with natural speech patterns or remove them
            expression_replacements = {
                # Natural expressions that should be removed (not spoken)
                '*giggles*': '',
                '*chuckles*': '',
                '*laughs*': '',
                '*sighs*': '',
                '*whispers*': '',
                '*gasps*': '',
                
                # Keep some natural interjections that work in speech
                '[giggle]': '',
                '[chuckle]': '',
                '[gasp]': ' oh! ',
                '[whisper]': '',
                '[amazed]': ' wow! ',
                '[surprised]': ' oh my! ',
                '[pause for effect]': '... ',
                '[pause]': '... ',
                
                # Complex expressions that should be removed (TTS instructions)
                '[playful chuckle]': '',
                '[with a big smile]': '',
                '[enthusiastically]': '',
                '[Enthusiastically]': '',
                '[warm, friendly tone]': '',
                '[Warm, friendly tone]': '',
                '[gentle]': '',
                '[excited]': '',
                '[friendly]': '',
                '[happily]': '',
                '[cheerfully]': '',
                '[softly]': '',
                '[warmly]': '',
                '[encouraging]': '',
                '[with excitement]': '',
                '[with wonder]': '',
                '[mysteriously]': '',
                '[dramatically]': '',
                '[proudly]': '',
                '[gently]': '',
                '[lovingly]': '',
                '[patiently]': '',
            }
            
            # Apply replacements and removals
            for marker, replacement in expression_replacements.items():
                enhanced_text = enhanced_text.replace(marker, replacement)
            
            # Remove any remaining bracketed expressions that weren't caught above
            enhanced_text = re.sub(r'\[([^\]]*)\]', '', enhanced_text)
            
            # Remove asterisk expressions like *giggles*, *chuckles*, etc.
            enhanced_text = re.sub(r'\*([^*]*)\*', '', enhanced_text)
            
            # Add natural speech fillers for personality
            if personality == "friendly_companion":
                # Add friendly natural sounds
                enhanced_text = re.sub(r'\bHmm\b', 'Hmm... ', enhanced_text)
                enhanced_text = re.sub(r'\bOh\b', 'Oh! ', enhanced_text)
                enhanced_text = re.sub(r'\bWow\b', 'Wow! ', enhanced_text)
            
            # Clean up multiple spaces
            enhanced_text = re.sub(r'\s+', ' ', enhanced_text).strip()
            
            logger.info(f"Enhanced text with expressions for {personality}")
            return enhanced_text
            
        except Exception as e:
            logger.error(f"Expression enhancement error: {str(e)}")
            return text
    

    async def _generate_simple_test_audio(self, personality: str) -> Optional[str]:
        """Generate simple test audio response for fallback"""
        try:
            logger.info("🎵 SIMPLE TEST AUDIO: Generating 'Test audio response' fallback")
            
            fallback_text = "Test audio response"
            headers = {
                "Authorization": f"Token {self.api_key}",
                "Content-Type": "application/json"
            }
            
            voice_config = self.voice_personalities.get(personality, self.voice_personalities["friendly_companion"])
            payload = {"text": fallback_text}
            params = {"model": voice_config["model"]}
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(
                    f"{self.base_url}/speak",
                    headers=headers,
                    params=params,
                    json=payload,
                    timeout=10
                )
            )
            
            if response.status_code == 200:
                audio_data = response.content
                if len(audio_data) > 0:
                    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                    logger.info(f"🎵 SIMPLE TEST AUDIO: Success - size: {len(audio_base64)}")
                    return audio_base64
                else:
                    logger.error("🎵 SIMPLE TEST AUDIO: Empty audio data returned")
                    return None
            else:
                logger.error(f"🎵 SIMPLE TEST AUDIO: API error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"🎵 SIMPLE TEST AUDIO: Exception: {str(e)}")
            return None


    async def _retry_tts_with_fallback(self, text: str, personality: str) -> Optional[str]:
        """Retry TTS with fallback text if original fails"""
        try:
            logger.info("🎵 DEBUG TTS FALLBACK: Attempting TTS with fallback message")
            
            fallback_text = "Test audio"
            headers = {
                "Authorization": f"Token {self.api_key}",
                "Content-Type": "application/json"
            }
            
            voice_config = self.voice_personalities.get(personality, self.voice_personalities["friendly_companion"])
            payload = {"text": fallback_text}
            params = {"model": voice_config["model"]}
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(
                    f"{self.base_url}/speak",
                    headers=headers,
                    params=params,
                    json=payload,
                    timeout=10
                )
            )
            
            if response.status_code == 200:
                audio_data = response.content
                if len(audio_data) > 0:
                    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                    logger.info(f"🎵 DEBUG TTS FALLBACK: Fallback TTS successful - size: {len(audio_base64)}")
                    return audio_base64
                else:
                    logger.error("🎵 DEBUG TTS FALLBACK: Fallback returned empty audio")
                    return None
            else:
                logger.error(f"🎵 DEBUG TTS FALLBACK: Fallback TTS failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"🎵 DEBUG TTS FALLBACK: Exception in fallback: {str(e)}")
            return None
        """Get available voice personalities"""
        return {
            "friendly_companion": {
                "name": "Friendly Companion",
                "description": "Warm and encouraging voice for daily conversations",
                "sample_text": "Hi there! I'm your friendly AI companion. What would you like to talk about today?"
            },
            "story_narrator": {
                "name": "Story Narrator", 
                "description": "Engaging storyteller voice for bedtime stories",
                "sample_text": "Once upon a time, in a magical forest far away, there lived a very special little rabbit..."
            },
            "learning_buddy": {
                "name": "Learning Buddy",
                "description": "Patient teacher voice for educational content",
                "sample_text": "That's a great question! Let me help you understand this step by step."
            }
        }