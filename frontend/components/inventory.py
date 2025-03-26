import streamlit as st


def render_word_dictionary():
    """Renders the word lexicon in the sidebar"""
    with st.sidebar.expander("Lexicon", expanded=True):
        # Container styling matching the dungeon map
        st.markdown("""
        <div style="border:3px solid #8B0000; padding:10px; margin-bottom:12px;">
            <h3 style="color:#FFD700; font-family:'Press Start 2P'; 
                text-align:center; text-shadow: 1px 1px #8B0000; margin:0;">
                TOME OF WORDS
            </h3>
        </div>
        """, unsafe_allow_html=True)

        if not st.session_state.get('word_dictionary'):
            st.write("Thy lexicon stands empty, traveler.")
            return

        label_style = "color: #8B0000; text-shadow: 1px 1px 2px #8B0000;"

        for word, data in st.session_state.word_dictionary.items():
            # Стиль для основного слова
            st.markdown(
                f"<span style='{label_style}'><strong>{word}</strong></span>",
                unsafe_allow_html=True
            )

            # Стиль для "Deciphered as"
            st.markdown(
                f"<span style='{label_style}'>Deciphered as:</span> "
                f"{data['translation']}",
                unsafe_allow_html=True
            )

            # Стиль для "Ancient scrolls speak thus"
            st.markdown(
                f"<span style='{label_style}'>Ancient scrolls speak thus:</span>",
                unsafe_allow_html=True
            )

            for example in data['usage_examples']:
                st.markdown(f"<div style='margin-left:12px;'>- {example}</div>",
                            unsafe_allow_html=True)

            st.markdown("---")

        # Стиль для нижнего элемента
        st.markdown(f"""
        <div style="text-align:center; {label_style} margin-top:8px;">
            ✦ The Words of Power ✦
        </div>
        """, unsafe_allow_html=True)