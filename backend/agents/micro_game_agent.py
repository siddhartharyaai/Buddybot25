"""
Micro-Game Agent - Handles engagement through mini-games and interactive activities
"""
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import random
from enum import Enum

logger = logging.getLogger(__name__)

class GameType(Enum):
    """Available micro-game types"""
    QUICK_MATH = "quick_math"
    RHYME_COMPLETION = "rhyme_completion"
    BREATHING_EXERCISE = "breathing_exercise"
    ANIMAL_SOUNDS = "animal_sounds"
    COLOR_GAME = "color_game"
    RIDDLES = "riddles"
    STORY_BUILDER = "story_builder"
    MEMORY_GAME = "memory_game"
    COUNTING_GAME = "counting_game"
    WORD_ASSOCIATION = "word_association"

class MicroGameAgent:
    """Handles micro-games for engagement and learning"""
    
    def __init__(self):
        self.active_games = {}  # session_id -> game_state
        self.game_library = self._initialize_game_library()
        self.engagement_triggers = {
            "silence_duration": 5.0,  # seconds
            "low_engagement_threshold": 0.4,
            "boredom_indicators": ["boring", "bored", "nothing", "i don't know"],
            "neutral_response_limit": 3  # consecutive neutral responses
        }
        
        logger.info("Micro-Game Agent initialized")
    
    def _initialize_game_library(self) -> Dict[GameType, Dict[str, Any]]:
        """Initialize the game library with all available games"""
        
        return {
            GameType.QUICK_MATH: {
                "name": "Quick Math",
                "description": "Simple math problems for different ages",
                "age_groups": ["toddler", "child", "preteen"],
                "duration": 60,  # seconds
                "difficulty_levels": 3,
                "engagement_type": "educational"
            },
            GameType.RHYME_COMPLETION: {
                "name": "Rhyme Time",
                "description": "Complete the rhyme or nursery rhyme",
                "age_groups": ["toddler", "child"],
                "duration": 45,
                "difficulty_levels": 2,
                "engagement_type": "creative"
            },
            GameType.BREATHING_EXERCISE: {
                "name": "Calm Breathing",
                "description": "Relaxation and breathing exercises",
                "age_groups": ["toddler", "child", "preteen"],
                "duration": 90,
                "difficulty_levels": 1,
                "engagement_type": "calming"
            },
            GameType.ANIMAL_SOUNDS: {
                "name": "Animal Sounds",
                "description": "Guess the animal by its sound",
                "age_groups": ["toddler", "child"],
                "duration": 40,
                "difficulty_levels": 2,
                "engagement_type": "fun"
            },
            GameType.COLOR_GAME: {
                "name": "Color Hunt",
                "description": "Find things of specific colors",
                "age_groups": ["toddler", "child"],
                "duration": 50,
                "difficulty_levels": 2,
                "engagement_type": "educational"
            },
            GameType.RIDDLES: {
                "name": "Riddle Me This",
                "description": "Age-appropriate riddles",
                "age_groups": ["child", "preteen"],
                "duration": 60,
                "difficulty_levels": 3,
                "engagement_type": "thinking"
            },
            GameType.STORY_BUILDER: {
                "name": "Story Builder",
                "description": "Build a story together",
                "age_groups": ["child", "preteen"],
                "duration": 120,
                "difficulty_levels": 2,
                "engagement_type": "creative"
            },
            GameType.MEMORY_GAME: {
                "name": "Memory Challenge",
                "description": "Remember sequences or items",
                "age_groups": ["child", "preteen"],
                "duration": 45,
                "difficulty_levels": 3,
                "engagement_type": "cognitive"
            },
            GameType.COUNTING_GAME: {
                "name": "Count Along",
                "description": "Counting games and number recognition",
                "age_groups": ["toddler", "child"],
                "duration": 35,
                "difficulty_levels": 2,
                "engagement_type": "educational"
            },
            GameType.WORD_ASSOCIATION: {
                "name": "Word Friends",
                "description": "Word association and vocabulary building",
                "age_groups": ["child", "preteen"],
                "duration": 45,
                "difficulty_levels": 2,
                "engagement_type": "vocabulary"
            }
        }
    
    async def should_trigger_game(self, 
                                session_id: str,
                                emotional_state: Dict[str, Any],
                                context: Dict[str, Any]) -> bool:
        """Determine if a micro-game should be triggered"""
        
        try:
            # Check if there's already an active game
            if session_id in self.active_games:
                return False
            
            # Check silence duration
            silence_duration = context.get("silence_duration", 0)
            if silence_duration > self.engagement_triggers["silence_duration"]:
                return True
            
            # Check engagement level
            engagement_level = context.get("engagement_level", 0.7)
            if engagement_level < self.engagement_triggers["low_engagement_threshold"]:
                return True
            
            # Check for boredom indicators
            last_user_input = context.get("last_user_input", "").lower()
            if any(indicator in last_user_input for indicator in self.engagement_triggers["boredom_indicators"]):
                return True
            
            # Check for consecutive neutral responses
            neutral_count = context.get("consecutive_neutral_responses", 0)
            if neutral_count >= self.engagement_triggers["neutral_response_limit"]:
                return True
            
            # Check emotional state
            mood = emotional_state.get("mood", "neutral")
            if mood in ["sad", "bored", "tired"] and emotional_state.get("energy_level") == "low":
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking game trigger: {str(e)}")
            return False
    
    async def select_appropriate_game(self, 
                                    user_profile: Dict[str, Any],
                                    emotional_state: Dict[str, Any],
                                    context: Dict[str, Any]) -> Optional[GameType]:
        """Select an appropriate game based on user profile and state"""
        
        try:
            age = user_profile.get("age", 5)
            age_group = self._get_age_group(age)
            
            mood = emotional_state.get("mood", "neutral")
            energy_level = emotional_state.get("energy_level", "medium")
            
            # Filter games by age group
            suitable_games = []
            for game_type, game_info in self.game_library.items():
                if age_group in game_info["age_groups"]:
                    suitable_games.append(game_type)
            
            # Further filter by emotional state and context
            if mood == "sad" or energy_level == "low":
                # Prefer calming or gentle games
                priority_games = [GameType.BREATHING_EXERCISE, GameType.ANIMAL_SOUNDS, GameType.COLOR_GAME]
            elif mood == "excited" or energy_level == "high":
                # Prefer active or challenging games
                priority_games = [GameType.QUICK_MATH, GameType.RIDDLES, GameType.MEMORY_GAME]
            elif mood == "confused":
                # Prefer simple, clear games
                priority_games = [GameType.COUNTING_GAME, GameType.ANIMAL_SOUNDS, GameType.COLOR_GAME]
            else:
                # Default variety
                priority_games = [GameType.RHYME_COMPLETION, GameType.STORY_BUILDER, GameType.WORD_ASSOCIATION]
            
            # Find intersection of suitable and priority games
            available_games = [game for game in priority_games if game in suitable_games]
            
            if not available_games:
                available_games = suitable_games
            
            if not available_games:
                return None
            
            # Select random game from available options
            return random.choice(available_games)
            
        except Exception as e:
            logger.error(f"Error selecting game: {str(e)}")
            return None
    
    async def start_game(self, 
                        session_id: str,
                        game_type: GameType,
                        user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Start a micro-game"""
        
        try:
            age = user_profile.get("age", 5)
            age_group = self._get_age_group(age)
            
            # Initialize game state
            game_state = {
                "game_type": game_type,
                "session_id": session_id,
                "user_profile": user_profile,
                "started_at": datetime.utcnow(),
                "status": "active",
                "score": 0,
                "attempts": 0,
                "current_question": None,
                "game_data": {}
            }
            
            # Generate first question/challenge
            first_challenge = await self._generate_challenge(game_type, age_group, 1)
            game_state["current_question"] = first_challenge
            
            # Store active game
            self.active_games[session_id] = game_state
            
            # Generate game introduction
            introduction = self._generate_game_introduction(game_type, age_group)
            
            return {
                "game_started": True,
                "game_type": game_type.value,
                "introduction": introduction,
                "challenge": first_challenge,
                "game_state": game_state
            }
            
        except Exception as e:
            logger.error(f"Error starting game: {str(e)}")
            return {"game_started": False, "error": str(e)}
    
    async def process_game_response(self, 
                                  session_id: str,
                                  user_response: str,
                                  emotional_state: Dict[str, Any]) -> Dict[str, Any]:
        """Process user response in active game"""
        
        try:
            if session_id not in self.active_games:
                return {"error": "No active game found"}
            
            game_state = self.active_games[session_id]
            game_type = game_state["game_type"]
            
            # Process the response based on game type
            result = await self._process_game_specific_response(
                game_type, user_response, game_state, emotional_state
            )
            
            # Update game state
            game_state["attempts"] += 1
            
            if result.get("correct", False):
                game_state["score"] += 1
                
                # Check if game should continue
                if self._should_continue_game(game_state):
                    # Generate next challenge
                    next_challenge = await self._generate_next_challenge(game_state)
                    game_state["current_question"] = next_challenge
                    
                    return {
                        "game_continues": True,
                        "feedback": result.get("feedback", "Great job!"),
                        "next_challenge": next_challenge,
                        "score": game_state["score"]
                    }
                else:
                    # End game
                    return await self._end_game(session_id, "completed")
            else:
                # Wrong answer
                if game_state["attempts"] >= 3:
                    # End game after 3 attempts
                    return await self._end_game(session_id, "max_attempts")
                else:
                    # Give hint or encouragement
                    hint = result.get("hint", "Try again!")
                    return {
                        "game_continues": True,
                        "feedback": result.get("feedback", "Not quite right."),
                        "hint": hint,
                        "attempts_left": 3 - game_state["attempts"]
                    }
                    
        except Exception as e:
            logger.error(f"Error processing game response: {str(e)}")
            return {"error": str(e)}
    
    async def _generate_challenge(self, 
                                game_type: GameType,
                                age_group: str,
                                difficulty: int) -> Dict[str, Any]:
        """Generate a challenge for specific game type"""
        
        if game_type == GameType.QUICK_MATH:
            return self._generate_math_challenge(age_group, difficulty)
        elif game_type == GameType.RHYME_COMPLETION:
            return self._generate_rhyme_challenge(age_group, difficulty)
        elif game_type == GameType.BREATHING_EXERCISE:
            return self._generate_breathing_challenge(age_group)
        elif game_type == GameType.ANIMAL_SOUNDS:
            return self._generate_animal_sounds_challenge(age_group, difficulty)
        elif game_type == GameType.COLOR_GAME:
            return self._generate_color_challenge(age_group, difficulty)
        elif game_type == GameType.RIDDLES:
            return self._generate_riddle_challenge(age_group, difficulty)
        elif game_type == GameType.STORY_BUILDER:
            return self._generate_story_builder_challenge(age_group)
        elif game_type == GameType.MEMORY_GAME:
            return self._generate_memory_challenge(age_group, difficulty)
        elif game_type == GameType.COUNTING_GAME:
            return self._generate_counting_challenge(age_group, difficulty)
        elif game_type == GameType.WORD_ASSOCIATION:
            return self._generate_word_association_challenge(age_group, difficulty)
        else:
            return {"question": "Let's play a game!", "answer": "yes", "type": "general"}
    
    def _generate_math_challenge(self, age_group: str, difficulty: int) -> Dict[str, Any]:
        """Generate math challenge"""
        
        if age_group == "toddler":
            # Simple counting
            num = random.randint(1, 5)
            return {
                "question": f"Can you count to {num}?",
                "answer": str(num),
                "type": "counting",
                "hint": "Just count: 1, 2, 3..."
            }
        elif age_group == "child":
            # Simple addition/subtraction
            if difficulty == 1:
                a, b = random.randint(1, 5), random.randint(1, 5)
                return {
                    "question": f"What is {a} + {b}?",
                    "answer": str(a + b),
                    "type": "addition",
                    "hint": f"Try counting from {a} and adding {b} more"
                }
            else:
                a, b = random.randint(1, 10), random.randint(1, 5)
                return {
                    "question": f"What is {a} - {b}?",
                    "answer": str(a - b),
                    "type": "subtraction",
                    "hint": f"Start with {a} and take away {b}"
                }
        else:  # preteen
            # Multiplication/division
            if difficulty <= 2:
                a, b = random.randint(2, 9), random.randint(2, 9)
                return {
                    "question": f"What is {a} × {b}?",
                    "answer": str(a * b),
                    "type": "multiplication",
                    "hint": f"Think of {a} groups of {b}"
                }
            else:
                a, b = random.randint(2, 9), random.randint(2, 9)
                product = a * b
                return {
                    "question": f"What is {product} ÷ {a}?",
                    "answer": str(b),
                    "type": "division",
                    "hint": f"How many {a}s make {product}?"
                }
    
    def _generate_rhyme_challenge(self, age_group: str, difficulty: int) -> Dict[str, Any]:
        """Generate rhyme completion challenge"""
        
        rhymes = {
            "toddler": [
                {"line": "Twinkle, twinkle, little ___", "answer": "star", "hint": "It shines in the sky at night"},
                {"line": "Mary had a little ___", "answer": "lamb", "hint": "It's a baby sheep"},
                {"line": "Humpty Dumpty sat on a ___", "answer": "wall", "hint": "It's tall and made of bricks"}
            ],
            "child": [
                {"line": "Jack and Jill went up the ___", "answer": "hill", "hint": "It's high up, like a mountain"},
                {"line": "Hickory dickory dock, the mouse ran up the ___", "answer": "clock", "hint": "It tells time and goes tick-tock"},
                {"line": "Little Bo Peep has lost her ___", "answer": "sheep", "hint": "White fluffy animals that say 'baa'"}
            ]
        }
        
        available_rhymes = rhymes.get(age_group, rhymes["child"])
        chosen_rhyme = random.choice(available_rhymes)
        
        return {
            "question": f"Complete this rhyme: {chosen_rhyme['line']}",
            "answer": chosen_rhyme["answer"],
            "type": "rhyme_completion",
            "hint": chosen_rhyme["hint"]
        }
    
    def _generate_breathing_challenge(self, age_group: str) -> Dict[str, Any]:
        """Generate breathing exercise challenge"""
        
        exercises = {
            "toddler": "Let's take 3 deep breaths together. Breathe in slowly... and out slowly...",
            "child": "Let's do some calm breathing. Breathe in for 3 counts, hold for 1, then out for 3 counts.",
            "preteen": "Let's try box breathing. Breathe in for 4, hold for 4, out for 4, hold for 4."
        }
        
        return {
            "question": exercises.get(age_group, exercises["child"]),
            "answer": "done",
            "type": "breathing_exercise",
            "hint": "Just follow along with me"
        }
    
    def _generate_animal_sounds_challenge(self, age_group: str, difficulty: int) -> Dict[str, Any]:
        """Generate animal sounds challenge"""
        
        animals = {
            1: [
                {"animal": "cow", "sound": "moo", "hint": "It gives us milk"},
                {"animal": "dog", "sound": "woof", "hint": "It's man's best friend"},
                {"animal": "cat", "sound": "meow", "hint": "It purrs and likes fish"}
            ],
            2: [
                {"animal": "lion", "sound": "roar", "hint": "It's the king of the jungle"},
                {"animal": "elephant", "sound": "trumpet", "hint": "It has a long trunk"},
                {"animal": "owl", "sound": "hoot", "hint": "It's awake at night"}
            ]
        }
        
        animal_list = animals.get(difficulty, animals[1])
        chosen_animal = random.choice(animal_list)
        
        return {
            "question": f"What sound does a {chosen_animal['animal']} make?",
            "answer": chosen_animal["sound"],
            "type": "animal_sounds",
            "hint": chosen_animal["hint"]
        }
    
    def _generate_color_challenge(self, age_group: str, difficulty: int) -> Dict[str, Any]:
        """Generate color recognition challenge"""
        
        colors = ["red", "blue", "green", "yellow", "purple", "orange", "pink", "brown"]
        chosen_color = random.choice(colors)
        
        color_objects = {
            "red": ["apple", "fire truck", "rose"],
            "blue": ["sky", "ocean", "blueberry"],
            "green": ["grass", "tree", "frog"],
            "yellow": ["sun", "banana", "school bus"],
            "purple": ["grape", "eggplant", "violet"],
            "orange": ["orange", "pumpkin", "carrot"],
            "pink": ["flamingo", "cotton candy", "pig"],
            "brown": ["chocolate", "tree trunk", "bear"]
        }
        
        objects = color_objects.get(chosen_color, ["something"])
        chosen_object = random.choice(objects)
        
        return {
            "question": f"What color is a {chosen_object}?",
            "answer": chosen_color,
            "type": "color_recognition",
            "hint": f"Think about the color of {chosen_object}"
        }
    
    def _generate_riddle_challenge(self, age_group: str, difficulty: int) -> Dict[str, Any]:
        """Generate riddle challenge"""
        
        riddles = {
            "child": [
                {"question": "I have four legs and I bark. What am I?", "answer": "dog", "hint": "It's a pet that loves to play fetch"},
                {"question": "I'm yellow and I shine in the sky. What am I?", "answer": "sun", "hint": "It makes the day bright and warm"},
                {"question": "I have wings but I'm not a bird. I make honey. What am I?", "answer": "bee", "hint": "It buzzes and lives in a hive"}
            ],
            "preteen": [
                {"question": "I have keys but no locks. I have space but no room. What am I?", "answer": "keyboard", "hint": "You use me to type"},
                {"question": "I'm tall when I'm young and short when I'm old. What am I?", "answer": "candle", "hint": "I give light when lit"},
                {"question": "I have a face but no eyes. I have hands but no arms. What am I?", "answer": "clock", "hint": "I tell time"}
            ]
        }
        
        available_riddles = riddles.get(age_group, riddles["child"])
        chosen_riddle = random.choice(available_riddles)
        
        return {
            "question": chosen_riddle["question"],
            "answer": chosen_riddle["answer"],
            "type": "riddle",
            "hint": chosen_riddle["hint"]
        }
    
    def _generate_story_builder_challenge(self, age_group: str) -> Dict[str, Any]:
        """Generate story building challenge"""
        
        story_starters = [
            "Once upon a time, there was a magical forest where...",
            "In a land far away, a brave little mouse decided to...",
            "On a sunny day, a curious child found a mysterious box that...",
            "Deep in the ocean, a friendly dolphin discovered..."
        ]
        
        return {
            "question": f"Let's build a story together! {random.choice(story_starters)} What happens next?",
            "answer": "continue",
            "type": "story_builder",
            "hint": "Use your imagination!"
        }
    
    def _generate_memory_challenge(self, age_group: str, difficulty: int) -> Dict[str, Any]:
        """Generate memory challenge"""
        
        if age_group == "child":
            items = ["apple", "ball", "cat"]
        else:  # preteen
            items = ["book", "pencil", "flower", "star"]
        
        if difficulty > 1:
            items.append(random.choice(["tree", "car", "house", "bird"]))
        
        return {
            "question": f"Remember these items: {', '.join(items)}. Now tell me back all the items!",
            "answer": items,
            "type": "memory_sequence",
            "hint": "Take your time and think carefully"
        }
    
    def _generate_counting_challenge(self, age_group: str, difficulty: int) -> Dict[str, Any]:
        """Generate counting challenge"""
        
        if age_group == "toddler":
            if difficulty == 1:
                return {
                    "question": "Let's count from 1 to 3! Can you do it?",
                    "answer": "1, 2, 3",
                    "type": "counting",
                    "hint": "Start with 1, then 2, then 3"
                }
            else:
                return {
                    "question": "Count from 1 to 5!",
                    "answer": "1, 2, 3, 4, 5",
                    "type": "counting",
                    "hint": "One at a time: 1, 2, 3, 4, 5"
                }
        else:  # child
            start = random.randint(1, 5)
            end = start + random.randint(3, 6)
            return {
                "question": f"Count from {start} to {end}!",
                "answer": ", ".join(str(i) for i in range(start, end + 1)),
                "type": "counting_range",
                "hint": f"Start with {start} and count up to {end}"
            }
    
    def _generate_word_association_challenge(self, age_group: str, difficulty: int) -> Dict[str, Any]:
        """Generate word association challenge"""
        
        word_pairs = {
            "child": [
                {"word": "hot", "expected": ["cold", "fire", "sun"], "hint": "What's the opposite of hot?"},
                {"word": "big", "expected": ["small", "little", "tiny"], "hint": "What's the opposite of big?"},
                {"word": "day", "expected": ["night", "dark", "moon"], "hint": "What comes after day?"}
            ],
            "preteen": [
                {"word": "ocean", "expected": ["water", "sea", "fish", "blue"], "hint": "What do you find in the ocean?"},
                {"word": "library", "expected": ["books", "read", "quiet"], "hint": "What do you do in a library?"},
                {"word": "kitchen", "expected": ["cook", "food", "eat"], "hint": "What happens in a kitchen?"}
            ]
        }
        
        available_pairs = word_pairs.get(age_group, word_pairs["child"])
        chosen_pair = random.choice(available_pairs)
        
        return {
            "question": f"When I say '{chosen_pair['word']}', what word comes to mind?",
            "answer": chosen_pair["expected"],
            "type": "word_association",
            "hint": chosen_pair["hint"]
        }
    
    async def _process_game_specific_response(self, 
                                            game_type: GameType,
                                            user_response: str,
                                            game_state: Dict[str, Any],
                                            emotional_state: Dict[str, Any]) -> Dict[str, Any]:
        """Process response for specific game type"""
        
        current_question = game_state.get("current_question", {})
        expected_answer = current_question.get("answer", "")
        question_type = current_question.get("type", "")
        
        user_response_lower = user_response.lower().strip()
        
        # Handle different answer types
        if question_type == "memory_sequence":
            # Check if user listed all items
            expected_items = expected_answer
            mentioned_items = [item for item in expected_items if item in user_response_lower]
            
            if len(mentioned_items) >= len(expected_items) * 0.8:  # 80% correct
                return {
                    "correct": True,
                    "feedback": f"Excellent memory! You remembered {len(mentioned_items)} out of {len(expected_items)} items!"
                }
            else:
                return {
                    "correct": False,
                    "feedback": f"Good try! You remembered {len(mentioned_items)} items.",
                    "hint": f"The items were: {', '.join(expected_items)}"
                }
        
        elif question_type == "word_association":
            # Check if response matches any expected answers
            expected_answers = expected_answer if isinstance(expected_answer, list) else [expected_answer]
            
            if any(answer in user_response_lower for answer in expected_answers):
                return {
                    "correct": True,
                    "feedback": "Great association! That's exactly right!"
                }
            else:
                return {
                    "correct": False,
                    "feedback": "Interesting answer! Let me give you a hint.",
                    "hint": current_question.get("hint", "Try again!")
                }
        
        elif question_type == "story_builder":
            # Story building is always "correct" - encourage creativity
            return {
                "correct": True,
                "feedback": "What a creative story! I love your imagination!"
            }
        
        elif question_type == "breathing_exercise":
            # Breathing exercises are completion-based
            if any(word in user_response_lower for word in ["done", "finished", "ready", "ok"]):
                return {
                    "correct": True,
                    "feedback": "Perfect! You did great breathing exercises. Feel more relaxed?"
                }
            else:
                return {
                    "correct": False,
                    "feedback": "Take your time with the breathing exercise.",
                    "hint": "Just say 'done' when you're finished"
                }
        
        else:
            # Standard answer checking
            if isinstance(expected_answer, list):
                correct = any(answer in user_response_lower for answer in expected_answer)
            else:
                correct = expected_answer.lower() in user_response_lower
            
            if correct:
                return {
                    "correct": True,
                    "feedback": "Exactly right! Well done!"
                }
            else:
                return {
                    "correct": False,
                    "feedback": "Not quite right, but good try!",
                    "hint": current_question.get("hint", "Try again!")
                }
    
    def _should_continue_game(self, game_state: Dict[str, Any]) -> bool:
        """Determine if game should continue"""
        
        # Check if we've reached maximum questions
        if game_state["score"] >= 3:  # Max 3 questions per game
            return False
        
        # Check if game has been running too long
        duration = (datetime.utcnow() - game_state["started_at"]).total_seconds()
        max_duration = self.game_library[game_state["game_type"]]["duration"]
        
        if duration > max_duration:
            return False
        
        return True
    
    async def _generate_next_challenge(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate next challenge in the game"""
        
        game_type = game_state["game_type"]
        user_profile = game_state["user_profile"]
        age_group = self._get_age_group(user_profile.get("age", 5))
        
        # Increase difficulty slightly
        difficulty = min(game_state["score"] + 1, 3)
        
        return await self._generate_challenge(game_type, age_group, difficulty)
    
    async def _end_game(self, session_id: str, end_reason: str) -> Dict[str, Any]:
        """End the active game"""
        
        if session_id not in self.active_games:
            return {"error": "No active game found"}
        
        game_state = self.active_games[session_id]
        score = game_state["score"]
        total_attempts = game_state["attempts"]
        
        # Remove from active games
        del self.active_games[session_id]
        
        # Generate end message
        if end_reason == "completed":
            message = f"Fantastic job! You scored {score} points! Want to play another game?"
        elif end_reason == "max_attempts":
            message = f"Good effort! You tried your best. Let's try a different game!"
        else:
            message = f"Thanks for playing! You scored {score} points!"
        
        return {
            "game_ended": True,
            "end_reason": end_reason,
            "final_score": score,
            "total_attempts": total_attempts,
            "message": message
        }
    
    def _generate_game_introduction(self, game_type: GameType, age_group: str) -> str:
        """Generate game introduction"""
        
        introductions = {
            GameType.QUICK_MATH: "Let's play some fun math! I'll give you a problem and you solve it!",
            GameType.RHYME_COMPLETION: "Time for rhyme time! I'll start a rhyme and you finish it!",
            GameType.BREATHING_EXERCISE: "Let's do some calm breathing together to feel peaceful!",
            GameType.ANIMAL_SOUNDS: "Let's play animal sounds! I'll ask about animals and you tell me their sounds!",
            GameType.COLOR_GAME: "Let's play with colors! I'll ask about different colors!",
            GameType.RIDDLES: "Riddle time! I'll give you a fun riddle to solve!",
            GameType.STORY_BUILDER: "Let's build a story together! I'll start and you continue!",
            GameType.MEMORY_GAME: "Memory challenge! I'll give you things to remember!",
            GameType.COUNTING_GAME: "Let's count together! Numbers are fun!",
            GameType.WORD_ASSOCIATION: "Word friends! I'll say a word and you say what comes to mind!"
        }
        
        return introductions.get(game_type, "Let's play a fun game together!")
    
    def _get_age_group(self, age: int) -> str:
        """Get age group category"""
        if age <= 5:
            return "toddler"
        elif age <= 9:
            return "child"
        else:
            return "preteen"
    
    def get_game_statistics(self) -> Dict[str, Any]:
        """Get game statistics"""
        
        return {
            "total_games_available": len(self.game_library),
            "active_games": len(self.active_games),
            "game_types": [game_type.value for game_type in self.game_library.keys()],
            "engagement_triggers": self.engagement_triggers
        }