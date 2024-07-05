import re
from typing import Optional

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


class ScraperException(Exception):
    """Custom exception for scraper-related errors."""


class FearGreedIndexScraper:
    """A scraper for the Cardano Fear and Greed Index."""

    URL = 'https://cfgi.io/cardano-fear-greed-index/'
    # cspell:disable-next-line
    CLASS_SELECTOR = 'apexcharts-datalabel-value'
    WEB_DRIVER_WAIT_DEFAULT_TIMEOUT = 15

    def __init__(self, logger, web_driver_wait_timeout: Optional[int] = None):
        """
        Initialize the FearGreedIndexScraper.

        :param logger: Logger object for logging messages.
        :param web_driver_wait_timeout: Timeout for WebDriverWait (optional).
        """
        self.logger = logger
        self.index_value: Optional[str] = None
        self.web_driver_wait_timeout = web_driver_wait_timeout or self.WEB_DRIVER_WAIT_DEFAULT_TIMEOUT
        self.driver = self._init_driver()

    def _init_driver(self) -> webdriver.Chrome:
        """Initialize and return a Chrome WebDriver."""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def fetch_page_content(self) -> Optional[str]:
        """Fetch the page content from the URL."""
        try:
            self.driver.get(self.URL)
            WebDriverWait(self.driver, self.web_driver_wait_timeout).until(
                EC.presence_of_element_located((By.CLASS_NAME, self.CLASS_SELECTOR))
            )
            return self.driver.page_source
        except Exception as e:
            self.logger.error(f"Error fetching page content: {e}")
            raise ScraperException(f"Failed to fetch page content: {e}") from e

    def parse_index_value(self, html_content: str) -> None:
        """Parse the index value from the HTML content."""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            index_element = soup.find(class_=self.CLASS_SELECTOR)
            if index_element:
                self.index_value = index_element.get_text(strip=True)
                self.logger.info(f"Successfully parsed index value: {self.index_value}")
            else:
                raise ScraperException("Could not find the Fear and Greed Index element on the page.")
        except Exception as e:
            self.logger.error(f"Error parsing HTML content: {e}")
            raise ScraperException(f"Failed to parse HTML content: {e}") from e

    @staticmethod
    def extract_number(percentage_str: str) -> Optional[int]:
        """Extract the numeric value from a percentage string."""
        match = re.search(r'\d+', percentage_str)
        return int(match.group()) if match else None

    def get_index_value(self) -> Optional[int]:
        """Get the Fear and Greed Index value."""
        try:
            with self.driver:  # Use context manager for proper cleanup
                html_content = self.fetch_page_content()
                if html_content:
                    self.parse_index_value(html_content)
                return self.extract_number(self.index_value) if self.index_value else None
        except ScraperException as e:
            self.logger.error(f"Scraper error: {e}")
            return None
        finally:
            if self.driver:
                self.driver.quit()
