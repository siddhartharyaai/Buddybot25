"""
Emotional Sensing Agent - Analyzes user sentiment and energy levels
"""
import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)

class EmotionalSensingAgent:
    """Handles emotional analysis of user input for adaptive responses"""
    
    def __init__(self, gemini_api_key: str):
        self.gemini_api_key = gemini_api_key
        
        # Emotional state mappings
        self.sentiment_labels = ["positive", "neutral", "negative"]
        self.energy_labels = ["low", "medium", "high"]
        self.mood_indicators = {
            "excited": ["wow", "yay", "awesome", "amazing", "cool", "fun"],
            "sad": ["sad", "cry", "upset", "bad", "hurt", "lonely"],
            "tired": ["tired", "sleepy", "yawn", "bed", "rest"],
            "confused": ["what", "why", "how", "don't understand", "help"],
            "happy": ["happy", "good", "smile", "laugh", "joy", "great"],
            "angry": ["mad", "angry", "upset", "hate", "annoying"]
        }
        
        logger.info("Emotional Sensing Agent initialized")
    
    async def analyze_emotional_state(self, user_input: str, user_profile: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze emotional state from user input"""
        try:
            age = user_profile.get('age', 5)
            
            # Quick sentiment analysis using keyword matching
            quick_sentiment = self._quick_sentiment_analysis(user_input)
            
            # Energy level detection
            energy_level = self._detect_energy_level(user_input)
            
            # Mood detection
            detected_mood = self._detect_mood(user_input)
            
            # Deep analysis using Gemini for complex cases
            if quick_sentiment == "uncertain" or detected_mood == "uncertain":
                deep_analysis = await self._deep_emotional_analysis(user_input, age)
                return {
                    **deep_analysis,
                    "energy_level": energy_level,
                    "analysis_type": "deep",
                    "confidence": deep_analysis.get("confidence", 0.8)
                }
            
            return {
                "sentiment": quick_sentiment,
                "energy_level": energy_level,
                "mood": detected_mood,
                "emotional_indicators": self._extract_emotional_indicators(user_input),
                "analysis_type": "quick",
                "confidence": 0.7,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing emotional state: {str(e)}")
            return self._get_default_emotional_state()
    
    def _quick_sentiment_analysis(self, text: str) -> str:
        """Quick sentiment analysis using keyword matching"""
        text_lower = text.lower()
        
        positive_indicators = [
            "good", "great", "awesome", "fun", "happy", "love", "like", "yes", 
            "cool", "amazing", "wonderful", "nice", "thank you", "please", "yay"
        ]
        
        negative_indicators = [
            "bad", "sad", "no", "hate", "don't like", "upset", "angry", "hurt", 
            "cry", "scared", "worried", "tired", "bored", "annoying"
        ]
        
        positive_score = sum(1 for word in positive_indicators if word in text_lower)
        negative_score = sum(1 for word in negative_indicators if word in text_lower)
        
        if positive_score > negative_score and positive_score > 0:
            return "positive"
        elif negative_score > positive_score and negative_score > 0:
            return "negative"
        elif positive_score == negative_score == 0:
            return "neutral"
        else:
            return "uncertain"
    
    def _detect_energy_level(self, text: str) -> str:
        """Detect energy level from text characteristics"""
        text_lower = text.lower()
        
        # High energy indicators
        high_energy_indicators = [
            "!", "wow", "yay", "amazing", "excited", "run", "play", "jump", 
            "fast", "quick", "loud", "big", "huge"
        ]
        
        # Low energy indicators
        low_energy_indicators = [
            "tired", "sleepy", "slow", "quiet", "soft", "small", "little", 
            "rest", "sit", "calm", "peaceful"
        ]
        
        # Check for multiple exclamation marks or caps
        if text.count("!") > 1 or text.isupper():
            return "high"
        
        high_score = sum(1 for indicator in high_energy_indicators if indicator in text_lower)
        low_score = sum(1 for indicator in low_energy_indicators if indicator in text_lower)
        
        if high_score > low_score and high_score > 0:
            return "high"
        elif low_score > high_score and low_score > 0:
            return "low"
        else:
            return "medium"
    
    def _detect_mood(self, text: str) -> str:
        """Detect specific mood from text"""
        text_lower = text.lower()
        
        mood_scores = {}
        for mood, indicators in self.mood_indicators.items():
            score = sum(1 for indicator in indicators if indicator in text_lower)
            if score > 0:
                mood_scores[mood] = score
        
        if not mood_scores:
            return "neutral"
        
        # Return the mood with highest score
        return max(mood_scores, key=mood_scores.get)
    
    def _extract_emotional_indicators(self, text: str) -> Dict[str, Any]:
        """Extract specific emotional indicators from text"""
        text_lower = text.lower()
        
        return {
            "exclamation_count": text.count("!"),
            "question_count": text.count("?"),
            "caps_ratio": sum(1 for c in text if c.isupper()) / len(text) if text else 0,
            "word_count": len(text.split()),
            "repeated_letters": self._detect_repeated_letters(text),
            "emotional_words": [word for word in text.split() if self._is_emotional_word(word.lower())]
        }
    
    def _detect_repeated_letters(self, text: str) -> bool:
        """Detect repeated letters indicating excitement (e.g., 'sooo good', 'yaaaay')"""
        import re
        pattern = r'(.)\1{2,}'  # 3 or more repeated characters
        return bool(re.search(pattern, text))
    
    def _is_emotional_word(self, word: str) -> bool:
        """Check if a word is emotionally charged"""
        emotional_words = set()
        for mood_words in self.mood_indicators.values():
            emotional_words.update(mood_words)
        
        return word in emotional_words
    
    async def _deep_emotional_analysis(self, text: str, age: int) -> Dict[str, Any]:
        """Deep emotional analysis using Gemini for complex cases"""
        try:
            system_prompt = f"""
            You are an expert in child psychology and emotional analysis. Analyze the emotional state of a {age}-year-old child based on their message.

            Provide analysis in this exact JSON format:
            {{
                "sentiment": "positive" | "neutral" | "negative",
                "mood": "excited" | "sad" | "tired" | "confused" | "happy" | "angry" | "neutral",
                "confidence": 0.0-1.0,
                "emotional_needs": ["comfort", "encouragement", "play", "rest", "understanding"],
                "suggested_response_tone": "encouraging" | "soothing" | "playful" | "understanding" | "gentle"
            }}

            Consider:
            - Age-appropriate emotional expressions
            - Context clues from the message
            - Emotional needs of children this age
            - Cultural context (Indian English/Hinglish)
            """

            chat = LlmChat(
                api_key=self.gemini_api_key,
                system_message=system_prompt
            ).with_model("gemini", "gemini-2.0-flash").with_max_tokens(200)

            user_message = UserMessage(text=f"Child's message: '{text}'")
            response = await chat.send_message(user_message)

            # Parse JSON response
            import json
            try:
                analysis = json.loads(response)
                return analysis
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return self._parse_text_response(response)

        except Exception as e:
            logger.error(f"Error in deep emotional analysis: {str(e)}")
            return self._get_default_emotional_state()
    
    def _parse_text_response(self, response: str) -> Dict[str, Any]:
        """Parse text response if JSON parsing fails"""
        # Simple text parsing fallback
        sentiment = "neutral"
        mood = "neutral"
        
        if "positive" in response.lower():
            sentiment = "positive"
        elif "negative" in response.lower():
            sentiment = "negative"
        
        for mood_type in ["excited", "sad", "tired", "confused", "happy", "angry"]:
            if mood_type in response.lower():
                mood = mood_type
                break
        
        return {
            "sentiment": sentiment,
            "mood": mood,
            "confidence": 0.6,
            "emotional_needs": ["understanding"],
            "suggested_response_tone": "gentle"
        }
    
    def _get_default_emotional_state(self) -> Dict[str, Any]:
        """Get default emotional state for error cases"""
        return {
            "sentiment": "neutral",
            "energy_level": "medium",
            "mood": "neutral",
            "emotional_indicators": {},
            "analysis_type": "default",
            "confidence": 0.5,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_response_adaptation(self, emotional_state: Dict[str, Any]) -> Dict[str, Any]:
        """Get response adaptation recommendations based on emotional state"""
        sentiment = emotional_state.get("sentiment", "neutral")
        energy = emotional_state.get("energy_level", "medium")
        mood = emotional_state.get("mood", "neutral")
        
        # Response tone adaptation
        tone_mapping = {
            "excited": "playful",
            "sad": "comforting",
            "tired": "soothing",
            "confused": "patient",
            "happy": "enthusiastic",
            "angry": "calming",
            "neutral": "friendly"
        }
        
        # Response length adaptation
        length_mapping = {
            "high": "medium",  # High energy can handle medium responses
            "medium": "medium",
            "low": "short"  # Low energy needs shorter responses
        }
        
        # Mode recommendations
        mode_mapping = {
            "excited": "game",
            "sad": "comfort",
            "tired": "bedtime",
            "confused": "teaching",
            "happy": "chat",
            "angry": "calm",
            "neutral": "chat"
        }
        
        return {
            "suggested_tone": tone_mapping.get(mood, "friendly"),
            "suggested_length": length_mapping.get(energy, "medium"),
            "suggested_mode": mode_mapping.get(mood, "chat"),
            "emotional_needs": emotional_state.get("emotional_needs", []),
            "confidence": emotional_state.get("confidence", 0.5)
        }