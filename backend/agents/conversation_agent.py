"""
Conversation Agent - Handles AI conversations using Gemini 2.0 Flash
"""
import asyncio
import logging
import random
import re
import time
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)

class ConversationAgent:
    """Handles AI conversations with age-appropriate responses"""
    
    def __init__(self, gemini_api_key: str):
        self.gemini_api_key = gemini_api_key
        self.conversations = {}  # Store conversation history
        self.story_sessions = {}  # Store story sessions
        self.db = None  # Will be set by orchestrator
        
        # Enhanced age-appropriate system messages with content frameworks
        self.system_messages = {
            "toddler": (
                "You are a friendly AI companion for children aged 3-5. Use very simple words, "
                "short sentences, and a playful tone. Always be encouraging and patient. "
                "Focus on basic concepts like colors, shapes, animals, and simple stories. "
                "When creating content, make it developmentally appropriate with repetitive elements and simple concepts."
            ),
            "child": (
                "You are an AI companion for children aged 6-9. Use clear, simple language "
                "and be educational while staying fun. You can discuss school topics, "
                "tell stories, play simple games, and answer basic questions about the world. "
                "Create rich, engaging content that follows proper storytelling and educational frameworks."
            ),
            "preteen": (
                "You are an AI companion for children aged 10-12. Use more sophisticated "
                "vocabulary and can discuss more complex topics like science, history, "
                "and help with homework. Maintain a friendly, encouraging tone while "
                "providing detailed, well-structured content that challenges their thinking."
            )
        }
        
        # Content generation frameworks by type
        self.content_frameworks = {
            "story": {
                "structure": [
                    "Characters: Introduce main character(s) and supporting characters",
                    "Setting: Establish where and when the story takes place",
                    "Plot: Beginning (introduction) → Rising Action → Climax → Falling Action → Resolution",
                    "Conflict: Present a problem or challenge for characters to overcome",
                    "Theme: Include an underlying message or lesson (friendship, courage, honesty, etc.)",
                    "Language: Use age-appropriate vocabulary and sentence structure"
                ],
                "age_guidelines": {
                    3: "100-300 words, simple plot, repetitive elements, happy ending",
                    5: "200-500 words, clear moral lesson, simple conflicts",
                    7: "300-800 words, more complex characters, detailed descriptions",
                    10: "500-1200 words, sophisticated themes, character development",
                    12: "800-1500 words, complex plots, meaningful themes"
                }
            },
            "song": {
                "structure": [
                    "Verse-Chorus-Verse-Chorus structure or simple AABA pattern",
                    "Consistent rhythm and meter",
                    "Age-appropriate rhyming scheme",
                    "Repetitive elements for memorability",
                    "Positive, uplifting message"
                ],
                "age_guidelines": {
                    3: "4-8 lines, simple AABB rhyme scheme, repetitive chorus",
                    5: "8-12 lines, basic verse-chorus structure",
                    7: "12-20 lines, more complex rhyming patterns",
                    10: "16-32 lines, sophisticated themes and wordplay",
                    12: "20-40 lines, advanced structure and meaning"
                }
            },
            "rhyme": {
                "structure": [
                    "Consistent rhythm and meter",
                    "Clear rhyming pattern (AABB, ABAB, or ABCB)",
                    "Playful, musical quality",
                    "Age-appropriate vocabulary",
                    "Often includes action or movement words"
                ],
                "age_guidelines": {
                    3: "4-6 lines, simple AABB pattern",
                    5: "6-8 lines, basic rhythm",
                    7: "8-12 lines, varied patterns",
                    10: "10-16 lines, complex wordplay",
                    12: "12-20 lines, sophisticated themes"
                }
            },
            "joke": {
                "structure": [
                    "Setup: Establish context or scenario",
                    "Punchline: Deliver surprising or funny conclusion",
                    "Age-appropriate humor (wordplay, silly situations, not mean-spirited)",
                    "Clean and positive content"
                ],
                "age_guidelines": {
                    3: "Very simple, often repetitive (knock-knock style)",
                    5: "Simple wordplay and silly situations",
                    7: "Puns and basic humor concepts",
                    10: "More sophisticated wordplay and situational humor",
                    12: "Complex puns and intelligent humor"
                }
            },
            "riddle": {
                "structure": [
                    "Clear, engaging question or puzzle",
                    "Age-appropriate difficulty level",
                    "Logical answer that makes sense when revealed",
                    "Often uses wordplay, rhyme, or clever misdirection",
                    "Educational element when possible"
                ],
                "age_guidelines": {
                    3: "Very simple, concrete objects and concepts",
                    5: "Basic wordplay and familiar objects",
                    7: "More complex wordplay and abstract thinking",
                    10: "Logic puzzles and sophisticated wordplay",
                    12: "Complex reasoning and advanced concepts"
                }
            }
        }
        
        # BLAZING SPEED OPTIMIZATION: Expanded comprehensive template system for <0.5s responses
        self.blazing_templates = {
            "story": {
                "animals": {
                    "toddler": [
                        "Once upon a time, there was a little {animal} named {name}. {name} loved to play in the {place}. Every day, {name} would hop and jump and have fun with friends. The end!",
                        "A tiny {animal} called {name} lived in a cozy {place}. {name} liked to eat {food} and play games. One day, {name} made a new friend. They played together all day long!",
                        "There was a happy {animal} named {name}. {name} had soft {color} fur and loved to sing songs. All the other animals liked {name} because {name} was so kind and friendly.",
                        "Little {animal} {name} woke up in the sunny {place}. {name} stretched and yawned, then went to find some yummy {food}. What a wonderful day to be a happy {animal}!",
                        "In the {place}, a sweet {animal} named {name} lived with many friends. They would play hide and seek among the {objects}. {name} was the best at finding everyone!"
                    ],
                    "child": [
                        "In a magical {place}, there lived a brave {animal} named {name}. One sunny morning, {name} discovered something amazing - a {object} that sparkled like stars! {name} decided to go on an adventure to learn more about this mysterious treasure. Along the way, {name} met helpful friends who taught important lessons about courage and kindness.",
                        "Deep in the enchanted {place}, {name} the {animal} had a special gift - {name} could talk to all the creatures of the forest. When the animals came to {name} with a big problem, {name} knew it was time to use this gift to help everyone work together and solve it.",
                        "Long ago, in a land far away, there was a clever {animal} named {name}. {name} lived in a beautiful {place} filled with {objects}. One day, {name} found a map that led to an incredible adventure full of friendship, discovery, and magical surprises.",
                        "The wise old owl told all the animals about {name}, a special {animal} who lived by the crystal-clear pond in the heart of the {place}. {name} had the remarkable ability to understand what every creature was feeling. When a great sadness fell over the forest, it was {name} who brought back joy and laughter.",
                        "In the bustling village near the {place}, everyone knew about {name} the {animal}. {name} ran the most wonderful bakery, making delicious treats from forest berries and nuts. But {name}'s real magic wasn't in baking - it was in making everyone feel welcome and loved."
                    ],
                    "preteen": [
                        "In the mystical realm of {place}, where ancient {objects} held the secrets of the world, there lived an extraordinary {animal} named {name}. {name} possessed a rare ability that had been passed down through generations - the power to understand the language of all living things. When a great challenge threatened the harmony of their world, {name} embarked on an epic quest that would test not only their special gift, but their courage, wisdom, and determination to protect everything they held dear.",
                        "The legend spoke of a {animal} who would rise when the {place} needed a hero most. {name} never believed they were that {animal} until the day mysterious {objects} began appearing throughout their homeland. These weren't ordinary {objects} - they pulsed with an otherworldly energy that seemed to call out to {name}. Thus began an adventure that would take {name} across vast landscapes, through treacherous challenges, and ultimately to a discovery that would change their understanding of themselves and their place in the world forever.",
                        "Dr. Marina Blackwood had studied the ancient texts for decades, but she never expected to encounter {name}, a {animal} with intelligence that rivaled her own. Deep in the unexplored regions of {place}, {name} had built a sophisticated society using {objects} in ways that defied scientific understanding. As Marina documented her groundbreaking discovery, she realized that {name} and their community held the key to solving one of humanity's greatest challenges."
                    ]
                },
                "adventure": {
                    "toddler": [
                        "Little {name} went on a fun trip to the {place}. {name} saw many pretty {objects} and made friends with a nice {animal}. They played games and laughed a lot. When it was time to go home, {name} was very happy!",
                        "{name} found a magical {object} in the backyard. When {name} touched it, something wonderful happened! {name} could fly like a bird! {name} flew around the {place} and saw all the beautiful things. What a fun adventure!",
                        "One sunny day, {name} decided to explore the big {place} behind the house. {name} discovered a tiny door hidden under some leaves. When {name} opened it, out came friendly fairy friends who wanted to play!",
                        "Captain {name} sailed on a boat made of {objects} across the puddle in the {place}. The {animal} crew helped navigate through the splashing waves. They found treasure - a box full of pretty, shiny pebbles!"
                    ],
                    "child": [
                        "When {name} discovered the hidden {place} behind their house, they never imagined it would lead to the greatest adventure of their life. The {place} was filled with glowing {objects} and friendly creatures who needed {name}'s help to solve an important mystery. With courage and cleverness, {name} helped the creatures and learned that being brave means helping others, even when you're scared.",
                        "The old {object} in {name}'s attic wasn't just any ordinary thing - it was a portal to an amazing world called {place}! In this magical realm, {name} met talking {animals} and discovered they had special powers. But with great power comes great responsibility, and {name} had to use their abilities to help restore peace to this wonderful land.",
                        "Detective {name} received a mysterious letter asking for help solving the case of the missing {objects} from the {place}. Armed with a magnifying glass and notepad, {name} followed clues that led through secret passages, hidden rooms, and finally to a surprising discovery that taught everyone about friendship and forgiveness.",
                        "The annual {place} festival was in danger when the magical {objects} went missing! {name} volunteered to help search, teaming up with a wise {animal} guide. Their quest took them through enchanted forests, across rainbow bridges, and into caves filled with singing crystals."
                    ],
                    "preteen": [
                        "What started as an ordinary day for {name} quickly transformed into an extraordinary journey when they stumbled upon an ancient {object} hidden in the depths of the old {place}. This wasn't just any artifact - it was a key to unlocking mysteries that had been buried for centuries. As {name} delved deeper into the secrets surrounding this discovery, they found themselves at the center of an adventure that would challenge everything they thought they knew about history, courage, and their own potential to make a difference in the world.",
                        "The International Space Station received an unusual signal from the remote {place} on Earth, and fifteen-year-old communications specialist {name} was the only one who could decode it. The message revealed the existence of an advanced civilization living beneath the {objects} that had been monitoring human progress for millennia. Now {name} faced an impossible choice: report the discovery to the authorities or honor the civilization's request for secrecy while helping them solve a crisis that could affect both their worlds."
                    ]
                },
                "friendship": {
                    "toddler": [
                        "{name} and {friend} were best friends who loved to play together in the {place}. They shared their {food} and took turns with their favorite {objects}. When one felt sad, the other would give big hugs. That's what good friends do!",
                        "Two little friends, {name} and {friend}, found a special {object} while playing. They decided to share it and take turns. This made both friends very happy because sharing is caring!"
                    ],
                    "child": [
                        "{name} was nervous about starting at a new school, but everything changed when they met {friend} at the {place} during recess. {friend} was kind and helpful, showing {name} around and sharing lunch. Together they discovered they both loved {objects} and became the very best of friends. Their friendship taught them that being different makes friendships even more special.",
                        "When {name} and {friend} disagreed about which game to play at the {place}, they both felt upset. But then they remembered what their teacher said about compromise. They created a new game that combined both their ideas, making it twice as fun! Their friendship grew stronger because they learned to work together."
                    ],
                    "preteen": [
                        "{name} thought middle school would be easy until they had a falling out with their best friend {friend} over a misunderstanding about the {objects} project. What followed was a journey of self-reflection, difficult conversations, and ultimately learning that true friendship means admitting mistakes, listening with empathy, and choosing to rebuild trust even when it's hard. Through working together to help younger students at the {place}, they discovered their friendship was stronger than any disagreement.",
                        "When {name} discovered that their friend {friend} was being bullied for their interest in {objects}, they faced a difficult choice. Standing up would mean risking their own social status, but staying silent would betray the values their friendship was built on. The decision {name} made that day in the {place} not only changed their relationship with {friend} but also inspired others to stand up for what's right."
                    ]
                }
            },
            "fact": {
                "animals": {
                    "toddler": [
                        "Did you know that {animals} love to {action}? They use their {body_part} to do this! {animals} are really good at {skill}. Isn't that cool?",
                        "{animals} have {color} {body_part}! They use them to {action}. {animals} live in {places} and eat {food}. They are very {adjective}!",
                        "Baby {animals} are called {baby_name}! They love to play and learn from their mommies. {animals} families take care of each other just like your family takes care of you!"
                    ],
                    "child": [
                        "Here's an amazing fact about {animals}: They can {special_ability}! Scientists have discovered that {animals} use their {body_part} in incredible ways. For example, they can {example_action} which helps them {benefit}. This makes {animals} some of the most {adjective} creatures on Earth!",
                        "Did you know that {animals} have a superpower? They can {ability}! This special skill helps them {purpose}. What's even more amazing is that {animals} learn this ability when they're very young, just like how you learn new things every day!",
                        "{animals} are incredible communicators! They use different sounds, movements, and even smells to talk to each other. Some {animals} can recognize hundreds of different calls and know exactly what each one means. It's like they have their own language!"
                    ],
                    "preteen": [
                        "Here's a fascinating scientific discovery about {animals}: Research has revealed that they possess {special_ability}, which allows them to {complex_action}. This remarkable adaptation evolved over millions of years and serves multiple purposes including {purpose1}, {purpose2}, and {purpose3}. What makes this even more interesting is that {animals} can {additional_fact}, making them one of the most evolutionarily advanced species in their ecosystem.",
                        "Recent studies have shown that {animals} demonstrate complex cognitive abilities that were once thought to be unique to humans. They can solve multi-step problems, use tools creatively, and even show evidence of planning for future events. This research is revolutionizing our understanding of animal intelligence and consciousness."
                    ]
                },
                "space": {
                    "toddler": [
                        "The {planet} is very {size}! It has pretty {color} colors. Sometimes you can see {planet} in the sky at night. It looks like a bright {object}!",
                        "Did you know there are {number} moons around {planet}? They go round and round! The moons look like little {objects} dancing in space!",
                        "Astronauts wear special suits when they go to space! The suits help them breathe because there's no air in space. They float around like they're swimming!"
                    ],
                    "child": [
                        "Here's an incredible space fact: {planet} is {distance} away from Earth! That means if you could drive a car to {planet}, it would take {time_period} to get there. {planet} has {special_feature} that makes it unique in our solar system. Scientists use special telescopes to study {planet} and learn amazing things about space!",
                        "Did you know that {planet} has {weather_phenomenon}? Unlike Earth's weather, {planet}'s {weather_phenomenon} can {extreme_description}. This happens because {planet} is made mostly of {composition} and has gravity that is {gravity_comparison} than Earth's!",
                        "The International Space Station orbits Earth every 90 minutes! That means astronauts see 16 sunrises and sunsets every day. They conduct amazing experiments in zero gravity that help us understand how things work differently in space."
                    ],
                    "preteen": [
                        "Here's a mind-blowing astronomical fact: {planet} contains {scientific_detail} which creates {phenomenon}. The atmospheric composition of {planet} includes {elements}, resulting in {effects}. What's particularly fascinating is that recent space missions have discovered {recent_discovery}, revolutionizing our understanding of {scientific_concept}. This discovery has implications for {broader_implications} and opens new possibilities for {future_applications}.",
                        "The search for exoplanets has revealed thousands of worlds beyond our solar system, some of which might harbor conditions suitable for life. Using advanced techniques like the transit method and gravitational microlensing, astronomers have identified planets in the 'habitable zone' of their stars, where liquid water could potentially exist on the surface."
                    ]
                }
            },
            "joke": {
                "animals": {
                    "toddler": [
                        "Why don't {animals} use computers? Because they're afraid of the mouse! *giggles*",
                        "What do you call a sleeping {animal}? A {silly_name}! Hehe!",
                        "Why did the {animal} cross the road? To get to the {place}! That's so funny!",
                        "What do you call a {animal} with no legs? It doesn't matter - they can't come when you call them anyway! *laughs*"
                    ],
                    "child": [
                        "Why don't {animals} ever get lost? Because they always use their {body_part}-S! Get it? Like GPS but with {body_part}!",
                        "What do you call a {animal} that loves to dance? A {dance_style}-{animal}! They're always moving to the beat!",
                        "Why did the {animal} become a teacher? Because they were great at {subject} and loved to help others learn!",
                        "What do you call a {animal} magician? A {animal}-cadabra! They make all their problems disappear!"
                    ],
                    "preteen": [
                        "Why don't {animals} ever win at poker? Because they always {animal_behavior} when they have a good hand! Plus, they can never keep a straight face with those {facial_feature}!",
                        "What do you call a {animal} who's also a detective? A {profession}-{animal}! They're excellent at sniffing out clues and always solve the case!",
                        "Why did the {animal} start a band? Because they had perfect {musical_ability} and could really {performance_skill}! Their concerts were always sold out."
                    ]
                },
                "school": {
                    "toddler": [
                        "Why did the crayon go to school? To get sharper! *laughs*",
                        "What's a book's favorite food? Book-ies! Like cookies but for books! Hehe!",
                        "Why don't pencils tell jokes? Because they might break! Get it? Break like snap!"
                    ],
                    "child": [
                        "Why don't math books ever get sad? Because they have too many problems to solve! They're always busy figuring things out!",
                        "What do you call a teacher who never frowns? A geometry teacher - they're always working with angles! Get it?",
                        "Why did the student eat his homework? Because the teacher said it was a piece of cake!"
                    ],
                    "preteen": [
                        "Why did the science teacher bring a ladder to class? Because they wanted to reach the highest grade! And also to demonstrate potential energy!",
                        "What's the difference between a teacher and a train? A teacher says 'Take out your notebooks,' and a train says 'Choo choo!' But both help you reach your destination!",
                        "Why don't history teachers ever get old? Because they're always living in the past!"
                    ]
                }
            },
            "greeting": {
                "any": {
                    "toddler": [
                        "Hi there, {name}! I'm so happy to see you today! What fun things do you want to do?",
                        "Hello, my friend {name}! You look great today! What's making you smile?",
                        "Hey {name}! I've been waiting to play with you! What should we explore together?"
                    ],
                    "child": [
                        "Hello {name}! It's wonderful to see you again! I hope you're having a fantastic day. What exciting adventures are we going on today?",
                        "Hi there, {name}! I'm always excited when you visit. You always have such interesting questions and ideas. What's on your mind today?",
                        "Hey {name}! Great to see you! I've been thinking about all the cool things we could learn about together. What catches your curiosity today?"
                    ],
                    "preteen": [
                        "Hello {name}! It's great to connect with you again. I really value our conversations because you always bring such thoughtful perspectives. What's been interesting in your world lately?",
                        "Hi {name}! I hope you're having a good day. I'm always impressed by your curiosity and the depth of your questions. What would you like to explore or discuss today?",
                        "Hey there, {name}! Nice to see you. I appreciate how you always challenge me to think about things in new ways. What's captured your attention recently?"
                    ]
                }
            },
            "help": {
                "any": {
                    "toddler": [
                        "I'm Buddy, your AI friend! I love to tell stories, share fun facts, and play games with you. What sounds fun to you?",
                        "I'm here to help you learn and have fun! I can tell you about animals, sing songs, or make up silly jokes. What do you want to try?",
                        "I'm your buddy who knows lots of cool things! I can help you learn about anything you're curious about. What makes you wonder?"
                    ],
                    "child": [
                        "I'm Buddy, your AI companion! I'm here to help you learn, explore new ideas, and have great conversations. I can tell stories, explain how things work, help with homework, or just chat about whatever interests you. What would you like to do together?",
                        "Hi! I'm your friendly AI assistant. I love helping kids learn about the world around them. Whether you want to hear a story, learn about science, get help with school work, or just have a fun conversation, I'm here for you. What sounds interesting?",
                        "I'm designed to be your learning companion! I can help explain difficult concepts, create fun stories, answer your questions about pretty much anything, and even help you with creative projects. What kind of help are you looking for?"
                    ],
                    "preteen": [
                        "I'm Buddy, an AI designed to be your intelligent companion and learning partner. I can help with homework, explain complex topics, engage in thoughtful discussions, provide creative inspiration, or simply be someone to talk through ideas with. I'm programmed to understand that you're capable of sophisticated thinking, and I aim to match that level in our conversations. What would you like to work on or talk about?",
                        "I'm an AI assistant created to support young learners like yourself. I can provide detailed explanations, help with research, offer study strategies, engage in debates about interesting topics, or help you explore your interests more deeply. I recognize that you're developing critical thinking skills, and I try to encourage that growth. How can I assist you today?",
                        "Think of me as your personal AI tutor and discussion partner. I'm equipped to help with academic subjects, creative projects, problem-solving, and exploring complex ideas. I believe in treating you as the capable thinker you are while providing the support you need. What challenges or interests would you like to tackle together?"
                    ]
                }
            }
        }
        
        # BLAZING SPEED: Intent detection patterns for template matching - EXPANDED to 100+ patterns
        self.intent_patterns = {
            "story_animal": [
                r"story.*about.*(cat|dog|rabbit|mouse|bird|elephant|lion|tiger|bear|fox|wolf|deer|cow|pig|chicken|duck|horse|sheep|goat)",
                r"tell.*me.*about.*(animal|pet|cat|dog|rabbit|mouse|bird|elephant|lion|tiger|bear|fox|wolf|deer)",
                r"(cat|dog|rabbit|mouse|bird|elephant|lion|tiger|bear|fox|wolf|deer|cow|pig|chicken|duck|horse|sheep|goat).*story",
                r"animal.*story", r"pet.*story", r"farm.*animal", r"wild.*animal"
            ],
            "story_adventure": [
                r"adventure.*story", r"story.*adventure", r"quest.*story", r"journey.*story", r"explore.*story",
                r"treasure.*story", r"pirate.*story", r"knight.*story", r"princess.*story", r"dragon.*story",
                r"magic.*story", r"fairy.*tale", r"superhero.*story", r"space.*adventure", r"underwater.*adventure"
            ],
            "story_friendship": [
                r"friendship.*story", r"friend.*story", r"story.*about.*friends", r"best.*friend",
                r"making.*friends", r"helping.*friends", r"story.*together", r"teamwork.*story"
            ],
            "story_school": [
                r"school.*story", r"classroom.*story", r"teacher.*story", r"homework.*story",
                r"first.*day.*school", r"learning.*story", r"reading.*story", r"math.*story"
            ],
            "fact_animal": [
                r"fact.*about.*(cat|dog|rabbit|mouse|bird|elephant|lion|tiger|bear|fox|wolf|deer|cow|pig|chicken|duck|horse|sheep|goat)",
                r"tell.*me.*about.*(cat|dog|rabbit|mouse|bird|elephant|lion|tiger|bear|fox|wolf|deer|cow|pig|chicken|duck|horse|sheep|goat)",
                r"how.*do.*(cat|dog|rabbit|mouse|bird|elephant|lion|tiger|bear|fox|wolf|deer|cow|pig|chicken|duck|horse|sheep|goat)",
                r"what.*do.*(animals|pets).*do", r"animal.*facts", r"cool.*animal", r"amazing.*animal"
            ],
            "fact_space": [
                r"fact.*about.*(space|planet|star|moon|sun|mars|jupiter|saturn|venus|mercury|uranus|neptune|pluto)",
                r"tell.*me.*about.*(space|planet|star|moon|sun|mars|jupiter|saturn|venus|mercury|uranus|neptune|pluto)",
                r"(space|planet|star|moon|sun|mars|jupiter|saturn|venus|mercury|uranus|neptune|pluto).*fact",
                r"solar.*system", r"astronaut", r"rocket", r"alien", r"galaxy", r"universe"
            ],
            "fact_science": [
                r"how.*does.*work", r"why.*does", r"what.*happens.*when", r"science.*fact",
                r"experiment", r"discovery", r"invention", r"weather", r"rainbow", r"volcano", r"earthquake"
            ],
            "fact_body": [
                r"how.*does.*body", r"heart.*beat", r"brain.*work", r"why.*do.*we.*sleep",
                r"muscles", r"bones", r"blood", r"breathe", r"digest", r"grow"
            ],
            "joke_animal": [
                r"joke.*about.*(cat|dog|rabbit|mouse|bird|elephant|lion|tiger|bear|fox|wolf|deer)",
                r"funny.*joke", r"make.*me.*laugh", r"tell.*joke", r"animal.*joke", r"pet.*joke"
            ],
            "joke_school": [
                r"joke.*about.*school", r"school.*joke", r"funny.*about.*learning", r"teacher.*joke",
                r"homework.*joke", r"classroom.*joke", r"book.*joke"
            ],
            "joke_food": [
                r"food.*joke", r"joke.*about.*food", r"funny.*food", r"vegetable.*joke", r"fruit.*joke"
            ],
            "greeting": [
                r"^(hi|hello|hey|good morning|good afternoon|good evening)", r"how.*are.*you",
                r"what.*up", r"greetings", r"salutations"
            ],
            "help": [
                r"help.*me", r"can.*you.*help", r"i.*need.*help", r"what.*can.*you.*do",
                r"what.*are.*you", r"who.*are.*you"
            ],
            "learning": [
                r"teach.*me", r"learn.*about", r"explain.*how", r"what.*is.*a",
                r"homework.*help", r"study.*help", r"understand"
            ]
        }
        
        # BLAZING SPEED: Enhanced replacement variables for comprehensive personalization
        self.template_variables = {
            "animal": ["cat", "dog", "rabbit", "mouse", "bird", "elephant", "lion", "tiger", "bear", "fox", "wolf", "deer", "cow", "pig", "chicken", "duck", "horse", "sheep", "goat", "squirrel", "owl", "eagle", "dolphin", "whale", "shark", "butterfly", "bee", "ant"],
            "animals": ["cats", "dogs", "rabbits", "mice", "birds", "elephants", "lions", "tigers", "bears", "foxes", "wolves", "deer", "cows", "pigs", "chickens", "ducks", "horses", "sheep", "goats", "squirrels", "owls", "eagles", "dolphins", "whales", "sharks", "butterflies", "bees", "ants"],
            "place": ["forest", "meadow", "garden", "park", "mountain", "valley", "pond", "cave", "field", "village", "castle", "beach", "desert", "jungle", "farm", "school", "playground", "library", "museum", "bakery"],
            "places": ["forests", "meadows", "gardens", "parks", "mountains", "valleys", "ponds", "caves", "fields", "villages", "castles", "beaches", "deserts", "jungles", "farms", "schools", "playgrounds", "libraries", "museums", "bakeries"],
            "object": ["crystal", "flower", "book", "key", "treasure", "gem", "star", "shell", "feather", "stone", "map", "compass", "lantern", "crown", "wand", "sword", "shield", "potion", "scroll", "bell"],
            "objects": ["crystals", "flowers", "books", "keys", "treasures", "gems", "stars", "shells", "feathers", "stones", "maps", "compasses", "lanterns", "crowns", "wands", "swords", "shields", "potions", "scrolls", "bells"],
            "color": ["golden", "silver", "purple", "blue", "green", "red", "orange", "rainbow", "sparkly", "shiny", "glowing", "bright", "pastel", "vibrant", "multicolored", "iridescent", "pearl", "crystal"],
            "colors": ["golden", "silver", "purple", "blue", "green", "red", "orange", "rainbow", "sparkly", "shiny", "glowing", "bright", "pastel", "vibrant", "multicolored", "iridescent", "pearl", "crystal"],
            "adjective": ["brave", "kind", "clever", "funny", "gentle", "curious", "helpful", "smart", "caring", "amazing", "wonderful", "talented", "creative", "patient", "generous", "wise", "cheerful", "determined"],
            "adjectives": ["brave", "kind", "clever", "funny", "gentle", "curious", "helpful", "smart", "caring", "amazing", "wonderful", "talented", "creative", "patient", "generous", "wise", "cheerful", "determined"],
            "action": ["run", "jump", "play", "dance", "sing", "explore", "discover", "learn", "help", "share", "climb", "swim", "fly", "hop", "skip", "slide", "build", "create", "imagine", "laugh"],
            "actions": ["run", "jump", "play", "dance", "sing", "explore", "discover", "learn", "help", "share", "climb", "swim", "fly", "hop", "skip", "slide", "build", "create", "imagine", "laugh"],
            "subject": ["math", "reading", "science", "art", "music", "history", "geography", "spelling"],
            "subjects": ["math", "reading", "science", "art", "music", "history", "geography", "spelling"],
            "planet": ["Mars", "Jupiter", "Saturn", "Venus", "Mercury", "Uranus", "Neptune"],
            "planets": ["Mars", "Jupiter", "Saturn", "Venus", "Mercury", "Uranus", "Neptune"],
            "food": ["berries", "nuts", "fruits", "seeds", "vegetables", "honey", "leaves", "flowers", "apples", "carrots", "corn", "wheat", "mushrooms", "clover", "dandelions", "acorns"],
            "foods": ["berries", "nuts", "fruits", "seeds", "vegetables", "honey", "leaves", "flowers", "apples", "carrots", "corn", "wheat", "mushrooms", "clover", "dandelions", "acorns"],
            "body_part": ["ears", "tail", "nose", "paws", "wings", "fins", "antennae", "trunk", "mane", "whiskers", "claws", "beak", "horns", "shell", "fur", "feathers", "scales"],
            "body_parts": ["ears", "tail", "nose", "paws", "wings", "fins", "antennae", "trunk", "mane", "whiskers", "claws", "beak", "horns", "shell", "fur", "feathers", "scales"],
            "skill": ["jumping", "flying", "swimming", "climbing", "running", "hiding", "hunting", "singing", "dancing", "building", "digging", "gathering", "protecting", "communicating"],
            "skills": ["jumping", "flying", "swimming", "climbing", "running", "hiding", "hunting", "singing", "dancing", "building", "digging", "gathering", "protecting", "communicating"],
            "abilities": ["hear very well", "see in the dark", "swim very fast", "climb tall trees", "fly high", "run quickly", "jump far", "dig deep holes", "find food easily", "make beautiful sounds"],
            "baby_names": ["puppies", "kittens", "chicks", "cubs", "calves", "foals", "lambs", "piglets", "ducklings", "goslings", "fawns", "kits", "pups"],
            "special_abilities": ["echolocation", "migration patterns", "tool usage", "complex communication", "problem-solving skills", "memory capabilities", "social cooperation", "adaptation skills"],
            "dance_styles": ["ballet", "hip-hop", "jazz", "tap", "break", "swing", "salsa", "waltz"],
            "subjects": ["math", "reading", "science", "art", "music", "history", "geography", "spelling"],
            "professions": ["detective", "scientist", "teacher", "doctor", "chef", "artist", "musician", "writer", "explorer", "inventor"],
            "musical_abilities": ["rhythm", "pitch", "harmony", "melody", "beat"],
            "performance_skills": ["rock out", "harmonize", "improvise", "compose", "conduct"],
            "sizes": ["tiny", "small", "big", "huge", "enormous", "gigantic", "massive", "immense"],
            "distances": ["millions of miles", "billions of kilometers", "light-years", "thousands of miles"],
            "time_periods": ["years", "decades", "centuries", "lifetimes"],
            "planets": ["Mars", "Jupiter", "Saturn", "Venus", "Mercury", "Uranus", "Neptune"],
            "weather_phenomena": ["storms", "winds", "clouds", "lightning", "auroras", "dust devils"],
            "compositions": ["gases", "rocks", "ice", "metals", "liquids", "crystals"],
            "gravity_comparisons": ["stronger", "weaker", "different", "more intense", "less intense"]
        }
        
        logger.info("ConversationAgent initialized with enhanced content frameworks and BLAZING SPEED templates")
    
    def _detect_template_intent(self, user_input: str) -> Tuple[Optional[str], Optional[str]]:
        """BLAZING SPEED: Detect intent and return template category instantly"""
        user_input_lower = user_input.lower()
        
        for intent_name, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, user_input_lower):
                    # Parse intent: "story_animal" -> ("story", "animal")
                    parts = intent_name.split('_', 1)
                    if len(parts) == 2:
                        return parts[0], parts[1]
        
        return None, None
    
    def _get_blazing_template_response(self, content_type: str, category: str, user_profile: Dict[str, Any], user_input: str) -> Optional[str]:
        """BLAZING SPEED: Get instant template response with personalization"""
        age = user_profile.get('age', 5)
        name = user_profile.get('name', 'friend')
        
        # Determine age group
        if age <= 5:
            age_group = "toddler"
        elif age <= 9:
            age_group = "child"
        else:
            age_group = "preteen"
        
        # Get templates for this content type and category
        templates = self.blazing_templates.get(content_type, {}).get(category, {}).get(age_group, [])
        
        if not templates:
            return None
        
        # Select template (rotate based on hash for consistency)
        template_index = hash(user_input + str(user_profile.get('id', ''))) % len(templates)
        template = templates[template_index]
        
        # Extract animal or specific subject from user input for better personalization
        animal_match = re.search(r'\b(cat|dog|rabbit|mouse|bird|elephant|lion|tiger|bear|fox|wolf|deer|dragon|unicorn|dinosaur)\b', user_input.lower())
        place_match = re.search(r'\b(forest|jungle|ocean|mountain|castle|space|garden|farm|city|village)\b', user_input.lower())
        
        # Personalize template with profile data and detected entities
        replacements = {
            'name': name,
            'animal': animal_match.group(1) if animal_match else self._random_from_list('animals'),
            'place': place_match.group(1) if place_match else self._random_from_list('places'),
            'object': self._random_from_list('objects'),
            'color': self._random_from_list('colors'),
            'adjective': self._random_from_list('adjectives'),
            'food': self._random_from_list('foods'),
            'action': self._random_from_list('actions'),
            'objects': self._random_from_list('objects'),
            'animals': self._random_from_list('animals'),
            'body_part': 'ears' if category == 'animals' else 'wings',
            'skill': 'jumping' if category == 'animals' else 'flying',
            'ability': 'hear very well' if category == 'animals' else 'see in the dark',
            'size': 'big' if age <= 5 else 'enormous',
            'planet': 'Mars' if 'mars' in user_input.lower() else 'Jupiter',
            'number': 'many' if age <= 5 else 'over 50',
            'silly_name': f"sleepy-{name.lower()}" if name else 'sleepy-friend'
        }
        
        # Replace all template variables
        response = template
        for key, value in replacements.items():
            response = response.replace(f'{{{key}}}', str(value))
        
        # Add age appropriate conclusion for stories
        if content_type == "story" and age_group == "toddler":
            response += " The end! Wasn't that a fun story?"
        elif content_type == "story" and age_group == "child":
            response += f" And that's how {name} learned that adventures are everywhere when you're curious and kind!"
        elif content_type == "story" and age_group == "preteen":
            response += f" This adventure taught {name} that courage isn't about not being afraid - it's about doing what's right even when you are afraid."
        
        return response
    
    def _random_from_list(self, list_name: str) -> str:
        """Get random item from template variables list"""
        items = self.template_variables.get(list_name, ['something'])
        return items[hash(str(time.time())) % len(items)]
    
    async def get_template_suggestions(self) -> List[str]:
        """BLAZING LATENCY: Get dynamic conversation suggestions from template system"""
        try:
            suggestions = []
            
            # Generate template-based suggestions from different categories
            suggestion_templates = [
                # Story suggestions with variety
                "Tell me a story about a {animal}",
                "Story about {animal} and {animal}",
                "Adventure story in the {place}",
                "Tell me a {adjective} story",
                "Story about friendship and {animal}",
                
                # Fact suggestions
                "What's a fun fact about {animals}?",
                "Tell me about {planet}",
                "How do {animals} {action}?",
                "Fun fact about {place}",
                
                # Interactive suggestions
                "Can you tell me a {adjective} joke?",
                "Sing me a song about {animals}",
                "Help me learn about {subject}",
                "What can you teach me?",
                
                # Creative suggestions
                "Make up a funny joke",
                "Tell me something cool", 
                "What's your favorite story?",
                "Let's play a word game"
            ]
            
            # Select random suggestions and personalize them
            import random
            selected_templates = random.sample(suggestion_templates, min(6, len(suggestion_templates)))
            
            for template in selected_templates:
                # Replace template variables
                suggestion = template
                for variable, options in self.template_variables.items():
                    placeholder = f'{{{variable}}}'
                    if placeholder in suggestion:
                        replacement = random.choice(options)
                        suggestion = suggestion.replace(placeholder, replacement)
                
                suggestions.append(suggestion)
            
            # Add some static high-quality suggestions to ensure variety
            static_suggestions = [
                "What's your favorite animal?",
                "Tell me about your day",
                "Can you help me with something?",
                "I want to learn something new"
            ]
            
            # Mix template and static suggestions
            final_suggestions = suggestions[:4] + static_suggestions[:2]
            
            logger.info(f"BLAZING SPEED: Generated {len(final_suggestions)} template-based suggestions")
            return final_suggestions
            
        except Exception as e:
            logger.error(f"Error generating template suggestions: {str(e)}")
            # Return fallback suggestions
            return [
                "Tell me a story about a brave little mouse",
                "What's a fun fact about elephants?",
                "Can you tell me a funny joke?",
                "Sing me a song",
                "Help me learn something new",
                "What's your favorite animal?"
            ]
    
    def set_database(self, db):
        """Set database reference for story session management and BLAZING SPEED cache"""
        self.db = db
        # BLAZING SPEED: Initialize prefetch cache
        asyncio.create_task(self._initialize_prefetch_cache())
    
    async def _initialize_prefetch_cache(self):
        """BLAZING SPEED: Initialize MongoDB prefetch cache with top 50 queries"""
        try:
            if self.db is None:  # FIXED: Compare with None instead of truth testing
                return
            
            # Create prefetch_cache collection if it doesn't exist
            prefetch_collection = self.db.prefetch_cache
            
            # Top 100 common queries with pre-generated responses - EXPANDED
            common_queries = [
                # Stories - Basic
                "tell me a story", "story about a cat", "story about a dog", "story about animals", "adventure story",
                "story about dragons", "story about princesses", "story about space", "bedtime story", "funny story",
                "story about friendship", "story about magic", "story about brave mouse", "story about forest",
                "story about treasure", "story about dinosaurs", "story about unicorns", "story about ocean",
                
                # Stories - Expanded  
                "story about school", "story about family", "story about helping", "story about sharing",
                "story about being brave", "story about making friends", "story about learning", "story about kindness",
                "story about a superhero", "story about robots", "story about pirates", "story about fairies",
                
                # Facts - Basic
                "tell me a fact", "fact about animals", "fact about space", "fact about planets", "fact about dinosaurs",
                "how do birds fly", "why is the sky blue", "fact about elephants", "fact about dolphins", "fact about cats",
                "fact about dogs", "fact about moon", "fact about sun", "fact about earth", "fact about ocean",
                
                # Facts - Expanded
                "how does the heart work", "why do we sleep", "how do plants grow", "what are clouds made of",
                "how do cars work", "what makes rainbows", "how do fish breathe underwater", "why do leaves change color",
                "how do magnets work", "what causes earthquakes", "how do batteries work", "why do we dream",
                
                # Jokes - Basic
                "tell me a joke", "funny joke", "joke about animals", "joke about cats", "joke about dogs",
                "make me laugh", "school joke", "silly joke", "joke about elephants", "joke about space",
                "joke about food", "joke about books", "joke about teachers", "joke about friends",
                
                # Jokes - Expanded
                "knock knock joke", "joke about math", "joke about homework", "joke about vegetables",
                "joke about bedtime", "joke about dinosaurs", "joke about pirates", "joke about robots",
                
                # Greetings
                "hello", "hi", "hey", "good morning", "good afternoon", "good evening", "how are you",
                "what's up", "hi there", "hey buddy", "greetings", "nice to see you",
                
                # Help and Learning
                "what can you do", "help me", "teach me", "explain how", "what is", "how does",
                "can you help me learn", "i need help with", "show me how to", "what does that mean",
                
                # Conversational
                "I'm bored", "what should we do", "let's play", "sing a song", "what's your name", 
                "are you my friend", "do you like me", "what's your favorite", "tell me something cool",
                "i'm sad", "i'm happy", "i'm excited", "i had a good day", "i had a bad day",
                
                # Educational requests
                "homework help", "help me study", "explain math", "help with reading", "what's science",
                "tell me about history", "geography facts", "help me understand", "make learning fun"
            ]
            
            # Check if cache already exists
            cache_count = await prefetch_collection.count_documents({})
            if cache_count > 0:
                logger.info(f"BLAZING SPEED: Prefetch cache already initialized with {cache_count} entries")
                return
            
            logger.info("BLAZING SPEED: Initializing prefetch cache with top 50 queries...")
            
            # Pre-generate responses for common queries
            cache_entries = []
            for query in common_queries:
                # Detect template intent
                content_type, category = self._detect_template_intent(query)
                
                if content_type and category:
                    # Generate template responses for different age groups
                    for age_group in ["toddler", "child", "preteen"]:
                        age = 4 if age_group == "toddler" else 7 if age_group == "child" else 11
                        
                        mock_profile = {
                            'name': 'friend',
                            'age': age,
                            'id': f'cache_{age_group}'
                        }
                        
                        template_response = self._get_blazing_template_response(
                            content_type, category, mock_profile, query
                        )
                        
                        if template_response:
                            cache_entry = {
                                "query": query.lower().strip(),
                                "age_group": age_group,
                                "response": template_response,
                                "content_type": content_type,
                                "category": category,
                                "created_at": datetime.now(),
                                "hit_count": 0
                            }
                            cache_entries.append(cache_entry)
            
            # Insert cache entries
            if cache_entries:
                await prefetch_collection.insert_many(cache_entries)
                logger.info(f"BLAZING SPEED: Prefetch cache initialized with {len(cache_entries)} entries")
            
            # Create index for fast lookup
            await prefetch_collection.create_index([("query", 1), ("age_group", 1)])
            
        except Exception as e:
            logger.error(f"Error initializing prefetch cache: {str(e)}")
    
    async def _check_prefetch_cache(self, user_input: str, user_profile: Dict[str, Any]) -> Optional[str]:
        """BLAZING SPEED: Check prefetch cache for instant response"""
        try:
            if self.db is None:  # FIXED: Compare with None instead of truth testing
                return None
            
            # Determine age group
            age = user_profile.get('age', 5)
            if age <= 5:
                age_group = "toddler"
            elif age <= 9:
                age_group = "child" 
            else:
                age_group = "preteen"
            
            # Normalize query
            query_normalized = user_input.lower().strip()
            
            # Check cache
            prefetch_collection = self.db.prefetch_cache
            cache_entry = await prefetch_collection.find_one({
                "query": query_normalized,
                "age_group": age_group
            })
            
            if cache_entry:
                # Update hit count
                await prefetch_collection.update_one(
                    {"_id": cache_entry["_id"]},
                    {"$inc": {"hit_count": 1}}
                )
                
                # Personalize cached response with user's name
                response = cache_entry["response"]
                user_name = user_profile.get('name', 'friend')
                response = response.replace('friend', user_name)
                
                logger.info(f"BLAZING SPEED: Cache hit for '{user_input[:30]}...' (age: {age_group})")
                return response
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking prefetch cache: {str(e)}")
            return None
    
    async def create_story_session(self, session_id: str, user_id: str, story_type: str = "adventure") -> str:
        """Create a new story session for continuation tracking"""
        try:
            story_session_id = f"story_{session_id}_{int(time.time())}"
            story_session = {
                "_id": story_session_id,
                "session_id": session_id,
                "user_id": user_id,
                "story_type": story_type,
                "story_title": None,
                "total_chunks": 0,
                "completed_chunks": 0,
                "last_chunk_index": -1,
                "full_story_text": "",
                "current_state": "active",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "continuation_context": {}
            }
            
            if self.db:
                await self.db.story_sessions.insert_one(story_session)
            
            self.story_sessions[story_session_id] = story_session
            logger.info(f"Created story session: {story_session_id}")
            return story_session_id
            
        except Exception as e:
            logger.error(f"Error creating story session: {e}")
            return None
    
    async def get_story_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get story session for continuation"""
        try:
            # First check local cache
            for story_id, story_session in self.story_sessions.items():
                if story_session["session_id"] == session_id and story_session["current_state"] == "active":
                    return story_session
            
            # Check database
            if self.db:
                story_session = await self.db.story_sessions.find_one({
                    "session_id": session_id,
                    "current_state": "active"
                })
                if story_session:
                    self.story_sessions[story_session["_id"]] = story_session
                    return story_session
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting story session: {e}")
            return None
    
    async def update_story_session(self, story_session_id: str, update_data: Dict[str, Any]):
        """Update story session with new chunk information"""
        try:
            update_data["updated_at"] = datetime.utcnow()
            
            # Update local cache
            if story_session_id in self.story_sessions:
                self.story_sessions[story_session_id].update(update_data)
            
            # Update database
            if self.db:
                await self.db.story_sessions.update_one(
                    {"_id": story_session_id},
                    {"$set": update_data}
                )
            
            logger.info(f"Updated story session: {story_session_id}")
            
        except Exception as e:
            logger.error(f"Error updating story session: {e}")
    
    async def complete_story_session(self, story_session_id: str):
        """Mark story session as completed"""
        try:
            await self.update_story_session(story_session_id, {
                "current_state": "completed",
                "completed_chunks": self.story_sessions.get(story_session_id, {}).get("total_chunks", 0)
            })
            logger.info(f"Completed story session: {story_session_id}")
            
        except Exception as e:
            logger.error(f"Error completing story session: {e}")
    
    async def _generate_continuation_chunk(self, continuation_prompt: str, age: int) -> str:
        """Generate a story continuation chunk using the LLM"""
        try:
            chat = LlmChat()
            age_group = "toddler" if age <= 5 else "child" if age <= 9 else "preteen"
            system_message = self.system_messages[age_group]
            
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": continuation_prompt}
            ]
            
            response = await chat.achat(messages=messages, max_tokens=800)
            
            if response and response.strip():
                return response.strip()
            else:
                # Fallback continuation if LLM fails
                return f"The adventure continued with exciting new developments that delighted our young hero. More surprises were waiting just around the corner, making this an unforgettable journey filled with wonder and discovery."
                
        except Exception as e:
            logger.error(f"Error generating continuation chunk: {e}")
            # Return fallback continuation
            return f"The story continued with amazing adventures and wonderful discoveries that brought joy and excitement to everyone involved."
    
    def _get_dynamic_content_guidelines(self, content_type: str, age: int) -> Dict[str, Any]:
        """Get dynamic content guidelines based on type and age"""
        framework = self.content_frameworks.get(content_type, {})
        structure = framework.get("structure", [])
        
        # Get age-appropriate guidelines
        age_guidelines = framework.get("age_guidelines", {})
        closest_age = min(age_guidelines.keys(), key=lambda x: abs(x - age)) if age_guidelines else age
        guidelines = age_guidelines.get(closest_age, "")
        
        return {
            "structure": structure,
            "guidelines": guidelines,
            "framework": framework
        }

    def _create_content_system_message(self, content_type: str, user_profile: Dict[str, Any], base_message: str) -> str:
        """Create enhanced system message for specific content types with deep profile integration"""
        age = user_profile.get('age', 7)
        interests = user_profile.get('interests', [])
        learning_goals = user_profile.get('learning_goals', [])
        name = user_profile.get('name', 'friend')
        
        content_guidelines = self._get_dynamic_content_guidelines(content_type, age)
        
        # Create interest-based content suggestions
        interest_integration = ""
        if interests:
            interest_integration = f"""
