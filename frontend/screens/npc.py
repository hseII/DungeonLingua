import streamlit as st
from constants import ROOT_LOG
from screens.my.character import Character, prompt_template_guardian, prompt_template_conv, gemini_model, whisper_model, \
    prompt_template_check_sucess, prompt_template_trap_room, prompt_template_guardian_de, prompt_template_conv_de, \
    prompt_template_check_sucess_de, prompt_template_trap_room_de
from pydub import AudioSegment
from io import BytesIO
import tempfile
import csv
import os


def get_localized_text(key):
    """Локализация текста для NPC"""
    current_language = st.session_state.get("selected_language", "en")

    localized_texts = {
        "en": {
            "speak_stranger": "Speak, Stranger",
            "record_help": "Press and hold to parley",
            "message_input": "Inscribe thy words:",
            "send_button": "Send",
            "start_dialog": "Start dialog",
            "back_to_room": "Retreat to Chamber",
            "dialog_title": "Court of Words",
            "patience_remaining": "Mercy remaining:",
            "npc_disappear": "The figure melts into shadows... No aid shall come.",
            "return_button": "Flee this Discourse",
            "npc_image_error": "Alas! The visage scroll is missing!",
        },
        "de": {
            "speak_stranger": "Sprich, Fremdling",
            "record_help": "Halten zum Verhandeln",
            "message_input": "Ritze Deine Worte:",
            "send_button": "Entsenden",
            "start_dialog": "Güldene Zunge",
            "back_to_room": "Zurück zur Kammer",
            "dialog_title": "Wortgefecht",
            "patience_remaining": "Geduld schwindet:",
            "npc_disappear": "Die Gestalt zerrinnt... Kein Beistand naht.",
            "return_button": "Flieh dem Wortstreit",
            "npc_image_error": "Das Antlitz-Pergament fehlt!",
        }
    }
    return localized_texts[current_language].get(key, key)

def get_npc_key(npc: dict, suffix: str) -> str:
    """Generate unique state key for NPC"""
    return f"npc_{npc['name']}_{suffix}"


def reset_npc_states(npc_name: str) -> None:
    """Reset all states for specified NPC"""
    base_keys = [
        'dialog_started',
        'chat_history',
        'patience',
        'initial_patience',
        'dialog_completed',
        'success',
        'character'
    ]
    for key in base_keys:
        full_key = f"npc_{npc_name}_{key}"
        if full_key in st.session_state:
            del st.session_state[full_key]


def log_user_text(root: str, text: str) -> None:
    """Log user text to CSV file and session state"""
    # Сохраняем в session_state
    if 'user_text_log' not in st.session_state:
        st.session_state.user_text_log = []
    st.session_state.user_text_log.append(text)


# ======================
# NPC State Management
# ======================
def initialize_npc_states(npc: dict) -> None:
    """Initialize default states for NPC"""
    npc_key = lambda s: get_npc_key(npc, s)

    defaults = {
        'dialog_started': False,
        'chat_history': [],
        'dialog_completed': False,
        'success': False
    }

    for key, value in defaults.items():
        if not st.session_state.get(npc_key(key)):
            st.session_state[npc_key(key)] = value

    # Initialize patience for Conversational NPC
    if npc['type'].lower() == "conversational" and not st.session_state.get(npc_key('patience')):
        st.session_state[npc_key('patience')] = npc.get('patience', 3)
    if 'player_stats' not in st.session_state:
        st.session_state.player_stats = {'speaking_rate':[]}


