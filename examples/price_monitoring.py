"""
Track price changes for a list of WooCommerce stores over time.

Run on a schedule (cron, GitHub Actions). Saves snapshots to a local JSON
and reports diffs between runs:
- Price changes per product
- New products added
- Products that went on sale / off sale

    export APIFY_API_TOKEN=apify_api_xxxxxx
    python examples/price_monitoring.py
"""

import json
from pathlib import Path

from woocommerce_scraper import WooCommerceScraperClient


WATCH_STORES = [
    "https://woocommerce.com",
    # Add more stores
]
SNAPSHOT_FILE = Path("price_monitor_snapshot.json")


def index_by_id(records: list[dict]) -> dict[str, dict]:
    return {str(r.get("productId")): r for r in records if r.get("productId")}


def main() -> None:
    client = WooCommerceScraperClient(timeout=1800)
    new = []
    for store in WATCH_STORES:
        new.extend(client.analyze_store(store, max_products=200))

    new_idx = index_by_id(new)

    if SNAPSHOT_FILE.exists():
        old_records = json.loads(SNAPSHOT_FILE.read_text(encoding="utf-8"))
        old_idx = index_by_id(old_records)
    else:
        old_idx = {}

    print(f"\nTracking {len(new_idx)} products "
          f"(snapshot: {SNAPSHOT_FILE})\n")

    if not old_idx:
        print("(first run, no diff)")
    else:
        # Price changes
        for pid, new_p in new_idx.items():
            old_p = old_idx.get(pid)
            if not old_p:
                print(f"  + NEW: {new_p.get('title')} "
                      f"@ {new_p.get('price')} {new_p.get('currency')}")
                continue
            old_price = (old_p.get("price") or "").strip()
            new_price = (new_p.get("price") or "").strip()
            if old_price and new_price and old_price != new_price:
                print(f"  ~ PRICE: {new_p.get('title')[:40]:40} "
                      f"{old_price} → {new_price}")
            old_sale = old_p.get("onSale", False)
            new_sale = new_p.get("onSale", False)
            if not old_sale and new_sale:
                disc = new_p.get("discountPct", "?")
                print(f"  + SALE: {new_p.get('title')[:40]:40} "
                      f"now {disc}% off")
            elif old_sale and not new_sale:
                print(f"  - SALE ENDED: {new_p.get('title')[:40]}")

        # Removed products
        for pid in old_idx:
            if pid not in new_idx:
                print(f"  - REMOVED: {old_idx[pid].get('title')}")

    SNAPSHOT_FILE.write_text(json.dumps(new, indent=2), encoding="utf-8")
    print(f"\nSnapshot saved → {SNAPSHOT_FILE}")


if __name__ == "__main__":
    main()
