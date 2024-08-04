import logging
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


class FearAndGreedIndexWebScraper:
    """
    A scraper for the Cardano Fear and Greed Index.

    This class provides functionality to scrape the Cardano Fear and Greed Index
    from a specified URL using Selenium WebDriver and BeautifulSoup.

    Attributes:
        URL (str): The URL of the Cardano Fear and Greed Index page.
        CLASS_SELECTOR (str): The CSS class selector for the index value element.
        WEB_DRIVER_WAIT_DEFAULT_TIMEOUT (int): Default timeout for WebDriverWait.
    """

    URL: str = 'https://cfgi.io/cardano-fear-greed-index/'
    # cspell:disable-next-line
    CLASS_SELECTOR: str = 'apexcharts-datalabel-value'
    WEB_DRIVER_WAIT_DEFAULT_TIMEOUT: int = 15

    def __init__(self, logger: logging.Logger, web_driver_wait_timeout: Optional[int] = None):
        """
        Initialize the FearGreedIndexScraper.

        Args:
            logger (logging.Logger): Logger object for logging messages.
            web_driver_wait_timeout (Optional[int]): 
                Timeout for WebDriverWait. Defaults to WEB_DRIVER_WAIT_DEFAULT_TIMEOUT.
        """
        self.logger: logging.Logger = logger
        self.index_value: Optional[str] = None
        self.web_driver_wait_timeout: int = web_driver_wait_timeout or self.WEB_DRIVER_WAIT_DEFAULT_TIMEOUT
        self.logger.info("[FearAndGreedIndexWebScraper] Initializing WebDriver...")
        self.driver: webdriver.Chrome = self._init_driver()
        self.logger.info("[FearAndGreedIndexWebScraper] WebDriver initialized.")

    def _init_driver(self) -> webdriver.Chrome:
        """
        Initialize and return a Chrome WebDriver.

        Returns:
            webdriver.Chrome: An instance of Chrome WebDriver.
        """
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def fetch_page_content(self) -> str:
        """
        Fetch the page content from the URL.

        Returns:
            str: The HTML content of the page.

        Raises:
            ScraperException: If there's an error fetching the page content.
        """
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
        """
        Parse the index value from the HTML content.

        Args:
            html_content (str): The HTML content to parse.

        Raises:
            ScraperException: If there's an error parsing the HTML content or if the index element is not found.
        """
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
        """
        Extract the numeric value from a percentage string.

        Args:
            percentage_str (str): The percentage string to extract the number from.

        Returns:
            Optional[int]: The extracted number as an integer, or None if no number is found.
        """
        match = re.search(r'\d+', percentage_str)
        return int(match.group()) if match else None

    def get_index_value(self) -> Optional[int]:
        """
        Get the Fear and Greed Index value.

        Returns:
            Optional[int]: The Fear and Greed Index value as an integer, or None if the value couldn't be retrieved.
        """
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
