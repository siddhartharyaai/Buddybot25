"""
Content Agent - Manages content library and suggestions
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import random

logger = logging.getLogger(__name__)

class ContentAgent:
    """Manages content library and provides content suggestions"""
    
    def __init__(self, db):
        self.db = db
        self.content_types = {
            "story": "stories",
            "song": "songs", 
            "rhyme": "nursery_rhymes",
            "game": "games",
            "educational": "educational_content"
        }
        
        logger.info("Content Agent initialized")
    
    async def enhance_response(self, response: str, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance response with relevant content"""
        try:
            age = user_profile.get('age', 5)
            
            # Analyze if response needs content enhancement
            content_type = self._analyze_content_need(response)
            
            enhanced_response = {
                "text": response,
                "content_type": "conversation",
                "metadata": {}
            }
            
            if content_type:
                # Get relevant content
                content = await self.get_content_by_type(content_type, user_profile)
                
                if content:
                    enhanced_response["content_type"] = content_type
                    enhanced_response["metadata"] = {
                        "suggested_content": content,
                        "content_source": "library"
                    }
            
            return enhanced_response
            
        except Exception as e:
            logger.error(f"Error enhancing response: {str(e)}")
            return {"text": response, "content_type": "conversation", "metadata": {}}
    
    def _analyze_content_need(self, response: str) -> Optional[str]:
        """Analyze if response needs specific content type"""
        response_lower = response.lower()
        
        # Keywords that suggest content types
        content_keywords = {
            "story": ["story", "tale", "once upon", "adventure", "character"],
            "song": ["song", "sing", "music", "melody", "tune"],
            "rhyme": ["rhyme", "nursery", "poem", "verse"],
            "game": ["game", "play", "activity", "puzzle", "quiz"],
            "educational": ["learn", "teach", "explain", "lesson", "question"]
        }
        
        for content_type, keywords in content_keywords.items():
            if any(keyword in response_lower for keyword in keywords):
                return content_type
        
        return None
    
    async def get_content_by_type(self, content_type: str, user_profile: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get content by type for user profile"""
        try:
            collection_name = self.content_types.get(content_type)
            if not collection_name:
                return None
            
            age = user_profile.get('age', 5)
            age_group = self._get_age_group(age)
            
            # Query database for appropriate content
            collection = getattr(self.db, collection_name)
            
            query = {
                "age_group": age_group,
                "language": "english"  # MVP focuses on English
            }
            
            content_items = await collection.find(query).to_list(length=10)
            
            if content_items:
                # Select random content
                selected_content = random.choice(content_items)
                return {
                    "id": str(selected_content["_id"]),
                    "title": selected_content.get("title", ""),
                    "content": selected_content.get("content", ""),
                    "audio_base64": selected_content.get("audio_base64", ""),
                    "metadata": selected_content.get("metadata", {})
                }
            
            # If no content found, return default content
            return await self._get_default_content(content_type, age_group)
            
        except Exception as e:
            logger.error(f"Error getting content: {str(e)}")
            return None
    
    async def _get_default_content(self, content_type: str, age_group: str) -> Dict[str, Any]:
        """Get default content when database is empty"""
        default_content = {
            "story": {
                "toddler": {
                    "title": "The Happy Little Bear",
                    "content": "Once there was a little bear who loved to play. He played with his friends every day in the forest. The end!"
                },
                "child": {
                    "title": "The Brave Little Mouse",
                    "content": "A small mouse lived in a big house. One day, he helped his family by being very brave and clever. Everyone was proud of him!"
                },
                "preteen": {
                    "title": "The Young Explorer",
                    "content": "Maya loved exploring nature. She discovered a hidden cave with beautiful crystals and learned about geology. Her curiosity led to amazing discoveries!"
                }
            },
            "song": {
                "toddler": {
                    "title": "Twinkle Twinkle Little Star",
                    "content": "Twinkle, twinkle, little star, How I wonder what you are! Up above the world so high, Like a diamond in the sky!"
                },
                "child": {
                    "title": "If You're Happy and You Know It",
                    "content": "If you're happy and you know it, clap your hands! If you're happy and you know it, clap your hands!"
                },
                "preteen": {
                    "title": "This Old Man",
                    "content": "This old man, he played one, He played knick-knack on my thumb, With a knick-knack paddy whack, Give a dog a bone!"
                }
            },
            "rhyme": {
                "toddler": {
                    "title": "Humpty Dumpty",
                    "content": "Humpty Dumpty sat on a wall, Humpty Dumpty had a great fall!"
                },
                "child": {
                    "title": "Mary Had a Little Lamb",
                    "content": "Mary had a little lamb, Its fleece was white as snow!"
                },
                "preteen": {
                    "title": "Jack and Jill",
                    "content": "Jack and Jill went up the hill, To fetch a pail of water!"
                }
            }
        }
        
        content = default_content.get(content_type, {}).get(age_group, {})
        return {
            "id": f"default_{content_type}_{age_group}",
            "title": content.get("title", "Default Content"),
            "content": content.get("content", "Default content for this age group."),
            "audio_base64": "",
            "metadata": {"source": "default", "type": content_type}
        }
    
    def _get_age_group(self, age: int) -> str:
        """Determine age group category"""
        if age <= 5:
            return "toddler"
        elif age <= 9:
            return "child"
        else:
            return "preteen"
    
    async def get_content_suggestions(self, user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get content suggestions for user"""
        try:
            age_group = self._get_age_group(user_profile.get('age', 5))
            suggestions = []
            
            # Get suggestions from each content type
            for content_type in self.content_types.keys():
                content = await self.get_content_by_type(content_type, user_profile)
                if content:
                    suggestions.append({
                        "type": content_type,
                        "title": content["title"],
                        "description": f"A {content_type} perfect for your age!",
                        "content_id": content["id"]
                    })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting content suggestions: {str(e)}")
            return []