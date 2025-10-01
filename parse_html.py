import re
from bs4 import BeautifulSoup

def parse():
    with open("output.html", "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style"]):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)

    text = re.sub(r"\n", " ", text).strip()
    days = ["Пон", "Вто", "Сря", "Чет", "Пет"]

    for d in days:
        text = re.sub(rf"\b{d}\b", "\n", text)
    text = re.sub(r"\n+", "\n", text).strip()
    text = re.sub(r'^\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'(\b\d\.)', r'\n\1', text)
    text = re.sub(r'/ Група 1', "", text)
    text = re.sub(r"\([^)]*\)", "", text)
    text = re.sub(r"Последна.*", "", text)
    text = re.sub(r"УП - Специализирана", "УП_Практика", text).strip()
    text = re.sub(r"Приложен софтуер", "ПС", text).strip()
    text = re.sub(r"Промишлена електроника", "ПЕ", text).strip()
    text = re.sub(r"Микропроцесорна техника", "МТ", text).strip()
    text = re.sub(r"Компютърни системи", "КС", text).strip()
    text = re.sub(r"УП - По специални измервания", "УП_Измервания", text).strip()
    text = re.sub(r"Спортни дейности", "ФВС", text).strip()
    text = re.sub(r"Съвременни тенденции в промишлен", "СТП", text).strip()

    for i in range(10):
        text = re.sub(r"  ", " ", text).strip()

    with open("output.txt", "w", encoding="utf-8") as f:
        f.write(text)
