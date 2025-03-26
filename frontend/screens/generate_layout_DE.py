import google.generativeai as genai
import json
import re
from secrets import *


def generate_and_validate_dungeon_DE(language_focus, difficulty_level, api_key_gemini_layout):
    """
        Генерация и валидация подземелья для RPG "Dungeon of Lingua" на немецком языке.

        Вход:
        - language_focus: выбранный язык для изучения (немецкий).
        - difficulty_level: уровень сложности (A, B, C).
        - api_key_gemini_layout: API-ключ для Gemini.

        Выход:
        - JSON с описанием подземелья, включая комнаты, NPC, сокровища и головоломки.
        - В случае успеха возвращает JSON, иначе None.

        Процесс:
        1. Генерация подземелья через запрос к Gemini API на немецком языке.
        2. Валидация и улучшение структуры подземелья.
        3. Сохранение результата в JSON-файл.
    """
    # Настройка API-ключа Gemini
    genai.configure(api_key=api_key_gemini_layout)

    # Инициализация модели Gemini
    model = genai.GenerativeModel('gemini-2.0-flash')  # Используем модель Gemini Flash

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

    # Промт для генерации подземелья на немецком языке
    prompt = f"""
    Sie sind ein Dungeon-Architekt für ein Sprachlern-RPG namens "Dungeon of Lingua." 
    Entwerfen Sie ein Dungeon mit 12+ Räumen (!!!), das sich auf den Erwerb von Vokabeln, Sprachrätsel und nicht-linearen Fortschritt konzentriert. 
    Das Dungeon sollte die Spieler in eine dunkle, mysteriöse Atmosphäre eintauchen und sie dazu anregen, neue Wörter zu verwenden und zu lernen. 
    Das Dungeon sollte sich an die Sprachpräferenzen der Spieler anpassen und Vokabelthemen in Rätsel, Dialoge und Schätze integrieren.

    ### Anweisungen:
    1. **Denkphase**: 
       - Denken Sie zuerst über das Dungeon-Layout, die Verbindungen zwischen den Räumen und den logischen Ablauf nach. 
       - Überlegen Sie, wie der Spieler durch das Dungeon fortschreitet, einschließlich Rätsel, NPCs und Schätze. 
       - Planen Sie verzweigte Pfade (Gabelungen), um nicht-linearen Fortschritt zu ermöglichen.
       - Validieren Sie die logische Konsistenz des Dungeons:
         - Stellen Sie sicher, dass alle Räume über Ausgänge verbunden sind.
         - Überprüfen Sie, ob die Wörter auf den Schriftrollen in den Schätzen mit den trigger_words der NPCs übereinstimmen.
         - Bestätigen Sie, dass die Rätsel dem Schwierigkeitsgrad {difficulty_level} entsprechen.
         - Stellen Sie sicher, dass das finale Ziel (Schatz) erreichbar ist.

    2. **Ausgabephase**: 
       - Schreiben Sie nach der Validierung eine kurze Zusammenfassung (2-3 Sätze), die erklärt, wie das Dungeon diese Anforderungen erfüllt.
       - Geben Sie das endgültige Design im JSON-Format aus, umschlossen von ```json``` Markern.

    ### Anforderungen:
    1. **Spielerpräferenzen**:
       - Der Spieler hat den folgenden Sprachfokus gewählt: {language_focus}.
       - Der gewählte Fokus sollte in Rätsel, NPC-Dialoge und Schätze integriert werden, aber das Dungeon sollte nicht ausschließlich darauf ausgerichtet sein.
       - Schwierigkeitsgrad: {difficulty_level}. Dies bestimmt die Komplexität der verwendeten Vokabeln:
         - A (Anfänger): A1-A2 CEFR-Niveau. Einfache Vokabeln (z. B. Alltagsgegenstände, einfache Verben).
         - B (Mittelstufe): B1-B2 CEFR-Niveau. Mittelschwere Vokabeln (z. B. thematische Wörter, Phrasalverben).
         - C (Fortgeschritten): C1-C2 CEFR-Niveau. Fortgeschrittene Vokabeln (z. B. Redewendungen, akademische Begriffe).

    2. **Räume**:
       - Das Dungeon muss 12+ Räume (!!!) haben.
       - Jeder Raum muss einen eindeutigen Namen, eine lebendige Beschreibung und logische Ausgänge haben.
       - Fügen Sie **mindestens 3+ Fallenräume** FÜR JEDE GABELUNG hinzu, deren Namen nicht sofort auf Gefahr hinweisen (z. B. "Stille Nische", "Halle der Flüsterer", "Archiv der Halbwahrheiten").
       - Fallenräume DÜRFEN KEINE Inhalte haben (keine NPCs, Rätsel oder Schätze). Sie müssen NUR ein `description`-Feld haben.
       - Balancieren Sie NPCs, Rätsel und Schätze in normalen Räumen (nicht jeder Raum muss alle drei haben).
       - Fügen Sie verzweigte Pfade (Gabelungen) hinzu, um nicht-linearen Fortschritt zu ermöglichen.
       - Jeder Raum muss ein `room_type`-Feld haben, das angibt, ob es sich um einen normalen Raum oder einen Fallenraum handelt.

    3. **NPCs**:
       - Fügen Sie **Gesprächs-NPCs** vor JEDER GABELUNG hinzu.
       - Jeder NPC muss haben:
         - Name, Aussehen und Typ (entweder `guardian` oder `conversational`).
         - Motivation/Geheimnis, das mit Sprache verbunden ist (z. B. "Möchte alte Dialekte lehren").
         - Verhalten (neutral/freundlich für Gesprächs-NPCs, neutral für Wächter).
       - Für **Gesprächs-NPCs**:
         - `trigger_words`: Eine Liste von 5-10 Wörtern, die ihr Verhalten beeinflussen.
         - `patience`: Anzahl der Versuche, bevor der Spieler in die Irre geführt wird (5-10).
         - `information_to_share`: Der Name des richtigen Raums, um fortzufahren.
         - `trap_rooms`: Eine Liste von Fallenraum-Namen, um den Spieler in die Irre zu führen, wenn die Geduld erschöpft ist.
       - Für **Wächter-NPCs**:
         - `challenge`: Eine sprachbasierte Herausforderung, die der Spieler bestehen muss, um weiterzukommen. Beispiele:
           - Verwenden Sie einen Satz in einer bestimmten grammatikalischen Form.
           - Verwenden Sie ein Wort (oder Wörter) aus einem bestimmten lexikalischen Thema.
           - Erraten Sie ein Wort basierend auf seiner Beschreibung.
         - Fügen Sie KEIN `information_to_share` für Wächter hinzu.

    4. **Schätze**:
       - Schätze können NUR durch das Lösen von Rätseln erhalten werden.
       - Schätze gibt es in zwei Arten:
         A. Vokabel-Schriftrolle:
           {{
             "type": "scroll",
             "words": [
               {{
                 "word": "[Englisches Wort 1]",
                 "translation": "[Übersetzung 1 (DE)]",
                 "usage_examples": ["Beispiel1", "Beispiel2"]  # Beispiele sollten zu einem Fantasy-Thema passen
               }},
               {{
                 "word": "[Englisches Wort 2]",
                 "translation": "[Übersetzung 2 (DE)]",
                 "usage_examples": ["Beispiel1", "Beispiel2"]
               }}
             ],
             "description": "[Physische Beschreibung der Schriftrolle]",
             "is_final_goal": false,
             "linked_npc": "[Name des NPCs, dessen trigger_words diese Wörter enthalten]"
           }}
         B. Finaler Zielschatz:
           {{
             "type": "artefact",
             "name": "[Artefaktname]",
             "description": "[Lore-reiche Beschreibung des Artefakts]",
             "is_final_goal": true
           }}

    5. **Rätsel**:
       - Vokabelthematisch, aber intuitiv (z. B. "Ordnen Sie fragmentierte Wörter neu an, um einen sinnvollen Satz zu bilden").
       - Rätsel sollten die Spieler dazu anregen, kreativ zu lesen und zu decodieren.
       - Fügen Sie mindestens ein Rätsel hinzu, das den gewählten Sprachfokus des Spielers ({language_focus}) erfordert.
       - Beispiele:
         - Identifizieren Sie korrekte Aussagen basierend auf einem Textfragment.
         - Erraten Sie die Bedeutung von archaischen oder buchstäblichen Wörtern (geben Sie ein modernes Synonym an).
         - Ordnen Sie Wortfragmente neu an, um einen vollständigen Satz zu bilden.
         - Füllen Sie die richtigen Präpositionen des Ortes oder der Zeit ein.
       - Für Schwierigkeitsgrad B oder C sollten die Rätsel mäßig herausfordernd sein:
         - Verwenden Sie Phrasalverben oder thematische Vokabeln.

    6. **Logische Struktur**:
       - Jedes Rätsel, jeder Schatz und jeder NPC sollte einen klaren Zweck im Dungeon haben.
       - Fügen Sie verzweigte Pfade (Gabelungen) hinzu, um nicht-linearen Fortschritt zu ermöglichen.

    7. **Atmosphäre**:
       - Dunkel, mysteriös und gefährlich. Fügen Sie Umweltdetails hinzu (z. B. "Echos vergessener Gesänge schweben in der Luft").
       - Verwenden Sie sprachbezogene Beschreibungen (z. B. "Wände, die mit leuchtenden Runen bedeckt sind, die sich verschieben, wenn man sie anstarrt").

    ### Ausgabeformat:
    Schreiben Sie zuerst eine Zusammenfassung:
    - Validieren Sie die logische Konsistenz des Dungeons.
    - Erklären Sie, wie das Dungeon die Anforderungen erfüllt.

    Geben Sie dann das JSON aus, umschlossen von ```json``` Markern.
    """

    # Отправка первого запроса для генерации подземелья
    response_text = send_prompt_to_gemini(prompt)
    if response_text:
        print("Ответ от Gemini API (генерация подземелья):")
        print(response_text)

        # Извлечение JSON из ответа
        try:
            json_match = re.search(r'```json\s*({.*?})\s*```', response_text, re.DOTALL)
            if json_match:
                response_json = json.loads(json_match.group(1))

                # Сохранение в файл
                with open("dungeon_of_lingua.json", "w", encoding="utf-8") as f:
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
        with open("dungeon_of_lingua.json", "r", encoding="utf-8") as f:
            dungeon_data = json.load(f)
    except FileNotFoundError:
        print("Ошибка: Файл 'dungeon_of_lingua.json' не найден. Пожалуйста, сгенерируйте подземелье сначала.")
        return None

    prompt_check = f"""
    Sie sind ein Dungeon-Architekt für ein Sprachlern-RPG namens "Dungeon of Lingua." 
    Ihre Aufgabe ist es, die bereitgestellten Dungeon-JSON-Daten zu validieren und zu verbessern. 
    Stellen Sie sicher, dass das Dungeon alle strukturellen und logischen Anforderungen erfüllt.

    ### Dungeon-Daten:
    ```json
    {json.dumps(dungeon_data, indent=4)}
    Anweisungen:
    Dungeon-Struktur:
    - Das Dungeon sollte Gabelungen haben: Ein Raum in jeder Gabelung ist der richtige Pfad.
    - VOR JEDER GABELUNG muss ein Gesprächs-NPC stehen.
    - Jeder Gesprächs-NPC muss ein Rätsel mit einem Schatz FRÜHER (!!!) im Dungeon haben, das seine trigger_words enthüllt.
    - Räume dürfen NICHT LEER sein!!! FÜGEN SIE MEHR WÄCHTER HINZU.
    Logikprüfung:
    - Stellen Sie sicher, dass alle Räume über Ausgänge verbunden sind.
    - Überprüfen Sie, ob die Wörter in den Schätzen (scroll.words) mit den trigger_words der NPCs übereinstimmen.
    - Stellen Sie sicher, dass jede Gabelung mindestens 3 Räume hat (einer richtig, die anderen Fallen).
    - Überprüfen Sie, dass jeder Raum eine Beschreibung und einen Typ (room_type: normal oder trap) hat.
    Verbesserungen:
    - Wenn Unstimmigkeiten gefunden werden, beheben Sie diese und fügen Sie fehlende Elemente hinzu (z. B. Wächter, Raum-Beschreibungen, NPC trigger_words).
    - Stellen Sie sicher, dass alle NPCs vor Gabelungen verknüpfte Rätsel und Schätze haben.
    - Fügen Sie mehr Wächter hinzu, um die Herausforderung und Atmosphäre des Dungeons zu erhöhen.
    Ausgabe:
    Geben Sie nach der Validierung und Verbesserung das aktualisierte JSON im JSON-Format aus.
    Fügen Sie eine kurze Zusammenfassung der Änderungen hinzu (z. B. "3 Wächter zu Raum X hinzugefügt", "trigger_words für NPC Y korrigiert").
    Ausgabeformat:
    Schreiben Sie zuerst eine kurze Zusammenfassung der Änderungen:
    Listen Sie die am Dungeon vorgenommenen Änderungen auf.
    Geben Sie dann das aktualisierte JSON aus, umschlossen von json Markern.
    """

    # Второй запрос для валидации и улучшения
    response_text_check = send_prompt_to_gemini(prompt_check)
    if response_text_check:
        print("Ответ от Gemini API (валидация и улучшение):")
        print(response_text_check)

        # Извлечение JSON из ответа
        try:
            json_match_check = re.search(r'```json\s*({.*?})\s*```', response_text_check, re.DOTALL)
            if json_match_check:
                response_json_check = json.loads(json_match_check.group(1))

                # Сохранение в файл
                with open("dungeon_of_lingua_checked.json", "w", encoding="utf-8") as f:
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