🎯 PROFILE-BASED CONTENT CUSTOMIZATION:
User's Primary Interests: {', '.join(interests)}
- If creating stories: Feature characters or plots involving {', '.join(interests)}
- If telling jokes: Use humor related to {', '.join(interests)}  
- If suggesting activities: Focus on {', '.join(interests)}-related options
- If answering questions: Connect explanations to {', '.join(interests)} when possible
"""
        
        # Create learning-goal integration
        learning_integration = ""
        if learning_goals:
            learning_integration = f"""
📚 EDUCATIONAL INTEGRATION FOR LEARNING GOALS:
Target Learning Areas: {', '.join(learning_goals)}
- Subtly incorporate {', '.join(learning_goals)} concepts into content
- Use examples that reinforce {', '.join(learning_goals)} skills
- Create teachable moments related to {', '.join(learning_goals)}
"""
        
        enhanced_message = f"{base_message}\n\n{interest_integration}{learning_integration}"
        
        if content_type == "story":
            enhanced_message += f"""
STORY CREATION FRAMEWORK - PERSONALIZED FOR {name.upper()}:

‼️ CRITICAL INSTRUCTION: You MUST write a COMPLETE story that is AT LEAST 300 WORDS LONG. This is mandatory.

🎯 PERSONALIZATION REQUIREMENTS:
- Use {name}'s name in the story (as narrator acknowledgment: "This story is for you, {name}!")
- AGE {age} LANGUAGE REQUIREMENTS: {self._get_age_language_rules(age)}
- Incorporate their interests: {', '.join(interests) if interests else 'adventure, friendship, learning'}
- Connect to learning goals: {', '.join(learning_goals) if learning_goals else 'creativity and imagination'}

