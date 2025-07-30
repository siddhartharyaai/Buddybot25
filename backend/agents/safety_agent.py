"""
Safety Agent - Handles content moderation and child safety
"""
import asyncio
import logging
from typing import Dict, Any, List
import re

logger = logging.getLogger(__name__)

class SafetyAgent:
    """Handles content safety and moderation for children"""
    
    def __init__(self):
        # Inappropriate content patterns
        self.inappropriate_patterns = [
            r'\b(violence|violent|fight|hurt|kill|death|die|blood)\b',
            r'\b(scary|frightening|terrifying|nightmare|monster)\b',
            r'\b(adult|grown.up|inappropriate|sexual|romantic)\b',
            r'\b(weapon|gun|knife|sword|bomb)\b',
            r'\b(drug|alcohol|cigarette|smoke)\b',
            r'\b(hate|stupid|dumb|idiot|bad words)\b'
        ]
        
        # Age-appropriate topics
        self.age_appropriate_topics = {
            "toddler": [
                "animals", "colors", "shapes", "family", "toys", "food", 
                "simple stories", "nursery rhymes", "counting", "letters"
            ],
            "child": [
                "school", "friends", "science", "nature", "books", "games",
                "sports", "art", "music", "history", "geography", "math"
            ],
            "preteen": [
                "homework", "hobbies", "technology", "environment", "cultures",
                "achievements", "goals", "creativity", "problem-solving"
            ]
        }
        
        logger.info("Safety Agent initialized")
    
    async def check_content_safety(self, content: str, age: int, content_type: str = "general") -> Dict[str, Any]:
        """Check if content is safe for the given age, with context-aware filtering"""
        try:
            safety_result = {
                "is_safe": True,
                "reason": "",
                "suggested_alternative": "",
                "confidence": 1.0
            }
            
            # For story narration and educational content, use more lenient filtering
            if content_type in ["story", "story_narration", "educational"]:
                # Only check for truly inappropriate content, not educational story elements
                strict_patterns = [
                    r'\b(sexual|romantic|inappropriate|adult content)\b',
                    r'\b(weapon|gun|knife|sword|bomb)\b',
                    r'\b(drug|alcohol|cigarette|smoke)\b',
                    r'\b(hate|stupid|dumb|idiot|bad words)\b'
                ]
                
                content_lower = content.lower()
                for pattern in strict_patterns:
                    if re.search(pattern, content_lower):
                        safety_result["is_safe"] = False
                        safety_result["reason"] = f"Content contains inappropriate material for age {age}"
                        safety_result["suggested_alternative"] = self._get_alternative_topic(age)
                        safety_result["confidence"] = 0.9
                        break
                        
                logger.info(f"Story content safety check passed for age {age}")
                return safety_result
            
            # For general content, use full filtering
            content_lower = content.lower()
            
            for pattern in self.inappropriate_patterns:
                if re.search(pattern, content_lower):
                    safety_result["is_safe"] = False
                    safety_result["reason"] = f"Content contains inappropriate material for age {age}"
                    safety_result["suggested_alternative"] = self._get_alternative_topic(age)
                    safety_result["confidence"] = 0.9
                    break
            
            # Age-specific checks
            if safety_result["is_safe"]:
                age_group = self._get_age_group(age)
                safety_result = await self._check_age_appropriateness(content, age_group, safety_result)
            
            return safety_result
            
        except Exception as e:
            logger.error(f"Error checking content safety: {str(e)}")
            return {"is_safe": False, "reason": "Safety check failed", "suggested_alternative": "Let's talk about animals!", "confidence": 0.5}
    
    async def _check_age_appropriateness(self, content: str, age_group: str, safety_result: Dict[str, Any]) -> Dict[str, Any]:
        """Check if content is appropriate for age group"""
        content_lower = content.lower()
        
        # Complex topic patterns for different age groups
        complex_patterns = {
            "toddler": [
                r'\b(complex|complicated|difficult|advanced)\b',
                r'\b(chemistry|physics|biology|calculus)\b',
                r'\b(politics|government|election|voting)\b'
            ],
            "child": [
                r'\b(quantum|molecular|cellular|atomic)\b',
                r'\b(philosophical|existential|metaphysical)\b',
                r'\b(advanced mathematics|calculus|trigonometry)\b'
            ]
        }
        
        patterns = complex_patterns.get(age_group, [])
        
        for pattern in patterns:
            if re.search(pattern, content_lower):
                safety_result["is_safe"] = False
                safety_result["reason"] = f"Content too advanced for {age_group}"
                safety_result["suggested_alternative"] = self._get_alternative_topic_by_age_group(age_group)
                safety_result["confidence"] = 0.8
                break
        
        return safety_result
    
    def _get_age_group(self, age: int) -> str:
        """Determine age group category"""
        if age <= 5:
            return "toddler"
        elif age <= 9:
            return "child"
        else:
            return "preteen"
    
    def _get_alternative_topic(self, age: int) -> str:
        """Get alternative topic suggestion"""
        age_group = self._get_age_group(age)
        return self._get_alternative_topic_by_age_group(age_group)
    
    def _get_alternative_topic_by_age_group(self, age_group: str) -> str:
        """Get alternative topic by age group"""
        alternatives = {
            "toddler": "How about we talk about your favorite animals or colors?",
            "child": "Let's talk about something fun like science facts or your favorite books!",
            "preteen": "How about we discuss your hobbies or something you're learning in school?"
        }
        
        return alternatives.get(age_group, "Let's talk about something fun!")
    
    async def moderate_response(self, response: str, age: int) -> Dict[str, Any]:
        """Moderate AI response before sending to user"""
        try:
            # Check response safety
            safety_result = await self.check_content_safety(response, age)
            
            if not safety_result["is_safe"]:
                # Replace with safe alternative
                safe_response = self._generate_safe_response(age)
                return {
                    "response": safe_response,
                    "was_modified": True,
                    "original_flagged": True,
                    "reason": safety_result["reason"]
                }
            
            # Response is safe
            return {
                "response": response,
                "was_modified": False,
                "original_flagged": False,
                "reason": ""
            }
            
        except Exception as e:
            logger.error(f"Error moderating response: {str(e)}")
            return {
                "response": self._generate_safe_response(age),
                "was_modified": True,
                "original_flagged": True,
                "reason": "Moderation error occurred"
            }
    
    def _generate_safe_response(self, age: int) -> str:
        """Generate safe response when content is flagged"""
        age_group = self._get_age_group(age)
        
        safe_responses = {
            "toddler": "That's a great question! Let's talk about something fun like animals or colors!",
            "child": "Interesting! How about we explore some cool science facts or talk about your favorite activities?",
            "preteen": "That's a thoughtful question! Let's discuss something engaging like your interests or school projects!"
        }
        
        return safe_responses.get(age_group, "Let's talk about something fun and interesting!")
    
    async def get_safety_report(self, session_id: str) -> Dict[str, Any]:
        """Get safety report for a session"""
        # This would typically query the database for safety incidents
        return {
            "session_id": session_id,
            "total_interactions": 0,
            "flagged_content": 0,
            "safety_score": 1.0,
            "last_updated": "2024-01-01T00:00:00Z"
        }