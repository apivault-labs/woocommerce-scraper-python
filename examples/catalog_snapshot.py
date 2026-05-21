"""
Pull aggregate intelligence on multiple WooCommerce stores in one call.

Each store returns ONE record summarizing its entire catalog —
totals, brands, categories, AOV estimate, premium-listings %, top-3 by reviews.

Perfect for weekly competitor dashboards. 100 stores -> 100 rows of intel.

    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/catalog_snapshot.py
"""

from woocommerce_scraper import WooCommerceScraperClient


COMPETITORS = [
    "https://woocommerce.com",
    # Add more competitor stores here
]


def main() -> None:
    client = WooCommerceScraperClient(timeout=900)
    snapshots = client.snapshot(COMPETITORS, max_products=200)

    for s in snapshots:
        print(f"\n=== {s.get('domain')} ===")
        print(f"  Products:           {s.get('product_count')}")
        print(f"  Currency:           {s.get('currency')}")
        print(f"  Price range:        "
              f"{s.get('price_min')} - {s.get('price_max')} "
              f"(median {s.get('price_median')})")
        print(f"  AOV estimate:       {s.get('aov_estimate')}")
        print(f"  On sale:            {s.get('products_on_sale_pct')}%")
        print(f"  In stock:           {s.get('in_stock_pct')}%")
        print(f"  New arrivals (30d): {s.get('new_arrivals_30d')}")
        print(f"  Brands:             {s.get('brands_count')} unique")
        print(f"  Avg quality score:  {s.get('avg_intelligence_score')}/100")
        print(f"  Premium listings:   {s.get('premium_listings_pct')}%")
        print(f"  Total reviews:      {s.get('total_reviews')}")

        cats = s.get("category_distribution") or []
        if cats:
            print(f"  Top categories:")
            for c in cats[:5]:
                print(f"    {c['category']:20} {c['count']}")

        top = s.get("top_3_by_reviews") or []
        if top:
            print(f"  Bestsellers:")
            for t in top:
                print(f"    {t.get('title', '')[:50]:50} "
                      f"({t.get('reviewCount')} reviews, "
                      f"{t.get('averageRating')}⭐)")


if __name__ == "__main__":
    main()
