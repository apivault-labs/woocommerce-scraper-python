"""
Quickstart: pull a few products from a single WooCommerce store.

    pip install -r requirements.txt
    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/quickstart.py
"""

from woocommerce_scraper import WooCommerceScraperClient


def main() -> None:
    client = WooCommerceScraperClient()

    products = client.analyze_store(
        "https://woocommerce.com",
        max_products=10,
        enrich_variants=True,
    )

    print(f"\nGot {len(products)} products\n")
    for p in products[:5]:
        print(f"=== {p.get('title')} ===")
        print(f"  Price:        {p.get('price')} {p.get('currency')}")
        if p.get("discountPct"):
            print(f"  Discount:     {p.get('discountPct')}%")
        print(f"  Brand:        {p.get('brand') or '(unknown)'}")
        print(f"  Category:     {p.get('autoCategory')}")
        print(f"  Rank:         #{p.get('popularityRank')}")
        print(f"  Score:        {p.get('productIntelligenceScore')}/100")
        print(f"  In stock:     {p.get('inStock')}")
        print(f"  New arrival:  {p.get('isNewArrival')}")
        print()


if __name__ == "__main__":
    main()
