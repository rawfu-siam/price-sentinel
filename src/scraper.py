"""Web scraper module utilizing Playwright and Tenacity for robust automation.

Performs headless browser automation to extract product pricing and availability
from target e-commerce sites with built-in retry mechanisms and error isolation.
"""

from playwright.async_api import Error as PlaywrightError
from playwright.async_api import async_playwright
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from src.logger import logger


class PriceScraper:
    """Automates browser interactions to scrape product details safely."""

    def __init__(self, headless: bool = True) -> None:
        """Initialize scraper parameters."""
        self.headless = headless
        logger.info("Initialized PriceScraper instance.")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((PlaywrightError, ConnectionError)),
        reraise=True,
    )
    async def fetch_page_content(self, url: str) -> str:
        """Fetch raw HTML content from the target URL with automatic retry logic."""
        logger.info(f"Navigating to target URL: {url}")
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            )
            page = await context.new_page()
            try:
                await page.goto(url, timeout=30000, wait_until="domcontentloaded")
                content = await page.content()
                logger.info(f"Successfully fetched content from {url}")
                return content
            except Exception as e:
                logger.error(f"Failed to load page {url}: {e}")
                raise
            finally:
                await browser.close()
