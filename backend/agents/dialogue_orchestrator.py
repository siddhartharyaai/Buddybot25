"""
Dialogue Orchestration Layer - Manages conversation modes and adaptive responses
"""
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum
import random

logger = logging.getLogger(__name__)

class DialogueMode(Enum):
    """Available dialogue modes"""
    CHAT = "chat"
    STORY = "story"
    GAME = "game"
    COACHING = "coaching"
    BEDTIME = "bedtime"
    REPAIR = "repair"
    TEACHING = "teaching"
    COMFORT = "comfort"
    CALM = "calm"

class DialogueOrchestrator:
    """Orchestrates conversation modes and adaptive responses"""
    
    def __init__(self):
        self.current_mode = DialogueMode.CHAT
        self.mode_history = []
        self.silence_threshold = 3.0  # seconds
        self.boredom_threshold = 5  # consecutive neutral responses
        self.engagement_score = 0.7  # 0.0 to 1.0
        
        # Mode transition rules
        self.mode_transitions = {
            DialogueMode.CHAT: {
                "emotional_triggers": {
                    "sad": DialogueMode.COMFORT,
                    "tired": DialogueMode.BEDTIME,
                    "confused": DialogueMode.TEACHING,
                    "angry": DialogueMode.CALM,
                    "excited": DialogueMode.GAME
                },
                "engagement_triggers": {
                    "low": DialogueMode.GAME,
                    "bored": DialogueMode.STORY
                }
            },
            DialogueMode.STORY: {
                "completion_triggers": {
                    "finished": DialogueMode.CHAT,
                    "interrupted": DialogueMode.CHAT
                }
            },
            DialogueMode.GAME: {
                "completion_triggers": {
                    "finished": DialogueMode.CHAT,
                    "lost_interest": DialogueMode.CHAT
                }
            },
            DialogueMode.COACHING: {
                "resolution_triggers": {
                    "resolved": DialogueMode.CHAT,
                    "needs_more": DialogueMode.COACHING
                }
            }
        }
        
        # Prosody settings for different modes
        self.prosody_settings = {
            DialogueMode.CHAT: {
                "tone": "friendly",
                "pace": "normal",
                "volume": "normal",
                "emphasis": "balanced"
            },
            DialogueMode.STORY: {
                "tone": "narrative",
                "pace": "slow",
                "volume": "soft",
                "emphasis": "dramatic"
            },
            DialogueMode.GAME: {
                "tone": "excited",
                "pace": "fast",
                "volume": "energetic",
                "emphasis": "playful"
            },
            DialogueMode.COACHING: {
                "tone": "supportive",
                "pace": "slow",
                "volume": "gentle",
                "emphasis": "reassuring"
            },
            DialogueMode.BEDTIME: {
                "tone": "soothing",
                "pace": "very_slow",
                "volume": "whisper",
                "emphasis": "calming"
            },
            DialogueMode.REPAIR: {
                "tone": "understanding",
                "pace": "slow",
                "volume": "normal",
                "emphasis": "clarifying"
            },
            DialogueMode.TEACHING: {
                "tone": "patient",
                "pace": "slow",
                "volume": "clear",
                "emphasis": "educational"
            },
            DialogueMode.COMFORT: {
                "tone": "warm",
                "pace": "slow",
                "volume": "soft",
                "emphasis": "nurturing"
            },
            DialogueMode.CALM: {
                "tone": "peaceful",
                "pace": "very_slow",
                "volume": "quiet",
                "emphasis": "stabilizing"
            }
        }
        
        # Token budgets for different ages and modes - INCREASED for rich content
        self.token_budgets = {
            "toddler": {"short": 200, "medium": 400, "long": 600},
            "child": {"short": 400, "medium": 800, "long": 1200},
            "preteen": {"short": 600, "medium": 1000, "long": 1600}
        }
        
        logger.info("Dialogue Orchestrator initialized")
    
    async def orchestrate_response(self, 
                                 user_input: str, 
                                 emotional_state: Dict[str, Any],
                                 user_profile: Dict[str, Any],
                                 context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Main orchestration function that determines dialogue plan"""
        try:
            # Analyze current situation
            situation_analysis = self._analyze_situation(
                user_input, emotional_state, user_profile, context
            )
            
            # Determine target mode
            target_mode = self._determine_target_mode(
                situation_analysis, emotional_state
            )
            
            # Handle mode transition
            if target_mode != self.current_mode:
                transition_plan = self._plan_mode_transition(
                    self.current_mode, target_mode
                )
            else:
                transition_plan = None
            
            # Update current mode
            self.current_mode = target_mode
            
            # Determine prosody settings
            prosody = self._get_prosody_settings(target_mode, emotional_state)
            
            # Determine token budget
            token_budget = self._determine_token_budget(
                user_profile, emotional_state, target_mode
            )
            
            # Create dialogue plan
            dialogue_plan = {
                "mode": target_mode.value,
                "prosody": prosody,
                "token_budget": token_budget,
                "transition_plan": transition_plan,
                "engagement_strategy": self._get_engagement_strategy(
                    target_mode, emotional_state, user_profile
                ),
                "cultural_context": self._get_cultural_context(user_profile),
                "response_guidelines": self._get_response_guidelines(
                    target_mode, emotional_state, user_profile
                )
            }
            
            # Update mode history
            self._update_mode_history(target_mode, emotional_state)
            
            return dialogue_plan
            
        except Exception as e:
            logger.error(f"Error in dialogue orchestration: {str(e)}")
            return self._get_default_dialogue_plan()
    
    def _analyze_situation(self, 
                          user_input: str, 
                          emotional_state: Dict[str, Any],
                          user_profile: Dict[str, Any],
                          context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze the current conversational situation"""
        
        # Check for content requests
        content_request_detected, content_type = self._detect_content_request(user_input)
        
        # Check for silence or low engagement
        silence_detected = context and context.get("silence_duration", 0) > self.silence_threshold
        
        # Check for boredom indicators
        boredom_detected = self._detect_boredom(user_input, emotional_state)
        
        # Check for interruption patterns
        interruption_detected = context and context.get("interruption", False)
        
        # Check for repair needs
        repair_needed = self._detect_repair_need(user_input, context)
        
        # Check time of day for bedtime mode
        current_hour = datetime.now().hour
        bedtime_appropriate = 19 <= current_hour <= 22  # 7 PM to 10 PM
        
        return {
            "content_request_detected": content_request_detected,
            "content_type": content_type,
            "silence_detected": silence_detected,
            "boredom_detected": boredom_detected,
            "interruption_detected": interruption_detected,
            "repair_needed": repair_needed,
            "bedtime_appropriate": bedtime_appropriate,
            "emotional_intensity": emotional_state.get("confidence", 0.5),
            "user_engagement": self._assess_user_engagement(user_input, emotional_state)
        }
    
    def _detect_content_request(self, user_input: str) -> tuple:
        """Detect if user is requesting specific content like stories, songs, etc."""
        user_input_lower = user_input.lower()
        
        # Story detection
        story_keywords = ['story', 'tale', 'tell me about', 'once upon', 'adventure', 'fairy tale']
        if any(keyword in user_input_lower for keyword in story_keywords):
            return True, "story"
        
        # Song detection
        song_keywords = ['song', 'sing', 'music', 'lullaby', 'rhyme about']
        if any(keyword in user_input_lower for keyword in song_keywords):
            return True, "song"
        
        # Riddle detection
        riddle_keywords = ['riddle', 'puzzle', 'guess', 'brain teaser']
        if any(keyword in user_input_lower for keyword in riddle_keywords):
            return True, "riddle"
        
        # Joke detection
        joke_keywords = ['joke', 'funny', 'make me laugh', 'something silly']
        if any(keyword in user_input_lower for keyword in joke_keywords):
            return True, "joke"
        
        # Rhyme/Poem detection
        rhyme_keywords = ['rhyme', 'poem', 'poetry', 'verse']
        if any(keyword in user_input_lower for keyword in rhyme_keywords):
            return True, "rhyme"
        
        # Game detection
        game_keywords = ['game', 'play', 'let\'s play', 'activity', 'something fun']
        if any(keyword in user_input_lower for keyword in game_keywords):
            return True, "game"
        
        return False, ""
    
    def _determine_target_mode(self, 
                             situation_analysis: Dict[str, Any],
                             emotional_state: Dict[str, Any]) -> DialogueMode:
        """Determine the target dialogue mode based on situation analysis"""
        
        # Priority 0: Content requests (highest priority)
        if situation_analysis.get("content_request_detected", False):
            content_type = situation_analysis.get("content_type", "")
            if content_type in ["story", "tale"]:
                return DialogueMode.STORY
            elif content_type in ["song", "rhyme", "poem"]:
                return DialogueMode.STORY  # Use STORY mode for all content with long token budget
            elif content_type in ["joke", "riddle", "game"]:
                return DialogueMode.GAME
            else:
                return DialogueMode.TEACHING  # For facts and educational content
        
        # Priority 1: Repair if needed
        if situation_analysis.get("repair_needed", False):
            return DialogueMode.REPAIR
        
        # Priority 2: Emotional needs
        mood = emotional_state.get("mood", "neutral")
        if mood in ["sad", "upset"]:
            return DialogueMode.COMFORT
        elif mood == "angry":
            return DialogueMode.CALM
        elif mood == "confused":
            return DialogueMode.TEACHING
        elif mood == "tired" and situation_analysis.get("bedtime_appropriate", False):
            return DialogueMode.BEDTIME
        
        # Priority 3: Engagement issues
        if situation_analysis.get("boredom_detected", False):
            return DialogueMode.GAME if random.random() < 0.6 else DialogueMode.STORY
        
        if situation_analysis.get("silence_detected", False):
            return DialogueMode.GAME
        
        # Priority 4: Emotional opportunities
        if mood == "excited" and emotional_state.get("energy_level") == "high":
            return DialogueMode.GAME
        
        # Default: Continue current mode or return to chat
        if self.current_mode in [DialogueMode.STORY, DialogueMode.GAME] and not situation_analysis.get("interruption_detected", False):
            return self.current_mode
        
        return DialogueMode.CHAT
    
    def _plan_mode_transition(self, 
                            current_mode: DialogueMode, 
                            target_mode: DialogueMode) -> Dict[str, Any]:
        """Plan smooth transition between modes"""
        
        transition_phrases = {
            (DialogueMode.CHAT, DialogueMode.STORY): "Let me tell you a story...",
            (DialogueMode.CHAT, DialogueMode.GAME): "Want to play a fun game?",
            (DialogueMode.CHAT, DialogueMode.COMFORT): "I can see you might need some comfort...",
            (DialogueMode.GAME, DialogueMode.CHAT): "Great job playing! What else would you like to talk about?",
            (DialogueMode.STORY, DialogueMode.CHAT): "And that's the end of our story! What did you think?",
            (DialogueMode.COMFORT, DialogueMode.CHAT): "Feeling better now? I'm here if you need me.",
            (DialogueMode.BEDTIME, DialogueMode.CHAT): "Sweet dreams! Let's chat more tomorrow.",
        }
        
        return {
            "transition_phrase": transition_phrases.get((current_mode, target_mode), ""),
            "previous_mode": current_mode.value,
            "reason": f"Transitioning from {current_mode.value} to {target_mode.value}",
            "smooth_transition": True
        }
    
    def _get_prosody_settings(self, 
                            mode: DialogueMode, 
                            emotional_state: Dict[str, Any]) -> Dict[str, Any]:
        """Get prosody settings for the current mode and emotional state"""
        
        base_prosody = self.prosody_settings.get(mode, self.prosody_settings[DialogueMode.CHAT])
        
        # Adjust based on emotional state
        energy_level = emotional_state.get("energy_level", "medium")
        
        # Adjust pace based on energy
        if energy_level == "high":
            base_prosody["pace"] = "fast" if base_prosody["pace"] == "normal" else base_prosody["pace"]
        elif energy_level == "low":
            base_prosody["pace"] = "slow" if base_prosody["pace"] == "normal" else base_prosody["pace"]
        
        # Adjust volume based on mood
        mood = emotional_state.get("mood", "neutral")
        if mood in ["sad", "tired"]:
            base_prosody["volume"] = "soft"
        elif mood == "excited":
            base_prosody["volume"] = "energetic"
        
        return base_prosody
    
    def _determine_token_budget(self, 
                               user_profile: Dict[str, Any],
                               emotional_state: Dict[str, Any],
                               mode: DialogueMode) -> int:
        """Determine appropriate token budget"""
        
        age = user_profile.get("age", 5)
        age_group = self._get_age_group(age)
        
        # Base budget by age
        budgets = self.token_budgets.get(age_group, self.token_budgets["child"])
        
        # Adjust based on mode
        if mode in [DialogueMode.STORY, DialogueMode.TEACHING]:
            return budgets["long"]
        elif mode in [DialogueMode.GAME, DialogueMode.COMFORT]:
            return budgets["medium"]
        elif mode == DialogueMode.REPAIR:
            return budgets["short"]
        
        # Adjust based on emotional state
        energy_level = emotional_state.get("energy_level", "medium")
        if energy_level == "low":
            return budgets["short"]
        elif energy_level == "high":
            return budgets["medium"]
        
        return budgets["medium"]
    
    def _get_engagement_strategy(self, 
                               mode: DialogueMode,
                               emotional_state: Dict[str, Any],
                               user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Get engagement strategy for the current mode"""
        
        strategies = {
            DialogueMode.CHAT: {
                "techniques": ["questions", "curiosity", "validation"],
                "interaction_style": "conversational",
                "follow_up_prompts": True
            },
            DialogueMode.STORY: {
                "techniques": ["narrative", "suspense", "character_voices"],
                "interaction_style": "immersive",
                "follow_up_prompts": False
            },
            DialogueMode.GAME: {
                "techniques": ["challenge", "reward", "progression"],
                "interaction_style": "interactive",
                "follow_up_prompts": True
            },
            DialogueMode.COMFORT: {
                "techniques": ["empathy", "validation", "gentle_guidance"],
                "interaction_style": "supportive",
                "follow_up_prompts": False
            },
            DialogueMode.BEDTIME: {
                "techniques": ["soothing", "repetition", "calm_imagery"],
                "interaction_style": "relaxing",
                "follow_up_prompts": False
            }
        }
        
        return strategies.get(mode, strategies[DialogueMode.CHAT])
    
    def _get_cultural_context(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Get cultural context for response adaptation"""
        
        location = user_profile.get("location", "").lower()
        
        # Indian context adaptations
        hinglish_usage = "india" in location or any(city in location for city in 
                                                    ["mumbai", "delhi", "bangalore", "chennai", "kolkata", "pune"])
        
        return {
            "hinglish_usage": hinglish_usage,
            "cultural_references": "indian" if hinglish_usage else "global",
            "language_style": "indian_english" if hinglish_usage else "standard_english",
            "emoji_usage": True,
            "colloquialisms": hinglish_usage
        }
    
    def _get_response_guidelines(self, 
                               mode: DialogueMode,
                               emotional_state: Dict[str, Any],
                               user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Get response guidelines for current mode and state"""
        
        guidelines = {
            DialogueMode.CHAT: {
                "be_curious": True,
                "ask_questions": True,
                "validate_feelings": True,
                "use_examples": True
            },
            DialogueMode.STORY: {
                "be_descriptive": True,
                "use_character_voices": True,
                "create_suspense": True,
                "age_appropriate": True
            },
            DialogueMode.GAME: {
                "be_encouraging": True,
                "give_clear_instructions": True,
                "celebrate_success": True,
                "make_it_fun": True
            },
            DialogueMode.COMFORT: {
                "be_empathetic": True,
                "validate_emotions": True,
                "offer_support": True,
                "avoid_dismissing": True
            },
            DialogueMode.TEACHING: {
                "be_patient": True,
                "break_down_concepts": True,
                "use_examples": True,
                "encourage_questions": True
            }
        }
        
        return guidelines.get(mode, guidelines[DialogueMode.CHAT])
    
    def _detect_boredom(self, user_input: str, emotional_state: Dict[str, Any]) -> bool:
        """Detect if user is bored"""
        
        boredom_indicators = [
            "boring", "bored", "nothing", "i don't know", "whatever", 
            "ok", "fine", "sure", "maybe", "umm", "uh"
        ]
        
        user_input_lower = user_input.lower()
        
        # Check for boredom keywords
        if any(indicator in user_input_lower for indicator in boredom_indicators):
            return True
        
        # Check for very short responses
        if len(user_input.split()) <= 2 and emotional_state.get("sentiment") == "neutral":
            return True
        
        # Check for low energy and neutral sentiment
        if (emotional_state.get("energy_level") == "low" and 
            emotional_state.get("sentiment") == "neutral"):
            return True
        
        return False
    
    def _detect_repair_need(self, user_input: str, context: Dict[str, Any] = None) -> bool:
        """Detect if conversational repair is needed"""
        
        repair_indicators = [
            "no", "not that", "i didn't say", "i meant", "actually", 
            "wait", "that's wrong", "i said", "listen"
        ]
        
        user_input_lower = user_input.lower()
        
        # Check for repair keywords
        if any(indicator in user_input_lower for indicator in repair_indicators):
            return True
        
        # Check for very short correction
        if len(user_input.split()) <= 3 and context and context.get("stt_confidence", 1.0) < 0.7:
            return True
        
        return False
    
    def _assess_user_engagement(self, user_input: str, emotional_state: Dict[str, Any]) -> float:
        """Assess user engagement level (0.0 to 1.0)"""
        
        # Base engagement from emotional state
        base_engagement = emotional_state.get("confidence", 0.5)
        
        # Adjust based on input length
        word_count = len(user_input.split())
        if word_count > 5:
            base_engagement += 0.2
        elif word_count < 3:
            base_engagement -= 0.1
        
        # Adjust based on sentiment
        sentiment = emotional_state.get("sentiment", "neutral")
        if sentiment == "positive":
            base_engagement += 0.1
        elif sentiment == "negative":
            base_engagement -= 0.1
        
        # Adjust based on energy level
        energy = emotional_state.get("energy_level", "medium")
        if energy == "high":
            base_engagement += 0.2
        elif energy == "low":
            base_engagement -= 0.2
        
        return max(0.0, min(1.0, base_engagement))
    
    def _get_age_group(self, age: int) -> str:
        """Get age group category"""
        if age <= 5:
            return "toddler"
        elif age <= 9:
            return "child"
        else:
            return "preteen"
    
    def _update_mode_history(self, mode: DialogueMode, emotional_state: Dict[str, Any]):
        """Update mode history for analysis"""
        
        self.mode_history.append({
            "mode": mode.value,
            "timestamp": datetime.utcnow(),
            "emotional_state": emotional_state
        })
        
        # Keep only last 20 entries
        if len(self.mode_history) > 20:
            self.mode_history = self.mode_history[-20:]
    
    def _get_default_dialogue_plan(self) -> Dict[str, Any]:
        """Get default dialogue plan for error cases"""
        
        return {
            "mode": DialogueMode.CHAT.value,
            "prosody": self.prosody_settings[DialogueMode.CHAT],
            "token_budget": 150,
            "transition_plan": None,
            "engagement_strategy": {
                "techniques": ["questions", "curiosity"],
                "interaction_style": "conversational",
                "follow_up_prompts": True
            },
            "cultural_context": {
                "hinglish_usage": False,
                "cultural_references": "global",
                "language_style": "standard_english",
                "emoji_usage": True,
                "colloquialisms": False
            },
            "response_guidelines": {
                "be_curious": True,
                "ask_questions": True,
                "validate_feelings": True,
                "use_examples": True
            }
        }
    
    def get_mode_statistics(self) -> Dict[str, Any]:
        """Get statistics about mode usage"""
        
        if not self.mode_history:
            return {"total_modes": 0, "current_mode": self.current_mode.value}
        
        mode_counts = {}
        for entry in self.mode_history:
            mode = entry["mode"]
            mode_counts[mode] = mode_counts.get(mode, 0) + 1
        
        return {
            "total_modes": len(self.mode_history),
            "current_mode": self.current_mode.value,
            "mode_distribution": mode_counts,
            "most_common_mode": max(mode_counts, key=mode_counts.get) if mode_counts else None
        }