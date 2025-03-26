from bs4 import BeautifulSoup
import csv
# Загрузка HTML-файла
with open('/FAI/my/data/model/English Profile - EVP Online.html', 'r', encoding='utf-8') as file:
    html_content = file.read()

soup = BeautifulSoup(html_content, 'html.parser')
table = soup.find('tbody')
words_with_levels = []
if table:
    rows = table.find_all('tr')
    for row in rows:
        cells = row.find_all('td')
        if len(cells) > 2:
            word = cells[0].text.strip()
            level_span = cells[2].find('span', class_='label')
            if level_span:
                level = level_span.text.strip()
                words_with_levels.append((word, level))

print(len(words_with_levels))
with open("/FAI/my/data/words.csv", "w", encoding='utf-8') as f:
    fieldnames = ['word', 'level']
    writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator='\n')
    writer.writeheader()
    ind = 0
    for word, level in words_with_levels:
        print(ind, word)
        ind += 1
        writer.writerow({'word': word, 'level': level})