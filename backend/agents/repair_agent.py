"""
Conversational Repair Agent - Handles STT errors and conversational misunderstandings
"""
import asyncio
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import difflib
import re

logger = logging.getLogger(__name__)

class RepairAgent:
    """Handles conversational repair for STT errors and misunderstandings"""
    
    def __init__(self):
        # Common child speech corrections
        self.child_speech_corrections = {
            "twy": "try", "fwee": "free", "bwue": "blue", "gweat": "great",
            "pwease": "please", "wove": "love", "vewy": "very", "widdle": "little",
            "wight": "right", "weally": "really", "fwiend": "friend", "wun": "run",
            "wight": "light", "wed": "red", "wellow": "yellow", "gween": "green",
            "bwown": "brown", "puwple": "purple", "owange": "orange", "bwack": "black",
            "dino": "dinosaur", "doggie": "dog", "kitty": "cat", "bunny": "rabbit",
            "fishie": "fish", "birdie": "bird", "horsie": "horse", "piggie": "pig"
        }
        
        # Common STT error patterns
        self.stt_error_patterns = {
            "die": ["dinosaur", "dino", "die"],
            "bad": ["dad", "pad", "bat"],
            "cat": ["bat", "hat", "mat"],
            "big": ["pig", "fig", "dig"],
            "see": ["sea", "bee", "tea"],
            "too": ["two", "to", "do"],
            "no": ["go", "so", "now"],
            "play": ["pray", "clay", "stay"],
            "story": ["sorry", "study", "start"],
            "song": ["long", "strong", "wrong"],
            "game": ["same", "name", "came"],
            "fun": ["run", "sun", "done"],
            "good": ["food", "wood", "book"],
            "help": ["kelp", "yelp", "held"],
            "want": ["went", "won't", "what"],
            "like": ["bike", "hike", "mike"],
            "love": ["dove", "glove", "above"],
            "happy": ["sappy", "nappy", "snappy"],
            "sad": ["mad", "bad", "dad"],
            "tired": ["wired", "hired", "fired"],
            "hungry": ["angry", "hurry", "hung"],
            "thirsty": ["thirty", "first", "worst"]
        }
        
        # Contextual word suggestions
        self.context_suggestions = {
            "animals": ["dog", "cat", "bird", "fish", "elephant", "lion", "tiger", "bear", "rabbit", "horse"],
            "colors": ["red", "blue", "green", "yellow", "purple", "orange", "pink", "brown", "black", "white"],
            "actions": ["play", "run", "jump", "dance", "sing", "read", "eat", "sleep", "walk", "talk"],
            "emotions": ["happy", "sad", "angry", "excited", "tired", "scared", "surprised", "confused"],
            "family": ["mom", "dad", "sister", "brother", "grandma", "grandpa", "uncle", "aunt", "cousin"],
            "toys": ["ball", "doll", "car", "blocks", "puzzle", "game", "teddy", "truck", "bike", "train"],
            "food": ["apple", "banana", "cookie", "pizza", "cake", "ice cream", "sandwich", "juice", "milk"],
            "activities": ["story", "song", "game", "dance", "draw", "paint", "build", "count", "learn"]
        }
        
        # Repair response templates
        self.repair_templates = {
            "clarification": [
                "Did you mean {suggestion}?",
                "I think you said {suggestion}. Is that right?",
                "Are you talking about {suggestion}?",
                "Do you mean {suggestion}?"
            ],
            "multiple_options": [
                "I heard {original}. Did you mean {suggestion1} or {suggestion2}?",
                "Are you saying {suggestion1} or {suggestion2}?",
                "I'm not sure if you said {suggestion1} or {suggestion2}. Which one?"
            ],
            "context_based": [
                "When you said {original}, did you mean {suggestion}?",
                "I think you're talking about {suggestion}. Is that right?",
                "Are you trying to say {suggestion}?"
            ],
            "gentle_correction": [
                "I think you meant {suggestion}. Let's talk about that!",
                "Oh, {suggestion}! Yes, let's talk about that.",
                "Ah, {suggestion}! That's a great topic."
            ]
        }
        
        logger.info("Repair Agent initialized")
    
    async def detect_repair_need(self, 
                               user_input: str, 
                               stt_confidence: float, 
                               context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Detect if conversational repair is needed"""
        
        try:
            repair_indicators = []
            
            # Check STT confidence
            if stt_confidence < 0.6:
                repair_indicators.append("low_stt_confidence")
            
            # Check for explicit repair requests
            if self._detect_explicit_repair(user_input):
                repair_indicators.append("explicit_repair_request")
            
            # Check for nonsensical words
            if self._detect_nonsensical_words(user_input):
                repair_indicators.append("nonsensical_words")
            
            # Check for very short responses that might be corrections
            if self._detect_short_correction(user_input, context):
                repair_indicators.append("short_correction")
            
            # Check for common STT error patterns
            if self._detect_stt_error_patterns(user_input):
                repair_indicators.append("stt_error_patterns")
            
            repair_needed = len(repair_indicators) > 0
            
            return {
                "repair_needed": repair_needed,
                "indicators": repair_indicators,
                "confidence": stt_confidence,
                "original_input": user_input,
                "repair_type": self._determine_repair_type(repair_indicators)
            }
            
        except Exception as e:
            logger.error(f"Error detecting repair need: {str(e)}")
            return {"repair_needed": False, "indicators": [], "confidence": 1.0}
    
    async def generate_repair_response(self, 
                                     repair_info: Dict[str, Any],
                                     user_profile: Dict[str, Any],
                                     conversation_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate appropriate repair response"""
        
        try:
            if not repair_info.get("repair_needed", False):
                return {"repair_response": None, "suggestions": []}
            
            original_input = repair_info["original_input"]
            repair_type = repair_info["repair_type"]
            
            # Generate suggestions based on repair type
            suggestions = await self._generate_suggestions(
                original_input, repair_type, user_profile, conversation_context
            )
            
            if not suggestions:
                return {"repair_response": None, "suggestions": []}
            
            # Generate repair response
            repair_response = self._generate_repair_response_text(
                original_input, suggestions, repair_type, user_profile
            )
            
            return {
                "repair_response": repair_response,
                "suggestions": suggestions,
                "repair_type": repair_type,
                "original_input": original_input
            }
            
        except Exception as e:
            logger.error(f"Error generating repair response: {str(e)}")
            return {"repair_response": None, "suggestions": []}
    
    def _detect_explicit_repair(self, user_input: str) -> bool:
        """Detect explicit repair requests"""
        
        repair_keywords = [
            "no", "not that", "i didn't say", "i meant", "actually", 
            "wait", "that's wrong", "i said", "listen", "no no",
            "wrong", "fix", "change", "correct", "oops"
        ]
        
        user_input_lower = user_input.lower()
        return any(keyword in user_input_lower for keyword in repair_keywords)
    
    def _detect_nonsensical_words(self, user_input: str) -> bool:
        """Detect nonsensical or very unclear words"""
        
        words = user_input.lower().split()
        
        # Check for very short words that might be errors
        short_unclear_words = [word for word in words if len(word) <= 2 and word not in ["i", "a", "is", "it", "we", "do", "go", "to", "up", "on", "in", "at", "of", "or", "so", "no", "me", "my", "be", "he", "hi"]]
        
        # Check for words with unusual character patterns
        unusual_patterns = [
            r'^[bcdfghjklmnpqrstvwxyz]{4,}$',  # All consonants
            r'^[aeiou]{3,}$',  # All vowels
            r'^(.)\1{3,}$',  # Repeated characters
            r'^[^a-zA-Z0-9\s]{2,}$'  # Special characters
        ]
        
        for word in words:
            for pattern in unusual_patterns:
                if re.match(pattern, word):
                    return True
        
        return len(short_unclear_words) > 0
    
    def _detect_short_correction(self, user_input: str, context: Dict[str, Any] = None) -> bool:
        """Detect short corrections"""
        
        words = user_input.split()
        
        # Very short responses that might be corrections
        if len(words) <= 2:
            if context and context.get("last_ai_response"):
                # Check if it's a correction to the last response
                return True
        
        return False
    
    def _detect_stt_error_patterns(self, user_input: str) -> bool:
        """Detect common STT error patterns"""
        
        words = user_input.lower().split()
        
        for word in words:
            # Check against known error patterns
            if word in self.stt_error_patterns:
                return True
            
            # Check against child speech patterns
            if word in self.child_speech_corrections:
                return True
        
        return False
    
    def _determine_repair_type(self, indicators: List[str]) -> str:
        """Determine the type of repair needed"""
        
        if "explicit_repair_request" in indicators:
            return "explicit_correction"
        elif "low_stt_confidence" in indicators:
            return "stt_clarification"
        elif "nonsensical_words" in indicators:
            return "word_clarification"
        elif "short_correction" in indicators:
            return "simple_correction"
        elif "stt_error_patterns" in indicators:
            return "pattern_correction"
        else:
            return "general_clarification"
    
    async def _generate_suggestions(self, 
                                  original_input: str,
                                  repair_type: str,
                                  user_profile: Dict[str, Any],
                                  conversation_context: Dict[str, Any] = None) -> List[str]:
        """Generate repair suggestions"""
        
        suggestions = []
        words = original_input.lower().split()
        
        # Apply child speech corrections
        corrected_words = []
        for word in words:
            if word in self.child_speech_corrections:
                corrected_words.append(self.child_speech_corrections[word])
            else:
                corrected_words.append(word)
        
        corrected_text = " ".join(corrected_words)
        if corrected_text != original_input.lower():
            suggestions.append(corrected_text)
        
        # Apply STT error pattern corrections
        for word in words:
            if word in self.stt_error_patterns:
                similar_words = self.stt_error_patterns[word]
                # Add contextually appropriate suggestions
                for similar_word in similar_words:
                    if similar_word not in suggestions:
                        suggestions.append(similar_word)
        
        # Generate context-based suggestions
        if conversation_context:
            context_suggestions = self._get_context_suggestions(
                original_input, conversation_context, user_profile
            )
            suggestions.extend(context_suggestions)
        
        # Generate phonetic suggestions
        phonetic_suggestions = self._get_phonetic_suggestions(original_input)
        suggestions.extend(phonetic_suggestions)
        
        # Limit to top 3 suggestions
        return suggestions[:3]
    
    def _get_context_suggestions(self, 
                               original_input: str,
                               conversation_context: Dict[str, Any],
                               user_profile: Dict[str, Any]) -> List[str]:
        """Get contextually appropriate suggestions"""
        
        suggestions = []
        
        # Get user interests
        interests = user_profile.get("interests", [])
        
        # Get conversation topic
        last_ai_response = conversation_context.get("last_ai_response", "")
        
        # Match against context categories
        for category, words in self.context_suggestions.items():
            if category in interests or category in last_ai_response.lower():
                for word in words:
                    if self._is_similar_word(original_input, word):
                        suggestions.append(word)
        
        return suggestions
    
    def _get_phonetic_suggestions(self, original_input: str) -> List[str]:
        """Get phonetically similar suggestions"""
        
        suggestions = []
        
        # Get all possible words from context suggestions
        all_words = []
        for words in self.context_suggestions.values():
            all_words.extend(words)
        
        # Find phonetically similar words
        for word in all_words:
            if self._is_phonetically_similar(original_input, word):
                suggestions.append(word)
        
        return suggestions
    
    def _is_similar_word(self, input_word: str, target_word: str) -> bool:
        """Check if words are similar"""
        
        # Check string similarity
        similarity = difflib.SequenceMatcher(None, input_word.lower(), target_word.lower()).ratio()
        return similarity > 0.6
    
    def _is_phonetically_similar(self, input_word: str, target_word: str) -> bool:
        """Check if words are phonetically similar"""
        
        # Simple phonetic similarity check
        input_sounds = self._get_phonetic_representation(input_word)
        target_sounds = self._get_phonetic_representation(target_word)
        
        similarity = difflib.SequenceMatcher(None, input_sounds, target_sounds).ratio()
        return similarity > 0.7
    
    def _get_phonetic_representation(self, word: str) -> str:
        """Get simple phonetic representation"""
        
        # Simple phonetic mapping
        phonetic_map = {
            'c': 'k', 'ck': 'k', 'ch': 'ch', 'ph': 'f', 'gh': 'g',
            'th': 'th', 'sh': 'sh', 'tion': 'shun', 'sion': 'shun',
            'y': 'i', 'ie': 'i', 'ee': 'i', 'ea': 'i', 'oo': 'u'
        }
        
        word_lower = word.lower()
        for original, replacement in phonetic_map.items():
            word_lower = word_lower.replace(original, replacement)
        
        return word_lower
    
    def _generate_repair_response_text(self, 
                                     original_input: str,
                                     suggestions: List[str],
                                     repair_type: str,
                                     user_profile: Dict[str, Any]) -> str:
        """Generate repair response text"""
        
        age = user_profile.get("age", 5)
        
        if len(suggestions) == 0:
            return "I'm sorry, I didn't understand that clearly. Can you try saying it again?"
        
        if len(suggestions) == 1:
            templates = self.repair_templates.get("clarification", [])
            template = templates[0] if templates else "Did you mean {suggestion}?"
            return template.format(suggestion=suggestions[0])
        
        if len(suggestions) == 2:
            templates = self.repair_templates.get("multiple_options", [])
            template = templates[0] if templates else "Did you mean {suggestion1} or {suggestion2}?"
            return template.format(
                original=original_input,
                suggestion1=suggestions[0],
                suggestion2=suggestions[1]
            )
        
        # Multiple suggestions
        if age <= 6:
            # Simple for young children
            return f"I heard '{original_input}'. Did you mean {suggestions[0]}?"
        else:
            # More options for older children
            return f"I heard '{original_input}'. Did you mean {suggestions[0]}, {suggestions[1]}, or {suggestions[2]}?"
    
    def get_repair_statistics(self) -> Dict[str, Any]:
        """Get repair statistics"""
        
        return {
            "total_corrections": len(self.child_speech_corrections),
            "error_patterns": len(self.stt_error_patterns),
            "context_categories": len(self.context_suggestions),
            "repair_templates": sum(len(templates) for templates in self.repair_templates.values())
        }