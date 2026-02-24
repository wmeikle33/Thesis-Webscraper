from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional
import time
import random
import logging

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ScrapeConfig:
    base_url: str
    headless: bool = True
    page_load_timeout_s: int = 30
    wait_timeout_s: int = 15
    min_delay_s: float = 1.0
    max_delay_s: float = 2.5
    max_retries: int = 3


@dataclass(frozen=True)
class Listing:
    url: str
    title: Optional[str] = None
    price: Optional[str] = None
    location: Optional[str] = None


class ThesisWebscraper:
    """
    Selenium-driven scraper. Keeps browser concerns here, not in cli.py.
    """

    def __init__(self, cfg: ScrapeConfig):
        self.cfg = cfg
        self.driver = self._make_driver()

    def _make_driver(self) -> webdriver.Chrome:
        opts = ChromeOptions()
        if self.cfg.headless:
            # "new" headless mode for recent Chromes
            opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--window-size=1280,900")

        driver = webdriver.Chrome(options=opts)
        driver.set_page_load_timeout(self.cfg.page_load_timeout_s)
        return driver

    def close(self) -> None:
        try:
            self.driver.quit()
        except Exception:
            pass

    def __enter__(self) -> "ThesisWebscraper":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def _polite_delay(self) -> None:
        time.sleep(random.uniform(self.cfg.min_delay_s, self.cfg.max_delay_s))

    def _get_with_retries(self, url: str) -> None:
        last_err: Exception | None = None
        for attempt in range(1, self.cfg.max_retries + 1):
            try:
                logger.info("GET %s (attempt %d/%d)", url, attempt, self.cfg.max_retries)
                self.driver.get(url)
                return
            except Exception as e:
                last_err = e
                # backoff + jitter
                sleep_s = min(10.0, attempt * 1.5) + random.uniform(0.0, 0.5)
                logger.warning("GET failed: %s. Sleeping %.2fs", e, sleep_s)
                time.sleep(sleep_s)
        assert last_err is not None
        raise last_err

    def search(self, query: str, limit: int = 100) -> list[Listing]:
        """
        High-level method: perform a search and return listings.
        You’ll replace selectors + URL format to match your target site.
        """
        # Example: build a search URL (update to your actual site)
        url = f"{self.cfg.base_url}/search?q={query}"
        self._get_with_retries(url)

        # Wait for results container to appear (update selector)
        wait = WebDriverWait(self.driver, self.cfg.wait_timeout_s)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".results")))

        listings: list[Listing] = []
        while len(listings) < limit:
            self._polite_delay()

            # Collect result cards (update selector)
            cards = self.driver.find_elements(By.CSS_SELECTOR, ".result-card")
            for card in cards:
                if len(listings) >= limit:
                    break

                # Extract fields (update selectors)
                link_el = card.find_elements(By.CSS_SELECTOR, "a")
                href = link_el[0].get_attribute("href") if link_el else None
                if not href:
                    continue

                title_el = card.find_elements(By.CSS_SELECTOR, ".title")
                price_el = card.find_elements(By.CSS_SELECTOR, ".price")
                loc_el = card.find_elements(By.CSS_SELECTOR, ".location")

                listings.append(
                    Listing(
                        url=href,
                        title=title_el[0].text.strip() if title_el else None,
                        price=price_el[0].text.strip() if price_el else None,
                        location=loc_el[0].text.strip() if loc_el else None,
                    )
                )

            # Pagination (update logic to match your site)
            next_btn = self.driver.find_elements(By.CSS_SELECTOR, "a.next")
            if not next_btn:
                break
            next_href = next_btn[0].get_attribute("href")
            if not next_href:
                break
            self._get_with_retries(next_href)

        return listings

    def enrich_listing(self, listing: Listing) -> Listing:
        """
        Optional: open a listing page and pull more details.
        """
        self._get_with_retries(listing.url)

        wait = WebDriverWait(self.driver, self.cfg.wait_timeout_s)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Example detail extraction (update selectors)
        title_el = self.driver.find_elements(By.CSS_SELECTOR, "h1")
        price_el = self.driver.find_elements(By.CSS_SELECTOR, ".price")
        loc_el = self.driver.find_elements(By.CSS_SELECTOR, ".location")

        return Listing(
            url=listing.url,
            title=title_el[0].text.strip() if title_el else listing.title,
            price=price_el[0].text.strip() if price_el else listing.price,
            location=loc_el[0].text.strip() if loc_el else listing.location,
        )


def scrape(query: str, limit: int, cfg: ScrapeConfig) -> list[Listing]:
    """
    Convenience function for orchestration layers (main.py).
    """
    with ThesisWebscraper(cfg) as s:
        listings = s.search(query=query, limit=limit)

        # If you want per-listing enrichment:
        # listings = [s.enrich_listing(x) for x in listings]

        return listings
