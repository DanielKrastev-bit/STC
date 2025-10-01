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


    for i in range(10):
        text = re.sub(r"  ", " ", text).strip()

    with open("output.txt", "w", encoding="utf-8") as f:
        f.write(text)
