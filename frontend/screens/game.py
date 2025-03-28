import streamlit as st
from data_handler.json_handler import find_room_by_id
from components.dungeon_map import show_dungeon_map
from components.puzzles import check_puzzle_condition, render_puzzles
from components.inventory import render_word_dictionary
from screens.npc import render_npc_page
from components.tutorial import show_tutorial
import subprocess
from screens.npc import reset_npc_states



# Добавить новую функцию для рендера сокровищ
def render_treasures(current_room):
    """Рендерит сокровища комнаты"""
    if not current_room.get('treasures'):
        return

    st.markdown("---")
    st.markdown("### Discovered Treasures")

    @st.dialog("Artifact Found!", width="large")
    def show_artifact_dialog():
        st.markdown("Congratulations! You've found the artifact that allows you to escape the dungeon.")
        if st.button("Go to review"):
            st.session_state.current_screen = "report"
            st.rerun()

    for treasure in current_room['treasures']:
        if treasure.get('is_final_goal') and treasure['type'] == "artifact":
            btn_key = f"artifact_{treasure['name'].lower().replace(' ', '_')}"

            # Создаем кнопку с явным ключом
            if st.button(f" {treasure['name']}", key=btn_key):
                show_artifact_dialog()

def handle_room_transition(target_room_id, dungeon_data):
    """Обрабатывает переход между комнатами"""
    target_room = find_room_by_id(dungeon_data, target_room_id)

    if target_room["room_type"] != "trap":
        if target_room_id not in st.session_state.visited_rooms:
            st.session_state.visited_rooms.append(target_room_id)
    st.session_state.current_room_id = target_room_id
    if 'current_npc' in st.session_state:
        reset_npc_states(st.session_state.current_npc)
    st.session_state.target_room_id = None
    st.rerun()


def render_unlocked_doors(current_room_id, dungeon_data):
    """Рендерит разблокированные двери через NPC"""
    unlocked_doors = st.session_state.unlocked_doors.get(current_room_id, [])

    if unlocked_doors:
        st.markdown("---")
        st.markdown("### Unlocked Paths")
        cols = st.columns(len(unlocked_doors))

        for idx, room_id in enumerate(unlocked_doors):
            target_room = find_room_by_id(dungeon_data, room_id)
            with cols[idx]:
                if st.button(f" {target_room['name']}", key=f"npc_door_{room_id}"):
                    handle_room_transition(room_id, dungeon_data)
                    del st.session_state.unlocked_doors[current_room_id]  # Очищаем после перехода
                    st.rerun()
    return unlocked_doors


def render_room_exits(current_room, dungeon_data):
    """Рендерит выходы из текущей комнаты"""
    exits = current_room.get('exits', [])
    if not exits:
        return

    st.markdown("---")
    if current_room.get('npcs'):
        st.markdown("**A dungeon dweller will show you the way.**", unsafe_allow_html=True)
    else:
        cols = st.columns(len(exits))
        for idx, (col, exit_data) in enumerate(zip(cols, exits)):
            with col:
                target_room_id = exit_data['target_room']
                target_room = find_room_by_id(dungeon_data, target_room_id)
                exit_condition = exit_data.get('unlock_condition', '')
                puzzle_met = check_puzzle_condition(exit_condition)

                is_visited = target_room_id in st.session_state.visited_rooms

                if puzzle_met or is_visited:
                    col.markdown("<div class='exit-button-container'>", unsafe_allow_html=True)
                    if col.button(target_room['name'], key=f"exit_{idx}"):
                        handle_room_transition(target_room_id, dungeon_data)
                    col.markdown("</div>", unsafe_allow_html=True)
                else:
                    col.markdown(f"""
                        <div style='
                            border: 3px solid #4B0082;
                            width: 100px;
                            height: 100px;
                            margin: 0 auto;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                        '>
                            <span style="color: #4B0082; font-size: 1.2rem;">???</span>
                        </div>
                        """, unsafe_allow_html=True)


