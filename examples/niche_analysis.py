"""
Aggregate niche stats from many WooCommerce stores.

Pulls catalog snapshots for a list of stores, then computes niche-wide
metrics: average price, brand diversity, category dominance, premium ratio.

Useful for picking which niche to enter or which to avoid.

    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/niche_analysis.py
"""

from collections import Counter

from woocommerce_scraper import WooCommerceScraperClient


# Stores in the same niche
NICHE_STORES = [
    "https://woocommerce.com",
    # Replace with stores in your niche
]


def main() -> None:
    client = WooCommerceScraperClient(timeout=900)
    snapshots = client.snapshot(NICHE_STORES, max_products=300)
    snapshots = [s for s in snapshots if s.get("success")]
    if not snapshots:
        print("No data."); return

    # Niche-wide aggregates
    total_products = sum(s.get("product_count") or 0 for s in snapshots)
    avg_median = sum(s.get("price_median") or 0 for s in snapshots) / len(snapshots)
    avg_aov = sum(s.get("aov_estimate") or 0 for s in snapshots) / len(snapshots)
    avg_quality = sum(s.get("avg_intelligence_score") or 0 for s in snapshots) / len(snapshots)
    avg_premium = sum(s.get("premium_listings_pct") or 0 for s in snapshots) / len(snapshots)

    # Brand diversity
    all_brands: Counter = Counter()
    all_categories: Counter = Counter()
    for s in snapshots:
        for b in s.get("top_brands") or []:
            all_brands[b["brand"]] += b["products"]
        for c in s.get("category_distribution") or []:
            all_categories[c["category"]] += c["count"]

    print(f"\n=== Niche analysis ({len(snapshots)} stores) ===\n")
    print(f"  Total products tracked:   {total_products:,}")
    print(f"  Avg price median:         ${avg_median:.2f}")
    print(f"  Avg AOV estimate:         ${avg_aov:.2f}")
    print(f"  Avg quality score:        {avg_quality:.1f}/100")
    print(f"  Avg premium listings %:   {avg_premium:.1f}%")

    print(f"\n  Top brands across niche:")
    for brand, count in all_brands.most_common(10):
        print(f"    {brand:30} {count}")

    print(f"\n  Category distribution:")
    for cat, count in all_categories.most_common():
        print(f"    {cat:20} {count}")


if __name__ == "__main__":
    main()
