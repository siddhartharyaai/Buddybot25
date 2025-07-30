"""
Memory Agent - Handles long-term memory and memory snapshots
"""
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from emergentintegrations.llm.chat import LlmChat, UserMessage
import json

logger = logging.getLogger(__name__)

class MemoryAgent:
    """Handles long-term memory and daily memory snapshots"""
    
    def __init__(self, db, gemini_api_key: str):
        self.db = db
        self.gemini_api_key = gemini_api_key
        self.session_memories = {}  # session_id -> memory_data
        
        # Memory categories
        self.memory_categories = {
            "preferences": {
                "favorite_activities": [],
                "favorite_stories": [],
                "favorite_games": [],
                "favorite_songs": [],
                "dislikes": []
            },
            "personality_traits": {
                "communication_style": "friendly",
                "energy_levels": "medium",
                "emotional_patterns": [],
                "learning_preferences": []
            },
            "relationships": {
                "family_members": [],
                "friends": [],
                "pets": [],
                "important_people": []
            },
            "achievements": {
                "completed_games": [],
                "learned_skills": [],
                "milestones": [],
                "progress_tracking": {}
            },
            "interests_evolution": {
                "current_interests": [],
                "emerging_interests": [],
                "declining_interests": [],
                "seasonal_interests": []
            }
        }
        
        logger.info("Memory Agent initialized")
    
    async def update_session_memory(self, session_id: str, interaction_data: Dict[str, Any]) -> None:
        """Update session memory with new interaction"""
        try:
            if session_id not in self.session_memories:
                self.session_memories[session_id] = {
                    "interactions": [],
                    "session_start": datetime.utcnow(),
                    "total_interactions": 0,
                    "emotional_patterns": [],
                    "topics_discussed": [],
                    "preferences_discovered": {},
                    "achievements": []
                }
            
            session_memory = self.session_memories[session_id]
            
            # Add interaction
            session_memory["interactions"].append({
                "timestamp": datetime.utcnow(),
                "user_input": interaction_data.get("user_input", ""),
                "ai_response": interaction_data.get("ai_response", ""),
                "emotional_state": interaction_data.get("emotional_state", {}),
                "dialogue_mode": interaction_data.get("dialogue_mode", "chat"),
                "content_type": interaction_data.get("content_type", "conversation")
            })
            
            session_memory["total_interactions"] += 1
            
            # Extract and update patterns
            await self._extract_session_patterns(session_id, interaction_data)
            
        except Exception as e:
            logger.error(f"Error updating session memory: {str(e)}")
    
    async def _extract_session_patterns(self, session_id: str, interaction_data: Dict[str, Any]) -> None:
        """Extract patterns from interaction data"""
        try:
            session_memory = self.session_memories[session_id]
            
            # Extract emotional patterns
            emotional_state = interaction_data.get("emotional_state", {})
            if emotional_state:
                session_memory["emotional_patterns"].append({
                    "timestamp": datetime.utcnow(),
                    "mood": emotional_state.get("mood", "neutral"),
                    "energy_level": emotional_state.get("energy_level", "medium"),
                    "sentiment": emotional_state.get("sentiment", "neutral")
                })
            
            # Extract topics discussed
            user_input = interaction_data.get("user_input", "").lower()
            ai_response = interaction_data.get("ai_response", "").lower()
            
            # Simple topic extraction
            topics = self._extract_topics(user_input + " " + ai_response)
            session_memory["topics_discussed"].extend(topics)
            
            # Extract preferences
            preferences = self._extract_preferences(user_input, ai_response)
            session_memory["preferences_discovered"].update(preferences)
            
            # Extract achievements
            achievements = self._extract_achievements(interaction_data)
            session_memory["achievements"].extend(achievements)
            
        except Exception as e:
            logger.error(f"Error extracting session patterns: {str(e)}")
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract topics from text"""
        
        topic_keywords = {
            "animals": ["dog", "cat", "bird", "fish", "lion", "tiger", "elephant", "bear", "rabbit", "horse"],
            "colors": ["red", "blue", "green", "yellow", "purple", "orange", "pink", "brown", "black", "white"],
            "family": ["mom", "dad", "sister", "brother", "grandma", "grandpa", "uncle", "aunt", "cousin"],
            "school": ["school", "teacher", "friend", "class", "homework", "study", "learn", "book", "pencil"],
            "food": ["apple", "banana", "cookie", "pizza", "cake", "ice cream", "sandwich", "juice", "milk"],
            "activities": ["play", "game", "story", "song", "dance", "draw", "paint", "run", "jump", "swim"],
            "emotions": ["happy", "sad", "angry", "excited", "tired", "scared", "surprised", "confused"],
            "nature": ["tree", "flower", "sun", "moon", "star", "rain", "snow", "ocean", "mountain", "forest"]
        }
        
        detected_topics = []
        for topic, keywords in topic_keywords.items():
            if any(keyword in text for keyword in keywords):
                detected_topics.append(topic)
        
        return detected_topics
    
    def _extract_preferences(self, user_input: str, ai_response: str) -> Dict[str, Any]:
        """Extract user preferences from conversation"""
        
        preferences = {}
        
        # Extract likes
        like_patterns = ["i like", "i love", "my favorite", "i enjoy", "i want", "i prefer"]
        for pattern in like_patterns:
            if pattern in user_input:
                # Extract what they like
                parts = user_input.split(pattern, 1)
                if len(parts) > 1:
                    preference = parts[1].strip().split()[0:3]  # First few words
                    preferences[f"likes_{pattern.replace(' ', '_')}"] = " ".join(preference)
        
        # Extract dislikes
        dislike_patterns = ["i don't like", "i hate", "i don't want", "boring", "not fun"]
        for pattern in dislike_patterns:
            if pattern in user_input:
                parts = user_input.split(pattern, 1)
                if len(parts) > 1:
                    preference = parts[1].strip().split()[0:3]
                    preferences[f"dislikes_{pattern.replace(' ', '_')}"] = " ".join(preference)
        
        return preferences
    
    def _extract_achievements(self, interaction_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract achievements from interaction"""
        
        achievements = []
        
        # Check for game completions
        if interaction_data.get("content_type") == "game_end":
            metadata = interaction_data.get("metadata", {})
            if metadata.get("final_score", 0) > 0:
                achievements.append({
                    "type": "game_completion",
                    "game_type": metadata.get("game_type", "unknown"),
                    "score": metadata.get("final_score", 0),
                    "timestamp": datetime.utcnow()
                })
        
        # Check for learning milestones
        dialogue_mode = interaction_data.get("dialogue_mode", "")
        if dialogue_mode == "teaching":
            achievements.append({
                "type": "learning_interaction",
                "topic": "teaching_session",
                "timestamp": datetime.utcnow()
            })
        
        return achievements
    
    async def generate_daily_memory_snapshot(self, user_id: str) -> Dict[str, Any]:
        """Generate daily memory snapshot for a user"""
        try:
            # Get all conversations from today
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            
            conversations = await self.db.conversations.find({
                "user_id": user_id,
                "timestamp": {"$gte": today_start, "$lt": today_end}
            }).to_list(length=None)
            
            if not conversations:
                return {"user_id": user_id, "date": today_start.date(), "summary": "No interactions today"}
            
            # Analyze conversations using Gemini
            conversation_summary = await self._analyze_conversations_with_gemini(conversations)
            
            # Extract key insights
            insights = await self._extract_daily_insights(conversations)
            
            # Create memory snapshot
            memory_snapshot = {
                "user_id": user_id,
                "date": today_start.date(),
                "total_interactions": len(conversations),
                "summary": conversation_summary,
                "insights": insights,
                "mood_patterns": self._analyze_mood_patterns(conversations),
                "topics_discussed": self._analyze_topics_discussed(conversations),
                "preferences_discovered": self._analyze_preferences_discovered(conversations),
                "achievements": self._analyze_achievements(conversations),
                "engagement_metrics": self._calculate_engagement_metrics(conversations),
                "parent_summary": self._generate_parent_summary(conversation_summary, insights),
                "created_at": datetime.utcnow()
            }
            
            # Store in database
            await self.db.memory_snapshots.insert_one(memory_snapshot)
            
            # Update user profile with new insights
            await self._update_user_profile_with_insights(user_id, insights)
            
            return memory_snapshot
            
        except Exception as e:
            logger.error(f"Error generating daily memory snapshot: {str(e)}")
            return {"user_id": user_id, "error": str(e)}
    
    async def _analyze_conversations_with_gemini(self, conversations: List[Dict[str, Any]]) -> str:
        """Analyze conversations using Gemini to create summary"""
        try:
            # Prepare conversation text
            conversation_text = ""
            for conv in conversations:
                conversation_text += f"User: {conv.get('user_input', '')}\n"
                conversation_text += f"AI: {conv.get('ai_response', '')}\n\n"
            
            # Limit text length
            if len(conversation_text) > 5000:
                conversation_text = conversation_text[:5000] + "..."
            
            system_prompt = """
            You are analyzing a child's conversations with an AI companion. Create a brief, warm summary of the day's interactions.
            
            Focus on:
            - Main topics discussed
            - Child's mood and energy
            - Learning moments
            - Preferences shown
            - Notable achievements or milestones
            
            Write in a friendly, parent-appropriate tone. Keep it concise but informative.
            """
            
            chat = LlmChat(
                api_key=self.gemini_api_key,
                system_message=system_prompt
            ).with_model("gemini", "gemini-2.0-flash").with_max_tokens(300)
            
            user_message = UserMessage(text=f"Today's conversations:\n\n{conversation_text}")
            response = await chat.send_message(user_message)
            
            return response
            
        except Exception as e:
            logger.error(f"Error analyzing conversations with Gemini: {str(e)}")
            return "Unable to generate conversation summary"
    
    async def _extract_daily_insights(self, conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract key insights from daily conversations"""
        
        insights = {
            "dominant_mood": "neutral",
            "energy_trend": "stable",
            "favorite_topics": [],
            "new_interests": [],
            "learning_progress": [],
            "social_mentions": [],
            "emotional_growth": []
        }
        
        # Analyze mood patterns
        moods = []
        for conv in conversations:
            emotional_state = conv.get("emotional_state", {})
            if emotional_state:
                moods.append(emotional_state.get("mood", "neutral"))
        
        if moods:
            insights["dominant_mood"] = max(set(moods), key=moods.count)
        
        # Analyze topics
        all_topics = []
        for conv in conversations:
            user_input = conv.get("user_input", "")
            ai_response = conv.get("ai_response", "")
            topics = self._extract_topics(user_input + " " + ai_response)
            all_topics.extend(topics)
        
        if all_topics:
            topic_counts = {}
            for topic in all_topics:
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
            
            insights["favorite_topics"] = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return insights
    
    def _analyze_mood_patterns(self, conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze mood patterns from conversations"""
        
        mood_timeline = []
        for conv in conversations:
            emotional_state = conv.get("emotional_state", {})
            if emotional_state:
                mood_timeline.append({
                    "timestamp": conv.get("timestamp"),
                    "mood": emotional_state.get("mood", "neutral"),
                    "energy": emotional_state.get("energy_level", "medium"),
                    "sentiment": emotional_state.get("sentiment", "neutral")
                })
        
        return {
            "mood_timeline": mood_timeline,
            "total_moods": len(mood_timeline),
            "mood_distribution": self._calculate_mood_distribution(mood_timeline)
        }
    
    def _analyze_topics_discussed(self, conversations: List[Dict[str, Any]]) -> List[str]:
        """Analyze topics discussed throughout the day"""
        
        all_topics = []
        for conv in conversations:
            user_input = conv.get("user_input", "")
            ai_response = conv.get("ai_response", "")
            topics = self._extract_topics(user_input + " " + ai_response)
            all_topics.extend(topics)
        
        # Remove duplicates and return
        return list(set(all_topics))
    
    def _analyze_preferences_discovered(self, conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze preferences discovered during conversations"""
        
        all_preferences = {}
        for conv in conversations:
            user_input = conv.get("user_input", "")
            ai_response = conv.get("ai_response", "")
            preferences = self._extract_preferences(user_input, ai_response)
            all_preferences.update(preferences)
        
        return all_preferences
    
    def _analyze_achievements(self, conversations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze achievements from conversations"""
        
        achievements = []
        for conv in conversations:
            conv_achievements = self._extract_achievements(conv)
            achievements.extend(conv_achievements)
        
        return achievements
    
    def _calculate_engagement_metrics(self, conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate engagement metrics"""
        
        total_interactions = len(conversations)
        total_duration = 0
        
        if total_interactions > 0:
            first_interaction = conversations[0].get("timestamp")
            last_interaction = conversations[-1].get("timestamp")
            
            if first_interaction and last_interaction:
                total_duration = (last_interaction - first_interaction).total_seconds() / 60  # minutes
        
        return {
            "total_interactions": total_interactions,
            "session_duration_minutes": total_duration,
            "average_interaction_length": total_duration / total_interactions if total_interactions > 0 else 0,
            "engagement_score": min(total_interactions / 10, 1.0)  # Normalized score
        }
    
    def _generate_parent_summary(self, conversation_summary: str, insights: Dict[str, Any]) -> str:
        """Generate parent-friendly summary"""
        
        dominant_mood = insights.get("dominant_mood", "neutral")
        favorite_topics = insights.get("favorite_topics", [])
        
        summary = f"Today your child was mostly {dominant_mood} during conversations with Buddy. "
        
        if favorite_topics:
            topics_str = ", ".join([topic[0] for topic in favorite_topics[:2]])
            summary += f"They showed particular interest in {topics_str}. "
        
        summary += "All interactions were safe and age-appropriate."
        
        return summary
    
    def _calculate_mood_distribution(self, mood_timeline: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate mood distribution"""
        
        mood_counts = {}
        for mood_entry in mood_timeline:
            mood = mood_entry.get("mood", "neutral")
            mood_counts[mood] = mood_counts.get(mood, 0) + 1
        
        return mood_counts
    
    async def _update_user_profile_with_insights(self, user_id: str, insights: Dict[str, Any]) -> None:
        """Update user profile with daily insights"""
        try:
            # Get current profile
            profile = await self.db.user_profiles.find_one({"id": user_id})
            if not profile:
                return
            
            # Update interests based on favorite topics
            favorite_topics = insights.get("favorite_topics", [])
            current_interests = profile.get("interests", [])
            
            # Add new interests
            for topic, count in favorite_topics:
                if topic not in current_interests and count > 2:  # Mentioned more than twice
                    current_interests.append(topic)
            
            # Update profile
            await self.db.user_profiles.update_one(
                {"id": user_id},
                {"$set": {"interests": current_interests, "updated_at": datetime.utcnow()}}
            )
            
        except Exception as e:
            logger.error(f"Error updating user profile with insights: {str(e)}")
    
    async def get_user_memory_context(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """Get user memory context for the last N days"""
        try:
            # Get memory snapshots from last N days
            start_date = datetime.utcnow() - timedelta(days=days)
            
            snapshots = await self.db.memory_snapshots.find({
                "user_id": user_id,
                "created_at": {"$gte": start_date}
            }).sort("created_at", -1).to_list(length=days)
            
            if not snapshots:
                return {"user_id": user_id, "memory_context": "No recent memory available"}
            
            # Compile memory context
            memory_context = {
                "recent_preferences": {},
                "personality_insights": {},
                "favorite_topics": [],
                "achievements": [],
                "mood_patterns": []
            }
            
            for snapshot in snapshots:
                insights = snapshot.get("insights", {})
                
                # Aggregate preferences
                preferences = snapshot.get("preferences_discovered", {})
                memory_context["recent_preferences"].update(preferences)
                
                # Aggregate favorite topics
                favorite_topics = insights.get("favorite_topics", [])
                memory_context["favorite_topics"].extend(favorite_topics)
                
                # Aggregate achievements
                achievements = snapshot.get("achievements", [])
                memory_context["achievements"].extend(achievements)
                
                # Aggregate mood patterns
                mood_patterns = snapshot.get("mood_patterns", {})
                memory_context["mood_patterns"].append(mood_patterns)
            
            return memory_context
            
        except Exception as e:
            logger.error(f"Error getting user memory context: {str(e)}")
            return {"user_id": user_id, "error": str(e)}
    
    async def cleanup_old_memories(self, days_to_keep: int = 30) -> None:
        """Clean up old memory snapshots"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            
            result = await self.db.memory_snapshots.delete_many({
                "created_at": {"$lt": cutoff_date}
            })
            
            logger.info(f"Cleaned up {result.deleted_count} old memory snapshots")
            
        except Exception as e:
            logger.error(f"Error cleaning up old memories: {str(e)}")
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        
        return {
            "active_sessions": len(self.session_memories),
            "memory_categories": list(self.memory_categories.keys()),
            "total_memory_categories": len(self.memory_categories)
        }