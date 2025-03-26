import spacy
from collections import defaultdict
import csv

# Загрузка модели spaCy
nlp = spacy.load("en_core_web_sm")

# Пример словаря "слово - уровень"
word_level_dict = defaultdict(str)
level_count = ["A1", "A2", "B1", "B2", "C1", "C2"]
with open("FAI/data/words.csv", "r") as f:
    reader = csv.DictReader(f)
    for en, row in enumerate(reader):
        if row['word'] == "in":
            print(row['word'], row['level'])
        if word_level_dict[row['word']] in level_count:
            if level_count.index(row['level']) < level_count.index(word_level_dict[row['word']]):
                word_level_dict[row['word']] = row['level']
        else:
            word_level_dict[row['word']] = row['level']


# Функция для лемматизации
def lemmatize(word):
    return nlp(word)[0].lemma_


# Текст для анализа
text = "The cats are running in a complex environment."

doc = nlp(text)
lemmatized_tokens = [lemmatize(token.text) for token in doc]

levels_in_text = []
for token in lemmatized_tokens:
    if token in word_level_dict:
        levels_in_text.append((token, word_level_dict[token]))

for word, level in levels_in_text:
    print(f"Word: {word}, Level: {level}")

level_count = defaultdict(int)
for _, level in levels_in_text:
    level_count[level] += 1
print("Level counts:", dict(level_count))