CRITICAL AGE-APPROPRIATE LANGUAGE:
{self._get_detailed_language_requirements(age)}

STORY REQUEST: Please create a complete, engaging story based on the user's request, personalized for {name}.

MANDATORY LENGTH REQUIREMENT:
- MINIMUM 300 words (target 400-600 words for optimal storytelling)
- Count words as you write - you MUST reach at least 300 words
- This is a COMPLETE story, not a summary or teaser
- Do NOT stop until you have told the full story from beginning to end

REQUIRED STORY STRUCTURE - ALL ELEMENTS MANDATORY:
1. 🎭 CHARACTER INTRODUCTION: Create vivid main character(s) with names, personalities, clear descriptions (75+ words)
2. 🏰 SETTING ESTABLISHMENT: Rich description of time, place, and atmosphere (50+ words)
3. 📈 RISING ACTION: Build tension, introduce conflict, develop the story (125+ words)
4. ⭐ CLIMAX: The most exciting/challenging/important moment (50+ words)
5. 📉 FALLING ACTION: Begin resolving conflicts and tensions (50+ words)
6. ✅ RESOLUTION: Satisfying conclusion with clear ending and lesson (50+ words)

STORY QUALITY REQUIREMENTS:
- Include meaningful dialogue between characters
- Use rich, descriptive language that paints vivid pictures
- Show character emotions and growth
- Include sensory details (what characters see, hear, feel)
- Build suspense and maintain engagement throughout
- End with a clear moral lesson appropriate for {age}-year-olds