def create_npc_character(npc: dict) -> Character:
    """Create Character instance based on NPC type"""
    current_language = st.session_state.get("selected_language", "en")
    print("!!", current_language)
    if current_language == 'en':
        if "guard" in npc['type'].lower():
            character = Character(
                prompt=prompt_template_guardian,
                sucess_prompt=prompt_template_check_sucess,
                whisper_model=whisper_model,
                gemini_model=gemini_model
            )
            character.fill(
                name=npc['name'],
                appearance=npc['appearance'],
                behavior=npc['behavior'],
                challenge=npc['challenge']
            )
        else:
            character = Character(
                prompt=prompt_template_conv,
                sucess_prompt=prompt_template_check_sucess,
                whisper_model=whisper_model,
                gemini_model=gemini_model
            )
            traps = "trap room" if type(npc['trap_rooms']) == list else ", ".join(npc['trap_rooms'])
            character.fill(
                name=npc['name'],
                behavior=npc['behavior'],
                appearance=npc['appearance'],
                trigger_words=npc['trigger_words'],
                information_to_share=npc['information_to_share'],
                trap_rooms=traps
            )
    else:
        if "guard" in npc['type'].lower():
            character = Character(
                prompt=prompt_template_guardian_de,
                sucess_prompt=prompt_template_check_sucess_de,
                whisper_model=whisper_model,
                gemini_model=gemini_model
            )
            character.fill(
                name=npc['name'],
                appearance=npc['appearance'],
                behavior=npc['behavior'],
                challenge=npc['challenge']
            )
        else:
            character = Character(
                prompt=prompt_template_conv_de,
                sucess_prompt=prompt_template_check_sucess_de,
                whisper_model=whisper_model,
                gemini_model=gemini_model
            )
            traps = "trap room" if type(npc['trap_rooms']) == list else ", ".join(npc['trap_rooms'])
            character.fill(
                name=npc['name'],
                behavior=npc['behavior'],
                appearance=npc['appearance'],
                trigger_words=npc['trigger_words'],
                information_to_share=npc['information_to_share'],
                trap_rooms=traps
            )
    return character


# ======================
# Dialog Handling
# ======================
def handle_successful_dialog(npc, current_room, is_success=True):
    """Обрабатывает завершение диалога, сохраняя открытые двери"""
    npc_key = lambda s: get_npc_key(npc, s)

    # Для conversational NPC обрабатываем терпение
    if npc['type'].lower() == "conversational":
        if not is_success:
            current_patience = st.session_state.get(npc_key('patience'), 0)
            if current_patience > 0 and len(st.session_state[npc_key('chat_history')]) > 1:
                st.session_state[npc_key('patience')] = current_patience - 1

            if st.session_state.get(npc_key('patience'), 0) <= 0:
                st.session_state[npc_key('dialog_completed')] = True
                st.session_state[npc_key('success')] = False
                return

    st.session_state[npc_key('dialog_completed')] = True
    st.session_state[npc_key('success')] = is_success

    current_room_id = current_room['id']
    target_rooms = []

    # Логика для guardian (только exits при успехе)
    if "guard" in npc['type'].lower() and is_success:
        target_rooms = [exit['target_room'] for exit in current_room.get('exits', [])]

    # Логика для conversational (exits + information_to_share при успехе / trap_rooms при неудаче)
    elif npc['type'].lower() == "conversational":
        if is_success:
            # Добавляем стандартные exits
            target_rooms = [exit['target_room'] for exit in current_room.get('exits', [])]
            # Добавляем information_to_share, если он есть
            if 'information_to_share' in npc:
                target_rooms.append(npc['information_to_share'])
        else:
            target_rooms = npc.get('trap_rooms', [])

    # Удаляем дубликаты и сохраняем
    if target_rooms:
        unique_rooms = list(set(target_rooms))  # На случай, если information_to_share совпадает с exit
        st.session_state.setdefault('unlocked_doors', {})[current_room_id] = unique_rooms

