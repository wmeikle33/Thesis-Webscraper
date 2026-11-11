from __future__ import annotations

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .config import ScrapeConfig
from .parser import parse_post
from .models import ScrapeResult


class ThesisWebscraper:
    def __init__(self, cfg: ScrapeConfig):
        self.cfg = cfg
        self.driver = self._make_driver()

    def _make_driver(self) -> webdriver.Chrome:
        opts = ChromeOptions()
        if self.cfg.headless:
            opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--window-size=1280,900")

        driver = webdriver.Chrome(options=opts)
        return driver

    def _build_page_url(self, base_url: str, page: int) -> str:
        if page == 1:
            return base_url
        return f"{base_url}?page={page}"

    def collect_thread_urls(self, start_url: str, max_pages: int) -> list[str]:
        thread_urls = []
    
        for page in range(1, max_pages + 1):
            url = self._build_page_url(start_url, page)
    
            self.driver.get(url)
    
            links = self.driver.find_elements("css selector", "a[href*='thread']")
    
            for link in links:
                href = link.get_attribute("href")
                if href:
                    thread_urls.append(href)
    
        return list(set(thread_urls)) 

    def close(self) -> None:
        try:
            self.driver.quit()
        except Exception:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def fetch_html(self, url: str) -> str:
        self.driver.get(url)
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        return self.driver.page_source

    def scrape_thread(self, url: str):
        html = self.fetch_html(url)
        return parse_post(html, url)


def scrape(cfg: ScrapeConfig) -> ScrapeResult:
    result = ScrapeResult()

    # For now, assume cfg.start_urls exists and contains thread URLs.
    with ThesisWebscraper(cfg) as scraper:
        thread_urls = scraper.collect_thread_urls(
            start_url=cfg.start_url,
            max_pages=cfg.pages,
        )
        
        for url in thread_urls:
            post, comments = scraper.scrape_thread(url)

    return result

