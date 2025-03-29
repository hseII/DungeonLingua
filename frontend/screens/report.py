from constants import ROOT_LOG, WORDS_ROOT
import spacy
from collections import defaultdict
import csv
import os
import streamlit as st
import plotly.express as px
import pandas as pd

# Загрузка модели spaCy
nlp = spacy.load("en_core_web_sm")


# Функция для лемматизации
def lemmatize(word):
    return nlp(word)[0].lemma_


# Функция для анализа текста
def analyze_text(text) -> dict:
    # Загрузка словаря "слово - уровень"
    word_level_dict = defaultdict(str)
    level_count = ["A1", "A2", "B1", "B2", "C1", "C2"]
    with open(WORDS_ROOT, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if word_level_dict[row['word']] in level_count:
                if level_count.index(row['level']) < level_count.index(word_level_dict[row['word']]):
                    word_level_dict[row['word']] = row['level']
            else:
                word_level_dict[row['word']] = row['level']

    # Лемматизация текста
    doc = nlp(text)
    lemmatized_tokens = [lemmatize(token.text) for token in doc]

    # Определение уровней слов в тексте
    levels_in_text = []
    for token in lemmatized_tokens:
        if token in word_level_dict:
            levels_in_text.append((token, word_level_dict[token]))

    # Подсчёт количества слов по уровням
    level_count = defaultdict(int)
    for _, level in levels_in_text:
        level_count[level] += 1

    return dict(level_count)


# Функция для создания круговой диаграммы
def create_pie_chart(level_counts):
    levels = list(level_counts.keys())
    counts = list(level_counts.values())

    # Более светлая палитра в ретро-стиле
    colors = {
        "A1": "#FF6B6B",  # Светло-красный
        "A2": "#6BCB77",  # Светло-зеленый
        "B1": "#FFD93D",  # Светло-желтый
        "B2": "#A685E2",  # Светло-фиолетовый
        "C1": "#4D96FF",  # Светло-синий
        "C2": "#FF9F45"  # Светло-оранжевый
    }

    df = pd.DataFrame({
        "Level": levels,
        "Count": counts,
        "Color": [colors[level] for level in levels]
    })

    fig = px.pie(
        df,
        values="Count",
        names="Level",
        color="Level",
        color_discrete_map=colors,
        hole=0.35,
        title="<b>WORD LEVEL DISTRIBUTION</b>"
    )

    if counts:
        max_index = max(range(len(counts)), key=lambda i: counts[i])
        pull_values = [0.1 if i == max_index else 0 for i in range(len(counts))]
    else:
        pull_values = [0] * len(counts)

    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        marker=dict(
            line=dict(color='#333333', width=2)
        ),
        textfont=dict(
            family='"Press Start 2P", cursive',
            size=10,
            color='#FFFFFF'
        ),
        rotation=90,
        pull=pull_values,
        direction='clockwise',
        opacity=0.95
    )

    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5,
            font=dict(
                family='"Press Start 2P", cursive',
                size=8,
                color='#FFD700'
            ),
            bgcolor='rgba(0,0,0,0.5)'
        ),
        title=dict(
            x=0.5,
            y=0.95,
            font=dict(
                family='"Press Start 2P", cursive',
                size=14,
                color='#FFD700'
            )
        ),
        paper_bgcolor='rgba(0,0,0,0.5)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=80, b=80, l=40, r=40),
        hoverlabel=dict(
            font=dict(
                family='"Press Start 2P", cursive',
                size=10,
                color='#000000'
            ),
            bgcolor='#FFD700'
        ),
        uniformtext=dict(
            minsize=8,
            mode='hide'
        )
    )

    return fig


def display_player_stats():
    st.markdown('### Visited Rooms', unsafe_allow_html=True)
    st.markdown(f'**Count**: {len(st.session_state.get("visited_rooms", []))}', unsafe_allow_html=True)


def display_vocabulary():
    st.markdown('### Vocabulary Collection', unsafe_allow_html=True)
    if 'word_dictionary' in st.session_state:
        for word, data in st.session_state.word_dictionary.items():
            st.markdown(f'**{word}**: {data["translation"]}', unsafe_allow_html=True)
    else:
        st.markdown('No words collected yet!', unsafe_allow_html=True)


