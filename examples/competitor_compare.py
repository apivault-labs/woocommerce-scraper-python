"""
Side-by-side comparison of competing WooCommerce catalogs.

Useful for niche research: "which competitor has the deepest catalog?",
"who has the most premium listings?", "who's discounting hardest?".

    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/competitor_compare.py
"""

from woocommerce_scraper import WooCommerceScraperClient


COMPETITORS = [
    "https://woocommerce.com",
    # Add more
]


def fmt(v) -> str:
    if v is None:
        return "—"
    return str(v)


def main() -> None:
    client = WooCommerceScraperClient(timeout=900)
    snapshots = client.snapshot(COMPETITORS, max_products=300)
    snapshots = [s for s in snapshots if s.get("success")]
    if not snapshots:
        print("No successful snapshots."); return

    rows = [
        ("Domain",                "domain"),
        ("Products",              "product_count"),
        ("Median price",          "price_median"),
        ("AOV estimate",          "aov_estimate"),
        ("On-sale %",             "products_on_sale_pct"),
        ("Avg discount %",        "avg_discount_pct"),
        ("In-stock %",            "in_stock_pct"),
        ("New arrivals (30d)",    "new_arrivals_30d"),
        ("Brands count",          "brands_count"),
        ("Avg quality score",     "avg_intelligence_score"),
        ("Premium listings %",    "premium_listings_pct"),
        ("Total reviews",         "total_reviews"),
        ("Avg rating",            "catalog_avg_rating"),
    ]

    col_w = 24
    print()
    header = f"{'Metric':<{col_w}} | " + " | ".join(
        f"{(s['domain'] or '?')[:col_w]:<{col_w}}" for s in snapshots
    )
    print(header)
    print("-" * len(header))
    for label, key in rows[1:]:  # skip the first row (domain header)
        line = f"{label:<{col_w}} | " + " | ".join(
            f"{fmt(s.get(key))[:col_w]:<{col_w}}" for s in snapshots
        )
        print(line)


if __name__ == "__main__":
    main()
