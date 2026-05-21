# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] — 2026-05-22

### Added
- Initial release of the Python SDK
- `WooCommerceScraperClient` with synchronous `analyze()`, `analyze_one()`,
  `analyze_store()`, and `snapshot()` methods
- Support for all input parameters of the underlying actor:
  `enrichVariants`, `extractReviewsText`, `convertToCurrency`,
  `exportFormat` (default / shopify-csv / google-merchant / custom-csv / catalog-snapshot)
- 7 example scripts: quickstart, catalog snapshot, Shopify migration,
  Google Merchant feed, competitor compare, price monitoring, niche analysis
- MIT license
