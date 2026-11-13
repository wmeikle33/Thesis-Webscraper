from .fetch import fetch_html
from scraping.parser import parse_post

def scrape_post(driver, url: str):
    html = fetch_html(driver, url)
    return parse_post(html, url)
