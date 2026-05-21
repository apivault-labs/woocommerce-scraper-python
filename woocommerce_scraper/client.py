"""
WooCommerceScraperClient — synchronous wrapper around the Apify
``apivault_labs/woocommerce-product-scraper`` actor.

The actor handles all heavy work (HTTP, pagination, variant enrichment,
brand/category auto-extraction, FX conversion, export formats) on Apify
infrastructure. This client forwards inputs, polls until the run finishes,
then downloads the dataset.

Usage:

    from woocommerce_scraper import WooCommerceScraperClient

    client = WooCommerceScraperClient(api_token="apify_api_xxxxxx")

    # Whole-catalog scrape with full variant data
    products = client.analyze_store(
        "https://store.com",
        max_products=100,
        enrich_variants=True,
    )

    # Catalog snapshots for many stores
    snapshots = client.snapshot([
        "https://store1.com",
        "https://store2.com",
    ])
"""

from __future__ import annotations

import os
import time
from typing import Any, Iterable

import requests

from .exceptions import (
    ActorRunError,
    ActorTimeoutError,
    AuthenticationError,
    WooCommerceScraperError,
)


ACTOR_ID = "apivault_labs~woocommerce-product-scraper"
APIFY_API_BASE = "https://api.apify.com/v2"

TERMINAL_OK = {"SUCCEEDED"}
TERMINAL_FAIL = {"FAILED", "TIMED-OUT", "ABORTED"}

# All export formats the actor accepts
EXPORT_FORMATS = {
    "default", "shopify-csv", "shopify-csv-only",
    "google-merchant", "google-merchant-only",
    "custom-csv", "catalog-snapshot",
}


