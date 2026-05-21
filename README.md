# WooCommerce Scraper — Python SDK

> **Full catalog extraction for any WooCommerce store: variants, reviews, brand auto-detection, FX conversion, Shopify CSV export, Google Merchant feed and one-record catalog snapshots — via the official public Store API.**

Python client for the [WooCommerce Scraper Apify Actor](https://apify.com/apivault_labs/woocommerce-product-scraper) — turn any of the **~30% of e-commerce sites running WooCommerce** into structured data using only public endpoints.

[![Apify Actor](https://img.shields.io/badge/Apify-Actor-blue?logo=apify)](https://apify.com/apivault_labs/woocommerce-product-scraper)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![PyPI-friendly](https://img.shields.io/badge/install-pip-success)](#installation)

---

## What it does

For any WooCommerce store URL, this actor returns up to **39 fields per product** — or one rich aggregate record per store (catalog-snapshot mode).

A direct, pay-per-use alternative to:
- WooCommerce REST API (requires authenticated keys, store-by-store config)
- Generic e-commerce scrapers (10–100× slower, anti-bot fragile)
- Manual catalog migration tools (charge $5–50 per store, one-time only)

**Pricing:** $0.003 per product (catalog snapshot is one record = $0.003 per store).

---

## Quick start

```python
from woocommerce_scraper import WooCommerceScraperClient

client = WooCommerceScraperClient(api_token="apify_api_xxxxxx")

# Pull 100 products with full intelligence
products = client.analyze_store(
    "https://store.com",
    max_products=100,
    enrich_variants=True,
)

for p in products[:3]:
    print(f"{p['title']}: {p['price']} {p['currency']} "
          f"(rank #{p['popularityRank']}, "
          f"score {p['productIntelligenceScore']}, "
          f"{p['autoCategory']})")
```

Output:
```
Awesome Hoodie: 59.00 USD (rank #1, score 87, apparel)
Premium T-Shirt: 29.00 USD (rank #2, score 75, apparel)
Designer Sneakers: 129.00 USD (rank #3, score 92, footwear)
```

---

## Installation

```bash
pip install git+https://github.com/apivault-labs/woocommerce-scraper-python.git
```

Or clone and use directly:

```bash
git clone https://github.com/apivault-labs/woocommerce-scraper-python.git
cd woocommerce-scraper-python
pip install -r requirements.txt
```

Requires Python 3.9+ and the [`requests`](https://pypi.org/project/requests/) library.

---

## Get your API token (free)

1. Sign up at [apify.com](https://apify.com) — free tier includes $5 monthly credits, no card required
2. Go to [Account → Integrations](https://console.apify.com/account/integrations)
3. Copy your Personal API token

```bash
export APIFY_API_TOKEN=apify_api_xxxxxxxxxxxxxxxxxxxxxxxx
```

Or pass it explicitly:

```python
client = WooCommerceScraperClient(api_token="apify_api_xxxxxx")
```

---

## What you get

### 📦 Per-product fields (39 total)
**Core:** `productId`, `productUrl`, `slug`, `title`, `description`, `shortDescription`, `sku`, `images`, `mainImage`, `imagesCount`, `categories`, `categorySlugs`, `tags`, `attributes`, `type`, `parentId`, `hasOptions`, `isPurchasable`, `addToCartUrl`, `variationsCount`

**Pricing:** `price`, `regularPrice`, `salePrice`, `currency`, `onSale`, `discountPct`, `priceUsd` / `priceEur` / etc (when `convert_to_currency` is set)

**Stock & ratings:** `inStock`, `stockStatus`, `lowStock`, `averageRating`, `reviewCount`

**🆕 Auto-extracted intelligence:**
- `brand` — extracted from product attributes / meta_data
- `autoCategory` — apparel / footwear / accessories / beauty / electronics / home / food / toys / books / sports / pets / baby / tools / art / office
- `isNewArrival` — true if added in last 30 days
- `dateCreated` — ISO 8601 timestamp
- `popularityRank` — within-store rank by review count (1 = most reviewed)
- `productIntelligenceScore` — 0–100 listing quality heuristic
- `relatedProductIds` — cross-sell graph (when `enrich_variants: True`)

**Optional enrichment:**
- `variations[]` — full variant prices, stock, attributes (set `enrich_variants: True`)
- `reviews[]` — review text + reviewer info (set `extract_reviews_text: True`)

### 📊 Catalog snapshot fields (one record per store)
- `product_count`, `currency`, `price_min`, `price_max`, `price_median`, `aov_estimate`
- `products_on_sale_pct`, `avg_discount_pct`, `in_stock_pct`
- `new_arrivals_30d`, `new_arrivals_pct`
- `brands_count`, `top_brands[]`, `category_distribution[]`
- `avg_intelligence_score`, `max_intelligence_score`, `premium_listings_pct`
- `total_reviews`, `catalog_avg_rating`
- `top_3_by_reviews[]`

---

## Examples

See [`examples/`](examples) for full code:

| File | What it does |
|---|---|
| [`quickstart.py`](examples/quickstart.py) | Pull products from a single store |
| [`catalog_snapshot.py`](examples/catalog_snapshot.py) | One aggregate record per store (competitor monitoring at scale) |
| [`shopify_migration.py`](examples/shopify_migration.py) | Export WooCommerce → Shopify CSV |
| [`google_merchant_feed.py`](examples/google_merchant_feed.py) | Generate Google Shopping product feed |
| [`competitor_compare.py`](examples/competitor_compare.py) | Side-by-side competitor catalog comparison |
| [`price_monitoring.py`](examples/price_monitoring.py) | Track price changes over time |
| [`niche_analysis.py`](examples/niche_analysis.py) | Aggregate niche stats from many stores |

---

## API reference

### `WooCommerceScraperClient(api_token=None, timeout=600)`

| Param | Type | Description |
|---|---|---|
| `api_token` | `str` | Apify API token. Falls back to `APIFY_API_TOKEN` env var. |
| `timeout` | `int` | Max seconds to wait for an actor run to finish. Default 600. |

### `client.analyze(store_urls, **kwargs)`

Most flexible entry point — accepts a list of stores, products, or mixed.

| Param | Type | Default | Description |
|---|---|---|---|
| `store_urls` | `list[str]` | required | Store domains, product URLs, or bare domains |
| `max_products` | `int` | 250 | Per-store cap (0 = unlimited) |
| `per_page` | `int` | 100 | API page size (WC max: 100) |
| `flatten_variants` | `bool` | False | One row per variant (auto-enables `enrich_variants`) |
| `enrich_variants` | `bool` | False | Second API call for full variant prices + related |
| `extract_reviews_text` | `bool` | False | Fetch review text per product |
| `reviews_per_product` | `int` | 5 | Number of reviews when `extract_reviews_text` is on |
| `export_format` | `str` | `default` | One of: `default`, `shopify-csv`, `shopify-csv-only`, `google-merchant`, `google-merchant-only`, `custom-csv`, `catalog-snapshot` |
| `custom_columns` | `list[str]` | `[]` | Column names for `custom-csv` mode |
| `convert_to_currency` | `str` | `""` | ISO code (`USD`, `EUR`...) — adds `priceXxx` field |
| `only_in_stock` | `bool` | False | Skip out-of-stock |
| `category` | `str` | `""` | Category slug filter |
| `max_concurrency` | `int` | 3 | Parallel store fetches |

Returns: `list[dict]` — one record per product (or per store in `catalog-snapshot` mode).

### `client.analyze_one(url, **kwargs)`
Convenience wrapper for a single product URL. Returns one `dict`.

### `client.analyze_store(store_url, **kwargs)`
Convenience for a whole-store run. Returns `list[dict]` of products.

### `client.snapshot(store_urls, **kwargs)`
Forces `export_format="catalog-snapshot"`. Returns one record per store.

### `client.estimate_cost(product_count)`
Returns USD cost for `product_count × $0.003`.

---

## Sample output

```json
{
  "success": true,
  "productId": 18734,
  "productUrl": "https://store.com/product/awesome-hoodie/",
  "title": "Awesome Hoodie",
  "price": "59.00",
  "regularPrice": "79.00",
  "currency": "USD",
  "priceEur": 54.21,
  "discountPct": 25.3,
  "onSale": true,
  "brand": "ApiVault Apparel",
  "autoCategory": "apparel",
  "isNewArrival": true,
  "popularityRank": 3,
  "productIntelligenceScore": 87,
  "imagesCount": 6,
  "averageRating": 4.7,
  "reviewCount": 128,
  "inStock": true,
  "variationsCount": 12,
  "relatedProductIds": "18735, 18736, 18737"
}
```

### Catalog snapshot output

```json
{
  "snapshot_type": "catalog",
  "domain": "store.com",
  "product_count": 487,
  "price_median": 89.00,
  "aov_estimate": 133.50,
  "products_on_sale_pct": 32.4,
  "avg_discount_pct": 18.5,
  "in_stock_pct": 87.2,
  "new_arrivals_30d": 42,
  "brands_count": 17,
  "top_brands": [{"brand": "Nike", "products": 89}],
  "category_distribution": [{"category": "apparel", "count": 220}],
  "avg_intelligence_score": 68.4,
  "premium_listings_pct": 41.2,
  "catalog_avg_rating": 4.42
}
```

---

## Use cases

### 🚀 WooCommerce → Shopify migration
```python
products = client.analyze(
    ["https://my-old-store.com"],
    max_products=0,  # all products
    export_format="shopify-csv-only",
)
```
Each row already has the right Shopify CSV columns (`Handle`, `Title`, `Body (HTML)`, `Variant SKU`, `Variant Price`, `Variant Compare At Price`, `Image Src`, `SEO Title`, `Vendor`, ...) — export the dataset as CSV and import into Shopify Admin → Products → Import.

### 📢 Google Shopping feed
```python
feed = client.analyze(
    ["https://store.com"],
    export_format="google-merchant-only",
    only_in_stock=True,
)
```
Pipe directly into Google Merchant Center.

### 📊 Competitor monitoring at scale
```python
snapshots = client.snapshot([
    "https://competitor1.com",
    "https://competitor2.com",
    "https://competitor3.com",
])
# 3 stores → 3 aggregate records with totals, brands, categories,
# discount %, AOV, premium-listings %, top-3 by reviews
```

### 💱 Multi-currency price normalization
```python
products = client.analyze(
    ["https://uk-store.com", "https://eu-store.com", "https://us-store.com"],
    convert_to_currency="USD",
)
# Each product gets `priceUsd` for fair cross-store comparison
```

### 🎯 Custom CSV
```python
products = client.analyze(
    ["https://store.com"],
    export_format="custom-csv",
    custom_columns=["productId", "title", "brand", "price", "popularityRank",
                    "autoCategory", "isNewArrival"],
)
```

---

## Pricing

Pay only for what you analyze:

| Volume | Cost |
|---|---|
| 1 product | $0.003 |
| 100 products | $0.30 |
| 1,000 products | $3.00 |
| 10,000 products | $30.00 |
| 100 catalog snapshots | $0.30 |

Free Apify tier includes ~$5 monthly credit — analyze ~1,500 products per month for free.

---

## How it works

All data comes from public WooCommerce endpoints — no auth, no proxies, no scraping:

1. `/wp-json/wc/store/v1/products` — paginated catalog listing
2. `/wp-json/wc/store/v1/products/{id}` — full variant data + `related_ids` (when `enrich_variants` is on)
3. `/wp-json/wc/store/v1/products/reviews?product_id={id}` — review text (when `extract_reviews_text` is on)
4. `open.er-api.com` — free live FX rates (when `convert_to_currency` is set)

Brand and category extraction happen on the actor side from product attributes, meta_data, title, and tags.

---

## FAQ

**Q: Will this work on every WooCommerce store?**
A: Every modern WC install (4.7+, ~95% of WooCommerce stores) exposes the Store API by default. A few stores disable it via security plugins — those return 404.

**Q: Is the Store API the same as the WooCommerce REST API?**
A: No. The Store API (`/wc/store/v1/`) is read-only and public. The classic REST API (`/wc/v3/`) requires authenticated consumer keys. We use the Store API, which is faster and needs no setup.

**Q: How does the Shopify CSV export compare to a paid migration tool?**
A: Comparable for catalog data (titles, prices, images, variants, SEO). Paid tools also migrate orders, customers, redirects, and reviews — those require admin API access we deliberately don't use.

**Q: Are variant prices in cents?**
A: WooCommerce returns minor units. The actor auto-formats to decimal strings (`59.00`).

**Q: How accurate is `autoCategory`?**
A: It's a heuristic matching ~80 patterns. ~85–95% accuracy on consumer goods. Best as a filter, not a single source of truth.

**Q: How accurate is `productIntelligenceScore`?**
A: A rank, not a verdict. Use it to surface top listings (>70) or flag thin ones (<30) — always sample-check.

---

## Related Apify actors

- [Shopify Product Scraper](https://apify.com/apivault_labs/shopify-product-scraper) — Shopify catalogs
- [Shopify Store Analyzer](https://apify.com/apivault_labs/shopify-store-analyzer) — full Shopify intelligence
- [WordPress Plugin Detector](https://apify.com/apivault_labs/wp-plugin-detector) — detect WP plugins
- [WordPress Plugins Scraper](https://apify.com/apivault_labs/wordpress-plugins-scraper) — 60K+ plugins directory

See [all actors by apivault_labs](https://apify.com/apivault_labs).

---

## License

MIT — see [LICENSE](LICENSE).

This client is open source. The underlying Apify actor is a paid service ($0.003/product, $0.003/snapshot).

---

## Keywords

`woocommerce-scraper` `woocommerce-api` `wp-json` `woocommerce-store-api` `wordpress-scraper` `ecommerce-scraper` `product-scraper` `catalog-scraper` `woocommerce-to-shopify` `shopify-migration` `shopify-csv-export` `google-merchant-feed` `google-shopping-feed` `competitor-intelligence` `price-monitoring` `web-scraping` `apify` `apify-actor` `python-sdk` `woocommerce-without-api-key` `wp-store-api` `dropshipping-research` `niche-analysis` `aov-estimator` `catalog-snapshot`
