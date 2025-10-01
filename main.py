import sys
from scrape import scrape
from push_icloud import push
from parse_html import parse
from to_sql import import_schedule
from datetime import date

if __name__ == "__main__":
    week = sys.argv[1] if len(sys.argv) > 1 else str(date.today().isocalendar()[1])
    url=sys.argv[2] if len(sys.argv) > 2 else "https://app.shkolo.bg"
    for i in range(1, 6):
        print(f"--- WEEK {week} ---")
        scrape(url, week)
        parse()
        import_schedule()
        week = str(int(week)+1)
        i+=1

