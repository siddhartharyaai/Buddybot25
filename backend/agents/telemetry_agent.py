"""
Telemetry Agent - Handles usage analytics, flags, and A/B testing
"""
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json
import uuid

logger = logging.getLogger(__name__)

class TelemetryAgent:
    """Handles telemetry, flags, and A/B testing"""
    
    def __init__(self, db):
        self.db = db
        self.session_telemetry = {}  # session_id -> telemetry_data
        
        # Default flags for A/B testing and feature toggles
        self.default_flags = {
            "emoji_usage": True,
            "hinglish_enabled": True,
            "advanced_games": True,
            "story_generation": True,
            "emotional_responses": True,
            "prosody_enabled": True,
            "memory_snapshots": True,
            "parent_notifications": True,
            "voice_interruption": True,
            "cultural_adaptation": True,
            "game_difficulty_adaptive": True,
            "repair_suggestions": True,
            "ambient_listening": True,
            "wake_word_customization": False,
            "multi_language_support": False,
            "video_content": False,
            "voice_cloning": False,
            "advanced_analytics": False
        }
        
        # Telemetry event types
        self.event_types = {
            "session_start": "user_session_started",
            "session_end": "user_session_ended",
            "conversation": "conversation_interaction",
            "voice_interaction": "voice_message_processed",
            "game_started": "micro_game_started",
            "game_completed": "micro_game_completed",
            "story_requested": "story_content_requested",
            "song_requested": "song_content_requested",
            "repair_triggered": "conversation_repair_triggered",
            "emotion_detected": "emotion_state_detected",
            "wake_word_detected": "wake_word_activation",
            "safety_violation": "safety_filter_activated",
            "error_occurred": "system_error_logged",
            "parent_dashboard_access": "parent_dashboard_opened",
            "profile_updated": "user_profile_modified",
            "content_suggestion": "content_recommendation_shown",
            "engagement_drop": "user_engagement_decreased",
            "feature_used": "feature_utilization_tracked"
        }
        
        logger.info("Telemetry Agent initialized")
    
    async def track_event(self, event_type: str, user_id: str, session_id: str, event_data: Dict[str, Any]) -> None:
        """Track a telemetry event"""
        try:
            # Validate event type
            if event_type not in self.event_types.values():
                logger.warning(f"Unknown event type: {event_type}")
            
            # Create telemetry event
            telemetry_event = {
                "event_id": str(uuid.uuid4()),
                "event_type": event_type,
                "user_id": user_id,
                "session_id": session_id,
                "timestamp": datetime.utcnow(),
                "event_data": event_data,
                "client_info": {
                    "user_agent": event_data.get("user_agent", "unknown"),
                    "platform": event_data.get("platform", "web"),
                    "version": event_data.get("version", "1.0.0")
                }
            }
            
            # Store in database
            await self.db.telemetry_events.insert_one(telemetry_event)
            
            # Update session telemetry
            await self._update_session_telemetry(session_id, event_type, event_data)
            
            # Update daily telemetry for user
            await self._update_daily_telemetry(user_id, event_type, event_data)
            
        except Exception as e:
            logger.error(f"Error tracking event: {str(e)}")
    
    async def _update_session_telemetry(self, session_id: str, event_type: str, event_data: Dict[str, Any]) -> None:
        """Update session-level telemetry"""
        try:
            if session_id not in self.session_telemetry:
                self.session_telemetry[session_id] = {
                    "session_id": session_id,
                    "start_time": datetime.utcnow(),
                    "event_count": 0,
                    "event_types": {},
                    "total_interactions": 0,
                    "voice_interactions": 0,
                    "games_played": 0,
                    "stories_requested": 0,
                    "songs_requested": 0,
                    "emotions_detected": [],
                    "wake_word_activations": 0,
                    "repair_triggers": 0,
                    "safety_violations": 0,
                    "errors": 0,
                    "engagement_score": 0.0,
                    "session_duration": 0
                }
            
            session_data = self.session_telemetry[session_id]
            session_data["event_count"] += 1
            session_data["event_types"][event_type] = session_data["event_types"].get(event_type, 0) + 1
            
            # Update specific counters
            if event_type == "conversation_interaction":
                session_data["total_interactions"] += 1
            elif event_type == "voice_message_processed":
                session_data["voice_interactions"] += 1
            elif event_type == "micro_game_started":
                session_data["games_played"] += 1
            elif event_type == "story_content_requested":
                session_data["stories_requested"] += 1
            elif event_type == "song_content_requested":
                session_data["songs_requested"] += 1
            elif event_type == "emotion_state_detected":
                emotion_data = event_data.get("emotional_state", {})
                session_data["emotions_detected"].append(emotion_data)
            elif event_type == "wake_word_activation":
                session_data["wake_word_activations"] += 1
            elif event_type == "conversation_repair_triggered":
                session_data["repair_triggers"] += 1
            elif event_type == "safety_filter_activated":
                session_data["safety_violations"] += 1
            elif event_type == "system_error_logged":
                session_data["errors"] += 1
            
            # Update session duration
            session_data["session_duration"] = (datetime.utcnow() - session_data["start_time"]).total_seconds()
            
            # Calculate engagement score
            session_data["engagement_score"] = self._calculate_engagement_score(session_data)
            
        except Exception as e:
            logger.error(f"Error updating session telemetry: {str(e)}")
    
    async def _update_daily_telemetry(self, user_id: str, event_type: str, event_data: Dict[str, Any]) -> None:
        """Update daily telemetry for user"""
        try:
            today = datetime.utcnow().date()
            
            # Get or create daily telemetry record
            daily_record = await self.db.daily_telemetry.find_one({
                "user_id": user_id,
                "date": today
            })
            
            if not daily_record:
                daily_record = {
                    "user_id": user_id,
                    "date": today,
                    "total_events": 0,
                    "event_breakdown": {},
                    "total_interactions": 0,
                    "voice_interactions": 0,
                    "games_played": 0,
                    "stories_requested": 0,
                    "songs_requested": 0,
                    "wake_word_activations": 0,
                    "repair_triggers": 0,
                    "safety_violations": 0,
                    "errors": 0,
                    "session_count": 0,
                    "total_session_duration": 0,
                    "average_engagement": 0.0,
                    "feature_usage": {},
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            
            # Update counters
            daily_record["total_events"] += 1
            daily_record["event_breakdown"][event_type] = daily_record["event_breakdown"].get(event_type, 0) + 1
            daily_record["updated_at"] = datetime.utcnow()
            
            # Update specific metrics
            if event_type == "conversation_interaction":
                daily_record["total_interactions"] += 1
            elif event_type == "voice_message_processed":
                daily_record["voice_interactions"] += 1
            elif event_type == "micro_game_started":
                daily_record["games_played"] += 1
            elif event_type == "story_content_requested":
                daily_record["stories_requested"] += 1
            elif event_type == "song_content_requested":
                daily_record["songs_requested"] += 1
            elif event_type == "wake_word_activation":
                daily_record["wake_word_activations"] += 1
            elif event_type == "conversation_repair_triggered":
                daily_record["repair_triggers"] += 1
            elif event_type == "safety_filter_activated":
                daily_record["safety_violations"] += 1
            elif event_type == "system_error_logged":
                daily_record["errors"] += 1
            elif event_type == "user_session_started":
                daily_record["session_count"] += 1
            
            # Update feature usage
            feature_name = event_data.get("feature_name")
            if feature_name:
                daily_record["feature_usage"][feature_name] = daily_record["feature_usage"].get(feature_name, 0) + 1
            
            # Upsert daily record
            await self.db.daily_telemetry.replace_one(
                {"user_id": user_id, "date": today},
                daily_record,
                upsert=True
            )
            
        except Exception as e:
            logger.error(f"Error updating daily telemetry: {str(e)}")
    
    def _calculate_engagement_score(self, session_data: Dict[str, Any]) -> float:
        """Calculate engagement score for a session"""
        try:
            # Base score from interactions
            interactions = session_data.get("total_interactions", 0)
            base_score = min(interactions / 10, 1.0)  # Normalized to 1.0
            
            # Bonus for voice interactions
            voice_bonus = min(session_data.get("voice_interactions", 0) / 5, 0.2)
            
            # Bonus for games played
            game_bonus = min(session_data.get("games_played", 0) / 3, 0.15)
            
            # Bonus for content requested
            content_bonus = min((session_data.get("stories_requested", 0) + session_data.get("songs_requested", 0)) / 2, 0.1)
            
            # Penalty for errors and safety violations
            error_penalty = min(session_data.get("errors", 0) * 0.05, 0.2)
            safety_penalty = min(session_data.get("safety_violations", 0) * 0.1, 0.3)
            
            # Calculate final score
            final_score = base_score + voice_bonus + game_bonus + content_bonus - error_penalty - safety_penalty
            
            return max(0.0, min(1.0, final_score))
            
        except Exception as e:
            logger.error(f"Error calculating engagement score: {str(e)}")
            return 0.5  # Default score
    
    async def get_user_flags(self, user_id: str) -> Dict[str, Any]:
        """Get feature flags for a user"""
        try:
            # Get user profile
            user_profile = await self.db.user_profiles.find_one({"id": user_id})
            if not user_profile:
                return self.default_flags
            
            # Get user-specific flags
            user_flags = user_profile.get("flags", {})
            
            # Merge with defaults
            merged_flags = {**self.default_flags, **user_flags}
            
            # Apply A/B testing logic
            merged_flags = await self._apply_ab_testing(user_id, merged_flags)
            
            return merged_flags
            
        except Exception as e:
            logger.error(f"Error getting user flags: {str(e)}")
            return self.default_flags
    
    async def _apply_ab_testing(self, user_id: str, flags: Dict[str, Any]) -> Dict[str, Any]:
        """Apply A/B testing logic to flags"""
        try:
            # Get A/B test configurations
            ab_tests = await self.db.ab_tests.find({"active": True}).to_list(length=None)
            
            for test in ab_tests:
                test_name = test.get("name", "")
                variants = test.get("variants", [])
                
                if not variants:
                    continue
                
                # Determine user's variant based on user_id hash
                user_hash = hash(user_id) % 100
                
                # Assign variant based on traffic allocation
                cumulative_traffic = 0
                for variant in variants:
                    traffic_percentage = variant.get("traffic_percentage", 0)
                    cumulative_traffic += traffic_percentage
                    
                    if user_hash < cumulative_traffic:
                        # Apply variant flags
                        variant_flags = variant.get("flags", {})
                        flags.update(variant_flags)
                        
                        # Track A/B test assignment
                        await self.track_event(
                            "ab_test_assignment",
                            user_id,
                            "system",
                            {
                                "test_name": test_name,
                                "variant": variant.get("name", ""),
                                "flags_applied": variant_flags
                            }
                        )
                        break
            
            return flags
            
        except Exception as e:
            logger.error(f"Error applying A/B testing: {str(e)}")
            return flags
    
    async def update_user_flags(self, user_id: str, flags: Dict[str, Any]) -> None:
        """Update user-specific flags"""
        try:
            await self.db.user_profiles.update_one(
                {"id": user_id},
                {"$set": {"flags": flags, "updated_at": datetime.utcnow()}}
            )
            
            # Track flag update
            await self.track_event(
                "feature_flags_updated",
                user_id,
                "system",
                {"updated_flags": flags}
            )
            
        except Exception as e:
            logger.error(f"Error updating user flags: {str(e)}")
    
    async def get_analytics_dashboard(self, user_id: Optional[str] = None, days: int = 7) -> Dict[str, Any]:
        """Get analytics dashboard data"""
        try:
            end_date = datetime.utcnow().date()
            start_date = end_date - timedelta(days=days)
            
            # Base query
            query = {"date": {"$gte": start_date, "$lte": end_date}}
            if user_id:
                query["user_id"] = user_id
            
            # Get daily telemetry data
            daily_data = await self.db.daily_telemetry.find(query).to_list(length=None)
            
            # Aggregate metrics
            analytics = {
                "date_range": {"start": start_date, "end": end_date},
                "total_users": len(set(record["user_id"] for record in daily_data)),
                "total_sessions": sum(record.get("session_count", 0) for record in daily_data),
                "total_interactions": sum(record.get("total_interactions", 0) for record in daily_data),
                "voice_interactions": sum(record.get("voice_interactions", 0) for record in daily_data),
                "games_played": sum(record.get("games_played", 0) for record in daily_data),
                "stories_requested": sum(record.get("stories_requested", 0) for record in daily_data),
                "songs_requested": sum(record.get("songs_requested", 0) for record in daily_data),
                "wake_word_activations": sum(record.get("wake_word_activations", 0) for record in daily_data),
                "repair_triggers": sum(record.get("repair_triggers", 0) for record in daily_data),
                "safety_violations": sum(record.get("safety_violations", 0) for record in daily_data),
                "errors": sum(record.get("errors", 0) for record in daily_data),
                "average_engagement": sum(record.get("average_engagement", 0) for record in daily_data) / len(daily_data) if daily_data else 0,
                "feature_usage": self._aggregate_feature_usage(daily_data),
                "daily_breakdown": self._create_daily_breakdown(daily_data),
                "top_features": self._get_top_features(daily_data),
                "engagement_trends": self._calculate_engagement_trends(daily_data)
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting analytics dashboard: {str(e)}")
            return {"error": str(e)}
    
    def _aggregate_feature_usage(self, daily_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """Aggregate feature usage across all days"""
        
        aggregated = {}
        for record in daily_data:
            feature_usage = record.get("feature_usage", {})
            for feature, count in feature_usage.items():
                aggregated[feature] = aggregated.get(feature, 0) + count
        
        return aggregated
    
    def _create_daily_breakdown(self, daily_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create daily breakdown of metrics"""
        
        breakdown = []
        for record in daily_data:
            breakdown.append({
                "date": record.get("date"),
                "interactions": record.get("total_interactions", 0),
                "voice_interactions": record.get("voice_interactions", 0),
                "games_played": record.get("games_played", 0),
                "engagement": record.get("average_engagement", 0),
                "sessions": record.get("session_count", 0)
            })
        
        return sorted(breakdown, key=lambda x: x["date"])
    
    def _get_top_features(self, daily_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get top used features"""
        
        feature_usage = self._aggregate_feature_usage(daily_data)
        
        top_features = []
        for feature, count in sorted(feature_usage.items(), key=lambda x: x[1], reverse=True)[:5]:
            top_features.append({
                "feature": feature,
                "usage_count": count,
                "percentage": (count / sum(feature_usage.values()) * 100) if feature_usage else 0
            })
        
        return top_features
    
    def _calculate_engagement_trends(self, daily_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate engagement trends"""
        
        if not daily_data:
            return {"trend": "no_data", "change": 0}
        
        # Sort by date
        sorted_data = sorted(daily_data, key=lambda x: x.get("date"))
        
        # Calculate trend
        engagements = [record.get("average_engagement", 0) for record in sorted_data]
        
        if len(engagements) < 2:
            return {"trend": "stable", "change": 0}
        
        # Simple trend calculation
        first_half = engagements[:len(engagements)//2]
        second_half = engagements[len(engagements)//2:]
        
        first_avg = sum(first_half) / len(first_half) if first_half else 0
        second_avg = sum(second_half) / len(second_half) if second_half else 0
        
        change = second_avg - first_avg
        
        if change > 0.1:
            trend = "increasing"
        elif change < -0.1:
            trend = "decreasing"
        else:
            trend = "stable"
        
        return {"trend": trend, "change": change}
    
    async def cleanup_old_telemetry(self, days_to_keep: int = 90) -> None:
        """Clean up old telemetry data"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            
            # Clean up telemetry events
            result1 = await self.db.telemetry_events.delete_many({
                "timestamp": {"$lt": cutoff_date}
            })
            
            # Clean up daily telemetry
            result2 = await self.db.daily_telemetry.delete_many({
                "date": {"$lt": cutoff_date.date()}
            })
            
            logger.info(f"Cleaned up {result1.deleted_count} telemetry events and {result2.deleted_count} daily telemetry records")
            
        except Exception as e:
            logger.error(f"Error cleaning up old telemetry: {str(e)}")
    
    async def end_session(self, session_id: str) -> Dict[str, Any]:
        """End a session and get final telemetry"""
        try:
            if session_id not in self.session_telemetry:
                return {"error": "Session not found"}
            
            session_data = self.session_telemetry[session_id]
            session_data["end_time"] = datetime.utcnow()
            session_data["session_duration"] = (session_data["end_time"] - session_data["start_time"]).total_seconds()
            
            # Final engagement score calculation
            session_data["engagement_score"] = self._calculate_engagement_score(session_data)
            
            # Store final session data
            await self.db.session_telemetry.insert_one(session_data)
            
            # Remove from active sessions
            final_data = self.session_telemetry.pop(session_id)
            
            return {
                "session_id": session_id,
                "duration": final_data["session_duration"],
                "interactions": final_data["total_interactions"],
                "engagement_score": final_data["engagement_score"],
                "summary": "Session ended successfully"
            }
            
        except Exception as e:
            logger.error(f"Error ending session: {str(e)}")
            return {"error": str(e)}
    
    def get_telemetry_statistics(self) -> Dict[str, Any]:
        """Get telemetry system statistics"""
        
        return {
            "active_sessions": len(self.session_telemetry),
            "event_types": len(self.event_types),
            "default_flags": len(self.default_flags),
            "tracked_events": list(self.event_types.keys())
        }