def process_audio_input(audio_bytes: bytes, npc: dict, current_room: dict) -> None:
    """Process audio input and generate NPC response"""
    npc_key = lambda s: get_npc_key(npc, s)

    audio_buffer = BytesIO(audio_bytes.read())
    audio = AudioSegment.from_file(audio_buffer, format="wav")

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        audio.export(temp_file.name, format="wav")
        temp_file_path = temp_file.name

    recognized_text = st.session_state[npc_key('character')].transcribe_audio(temp_file_path)
    speed_sp = st.session_state[npc_key('character')].speaking_rate(
        transcript=recognized_text,
        path=temp_file_path
    )
    st.session_state.player_stats['speaking_rate'].append(speed_sp)
    log_user_text(text=recognized_text, root=ROOT_LOG)
    st.session_state[npc_key('chat_history')].append({'type': 'player', 'text': recognized_text})

    npc_response, is_success = st.session_state[npc_key('character')].generate_response(recognized_text)
    st.session_state[npc_key('chat_history')].append({'type': 'npc', 'text': npc_response})
    if is_success:
        handle_successful_dialog(npc, current_room, is_success)


def process_text_input(user_input: str, npc: dict, current_room: dict) -> None:
    """Process text input and generate NPC response"""
    npc_key = lambda s: get_npc_key(npc, s)

    log_user_text(text=user_input, root=ROOT_LOG)
    st.session_state[npc_key('chat_history')].append({'type': 'player', 'text': user_input})

    npc_response, is_success = st.session_state[npc_key('character')].generate_response(user_input)
    print("is_success: ", is_success)
    st.session_state[npc_key('chat_history')].append({'type': 'npc', 'text': npc_response})
    if is_success:
        handle_successful_dialog(npc, current_room, is_success)


# ======================
# UI Components
# ======================
def render_npc_avatar(npc: dict) -> None:
    """Render NPC avatar image"""
    avatar_image_path = f"data/images/{npc['name'].replace(' ', '_').lower()}_pixel_style.png"

    left_co, cent_co, last_co = st.columns(3)
    with cent_co:
        if not os.path.exists(avatar_image_path):
            st.error(get_localized_text("npc_image_error"))
        else:
            st.image(avatar_image_path, width=250, caption="")


def render_chat_history(npc: dict) -> None:
    """Render chat history between player and NPC"""
    npc_key = lambda s: get_npc_key(npc, s)

    for msg in st.session_state[npc_key('chat_history')]:
        bubble_color = "#2d4059" if msg['type'] == 'npc' else "#4a6572"
        st.markdown(
            f"<div class='chat-bubble' style='border-color: {bubble_color};'>"
            f"{msg['text']}</div>",
            unsafe_allow_html=True
        )


def render_dialog_controls(npc: dict, current_room: dict) -> None:
    """Render dialog input controls (audio and text)"""
    npc_key = lambda s: get_npc_key(npc, s)
    key_audio = npc_key('audio_input') + "_" + str(len(st.session_state[npc_key('chat_history')]))

    # Audio input
    audio_bytes = st.audio_input(
        label=get_localized_text("speak_stranger"),
        key=key_audio,
        help=get_localized_text("record_help"),
        disabled=False
    )

    if audio_bytes:
        process_audio_input(audio_bytes, npc, current_room)
        st.rerun()

    # Text input
    user_input = st.text_area(get_localized_text("message_input"), key=npc_key('text_input'),
                               height=100)
    if st.button(get_localized_text("send_button")):
        if user_input.strip():
            process_text_input(user_input, npc, current_room)
            st.rerun()


