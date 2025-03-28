import google.generativeai as genai
import json
import re
from screens.generate_maze import generate_maze, convert_to_json, add_npcs_to_json,\
    add_puzzles_and_treasures, add_guardians, package_dungeon
from screens.simulate_session import add_random_id_to_json

def generate_and_validate_dungeon_EN(language_focus, difficulty_level, api_key_gemini_layout):
    genai.configure(api_key=api_key_gemini_layout)
    generation_config = genai.GenerationConfig(
        temperature=0.7,
        max_output_tokens=8192
    )
    model = genai.GenerativeModel('gemini-2.0-flash', generation_config=generation_config)

    maze = generate_maze(difficulty_level)
    json_data = convert_to_json(maze)
    json_data = add_npcs_to_json(json_data)
    json_data = add_puzzles_and_treasures(json_data)
    json_data = add_guardians(json_data)
    final_data = package_dungeon(json_data, difficulty_level)

    with open("./data/final_dungeon.json", 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=4, ensure_ascii=False)

    prompt = f"""You are a dungeon architect for a language-learning RPG called "Dungeon of Lingua". 
Your task is to fill all empty fields in the provided dungeon JSON structure while maintaining strict consistency with game mechanics and thematic requirements.

The player has selected the following language focus: {language_focus}.
The selected focus should be integrated into puzzles, NPC dialogues, and treasures, but the dungeon should not be entirely dedicated to it. 

### Critical Requirements:
1. **NPC System**:
   - Replace ALL generic NPC IDs (npc1, npc2, npc3) with unique fantasy names
   - Each conversational NPC must:
     * Have 5-10 simple fantasy words ("potion", "scroll", "dagger")
     * Clearly hint at these words in their appearance
     * Example: 
       - Name: "Alchemist Bram" 
       - Appearance: "Gnome with bubbling vials and herb-stained fingers"
       - Trigger words: ["potion", "vial", "herb", "ingredient", "concoction"]

2. **Scroll Validation**:
   - EVERY scroll's linked_npc MUST reference an EXISTING conversational NPC by exact name
   - Scroll words MUST be exact matches from their NPC's trigger words
   - Example valid connection:
     ```json
     {{
       "linked_npc": "Alchemist Bram",  // Must match NPC name exactly
       "words": ["potion", "herb"]      // Must be from Bram's triggers
     }}
     ```

3. **Strict Task Requirements**:
   ALL challenges must test ONLY:
   - Vocabulary usage in fantasy contexts
   NO abstract/non-language tasks allowed (!!!)

4. **Challenge Design by Level**:
   - **A (Beginner)**:
     *Vocabulary*: Basic items ("sword", "spell", "gold")
     *Tasks*:
       - "Name 3 items: [dagger, ___, ___]"
       - "Complete: The warrior ___ (carry) a sword"

   - **B (Intermediate)**:
     *Vocabulary*: Adventuring terms ("rations", "torch")
     *Tasks*:
       - "Correct: 'We needs ten torches'"
       - "Use 'healing potion' in a sentence"

   - **C (Advanced)**:
     *Vocabulary*: Magic terms ("spellbook", "incantation")
     *Tasks*:
       - "Rewrite: 'I study the tome' (past tense)"
       - "Explain 'enchanted' in: 'The ___ sword glows'"

5. **Scroll Template**:
```json
{{
  "type": "scroll",
  "words": [
    {{
      "word": "potion",
      "translation": "зелье",
      "usage_examples": [
        "The healing potion restores 10 HP",
        "This potion smells like rotten eggs"
      ]
    }},
    {{
      "word": "herb",
      "translation": "трава",
      "usage_examples": [
        "Magic herbs grow in moonlit caves",
        "The herb's leaves shimmer blue"
      ]
    }}
  ],
  "description": "A stained parchment with herbal diagrams",
  "is_final_goal": false,
  "linked_npc": "Alchemist Bram"  // MUST match existing NPC
}}

### JSON Structure:
USE THIS EXACT STRUCTURE. Only fill empty fields. Keep all existing keys and formatting.

{json.dumps(final_data, indent=2)}

Output Instructions:
  - Replace ALL generic NPC IDs (npc1/npc2/npc3) with fantasy names
  - Ensure ALL scrolls reference EXISTING NPCs by exact name
  - Verify ALL tasks are language-focused

Output ONLY the completed JSON WRAPPED in ```json``` markers. I use (re.search(r'```json\s*({{.*?}})\s*```', validation_response, re.DOTALL)).
"""

    try:
        response = model.generate_content(prompt)
        if response.text:
            json_match = re.search(r'```json\s*({.*?})\s*```', response.text, re.DOTALL)
            if json_match:
                dungeon_data = json.loads(json_match.group(1))
                dungeon_data = add_random_id_to_json(dungeon_data)

                # Save to file
                with open("./data/dungeon_of_lingua.json", "w", encoding="utf-8") as f:
                    json.dump(dungeon_data, f, indent=4, ensure_ascii=False)

                return dungeon_data
        return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None