def render_trap_room(current_room):
    """Рендерит комнату-ловушку"""
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    st.markdown(f"### {current_room['name']}")
    st.markdown(f"*{current_room['description']}*")
    st.error(current_room.get("death_description", "Вы попали в смертельную ловушку!"))
    if st.button("Scribe's Scroll", key="to_report"):
        st.session_state.current_screen = "report"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


def render_normal_room(current_room, dungeon_data):
    """Рендерит обычную комнату"""
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    render_puzzles(current_room)
    render_treasures(current_room)

    # Рендерим разблокированные двери
    render_unlocked_doors(st.session_state.current_room_id, dungeon_data)

    # Рендерим выходы из комнаты
    render_room_exits(current_room, dungeon_data)

    st.markdown('</div>', unsafe_allow_html=True)

    # Блок описания комнаты
    st.markdown(f'''
        <div class="room-info">
            <div class="room-title">{current_room['name']}</div>
            <div class="room-description">{current_room['description']}</div>
        </div>
        ''', unsafe_allow_html=True)


def render_header(current_room):
    """Рендерит верхнюю панель с кнопками"""
    header_cols = st.columns([0.1, 0.7, 0.2])
    with header_cols[0]:
        if st.button("◄", help="Главное меню", key="main_menu"):
            st.session_state.clear()
            st.session_state.current_screen = "welcome"
            st.rerun()

    # NPC аватары
    with header_cols[2]:
        if current_room.get('npcs'):
            npc_cols = st.columns(len(current_room['npcs']))
            for idx, npc in enumerate(current_room['npcs']):
                with st.container():
                    if st.button(f"Chatter Mead", key=f"npc_{npc['name']}"):
                        st.session_state.selected_npc = npc
                        st.session_state.current_screen = "npc"
                        st.rerun()


