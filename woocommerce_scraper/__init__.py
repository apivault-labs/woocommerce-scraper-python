"""
WooCommerce Scraper — Python SDK

Official Python client for the apivault_labs/woocommerce-product-scraper Apify actor.
Full catalog extraction from any WooCommerce store: variants, reviews, brand
auto-detection, FX conversion, Shopify CSV export, Google Merchant feed,
catalog snapshots — all via the public Store API.

Quick start:

    from woocommerce_scraper import WooCommerceScraperClient

    client = WooCommerceScraperClient(api_token="apify_api_xxxxxx")
    products = client.analyze_store("https://store.com", max_products=100)

    print(products[0]["title"], products[0]["price"])

See https://github.com/apivault-labs/woocommerce-scraper-python for full docs.
"""

from .client import WooCommerceScraperClient
from .exceptions import (
    WooCommerceScraperError,
    AuthenticationError,
    ActorRunError,
    ActorTimeoutError,
)

__version__ = "0.1.0"
__all__ = [
    "WooCommerceScraperClient",
    "WooCommerceScraperError",
    "AuthenticationError",
    "ActorRunError",
    "ActorTimeoutError",
]
