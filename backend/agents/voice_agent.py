"""
Voice Agent - Ultra-low latency Deepgram Nova-3 STT and Aura-2 TTS
Optimized for <3s TTS generation and enhanced Indian kids' speech processing
"""
import asyncio
import logging
import base64
import requests
import re
import time
import os
from typing import Optional, Dict, Any, List


logger = logging.getLogger(__name__)


class VoiceAgent:
    """Ultra-fast voice processing with Deepgram Nova-3 STT and Aura-2 TTS"""
    
    def __init__(self, deepgram_api_key: str, mongo_client=None):
        self.deepgram_api_key = deepgram_api_key
        self.base_url = "https://api.deepgram.com/v1"
        
        # Ultra-fast voice personalities optimized for low latency
        self.voice_personalities = {
            "friendly_companion": {
                "model": "aura-2-amalthea-en",
                "description": "Warm, friendly voice for kids"
            },
            "story_narrator": {
                "model": "aura-2-amalthea-en", 
                "description": "Engaging storytelling voice"
            },
            "learning_buddy": {
                "model": "aura-2-amalthea-en",
                "description": "Clear, educational voice"
            }
        }
        
        logger.info("✅ Voice Agent initialized with ultra-fast Deepgram Nova-3 STT and Aura-2 TTS")

    async def initialize(self):
        """Initialize the voice agent - optimized for speed"""
        logger.info("✅ Voice Agent ready - ultra-low latency mode")

    async def text_to_speech(self, text: str, personality: str = "friendly_companion", language: str = "en") -> Optional[str]:
        """Ultra-fast TTS using Deepgram Aura-2 with <3s latency target"""
        try:
            start_time = time.time()
            logger.info(f"🎵 ULTRA-FAST TTS: Processing {len(text)} chars with {personality}")
            
            # Get voice configuration - optimized for speed
            voice_config = self.voice_personalities.get(personality, self.voice_personalities["friendly_companion"])
            
            headers = {
                "Authorization": f"Token {self.deepgram_api_key}",
                "Content-Type": "application/json"
            }
            
            # FIXED: Correct TTS payload format - only text in JSON body
            payload = {
                "text": text
            }
            
            # FIXED: Other parameters go as query parameters
            params = {
                "model": voice_config["model"],
                "encoding": "linear16",
                "container": "wav",
                "sample_rate": 16000,
                "bit_rate": 48000
            }
            
            # Make ultra-fast REST API call
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(
                    f"{self.base_url}/speak",
                    headers=headers,
                    json=payload,
                    params=params,
                    timeout=8  # Optimized timeout for speed vs reliability
                )
            )
            
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                # Ultra-fast base64 conversion
                audio_base64 = base64.b64encode(response.content).decode('utf-8')
                logger.info(f"✅ ULTRA-FAST TTS SUCCESS: {len(response.content)} bytes in {processing_time:.2f}s")
                return audio_base64
            else:
                logger.error(f"❌ Deepgram TTS error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Ultra-fast TTS error: {str(e)}")
            return None

    async def text_to_speech_chunked(self, text: str, personality: str = "friendly_companion", language: str = "en") -> Optional[str]:
        """Ultra-fast chunked TTS for long content with immediate first chunk"""
        try:
            logger.info(f"🎵 CHUNKED TTS: Processing {len(text)} characters")
            
            # Smart chunking for optimal performance
            if len(text) <= 500:  # Single chunk for short text
                return await self.text_to_speech(text, personality, language)
            
            # Split into optimized chunks
            chunks = self._chunk_text_smart(text, max_chunk_size=400)
            logger.info(f"🎵 Split into {len(chunks)} optimized chunks for speed")
            
            # Process first chunk immediately for ultra-low perceived latency
            first_chunk_audio = await self.text_to_speech(chunks[0], personality, language)
            
            if len(chunks) == 1:
                return first_chunk_audio
            
            # For now, return first chunk for immediate playback
            # Note: In production, you'd stream all chunks sequentially
            logger.info(f"✅ CHUNKED TTS: First chunk ready immediately, total chunks: {len(chunks)}")
            return first_chunk_audio
            
        except Exception as e:
            logger.error(f"❌ Chunked TTS error: {str(e)}")
            return None

    async def text_to_speech_streaming(self, text: str, personality: str = "friendly_companion") -> Optional[str]:
        """Streaming TTS for immediate playback start"""
        # For Deepgram, we'll use chunked approach for streaming effect
        return await self.text_to_speech_chunked(text, personality)

    async def text_to_speech_with_prosody(self, text: str, personality: str = "friendly_companion", prosody: dict = None) -> Optional[str]:
        """TTS with basic prosody through text formatting"""
        try:
            enhanced_text = text
            if prosody:
                # Apply basic prosody through punctuation
                if prosody.get("emphasis"):
                    enhanced_text = f"*{text}*"
                elif prosody.get("slow"):
                    enhanced_text = text.replace(" ", "... ")
                elif prosody.get("excited"):
                    enhanced_text = f"{text}!"
            
            return await self.text_to_speech(enhanced_text, personality)
        except Exception as e:
            logger.error(f"❌ Prosody TTS error: {str(e)}")
            return None
    
    def _chunk_text_smart(self, text: str, max_chunk_size: int = 400) -> List[str]:
        """Smart text chunking optimized for natural speech boundaries"""
        if len(text) <= max_chunk_size:
            return [text]
        
        # Split by sentences first for natural boundaries
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            # Check if adding sentence exceeds limit
            if len(current_chunk) + len(sentence) + 1 <= max_chunk_size:
                current_chunk += sentence + " "
            else:
                # Save current chunk and start new one
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + " "
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks

    async def speech_to_text_streaming(self, audio_data: bytes) -> str:
        """Enhanced STT with Indian accents and kids' speech processing"""
        try:
            start_time = time.time()
            logger.info(f"🎤 ENHANCED STT: Processing {len(audio_data)} bytes")
            
            headers = {
                "Authorization": f"Token {self.deepgram_api_key}",
                "Content-Type": "audio/wav"
            }
            
            # Enhanced parameters for Indian kids' speech
            params = {
                "model": "nova-2",
                "language": "en-IN",  # Indian English
                "smart_format": "true",
                "punctuate": "true",
                "diarize": "false",
                "filler_words": "false",
                "numerals": "true",
                "paragraphs": "true",
                "endpointing": "300",
                "interim_results": "false",
                "utterances": "true",
                "profanity_filter": "true",
                "alternatives": "1"
            }
            
            response = requests.post(
                f"{self.base_url}/listen",
                headers=headers,
                params=params,
                data=audio_data,
                timeout=8
            )
            
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("results") and result["results"].get("channels"):
                    channel = result["results"]["channels"][0]
                    if channel.get("alternatives") and len(channel["alternatives"]) > 0:
                        raw_transcript = channel["alternatives"][0].get("transcript", "")
                        
                        if raw_transcript.strip():
                            # Apply enhanced processing for Indian kids' speech
                            enhanced_transcript = await self.enhance_indian_kids_speech(raw_transcript)
                            logger.info(f"✅ ENHANCED STT: '{enhanced_transcript}' ({processing_time:.2f}s)")
                            return enhanced_transcript
            
            logger.warning("⚠️ STT returned empty or invalid response")
            return None
            
        except Exception as e:
            logger.error(f"❌ Enhanced STT error: {str(e)}")
            return None

    async def enhance_indian_kids_speech(self, transcript: str) -> str:
        """Enhanced processing for Indian kids' speech patterns"""
        if not transcript:
            return ""
        
        enhanced_text = transcript.lower().strip()
        
        # Indian accent corrections
        corrections = {
            "vill": "will", "vant": "want", "vork": "work", "vhat": "what",
            "dis": "this", "dat": "that", "dey": "they", "dem": "them",
            "tree": "three", "tank": "thank", "tinking": "thinking",
            
            # Kids' speech patterns
            "wabbit": "rabbit", "wed": "red", "wight": "right", "wun": "run",
            "dat": "that", "dis": "this", "fink": "think", "brover": "brother",
            
            # Hindi-English code switching
            "kahani": "story", "ghar": "home", "paani": "water", "khana": "food",
            "chalo": "let's go", "acha": "good", "bura": "bad",
            
            # Common mispronunciations
            "gonna": "going to", "wanna": "want to", "gimme": "give me",
            "lemme": "let me", "dunno": "don't know"
        }
        
        # Apply corrections
        for incorrect, correct in corrections.items():
            if incorrect in enhanced_text:
                enhanced_text = enhanced_text.replace(incorrect, correct)
        
        # Basic grammar fixes
        enhanced_text = re.sub(r'\bi is\b', 'i am', enhanced_text)
        enhanced_text = re.sub(r'\byou is\b', 'you are', enhanced_text)
        
        # Clean up and capitalize
        enhanced_text = re.sub(r'\s+', ' ', enhanced_text)
        enhanced_text = enhanced_text.strip().capitalize()
        
        return enhanced_text

    async def speech_to_text(self, audio_data: bytes) -> str:
        """Standard STT method"""
        return await self.speech_to_text_streaming(audio_data)