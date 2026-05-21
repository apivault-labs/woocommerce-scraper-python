"""Exception classes for the WooCommerce Scraper SDK."""


class WooCommerceScraperError(Exception):
    """Base exception for all SDK errors."""


class AuthenticationError(WooCommerceScraperError):
    """Raised when the Apify API token is missing or invalid."""


class ActorRunError(WooCommerceScraperError):
    """Raised when the actor run fails on Apify infrastructure."""


class ActorTimeoutError(WooCommerceScraperError):
    """Raised when the actor run does not finish within the allowed timeout."""
