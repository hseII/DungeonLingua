import streamlit as st


# def check_npc_condition(current_room):
#     if 'npcs' not in current_room:
#         return True
#
#     for npc in current_room['npcs']:
#         if not st.session_state.get(f"npc_{npc['name']}_completed", False):
#             return False
#     return True

def check_puzzle_condition(condition: str) -> bool:
    """Checks conditions related to puzzle solutions"""
    if "Solve the '" in condition and "'" in condition:
        puzzle_name = condition.split("'")[1]
        return puzzle_name in st.session_state.get('solved_puzzles', [])
    return True  # Condition doesn't require puzzle solution


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

        with st.expander("Reveal the Challenge"):
            st.markdown(f"**{puzzle['description']}**")

            # Answer input with medieval flair
            answer = st.text_input("Enter thy answer:", key=f"puzzle_{puzzle['type']}")

            # Verification button
            if st.button("Test Thy Wit", key=f"check_{puzzle['type']}"):
                if answer.strip().lower() == puzzle['solution'].lower():
                    st.success("Correct! The stars align!")

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
                                    st.success(f"Word added to thy lexicon: {word}")

                    st.rerun()
                else:
                    st.error("Nay! Try once more, traveler.")