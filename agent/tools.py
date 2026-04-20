import logging
import os
import time
from typing import List, Optional

import requests
from langchain_core.tools import tool

_logger = logging.getLogger(__name__)

# 2-week TTL in seconds
_CACHE_TTL_SECONDS = 14 * 24 * 60 * 60


class CommonItemsCache:
    """In-memory cache of common supermarket item names, refreshed every 2 weeks.

    The cache is populated by calling the ``GET /names`` REST endpoint on
    ``toto-ms-supermarket``.  An optional ``Authorization`` header can be
    supplied so that the request is authenticated.
    """

    def __init__(self) -> None:
        self._items: List[str] = []
        self._last_refresh: Optional[float] = None
        self._auth_header: Optional[str] = None

    def set_auth_header(self, auth_header: Optional[str]) -> None:
        """Update the authorization header used for REST calls."""
        self._auth_header = auth_header

    def _is_expired(self) -> bool:
        if self._last_refresh is None:
            return True
        return (time.time() - self._last_refresh) > _CACHE_TTL_SECONDS

    def refresh_if_needed(self) -> None:
        """Refresh the cache from the REST API if it is empty or expired."""
        if not self._is_expired():
            return

        supermarket_url = os.environ.get("SUPERMARKET_API_ENDPOINT")
        if not supermarket_url:
            return

        headers: dict = {}
        if self._auth_header:
            headers["Authorization"] = self._auth_header

        try:
            response = requests.get(
                f"{supermarket_url}/names", headers=headers, timeout=10
            )
            response.raise_for_status()

            data = response.json()
            if isinstance(data, list):
                self._items = data
            elif isinstance(data, dict):
                self._items = data.get("names", [])

            self._last_refresh = time.time()
        except Exception as exc:  # noqa: BLE001
            _logger.warning("Failed to refresh common items cache: %s", exc)

    def get_items(self) -> List[str]:
        """Return the cached list of common item names, refreshing if needed."""
        self.refresh_if_needed()
        return self._items


def create_get_common_items_tool(cache: CommonItemsCache):
    """Return a LangChain tool that serves common items from *cache*."""

    @tool
    def getCommonItems() -> List[str]:
        """Returns a list of common supermarket items.

        Use this tool to cross-reference the items that the user wants to add
        against known item names so that you can correct misspellings and pick
        the closest matching name before adding anything to the list.
        """
        return cache.get_items()

    return getCommonItems