# Функция для анализа текста и отображения результатов
def display_speaking_stats():
    st.markdown('### Speaking Statistics', unsafe_allow_html=True)
    if 'player_stats' not in st.session_state:
        st.session_state.player_stats = {'speaking_rate':[]}
    if len(st.session_state.player_stats['speaking_rate']) == 0:
        st.markdown('No speaking data available yet!', unsafe_allow_html=True)
    if 'player_stats' in st.session_state and 'speaking_rate' in st.session_state.player_stats:
        speed = sum(st.session_state.player_stats['speaking_rate']) / len(st.session_state.player_stats['speaking_rate'])
        st.markdown(f'**Average Speaking Rate**: {speed:.2f} words per second', unsafe_allow_html=True)
    else:
        st.markdown('No speaking data available yet!', unsafe_allow_html=True)


def display_text_analysis():
    if 'user_text_log' in st.session_state and st.session_state.user_text_log:
        join_text = " ".join(st.session_state.user_text_log)
    else:
        st.markdown('No text found for analysis!', unsafe_allow_html=True)
        return
    level_counts = analyze_text(join_text)
    st.markdown('### Text Analysis', unsafe_allow_html=True)
    st.plotly_chart(
        create_pie_chart(level_counts),
        use_container_width=True,
        config={'displayModeBar': False}
    )
    # Отображение текстовой статистики
    for level, count in level_counts.items():
        st.markdown(f'**Level {level}**: {count} words', unsafe_allow_html=True)
    # else:


# Функция для отображения кнопки возврата
def display_end_game_button():
    col1, col2, col3 = st.columns([1.5, 1, 1.5])
    with col2:
        if st.button("End Game", key="end_game"):
            st.session_state.clear()
            st.session_state.current_screen = "welcome"
            st.rerun()


# Основная функция отрисовки
def style():
    st.markdown(CSS_STYLE, unsafe_allow_html=True)
    st.markdown('<h1 class="report-header">Progress Report</h1>', unsafe_allow_html=True)


def render():
    # Применение стилей
    style()
    # Контейнер для контента
    with st.container():
        st.markdown('<div class="centered-container">', unsafe_allow_html=True)
        display_text_analysis()
        display_player_stats()
        display_vocabulary()
        display_speaking_stats()
        display_end_game_button()
        st.markdown('</div>', unsafe_allow_html=True)


# CSS_STYLE = None
CSS_STYLE = """<style>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

/* Базовые стили для интерфейса (кроме графиков) */
body, .stApp, 
.stTextInput>div>div>input, 
.stSelectbox>div>div>select,
.stAlert, .stMarkdown {
    font-family: 'Press Start 2P', cursive !important;
    color: #FF0 !important;
    background-color: #000 !important;
    image-rendering: pixelated;
}

/* Заголовки и текст */
h1, h2, h3, h4, h5, h6,
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    color: #FFD700 !important;
    text-shadow: 3px 3px #8B0000;
}

.report-header {
    font-size: 2rem !important;
    text-align: center;
    margin: 2rem 0;
}

/* Блоки статистики */
.stat-block {
    background: #1A1A1A !important;
    border: 3px solid #4B0082 !important;
    border-radius: 0 !important;
    padding: 1.5rem;
    margin: 1.5rem 0;
    width: 80%;
    max-width: 600px;
    box-shadow: 5px 5px 0px #000;
}

/* Кнопки в стиле ретро-игр */
.stButton>button {
    background: #8B0000 !important;
    border: 3px solid #FFD700 !important;
    color: #FFF !important;
    border-radius: 0 !important;
    padding: 1rem 2rem !important;
    margin: 1.5rem 0 !important;
    transition: all 0.1s !important;
    box-shadow: 5px 5px 0px #300 !important;
    text-transform: uppercase;
}

.stButton>button:hover {
    transform: translate(2px, 2px);
    box-shadow: 3px 3px 0px #300 !important;
}

/* Исключения для графиков Plotly */
.plotly, .plot-container, 
.svg-container, .main-svg,
.plotly .modebar {
    background: transparent !important;
    image-rendering: auto !important;
}

/* Текст в графиках */
.plotly .legend text, 
.plotly .gtitle {
    font-family: 'Press Start 2P', cursive !important;
    fill: #FF0 !important;
}

/* Анимация мигания для ретро-эффекта */
@keyframes blink {
    0% { opacity: 0.8; }
    50% { opacity: 0.4; }
    100% { opacity: 0.8; }
}

.blink {
    animation: blink 1.5s infinite;
}
</style>"""
