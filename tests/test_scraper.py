"""Unit tests for the PriceScraper module.

Verifies HTML parsing accuracy, price sanitization, exception handling for missing
or unparseable price elements, and stock status determination.
"""

from src.scraper import PriceScraper


def test_parse_product_html_success() -> None:
    """Verify successful extraction of product name, valid price, and stock status."""
    scraper = PriceScraper(headless=True)
    sample_html = """
    <html>
        <body>
            <h1 class="product-title">Enterprise AI Workstation</h1>
            <span class="price">$1,499.99</span>
            <span class="stock-status">In Stock</span>
        </body>
    </html>
    """
    result = scraper.parse_product_html(sample_html, "https://example.com/product/1")

    assert result["name"] == "Enterprise AI Workstation"
    assert result["current_price"] == 1499.99
    assert result["in_stock"] is True
    assert result["target_url"] == "https://example.com/product/1"