def initialize_session_state():
    """Инициализирует необходимые переменные в session_state"""
    defaults = {
        'solved_puzzles': [],
        'selected_npc': None,
        'word_dictionary': {},
        'npc_dialog_started': False,
        'npc_dialog_completed': False,
        'npc_chat_history': [],
        'npc_patience': 3,
        'show_artifact_dialog': False
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def check_ffmpeg():
    """Проверяет наличие FFmpeg"""
    if 'ffmpeg_checked' not in st.session_state:
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
            st.session_state.ffmpeg_checked = True
        except Exception as e:
            st.error("Требуется FFmpeg! Инструкции в README.md")
            st.stop()


def render():
    st.markdown("""
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

            * {
                font-family: 'Press Start 2P', cursive !important;
                image-rendering: pixelated;
                color: #FFFFFF !important;
                background-color: #000000 !important;
            }

            .stApp, .main-content, .stSidebar, .stAlert, .stButton>button {
                background-color: #000000 !important;
            }

            .room-info {
                position: relative;
                margin-top: 1rem;
                padding: 1.5rem;
                border-top: 3px solid #FFD700;
            }

            .room-title {
                font-size: 1rem !important;
                text-align: left;
                margin-bottom: 0.5rem !important;
                line-height: 1.4 !important;
            }

            .room-description {
                font-size: 0.7rem !important;
                line-height: 1.7 !important;
                border: 2px solid #FFD700;
                padding: 1rem;
                text-align: left;
                min-height: 80px;
            }

            .main-content {
                margin-bottom: 100px !important;
            }

            [data-testid="stSidebar"] {
                border-right: 2px solid #FFFFFF !important;
            }

            .stMarkdown {
                max-width: 800px !important;
                margin: 0 auto !important;
            }

            /* Основные стили для всех кнопок */
            .stButton > button {
                all: unset !important;
                width: 100% !important;
                min-width: 240px !important;
                height: 60px !important;
                margin: 10px 0 !important;
                display: flex !important;
                align-items: center;
                justify-content: center;
                border: 3px solid #FF0000 !important;
                color: #FF0000 !important;
                font-family: 'Press Start 2P', cursive !important;
                font-size: 0.8rem !important;
                text-align: center !important;
                cursor: pointer;
                position: relative;
                transition: all 0.3s !important;
            }

            /* Контейнер для текста внутри кнопок */
            .stButton > button > div {
                width: 100% !important;
                height: 100% !important;
                display: flex !important;
                align-items: center;
                justify-content: center;
                padding: 0 5px !important;
            }

            /* Стили для текста внутри кнопок */
            .stButton > button > div > * {
                margin: 0 !important;
                padding: 0 !important;
                width: 100% !important;
                text-align: center !important;
                display: flex !important;
                align-items: center;
                justify-content: center;
                line-height: 1.2 !important;
            }

            /* Анимации для обычных кнопок */
            .stButton > button:not(:disabled) {
                animation: shake 0.8s infinite !important;
            }

            /* Стили для NPC кнопок */
            .stButton > button[id^="npc_"] {
                border-color: #32CD32 !important;
                color: #32CD32 !important;
                animation: none !important;
            }

            .stButton > button[id^="npc_"]:hover {
                box-shadow: 0 0 15px #32CD32 !important;
            }

            /* Стили для кнопки Report */
            .stButton > button#to_report {
                border-color: #FFD700 !important;
                color: #FFD700 !important;
                animation: glow 2s infinite !important;
            }

            /* Стили для кнопок перехода */
            .stButton > button[id^="exit_"] {
                min-width: 100px !important;
                height: 100px !important;
            }

            /* Отключенные кнопки */
            .stButton > button:disabled {
                border-color: #4B0082 !important;
                color: #4B0082 !important;
                opacity: 0.7 !important;
                animation: none !important;
            }

            /* Ховер-эффекты */
            .stButton > button:not(:disabled):hover {
                animation-play-state: paused !important;
                transform: scale(1.05) !important;
                box-shadow: 0 0 15px #FFD700 !important;
            }

            /* Адаптация для мобильных устройств */
            @media (max-width: 768px) {
                .stButton > button {
                    min-width: 180px !important;
                    height: 50px !important;
                    font-size: 0.7rem !important;
                }

                .stButton > button[id^="exit_"] {
                    min-width: 80px !important;
                    height: 80px !important;
                }
            }

            /* Анимация тряски */
            @keyframes shake {
                0% { transform: translate(0, 0); }
                25% { transform: translate(-1px, 1px); }
                50% { transform: translate(1px, -1px); }
                75% { transform: translate(-1px, -1px); }
                100% { transform: translate(0, 0); }
            }

            /* Анимация свечения */
            @keyframes glow {
                0% { opacity: 0.9; }
                50% { opacity: 0.6; }
                100% { opacity: 0.9; }
            }

            .empty-room-message {
                text-align: center;
                font-size: 0.8rem !important;
                margin: 2rem 0;
                color: #FFD700;
            }

            .exit-button-container {
                width: 100% !important;
                padding: 10px 0 !important;
                margin: 0 auto !important;
                text-align: center !important;
            }

            button[data-testid="baseButton-secondary"] {
                width: 100% !important;
                max-width: 300px !important;
            }
            </style>
            """, unsafe_allow_html=True)

    if 'unlocked_doors' not in st.session_state:
        st.session_state.unlocked_doors = {}

    check_ffmpeg()

    if not st.session_state.get('dungeon_data') or not st.session_state.get('current_room_id'):
        st.error("Ошибка загрузки данных!")
        st.session_state.current_screen = "welcome"
        st.rerun()
        return

    current_room = find_room_by_id(st.session_state.dungeon_data, st.session_state.current_room_id)
    st.session_state.current_room = current_room

    # Сброс NPC при переходе
    if not current_room.get('npcs'):
        st.session_state.selected_npc = None

    # Хедер
    render_header(current_room)

    if current_room.get("is_start") and not st.session_state.get("tutorial_shown"):
        difficulty = st.session_state.player_preferences.get("difficulty_level", "B")
        show_tutorial(difficulty)
        st.session_state.tutorial_shown = True

    initialize_session_state()

    if st.session_state.current_screen == "npc" and st.session_state.selected_npc:
        render_npc_page(st.session_state.selected_npc, current_room)
    else:
        if current_room["room_type"] == "trap":
            render_trap_room(current_room)
        else:
            render_normal_room(current_room, st.session_state.dungeon_data)

    with st.sidebar:
        show_dungeon_map()
        render_word_dictionary()