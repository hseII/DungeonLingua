import streamlit as st


def get_localized_text(key):
    """Локализация для словаря"""
    current_language = st.session_state.get("selected_language", "en")

    localized_texts = {
        "en": {
            "lexicon_title": "TOME OF WORDS",
            "empty_lexicon": "Thy lexicon stands empty, traveler.",
            "deciphered_as": "Deciphered as:",
            "ancient_scrolls": "Ancient scrolls speak thus:",
            "words_of_power": "✦ The Words of Power ✦",
            "sidebar_label": "Lexicon"
        },
        "de": {
            "lexicon_title": "WORTKODEX",
            "empty_lexicon": "Euer Wörterbuch ist leer, Reisender.",
            "deciphered_as": "Entschlüsselt als:",
            "ancient_scrolls": "Alte Schriften künden:",
            "words_of_power": "✦ Die Worte der Macht ✦",
            "sidebar_label": "Wörterbuch"
        }
    }
    return localized_texts[current_language].get(key, key)


def render_word_dictionary():
    """Renders the word lexicon in the sidebar"""
    with st.sidebar.expander(get_localized_text("sidebar_label"), expanded=True):
        st.markdown(f"""
        <div style="border:3px solid #8B0000; padding:10px; margin-bottom:12px;">
            <h3 style="color:#FFD700; font-family:'Press Start 2P'; 
                text-align:center; text-shadow: 1px 1px #8B0000; margin:0;">
                {get_localized_text('lexicon_title')}
            </h3>
        </div>
        """, unsafe_allow_html=True)

        if not st.session_state.get('word_dictionary'):
            st.write(get_localized_text("empty_lexicon"))
            return

        label_style = "color: #8B0000; text-shadow: 1px 1px 2px #8B0000;"

        for word, data in st.session_state.word_dictionary.items():
            st.markdown(
                f"<span style='{label_style}'><strong>{word}</strong></span>",
                unsafe_allow_html=True
            )

            st.markdown(
                f"<span style='{label_style}'>{get_localized_text('deciphered_as')}</span> "
                f"{data['translation']}",
                unsafe_allow_html=True
            )

            st.markdown(
                f"<span style='{label_style}'>{get_localized_text('ancient_scrolls')}</span>",
                unsafe_allow_html=True
            )

            for example in data['usage_examples']:
                st.markdown(f"<div style='margin-left:12px;'>- {example}</div>",
                            unsafe_allow_html=True)

            st.markdown("---")

        st.markdown(f"""
        <div style="text-align:center; {label_style} margin-top:8px;">
            {get_localized_text('words_of_power')}
        </div>
        """, unsafe_allow_html=True)