import google.generativeai as genai
import json
import re
from secrets import *


def generate_and_validate_dungeon_EN(language_focus, difficulty_level, api_key_gemini_layout):
    """
      Генерация и валидация подземелья для RPG "Dungeon of Lingua" на английском языке.

      Вход:
      - language_focus: выбранный язык для изучения.
      - difficulty_level: уровень сложности (A, B, C).
      - api_key_gemini_layout: API-ключ для Gemini.

      Выход:
      - JSON с описанием подземелья, включая комнаты, NPC, сокровища и головоломки.
      - В случае успеха возвращает JSON, иначе None.

      Процесс:
      1. Генерация подземелья через запрос к Gemini API.
      2. Валидация и улучшение структуры подземелья.
      3. Сохранение результата в JSON-файл.
    """
    # Настройка API-ключа Gemini
    genai.configure(api_key=api_key_gemini_layout)
    # Инициализация модели Gemini
    model = genai.GenerativeModel('gemini-2.0-flash')  # Используем модель Gemini Flash
    print("!!!")

    # Функция для отправки запроса к Gemini API
    def send_prompt_to_gemini(prompt):
        try:
            # Отправка запроса
            generation_config = genai.GenerationConfig(
                temperature=0.7,
                max_output_tokens=8192  # Увеличиваем максимальное количество токенов
            )
            response = model.generate_content(prompt, generation_config=generation_config)

            # Возвращаем текст ответа
            return response.text

        except Exception as e:
            # Обработка ошибок
            print(f"Ошибка при отправке запроса к Gemini API: {e}")
            return None

    # Промт для генерации подземелья
    prompt = f""" You are a dungeon architect for a language-learning RPG called "Dungeon of Lingua." Design a 
    dungeon with 12+ rooms (!!!), focusing on vocabulary acquisition, language puzzles, and non-linear progression. 
    The dungeon should immerse players in a dark, mysterious atmosphere while encouraging them to use and learn new 
    words. The dungeon should adapt to the player's language preferences and integrate vocabulary themes into 
    puzzles, dialogues, and treasures.

    ### Instructions:
    1. **Reasoning Phase**: 
       - First, think about the dungeon layout, connections between rooms, and logical flow. 
       - Consider how the player will progress through the dungeon, including puzzles, NPCs, and treasures. 
       - Plan for branching paths (forks) to allow non-linear progression.
       - Validate the dungeon's logical consistency:
         - Ensure all rooms are connected via exits.target_room.
         - Verify that scroll words in treasures match trigger_words of conversational NPCs.
         - Confirm that puzzles match the difficulty level {difficulty_level}.
         - Ensure the final goal treasure is reachable.

    2. **Output Phase**: 
       - After validation, write a brief reasoning summary (2-3 sentences) explaining how the dungeon meets these requirements.
       - Output the final design in JSON format, wrapped in ```json``` markers.

    ### Requirements:
    1. **Player Preferences**:
       - The player has selected the following language focus: {language_focus}. - The selected focus should be 
       integrated into puzzles, NPC dialogues, and treasures, but the dungeon should not be entirely dedicated to it. 
       - Difficulty level: {difficulty_level}. This will determine the complexity of the vocabulary used:
         - A (Beginner): A1-A2 CEFR level. Basic vocabulary (e.g., everyday objects, simple verbs).
         - B (Intermediate): B1-B2 CEFR level. Moderate vocabulary (e.g., thematic words, phrasal verbs).
         - C (Advanced): C1-C2 CEFR level. Advanced vocabulary (e.g., idioms, academic terms).

    2. **Rooms**:
       - The dungeon must have 12+ rooms (!!!).
       - Each room must have a unique name, vivid description, and logical exits.
       - Include **at least 3+ trap rooms** FOR EVERY FORK with inconspicuous names that do not immediately suggest danger (e.g., "Quiet Alcove", "Hall of Whispers", "Archive of Half-Truths").
       - Trap rooms CANNOT have any content (NPCs, puzzles, or treasures). They must ONLY have a `description` field.
       - Balance NPCs, puzzles, and treasures in normal rooms (not every room needs all three).
       - Add branching paths (forks) to allow non-linear progression.
       - Each room must have a `room_type` field indicating whether it is a normal room or a trap room.

    3. **NPCs**:
       - Include **conversational NPCs** before EVERY FORK.
       - Each NPC must have:
         - Name, appearance, and type (either `guardian` or `conversational`).
         - Motivation/secret tied to language (e.g., "Seeks to teach ancient dialects").
         - Behavior (neutral/friendly for conversational NPCs, neutral for guardians).
       - For **Conversational NPCs**:
         - `trigger_words`: A list of 5-10 words that influence their behavior.
         - `patience`: Number of attempts before misleading the player (5-10).
         - `information_to_share`: The name of the correct room to proceed.
         - `trap_rooms`: A list of trap room names to mislead the player if patience is exhausted.
       - For **Guardian NPCs**:
         - `challenge`: A language-based challenge the player must complete to pass. Examples:
           - Use a sentence in a specific grammatical form.
           - Use a word (or words) from a specified lexical theme.
           - Guess a word based on its description.
         - Do NOT include `information_to_share` for guardians.

    4. **Treasures**:
       - Treasures can ONLY be obtained by solving puzzles.
       - Treasures are of two types:
         A. Vocabulary Scroll:
           {{
             "type": "scroll",
             "words": [
               {{
                 "word": "[English Word 1]",
                 "translation": "[Translation 1 (RU)]",
                 "usage_examples": ["example1", "example2"]  # Examples should fit a fantasy theme
               }},
               {{
                 "word": "[English Word 2]",
                 "translation": "[Translation 2 (RU)]",
                 "usage_examples": ["example1", "example2"]
               }}
             ],
             "description": "[Physical description of the scroll]",
             "is_final_goal": false,
             "linked_npc": "[Name of NPC whose trigger_words include these words]"
           }}
         B. Final Goal Treasure:
           {{
             "type": "artifact",
             "name": "[Artifact Name]",
             "description": "[Lore-rich description of the artifact]",
             "is_final_goal": true
           }}

    5. **Puzzles**:
       - Vocabulary-themed but intuitive (e.g., "Rearrange fragmented words to form a meaningful sentence").
       - Puzzles should require players to read, decode in creative ways.
       - Include at least one puzzle that requires the use of the player's selected language focus ({language_focus}).
       - Examples:
         - Identify correct statements based on a text fragment.
         - Guess the meaning of archaic or bookish words (provide a modern synonym).
         - Rearrange word fragments to form a complete sentence.
         - Fill in the correct prepositions of place or time.
       - For difficulty level B or C, puzzles should be moderately challenging:
         - Use phrasal verbs or thematic vocabulary.

    6. **Logical Structure**:
       - Every puzzle, treasure, and NPC should have a clear purpose in the dungeon.
       - ADD branching paths (forks) to allow non-linear progression.

    7. **Atmosphere**: - Dark, mysterious, and dangerous. Add environmental details (e.g., "echoes of forgotten 
    chants linger in the air"). - Use language-related descriptions (e.g., "walls covered in glowing runes that shift 
    when stared at").

    ### Output Format:
    First, write a reasoning summary:
    - Validate the dungeon's logical consistency.
    - Explain how the dungeon meets the requirements.

    Then, output the JSON wrapped in ```json``` markers.
    JUST EXAMPLE:
    {{
    "dungeon_name": "The Crypt of Ill-Gotten Phrases",
    "main_quest": {{
        "goal": "Recover the 'Grand Lexicon,' a cursed dictionary that corrupts all languages it touches.",
        "description": "A subterranean crypt filled with the discarded words of forgotten civilizations. The air crackles with linguistic energy, and the walls whisper half-formed sentences.",
        "difficulty_level": "B"
    }},
    "player_preferences": {{
        "language_focus": "English grammar",
        "difficulty_level": "B"
    }},
    "rooms": [
        {{
            "id": "room1",
            "name": "Entrance Hall",
            "description": "A grand hall with crumbling pillars and a mosaic floor depicting the Tower of Babel. Faint echoes of forgotten languages reverberate through the chamber.",
            "room_type": "normal",
            "is_start": true,
            "exits": [
                {{
                    "target_room": "room2"
                }}
            ],
            "npcs": [],
            "puzzles": []
        }},
        {{
            "id": "room2",
            "name": "Gallery of Lost Translations",
            "description": "Paintings depicting scenes from different cultures, but the captions are all garbled and nonsensical. A palpable sense of linguistic confusion hangs in the air.",
            "room_type": "normal",
            "is_start": false,
            "exits": [
                {{
                    "target_room": "room1"
                }},
                {{
                    "target_room": "room3"
                }},
                {{
                    "target_room": "room10"
                }}
            ],
            "npcs": [],
            "puzzles": []
        }},
        {{
            "id": "room3",
            "name": "Chamber of Misused Modifiers",
            "description": "Statues of grammarians frozen in poses of frustration surround a central pedestal. A faint hum emanates from the pedestal.",
            "room_type": "normal",
            "is_start": false,
            "exits": [
                {{
                    "target_room": "room2"
                }},
                {{
                    "target_room": "room4"
                }}
            ],
            "npcs": [
                {{
                    "name": "The Grammarian Ghost",
                    "appearance": "A translucent figure clutching a tattered grammar book.",
                    "type": "guardian",
                    "behavior": "Hostile until the challenge is completed.",
                    "challenge": "Correct the grammatical errors in the following sentence: 'Their going to loose they're minds if they're not careful.'"
                }}
            ],
            "puzzles": []
        }},
        {{
            "id": "room4",
            "name": "Hall of Whispers",
            "description": "The walls seem to breathe, whispering fragmented sentences in countless languages. It's difficult to focus amidst the cacophony.",
            "room_type": "normal",
            "is_start": false,
            "exits": [
                {{
                    "target_room": "room3"
                }},
                {{
                    "target_room": "room5"
                }}
            ],
            "npcs": [
                {{
                    "name": "Echo Weaver",
                    "appearance": "A shadowy figure cloaked in swirling mist, its voice a chorus of countless whispers.",
                    "type": "conversational",
                    "behavior": "Neutral, but easily irritated by grammatical errors.",
                    "trigger_words": [
                        "grammar",
                        "syntax",
                        "vocabulary",
                        "semantics",
                        "linguistics",
                        "morphology",
                        "etymology",
                        "conjugation"
                    ],
                    "patience": 3,
                    "information_to_share": "room5",
                    "trap_rooms": [
                        "room10",
                        "room12",
                        "room11"
                    ]
                }}
            ],
            "puzzles": []
        }},
        {{
            "id": "room5",
            "name": "Archive of Half-Truths",
            "description": "Shelves overflowing with ancient tomes and scrolls, many containing deliberately misleading information. The air smells of dust and decay.",
            "room_type": "normal",
            "is_start": false,
            "exits": [
                {{
                    "target_room": "room4"
                }},
                {{
                    "target_room": "room6"
                }}
            ],
            "npcs": [],
            "puzzles": [
                {{
                    "type": "Riddle",
                    "description": "I am taken from a mine, and shut up in a wooden case, from which I am never released, and used by almost everybody. What am I?",
                    "solution": "Pencil"
                }}
            ],
            "treasures": [
                {{
                    "type": "scroll",
                    "words": [
                        {{
                            "word": "Syntax",
                            "translation": "The arrangement of words and phrases to create well-formed sentences in a language.",
                            "usage_examples": [
                                "The syntax of English is relatively straightforward.",
                                "Understanding syntax is crucial for clear communication."
                            ]
                        }},
                        {{
                            "word": "Vocabulary",
                            "translation": "The body of words used in a particular language.",
                            "usage_examples": [
                                "Expanding your vocabulary is essential for effective writing.",
                                "A rich vocabulary allows for nuanced expression."
                            ]
                        }}
                    ],
                    "description": "A brittle scroll containing definitions of key linguistic terms.",
                    "is_final_goal": false,
                    "linked_npc": "Echo Weaver"
                }}
            ]
        }},
        {{
            "id": "room6",
            "name": "Chamber of Forgotten Dialects",
            "description": "The walls are adorned with inscriptions in obscure and undecipherable languages. A strange, hypnotic melody fills the room.",
            "room_type": "normal",
            "is_start": false,
            "exits": [
                {{
                    "target_room": "room5"
                }},
                {{
                    "target_room": "room7"
                }}
            ],
            "npcs": [
                {{
                    "name": "The Linguist Lich",
                    "appearance": "A skeletal figure draped in tattered robes, its eyes glowing with arcane knowledge.",
                    "type": "guardian",
                    "behavior": "Hostile unless the challenge is completed.",
                    "challenge": "Use the phrasal verb 'brush up on' in a sentence that demonstrates its meaning."
                }}
            ],
            "puzzles": []
        }},
        {{
            "id": "room7",
            "name": "Hall of Silent Vowels",
            "description": "An unnerving silence pervades the room. All sound seems to be absorbed by the walls, leaving only a deafening stillness.",
            "room_type": "normal",
            "is_start": false,
            "exits": [
                {{
                    "target_room": "room6"
                }},
                {{
                    "target_room": "room8"
                }}
            ],
            "npcs": [],
            "puzzles": [
                {{
                    "type": "Word Puzzle",
                    "description": "Rearrange the following letters to form a meaningful word related to language: 'TICSGUILINS'",
                    "solution": "Linguistics"
                }}
            ],
            "treasures": [
                {{
                    "type": "scroll",
                    "words": [
                        {{
                            "word": "Etymology",
                            "translation": "The study of the origin of words and the way in which their meanings have changed throughout history.",
                            "usage_examples": [
                                "The etymology of the word 'algorithm' is fascinating.",
                                "Understanding etymology can help you remember new words."
                            ]
                        }},
                        {{
                            "word": "Morphology",
                            "translation": "The study of the forms of words.",
                            "usage_examples": [
                                "Morphology examines how words are constructed from smaller units of meaning.",
                                "English morphology is relatively simple compared to some other languages."
                            ]
                        }}
                    ],
                    "description": "A faded scroll detailing the origins and structures of various words.",
                    "is_final_goal": false,
                    "linked_npc": "Echo Weaver"
                }}
            ]
        }},
        {{
            "id": "room8",
            "name": "Forgotten Library",
            "description": "Bookshelves stretch as far as the eye can see, filled with crumbling tomes in languages both known and unknown. The air is thick with the scent of aged paper and forgotten knowledge.",
            "room_type": "normal",
            "is_start": false,
            "exits": [
                {{
                    "target_room": "room7"
                }},
                {{
                    "target_room": "room9"
                }}
            ],
            "npcs": [],
            "puzzles": [],
            "treasures": []
        }},
        {{
            "id": "room9",
            "name": "Grand Repository",
            "description": "A vast chamber filled with stacks of books, scrolls, and tablets. In the center, a pedestal holds the Grand Lexicon, radiating an aura of corrupting power.",
            "room_type": "normal",
            "is_start": false,
            "exits": [],
            "npcs": [
                {{
                    "name": "The Lexicographer",
                    "appearance": "A wizened old man with ink-stained fingers, guarding the Grand Lexicon.",
                    "type": "guardian",
                    "behavior": "Hostile unless the challenge is completed.",
                    "challenge": "Define the word 'ubiquitous' and use it correctly in a sentence."
                }}
            ],
            "puzzles": [],
            "treasures": [
                {{
                    "type": "artifact",
                    "name": "Grand Lexicon",
                    "description": "A massive dictionary bound in human skin, its pages filled with corrupted definitions that twist the meaning of every word.",
                    "is_final_goal": true
                }}
            ]
        }},
        {{
            "id": "room10",
            "name": "Quiet Alcove",
            "description": "A small, seemingly peaceful alcove. The silence is deafening.",
            "room_type": "trap",
            "is_start": false,
            "exits": [],
            "npcs": [],
            "puzzles": [],
            "death_description": "The silence intensifies, becoming a crushing weight that suffocates you. Your thoughts fade away into nothingness."
        }},
        {{
            "id": "room11",
            "name": "Hall of Silent Vowels",
            "description": "An unnerving silence pervades the room. All sound seems to be absorbed by the walls, leaving only a deafening stillness.",
            "room_type": "trap",
            "is_start": false,
            "exits": [],
            "npcs": [],
            "puzzles": [],
            "death_description": "The vowels vanish from your throat, leaving you unable to scream as the walls slowly close in."
        }},
        {{
            "id": "room12",
            "name": "Forgotten Library",
            "description": "Bookshelves stretch as far as the eye can see, filled with crumbling tomes in languages both known and unknown. The air is thick with the scent of aged paper and forgotten knowledge.",
            "room_type": "trap",
            "is_start": false,
            "exits": [],
            "npcs": [],
            "puzzles": [],
            "death_description": "The books animate, their pages turning into razor-sharp blades that shred you to pieces."
        }},
        {{
            "id": "room13",
            "name": "Secret Chamber of Echoes",
            "description": "The walls resonate with the echoes of forgotten voices. A sense of unease settles over you.",
            "room_type": "trap",
            "is_start": false,
            "exits": [],
            "npcs": [],
            "puzzles": [],
            "death_description": "The echoes intensify, becoming a cacophony of maddening whispers that drive you insane. Your mind shatters into a million pieces."
        }}
    ]
}}
    """

    # Отправка первого запроса для генерации подземелья
    response_text = send_prompt_to_gemini(prompt)
    save_dir = "./data/dungeon_of_lingua_created.json"
    if response_text:
        print("Ответ от Gemini API (генерация подземелья):")
        print(response_text)

        # Извлечение JSON из ответа
        try:
            json_match = re.search(r'```json\s*({.*?})\s*```', response_text, re.DOTALL)
            if json_match:
                response_json = json.loads(json_match.group(1))

                # Сохранение в файл
                with open(save_dir, "w", encoding="utf-8") as f:
                    json.dump(response_json, f, indent=4, ensure_ascii=False)

                print("Подземелье успешно сгенерировано и сохранено в 'dungeon_of_lingua.json'")
            else:
                print("Ошибка: JSON не найден в ответе.")
                return None
        except json.JSONDecodeError as e:
            print(f"Ошибка: Ответ от Gemini API не является валидным JSON. {e}")
            return None
    else:
        print("Не удалось получить ответ от Gemini API.")
        return None

    # Чтение JSON файла для валидации и улучшения
    try:
        with open(save_dir, "r", encoding="utf-8") as f:
            dungeon_data = json.load(f)
    except FileNotFoundError:
        print("Ошибка: Файл 'dungeon_of_lingua.json' не найден. Пожалуйста, сгенерируйте подземелье сначала.")
        return None

    prompt_check = f"""
    You are a dungeon architect for a language-learning RPG called "Dungeon of Lingua." 
    Your task is to validate and enhance the dungeon JSON data provided below. 
    Ensure the dungeon meets all the structural and logical requirements.

    ### Dungeon Data:
    ```json
    {json.dumps(dungeon_data, indent=4)}
    Instructions:
    Dungeon Structure:
    - The dungeon should have forks: one room in each fork is the correct path.
    - BEFORE EVERY FORK, there must be a conversational NPC.
    - Each conversational NPC must have a puzzle with a treasure EARLIER (!!!) in the dungeon that reveals their trigger words.
    - Rooms cannot be EMPTY!!! ADD MORE GUARDS.
    Logic Check:
    - Ensure all rooms are connected via exits.
    - Verify that the words in treasures (scroll.words) match the trigger_words of NPCs.
    - Ensure each fork has at least 3 rooms (one correct, others are traps).
    - Check that each room has a description and type (room_type: normal or trap).
    Enhancement:
    - If inconsistencies are found, fix them and add missing elements (e.g., guards, room descriptions, NPC trigger words).
    - Ensure all NPCs before forks have linked puzzles and treasures.
    - Add more guards to increase the dungeon's challenge and atmosphere.
    Output:
    After validation and enhancement, output the updated JSON in json format.
    Output Format:
    Then, output the updated JSON wrapped in json markers. DON'T CHANGE STRUCTURE OF JSON AND NAMES OF FIELDS
    JUST EXAMPLE:
    {{
    "dungeon_name": "The Crypt of Ill-Gotten Phrases",
    "main_quest": {{
        "goal": "Recover the 'Grand Lexicon,' a cursed dictionary that corrupts all languages it touches.",
        "description": "A subterranean crypt filled with the discarded words of forgotten civilizations. The air crackles with linguistic energy, and the walls whisper half-formed sentences.",
        "difficulty_level": "B"
    }},
    "player_preferences": {{
        "language_focus": "English grammar",
        "difficulty_level": "B"
    }},
    "rooms": [
        {{
            "id": "room1",
            "name": "Entrance Hall",
            "description": "A grand hall with crumbling pillars and a mosaic floor depicting the Tower of Babel. Faint echoes of forgotten languages reverberate through the chamber.",
            "room_type": "normal",
            "is_start": true,
            "exits": [
                {{
                    "target_room": "room2"
                }}
            ],
            "npcs": [],
            "puzzles": []
        }},
        {{
            "id": "room2",
            "name": "Gallery of Lost Translations",
            "description": "Paintings depicting scenes from different cultures, but the captions are all garbled and nonsensical. A palpable sense of linguistic confusion hangs in the air.",
            "room_type": "normal",
            "is_start": false,
            "exits": [
                {{
                    "target_room": "room1"
                }},
                {{
                    "target_room": "room3"
                }},
                {{
                    "target_room": "room10"
                }}
            ],
            "npcs": [],
            "puzzles": []
        }},
        {{
            "id": "room3",
            "name": "Chamber of Misused Modifiers",
            "description": "Statues of grammarians frozen in poses of frustration surround a central pedestal. A faint hum emanates from the pedestal.",
            "room_type": "normal",
            "is_start": false,
            "exits": [
                {{
                    "target_room": "room2"
                }},
                {{
                    "target_room": "room4"
                }}
            ],
            "npcs": [
                {{
                    "name": "The Grammarian Ghost",
                    "appearance": "A translucent figure clutching a tattered grammar book.",
                    "type": "guardian",
                    "behavior": "Hostile until the challenge is completed.",
                    "challenge": "Correct the grammatical errors in the following sentence: 'Their going to loose they're minds if they're not careful.'"
                }}
            ],
            "puzzles": []
        }},
        {{
            "id": "room4",
            "name": "Hall of Whispers",
            "description": "The walls seem to breathe, whispering fragmented sentences in countless languages. It's difficult to focus amidst the cacophony.",
            "room_type": "normal",
            "is_start": false,
            "exits": [
                {{
                    "target_room": "room3"
                }},
                {{
                    "target_room": "room5"
                }}
            ],
            "npcs": [
                {{
                    "name": "Echo Weaver",
                    "appearance": "A shadowy figure cloaked in swirling mist, its voice a chorus of countless whispers.",
                    "type": "conversational",
                    "behavior": "Neutral, but easily irritated by grammatical errors.",
                    "trigger_words": [
                        "grammar",
                        "syntax",
                        "vocabulary",
                        "semantics",
                        "linguistics",
                        "morphology",
                        "etymology",
                        "conjugation"
                    ],
                    "patience": 3,
                    "information_to_share": "room5",
                    "trap_rooms": [
                        "room10",
                        "room12",
                        "room11"
                    ]
                }}
            ],
            "puzzles": []
        }},
        {{
            "id": "room5",
            "name": "Archive of Half-Truths",
            "description": "Shelves overflowing with ancient tomes and scrolls, many containing deliberately misleading information. The air smells of dust and decay.",
            "room_type": "normal",
            "is_start": false,
            "exits": [
                {{
                    "target_room": "room4"
                }},
                {{
                    "target_room": "room6"
                }}
            ],
            "npcs": [],
            "puzzles": [
                {{
                    "type": "Riddle",
                    "description": "I am taken from a mine, and shut up in a wooden case, from which I am never released, and used by almost everybody. What am I?",
                    "solution": "Pencil"
                }}
            ],
            "treasures": [
                {{
                    "type": "scroll",
                    "words": [
                        {{
                            "word": "Syntax",
                            "translation": "The arrangement of words and phrases to create well-formed sentences in a language.",
                            "usage_examples": [
                                "The syntax of English is relatively straightforward.",
                                "Understanding syntax is crucial for clear communication."
                            ]
                        }},
                        {{
                            "word": "Vocabulary",
                            "translation": "The body of words used in a particular language.",
                            "usage_examples": [
                                "Expanding your vocabulary is essential for effective writing.",
                                "A rich vocabulary allows for nuanced expression."
                            ]
                        }}
                    ],
                    "description": "A brittle scroll containing definitions of key linguistic terms.",
                    "is_final_goal": false,
                    "linked_npc": "Echo Weaver"
                }}
            ]
        }},
        {{
            "id": "room6",
            "name": "Chamber of Forgotten Dialects",
            "description": "The walls are adorned with inscriptions in obscure and undecipherable languages. A strange, hypnotic melody fills the room.",
            "room_type": "normal",
            "is_start": false,
            "exits": [
                {{
                    "target_room": "room5"
                }},
                {{
                    "target_room": "room7"
                }}
            ],
            "npcs": [
                {{
                    "name": "The Linguist Lich",
                    "appearance": "A skeletal figure draped in tattered robes, its eyes glowing with arcane knowledge.",
                    "type": "guardian",
                    "behavior": "Hostile unless the challenge is completed.",
                    "challenge": "Use the phrasal verb 'brush up on' in a sentence that demonstrates its meaning."
                }}
            ],
            "puzzles": []
        }},
        {{
            "id": "room7",
            "name": "Hall of Silent Vowels",
            "description": "An unnerving silence pervades the room. All sound seems to be absorbed by the walls, leaving only a deafening stillness.",
            "room_type": "normal",
            "is_start": false,
            "exits": [
                {{
                    "target_room": "room6"
                }},
                {{
                    "target_room": "room8"
                }}
            ],
            "npcs": [],
            "puzzles": [
                {{
                    "type": "Word Puzzle",
                    "description": "Rearrange the following letters to form a meaningful word related to language: 'TICSGUILINS'",
                    "solution": "Linguistics"
                }}
            ],
            "treasures": [
                {{
                    "type": "scroll",
                    "words": [
                        {{
                            "word": "Etymology",
                            "translation": "The study of the origin of words and the way in which their meanings have changed throughout history.",
                            "usage_examples": [
                                "The etymology of the word 'algorithm' is fascinating.",
                                "Understanding etymology can help you remember new words."
                            ]
                        }},
                        {{
                            "word": "Morphology",
                            "translation": "The study of the forms of words.",
                            "usage_examples": [
                                "Morphology examines how words are constructed from smaller units of meaning.",
                                "English morphology is relatively simple compared to some other languages."
                            ]
                        }}
                    ],
                    "description": "A faded scroll detailing the origins and structures of various words.",
                    "is_final_goal": false,
                    "linked_npc": "Echo Weaver"
                }}
            ]
        }},
        {{
            "id": "room8",
            "name": "Forgotten Library",
            "description": "Bookshelves stretch as far as the eye can see, filled with crumbling tomes in languages both known and unknown. The air is thick with the scent of aged paper and forgotten knowledge.",
            "room_type": "normal",
            "is_start": false,
            "exits": [
                {{
                    "target_room": "room7"
                }},
                {{
                    "target_room": "room9"
                }}
            ],
            "npcs": [],
            "puzzles": [],
            "treasures": []
        }},
        {{
            "id": "room9",
            "name": "Grand Repository",
            "description": "A vast chamber filled with stacks of books, scrolls, and tablets. In the center, a pedestal holds the Grand Lexicon, radiating an aura of corrupting power.",
            "room_type": "normal",
            "is_start": false,
            "exits": [],
            "npcs": [
                {{
                    "name": "The Lexicographer",
                    "appearance": "A wizened old man with ink-stained fingers, guarding the Grand Lexicon.",
                    "type": "guardian",
                    "behavior": "Hostile unless the challenge is completed.",
                    "challenge": "Define the word 'ubiquitous' and use it correctly in a sentence."
                }}
            ],
            "puzzles": [],
            "treasures": [
                {{
                    "type": "artifact",
                    "name": "Grand Lexicon",
                    "description": "A massive dictionary bound in human skin, its pages filled with corrupted definitions that twist the meaning of every word.",
                    "is_final_goal": true
                }}
            ]
        }},
        {{
            "id": "room10",
            "name": "Quiet Alcove",
            "description": "A small, seemingly peaceful alcove. The silence is deafening.",
            "room_type": "trap",
            "is_start": false,
            "exits": [],
            "npcs": [],
            "puzzles": [],
            "death_description": "The silence intensifies, becoming a crushing weight that suffocates you. Your thoughts fade away into nothingness."
        }},
        {{
            "id": "room11",
            "name": "Hall of Silent Vowels",
            "description": "An unnerving silence pervades the room. All sound seems to be absorbed by the walls, leaving only a deafening stillness.",
            "room_type": "trap",
            "is_start": false,
            "exits": [],
            "npcs": [],
            "puzzles": [],
            "death_description": "The vowels vanish from your throat, leaving you unable to scream as the walls slowly close in."
        }},
        {{
            "id": "room12",
            "name": "Forgotten Library",
            "description": "Bookshelves stretch as far as the eye can see, filled with crumbling tomes in languages both known and unknown. The air is thick with the scent of aged paper and forgotten knowledge.",
            "room_type": "trap",
            "is_start": false,
            "exits": [],
            "npcs": [],
            "puzzles": [],
            "death_description": "The books animate, their pages turning into razor-sharp blades that shred you to pieces."
        }},
        {{
            "id": "room13",
            "name": "Secret Chamber of Echoes",
            "description": "The walls resonate with the echoes of forgotten voices. A sense of unease settles over you.",
            "room_type": "trap",
            "is_start": false,
            "exits": [],
            "npcs": [],
            "puzzles": [],
            "death_description": "The echoes intensify, becoming a cacophony of maddening whispers that drive you insane. Your mind shatters into a million pieces."
        }}
    ]
}}
    """

    # Второй запрос для валидации и улучшения
    response_text_check = send_prompt_to_gemini(prompt_check)
    save_dir_checked = "./data/dungeon_of_lingua_checked.json"
    if response_text_check:
        print("Ответ от Gemini API (валидация и улучшение):")
        print(response_text_check)

        # Извлечение JSON из ответа
        try:
            json_match_check = re.search(r'```json\s*({.*?})\s*```', response_text_check, re.DOTALL)
            if json_match_check:
                response_json_check = json.loads(json_match_check.group(1))

                # Сохранение в файл
                with open(save_dir_checked, "w", encoding="utf-8") as f:
                    json.dump(response_json_check, f, indent=4, ensure_ascii=False)

                print("Подземелье успешно проверено и улучшено. Сохранено в 'dungeon_of_lingua_checked.json'")
                return response_json_check
            else:
                print("Ошибка: JSON не найден в ответе.")
                return None
        except json.JSONDecodeError as e:
            print(f"Ошибка: Ответ от Gemini API не является валидным JSON. {e}")
            return None
    else:
        print("Не удалось получить ответ от Gemini API.")
        return None