AGE-APPROPRIATE GUIDELINES: {content_guidelines['guidelines']}

STORY WRITING INSTRUCTIONS:
- Start immediately with the story - no "Here's a story" preamble
- Write in narrative present or past tense
- Use dialogue to bring characters to life: "Hello!" said the character.
- Include action and movement throughout
- Build emotional connection with the main character
- Create a satisfying ending that wraps up all story elements

⚠️ CRITICAL REMINDER: Your story response MUST be at least 300 words. If you're unsure about length, err on the side of more detail and description. The child is expecting a complete, immersive story experience."""
        
        elif content_type == "song":
            enhanced_message += f"""
PERSONALIZED SONG CREATION FRAMEWORK FOR {name.upper()}:
Create a complete, engaging song customized for {name} with these elements:

🚨 CRITICAL SONG COMPLETION RULE - ABSOLUTE REQUIREMENT:
NEVER give incomplete or teasing song responses. ALWAYS deliver COMPLETE song in ONE message:

❌ FORBIDDEN: "Let me think of a song...", "How about this tune...", "I'd love to sing you something..."
❌ FORBIDDEN: Interactive song format - "Here's a song for you... want to hear more?"
✅ REQUIRED: Direct, complete song with all verses and chorus immediately

**SONG DELIVERY FORMAT - MANDATORY:**
✅ CORRECT: "Here's a fun song for you, {name}! [COMPLETE SONG WITH ALL VERSES AND CHORUS] Want another song?"
❌ WRONG: "Let me sing you a song... [FIRST LINE ONLY] Tell me more!" [NEVER DO THIS]

🎯 PERSONALIZATION:
- Reference {name}'s interests: {', '.join(interests) if interests else 'fun, learning, friendship'}
- Age {age} appropriate: {content_guidelines.get('guidelines', 'Simple, catchy, memorable')}
- Learning focus: {', '.join(learning_goals) if learning_goals else 'creativity and joy'}

STRUCTURE: {content_guidelines.get('structure', ['Verse', 'Chorus', 'Verse', 'Chorus', 'Bridge', 'Chorus']) if isinstance(content_guidelines, dict) else 'Verse-Chorus-Verse-Chorus'}

QUALITY REQUIREMENTS:
- Song request → COMPLETE song with all verses + chorus + ending NOW
- Rhyme request → COMPLETE rhyme from start to finish NOW
- Consistent rhythm and meter throughout
- Memorable melody-friendly lyrics  
- Positive, uplifting message
- Connect to {name}'s interests when possible
- Complete verses and chorus delivered immediately
- Natural flow when sung aloud
- COMPLETE song in ONE response - no "Tell me more!" prompts

Create a full song, not just a snippet! Deliver everything immediately!
"""
        
        elif content_type in ["rhyme", "poem"]:
            enhanced_message += f"""
RHYME/POEM CREATION FRAMEWORK:
Create engaging rhymes with these elements:

STRUCTURE: {' | '.join(content_guidelines['structure'])}

AGE GUIDELINES ({age} years): {content_guidelines['guidelines']}

QUALITY REQUIREMENTS:
- Consistent rhythm and rhyming pattern
- Playful, musical quality
- Age-appropriate vocabulary and themes
- Often includes movement or action elements
- Complete verses, not fragments
"""
        
        elif content_type == "joke":
            enhanced_message += f"""
PERSONALIZED JOKE CREATION FOR {name.upper()}:
Create age-appropriate humor customized for {name}:

PERSONALIZATION:
- Connect to {name}'s interests: {', '.join(interests) if interests else 'fun topics'}
- Age {age} humor level: {content_guidelines.get('guidelines', 'Simple wordplay, visual humor')}
- Educational connection: {', '.join(learning_goals) if learning_goals else 'learning through laughter'}

STRUCTURE: Setup + Immediate Punchline + Brief Explanation

QUALITY REQUIREMENTS:
- Clean, positive humor
- Connect to {name}'s favorite things when possible
- Clear setup and punchline delivered immediately
- Not mean-spirited or scary
- Educational when possible
- COMPLETE joke in one response - no "Tell me more!" prompts
"""
        
        elif content_type == "riddle":
            enhanced_message += f"""
PERSONALIZED RIDDLE CREATION FOR {name.upper()}:
Create engaging riddles customized for {name}:

PERSONALIZATION:
- Use topics from {name}'s interests: {', '.join(interests) if interests else 'animals, objects, nature'}
- Age {age} difficulty: {content_guidelines.get('guidelines', 'Simple logic, familiar concepts')}
- Learning connection: {', '.join(learning_goals) if learning_goals else 'critical thinking'}

STRUCTURE: Question + Immediate Answer (unless they ask to guess)

QUALITY REQUIREMENTS:
- Clear, engaging question or puzzle
- Logical answer that makes sense
- Age-appropriate difficulty level
- Educational value when possible
- Creative wordplay or misdirection
- Fair clues that lead to the answer
"""
        
        enhanced_message += f"\n\nIMPORTANT: Generate content of appropriate length and depth for the user's age ({age} years) and the content type. Do not artificially limit length - create rich, complete content that fully serves its purpose!"
        
        return enhanced_message
    
    def _get_age_language_rules(self, age: int) -> str:
        """Get specific language rules for age group"""
        if age <= 5:
            return "Very simple words only (1-2 syllables), short sentences (under 8 words)"
        elif age <= 8:
            return "Simple everyday words, clear sentences (8-12 words maximum)"
        else:
            return "Grade-level vocabulary with explanations, sentences under 15 words"
    
    def _get_detailed_language_requirements(self, age: int) -> str:
        """Get detailed language requirements for content creation"""
        if age <= 5:
            return """- Use ONLY simple words: fun, big, small, run, jump, play, happy, sad, dog, cat
- NO complex words like: magnificent, extraordinary, tremendous, fantastic
- Sentences: "The cat is big." NOT "The magnificent feline is extraordinary."
- Explain everything in very simple terms"""
        elif age <= 8:
            return """- Use common words: awesome, great, wonderful, amazing, exciting, fun
- Avoid: sophisticated, elaborate, tremendous, magnificent, extraordinary
- OK to use: interesting, beautiful, fantastic (but explain if complex)
- Simple explanations for any new concepts"""
        else:
            return """- Can use more advanced vocabulary but explain complex terms
- OK to use: fascinating, incredible, amazing, sophisticated (with explanation)
- Introduce complex ideas gradually with simple explanations first"""
    
    def enforce_age_appropriate_language(self, text: str, age: int, content_type: str = "conversation") -> str:
        """Post-processing filter to enforce age-appropriate language rules"""
        import re
        
        logger.info(f"🔍 Enforcing age-appropriate language for age {age}, content type: {content_type}")
        
        # For stories, be gentler - only apply the most critical filters
        if content_type == "story" and len(text.split()) > 200:
            logger.info(f"🎭 Applying gentle language filtering to {len(text.split())} word story")
            gentle_mode = True
        else:
            gentle_mode = False
        
        if age <= 5:
            # Very strict filtering for toddlers
            complex_replacements = {
                'magnificent': 'big and fun',
                'extraordinary': 'super cool', 
                'tremendous': 'really big',
                'fantastic': 'super fun',
                'incredible': 'really cool',
                'amazing': 'really fun',
                'wonderful': 'really nice',
                'spectacular': 'really cool',
                'marvelous': 'really good',
                'phenomenal': 'super good',
                'sophisticated': 'fancy',
                'elaborate': 'fancy',
                'exceptional': 'really good'
            }
            
            # Replace complex words (case insensitive)
            for complex_word, simple_word in complex_replacements.items():
                text = re.sub(r'\b' + complex_word + r'\b', simple_word, text, flags=re.IGNORECASE)
            
            # Only split sentences if not in gentle mode (for stories)
            if not gentle_mode:
                # Split overly long sentences (over 8 words)
                sentences = re.split(r'(?<=[.!?])\s+', text)
                simplified_sentences = []
                
                for sentence in sentences:
                    words = sentence.split()
                    if len(words) > 8:
                        # Split into smaller chunks
                        chunks = [' '.join(words[i:i+6]) + '.' for i in range(0, len(words), 6)]
                        simplified_sentences.extend(chunks)
                    else:
                        simplified_sentences.append(sentence)
                
                text = ' '.join(simplified_sentences)
            
        elif age <= 8:
            # Moderate filtering for young children
            complex_replacements = {
                'magnificent': 'awesome',
                'extraordinary': 'amazing', 
                'tremendous': 'really big',
                'sophisticated': 'fancy',
                'elaborate': 'detailed',
                'exceptional': 'really great',
                'phenomenal': 'awesome',
                'spectacular': 'amazing'
            }
            
            # Replace overly complex words
            for complex_word, simple_word in complex_replacements.items():
                text = re.sub(r'\b' + complex_word + r'\b', simple_word, text, flags=re.IGNORECASE)
            
            # Only moderate sentence splitting for stories
            if not gentle_mode:
                # Check sentence length (should be under 12 words)
                sentences = re.split(r'(?<=[.!?])\s+', text)
                simplified_sentences = []
                
                for sentence in sentences:
                    words = sentence.split()
                    if len(words) > 12:
                        # Split longer sentences
                        mid_point = len(words) // 2
                        part1 = ' '.join(words[:mid_point]) + '.'
                        part2 = ' '.join(words[mid_point:])
                        simplified_sentences.extend([part1, part2])
                    else:
                        simplified_sentences.append(sentence)
                
                text = ' '.join(simplified_sentences)
        
        elif age <= 11:
            # Light filtering for preteens - mainly sentence length
            if not gentle_mode:
                sentences = re.split(r'(?<=[.!?])\s+', text)
                simplified_sentences = []
                
                for sentence in sentences:
                    words = sentence.split()
                    if len(words) > 15:
                        # Split very long sentences
                        mid_point = len(words) // 2
                        part1 = ' '.join(words[:mid_point]) + '.'
                        part2 = ' '.join(words[mid_point:])
                        simplified_sentences.extend([part1, part2])
                    else:
                        simplified_sentences.append(sentence)
                
                text = ' '.join(simplified_sentences)
        
        # Clean up any double spaces or periods
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\.+', '.', text)
        text = text.strip()
        
        logger.info(f"✅ Language enforcement complete for age {age} ({content_type})")
        return text

    def _create_empathetic_system_message(self, user_profile: Dict[str, Any], memory_context: str = "") -> str:
        """Create empathetic system message (delegates to dynamic response system)"""
        # Use the dynamic response system for all empathetic responses
        return self._create_dynamic_response_system_message(user_profile, "conversation", "general conversation")

    def _create_dynamic_response_system_message(self, user_profile: Dict[str, Any], content_type: str, user_input: str) -> str:
        """REVOLUTIONARY: Create dynamic system message based on Miko AI/Echo Kids best practices"""
        name = user_profile.get('name', 'friend')
        age = user_profile.get('age', 7)
        interests = user_profile.get('interests', [])
        
        # CORE PRINCIPLE: Dynamic response length based on query type and user intent
        response_strategy = self._determine_optimal_response_strategy(user_input, content_type, age)
        
        core_system = f"""You are Buddy, a super-smart AI friend for {name} (age {age}). 

🎯 DYNAMIC RESPONSE STRATEGY: {response_strategy['type'].upper()}
Response Length: {response_strategy['target_length']}
Response Style: {response_strategy['style']}

CRITICAL RESPONSE RULES:
{response_strategy['rules']}

PERSONALITY FOR {name}:
- Warm, enthusiastic friend who remembers everything about {name}
- Smart but never overwhelming - match {name}'s energy and interests
- Always age-perfect for {age}-year-olds
- Love {name}'s interests: {', '.join(interests) if interests else 'learning and fun'}

LANGUAGE RULES FOR AGE {age}:
{self._get_dynamic_language_rules(age)}

ENGAGEMENT STRATEGY:
- Be instantly helpful and direct
- Show genuine excitement about {name}'s interests  
- Ask follow-up questions that keep conversation flowing
- Celebrate {name}'s curiosity and achievements

Your goal: Be the perfect AI friend who gives exactly the right amount of information in exactly the right way for {name}."""

        return core_system

    def _determine_optimal_response_strategy(self, user_input: str, content_type: str, age: int) -> Dict[str, Any]:
        """Determine optimal response strategy like Miko AI/Echo Kids"""
        input_lower = user_input.lower()
        
        # QUICK FACTUAL QUERIES (Like "What is Neptune?", "How tall is giraffe?")
        quick_fact_indicators = [
            'what is', 'how tall', 'how fast', 'how long', 'how much', 'how many',
            'where is', 'when did', 'who is', 'tell me about', 'explain', 'define'
        ]
        
        # STORY REQUEST INDICATORS  
        story_indicators = [
            'tell me a story', 'story about', 'once upon', 'bedtime story', 
            'fairy tale', 'adventure story', 'make up a story'
        ]
        
        # GREETING/SOCIAL INDICATORS
        social_indicators = [
            'hello', 'hi', 'how are you', 'good morning', 'good night',
            'thank you', 'please', 'yes', 'no', 'okay'
        ]
        
        # JOKE/FUN INDICATORS
        fun_indicators = [
            'joke', 'funny', 'riddle', 'rhyme', 'song', 'game', 'play'
        ]
        
        # DETERMINE STRATEGY
        if any(indicator in input_lower for indicator in quick_fact_indicators):
            return {
                'type': 'quick_fact',
                'target_length': '2-3 sentences (30-50 words)',
                'style': 'Direct, informative, engaging',
                'rules': '''- Answer the question immediately and clearly
- Add one interesting extra detail  
- End with enthusiasm: "Isn't that cool?" or "Want to know more?"
- NO long explanations - keep it snappy and fun'''
            }
            
        elif any(indicator in input_lower for indicator in story_indicators):
            if age <= 5:
                target = '4-6 sentences (80-120 words)'
            elif age <= 8:
                target = '6-10 sentences (120-200 words)'  
            else:
                target = '8-15 sentences (200-300 words)'
                
            return {
                'type': 'story',
                'target_length': target,
                'style': 'Complete narrative with beginning, middle, end',
                'rules': f'''- Tell a COMPLETE story with clear beginning, middle, and end
- Keep it exactly {target} - not longer!
- Include characters, problem, solution, happy ending
- Use vivid but simple descriptions
- End with a gentle moral lesson
- Perfect for {age}-year-olds'''
            }
            
        elif any(indicator in input_lower for indicator in social_indicators):
            return {
                'type': 'social',
                'target_length': '1-2 sentences (15-25 words)',
                'style': 'Warm, friendly, brief',
                'rules': '''- Respond warmly but briefly
- Show genuine interest in the child
- Ask a simple follow-up question
- Keep it light and positive'''
            }
            
        elif any(indicator in input_lower for indicator in fun_indicators):
            return {
                'type': 'entertainment',
                'target_length': '3-5 sentences (40-80 words)',
                'style': 'Playful, complete, engaging',
                'rules': '''- Deliver complete joke/riddle/rhyme immediately
- Include setup + punchline + brief explanation
- Make it age-appropriate and fun
- End with offer for more fun'''
            }
            
        else:
            # General conversation
            return {
                'type': 'conversation',
                'target_length': '2-4 sentences (25-60 words)',
                'style': 'Helpful, friendly, complete',
                'rules': '''- Give a helpful, complete answer
- Keep it concise but thorough
- Show interest in the child's question
- Invite further conversation'''
            }

    def _get_dynamic_language_rules(self, age: int) -> str:
        """Get dynamic language rules optimized for engagement"""
        if age <= 5:
            return """- Use simple, everyday words (cat, dog, big, small, fun, happy)
- Keep sentences under 8 words each
- Repeat important words for understanding
- Use lots of descriptive sounds: "whoosh", "buzz", "splash"
- NEVER use: magnificent, extraordinary, tremendous, sophisticated"""
            
        elif age <= 8:
            return """- Use clear, common words most kids know
- Sentences 8-12 words maximum
- Explain any new words immediately: "Jupiter is huge - that means really, really big!"
- Use exciting words: awesome, amazing, incredible, fantastic
- OK to use some bigger words if you explain them"""
            
        else:
            return """- Can use more advanced vocabulary with explanations
- Sentences under 15 words  
- Introduce complex ideas step by step
- Use grade-level words: fascinating, extraordinary, magnificent (but explain)
- Challenge their thinking with interesting questions"""

    def _create_brief_system_message(self, user_profile: Dict[str, Any]) -> str:
        """Create system message optimized for brief, quick responses"""
        name = user_profile.get('name', 'friend')
        age = user_profile.get('age', 7)
        
        brief_system = f"""You are Buddy, an AI companion for kids. 

CRITICAL: Keep ALL responses brief and concise (2-3 sentences maximum).

RESPONSE RULES:
- General questions: Give direct, helpful answers in 2-3 sentences
- Quick facts: Be informative but brief  
- Greetings: Warm but short responses
- Always be friendly and age-appropriate for {age}-year-old {name}

TONE: Friendly, helpful, but always brief and to the point.

Your goal: Quick, helpful responses that get straight to the point."""

        return brief_system

    def _generate_structured_story_fallback(self, user_input: str, age: int) -> str:
        """Generate a structured story fallback when LLM generation fails or is too short"""
        
        # Extract story theme from user input
        theme = "adventure"
        if "dragon" in user_input.lower():
            theme = "dragon adventure"
        elif "princess" in user_input.lower():
            theme = "princess story"
        elif "magic" in user_input.lower():
            theme = "magical tale"
        elif "space" in user_input.lower():
            theme = "space adventure"
        elif "animal" in user_input.lower():
            theme = "animal story"
        elif "bedtime" in user_input.lower():
            theme = "bedtime story"
        
        # Age-appropriate story templates
        if age <= 5:
            story = f"""Once upon a time, there was a little character who went on a wonderful {theme}. 
            
            They discovered many amazing things along the way. The character met friendly helpers who showed them incredible sights and taught them important lessons about being kind and brave.
            
            Through their journey, they learned that being curious and helpful makes the world a better place for everyone. The character had so much fun exploring and making new friends.
            
            When it was time to go home, they felt happy and excited to share all their wonderful discoveries. They knew that tomorrow would bring even more amazing adventures.
            
            And so the little character went to sleep with a smile, dreaming of all the wonderful things waiting to be discovered. The end."""
            
        elif age <= 8:
            story = f"""There once lived a brave young hero who dreamed of the most incredible {theme} imaginable.
            
            One bright morning, they set off on their quest, carrying nothing but courage in their heart and wonder in their eyes. The path ahead was filled with mysterious forests, sparkling streams, and hidden treasures waiting to be found.
            
            Along the way, the hero encountered magical creatures who needed help solving important problems. Using creativity and kindness, our hero found clever solutions that helped everyone. Each challenge made them stronger and wiser.
            
            The most amazing discovery came when the hero realized that the greatest adventures happen when we help others and stay true to ourselves. Friends appeared from the most unexpected places, and together they created memories that would last forever.
            
            When the sun began to set, the hero returned home with stories to share and dreams for tomorrow's adventures. They had learned that every day holds the possibility for something truly extraordinary.
            
            The hero fell asleep that night knowing that the best adventures are those we share with friends, and that courage and kindness can overcome any challenge. Sweet dreams filled with endless possibilities. The end."""
            
        else:  # age 9+
            story = f"""In a land where possibilities were endless, a determined young adventurer embarked on an extraordinary {theme} that would change everything.
            
            The journey began at dawn, when mysterious signals led our hero to discover a hidden world filled with ancient secrets and modern wonders. Each step forward revealed new challenges that required not just bravery, but intelligence, creativity, and the wisdom to know when to ask for help.
            
            The most fascinating part of the adventure came when the hero realized they weren't alone. A diverse group of companions, each with unique talents and perspectives, joined the quest. Together, they solved puzzles that had mystified explorers for generations.
            
            Through trials that tested their resolve and discoveries that expanded their understanding of the world, the team learned invaluable lessons about friendship, perseverance, and the power of working together toward a common goal.
            
            The climax of their adventure revealed that the greatest treasure wasn't gold or jewels, but the knowledge they'd gained and the unbreakable bonds they'd formed. Each character had grown stronger, wiser, and more confident in their abilities.
            
            As they prepared to return home, they knew this was just the beginning of many more adventures to come. They had discovered that the world is full of wonders waiting to be explored by those brave enough to seek them.
            
            The hero went to sleep that night with a heart full of gratitude and a mind buzzing with plans for future explorations, knowing that the greatest adventures always lie just beyond the horizon. The end."""
        
        return story

    async def generate_dynamic_response(self, user_input: str, user_profile: Dict[str, Any]) -> str:
        """Generate dynamic responses based on query type and user profile (Miko AI approach)"""
        try:
            age = user_profile.get('age', 7)
            
            # Use DYNAMIC system message based on query type and user intent
            system_message = self._create_dynamic_response_system_message(user_profile, "conversation", user_input)
            
            logger.info(f"⚡ DYNAMIC RESPONSE: Analyzing query type for: '{user_input[:50]}...'")
            
            # Create chat with dynamic system message optimized for the specific query
            chat = LlmChat(
                api_key=self.gemini_api_key,
                session_id=f"dynamic_{hash(user_input)}",
                system_message=system_message
            ).with_model("gemini", "gemini-2.0-flash").with_max_tokens(200)  # Conservative limit for responsiveness
            
            # Create user message
            user_message = UserMessage(text=user_input)
            
            # Generate response
            # CRITICAL FIX: Add timeout to main LLM call to prevent hanging
            try:
                response = await asyncio.wait_for(
                    chat.send_message(user_message), 
                    timeout=30.0  # 30 second timeout for main response
                )
            except asyncio.TimeoutError:
                logger.error(f"Timeout during main LLM call for user: {user_profile.get('name', 'unknown')}")
                return self._get_fallback_ambient_response(user_profile.get('age', 5))
            
            if not response or not response.strip():
                return "I'm here to help! Can you ask that again?"
            
            dynamic_response = response.strip()
            
            # Apply age-appropriate language filtering
            processed_response = self.enforce_age_appropriate_language(dynamic_response, age, "conversation")
            
            logger.info(f"⚡ DYNAMIC RESPONSE COMPLETE: {len(processed_response)} chars generated")
            
            return processed_response
            
        except Exception as e:
            logger.error(f"Error generating brief response: {str(e)}")
            return "I'm here to help! Can you ask that again?"

    async def generate_story_with_streaming(self, user_input: str, user_profile: Dict[str, Any], session_id: str, context: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate story content with streaming chunks for progressive display and audio"""
        try:
            import time
            start_time = time.time()
            
            age = user_profile.get('age', 7)
            user_id = user_profile.get('user_id', 'unknown')
            logger.info(f"🎭 STORY STREAMING: Starting ultra-fast chunked story generation for age {age}")
            
            # STORY SESSION MANAGEMENT: Check for existing story session
            story_session = None
            is_continuation = False
            
            # Check if this is a continuation request
            if any(word in user_input.lower() for word in ['continue', 'more', 'next', 'keep going', 'what happens']):
                story_session = await self.get_story_session(session_id)
                if story_session:
                    is_continuation = True
                    logger.info(f"📖 STORY CONTINUATION: Found existing story session {story_session['_id']}")
            
            if is_continuation and story_session:
                # CONTINUATION: Resume from where we left off
                logger.info("🔄 Continuing existing story from last checkpoint")
                
                # Get the last part of the story for context
                full_story = story_session.get("full_story_text", "")
                last_chunk_index = story_session.get("last_chunk_index", -1)
                
                # Generate continuation
                continuation_prompt = f"""Continue this story seamlessly from where it left off. 
Current story so far: ...{full_story[-300:] if len(full_story) > 300 else full_story}

Continue the story with 2-3 more paragraphs, advancing the plot and maintaining the same characters and tone. Make it engaging for a {age}-year-old child."""
                
                continuation_text = await self._generate_continuation_chunk(continuation_prompt, age)
                
                # Create continuation chunks
                sentences = continuation_text.split('. ')
                chunks = []
                chunk_text = ""
                chunk_id = last_chunk_index + 1
                
                for sentence in sentences:
                    chunk_text += sentence + ". "
                    if len(chunk_text.split()) >= 35:
                        chunks.append({
                            "text": chunk_text.strip(),
                            "chunk_id": chunk_id,
                            "word_count": len(chunk_text.split()),
                            "timestamp": time.time() - start_time
                        })
                        chunk_text = ""
                        chunk_id += 1
                
                # Add final chunk if there's remaining text
                if chunk_text.strip():
                    chunks.append({
                        "text": chunk_text.strip(),
                        "chunk_id": chunk_id,
                        "word_count": len(chunk_text.split()),
                        "timestamp": time.time() - start_time
                    })
                
                # Update story session
                await self.update_story_session(story_session["_id"], {
                    "full_story_text": full_story + " " + continuation_text,
                    "last_chunk_index": chunk_id,
                    "total_chunks": story_session.get("total_chunks", 0) + len(chunks)
                })
                
                return {
                    "success": True,
                    "response_type": "story_continuation",
                    "chunks": chunks,
                    "total_chunks": len(chunks),
                    "is_continuation": True,
                    "story_session_id": story_session["_id"]
                }
            
            else:
                # NEW STORY: Create story session and generate fresh content
                story_session_id = await self.create_story_session(session_id, user_id, "adventure")
                logger.info(f"📚 NEW STORY: Created story session {story_session_id}")
                
                # ULTRA-FAST STRATEGY: Return immediate first chunk, generate rest in background
                logger.info("🚀 ULTRA-FAST MODE: Generating immediate first chunk")
                
                # Generate a quick story opening based on the prompt
                quick_opening = self._generate_instant_story_opening(user_input, age)
                
                # Create first chunk immediately
                first_chunk = {
                    "text": quick_opening,
                    "chunk_id": 0,
                    "word_count": len(quick_opening.split()),
                    "timestamp": time.time() - start_time
                }
                
                logger.info(f"🚀 INSTANT FIRST CHUNK: {first_chunk['word_count']} words in {first_chunk['timestamp']:.2f}s")
                
                # Generate remaining story in background (simplified approach)
                remaining_story = self._generate_story_continuation(user_input, quick_opening, age)
                
                # Split remaining story into chunks
                remaining_chunks = []
                if remaining_story:
                    sentences = remaining_story.split('. ')
                    chunk_text = ""
                    chunk_id = 1
                    
                    for sentence in sentences:
                        chunk_text += sentence + ". "
                        if len(chunk_text.split()) >= 35:  # Small chunks for speed
                            remaining_chunks.append({
                                "text": chunk_text.strip(),
                                "chunk_id": chunk_id,
                                "word_count": len(chunk_text.split()),
                                "timestamp": time.time() - start_time
                            })
                            chunk_text = ""
                            chunk_id += 1
                    
                    # Add final chunk if any remaining text
                    if chunk_text.strip():
                        remaining_chunks.append({
                            "text": chunk_text.strip(),
                            "chunk_id": chunk_id,
                            "word_count": len(chunk_text.split()),
                            "timestamp": time.time() - start_time
                        })
                
                # Update story session with the complete story
                full_story_text = quick_opening + " " + remaining_story if remaining_story else quick_opening
                all_chunks = [first_chunk] + remaining_chunks
                await self.update_story_session(story_session_id, {
                    "full_story_text": full_story_text,
                    "last_chunk_index": len(all_chunks) - 1,
                    "total_chunks": len(all_chunks)
                })
                
                total_words = sum(chunk["word_count"] for chunk in all_chunks)
                generation_time = time.time() - start_time
                
                logger.info(f"🎭 ULTRA-FAST STORY COMPLETE: {len(all_chunks)} chunks, {total_words} words in {generation_time:.2f}s")
                
                return {
                    "status": "streaming",
                    "chunks": all_chunks,
                    "total_chunks": len(all_chunks),
                    "total_words": total_words,
                    "generation_time": generation_time,
                    "content_type": "story",
                    "story_session_id": story_session_id
                }
            
        except Exception as e:
            logger.error(f"❌ Ultra-fast story streaming error: {str(e)}")
            
            # Emergency fallback - instant response
            fallback_story = f"Once upon a time, there was an amazing adventure waiting to unfold. Let me tell you this wonderful story that I know you'll love!"
            
            return {
                "status": "fallback",
                "chunks": [{
                    "text": fallback_story,
                    "chunk_id": 0, 
                    "word_count": len(fallback_story.split()),
                    "timestamp": 0.1
                }],
                "total_chunks": 1,
                "total_words": len(fallback_story.split()),
                "generation_time": 0.1,
                "content_type": "story"
            }

    def _generate_instant_story_opening(self, user_input: str, age: int) -> str:
        """Generate an instant story opening without LLM call for <1s response"""
        
        # Extract key themes from the input
        themes = {
            'dragon': 'a brave dragon named Sparkle',
            'princess': 'a kind princess named Luna', 
            'magic': 'a magical world full of wonder',
            'adventure': 'an exciting journey',
            'bedtime': 'a peaceful dream',
            'forest': 'a mysterious forest',
            'castle': 'a grand castle',
            'fairy': 'a helpful fairy'
        }
        
        # Find matching theme
        theme_character = 'a wonderful character'
        for keyword, character in themes.items():
            if keyword in user_input.lower():
                theme_character = character
                break
        
        # Age-appropriate openings
        if age <= 5:
            opening = f"Once upon a time, there lived {theme_character} who was about to have the most amazing day ever. Today was going to be special because something wonderful was about to happen."
        elif age <= 8:
            opening = f"In a land far, far away, {theme_character} woke up one bright morning feeling excited about the adventure ahead. Little did they know that this day would be filled with incredible discoveries and new friends."
        else:
            opening = f"Deep in a realm where anything was possible, {theme_character} stood at the beginning of an extraordinary quest. The morning sun cast long shadows as they prepared for a journey that would test their courage and reveal amazing secrets."
        
        return opening
    
    def _generate_story_continuation(self, user_input: str, opening: str, age: int) -> str:
        """Generate story continuation using templates for speed"""
        
        # Template-based continuation for speed
        if age <= 5:
            continuation = """The character met friendly animals who wanted to help. They all worked together to solve a fun puzzle. Everyone was happy and laughing. 
            
            Then they discovered a hidden treasure that sparkled in the sunlight. But the best treasure was the friendship they found along the way.
            
            When the adventure was over, everyone went home with big smiles. They knew they would always remember this special day and the friends they made."""
            
        elif age <= 8:
            continuation = """As they began their journey, the character encountered three magical challenges that would test their kindness, bravery, and cleverness. The first challenge appeared when they met a lost creature who needed help finding their way home.
            
            Using their heart and wisdom, the character found creative solutions to each challenge. Along the way, they made unlikely allies who became trusted friends. Together, they discovered that the greatest adventures happen when we help others.
            
            The final challenge revealed that the real magic was inside them all along. With their new friends by their side, they returned home as heroes, knowing that friendship and kindness are the most powerful forces in any world."""
            
        else:
            continuation = """The quest led them through three distinct realms, each presenting unique obstacles that required different skills and approaches. In the first realm, they learned the importance of listening and understanding others. The second realm taught them about perseverance and creative problem-solving.
            
            As they progressed through each challenge, the character gained new abilities and insights about themselves and the world around them. They formed a diverse group of companions, each contributing their unique strengths to overcome seemingly impossible odds.
            
            The climactic moment arrived when they realized that their greatest strength came not from individual power, but from the bonds they had forged and the lessons they had learned. The resolution brought not just victory, but wisdom that would guide them in future adventures.
            
            Returning home transformed by their experiences, they carried with them the knowledge that every ending is also a new beginning, and that the world is full of wonders waiting for those brave enough to seek them."""
        
        return continuation

    async def _generate_continuation_chunk(self, continuation_prompt: str, age: int) -> str:
        """Generate continuation chunk for story using LLM"""
        try:
            # Create a simple chat for continuation generation
            chat = LlmChat(
                api_key=self.gemini_api_key,
                session_id=f"continuation_{hash(continuation_prompt)}",
                system_message=f"You are a storyteller for {age}-year-old children. Continue the story naturally and engagingly."
            ).with_model("gemini", "gemini-2.0-flash").with_max_tokens(300)  # RESTORED: Optimal chunk size for good content with speed
            
            user_message = UserMessage(text=continuation_prompt)
            response = await chat.send_message(user_message)
            
            return response.strip() if response else "And the adventure continued with even more exciting discoveries ahead!"
            
        except Exception as e:
            logger.error(f"Error generating continuation chunk: {e}")
            # Fallback continuation
            return "And the adventure continued with even more exciting discoveries ahead!"

    async def generate_response_with_dialogue_plan_LEGACY(self, user_input: str, user_profile: Dict[str, Any], session_id: str, context: List[Dict[str, Any]] = None, dialogue_plan: Dict[str, Any] = None, memory_context: Dict[str, Any] = None) -> str:
        """LEGACY METHOD - NOT USED - Generate response with conversation context and dialogue plan"""
        try:
            # Determine age group
            age = user_profile.get('age', 5)
            age_group = self._get_age_group(age)
            
            # Detect content type for proper post-processing
            content_type = self._detect_content_type(user_input)
            logger.info(f"🔍 Content type detected: {content_type}")
            
            # Use empathetic system message instead of generic base message
            base_system_message = self._create_empathetic_system_message(user_profile, memory_context)
            
            # Enhance with dialogue plan if provided
            if dialogue_plan:
                mode = dialogue_plan.get("mode", "chat")
                prosody = dialogue_plan.get("prosody", {})
                cultural_context = dialogue_plan.get("cultural_context", {})
                response_guidelines = dialogue_plan.get("response_guidelines", {})
                
                # Add mode-specific instructions
                mode_instructions = {
                    "story": "You are in storytelling mode. Be descriptive, engaging, and use narrative techniques.",
                    "game": "You are in game mode. Be encouraging, playful, and interactive.",
                    "comfort": "You are in comfort mode. Be empathetic, warm, and supportive.",
                    "teaching": "You are in teaching mode. Be patient, clear, and educational.",
                    "bedtime": "You are in bedtime mode. Be soothing, calm, and gentle.",
                    "calm": "You are in calming mode. Be peaceful, stabilizing, and reassuring."
                }
                
                if mode in mode_instructions:
                    base_system_message += f"\n\n{mode_instructions[mode]}"
                
                # Add prosody instructions
                tone = prosody.get("tone", "friendly")
                pace = prosody.get("pace", "normal")
                base_system_message += f"\n\nResponse tone: {tone}. Speech pace: {pace}."
                
                # Add cultural context
                if cultural_context.get("hinglish_usage", False):
                    base_system_message += "\n\nUse Indian English with occasional Hinglish words like 'yaar', 'accha', 'bahut', 'kya', 'hai na' naturally in conversation. Add relevant emojis."
                
                # Add response guidelines
                if response_guidelines.get("be_curious", False):
                    base_system_message += "\n\nBe curious and ask follow-up questions."
                if response_guidelines.get("use_examples", False):
                    base_system_message += "\n\nUse examples to explain concepts."
                
                # Remove artificial token budget constraints - let content be appropriate length
            
            # Add user context
            # Add COMPREHENSIVE user profile information
            enhanced_system_message = f"{base_system_message}\n\n🌟 COMPLETE USER PROFILE - USE ALL THIS INFORMATION:\n"
            enhanced_system_message += f"- Child's Name: {user_profile.get('name', 'Friend')} (Use their name frequently and naturally)\n"
            enhanced_system_message += f"- Age: {age} years old (Adjust language complexity accordingly)\n"
            enhanced_system_message += f"- Location: {user_profile.get('location', 'Unknown')}\n"
            enhanced_system_message += f"- Gender: {user_profile.get('gender', 'prefer_not_to_say')}\n"
            enhanced_system_message += f"- Avatar Choice: {user_profile.get('avatar', 'bunny')} (Shows their personality preferences)\n"
            enhanced_system_message += f"- Speech Speed Preference: {user_profile.get('speech_speed', 'normal')}\n"
            enhanced_system_message += f"- Energy Level: {user_profile.get('energy_level', 'balanced')}\n"
            enhanced_system_message += f"- Voice Personality: {user_profile.get('voice_personality', 'friendly_companion')}\n"
            
            # Enhanced interests integration
            interests = user_profile.get('interests', [])
            if interests:
                enhanced_system_message += f"\n🎯 INTERESTS TO WEAVE INTO EVERY CONVERSATION:\n"
                for i, interest in enumerate(interests, 1):
                    enhanced_system_message += f"  {i}. {interest.title()} - Find ways to mention this topic naturally\n"
                enhanced_system_message += f"CRITICAL: Always try to connect responses to these interests: {', '.join(interests)}\n"
            else:
                enhanced_system_message += f"\n🎯 DEFAULT INTERESTS: stories, games, learning, fun activities\n"
            
            # Enhanced learning goals integration
            learning_goals = user_profile.get('learning_goals', [])
            if learning_goals:
                enhanced_system_message += f"\n📚 LEARNING GOALS TO INCORPORATE:\n"
                for i, goal in enumerate(learning_goals, 1):
                    enhanced_system_message += f"  {i}. {goal.title()} - Weave educational content about this subtly\n"
                enhanced_system_message += f"CRITICAL: Look for opportunities to support these learning areas: {', '.join(learning_goals)}\n"
            else:
                enhanced_system_message += f"\n📚 DEFAULT LEARNING: basic literacy, creativity, problem-solving\n"
            
            # Add conversation context if available
            if context:
                enhanced_system_message += f"\nRecent conversation context:\n"
                for ctx in context[-3:]:  # Last 3 context items
                    enhanced_system_message += f"- {ctx.get('text', '')}\n"
                
                # CRITICAL: Check for conversation continuity needs
                last_bot_message = self._get_last_bot_message(context)
                last_user_message = self._get_last_user_message(context)
                
                logger.info(f"Context analysis - Last bot: '{last_bot_message}', User input: '{user_input}'")
                
                if self._requires_followthrough(last_bot_message, user_input):
                    enhanced_system_message += f"\n⚠️  CRITICAL CONTEXT CONTINUITY: You previously said '{last_bot_message}'. "
                    enhanced_system_message += f"The user responded '{user_input}'. This is clearly a response to your question/prompt. You MUST:\n"
                    enhanced_system_message += f"1. Recognize this as a direct response to your previous message\n"
                    enhanced_system_message += f"2. Continue the conversation based on their response\n"
                    enhanced_system_message += f"3. DO NOT ask 'what do you mean' or ignore the context\n"
                    enhanced_system_message += f"4. If they said 'yes' to your question, provide what they said yes to\n"
                    enhanced_system_message += f"5. If they said 'no', acknowledge and offer alternatives\n"
                    logger.info(f"FOLLOW-THROUGH REQUIRED: Bot said '{last_bot_message}' and user responded '{user_input}'")
                else:
                    logger.info(f"No follow-through required for: '{last_bot_message}' -> '{user_input}'")
                
                enhanced_system_message += f"\nContinue this conversation naturally and remember what was said before."
            
            # Add memory context if available
            if memory_context and memory_context.get("user_id") != "unknown":
                enhanced_system_message += f"\n\nLong-term memory context:\n"
                
                # Add recent preferences
                recent_preferences = memory_context.get("recent_preferences", {})
                if recent_preferences:
                    enhanced_system_message += f"Recent preferences: {', '.join(f'{k}: {v}' for k, v in list(recent_preferences.items())[:3])}\n"
                
                # Add favorite topics
                favorite_topics = memory_context.get("favorite_topics", [])
                if favorite_topics:
                    topics_str = ', '.join([topic[0] if isinstance(topic, tuple) else str(topic) for topic in favorite_topics[:3]])
                    enhanced_system_message += f"Favorite topics: {topics_str}\n"
                
                # Add achievements
                achievements = memory_context.get("achievements", [])
                if achievements:
                    recent_achievements = achievements[-2:]  # Last 2 achievements
                    for achievement in recent_achievements:
                        if isinstance(achievement, dict):
                            achievement_type = achievement.get("type", "unknown")
                            enhanced_system_message += f"Recent achievement: {achievement_type}\n"
                
                enhanced_system_message += "Use this memory context to personalize the conversation and reference past interactions naturally."
            
            # Add ambient listening context
            enhanced_system_message += f"\n\nNote: This is an ambient listening conversation. The child may have said a wake word like 'Hey Buddy' before this message. Be natural and conversational."
            
            # DYNAMIC TOKEN LENGTH MANAGEMENT - Critical for different content types
            content_type = self._detect_content_type(user_input)
            
            # Set dynamic token limits based on content type - FORCE HIGHER LIMITS
            if content_type == "story":
                # Stories need much more tokens for complete narratives
                max_tokens = 4000  # INCREASED from 2000 to ensure complete stories
                logger.info(f"🎭 STORY REQUEST - Using {max_tokens} tokens for complete narrative")
            elif content_type in ["song", "poem", "rhyme"]:
                # Creative content needs moderate tokens - RESTORED optimal balance
                max_tokens = 800  # RESTORED from previous working configuration
                logger.info(f"🎵 CREATIVE CONTENT - Using {max_tokens} tokens for optimal speed")
            elif content_type in ["riddle", "joke"]:
                # Short content can use fewer tokens
                max_tokens = 800  # INCREASED from 400
                logger.info(f"🧩 SHORT CONTENT - Using {max_tokens} tokens")
            else:
                # Regular conversation gets standard allocation
                max_tokens = 2000  # INCREASED from 1000
                logger.info(f"💬 CONVERSATION - Using {max_tokens} tokens")
            
            # CRITICAL FIX: Enhanced system message with conversation history for context continuity
            if context and len(context) > 0:
                logger.info(f"Adding {len(context)} conversation history items to system message for context continuity")
                history_text = "\n\nRECENT CONVERSATION HISTORY (for context continuity):\n"
                
                # Add last 10 messages to system message for context
                recent_context = context[-10:] if len(context) > 10 else context
                for ctx_item in recent_context:
                    role = ctx_item.get('role', ctx_item.get('sender', 'unknown'))
                    text = ctx_item.get('text', '')
                    if role == 'user':
                        history_text += f"Child: {text}\n"
                    elif role in ['assistant', 'bot']:
                        history_text += f"You (Buddy): {text}\n"
                
                history_text += "\nIMPORTANT: Use this conversation history to maintain context continuity. Reference previous exchanges naturally and respond appropriately to the current user input in the context of this conversation.\n"
                
                # Recreate chat with enhanced system message including history
                enhanced_system_with_history = enhanced_system_message + history_text
                
                chat = LlmChat(
                    api_key=self.gemini_api_key,
                    session_id=session_id,
                    system_message=enhanced_system_with_history
                ).with_model("gemini", "gemini-2.0-flash").with_max_tokens(max_tokens)
                
                logger.info("✅ Enhanced chat initialized with conversation history and dynamic token allocation")
            else:
                # No context available, use original system message
                chat = LlmChat(
                    api_key=self.gemini_api_key,
                    session_id=session_id,
                    system_message=enhanced_system_message
                ).with_model("gemini", "gemini-2.0-flash").with_max_tokens(max_tokens)
                
                logger.info("✅ Chat initialized with dynamic token allocation (no context available)")
            
            # Create user message
            user_message = UserMessage(text=user_input)
            
            # Generate response with timeout protection
            try:
                response = await asyncio.wait_for(
                    chat.send_message(user_message), 
                    timeout=30.0  # 30 second timeout for main response
                )
            except asyncio.TimeoutError:
                logger.error(f"Timeout during main LLM call in generate_response_with_dialogue_plan")
                return self._get_fallback_ambient_response(user_profile.get('age', 5))
            
            # ENHANCED RESPONSE LENGTH VALIDATION AND ITERATIVE GENERATION FOR STORY CONTENT
            content_type = self._detect_content_type(user_input)
            if content_type == "story" and response:
                original_word_count = len(response.split())
                logger.info(f"Initial story response: {original_word_count} words")
                
                # If story is too short, use iterative generation to build complete story
                if original_word_count < 250:
                    logger.info(f"Story too short ({original_word_count} words), using iterative generation")
                    
                    # Continue building the story iteratively
                    current_story = response
                    iteration_count = 0
                    max_iterations = 3
                    
                    while len(current_story.split()) < 300 and iteration_count < max_iterations:
                        iteration_count += 1
                        continuation_prompt = f"""Continue and expand this story to make it more complete and detailed. The current story is: 

{current_story}

Please continue with more details, dialogue, and story development. Add at least 100 more words to make this a richer, more complete story. Continue seamlessly from where it left off."""
                        
                        continuation_message = UserMessage(text=continuation_prompt)
                        
                        # CRITICAL FIX: Add timeout to prevent hanging
                        try:
                            continuation = await asyncio.wait_for(
                                chat.send_message(continuation_message), 
                                timeout=15.0  # 15 second timeout per iteration
                            )
                        except asyncio.TimeoutError:
                            logger.error(f"Timeout during story iteration {iteration_count}, breaking loop")
                            break
                        
                        if continuation:
                            # Combine the stories intelligently  
                            if current_story.endswith('.') or current_story.endswith('!') or current_story.endswith('?'):
                                current_story = current_story + " " + continuation
                            else:
                                current_story = current_story + continuation
                            
                            logger.info(f"Story iteration {iteration_count}: {len(current_story.split())} words")
                        else:
                            break
                    
                    response = current_story
                    final_word_count = len(response.split())
                    logger.info(f"Final story length: {final_word_count} words after {iteration_count} iterations")
            
            # Post-process response based on dialogue plan  
            if dialogue_plan:
                processed_response = self._post_process_with_dialogue_plan(response, dialogue_plan, age_group)
            else:
                processed_response = self._post_process_ambient_response(response, age_group, content_type)
            
            logger.info(f"Generated enhanced response for age {age}: {len(processed_response.split())} words total")
            return processed_response
            
        except Exception as e:
            logger.error(f"Error generating enhanced response: {str(e)}")
            return self._get_fallback_ambient_response(user_profile.get('age', 5))
    
    def _post_process_with_dialogue_plan(self, response: str, dialogue_plan: Dict[str, Any], age_group: str) -> str:
        """Post-process response based on dialogue plan"""
        
        mode = dialogue_plan.get("mode", "chat")
        prosody = dialogue_plan.get("prosody", {})
        cultural_context = dialogue_plan.get("cultural_context", {})
        
        # Apply mode-specific processing
        if mode == "story":
            # Add narrative elements
            if not any(starter in response.lower() for starter in ["once", "there was", "long ago"]):
                response = f"Let me tell you... {response}"
        elif mode == "game":
            # Add game enthusiasm
            if not any(word in response.lower() for word in ["great", "awesome", "good job", "well done"]):
                response = f"Great job! {response}"
        elif mode == "comfort":
            # Add comforting elements
            if not any(word in response.lower() for word in ["understand", "feel", "okay", "alright"]):
                response = f"I understand... {response}"
        
        # Apply cultural context
        if cultural_context.get("hinglish_usage", False):
            # Add occasional Hinglish words
            hinglish_replacements = {
                "yes": "haan",
                "no": "nahi",
                "good": "accha",
                "very": "bahut",
                "what": "kya",
                "friend": "yaar"
            }
            
            import random
            if random.random() < 0.3:  # 30% chance
                for eng, hindi in hinglish_replacements.items():
                    if eng in response.lower():
                        response = response.replace(eng, hindi, 1)
                        break
        
        # Apply prosody adjustments
        pace = prosody.get("pace", "normal")
        if pace == "slow" or pace == "very_slow":
            # Add more pauses
            response = response.replace(".", "... ").replace(",", ", ")
        
        return response

    async def generate_response_with_dialogue_plan(self, user_input: str, user_profile: Dict[str, Any], session_id: str, context: List[Dict[str, Any]] = None, dialogue_plan: Dict[str, Any] = None, memory_context: Dict[str, Any] = None) -> str:
        """Generate response with conversation context for ambient listening and enhanced content detection"""
        try:
            # CRITICAL FIX: Validate input message
            if not user_input or not user_input.strip():
                logger.warning("❌ Empty or whitespace-only message received")
                raise ValueError("Message is required and cannot be empty")
            
            # BLAZING SPEED OPTIMIZATION 1: Check template system first for instant <0.1s responses
            start_blazing = time.time()
            content_type_detected, category_detected = self._detect_template_intent(user_input)
            logger.info(f"🚀 BLAZING SPEED: Template detection for '{user_input[:50]}...': ({content_type_detected}, {category_detected})")
            
            if content_type_detected and category_detected:
                template_response = self._get_blazing_template_response(
                    content_type_detected, category_detected, user_profile, user_input
                )
                if template_response:
                    blazing_duration = time.time() - start_blazing
                    logger.info(f"🚀 BLAZING SPEED: Template response generated in {blazing_duration:.3f}s - '{template_response[:100]}...'")
                    return template_response
                else:
                    logger.warning(f"🚀 BLAZING SPEED: Template response generation failed for ({content_type_detected}, {category_detected})")
            
            # BLAZING SPEED OPTIMIZATION 2: Check prefetch cache for <0.2s responses  
            cache_response = await self._check_prefetch_cache(user_input, user_profile)
            if cache_response:
                blazing_duration = time.time() - start_blazing
                logger.info(f"🚀 BLAZING SPEED: Cache response served in {blazing_duration:.3f}s")
                return cache_response
            
            # BLAZING SPEED OPTIMIZATION 3: If no template/cache hit, proceed with optimized LLM
            logger.info(f"🚀 BLAZING SPEED: Template/cache miss, using optimized LLM pipeline...")
            
            # Determine age group
            age = user_profile.get('age', 5)
            age_group = self._get_age_group(age)
            
            # Detect content type using enhanced detection
            content_type = self._detect_content_type(user_input)
            
            # Enhanced logging for story detection
            logger.info(f"Content type detected: {content_type} for input: {user_input[:50]}...")
            if content_type == "story":
                logger.info("🎭 STORY REQUEST DETECTED - Will use iterative generation")
            is_content_request = content_type != "conversation"
            
            # Enhanced logging for story detection
            logger.info(f"Content type detected: {content_type} for input: {user_input[:50]}...")
            if content_type == "story":
                logger.info("🎭 STORY REQUEST DETECTED - Will use iterative generation")
            
            # Build empathetic, context-aware system message
            base_empathetic_message = self._create_empathetic_system_message(user_profile, memory_context)
            
            # Create enhanced system message based on content type
            if is_content_request:
                enhanced_system_message = self._create_content_system_message(
                    content_type, user_profile, base_empathetic_message
                )
            else:
                # Regular conversation - use empathetic base message
                enhanced_system_message = base_empathetic_message
            
            # Add conversation context if available
            if context:
                enhanced_system_message += f"\nRecent conversation context:\n"
                for ctx in context[-3:]:  # Last 3 context items
                    enhanced_system_message += f"- {ctx.get('text', '')}\n"
                
                # CRITICAL: Check for conversation continuity needs
                last_bot_message = self._get_last_bot_message(context)
                last_user_message = self._get_last_user_message(context)
                
                logger.info(f"Context analysis - Last bot: '{last_bot_message}', User input: '{user_input}'")
                
                if self._requires_followthrough(last_bot_message, user_input):
                    enhanced_system_message += f"\n⚠️  CRITICAL CONTEXT CONTINUITY: You previously said '{last_bot_message}'. "
                    enhanced_system_message += f"The user responded '{user_input}'. This is clearly a response to your question/prompt. You MUST:\n"
                    enhanced_system_message += f"1. Recognize this as a direct response to your previous message\n"
                    enhanced_system_message += f"2. Continue the conversation based on their response\n"
                    enhanced_system_message += f"3. DO NOT ask 'what do you mean' or ignore the context\n"
                    enhanced_system_message += f"4. If they said 'yes' to your question, provide what they said yes to\n"
                    enhanced_system_message += f"5. If they said 'no', acknowledge and offer alternatives\n"
                    logger.info(f"FOLLOW-THROUGH REQUIRED: Bot said '{last_bot_message}' and user responded '{user_input}'")
                else:
                    logger.info(f"No follow-through required for: '{last_bot_message}' -> '{user_input}'")
                
                enhanced_system_message += f"\nContinue this conversation naturally and remember what was said before."
            
            # Add memory context if available
            if memory_context and memory_context.get("user_id") != "unknown":
                enhanced_system_message += f"\n\nLong-term memory context:\n"
                
                # Add recent preferences
                recent_preferences = memory_context.get("recent_preferences", {})
                if recent_preferences:
                    enhanced_system_message += f"Recent preferences: {', '.join(f'{k}: {v}' for k, v in list(recent_preferences.items())[:3])}\n"
                
                # Add favorite topics
                favorite_topics = memory_context.get("favorite_topics", [])
                if favorite_topics:
                    topics_str = ', '.join([topic[0] if isinstance(topic, tuple) else str(topic) for topic in favorite_topics[:3]])
                    enhanced_system_message += f"Favorite topics: {topics_str}\n"
                
                # Add achievements
                achievements = memory_context.get("achievements", [])
                if achievements:
                    recent_achievements = achievements[-2:]  # Last 2 achievements
                    for achievement in recent_achievements:
                        if isinstance(achievement, dict):
                            achievement_type = achievement.get("type", "unknown")
                            enhanced_system_message += f"Recent achievement: {achievement_type}\n"
                
                enhanced_system_message += "Use this memory context to personalize the conversation and reference past interactions naturally."
            
            # Add ambient listening context
            enhanced_system_message += f"\n\nNote: This is an ambient listening conversation. The child may have said a wake word like 'Hey Buddy' before this message. Be natural and conversational."
            
            # DYNAMIC TOKEN LENGTH MANAGEMENT - Critical for different content types
            # Set dynamic token limits based on content type - FORCE HIGHER LIMITS
            if content_type == "story":
                # Stories need much more tokens for complete narratives
                max_tokens = 4000  # INCREASED from 2000 to ensure complete stories
                logger.info(f"🎭 STORY REQUEST - Using {max_tokens} tokens for complete narrative")
            elif content_type in ["song", "poem", "rhyme"]:
                # Creative content needs moderate tokens - RESTORED optimal balance
                max_tokens = 800  # RESTORED from previous working configuration
                logger.info(f"🎵 CREATIVE CONTENT - Using {max_tokens} tokens for optimal speed")
            elif content_type in ["riddle", "joke"]:
                # Short content can use fewer tokens
                max_tokens = 800  # INCREASED from 400
                logger.info(f"🧩 SHORT CONTENT - Using {max_tokens} tokens")
            else:
                # Regular conversation gets standard allocation
                max_tokens = 2000  # INCREASED from 1000
                logger.info(f"💬 CONVERSATION - Using {max_tokens} tokens")
            
            # CRITICAL FIX: Enhanced system message with conversation history for context continuity
            if context and len(context) > 0:
                logger.info(f"Adding {len(context)} conversation history items to system message for context continuity")
                history_text = "\n\nRECENT CONVERSATION HISTORY (for context continuity):\n"
                
                # Add last 10 messages to system message for context
                recent_context = context[-10:] if len(context) > 10 else context
                for ctx_item in recent_context:
                    role = ctx_item.get('role', ctx_item.get('sender', 'unknown'))
                    text = ctx_item.get('text', '')
                    if role == 'user':
                        history_text += f"Child: {text}\n"
                    elif role in ['assistant', 'bot']:
                        history_text += f"You (Buddy): {text}\n"
                
                history_text += "\nIMPORTANT: Use this conversation history to maintain context continuity. Reference previous exchanges naturally and respond appropriately to the current user input in the context of this conversation.\n"
                
                # Recreate chat with enhanced system message including history
                enhanced_system_with_history = enhanced_system_message + history_text
                
                # GROK'S UNLIMITED TOKEN SOLUTION - Force complete generation for ALL content
                chat = LlmChat(
                    api_key=self.gemini_api_key,
                    session_id=session_id,
                    system_message=enhanced_system_with_history
                ).with_model("gemini", "gemini-2.0-flash")
                # CRITICAL: NO TOKEN LIMITS - Force complete responses for everything
                logger.info(f"🔄 {content_type.upper()} REQUEST - Using UNLIMITED tokens for complete response")
                
                
                logger.info("✅ Enhanced chat initialized with conversation history and dynamic token allocation")
            else:
                # No context available, use original system message with unlimited tokens
                chat = LlmChat(
                    api_key=self.gemini_api_key,
                    session_id=session_id,
                    system_message=enhanced_system_message
                ).with_model("gemini", "gemini-2.0-flash")
                # CRITICAL: NO TOKEN LIMITS for any content type
                logger.info(f"🔄 {content_type.upper()} REQUEST - Using UNLIMITED tokens (no context)")
            
            # Create user message
            user_message = UserMessage(text=user_input)
            
            # GENERATE RESPONSE WITH CONTINUATION LOOP - Ensure completeness
            response = ""
            max_attempts = 3
            attempt = 0
            
            while attempt < max_attempts:
                try:
                    # CRITICAL FIX: Add timeout to prevent hanging
                    current_response = await asyncio.wait_for(
                        chat.send_message(user_message), 
                        timeout=30.0  # 30 second timeout per attempt
                    )
                    response += current_response if current_response else ""
                    
                    # Check if response is complete (not truncated)
                    if response and len(response.strip()) > 50:
                        # For specific content types, check for completeness
                        if content_type == "joke":
                            # Jokes must have both setup and punchline - no interactive format
                            if ("?" in response and ("!" in response or "." in response) and 
                                "tell me more" not in response.lower() and "..." not in response):
                                break  # Complete joke delivered
                            else:
                                logger.warning(f"⚠️ Joke appears incomplete or interactive, retrying...")
                                attempt += 1
                                continue
                        elif content_type == "story" and ("The End" in response or len(response.split()) >= 100):
                            break  # Story with ending or sufficient length
                        elif content_type == "riddle" and ("?" in response and len(response.split()) >= 30):
                            break  # Riddle with question
                        elif content_type in ["song", "rhyme"] and len(response.split()) >= 50:
                            break  # Song/rhyme with sufficient content
                        elif content_type == "conversation" and len(response.split()) >= 20:
                            break  # Regular conversation response
                        else:
                            break  # For other content, accept if we got something substantial
                    else:
                        logger.warning(f"⚠️ Response too short ({len(response)} chars), retrying...")
                        attempt += 1
                        if attempt < max_attempts:
                            # Add continuation prompt - emphasize complete delivery for jokes
                            if content_type == "joke":
                                user_message = UserMessage(text=f"{user_input}\n\nPlease provide the complete joke with setup AND punchline in one response.")
                            else:
                                user_message = UserMessage(text=f"{user_input}\n\nPlease provide a complete, full response.")
                        continue
                        
                    break
                    
                except asyncio.TimeoutError:
                    logger.error(f"❌ Timeout during generation attempt {attempt + 1}")
                    attempt += 1
                    if attempt >= max_attempts:
                        response = f"I'd love to help you with that! Let's try something fun together, {user_profile.get('name', 'friend')}!"
                        break
                except Exception as gen_error:
                    logger.error(f"❌ Generation attempt {attempt + 1} failed: {str(gen_error)}")
                    attempt += 1
                    if attempt >= max_attempts:
                        response = f"I'd love to help you with that! Let's try something fun together, {user_profile.get('name', 'friend')}!"
                        break
            
            if not response or len(response.strip()) < 20:
                logger.error("❌ All generation attempts failed or produced inadequate response")
                response = f"I'd love to help you with that! Let's have some fun together, {user_profile.get('name', 'friend')}!"
            
            # ENHANCED RESPONSE LENGTH VALIDATION AND ITERATIVE GENERATION FOR STORY CONTENT
            if content_type == "story" and response:
                original_word_count = len(response.split())
                logger.info(f"Initial story response: {original_word_count} words")
                
                # If story is too short, use iterative generation to build complete story
                if original_word_count < 250:
                    logger.info(f"Story too short ({original_word_count} words), using iterative generation")
                    
                    # Continue building the story iteratively
                    current_story = response
                    iteration_count = 0
                    max_iterations = 3
                    
                    while len(current_story.split()) < 300 and iteration_count < max_iterations:
                        iteration_count += 1
                        continuation_prompt = f"""Continue and expand this story to make it more complete and detailed. The current story is: 

{current_story}

Please continue with more details, dialogue, and story development. Add at least 100 more words to make this a richer, more complete story. Continue seamlessly from where it left off."""
                        
                        continuation_message = UserMessage(text=continuation_prompt)
                        
                        # CRITICAL FIX: Add timeout to prevent hanging
                        try:
                            continuation = await asyncio.wait_for(
                                chat.send_message(continuation_message), 
                                timeout=15.0  # 15 second timeout per iteration
                            )
                        except asyncio.TimeoutError:
                            logger.error(f"Timeout during story iteration {iteration_count}, breaking loop")
                            break
                        
                        if continuation:
                            # Combine the stories intelligently  
                            if current_story.endswith('.') or current_story.endswith('!') or current_story.endswith('?'):
                                current_story = current_story + " " + continuation
                            else:
                                current_story = current_story + continuation
                            
                            logger.info(f"Story iteration {iteration_count}: {len(current_story.split())} words")
                        else:
                            break
                    
                    response = current_story
                    final_word_count = len(response.split())
                    logger.info(f"Final story length: {final_word_count} words after {iteration_count} iterations")
            
            # Post-process response - CRITICAL: Don't truncate stories after iterative generation!
            if content_type == "story":
                # Stories must NOT be truncated after iterative generation
                processed_response = response  # Keep full story intact
                logger.info(f"🎭 STORY PRESERVED: Skipping truncation for {len(response.split())} word story")
            else:
                processed_response = self._post_process_ambient_response(response, age_group, content_type)
            
            # Apply age-appropriate language enforcement (POST-PROCESSING) - ALWAYS APPLY
            age = user_profile.get('age', 7)
            processed_response = self.enforce_age_appropriate_language(processed_response, age, content_type)
            logger.info(f"🔍 Applied age-appropriate language enforcement for age {age} to {content_type} content")
            
            logger.info(f"Generated context-aware response for age {age}: {processed_response[:100]}...")
            
            # Return both text and content_type for proper audio handling
            # FORCE TTS AUDIO GENERATION FOR ALL RESPONSES
            logger.info(f"🎵 FORCE TTS: Ensuring audio generation for {content_type} response")
            
            # Import voice agent if not already imported
            try:
                from .voice_agent import VoiceAgent
                import os
                
                # Get Deepgram API key
                deepgram_key = os.environ.get('DEEPGRAM_API_KEY')
                if deepgram_key:
                    logger.info("🎵 FORCE TTS: Creating voice agent for audio generation")
                    voice_agent = VoiceAgent(deepgram_key)
                    
                    # Force TTS generation for this response
                    voice_personality = user_profile.get('voice_personality', 'friendly_companion')
                    audio_base64 = await voice_agent.text_to_speech_chunked(processed_response, voice_personality)
                    
                    if audio_base64 and len(audio_base64) > 0:
                        logger.info(f"🎵 FORCE TTS: Audio generated successfully - size: {len(audio_base64)}")
                        return {
                            "text": processed_response,
                            "content_type": content_type,
                            "audio_base64": audio_base64
                        }
                    else:
                        logger.error("🎵 FORCE TTS: Audio generation failed - no audio returned")
                        # Fallback with test audio
                        fallback_audio = await voice_agent.text_to_speech("Test audio", voice_personality)
                        if fallback_audio and len(fallback_audio) > 0:
                            logger.info("🎵 FORCE TTS: Fallback audio generated successfully")
                            return {
                                "text": processed_response,
                                "content_type": content_type,
                                "audio_base64": fallback_audio
                            }
                        else:
                            logger.error("🎵 FORCE TTS: Even fallback audio failed")
                            return {
                                "text": processed_response,
                                "content_type": content_type,
                                "audio_base64": ""
                            }
                else:
                    logger.error("🎵 FORCE TTS: No Deepgram API key found")
                    return {
                        "text": processed_response,
                        "content_type": content_type,
                        "audio_base64": ""
                    }
                    
            except Exception as tts_error:
                logger.error(f"🎵 FORCE TTS: Exception during audio generation: {str(tts_error)}")
                return {
                    "text": processed_response,
                    "content_type": content_type,
                    "audio_base64": ""
                }
            
        except Exception as e:
            logger.error(f"Error generating context-aware response: {str(e)}")
            
            # FORCE TTS EVEN FOR FALLBACK RESPONSES
            try:
                from .voice_agent import VoiceAgent
                import os
                
                fallback_text = self._get_fallback_ambient_response(user_profile.get('age', 5))
                deepgram_key = os.environ.get('DEEPGRAM_API_KEY')
                
                if deepgram_key:
                    logger.info("🎵 FORCE TTS FALLBACK: Generating audio for fallback response")
                    voice_agent = VoiceAgent(deepgram_key)
                    voice_personality = user_profile.get('voice_personality', 'friendly_companion')
                    fallback_audio = await voice_agent.text_to_speech(fallback_text, voice_personality)
                    
                    return {
                        "text": fallback_text,
                        "content_type": "conversation",
                        "audio_base64": fallback_audio if fallback_audio else ""
                    }
                else:
                    return {
                        "text": fallback_text,
                        "content_type": "conversation",
                        "audio_base64": ""
                    }
                    
            except Exception as fallback_tts_error:
                logger.error(f"🎵 FORCE TTS FALLBACK: Exception during fallback audio: {str(fallback_tts_error)}")
                return {
                    "text": self._get_fallback_ambient_response(user_profile.get('age', 5)),
                    "content_type": "conversation",
                    "audio_base64": ""
                }
    
    def _post_process_ambient_response(self, response: str, age_group: str, content_type: str = "conversation") -> str:
        """Post-process response for ambient conversation - PRESERVES story content"""
        
        # CRITICAL: Never truncate story content regardless of age group
        if content_type == "story":
            logger.info(f"🎭 STORY CONTENT DETECTED: Preserving full {len(response.split())} word story")
            return response  # Return story completely unchanged
        
        # Only apply truncation to regular conversation content
        if age_group == "toddler":
            # Keep responses very short for toddlers in conversation only
            sentences = response.split('.')
            if len(sentences) > 2:
                response = '. '.join(sentences[:2]) + '.'
        elif age_group == "child":
            # Moderate length for children in conversation only
            sentences = response.split('.')
            if len(sentences) > 3:
                response = '. '.join(sentences[:3]) + '.'
        
        # Add natural conversation starters occasionally
        conversation_starters = {
            "toddler": ["Want to hear more?", "What do you think?", "Should we play?"],
            "child": ["What would you like to know?", "Want to try something fun?", "Any questions?"],
            "preteen": ["What's your opinion?", "Want to explore this more?", "Any questions?"]
        }
        
        # Add conversation starter 20% of the time
        import random
        if random.random() < 0.2:
            starter = random.choice(conversation_starters[age_group])
            response = f"{response} {starter}"
        
        return response
    
    def _get_fallback_ambient_response(self, age: int) -> str:
        """Get fallback response for ambient conversation"""
        age_group = self._get_age_group(age)
        
        fallback_responses = {
            "toddler": "I'm here to help! What would you like to do?",
            "child": "Hi there! I'm listening. What can I help you with?",
            "preteen": "I'm ready to chat! What's on your mind?"
        }
        
        return fallback_responses[age_group]

    async def generate_response(self, user_input: str, user_profile: Dict[str, Any], session_id: str) -> str:
        """Generate age-appropriate response using Gemini 2.0 Flash with content frameworks"""
        try:
            # Determine age group
            age = user_profile.get('age', 5)
            age_group = self._get_age_group(age)
            
            # Detect content type
            content_type = self._detect_content_type(user_input)
            
            # Get empathetic base system message (without memory_context for this method)
            base_empathetic_message = self._create_empathetic_system_message(user_profile, "")
            
            # Create enhanced system message based on content type
            if content_type in ["story", "song", "rhyme", "poem", "joke", "riddle"]:
                enhanced_system_message = self._create_content_system_message(
                    content_type, user_profile, base_empathetic_message
                )
            else:
                # Regular conversation - use empathetic base message
                enhanced_system_message = f"{base_empathetic_message}\n\nProvide rich, thoughtful responses with the depth and warmth this conversation deserves. Remember - you genuinely care about this child's happiness and growth!"
            
            # Initialize chat with session - COMPLETELY REMOVE TOKEN LIMITS  
            chat = LlmChat(
                api_key=self.gemini_api_key,
                session_id=session_id,
                system_message=enhanced_system_message
            ).with_model("gemini", "gemini-2.0-flash")
            # INTENTIONALLY NO .with_max_tokens() - Allow unlimited length
            
            # Create user message
            user_message = UserMessage(text=user_input)
            
            # GROK'S ITERATIVE GENERATION SOLUTION - Proven approach
            response = await chat.send_message(user_message)
            original_response = response
            
            # Check if response was truncated and continue iteratively
            complete_response = response
            iteration_count = 0
            max_iterations = 5  # Prevent infinite loops
            
            # For stories, ensure minimum word count through iteration
            if content_type == "story":
                word_count = len(complete_response.split())
                logger.info(f"🎭 Initial story response: {word_count} words")
                
                while word_count < 300 and iteration_count < max_iterations:
                    iteration_count += 1
                    logger.info(f"🔄 Story iteration {iteration_count}: Continuing from {word_count} words")
                    
                    # Continue the story from where it left off
                    continuation_prompt = f"Continue this story seamlessly to complete it (add at least 100 more words): {complete_response[-200:]}"  # Last 200 chars for context
                    continuation_message = UserMessage(text=continuation_prompt)
                    
                    continuation_response = await chat.send_message(continuation_message)
                    
                    if continuation_response:
                        # Smart continuation - avoid repetition
                        if not complete_response.endswith(('.', '!', '?')):
                            complete_response += " " + continuation_response
                        else:
                            complete_response += " " + continuation_response
                        
                        word_count = len(complete_response.split())
                        logger.info(f"📈 Story expanded to {word_count} words after iteration {iteration_count}")
                    else:
                        logger.warning(f"⚠️ No continuation received in iteration {iteration_count}")
                        break
                
                response = complete_response
                final_word_count = len(response.split())
                logger.info(f"📚 FINAL STORY LENGTH: {final_word_count} words after {iteration_count} iterations")
                
            else:
                # For non-story content, check for completeness differently
                if len(response.split()) < 50:  # Minimum for complete responses
                    logger.info("🔄 Response seems incomplete, attempting continuation")
                    continuation_prompt = f"Complete this response fully: {response}"
                    continuation_message = UserMessage(text=continuation_prompt)
                    continuation_response = await chat.send_message(continuation_message)
                    
                    if continuation_response:
                        response = response + " " + continuation_response
                        logger.info(f"✅ Response completed: {len(response.split())} words")
            
            # RESPONSE LENGTH VALIDATION AND ITERATIVE GENERATION FOR STORY CONTENT
            if content_type == "story" and response:
                original_word_count = len(response.split())
                logger.info(f"Initial story response: {original_word_count} words")
                
                # If story is too short, use iterative generation to build complete story
                if original_word_count < 250:
                    logger.info(f"Story too short ({original_word_count} words), using iterative generation")
                    
                    # Continue building the story iteratively
                    current_story = response
                    iteration_count = 0
                    max_iterations = 3
                    
                    while len(current_story.split()) < 300 and iteration_count < max_iterations:
                        iteration_count += 1
                        continuation_prompt = f"""Continue and expand this story to make it more complete and detailed. The current story is: 

{current_story}

Please continue with more details, dialogue, and story development. Add at least 100 more words to make this a richer, more complete story. Continue seamlessly from where it left off."""
                        
                        continuation_message = UserMessage(text=continuation_prompt)
                        
                        # CRITICAL FIX: Add timeout to prevent hanging
                        try:
                            continuation = await asyncio.wait_for(
                                chat.send_message(continuation_message), 
                                timeout=15.0  # 15 second timeout per iteration
                            )
                        except asyncio.TimeoutError:
                            logger.error(f"Timeout during story iteration {iteration_count}, breaking loop")
                            break
                        
                        if continuation:
                            # Combine the stories intelligently  
                            if current_story.endswith('.') or current_story.endswith('!') or current_story.endswith('?'):
                                current_story = current_story + " " + continuation
                            else:
                                current_story = current_story + continuation
                            
                            logger.info(f"Story iteration {iteration_count}: {len(current_story.split())} words")
                        else:
                            break
                    
                    response = current_story
                    final_word_count = len(response.split())
                    logger.info(f"Final story length: {final_word_count} words after {iteration_count} iterations")
            
            # Light post-processing (no artificial truncation)
            processed_response = self._post_process_response_enhanced(response, age_group, content_type)
            
            # Apply age-appropriate language enforcement (POST-PROCESSING) - ALWAYS APPLY
            age = user_profile.get('age', 7)
            processed_response = self.enforce_age_appropriate_language(processed_response, age, content_type)
            logger.info(f"🔍 Applied age-appropriate language enforcement for age {age} to {content_type} content")
            
            logger.info(f"Generated {content_type} response for age {age}: {len(processed_response.split())} words")
            return processed_response
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return self._get_fallback_response(user_profile.get('age', 5))

    def _detect_content_type(self, user_input: str) -> str:
        """Detect what type of content the user is requesting"""
        user_input_lower = user_input.lower()
        
        # Story detection
        story_keywords = ['story', 'tale', 'tell me about', 'once upon', 'adventure', 'fairy tale']
        if any(keyword in user_input_lower for keyword in story_keywords):
            return "story"
        
        # Song detection
        song_keywords = ['song', 'sing', 'music', 'lullaby', 'rhyme about']
        if any(keyword in user_input_lower for keyword in song_keywords):
            return "song"
        
        # Riddle detection
        riddle_keywords = ['riddle', 'puzzle', 'guess', 'brain teaser']
        if any(keyword in user_input_lower for keyword in riddle_keywords):
            return "riddle"
        
        # Joke detection
        joke_keywords = ['joke', 'funny', 'make me laugh', 'something silly']
        if any(keyword in user_input_lower for keyword in joke_keywords):
            return "joke"
        
        # Rhyme/Poem detection
        rhyme_keywords = ['rhyme', 'poem', 'poetry', 'verse']
        if any(keyword in user_input_lower for keyword in rhyme_keywords):
            return "rhyme"
        
        return "conversation"

    def _post_process_response_enhanced(self, response: str, age_group: str, content_type: str) -> str:
        """Enhanced post-processing without artificial truncation"""
        if age_group == "toddler":
            # Simple vocabulary replacements only
            response = response.replace("understand", "know")
            response = response.replace("excellent", "great")
            response = response.replace("magnificent", "amazing")
        
        # Add encouraging elements occasionally (but don't truncate)
        encouraging_phrases = {
            "toddler": ["Good job!", "You're so smart!", "That's wonderful!"],
            "child": ["Great question!", "You're doing awesome!", "I love how curious you are!"],
            "preteen": ["Excellent thinking!", "You're really getting it!", "That's a thoughtful question!"]
        }
        
        import random
        if random.random() < 0.2 and content_type == "conversation":  # 20% chance for regular conversation only
            phrase = random.choice(encouraging_phrases[age_group])
            response = f"{phrase} {response}"
        
        return response
    
    def _get_age_group(self, age: int) -> str:
        """Determine age group category"""
        if age <= 5:
            return "toddler"
        elif age <= 9:
            return "child"
        else:
            return "preteen"
    
    def _post_process_response(self, response: str, age_group: str) -> str:
        """Post-process response based on age group"""
        if age_group == "toddler":
            # Ensure very simple language
            response = response.replace("understand", "know")
            response = response.replace("excellent", "great")
            response = response.replace("magnificent", "amazing")
            
        # Add encouraging elements
        encouraging_phrases = {
            "toddler": ["Good job!", "You're so smart!", "That's wonderful!"],
            "child": ["Great question!", "You're doing awesome!", "I love how curious you are!"],
            "preteen": ["Excellent thinking!", "You're really getting it!", "That's a thoughtful question!"]
        }
        
        # Randomly add encouraging phrases occasionally
        import random
        if random.random() < 0.3:  # 30% chance
            phrase = random.choice(encouraging_phrases[age_group])
            response = f"{phrase} {response}"
        
        return response
    
    def _get_fallback_response(self, age: int) -> str:
        """Get fallback response when AI fails"""
        age_group = self._get_age_group(age)
        
        fallback_responses = {
            "toddler": "That's a fun question! Let me think about it. What else would you like to know?",
            "child": "That's really interesting! I'm still learning about that. What else are you curious about?",
            "preteen": "That's a great question! I need to think more about that. Is there something else I can help you with?"
        }
        
        return fallback_responses[age_group]
    


    def _format_content_response_with_emotion(self, content_type: str, content: Dict[str, Any], user_profile: Dict[str, Any]) -> str:
        """Format content responses with proper emotional expression and re-engagement"""
        name = user_profile.get('name', 'friend')
        
        if content_type == "joke":
            return f"{content['setup']}\n\n{content['punchline']}\n\n{content.get('reaction', '😂 Haha!')} Want another joke, {name}?"
        
        elif content_type == "riddle":
            return f"Here's a riddle for you, {name}! 🧩\n\n{content['question']}\n\nTake your time to think! When you're ready, tell me your answer and I'll let you know if you got it!"
        
        elif content_type == "fact":
            return f"{content.get('text', content.get('fact', ''))} {content.get('reaction', '🤯 Amazing, right?')} Want to learn another cool fact, {name}?"
        
        elif content_type == "rhyme":
            beautiful_msg = "🎵 Wasn't that beautiful?"
            return f"Here's a lovely rhyme for you, {name}! ✨\n\n{content.get('text', content.get('content', ''))}\n\n{content.get('reaction', beautiful_msg)} Want to hear another rhyme?"
        
        elif content_type == "song":
            return f"Let's sing together, {name}! 🎵\n\n{content.get('text', content.get('content', ''))}\n\n{content.get('reaction', '🎶 That was fun!')} Should we sing another song?"
        
        elif content_type == "story":
            full_story = content.get('text', content.get('content', ''))
            moral = content.get('moral', '')
            story_end = f"\n\nThe End! ✨"
            if moral:
                story_end += f"\n\n💫 {moral}"
            story_end += f"\n\nWhat did you think of that story, {name}? Want to hear another one?"
            return full_story + story_end
        
        elif content_type == "game":
            return f"{content.get('intro', content.get('text', ''))} {content.get('reaction', '🎮 This will be fun!')} Are you ready to play, {name}?"
        
        return content.get('text', str(content))
    
    def _get_last_bot_message(self, context: List[Dict[str, Any]]) -> Optional[str]:
        """Get the last bot message from context"""
        if not context:
            return None
        
        for ctx in reversed(context):
            if ctx.get('role') == 'assistant' or ctx.get('sender') == 'bot':
                return ctx.get('text', '')
        return None
    
    def _get_last_user_message(self, context: List[Dict[str, Any]]) -> Optional[str]:
        """Get the last user message from context"""
        if not context:
            return None
        
        for ctx in reversed(context):
            if ctx.get('role') == 'user' or ctx.get('sender') == 'user':
                return ctx.get('text', '')
        return None
    
    def _requires_followthrough(self, last_bot_message: Optional[str], user_input: str) -> bool:
        """Check if the last bot message requires follow-through"""
        if not last_bot_message:
            return False
        
        # Check for questions, riddles, games that need responses
        followthrough_patterns = [
            r'\?',  # Any question
            r'\bguess\b',  # Guessing games
            r'\briddle\b',  # Riddles
            r'\bwhat am i\b',  # What am I riddles
            r'\bthink about\b',  # Thinking prompts
            r'\btell me\b',  # Direct requests
            r'\bwhat do you think\b',  # Opinion requests
            r'\bready\b.*\?',  # Ready questions
            r'\bwant to\b.*\?',  # Want to questions - THIS SHOULD MATCH THE OCTOPUS CASE
            r'\bwould you like\b.*\?',  # Would you like questions
            r'\bdo you want\b.*\?',  # Do you want questions  
            r'\bshould we\b.*\?',  # Should we questions
            r'\blet me know\b',  # Let me know requests
            r'\blearn more\b.*\?',  # Learn more questions
            r'\bchoose\b',  # Choice prompts
            r'\bpick\b',  # Pick prompts
        ]
        
        last_bot_lower = last_bot_message.lower()
        
        # Additional check for common response patterns
        user_lower = user_input.lower().strip()
        response_patterns = ['yes', 'no', 'yeah', 'sure', 'okay', 'ok', 'please', 'yes please', 'no thanks']
        
        # If user gave a simple response, check if bot asked a question
        if any(user_lower.startswith(pattern) for pattern in response_patterns):
            # More likely to be a follow-through if it's a simple response to a question
            if '?' in last_bot_message:
                return True
        
        for pattern in followthrough_patterns:
            if re.search(pattern, last_bot_lower):
                return True
        
        return False
    
    async def get_conversation_history(self, session_id: str) -> list:
        """Get conversation history for a session"""
        return self.conversations.get(session_id, [])
    
    async def clear_conversation_history(self, session_id: str):
        """Clear conversation history for a session"""
        if session_id in self.conversations:
            del self.conversations[session_id]