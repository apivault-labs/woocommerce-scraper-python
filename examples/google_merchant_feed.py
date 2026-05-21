"""
Generate a Google Merchant Center / Google Shopping product feed.

The output is one row per product with fields Google requires:
id, title, description, link, image_link, availability, price, brand, ...

    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/google_merchant_feed.py > merchant_feed.csv
"""

import csv
import sys

from woocommerce_scraper import WooCommerceScraperClient


SOURCE_STORE = "https://woocommerce.com"

GOOGLE_COLUMNS = [
    "id", "title", "description", "link", "image_link",
    "additional_image_link", "availability",
    "price", "sale_price", "brand", "mpn", "gtin",
    "condition", "google_product_category", "product_type",
    "identifier_exists",
]


def main() -> None:
    client = WooCommerceScraperClient(timeout=1800)

    feed = client.analyze(
        [SOURCE_STORE],
        max_products=0,
        export_format="google-merchant-only",
        only_in_stock=True,
    )

    writer = csv.DictWriter(sys.stdout, fieldnames=GOOGLE_COLUMNS,
                            extrasaction="ignore")
    writer.writeheader()
    for p in feed:
        writer.writerow(p)


if __name__ == "__main__":
    main()
