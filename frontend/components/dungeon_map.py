import streamlit as st
from data_handler.graph import build_dungeon_graph


def show_dungeon_map():
    """Отображает пиксельную карту с угловатыми соединениями"""
    if 'dungeon_data' in st.session_state and 'visited_rooms' in st.session_state:
        dungeon_data = st.session_state.dungeon_data
        visited_rooms = st.session_state.visited_rooms

        graph = build_dungeon_graph(visited_rooms, dungeon_data["rooms"])

        st.markdown("""
        <div style="border:3px solid #8B0000; padding:10px; margin-bottom:20px;">
            <h3 style="color:#FFFFFF; font-family:'Press Start 2P'; text-align:center;">DUNGEON MAP</h3>
        </div>
        """, unsafe_allow_html=True)

        st.graphviz_chart(
            graph.source,
            use_container_width=True
        )
    else:
        st.markdown("""
        <div style="border:3px solid #8B0000; padding:15px; color:#FFFFFF; 
            font-family:'Press Start 2P'; text-align:center;">
            > MAP SYSTEM OFFLINE
        </div>
        """, unsafe_allow_html=True)