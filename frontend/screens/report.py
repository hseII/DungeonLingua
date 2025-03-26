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


# Путь к CSV-файлу


# Функция для лемматизации
def lemmatize(word):
    return nlp(word)[0].lemma_


# Функция для анализа текста
def analyze_text(text):
    # Загрузка словаря "слово - уровень"
    word_level_dict = defaultdict(str)
    level_count = ["A1", "A2", "B1", "B2", "C1", "C2"]
    with open(WORDS_ROOT, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['word'] == "in":
                print(row['word'], row['level'])
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

    # Яркие цвета для уровней
    colors = {
        "A1": "#FF0000",  # Ярко-красный
        "A2": "#00FF00",  # Ярко-зелёный
        "B1": "#0000FF",  # Ярко-синий
        "B2": "#FF00FF",  # Ярко-розовый
        "C1": "#FFFF00",  # Ярко-жёлтый
        "C2": "#00FFFF"  # Ярко-голубой
    }

    # Создание DataFrame для Plotly
    import pandas as pd
    df = pd.DataFrame({"Level": levels, "Count": counts})
    df["Color"] = df["Level"].map(colors)

    # Создание круговой диаграммы
    fig = px.pie(df, values="Count", names="Level", color="Level",
                 color_discrete_map=colors,
                 title="Word Level Distribution in Text")

    # Настройка внешнего вида
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        marker=dict(line=dict(color='#FFFFFF', width=2)),  # Белая обводка для контраста
        textfont=dict(size=16, color='white')  # Белый текст для лучшей видимости
    )

    # Настройка макета
    fig.update_layout(
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',  # Прозрачный фон
        plot_bgcolor='rgba(0,0,0,0)',  # Прозрачный фон
        font=dict(color='white'),  # Белый цвет текста
        title_font=dict(size=20, color='white')  # Белый заголовок
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
def display_text_analysis():
    if os.path.exists(ROOT_LOG):
        with open(ROOT_LOG, "r") as file:
            reader = csv.DictReader(file)
            join_text = ""
            for row in reader:
                text = row["text"]
                join_text += text
            level_counts = analyze_text(join_text)
            st.markdown('### Text Analysis', unsafe_allow_html=True)

            # Отображение круговой диаграммы
            fig = create_pie_chart(level_counts)
            st.plotly_chart(fig, use_container_width=True)

            # Отображение текстовой статистики
            for level, count in level_counts.items():
                st.markdown(f'**Level {level}**: {count} words', unsafe_allow_html=True)
    else:
        st.markdown('No text file found for analysis!', unsafe_allow_html=True)


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
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

    * {
        font-family: 'Press Start 2P', cursive !important;
        image-rendering: pixelated;
        color: #FFF !important;
        background-color: #000 !important;
    }

    .report-header {
        font-size: 2rem !important;
        text-align: center;
        color: #FFD700 !important;
        text-shadow: 3px 3px #8B0000;
        margin: 2rem 0;
    }

    .stat-block {
        background: #1A1A1A !important;
        border: 3px solid #4B0082 !important;
        border-radius: 5px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        width: 80%;
        max-width: 600px;
    }

    .centered-container {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        width: 100%;
    }

    .stButton > button {
        background: #8B0000 !important;
        border: 3px solid #FFD700 !important;
        color: #FFF !important;
        border-radius: 0 !important;
        padding: 1rem 2rem !important;
        margin: 1.5rem 0 !important;
        transition: all 0.2s !important;
        box-shadow: 5px 5px 0px #8B0000 !important;
    }

    .stButton > button:hover {
        transform: translate(2px, 2px);
        box-shadow: 3px 3px 0px #8B0000 !important;
    }

    .section-header {
        color: #FFD700 !important;
        text-shadow: 2px 2px #8B0000;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    st.markdown('<h1 class="report-header">Progress Report</h1>', unsafe_allow_html=True)


def render():
    # Применение стилей
    style()
    # Контейнер для контента
    with st.container():
        st.markdown('<div class="centered-container">', unsafe_allow_html=True)
        display_player_stats()
        display_vocabulary()
        display_text_analysis()
        display_end_game_button()
        st.markdown('</div>', unsafe_allow_html=True)