class WooCommerceScraperClient:
    """Synchronous client for the WooCommerce Scraper Apify actor.

    Parameters
    ----------
    api_token : str, optional
        Apify Personal API token. If omitted, falls back to the
        ``APIFY_API_TOKEN`` environment variable.
    timeout : int, optional
        Maximum seconds to wait for an actor run to finish. Default 600.
    poll_interval : float, optional
        Seconds between status polls. Default 3.
    base_url : str, optional
        Override the Apify API base URL (mostly for testing).
    """

    def __init__(
        self,
        api_token: str | None = None,
        timeout: int = 600,
        poll_interval: float = 3.0,
        base_url: str = APIFY_API_BASE,
    ):
        token = api_token or os.environ.get("APIFY_API_TOKEN")
        if not token:
            raise AuthenticationError(
                "Apify API token is required. Pass api_token='apify_api_...' "
                "or set the APIFY_API_TOKEN environment variable. "
                "Get a token at https://console.apify.com/account/integrations"
            )
        self._token = token
        self._timeout = int(timeout)
        self._poll_interval = float(poll_interval)
        self._base_url = base_url.rstrip("/")
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
            "User-Agent": "woocommerce-scraper-python/0.1.0",
        })

    # ------------------------------------------------------------------ public

    def analyze(
        self,
        store_urls: Iterable[str],
        *,
        max_products: int = 250,
        per_page: int = 100,
        flatten_variants: bool = False,
        enrich_variants: bool = False,
        extract_reviews_text: bool = False,
        reviews_per_product: int = 5,
        export_format: str = "default",
        custom_columns: list[str] | None = None,
        convert_to_currency: str = "",
        only_in_stock: bool = False,
        category: str = "",
        max_concurrency: int = 3,
        actor_timeout_secs: int = 300,
    ) -> list[dict[str, Any]]:
        """Run the actor and return the result records.

        See the README for the full output schema.
        """
        urls = [u for u in store_urls if u]
        if not urls:
            raise ValueError("store_urls must contain at least one non-empty URL")

        if export_format not in EXPORT_FORMATS:
            raise ValueError(
                f"export_format must be one of {sorted(EXPORT_FORMATS)}, "
                f"got {export_format!r}"
            )

        custom_columns_str = ",".join(custom_columns) if custom_columns else ""

        payload = {
            "storeUrls": list(urls),
            "maxProducts": int(max_products),
            "perPage": int(per_page),
            "flattenVariants": flatten_variants,
            "enrichVariants": enrich_variants,
            "extractReviewsText": extract_reviews_text,
            "reviewsPerProduct": int(reviews_per_product),
            "exportFormat": export_format,
            "customColumns": custom_columns_str,
            "convertToCurrency": convert_to_currency,
            "onlyInStock": only_in_stock,
            "category": category,
            "maxConcurrency": int(max_concurrency),
        }

        run_id = self._start_run(payload, actor_timeout_secs=actor_timeout_secs)
        run = self._wait_for_run(run_id)
        return self._fetch_dataset(run["defaultDatasetId"])

    def analyze_one(self, product_url: str, **kwargs: Any) -> dict[str, Any]:
        """Convenience wrapper for a single product URL.

        Pass a `https://store.com/product/<slug>/` URL.
        """
        results = self.analyze([product_url], **kwargs)
        if not results:
            raise ActorRunError(
                f"Actor returned no records for {product_url!r} — "
                "the URL might not be a valid WooCommerce product page."
            )
        return results[0]

    def analyze_store(self, store_url: str, **kwargs: Any) -> list[dict[str, Any]]:
        """Convenience wrapper for analyzing one store and returning all products."""
        return self.analyze([store_url], **kwargs)

    def snapshot(
        self,
        store_urls: Iterable[str],
        *,
        max_products: int = 0,
        max_concurrency: int = 3,
        only_in_stock: bool = False,
        category: str = "",
        actor_timeout_secs: int = 600,
    ) -> list[dict[str, Any]]:
        """Aggregate intelligence mode — one record per store.

        Returns one dict per store with totals, brands, categories,
        AOV estimate, intelligence score, top-3 by reviews, etc.
        """
        return self.analyze(
            store_urls,
            max_products=max_products,
            export_format="catalog-snapshot",
            max_concurrency=max_concurrency,
            only_in_stock=only_in_stock,
            category=category,
            actor_timeout_secs=actor_timeout_secs,
        )

    def estimate_cost(self, product_count: int) -> float:
        """Return estimated USD cost for `product_count × $0.003`."""
        return round(product_count * 0.003, 4)

    # ------------------------------------------------------------------ private

    def _start_run(self, payload: dict[str, Any], actor_timeout_secs: int) -> str:
        url = f"{self._base_url}/acts/{ACTOR_ID}/runs"
        params = {"timeout": int(actor_timeout_secs)}
        try:
            r = self._session.post(url, params=params, json=payload, timeout=30)
        except requests.RequestException as e:
            raise WooCommerceScraperError(f"Failed to start actor run: {e}") from e

        if r.status_code == 401:
            raise AuthenticationError(
                "Apify rejected the API token. Generate a new one at "
                "https://console.apify.com/account/integrations"
            )
        if r.status_code >= 400:
            raise ActorRunError(
                f"Apify returned HTTP {r.status_code} when starting run: {r.text[:300]}"
            )

        data = r.json().get("data") or {}
        run_id = data.get("id")
        if not run_id:
            raise ActorRunError(f"Apify response missing run id: {r.text[:300]}")
        return run_id

    def _wait_for_run(self, run_id: str) -> dict[str, Any]:
        url = f"{self._base_url}/actor-runs/{run_id}"
        deadline = time.time() + self._timeout
        while True:
            try:
                r = self._session.get(url, timeout=30)
            except requests.RequestException as e:
                raise WooCommerceScraperError(f"Failed to poll run status: {e}") from e

            if r.status_code >= 400:
                raise ActorRunError(
                    f"Apify returned HTTP {r.status_code} when polling run: {r.text[:300]}"
                )

            run = r.json().get("data") or {}
            status = run.get("status")
            if status in TERMINAL_OK:
                return run
            if status in TERMINAL_FAIL:
                raise ActorRunError(
                    f"Actor run {run_id} ended with status={status}: "
                    f"{run.get('statusMessage') or '(no message)'}"
                )

            if time.time() > deadline:
                raise ActorTimeoutError(
                    f"Actor run {run_id} did not finish within {self._timeout}s "
                    f"(last status={status}). Increase `timeout=` or fetch the dataset manually."
                )

            time.sleep(self._poll_interval)

    def _fetch_dataset(self, dataset_id: str) -> list[dict[str, Any]]:
        url = f"{self._base_url}/datasets/{dataset_id}/items"
        params = {"clean": "true", "format": "json"}
        try:
            r = self._session.get(url, params=params, timeout=120)
        except requests.RequestException as e:
            raise WooCommerceScraperError(f"Failed to download dataset: {e}") from e

        if r.status_code >= 400:
            raise ActorRunError(
                f"Apify returned HTTP {r.status_code} when fetching dataset: "
                f"{r.text[:300]}"
            )

        try:
            data = r.json()
        except ValueError as e:
            raise ActorRunError(f"Apify dataset is not valid JSON: {e}") from e

        if not isinstance(data, list):
            raise ActorRunError(
                f"Unexpected dataset payload (not a list): {type(data).__name__}"
            )
        return data
