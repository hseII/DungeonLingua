import streamlit as st
from screens.my.character import prompt_puzzle, gemini_model
from screens.my.api_key import gemini_key


def get_localized_text(key):
    """Локализация для головоломок"""
    current_language = st.session_state.get("selected_language", "en")

    localized_texts = {
        "en": {
            "reveal_challenge": "Reveal the Challenge",
            "enter_answer": "Enter thy answer:",
            "test_wit": "Test Thy Wit",
            "correct_answer": "Correct! The stars align!",
            "wrong_answer": "Nay! Try once more, traveler.",
            "word_added": "Word added to thy lexicon: {word}"
        },
        "de": {
            "reveal_challenge": "Enthülle die Prüfung",
            "enter_answer": "Ritze Deine Antwort:",
            "test_wit": "Prüfe Deinen Scharfsinn",
            "correct_answer": "Richtig! Die Sterne fügen sich!",
            "wrong_answer": "Fehlgeschlagen! Versuch's erneut, Wanderer.",
            "word_added": "Wort dem Kodex hinzugefügt: {word}"
        }
    }
    return localized_texts[current_language].get(key, key)

def check_puzzle_condition(condition: str) -> bool:
    """Checks conditions related to puzzle solutions"""
    if "Solve the '" in condition and "'" in condition:
        puzzle_name = condition.split("'")[1]
        return puzzle_name in st.session_state.get('solved_puzzles', [])
    return True  # Condition doesn't require puzzle solution


def check_puzzle_llm(user_answer, true_answer, desc):
    full_prompt = prompt_puzzle.format(user_input=user_answer, true_answer=true_answer, desc=desc)
    response = gemini_model.generate_content(full_prompt).text
    return "yes" in response.lower() or "ERFOLG".lower() in response.lower()


def render_puzzles(current_room: dict):
    """Renders puzzle interface within the chamber"""
    puzzles = current_room.get('puzzles', [])
    for puzzle in puzzles:
        st.markdown("---")
        # Display puzzle title with medieval styling
        st.markdown(
            f"<div style='text-align: center; color: #FFD700; "
            f"text-shadow: 2px 2px #8B0000;'>{puzzle['type']}</div>",
            unsafe_allow_html=True
        )

        with st.expander(get_localized_text("reveal_challenge")):
            st.markdown(f"**{puzzle['description']}**")

            # Answer input with medieval flair
            answer = st.text_input(
                get_localized_text("enter_answer"),
                key=f"puzzle_{puzzle['type']}"
            )

            # Verification button
            if st.button(get_localized_text("test_wit"), key=f"check_{puzzle['type']}"):
                if answer.strip().lower() == puzzle['solution'].lower() or check_puzzle_llm(
                        user_answer=answer.strip().lower(), desc=puzzle['description'],
                        true_answer=puzzle['solution'].lower()):
                    st.success(get_localized_text("correct_answer"))

                    # Add to solved puzzles
                    if puzzle['type'] not in st.session_state.solved_puzzles:
                        st.session_state.solved_puzzles.append(puzzle['type'])

                    # Handle treasure words
                    treasures = current_room.get('treasures', [])
                    for treasure in treasures:
                        if 'words' in treasure:
                            for word_data in treasure['words']:
                                word = word_data['word']
                                if word not in st.session_state.get('word_dictionary', {}):
                                    if 'word_dictionary' not in st.session_state:
                                        st.session_state.word_dictionary = {}
                                    st.session_state.word_dictionary[word] = {
                                        'translation': word_data['translation'],
                                        'usage_examples': word_data['usage_examples']
                                    }
                                    st.success(
                                        get_localized_text("word_added").format(word=word))

                    st.rerun()
                else:
                    st.error(get_localized_text("wrong_answer"))