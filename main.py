import sys
from scrape import scrape
from push_icloud import push
from parse_html import parse

if __name__ == "__main__":
    url=sys.argv[1] if len(sys.argv) > 1 else "https://app.shkolo.bg"
    data = scrape(url)
    parse()