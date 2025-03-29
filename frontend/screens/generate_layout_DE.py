import google.generativeai as genai
import json
import re
from screens.generate_maze import generate_maze, convert_to_json, add_npcs_to_json,\
    add_puzzles_and_treasures, add_guardians, package_dungeon
from screens.simulate_session import add_random_id_to_json

def generate_and_validate_dungeon_DE(language_focus, difficulty_level, api_key_gemini_layout):
    genai.configure(api_key=api_key_gemini_layout)
    generation_config = genai.GenerationConfig(
        temperature=0.7,
        max_output_tokens=8192
    )
    model = genai.GenerativeModel('gemini-2.0-flash', generation_config=generation_config)
    print("????????")

    maze = generate_maze(difficulty_level)
    json_data = convert_to_json(maze)
    json_data = add_npcs_to_json(json_data)
    json_data = add_puzzles_and_treasures(json_data)
    json_data = add_guardians(json_data)
    final_data = package_dungeon(json_data, difficulty_level)

    with open("./data/final_dungeon.json", 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=4, ensure_ascii=False)

    prompt = f"""Sie sind ein Dungeon-Architekt für ein Deutschlern-RPG namens "Dungeon of Lingua". 
    Ihre Aufgabe ist es, alle leeren Felder in der bereitgestellten Dungeon-JSON-Struktur mit deutschen Inhalten zu füllen, wobei Sie strikte Konsistenz mit Spielmechaniken und thematischen Anforderungen wahren.

    Der Spieler hat folgendes Lernziel ausgewählt: {language_focus}.
    Dieser Fokus sollte in Rätseln, NPC-Dialogen und Schätzen integriert werden, aber das Dungeon sollte nicht vollständig darauf ausgerichtet sein.

    ### Kritische Anforderungen:
    1. **NPC-System**:
       - Ersetzen Sie ALLE generischen NPC-IDs (npc1, npc2, npc3) durch einzigartige Fantasienamen

       **GUARDIAN-TYPE NPCs** (Sprachwächter):
       - Stellen AUSSCHLIESSLICH vokabelbasierte Herausforderungen:
         • Wortdefinitionen ("Was bedeutet 'Zaubertrank'?")
         • Übersetzungen ("Wie sagt man 'Schwert' auf Englisch?")
         • Kontextuelle Verwendung ("Verwende 'Zauberspruch' in einem Satz")

       **CONVERSATIONAL-TYPE NPCs**:
         - 5-10 einfache Fantasiewörter (["Zaubertrank", "Schriftrolle", "Dolch"])
         - Klare visuelle Hinweise auf diese Wörter
         - Beispiel: 
           - Name: "Alchimist Bram" 
           - Appearance: "Gnom mit blubbernden Fläschchen und kräuterverschmierten Fingern"
           - Trigger words: ["Zaubertrank", "Fläschchen", "Kraut", "Zutat", "Mischung"]

    2. **Scroll-Validierung**:
       - JEDER scroll's linked_npc MUSS sich auf einen EXISTIERENDEN conversational (!!!) NPC mit exaktem Namen beziehen
       - Scroll-Wörter MÜSSEN exakte Übereinstimmungen mit den Trigger-Wörtern des NPCs sein
       - Beispiel einer gültigen Verbindung:
         ```json
         {{
    "linked_npc": "Alchimist Bram",  // Muss genau mit NPC-Namen übereinstimmen
           "words": ["Zaubertrank", "Kraut"] // Muss aus Brams Trigger-Wörtern stammen
         }}
         ```

    3. **Strikte Aufgabenanforderungen**:
       ALLE Herausforderungen dürfen NUR testen:
       - Vokabelverwendung in Fantasiekontexten
       KEINE abstrakten/nicht-sprachlichen Aufgaben erlaubt (!!!)

    4. **Validierungsregeln**:
       - JEDES Rätsel muss Sprachverständnis testen
       - KEINE abstrakten/logischen Rätsel erlaubt
       - ALLE Antworten müssen objektiv überprüfbar sein

    5. **Herausforderungsdesign nach Level**:
       - **A (Anfänger)**:
         *Vokabeln*: Grundlegende Gegenstände (["Schwert", "Zauber", "Gold"])
         *Aufgaben*:
           - "Nenne 3 Gegenstände: [Dolch, ___, ___]"
           - "Vervollständige: Der Krieger ___ (tragen) ein Schwert"

       - **B (Mittelstufe)**:
         *Vokabeln*: Abenteuerbegriffe (["Proviant", "Fackel"])
         *Aufgaben*:
           - "Korrigiere: 'Wir braucht zehn Fackeln'"
           - "Verwende 'Heiltrank' in einem Satz"

       - **C (Fortgeschritten)**:
         *Vokabeln*: Magische Begriffe (["Zauberbuch", "Beschwörungsformel"])
         *Aufgaben*:
           - "Umschreibe: 'Ich studiere das Buch' (Präteritum)"
           - "Erkläre 'verzaubert' in: 'Das ___ Schwert leuchtet'"

    6. **Scroll-Vorlage**:
    ```json
    {{
    "type": "scroll",
      "words": [
        {{
    "word": "Zaubertrank",
          "translation": "potion",
          "usage_examples": [
            "Der Heiltrank stellt 10 Lebenspunkte wieder her",
            "Dieser Trank riecht nach faulen Eiern"
          ]
        }},
        {{
    "word": "Kraut",
          "translation": "herb",
          "usage_examples": [
            "Magische Kräuter wachsen in mondbeschienenen Höhlen",
            "Die Blätter des Krauts schimmern blau"
          ]
        }}
      ],
      "description": "Ein beflecktes Pergament mit Kräuterdiagrammen",
      "is_final_goal": false,
      "linked_npc": "Alchimist Bram"  // MUSS mit existierendem NPC übereinstimmen
    }}

       - JEDER CONVERSATIONAL-TYPE NPC muss GENAU EINEN zugeordneten treasure scroll haben
       - KEIN NPC sollte mehrere Scrolls besitzen
       - KEIN Scroll sollte ohne verknüpften NPC existieren

    ### JSON-Struktur:
    VERWENDEN SIE DIESE EXAKTE STRUKTUR. Füllen Sie nur leere Felder aus. Behalten Sie alle vorhandenen Schlüssel und die Formatierung bei.

    {json.dumps(final_data, indent=2)}

    Output-Anweisungen:
      - Ersetzen Sie ALLE generischen NPC-IDs (npc1/npc2/npc3 ...) durch Fantasienamen
      - Stellen Sie sicher, dass ALLE Scrolls:
         * Sich auf GENAU EINEN EXISTIERENDEN conversational NPC mit exaktem Namen beziehen
         * Das strikte 1:1 NPC-zu-Scroll-Verhältnis einhalten
      - Überprüfen Sie, dass ALLE Aufgaben sprachfokussiert sind (KEINE Logik)
      - GUARDIANs testen Vokabeln, PUZZLEs testen Grammatik
      - Verwenden Sie ausschließlich deutsche Inhalte und Beispiele

    Geben Sie NUR das vollständige JSON aus, das in ```json```-Markierungen verpackt ist. Ich verwende (re.search(r'```json\s*({{.*?}})\s*```', validation_response, re.DOTALL)).
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

