"""
Export a WooCommerce catalog to Shopify-Product-CSV format.

Use the resulting CSV to import into Shopify Admin → Products → Import.

    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/shopify_migration.py > shopify_products.csv
"""

import csv
import sys

from woocommerce_scraper import WooCommerceScraperClient


SOURCE_STORE = "https://woocommerce.com"

SHOPIFY_COLUMNS = [
    "Handle", "Title", "Body (HTML)", "Vendor", "Type", "Tags", "Published",
    "Option1 Name", "Option1 Value",
    "Variant SKU", "Variant Inventory Tracker", "Variant Inventory Qty",
    "Variant Inventory Policy", "Variant Fulfillment Service",
    "Variant Price", "Variant Compare At Price",
    "Variant Requires Shipping", "Variant Taxable",
    "Image Src", "Image Position", "Image Alt Text",
    "Gift Card", "SEO Title", "SEO Description", "Status",
]


def main() -> None:
    client = WooCommerceScraperClient(timeout=1800)

    products = client.analyze(
        [SOURCE_STORE],
        max_products=0,  # all
        export_format="shopify-csv-only",
    )

    writer = csv.DictWriter(sys.stdout, fieldnames=SHOPIFY_COLUMNS,
                            extrasaction="ignore")
    writer.writeheader()
    for p in products:
        writer.writerow(p)


if __name__ == "__main__":
    main()
