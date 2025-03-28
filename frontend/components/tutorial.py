import streamlit as st


def show_tutorial(difficulty_level="B"):
    """Отображает обучающее сообщение с анимацией и центрированием"""
    # CSS_TUTORIAL = None
    st.markdown(CSS_TUTORIAL, unsafe_allow_html=True)

    def get_localized_tutorial(level: str, lang: str) -> dict:
        localized_content = {
            "en": {
                "A": {
                    "header": "* Hark, Traveler! *",
                    "text": "Thou art trapped in the endless language maze! Heed these survival rules:",
                    "items": [
                        "Puzzles feed thy mind - solve or become supper!",
                        "Fear not the Guardian - others are worse...",
                        "Rooms bite back! Ponder twice, step once."
                    ],
                    "footer": "Keep thy wits sharp!"
                },
                "B": {
                    "header": "* List well, Stranger! *",
                    "text": "The Eternal Lingua Labyrinth claims thee! Mark these truths:",
                    "items": [
                        "Solve riddles or become spectral stew!",
                        "Guardian means well (dungeon standards)",
                        "Trust not innocent-looking rooms"
                    ],
                    "footer": "May thy quill be mighty!"
                },
                "C": {
                    "header": "* Attend, Wayfarer! *",
                    "text": "The arcane paradox ensnares thee! Observe these edicts:",
                    "items": [
                        "Conundrums sustain intellect and flesh",
                        "Guardian's wrath pales beside others",
                        "Chambers shift - choose wisely"
                    ],
                    "footer": "Persevere, lest become a footnote!"
                }
            },
            "de": {
                "A": {
                    "header": "* Hört, Wanderer! *",
                    "text": "Euch verschlingt das ewige Sprachlabyrinth! Beherzigt diese Regeln:",
                    "items": [
                        "Rätsel nähren Geist - löst sie oder werdet Mahlzeit!",
                        "Der Wächter ist harmlos (nach Kerker-Maßstab)",
                        "Gemächer beißen! Erst grübeln, dann schreiten."
                    ],
                    "footer": "Schärfet Euren Verstand!"
                },
                "B": {
                    "header": "* Merket, Fremdling! *",
                    "text": "Das Arkan-Lingua-Gefängnis umschlingt Euch! Beachtet:",
                    "items": [
                        "Rätzel lösen oder Geistersuppe werden!",
                        "Der Wächter meint's gut (Kerker-Standard)",
                        "Traut keinem harmlosen Gemach"
                    ],
                    "footer": "Eure Feder sei gewaltig!"
                },
                "C": {
                    "header": "* Achtet, Pfadsucher! *",
                    "text": "Der Zauberkerker fesselt Euch! Beherzigt:",
                    "items": [
                        "Rätsel stärken Geist und Leib",
                        "Des Wächters Zorn ist Lämmerlaut",
                        "Kammern wandeln - wählet weise"
                    ],
                    "footer": "Harrt aus, sonst Archivstaub!"
                }
            }

        }
        return localized_content[lang][level]

    lang = st.session_state.get("selected_language", "en")
    level = get_localized_tutorial(difficulty_level, lang)

    html = f"""
    <div class="tutorial-box {'tutorial-box-A' if difficulty_level == 'A' else ''}">
        <h3 class="tutorial-header">{level['header']}</h3>
        <p class="tutorial-text">{level['text']}</p>
        <ol class="tutorial-list">
            {''.join(f'<li>{item}</li>' for item in level['items'])}
        </ol>
        <p class="tutorial-footer">{level['footer']}</p>
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)

CSS_TUTORIAL = """
        <style>
            @keyframes title-float {
                0% { transform: translateY(0px); }
                50% { transform: translateY(-5px); }
                100% { transform: translateY(0px); }
            }

            .tutorial-box {
                border: 3px solid #FFD700;
                background: #000;
                margin: 1rem auto;
                padding: 1.5rem;
                max-width: 600px;
                text-align: center;
            }
            .tutorial-box-A {
                padding: 2rem !important;
                margin: 2rem auto !important;
            }
            /* Уменьшаем шрифт только для уровня A */
            .tutorial-box-A .tutorial-text,
            .tutorial-box-A .tutorial-list {
                font-size: 0.6rem;
            }
            .tutorial-header {
                color: #FF0000;
                text-shadow: 2px 2px #8B0000;
                margin: 0 0 1rem 0;
                font-size: 1rem !important;
                line-height: 1.4 !important;
                animation: title-float 3s ease-in-out infinite;
            }
            .tutorial-text {
                font-size: 0.7rem !important;
                line-height: 1.7 !important;
                margin: 0.7rem 0;
                text-align: center;
            }
            .tutorial-list {
                display: inline-block;
                text-align: left;
                margin: 0 auto;
                padding: 0;
                font-size: 0.7rem !important;
                line-height: 1.7 !important;
            }
            .tutorial-footer {
                margin: 1rem 0 0 0;
                color: #FFD700;
                font-size: 0.8rem !important;
            }
            .tutorial-list li {
                margin: 0.4rem 0;
            }
        </style>
        """