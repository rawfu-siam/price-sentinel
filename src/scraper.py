"""Web scraper module utilizing Playwright and Tenacity for robust automation.

Performs headless browser automation to extract product pricing and availability
from target e-commerce sites with built-in retry mechanisms and error isolation.
"""

from bs4 import BeautifulSoup
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

    def parse_product_html(self, html_content: str, target_url: str) -> dict:
        """Parse raw HTML to extract product name, price, and stock status."""
        logger.info("Parsing HTML content for product metrics...")
        soup = BeautifulSoup(html_content, "html.parser")

        try:
            # Robust selectors for standard e-commerce layout structures
            name_element = soup.select_one(
                "h1.product-title, h1.title, [data-testid='product-title']"
            )
            price_element = soup.select_one(
                ".product-price, .price, [data-testid='price']"
            )
            stock_element = soup.select_one(
                ".stock-status, .availability, [data-testid='stock']"
            )

            name = (
                name_element.get_text(strip=True) if name_element else "Unknown Product"
            )

            if price_element is None:
                raise ValueError(f"Price element not found on {target_url}")
            price_text = price_element.get_text(strip=True)
            cleaned_price = "".join(c for c in price_text if c.isdigit() or c == ".")
            if not cleaned_price:
                raise ValueError(f"Unparseable price '{price_text}' on {target_url}")
            current_price = float(cleaned_price)

            # Determine stock status defensively
            in_stock = True
            if stock_element:
                stock_text = stock_element.get_text(strip=True).lower()
                if (
                    "out of stock" in stock_text
                    or "unavailable" in stock_text
                    or "sold out" in stock_text
                ):
                    in_stock = False

            parsed_data = {
                "name": name,
                "target_url": target_url,
                "current_price": current_price,
                "in_stock": in_stock,
            }
            logger.info(f"Extracted product data for: {name} | Price: {current_price}")
            return parsed_data

        except Exception as e:
            logger.error(f"Error parsing HTML content: {e}")
            raise
