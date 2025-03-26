import streamlit as st
from screens import welcome, game, npc, report  # Добавляем импорт отчёта

def main():
    st.set_page_config(
        page_title="Dungeon of Lingua",
        page_icon="🏰",
        layout="centered"
    )

    # Инициализация состояний
    required_states = {
        "current_screen": "welcome",
        "dungeon_data": None,
        "current_room_id": None,
        "current_room": None,
        "death_description": None  # Новое состояние для хранения описания смерти
    }

    for key, value in required_states.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # Навигация
    if st.session_state.current_screen == "welcome":
        welcome.render()
    elif st.session_state.current_screen == "game":
        game.render()
    elif st.session_state.current_screen == "npc" and st.session_state.selected_npc:
        # Получаем текущую комнату из session_state
        current_room = st.session_state.current_room
        npc.render_npc_page(st.session_state.selected_npc, current_room)
    elif st.session_state.current_screen == "report":  # Новый экран отчёта
        from screens import report
        report.render()

if __name__ == "__main__":
    main()