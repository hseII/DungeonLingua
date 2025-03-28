import streamlit as st
import time
from data_handler.json_handler import load_and_validate, find_room_by_id
from screens.my.api_key import api_key_gemini_layout, api_key_pixellab
from screens.generate_layout_EN import generate_and_validate_dungeon_EN
from constants import ROOT_LOG
from screens.generate_images import generate_npc_avatars
import csv
from streamlit.runtime.scriptrunner import get_script_run_ctx
import re
from streamlit import runtime
from streamlit.components.v1 import html
from streamlit.web.server.websocket_headers import _get_websocket_headers


def detect_mobile():
    headers = st.context.headers
    user_agent = headers.get("User-Agent", "").lower()

    # Список мобильных идентификаторов
    mobile_keywords = [
        'mobile', 'android', 'iphone', 'ipod',
        'windows phone', 'blackberry', 'opera mini'
    ]
    print(user_agent)
    # Проверяем User-Agent
    return any(re.search(keyword, user_agent) for keyword in mobile_keywords)
    # return False


def generate(file, language_focus, difficulty_level):
    generated_json = generate_and_validate_dungeon_EN(language_focus=language_focus,
                                                      difficulty_level=difficulty_level,
                                                      api_key_gemini_layout=api_key_gemini_layout)
    print(generated_json)
    generate_npc_avatars(json_file_path=file, api_key_pixellab=api_key_pixellab)


def render():
    st.markdown(CSS_RENDER, unsafe_allow_html=True)
    if 'is_mobile' not in st.session_state:
        st.session_state.is_mobile = detect_mobile()
    print("mobile check", st.session_state.is_mobile)
    # Основной контент
    st.markdown('<h1 class="main-title">DUNGEON OF LINGUA</h1>', unsafe_allow_html=True)
    # st.session_state.is_mobile = True

    # Блок настроек
    with st.form("player_settings"):
        st.markdown('<div class="player-settings-form">', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            # Текстовый ввод вместо выпадающего списка
            language_focus = st.text_input(
                "LANGUAGE FOCUS",
                value="",
                max_chars=20
            )
        with col2:
            difficulty_level = st.selectbox("DIFFICULTY LEVEL", options=["A", "B", "C"], index=1)

        st.markdown('<div style="margin: 2rem 0;"></div>', unsafe_allow_html=True)

        _, center_col, _ = st.columns([2, 1, 2])
        with center_col:
            st.markdown('<div style="height: 600px; width= 600px;">', unsafe_allow_html=True)
            start_button = st.form_submit_button("START QUEST")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # Обработка загрузки
    if start_button:
        loading_html = """
        <div class="loading-container">
            <div class="pixel-spinner"></div>
            <div class="loading-text">>> GENERATING DUNGEON...</div>
        </div>
        """
        st.markdown(loading_html, unsafe_allow_html=True)

        try:
            if len(language_focus) < 2:
                language_focus = "grammar"
            start = time.time()

            # file = "data/dungeon_of_lingua.json"
            file = "data/dungeon_of_lingua_checked.json"
            dungeon_data = load_and_validate(file)
            # generate(file=file, language_focus=language_focus, difficulty_level=difficulty_level)
            print("GOOD VALIDATION!!!")
            st.session_state.player_preferences = {
                "language_focus": language_focus,
                "difficulty_level": difficulty_level
            }
            end = time.time()
            print("all time:", end - start)
            start_room = find_room_by_id(dungeon_data, dungeon_data["starting_room"])

            st.session_state.update({
                "dungeon_data": dungeon_data,
                "current_screen": "game",
                "current_room_id": start_room["id"],
                "visited_rooms": [start_room["id"]],
                "is_alive": True
            })

            # Искусственная задержка для демонстрации анимации
            time.sleep(2)
            st.rerun()

        except Exception as e:
            st.error(f"ERROR: {str(e)}")


CSS_RENDER = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

    /* Основные стили */
    * {
        font-family: 'Press Start 2P', cursive !important;
        image-rendering: pixelated;
    }

    /* Центрирование основного контента */
    .stApp > div {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: flex-start !important;
        min-height: 100vh !important;
    }

    /* Стиль для контейнера настроек */
    .player-settings-form {
        width: 80% !important;
        max-width: 600px !important;
        margin: 2rem auto !important;
    }

    /* Заголовок */
    .main-title {
        font-size: 2.5rem !important;
        text-align: center;
        color: #FFD700 !important;
        text-shadow: 3px 3px #8B0000;
        margin: 2rem 0;
        animation: title-float 2s ease-in-out infinite;
    }

    /* Анимация заголовка */
    @keyframes title-float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-5px); }
        100% { transform: translateY(0px); }
    }
    
     /* Фикс для кнопки */
    .stButton > button {
    width: 100px !important;
    height: 200px !important:
    padding: 1.5rem 3rem !important;
    font-size: 1.2rem !important;
    margin: 3rem 0 !important;
    background: #4B0082 !important;
    color: #FFF !important;
    border: 3px solid #FFD700 !important;
    border-radius: 0 !important;
    box-shadow: 5px 5px 0px #8B0000 !important;
    transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
    position: relative !important;
    overflow: hidden !important;
    }
    
    .stButton > button:hover {
        transform: translate(2px, 2px) !important;
        box-shadow: 3px 3px 0px #8B0000 !important;
    }
    
    .stButton > button:active {
        transform: translate(4px, 4px) !important;
        box-shadow: 1px 1px 0px #8B0000 !important;
    }
    
    /* Стилизация выпадающих списков */
    .stSelectbox [data-testid="stSelectbox"] {
        border: 3px solid #000 !important;
        border-radius: 0 !important;
        padding: 4px !important;
        background: #fff !important;
        image-rendering: pixelated;
    }

    .stSelectbox [data-testid="stSelectbox"]>div {
        background: #fff !important;
        color: #000 !important;
    }

    /* Общий стиль для заголовков */
    .stSelectbox label, .stTextInput label {
        color: #FFD700 !important;
        text-shadow: 2px 2px #8B0000 !important;
        font-size: 0.9rem !important;
    }

    /* Стилизация текстового ввода */
    .stTextInput input {
        font-family: 'Press Start 2P', cursive !important;
        border: 3px solid #000 !important;
        border-radius: 0 !important;
        padding: 8px !important;
        background: #fff !important;
        color: #000 !important;
        image-rendering: pixelated;
        box-shadow: none !important;
    }

    /* Анимация загрузки */
    .loading-text {
        color: #FFD700 !important;
        text-shadow: 2px 2px #8B0000;
        animation: blink 1s step-end infinite;
    }

    @keyframes blink {
        50% { opacity: 0; }
    }

    /* Позиционирование индикатора загрузки */
    .loading-container {
        position: fixed !important;
        bottom: 50px !important;
        left: 0 !important;
        right: 0 !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        gap: 1rem !important;
    }

    /* Кастомный спиннер */
    .pixel-spinner {
        width: 40px !important;
        height: 40px !important;
        border: 4px solid #FFD700 !important;
        border-top-color: transparent !important;
        border-radius: 50% !important;
        animation: pixel-spin 1s linear infinite !important;
    }

    @keyframes pixel-spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    /* Фон страницы */
    .stApp {
        background: #000 !important;
    }
    </style>
    """