# ======================
# Main Render Function
# ======================
def render_npc_page(npc: dict, current_room: dict) -> None:
    # handle_successful_dialog(npc, current_room)
    """Main function to render NPC page"""
    # Apply CSS styles
    st.markdown(CSS_STYLES, unsafe_allow_html=True)

    # Initialize NPC states
    if st.session_state.get('current_npc') != npc['name']:
        if 'current_npc' in st.session_state:
            reset_npc_states(st.session_state.current_npc)
        st.session_state.current_npc = npc['name']

    initialize_npc_states(npc)

    # Initialize Character if not exists
    npc_key = lambda s: get_npc_key(npc, s)
    if not st.session_state.get(npc_key('character')):
        st.session_state[npc_key('character')] = create_npc_character(npc)

    # Render NPC header and avatar
    st.markdown(f"<h1>{npc['name']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<div class='chat-bubble'>{npc['appearance']}</div>", unsafe_allow_html=True)
    render_npc_avatar(npc)

    st.markdown("---")

    # Render dialog start/back buttons if dialog not started
    if not st.session_state[npc_key('dialog_started')]:
        if st.button(get_localized_text("start_dialog"), use_container_width=True):
            st.session_state[npc_key('dialog_started')] = True
            st.rerun()

        if st.button(get_localized_text("back_to_room"), use_container_width=True):
            st.session_state.selected_npc = None
            st.session_state.current_screen = "game"
            st.rerun()

    # Render dialog if started
    if st.session_state[npc_key('dialog_started')]:
        st.markdown("---")
        st.markdown("<h2>Dialog</h2>", unsafe_allow_html=True)

        if npc['type'].lower() == "conversational":
            npc_patience_key = npc_key('patience')
            if npc_patience_key not in st.session_state:
                # Получаем начальное значение терпения из данных NPC
                initial_patience = npc.get('patience', 3) + 1
                st.session_state[npc_patience_key] = initial_patience
                # Сохраняем начальное значение для возможного сброса
                st.session_state[npc_key('initial_patience')] = initial_patience
            if st.session_state.get(npc_key('patience'), 0) <= 0:
                st.error(get_localized_text("npc_disappear"))
                if st.button(get_localized_text("return_button"), key=npc_key('return')):
                    st.session_state.selected_npc = None
                    st.session_state.current_screen = "game"
                    st.rerun()
                return
            else:
                # Показываем оставшееся терпение
                patience = st.session_state[npc_key('patience')]
                st.markdown(f"**{get_localized_text('patience_remaining')}** {patience}", unsafe_allow_html=True)

        render_chat_history(npc)
        render_dialog_controls(npc, current_room)

        st.markdown("---")
        if st.button(get_localized_text("return_button"), key=npc_key('return')):
            st.session_state.selected_npc = None
            st.session_state.current_screen = "game"
            st.rerun()


CSS_STYLES = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

    * {
        font-family: 'Press Start 2P', cursive !important;
        image-rendering: pixelated;
        color: #FFFFFF !important;
        background-color: #000000 !important;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #9229ea !important;
        text-shadow: 2px 2px #510e8a !important;
    }

    .stApp, .stSidebar, .stAlert {
        background-color: #000000 !important;
    }

    .stButton > button {
        all: unset !important;
        width: 100% !important;
        min-width: 240px !important;
        height: 40px !important;
        margin: 10px 0 !important;
        display: flex !important;
        align-items: center;
        justify-content: center!important;
        border: 3px solid  #9229ea !important;
        color: #9229ea!important;
        font-size: 0.8rem !important;
        cursor: pointer;
        transition: all 0.3s !important;
        text-align: center!importantr;
        padding-top: 15px !important;
        position: fixed;
        overflow: visible !important;
    }

    @keyframes red-glow {
        from {
            box-shadow: 0 0 5px #ff0000, 0 0 10px #ff0000;
        }
        to {
            box-shadow: 0 0 20px #ff0000, 0 0 40px #ff0000;
        }
    }
    .stButton > button:hover {
        animation: red-glow 0.8s ease-in-out infinite alternate;
        z-index: 1000;
    }

    .door-button {
        border-color: #9229ea !important;
        color: #9229ea !important;
    }

    button[key="return_button"] {
        border-color: #FFD700 !important !important;
    }

    div[data-testid="stAudioInput"] button {
        background-color: #9229ea !important;
        border: 2px solid #FFD700 !important;
        border-radius: 50% !important;
        width: 40px !important;
        height: 40px !important;
    }

    div[data-testid="stAudioInput"] label {
        color: #FFD700 !important;
        font-size: 0.8rem !important;
    }

    .chat-bubble {
        padding: 15px;
        margin: 10px 0;
        border-radius: 8px;
        border: 2px solid #FFD700;
        background-color: #1a1a1a;
    }

    .avatar-container {
        z-index: 1000;
        position: relative;
        text-align: center;
    }
    
    
    
</style>
"""
