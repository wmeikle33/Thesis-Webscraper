
"""
Pagination utilities for Thesis-Webscraper.

Handle navigation through multi-page automotive forums
using Selenium 4.
"""

from collections.abc import Iterator
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException


class PaginationManager:
    """
    Manage navigation between forum pages.

    Parameters
    ----------
    driver : WebDriver
        Selenium browser instance.

    max_pages : int
        Maximum number of pages to visit.

    timeout : int
        Maximum seconds to wait for navigation.
    """

    def __init__(
        self,
        driver: WebDriver,
        max_pages: int = 100,
        timeout: int = 10,
    ) -> None:

        if max_pages < 1:
            raise ValueError("max_pages must be positive")

        self.driver = driver
        self.max_pages = max_pages
        self.timeout = timeout

        self.visited_urls: set[str] = set()

    @staticmethod
    def generate_page_url(
        base_url: str,
        page_number: int,
        page_parameter: str = "page",
    ) -> str:
        """
        Generate a URL with a page query parameter.

        Example:
        example.com/forum?page=2
        """

        if page_number < 1:
            raise ValueError("page_number must be positive")

        parts = urlsplit(base_url)

        query = dict(parse_qsl(parts.query))
        query[page_parameter] = str(page_number)

        return urlunsplit((
            parts.scheme,
            parts.netloc,
            parts.path,
            urlencode(query),
            parts.fragment,
        ))

    def has_next_page(
        self,
        next_selector: str,
    ) -> bool:
        """
        Check whether an enabled next-page element exists.
        """

        elements = self.driver.find_elements(
            By.CSS_SELECTOR,
            next_selector,
        )

        for element in elements:

            disabled = element.get_attribute(
                "aria-disabled"
            )

            classes = (
                element.get_attribute("class") or ""
            ).split()

            if (
                element.is_displayed()
                and element.is_enabled()
                and disabled != "true"
                and "disabled" not in classes
            ):
                return True

        return False

    def go_to_next_page(
        self,
        next_selector: str,
    ) -> bool:
        """
        Click the next-page element and wait for
        the current page to become stale.

        Returns True if navigation succeeds.
        """

        if not self.has_next_page(next_selector):
            return False

        previous_page = self.driver.find_element(
            By.TAG_NAME,
            "html",
        )

        elements = self.driver.find_elements(
            By.CSS_SELECTOR,
            next_selector,
        )

        next_button = next(
            (
                element for element in elements
                if element.is_displayed()
                and element.is_enabled()
                and element.get_attribute("aria-disabled")
                != "true"
                and "disabled" not in (
                    element.get_attribute("class") or ""
                ).split()
            ),
            None,
        )

        if next_button is None:
            return False

        next_button.click()

        try:
            WebDriverWait(
                self.driver,
                self.timeout,
            ).until(
                lambda driver:
                    self._page_changed(previous_page)
            )

        except TimeoutException:
            return False

        return True

    def _page_changed(
        self,
        previous_page,
    ) -> bool:
        """
        Detect whether the previous HTML element
        has become stale.
        """

        try:
            previous_page.is_enabled()
            return False

        except Exception as exc:
            from selenium.common.exceptions import (
                StaleElementReferenceException,
            )

            if isinstance(
                exc,
                StaleElementReferenceException,
            ):
                return True

            raise

    def iterate_pages(
        self,
        start_url: str,
        next_selector: str,
        rate_limiter=None,
    ) -> Iterator[str]:
        """
        Yield HTML from each visited page.

        Rate limiting is applied before navigation.
        """

        if rate_limiter is not None:
            rate_limiter.wait()

        self.driver.get(start_url)

        for _ in range(self.max_pages):

            current_url = self.driver.current_url

            if current_url in self.visited_urls:
                break

            self.visited_urls.add(current_url)

            yield self.driver.page_source

            if not self.has_next_page(next_selector):
                break

            if rate_limiter is not None:
                rate_limiter.wait()

            if not self.go_to_next_page(next_selector):
                break
