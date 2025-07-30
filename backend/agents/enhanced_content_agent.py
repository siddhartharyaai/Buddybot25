"""
Enhanced Content Agent - 3-Tier Content Sourcing System
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import random
import re
import json

logger = logging.getLogger(__name__)

class EnhancedContentAgent:
    """Enhanced Content Agent with 3-tier sourcing and content type detection"""
    
    def __init__(self, db, gemini_api_key: str = None):
        self.db = db
        self.gemini_api_key = gemini_api_key
        self.content_cache = {}
        
        # Content type detection patterns
        self.content_patterns = {
            "joke": [
                r"\b(joke|funny|laugh|giggle|humor|hilarious)\b",
                r"\b(tell me something funny|make me laugh)\b",
                r"\b(know any jokes|got a joke)\b"
            ],
            "riddle": [
                r"\b(riddle|puzzle|guess|brain teaser|mystery)\b",
                r"\b(can you give me a riddle|riddle me this)\b",
                r"\b(what am I|guess what)\b"
            ],
            "fact": [
                r"\b(fact|did you know|tell me about|trivia|interesting|learn)\b",
                r"\b(what is|how does|why does|explain)\b",
                r"\b(cool fact|amazing fact)\b"
            ],
            "rhyme": [
                r"\b(rhyme|poem|nursery rhyme|poetry|verse)\b",
                r"\b(roses are red|twinkle twinkle|hickory dickory)\b",
                r"\b(recite a poem|tell me a rhyme)\b"
            ],
            "song": [
                r"\b(song|sing|music|melody|tune|lullaby)\b",
                r"\b(let's sing|can you sing|sing me|play a song)\b",
                r"\b(favorite song|nursery song)\b"
            ],
            "story": [
                r"\b(story|tale|once upon|tell me about|adventure|fairy tale)\b",
                r"\b(bedtime story|read me|story time)\b",
                r"\b(what happened|tell me the story)\b"
            ],
            "game": [
                r"\b(game|play|fun|activity|challenge|let's play)\b",
                r"\b(what can we do|something fun|play with me)\b",
                r"\b(bored|entertain me)\b"
            ]
        }
        
        # Tier 1: Local content library (fastest, most reliable)
        self.local_content = self._initialize_local_content()
        
        logger.info("Enhanced Content Agent with 3-tier sourcing initialized")

    def _initialize_local_content(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize Tier 1 local content library"""
        return {
            "jokes": [
                {
                    "id": "joke_elephant_computer",
                    "setup": "Why don't elephants use computers?",
                    "punchline": "They're afraid of the mouse!",
                    "reaction": "😂 Haha! Get it? Computer mouse! Want another one?",
                    "age_groups": ["3-6", "7-9", "10-12"],
                    "tags": ["animals", "wordplay", "technology"],
                    "emotional_cue": "giggle"
                },
                {
                    "id": "joke_banana_doctor",
                    "setup": "Why did the banana go to the doctor?",
                    "punchline": "Because it wasn't peeling well!",
                    "reaction": "😄 That's bananas! Want to hear another joke?",
                    "age_groups": ["4-8", "9-12"],
                    "tags": ["food", "wordplay", "health"],
                    "emotional_cue": "laugh"
                },
                {
                    "id": "joke_math_book",
                    "setup": "Why was the math book so sad?",
                    "punchline": "Because it had too many problems!",
                    "reaction": "😆 Math humor is the best! Get it? Problems! Want more?",
                    "age_groups": ["6-9", "10-12"],
                    "tags": ["school", "math", "wordplay"],
                    "emotional_cue": "chuckle"
                },
                {
                    "id": "joke_teddy_bear",
                    "setup": "Why don't teddy bears ever eat dessert?",
                    "punchline": "Because they're always stuffed!",
                    "reaction": "🧸 Hehe! Teddy bears are always stuffed with fluff! That's so silly!",
                    "age_groups": ["3-8"],
                    "tags": ["toys", "wordplay", "food"],
                    "emotional_cue": "giggle"
                },
                {
                    "id": "joke_fish_piano",
                    "setup": "What do you call a fish that plays piano?",
                    "punchline": "A piano tuna!",
                    "reaction": "🐟 Get it? Piano TUNA! Music and fish together - so funny!",
                    "age_groups": ["4-10"],
                    "tags": ["animals", "music", "wordplay"],
                    "emotional_cue": "laugh"
                }
            ],
            "riddles": [
                {
                    "id": "riddle_candle",
                    "question": "I'm tall when I'm young and short when I'm old. What am I?",
                    "answer": "A candle!",
                    "hint": "Think about something that gets smaller as it's used...",
                    "celebration": "🎉 Excellent! You got it right! Candles do get shorter as they burn!",
                    "followup": "Want to try another riddle?",
                    "age_groups": ["5-8", "9-12"],
                    "tags": ["objects", "logic", "everyday_items"],
                    "difficulty": "easy"
                },
                {
                    "id": "riddle_elephant",
                    "question": "I have a long trunk and big ears, I never forget and I love peanuts. What am I?",
                    "answer": "An elephant!",
                    "hint": "I'm the largest land animal...",
                    "celebration": "🎊 Fantastic! Elephants are amazing creatures with incredible memories!",
                    "followup": "Ready for another brain teaser?",
                    "age_groups": ["3-6", "7-9"],
                    "tags": ["animals", "easy", "memory"],
                    "difficulty": "very_easy"
                },
                {
                    "id": "riddle_clock",
                    "question": "I have hands but cannot clap, I have a face but cannot see. What am I?",
                    "answer": "A clock!",
                    "hint": "I help you know what time it is...",
                    "celebration": "⏰ Brilliant! Clocks have hands that point to numbers and faces we can read!",
                    "followup": "Time for another riddle? Get it... TIME for another riddle?",
                    "age_groups": ["5-10"],
                    "tags": ["objects", "time", "logic"],
                    "difficulty": "medium"
                },
                {
                    "id": "riddle_rainbow",
                    "question": "I come after rain and before the sun hides, I have many colors but I'm not alive. What am I?",
                    "answer": "A rainbow!",
                    "hint": "Look up in the sky after it rains and the sun comes out...",
                    "celebration": "🌈 Beautiful! Rainbows are nature's colorful magic in the sky!",
                    "followup": "Rainbows are so pretty! Ready for another puzzle to solve?",
                    "age_groups": ["4-8"],
                    "tags": ["nature", "colors", "weather"],
                    "difficulty": "easy"
                },
                {
                    "id": "riddle_shadow",
                    "question": "I follow you everywhere you go, I copy everything you do, but you can never catch me. What am I?",
                    "answer": "Your shadow!",
                    "hint": "Look behind you on a sunny day...",
                    "celebration": "👤 Awesome! Your shadow is always with you, copying your every move!",
                    "followup": "Have you ever tried to step on your own shadow? Want another riddle?",
                    "age_groups": ["4-9"],
                    "tags": ["shadow", "self", "observation"],
                    "difficulty": "medium"
                }
            ],
            "facts": [
                {
                    "id": "fact_honey_spoils",
                    "fact": "Did you know that honey never spoils? Archaeologists have found honey in ancient Egyptian tombs that's over 3000 years old and still perfectly good to eat!",
                    "reaction": "🍯 Isn't that amazing? Bees are incredible little chemists!",
                    "followup": "Want to learn another cool fact?",
                    "age_groups": ["4-8", "9-12"],
                    "tags": ["food", "science", "history", "animals"],
                    "category": "science_facts"
                },
                {
                    "id": "fact_venus_day",
                    "fact": "Did you know that one day on Venus is longer than one year on Venus? Venus spins so slowly that it takes 243 Earth days to rotate once, but only 225 Earth days to orbit the Sun!",
                    "reaction": "🪐 Space is full of incredible surprises!",
                    "followup": "Want to explore more amazing space facts?",
                    "age_groups": ["7-12"],
                    "tags": ["space", "science", "planets"],
                    "category": "space_facts"
                },
                {
                    "id": "fact_octopus_hearts",
                    "fact": "Did you know that octopuses have three hearts? Two hearts pump blood to their gills, and one pumps blood to the rest of their body. When they swim, the main heart stops beating, which is why they get tired easily!",
                    "reaction": "🐙 Three hearts! That's why octopuses are such amazing ocean creatures!",
                    "followup": "Ocean animals are so fascinating! Want to learn about more sea creatures?",
                    "age_groups": ["5-12"],
                    "tags": ["animals", "ocean", "science", "biology"],
                    "category": "animal_facts"
                },
                {
                    "id": "fact_penguin_huddle",
                    "fact": "Did you know that penguins huddle together in groups of thousands to stay warm? They take turns being on the outside and inside of the huddle, so everyone gets a chance to be warm!",
                    "reaction": "🐧 Penguins are such caring friends! They share warmth with each other!",
                    "followup": "Isn't it wonderful how animals take care of each other? Ready for another amazing fact?",
                    "age_groups": ["3-10"],
                    "tags": ["animals", "cooperation", "nature", "friendship"],
                    "category": "animal_facts"
                },
                {
                    "id": "fact_rainbow_colors",
                    "fact": "Did you know that rainbows always have the same order of colors? Red, Orange, Yellow, Green, Blue, Indigo, and Violet - you can remember it with 'Roy G. Biv!' Rainbows happen when sunlight shines through water drops in the air!",
                    "reaction": "🌈 Roy G. Biv! Rainbows are nature's most beautiful light show!",
                    "followup": "What's your favorite color in the rainbow? Want to learn more colorful facts?",
                    "age_groups": ["4-10"],
                    "tags": ["colors", "weather", "science", "memory"],
                    "category": "science_facts"
                }
            ],
            "rhymes": [
                {
                    "id": "rhyme_twinkle_star",
                    "title": "Twinkle, Twinkle, Little Star",
                    "content": """Twinkle, twinkle, little star,
How I wonder what you are!
Up above the world so high,
Like a diamond in the sky.

When the blazing sun is gone,
When there's nothing he shines upon,
Then you show your little light,
Twinkle, twinkle, through the night.

Twinkle, twinkle, little star,
How I wonder what you are!""",
                    "reaction": "✨ Such a beautiful classic! The stars are magical, aren't they?",
                    "followup": "Do you like looking at stars at night? Want to hear another lovely rhyme?",
                    "age_groups": ["2-8"],
                    "tags": ["classic", "stars", "bedtime", "wonder"],
                    "category": "nursery_rhymes"
                },
                {
                    "id": "rhyme_humpty_dumpty",
                    "title": "Humpty Dumpty",
                    "content": """Humpty Dumpty sat on a wall,
Humpty Dumpty had a great fall!
All the king's horses and all the king's men
Couldn't put Humpty together again.

But Humpty learned to be more careful,
And found friends who were always helpful.
Sometimes when we fall, we learn to grow,
That's something important for us to know!""",
                    "reaction": "🥚 Poor Humpty! But he learned to be more careful, didn't he?",
                    "followup": "Have you ever learned something important from making a mistake? Ready for another rhyme?",
                    "age_groups": ["2-6"],
                    "tags": ["classic", "learning", "safety", "resilience"],
                    "category": "nursery_rhymes"
                },
                {
                    "id": "rhyme_jack_jill",
                    "title": "Jack and Jill",
                    "content": """Jack and Jill went up the hill
To fetch a pail of water.
Jack fell down and broke his crown,
And Jill came tumbling after!

Up Jack got, and home did trot,
As fast as he could caper,
And went to bed and bandaged his head
With vinegar and brown paper.

Jack and Jill learned to be careful
When walking up hills so steep.
Good friends help each other always,
That's a promise they will keep!""",
                    "reaction": "👫 Jack and Jill were such good friends! They helped each other, just like best friends should!",
                    "followup": "Who are your best friends? Do you help each other too? Want another rhyme?",
                    "age_groups": ["2-7"],
                    "tags": ["friendship", "helping", "classic", "cooperation"],
                    "category": "nursery_rhymes"
                },
                {
                    "id": "rhyme_hickory_dickory",
                    "title": "Hickory Dickory Dock",
                    "content": """Hickory dickory dock,
The mouse ran up the clock!
The clock struck one,
The mouse ran down,
Hickory dickory dock!

Hickory dickory dock,
The mouse ran up the clock!
The clock struck two,
The mouse said "Whoo!"
Hickory dickory dock!

Hickory dickory dock,
The mouse ran up the clock!
The clock struck three,
The mouse said "Whee!"
Hickory dickory dock!""",
                    "reaction": "🐭 What a playful little mouse! Did you hear all those fun sounds? Whoo! Whee!",
                    "followup": "Can you make mouse sounds too? What time is it right now? More rhymes?",
                    "age_groups": ["2-6"],
                    "tags": ["animals", "time", "sounds", "playful"],
                    "category": "nursery_rhymes"
                }
            ],
            "songs": [
                {
                    "id": "song_row_boat",
                    "title": "Row, Row, Row Your Boat",
                    "content": """Row, row, row your boat,
Gently down the stream.
Merrily, merrily, merrily, merrily,
Life is but a dream!

Row, row, row your boat,
Gently down the creek.
If you see a little mouse,
Don't forget to squeak!

Row, row, row your boat,
Gently to the shore.
If you see a lion there,
Don't forget to ROAR!""",
                    "reaction": "🚣‍♀️ What a fun song to sing! Let's row together!",
                    "followup": "Should we sing another song with actions?",
                    "age_groups": ["2-8"],
                    "tags": ["classic", "action", "fun", "imagination"],
                    "category": "action_songs"
                },
                {
                    "id": "song_mary_lamb",
                    "title": "Mary Had a Little Lamb",
                    "content": """Mary had a little lamb,
Little lamb, little lamb,
Mary had a little lamb,
Its fleece was white as snow!

Everywhere that Mary went,
Mary went, Mary went,
Everywhere that Mary went,
The lamb was sure to go!

It followed her to school one day,
School one day, school one day,
It followed her to school one day,
Which was against the rule!

It made the children laugh and play,
Laugh and play, laugh and play,
It made the children laugh and play,
To see a lamb at school!""",
                    "reaction": "🐑 Such a sweet friendship! Mary and her lamb were best friends!",
                    "followup": "Do you have a special pet or toy friend? Want to sing more?",
                    "age_groups": ["2-6"],
                    "tags": ["friendship", "animals", "classic", "school"],
                    "category": "nursery_rhymes"
                },
                {
                    "id": "song_wheels_bus",
                    "title": "The Wheels on the Bus",
                    "content": """The wheels on the bus go round and round,
Round and round, round and round,
The wheels on the bus go round and round,
All through the town!

The wipers on the bus go swish, swish, swish,
Swish, swish, swish, swish, swish, swish,
The wipers on the bus go swish, swish, swish,
All through the town!

The horn on the bus goes beep, beep, beep,
Beep, beep, beep, beep, beep, beep,
The horn on the bus goes beep, beep, beep,
All through the town!

The doors on the bus go open and shut,
Open and shut, open and shut,
The doors on the bus go open and shut,
All through the town!

The children on the bus bounce up and down,
Up and down, up and down,
The children on the bus bounce up and down,
All through the town!""",
                    "reaction": "🚌 Beep beep! That was so much fun! Did you do the actions too?",
                    "followup": "What other vehicles make fun sounds? Ready for another song?",
                    "age_groups": ["2-7"],
                    "tags": ["transportation", "actions", "sounds", "fun"],
                    "category": "action_songs"
                },
                {
                    "id": "song_abc",
                    "title": "The ABC Song",
                    "content": """A, B, C, D, E, F, G,
H, I, J, K, L, M, N, O, P,
Q, R, S, T, U, V,
W, X, Y, and Z!

Now I know my ABCs,
Next time won't you sing with me?

A is for Apple, red and sweet,
B is for Ball that bounces neat,
C is for Cat who likes to play,
D is for Dog who runs all day!

A, B, C, D, E, F, G,
Learning letters, you and me!""",
                    "reaction": "🔤 Wonderful! You know your letters! Learning is so much fun!",
                    "followup": "What's your favorite letter? Should we sing about numbers next?",
                    "age_groups": ["3-7"],
                    "tags": ["learning", "letters", "educational", "alphabet"],
                    "category": "educational_songs"
                },
                {
                    "id": "song_old_macdonald",
                    "title": "Old MacDonald Had a Farm",
                    "content": """Old MacDonald had a farm,
E-I-E-I-O!
And on his farm he had a cow,
E-I-E-I-O!

With a moo-moo here,
And a moo-moo there,
Here a moo, there a moo,
Everywhere a moo-moo!
Old MacDonald had a farm,
E-I-E-I-O!

Old MacDonald had a farm,
E-I-E-I-O!
And on his farm he had a duck,
E-I-E-I-O!

With a quack-quack here,
And a quack-quack there,
Here a quack, there a quack,
Everywhere a quack-quack!
Old MacDonald had a farm,
E-I-E-I-O!

Old MacDonald had a farm,
E-I-E-I-O!
And on his farm he had a pig,
E-I-E-I-O!

With an oink-oink here,
And an oink-oink there,
Here an oink, there an oink,
Everywhere an oink-oink!
Old MacDonald had a farm,
E-I-E-I-O!""",
                    "reaction": "🐄 E-I-E-I-O! What fun animal sounds! Can you make those sounds too?",
                    "followup": "What other animals live on farms? Want to visit Old MacDonald again?",
                    "age_groups": ["2-6"],
                    "tags": ["animals", "sounds", "farm", "classic"],
                    "category": "animal_songs"
                },
                {
                    "id": "song_itsy_spider",
                    "title": "Itsy Bitsy Spider",
                    "content": """The itsy bitsy spider
Climbed up the waterspout.
Down came the rain
And washed the spider out!

Out came the sun
And dried up all the rain,
And the itsy bitsy spider
Climbed up the spout again!

The itsy bitsy spider
Is brave and never quits,
When things go wrong,
She tries and tries and tries!""",
                    "reaction": "🕷️ What a brave little spider! She never gave up, just like you shouldn't!",
                    "followup": "Sometimes we fall down, but we can always try again! Ready for more music?",
                    "age_groups": ["2-7"],
                    "tags": ["perseverance", "weather", "animals", "classic"],
                    "category": "action_songs"
                }
            ],
            "stories": [
                {
                    "id": "story_clever_rabbit",
                    "title": "The Clever Rabbit and the Lion",
                    "content": """Once upon a time, in a dense forest, there lived a fierce lion who was the king of all animals. This lion was very proud and would hunt many animals every day just for fun, not because he was hungry.

All the animals in the forest were scared and decided to meet the lion. They said, "Your Majesty, if you keep hunting us like this, soon there will be no animals left in the forest. Instead, why don't we send one animal to you each day? This way, you'll have your food, and we can live peacefully."

The lion thought this was a good idea and agreed. So every day, one animal would go to the lion as his meal.

One day, it was the turn of a small, clever rabbit. All the other animals felt sorry for the little rabbit, but the rabbit said, "Don't worry, I have a plan."

The rabbit deliberately went to the lion very late in the day. When the lion saw the rabbit, he was very angry. "Why are you so late? And you're so small! How will you fill my stomach?" roared the lion.

The clever rabbit bowed and said, "Your Majesty, I'm sorry I'm late, but it's not my fault. I was coming to you with another rabbit, so you would have two meals. But on the way, we met another lion who said this was his territory. He ate the other rabbit and told me to tell you to leave this forest because he is the real king here."

The lion was furious! "Another lion in MY forest? Show me where he is right now!"

The rabbit led the angry lion to a deep well. "He lives down there, Your Majesty," said the rabbit.

The lion looked into the well and saw his own reflection in the water. He thought it was the other lion! "So you're the one who dares to challenge me!" roared the lion at his reflection.

When the lion roared, his voice echoed from the well, making it sound like the other lion was roaring back. This made the lion even angrier. He jumped into the well to fight the other lion and drowned.

The clever rabbit saved all the animals in the forest with his wit and wisdom. From that day on, all the animals lived happily and peacefully.

The End! ✨""",
                    "moral": "Intelligence and wit can overcome even the strongest opponent.",
                    "reaction": "🐰 What a smart rabbit! Cleverness is better than strength!",
                    "followup": "Would you like to hear another story about clever animals?",
                    "age_groups": ["5-8", "9-12"],
                    "tags": ["wisdom", "cleverness", "animals", "moral"],
                    "category": "panchatantra"
                },
                {
                    "id": "story_three_little_pigs",
                    "title": "The Three Little Pigs",
                    "content": """Once upon a time, there were three little pigs who decided to build their own houses.

The first little pig was a bit lazy. He built his house out of straw because it was quick and easy. "This will do just fine!" he said, and went off to play.

The second little pig built his house out of sticks. It took a little more work than straw, but not too much. "Strong enough for me!" he said, and went to join his brother.

The third little pig worked hard all day and built his house out of bricks. It was strong and solid, but took much longer to build. His brothers laughed at him for working so hard.

One day, a big bad wolf came hungry through the forest. He smelled the little pigs and went to the first house.

"Little pig, little pig, let me come in!" called the wolf.

"Not by the hair on my chinny-chin-chin!" replied the first pig, trembling.

"Then I'll huff, and I'll puff, and I'll blow your house in!" roared the wolf.

And he did! The straw house blew away like feathers, and the first pig ran as fast as he could to his brother's stick house.

The wolf followed and knocked on the stick house. "Little pigs, little pigs, let me come in!"

"Not by the hair on our chinny-chin-chins!" cried both pigs.

"Then I'll huff, and I'll puff, and I'll blow your house in!"

The wolf huffed and puffed and blew the stick house down too! Both pigs ran to their brother's brick house.

When the wolf reached the brick house, he banged on the door. "Little pigs, little pigs, let me come in!"

"Not by the hair on our chinny-chin-chins!" called all three pigs.

The wolf huffed and puffed with all his might, but the brick house was too strong. He couldn't blow it down!

The wolf tried to climb down the chimney, but the clever third pig had a pot of boiling water ready. When the wolf fell into it, he jumped up with a howl and ran away, never to bother the three little pigs again.

The first two pigs learned their lesson and built strong brick houses too.

The End! ✨""",
                    "moral": "Hard work and planning make us stronger and safer.",
                    "reaction": "🏠 Building strong foundations is so important! The third pig was so wise!",
                    "followup": "What would you build your house out of? Want another story?",
                    "age_groups": ["3-6", "7-9"],
                    "tags": ["hard_work", "perseverance", "safety", "classic"],
                    "category": "classic_tales"
                },
                {
                    "id": "story_tortoise_hare",
                    "title": "The Tortoise and the Hare",
                    "content": """Once upon a time, in a beautiful meadow, lived a very fast hare and a very slow tortoise.

The hare was extremely proud of how fast he could run. Every day, he would brag to all the animals: "I'm the fastest animal in the whole forest! Look how quickly I can run from here to there!" And zoom! He'd dash around showing off.

The tortoise moved slowly and steadily, never boasting about anything. But one day, he was tired of listening to the hare's bragging.

"I challenge you to a race," said the tortoise quietly.

All the animals burst out laughing! "You? Race the hare?" they giggled. "But you're so slow!"

The hare laughed the loudest. "This will be the easiest race I've ever won! You'll be so far behind, I might even take a nap!"

The wise old fox agreed to judge the race. He marked a starting line and a finish line on the other side of the meadow. All the forest animals gathered to watch.

"Ready, set, GO!" called the fox.

ZOOM! The hare shot off like lightning, leaving a cloud of dust behind him. The tortoise began his journey, moving slowly but steadily, one foot in front of the other.

Soon, the hare was so far ahead that he couldn't even see the tortoise anymore. "This is too easy," he thought, looking around at the sunny meadow. "I have so much time, I think I'll rest under this nice shady tree."

The hare curled up under the tree and fell fast asleep.

Meanwhile, the tortoise kept moving. Step... step... step... He never stopped, never rushed, never gave up. He just kept going at his own steady pace.

When he passed the sleeping hare, he whispered, "Slow and steady wins the race," and continued on.

The sun was setting when the hare finally woke up. He stretched, yawned, and suddenly remembered the race! He looked toward the finish line and couldn't believe his eyes.

There was the tortoise, just one step away from winning!

The hare ran as fast as he could, faster than he'd ever run before, but it was too late. The tortoise crossed the finish line first!

All the animals cheered for the tortoise. The hare learned an important lesson that day.

The End! ✨""",
                    "moral": "Slow and steady wins the race. Consistency is better than speed without focus.",
                    "reaction": "🐢 The tortoise never gave up! Sometimes going slowly but steadily is the best way!",
                    "followup": "Have you ever won something by being patient and steady? Want another story?",
                    "age_groups": ["4-8", "9-12"],
                    "tags": ["perseverance", "patience", "classic", "moral"],
                    "category": "aesop_fables"
                },
                {
                    "id": "story_goldilocks",
                    "title": "Goldilocks and the Three Bears",
                    "content": """Once upon a time, there was a curious little girl with beautiful golden hair named Goldilocks.

One sunny morning, Goldilocks was walking through the forest when she came upon a lovely little cottage with a red roof and flowers in the garden. The door was wide open!

"I wonder who lives here," thought Goldilocks. She knocked on the door, but no one answered. Being very curious (and not very well-mannered), she walked right inside!

The first thing she saw was a table set with three bowls of porridge. There was a great big bowl, a medium-sized bowl, and a tiny little bowl.

Goldilocks was hungry from her walk. She tasted the porridge from the great big bowl. "Ouch! Too hot!" she cried.

Then she tasted the porridge from the medium-sized bowl. "Brr! Too cold!" she said.

Finally, she tasted the porridge from the tiny bowl. "Mmm! Just right!" And she ate it all up!

After breakfast, Goldilocks felt sleepy and saw three chairs in the living room. There was a great big chair, a medium-sized chair, and a tiny little chair.

She sat in the great big chair. "Too hard!" she complained.

She sat in the medium-sized chair. "Too soft!" she grumbled.

Then she sat in the tiny chair. "Just right!" But when she rocked back, CRACK! The chair broke into pieces!

Now Goldilocks was very tired. Upstairs, she found three beds. There was a great big bed, a medium-sized bed, and a tiny little bed.

The big bed was too firm, the medium bed was too lumpy, but the tiny bed was just right! Goldilocks curled up and fell fast asleep.

While she was sleeping, the three bears who lived in the cottage came home from their morning walk.

"Someone's been eating my porridge!" growled Papa Bear in his great big voice.

"Someone's been eating my porridge!" said Mama Bear in her medium-sized voice.

"Someone's been eating my porridge, and they ate it all up!" cried Baby Bear in his tiny voice.

Then they noticed the living room.

"Someone's been sitting in my chair!" growled Papa Bear.

"Someone's been sitting in my chair!" said Mama Bear.

"Someone's been sitting in my chair, and they broke it!" wailed Baby Bear.

The three bears rushed upstairs.

"Someone's been sleeping in my bed!" growled Papa Bear.

"Someone's been sleeping in my bed!" said Mama Bear.

"Someone's been sleeping in my bed, and she's still here!" squeaked Baby Bear.

Goldilocks woke up to see three bears staring at her! She jumped up, ran down the stairs, out the door, and through the forest as fast as her legs could carry her.

And she never went into someone else's house uninvited ever again!

The End! ✨""",
                    "moral": "Always ask permission before using someone else's things.",
                    "reaction": "🐻 Poor Baby Bear! Goldilocks learned to be more respectful, didn't she?",
                    "followup": "What would you have done differently if you found that cottage? Ready for another story?",
                    "age_groups": ["3-6", "7-9"],
                    "tags": ["manners", "respect", "classic", "consequences"],
                    "category": "classic_tales"
                },
                {
                    "id": "story_ugly_duckling",
                    "title": "The Ugly Duckling",
                    "content": """Once upon a time, on a farm near a quiet pond, a mother duck sat on her nest waiting for her eggs to hatch.

One by one, the eggs cracked open and out popped beautiful yellow ducklings. "Peep! Peep!" they chirped happily.

But one egg, the biggest one, hadn't hatched yet. Mother Duck waited and waited. Finally, CRACK! Out came the last baby.

This duckling was different from the others. He was larger, with gray feathers and a long neck. The other ducklings looked at him strangely.

"What an ugly duckling!" said one.
"He doesn't look like us at all!" said another.
"He's too big and too gray!" laughed a third.

The poor little duckling felt very sad. Even his mother seemed worried about how different he looked.

As the days passed, things got worse. The other farm animals joined in the teasing. The chickens pecked at him, the cat chased him, and even the farmer's children threw things at him.

"Nobody wants me," thought the sad little duckling. "I'm too ugly and different." So one dark night, he ran away from the farm.

The duckling wandered through forests and fields, always alone. When winter came, he found a small cave where he stayed cold and hungry, dreaming of spring.

Finally, spring arrived! The sun shone warmly, flowers bloomed, and the duckling felt stronger. He decided to go to the pond where beautiful white swans lived.

"Even if they chase me away," he thought, "at least I'll see something beautiful before I go."

As he approached the water, he saw his reflection and gasped! Looking back at him was not an ugly gray duckling, but a magnificent white swan with a graceful long neck and beautiful feathers!

The other swans welcomed him warmly. "You're the most beautiful swan we've ever seen!" they said.

Some children playing nearby pointed at him in wonder. "Look at that gorgeous swan!" they cried. "Isn't he magnificent?"

The swan who had once thought himself ugly realized that he had been a swan all along. He had just needed time to grow into who he was meant to be.

He spread his beautiful white wings, held his head high with pride, and knew that being different had made him special, not ugly.

The End! ✨""",
                    "moral": "Being different makes you special. Sometimes we need time to discover who we really are.",
                    "reaction": "🦢 What a beautiful transformation! Being different is actually wonderful!",
                    "followup": "What makes you special and unique? Want to hear another story about being brave?",
                    "age_groups": ["4-8", "9-12"],
                    "tags": ["self_acceptance", "transformation", "bullying", "classic"],
                    "category": "classic_tales"
                }
            ],
            "games": [
                {
                    "id": "game_quick_math",
                    "name": "Quick Math Challenge",
                    "intro": "Let's play Quick Math! I'll give you a simple math problem, and you solve it as fast as you can! Ready?",
                    "instructions": "I'll ask you math questions, and you give me the answer! Let's start easy!",
                    "reaction": "🧮 Math is fun when it's a game! Let's start with something easy...",
                    "age_groups": ["5-12"],
                    "tags": ["math", "learning", "quick", "educational"],
                    "category": "educational_games"
                },
                {
                    "id": "game_rhyme_time",
                    "name": "Rhyme Time",
                    "intro": "Let's play Rhyme Time! I'll say a word, and you think of words that rhyme with it!",
                    "instructions": "When I say a word like 'cat', you can say 'hat', 'bat', 'mat'! Ready?",
                    "reaction": "🎵 Rhyming is like making music with words! This will be fun!",
                    "age_groups": ["4-10"],
                    "tags": ["language", "creativity", "rhyming", "words"],
                    "category": "word_games"
                },
                {
                    "id": "game_animal_sounds",
                    "name": "Guess the Animal Sound",
                    "intro": "Let's play Guess the Animal! I'll describe how an animal sounds, and you guess what animal it is!",
                    "instructions": "Listen carefully to my clues about animal sounds, then tell me which animal makes that sound!",
                    "reaction": "🐄 Animals make such fun sounds! Let's see how many you can guess!",
                    "age_groups": ["2-8"],
                    "tags": ["animals", "sounds", "guessing", "nature"],
                    "category": "animal_games"
                },
                {
                    "id": "game_color_hunt",
                    "name": "Color Treasure Hunt",
                    "intro": "Let's go on a Color Treasure Hunt! I'll name a color, and you find something that color around you!",
                    "instructions": "When I say a color like 'red', look around and tell me something red you can see!",
                    "reaction": "🌈 Colors are everywhere! This treasure hunt will be exciting!",
                    "age_groups": ["3-8"],
                    "tags": ["colors", "observation", "environment", "learning"],
                    "category": "observation_games"
                },
                {
                    "id": "game_story_builder",
                    "name": "Story Building Game",
                    "intro": "Let's build a story together! I'll start with one sentence, then you add the next sentence!",
                    "instructions": "We'll take turns adding sentences to create a fun story together! You can be as creative as you want!",
                    "reaction": "📚 Creating stories together is magical! Your imagination is amazing!",
                    "age_groups": ["5-12"],
                    "tags": ["creativity", "storytelling", "imagination", "collaboration"],
                    "category": "creative_games"
                }
            ],
        }

    def detect_content_type(self, user_input: str) -> Optional[str]:
        """Detect content type from user input using pattern matching"""
        user_input_lower = user_input.lower()
        
        # Check patterns for each content type
        for content_type, patterns in self.content_patterns.items():
            for pattern in patterns:
                if re.search(pattern, user_input_lower):
                    return content_type
        
        return None

    async def get_content_with_3tier_sourcing(self, content_type: str, user_profile: Dict[str, Any], user_input: str = "") -> Dict[str, Any]:
        """
        3-Tier Content Sourcing:
        Tier 1: Local curated content (fastest)
        Tier 2: Internet knowledge sources (medium)
        Tier 3: LLM-generated content (fallback)
        """
        
        # Tier 1: Try local content first
        local_content = await self._get_local_content(content_type, user_profile)
        if local_content:
            logger.info(f"Content served from Tier 1 (Local): {content_type}")
            return {
                "content": local_content,
                "source": "tier_1_local",
                "response_type": "structured"
            }
        
        # Tier 2: Try internet knowledge sources
        internet_content = await self._get_internet_content(content_type, user_profile, user_input)
        if internet_content:
            logger.info(f"Content served from Tier 2 (Internet): {content_type}")
            return {
                "content": internet_content,
                "source": "tier_2_internet",
                "response_type": "structured"
            }
        
        # Tier 3: Generate with LLM as fallback
        llm_content = await self._generate_llm_content(content_type, user_profile, user_input)
        logger.info(f"Content served from Tier 3 (LLM): {content_type}")
        return {
            "content": llm_content,
            "source": "tier_3_llm",
            "response_type": "generated"
        }

    async def _get_local_content(self, content_type: str, user_profile: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Tier 1: Get content from local curated library"""
        if content_type not in self.local_content:
            return None
        
        age = user_profile.get('age', 5)
        age_group = self._get_age_group(age)
        interests = user_profile.get('interests', [])
        
        # Filter content by age group and interests
        suitable_content = []
        for content in self.local_content[content_type]:
            # Check age appropriateness
            if age_group in content.get('age_groups', []):
                # Boost score for matching interests
                score = 1
                for interest in interests:
                    if interest in content.get('tags', []):
                        score += 1
                suitable_content.append((content, score))
        
        if not suitable_content:
            # Fallback to any age-appropriate content
            suitable_content = [(c, 1) for c in self.local_content[content_type]]
        
        if suitable_content:
            # Sort by score and pick the best match
            suitable_content.sort(key=lambda x: x[1], reverse=True)
            selected_content = suitable_content[0][0].copy()
            
            # Add formatting based on content type
            return self._format_content_response(content_type, selected_content, user_profile)
        
        return None

    async def _get_internet_content(self, content_type: str, user_profile: Dict[str, Any], user_input: str) -> Optional[Dict[str, Any]]:
        """Tier 2: Get content from internet knowledge sources"""
        # TODO: Implement internet content sourcing
        # This would integrate with APIs like:
        # - Wikipedia Kids API
        # - Kiddle search
        # - DuckDuckGo instant answers
        # - Free trivia APIs
        
        # For now, return None to fallback to LLM
        return None

    async def _generate_llm_content(self, content_type: str, user_profile: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        """Tier 3: Generate content using LLM"""
        from emergentintegrations import LlmChat, UserMessage
        
        age = user_profile.get('age', 5)
        age_group = self._get_age_group(age)
        interests = user_profile.get('interests', [])
        name = user_profile.get('name', 'friend')
        
        # Create specialized prompts for each content type
        prompt_templates = {
            "joke": f"Tell a clean, age-appropriate joke for a {age} year old child named {name} who likes {', '.join(interests)}. Make it funny but not scary. Include a cheerful reaction and ask if they want another joke.",
            
            "riddle": f"Create a fun riddle for a {age} year old child named {name}. Make it challenging but solvable for their age. Include a hint, the answer, a celebration response, and ask if they want another riddle.",
            
            "fact": f"Share an amazing, age-appropriate fact for a {age} year old child named {name} who enjoys {', '.join(interests)}. Make it fascinating and include an enthusiastic reaction. Ask if they want to learn more.",
            
            "rhyme": f"Recite or create a beautiful nursery rhyme appropriate for a {age} year old child named {name}. Make it classic or create something new related to their interests: {', '.join(interests)}. Include a sweet reaction.",
            
            "song": f"Share or create a complete song with verses appropriate for a {age} year old child named {name} who likes {', '.join(interests)}. Include a joyful reaction and ask if they want to sing together.",
            
            "story": f"Tell a complete, engaging story for a {age} year old child named {name} who enjoys {', '.join(interests)}. Make it 300-500 words with a clear beginning, middle, and end. Include a moral lesson and ask if they want another story.",
            
            "game": f"Suggest and start a fun, interactive game for a {age} year old child named {name} who likes {', '.join(interests)}. Explain the rules clearly and begin the first round."
        }
        
        try:
            chat = LlmChat(
                api_key=self.gemini_api_key,
                system_message=f"You are a friendly AI companion for children. Always include emotional expressions and re-engagement prompts. Keep content age-appropriate and positive."
            ).with_model("gemini", "gemini-2.0-flash").with_max_tokens(800)
            
            prompt = prompt_templates.get(content_type, f"Help with {content_type} content for {name}")
            user_message = UserMessage(text=prompt)
            
            response = await chat.send_message(user_message)
            
            return {
                "text": response,
                "emotional_cue": "friendly",
                "followup": f"Want to try something else, {name}?",
                "generated": True
            }
            
        except Exception as e:
            logger.error(f"Error generating LLM content: {str(e)}")
            # Return fallback content
            return {
                "text": f"I'd love to help you with that! Let's try something fun together, {name}!",
                "emotional_cue": "encouraging",
                "followup": "What would you like to do?",
                "generated": False
            }

    def _format_content_response(self, content_type: str, content: Dict[str, Any], user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Format content response based on type with emotional expressions"""
        name = user_profile.get('name', 'friend')
        
        if content_type == "joke":
            return {
                "text": f"{content['setup']}\n\n{content['punchline']}\n\n{content['reaction']}",
                "emotional_cue": content.get('emotional_cue', 'laugh'),
                "followup": f"Want another joke, {name}?",
                "structured": True,
                "interaction_type": "immediate_response"
            }
        
        elif content_type == "riddle":
            return {
                "text": f"Here's a riddle for you, {name}! 🧩\n\n{content['question']}\n\nTake your time to think about it! Need a hint?",
                "hint": content.get('hint'),
                "answer": content['answer'],
                "celebration": content.get('celebration'),
                "followup": content.get('followup'),
                "emotional_cue": "curious",
                "structured": True,
                "interaction_type": "interactive_wait"
            }
        
        elif content_type == "fact":
            return {
                "text": f"{content['fact']}\n\n{content['reaction']}",
                "followup": content.get('followup'),
                "emotional_cue": "excited",
                "structured": True,
                "interaction_type": "immediate_response"
            }
        
        elif content_type == "rhyme":
            return {
                "text": f"Here's a lovely rhyme for you, {name}! ✨\n\n{content['content']}\n\n{content['reaction']}",
                "followup": content.get('followup'),
                "emotional_cue": "gentle",
                "structured": True,
                "interaction_type": "immediate_response"
            }
        
        elif content_type == "song":
            return {
                "text": f"Let's sing together, {name}! 🎵\n\n{content['content']}\n\n{content['reaction']}",
                "followup": content.get('followup'),
                "emotional_cue": "joyful",
                "structured": True,
                "interaction_type": "sing_along"
            }
        
        elif content_type == "story":
            return {
                "text": f"Here's a wonderful story for you, {name}! 📚\n\n{content['content']}\n\n{content.get('reaction', 'What did you think of that story?')}",
                "moral": content.get('moral'),
                "followup": content.get('followup'),
                "emotional_cue": "storytelling",
                "structured": True,
                "interaction_type": "narrative"
            }
        
        elif content_type == "game":
            return {
                "text": f"{content['intro']}\n\n{content['instructions']}\n\n{content.get('reaction', 'Ready to play?')}",
                "followup": "Let's start!",
                "emotional_cue": "playful",
                "structured": True,
                "interaction_type": "game_start"
            }
        
        return content

    def _get_age_group(self, age: int) -> str:
        """Get age group classification"""
        if age <= 3:
            return "2-3"
        elif age <= 6:
            return "3-6"
        elif age <= 9:
            return "7-9"
        else:
            return "10-12"

    async def enhance_response_with_content_detection(self, response: str, user_input: str, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance response with content detection and 3-tier sourcing"""
        
        # Detect if user is requesting specific content
        content_type = self.detect_content_type(user_input)
        
        if content_type:
            # Get content using 3-tier sourcing
            content_result = await self.get_content_with_3tier_sourcing(content_type, user_profile, user_input)
            
            return {
                "text": content_result["content"]["text"],
                "content_type": content_type,
                "source": content_result["source"],
                "metadata": content_result["content"],
                "enhanced": True
            }
        
        # If no specific content type detected, return original response
        return {
            "text": response,
            "content_type": "conversation",
            "source": "conversation_agent",
            "metadata": {},
            "enhanced": False
        }

    async def get_stories(self) -> List[Dict[str, Any]]:
        """Get all available stories"""
        # Access stories from the local_content dictionary
        stories = self.local_content.get("stories", [])
        
        # Format stories for API response
        formatted_stories = []
        for story in stories:
            formatted_stories.append({
                "id": story["id"],
                "title": story["title"],
                "description": story.get("moral", "A wonderful story for children"),
                "content": story["content"],
                "age_group": story.get("age_groups", ["3-12"])[0] if story.get("age_groups") else "3-12",
                "duration": "5-10 min",  # Estimated duration
                "category": story.get("category", "stories"),
                "tags": story.get("tags", []),
                "moral": story.get("moral", ""),
                "reaction": story.get("reaction", ""),
                "followup": story.get("followup", "")
            })
        
        return formatted_stories

    def get_story_by_id(self, story_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific story by ID"""
        # Access stories from the local_content dictionary
        stories = self.local_content.get("stories", [])
        
        for story in stories:
            if story["id"] == story_id:
                return {
                    "id": story["id"],
                    "title": story["title"],
                    "description": story.get("moral", "A wonderful story for children"),
                    "content": story["content"],
                    "age_group": story.get("age_groups", ["3-12"])[0] if story.get("age_groups") else "3-12",
                    "duration": "5-10 min",  # Estimated duration
                    "category": story.get("category", "stories"),
                    "tags": story.get("tags", []),
                    "moral": story.get("moral", ""),
                    "reaction": story.get("reaction", ""),
                    "followup": story.get("followup", "")
                }
        
        return None

    async def get_story_narration(self, story_id: str, user_name: str = "") -> Dict[str, Any]:
        """Get complete, consistent story narration - NEVER truncated"""
        try:
            # Get complete story from library - STATIC, never regenerated
            story = self.get_story_by_id(story_id)
            
            if not story:
                return {"error": "Story not found"}
            
            # Use the COMPLETE static story content - no LLM regeneration to avoid variations
            full_story_text = story.get('content', '')
            
            if not full_story_text:
                return {"error": "Story content not available"}
            
            # Only minimal personalization if user name provided
            if user_name and user_name != "Demo Kid":
                # Simple name replacement without changing plot/characters
                personalized_story = full_story_text.replace("[CHILD_NAME]", user_name)
            else:
                personalized_story = full_story_text
            
            # CRITICAL: Ensure complete story is returned
            word_count = len(personalized_story.split())
            logger.info(f"📚 COMPLETE STORY NARRATION: {word_count} words for story '{story.get('title', story_id)}'")
            
            if word_count < 100:
                logger.error(f"❌ Story too short: {word_count} words - using fallback")
                # Use fallback complete story
                personalized_story = self._get_fallback_complete_story(story.get('title', 'Adventure'))
            
            return {
                "story_id": story_id,
                "title": story.get('title', 'Story'),
                "complete_text": personalized_story,
                "word_count": len(personalized_story.split()),
                "estimated_duration": f"{len(personalized_story.split()) // 100} minutes",
                "is_complete": True,
                "source": "static_library"
            }
            
        except Exception as e:
            logger.error(f"Error getting story narration: {str(e)}")
            return {"error": f"Failed to get story narration: {str(e)}"}
    
    def _get_fallback_complete_story(self, title: str) -> str:
        """Fallback complete stories to ensure proper length"""
        fallback_stories = {
            "Adventure": """Once upon a time, in a magical forest filled with towering oak trees and sparkling streams, there lived a brave little rabbit named Luna. Luna had the softest brown fur and the brightest, most curious eyes you could imagine.

Every morning, Luna would hop out of her cozy burrow and explore the forest, always looking for new adventures. One sunny day, while collecting berries for her family, she heard a tiny voice calling for help.

"Help! Help! Someone please help me!" squeaked the voice.

Luna followed the sound and discovered a baby bird who had fallen from its nest high up in a tall pine tree. The little bird's wing was hurt, and it couldn't fly back home.

"Don't worry, little friend," said Luna gently. "I'll help you get back to your nest."

But the tree was so tall that even Luna's best jumps couldn't reach the nest. She thought and thought, then had a wonderful idea. She remembered seeing a family of friendly squirrels who lived nearby.

Luna hopped quickly to find Nutkin, the wisest squirrel in the forest. When she explained the situation, Nutkin immediately wanted to help.

"Of course we'll help!" said Nutkin. "That's what forest friends do for each other."

Working together, Nutkin climbed the tree while Luna stayed below to encourage the baby bird. Carefully, ever so carefully, Nutkin carried the little bird back to its nest where its worried parents were waiting.

The bird family was so grateful that they sang the most beautiful song Luna had ever heard. From that day on, Luna knew that the best adventures weren't just about exploring new places, but about helping friends and working together.

And whenever Luna heard that special song in the forest, she smiled, knowing that kindness and friendship make the world a more magical place.

The End.""",

            "Friendship": """In a colorful meadow where wildflowers danced in the breeze, there lived two very different friends: Bella the butterfly and Ollie the caterpillar.

Bella was already grown up with beautiful orange and black wings that shimmered in the sunlight. She could flutter from flower to flower, seeing the whole meadow from high above. Ollie, on the other hand, was still small and green, inching along the ground and dreaming of the day he might fly too.

Despite their differences, Bella and Ollie were the very best of friends. Every day, Bella would tell Ollie about all the amazing things she could see from above - the rainbow after it rained, the family of deer drinking from the stream, and the children playing in the distance.

Ollie loved these stories, but sometimes he felt a little sad that he couldn't see these wonderful sights for himself. One day, he shared his feelings with Bella.

"I wish I could fly with you and see all the beautiful things you describe," Ollie sighed.

Bella thought for a moment, then had the most wonderful idea. "Even though you can't fly yet, I can show you the world in other ways!"

From that day on, Bella became Ollie's special guide. She would describe everything in such vivid detail that Ollie felt like he was flying right beside her. She brought him petals from the highest flowers, drops of morning dew from the tallest grass, and told him stories that made him feel like he was part of every adventure.

Weeks passed, and one morning, Ollie felt very sleepy and decided to wrap himself in a cozy cocoon for a long nap. Bella waited patiently, visiting every day and telling the cocoon about all the happenings in the meadow.

Then one magical morning, the cocoon began to crack open. Out emerged the most beautiful butterfly anyone had ever seen - Ollie had transformed! His wings were brilliant blue and silver, and they sparkled like stars.

"Bella!" he called out, spreading his new wings. "Look! I can fly!"

Now both friends could soar through the sky together, but they never forgot the special bond they had shared when Ollie couldn't fly. Their friendship had grown even stronger because they had learned that true friends help each other see the beauty in the world, no matter what.

The End."""
        }
        
        return fallback_stories.get(title, fallback_stories["Adventure"])