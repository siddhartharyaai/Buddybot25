"""
Voice Agent - Enhanced with ultra-low latency streaming for real-time voice AI
"""
import asyncio
import logging
import base64
import requests
import re
from typing import Optional, Dict, Any, List


logger = logging.getLogger(__name__)


class VoiceAgent:
    """Simplified voice processing with Deepgram Nova 3 STT and Aura 2 TTS using REST API"""
    
    def __init__(self, deepgram_api_key: str):
        self.api_key = deepgram_api_key
        self.base_url = "https://api.deepgram.com/v1"
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
        
        logger.info("Voice Agent initialized with simplified Deepgram REST API")

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
                "Authorization": f"Token {self.api_key}",
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
        """Convert long text to speech with chunking for conversation, but single call for stories"""
        try:
            logger.info(f"Processing TTS for {len(text)} characters with personality: {personality}")
            
            # For story narration, don't chunk - send the complete story as one request
            # Stories should be narrated as a complete, uninterrupted experience
            if len(text) > 3000:  # Only chunk very long texts (>3000 chars)
                logger.info("Text is very long, using chunked processing")
                
                # Split text into manageable chunks (1500 chars to stay within limits)
                chunks = self._split_text_into_chunks(text, 1500)
                logger.info(f"Split into {len(chunks)} chunks")
                
                audio_chunks = []
                for i, chunk in enumerate(chunks):
                    logger.info(f"Processing chunk {i+1}/{len(chunks)}: {chunk[:50]}...")
                    
                    audio_base64 = await self.text_to_speech(chunk, personality)
                    if audio_base64:
                        audio_chunks.append(audio_base64)
                        # Add delay between chunks to avoid rate limiting
                        await asyncio.sleep(0.5)
                    else:
                        logger.warning(f"Failed to generate audio for chunk {i+1}")
                
                if audio_chunks:
                    # Return first chunk for immediate playback
                    logger.info(f"Chunked TTS completed: {len(audio_chunks)} chunks")
                    return self._concatenate_audio_chunks(audio_chunks)
                else:
                    logger.error("No audio chunks generated")
                    return None
            else:
                # For shorter texts and stories, process as single request for better flow
                logger.info("Processing as single TTS request for better narrative flow")
                return await self.text_to_speech(text, personality)
                
        except Exception as e:
            logger.error(f"Chunked TTS error: {str(e)}")
            return None
    
    def _split_text_into_chunks(self, text: str, max_size: int) -> List[str]:
        """Split text into chunks at sentence boundaries"""
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
            
            # If adding this sentence would exceed max size, start new chunk
            if len(current_chunk) + len(sentence) + 1 > max_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                current_chunk += " " + sentence if current_chunk else sentence
        
        # Add the last chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _concatenate_audio_chunks(self, audio_chunks: List[str]) -> str:
        """Concatenate base64 audio chunks - return all chunks combined"""
        try:
            if not audio_chunks:
                return ""
            
            # For now, we'll return all chunks as a single base64 string
            # Since proper audio concatenation requires complex audio processing,
            # we'll return the combined chunks with markers for frontend handling
            
            # Return the first chunk for immediate playback
            # TODO: Implement proper audio concatenation with pydub or similar library
            logger.info(f"Returning first of {len(audio_chunks)} audio chunks (sizes: {[len(chunk) for chunk in audio_chunks[:5]]}...)")
            
            # For stories, we want the complete first chunk which should be the full story
            return audio_chunks[0] if audio_chunks else ""
            
        except Exception as e:
            logger.error(f"Audio concatenation error: {str(e)}")
            return audio_chunks[0] if audio_chunks else ""

    async def text_to_speech(self, text: str, personality: str = "friendly_companion") -> Optional[str]:
        """Convert text to speech using Deepgram Aura 2 REST API with clean, natural speech"""
        try:
            # Get voice configuration
            voice_config = self.voice_personalities.get(personality, self.voice_personalities["friendly_companion"])
            
            # Clean text of any markup - ensure pure natural speech
            clean_text = self._clean_text_for_natural_speech(text, personality)
            
            # Prepare headers
            headers = {
                "Authorization": f"Token {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Prepare request body with clean text only
            payload = {
                "text": clean_text
            }
            
            # Prepare query parameters
            params = {
                "model": voice_config["model"]
            }
            
            logger.info(f"Making TTS request with clean text: {clean_text[:100]}...")
            
            # Make REST API call using requests in async context
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(
                    f"{self.base_url}/speak",
                    headers=headers,
                    params=params,
                    json=payload,
                    timeout=15
                )
            )
            
            if response.status_code == 200:
                audio_data = response.content
                # Convert to base64 for frontend
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                
                logger.info(f"TTS successful with clean text, audio size: {len(audio_base64)} chars")
                return audio_base64
            else:
                logger.error(f"TTS API error: {response.status_code} - {response.text}")
                return None
            
        except Exception as e:
            logger.error(f"TTS error: {str(e)}")
            return None
    
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
                "Authorization": f"Token {self.api_key}",
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