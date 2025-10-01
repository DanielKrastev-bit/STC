import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

def scrape(url, week):
    url = url+"/ajax/diary/getScheduleForClass"
    params = {
        "pupil_id": "2500074621",
        "year": "25",
        "week": f"{week}",
        "class_year_id": "2500004725"
    }
    cookies = {
        "shkolo-cookie": "eyJpdiI6IlVNS0NSdTMwSyswWjJ4aFE0cTc3d2c9PSIsInZhbHVlIjoiSDlUM3ZhK1JJcnR3QU1qd01BZWFrMGVyQ1pxb1QrZm1KV1JoemFjUHZiMDZhWFV0azdTbU9ZMElaRngwT0xWQTJYTFI3UWk5eUtSZmJMeEhxZXh0WWIxb3NRR3VxQUVQSXc3c0tUM2JVTFJEd2xCZVNIWmJVVmtkcVV2YUU4ckkiLCJtYWMiOiJjNTMxYTNiYWZmZTBmYmNhYjYxOGRjZWQyN2UwYzM1NTM5YmY0NTU0NDVkOTc0NTc1M2ZiZWRiODE3NDMxMWU4IiwidGFnIjoiIn0%3D"
    }
    r = requests.get(url, params=params, cookies=cookies)

    print("Status:", r.status_code)
    
    with open('output.html', 'w', encoding='utf-8') as f:
        f.write(r.text)