# dungeon.py
import streamlit as st
from data_handler.graph import build_dungeon_graph

def all_graph():
    for el in range(10):
        st.session_state.visited_rooms.append(ind)
def show_dungeon_map():
    """Отображает карту с туннелями и адаптивными комнатами"""
    if 'dungeon_data' in st.session_state and 'visited_rooms' in st.session_state:
        dungeon_data = st.session_state.dungeon_data
        visited_rooms = st.session_state.visited_rooms
        # visited_rooms = []
        # for el in dungeon_data["rooms"]:
        #     visited_rooms.append(el['id'])
        # visited_rooms = ['room9']
        # Изолированный контейнер для карты
        st.markdown("""
        <style>
            .dungeon-container {
                border: 4px solid #8B0000;
                padding: 12px;
                margin-bottom: 20px;
                background: #000;
            }
            .dungeon-title {
                color: #FFD700;
                font-family: 'Press Start 2P';
                text-align: center;
                font-size: 1.2rem;
                margin: 0 0 10px 0;
                text-shadow: 2px 2px #8B0000;
            }
            .dungeon-graph {
                width: 100%;
                overflow: auto;
            }
        </style>

        <div class="dungeon-container">
            <div class="dungeon-title">DUNGEON MAP</div>
            <div class="dungeon-graph">
        """, unsafe_allow_html=True)

        graph = build_dungeon_graph(visited_rooms, dungeon_data["rooms"])
        st.graphviz_chart(graph.source, use_container_width=True)

        st.markdown("</div></div>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="border:3px solid #8B0000; padding:15px; color:#FF0000; 
            font-family:'Press Start 2P'; text-align:center; background:#000;">
            > MAP SYSTEM OFFLINE <
        </div>
        """, unsafe_allow_html=True)