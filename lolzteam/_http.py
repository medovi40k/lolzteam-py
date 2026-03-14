"""
lolzteam._http
~~~~~~~~~~~~~~
Core HTTP transport layer supporting sync (requests) and async (httpx)
with automatic retry on 429 / 502 / 503 and proxy support.
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

logger = logging.getLogger("lolzteam")

# ── Retryable status codes ──────────────────────────────────────────────────
RETRY_STATUSES = {429, 502, 503}
DEFAULT_RETRY_COUNT = 5
DEFAULT_RETRY_BACKOFF = 1.0   # seconds between retries (doubles each time)
DEFAULT_TIMEOUT = 30.0

# ── Token header ────────────────────────────────────────────────────────────
AUTH_HEADER = "Authorization"


class LolzteamHTTPError(Exception):
    """Raised when the API returns a non-2xx response that is not retried."""

    def __init__(self, status_code: int, response_body: Any) -> None:
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(f"HTTP {status_code}: {response_body}")


class RateLimitError(LolzteamHTTPError):
    """Raised when 429 is received and max retries are exhausted."""


# ── Sync client ─────────────────────────────────────────────────────────────
class SyncHTTPClient:
    """
    Thin wrapper around *requests* for synchronous API calls.

    :param token:        Bearer token.
    :param base_url:     API base URL (no trailing slash).
    :param proxy:        Proxy URL, e.g. ``socks5://user:pass@host:port``.
    :param timeout:      Request timeout in seconds.
    :param max_retries:  How many times to retry on transient errors.
    :param language:     ``ru`` or ``en`` — sent as ``Accept-Language`` header.
    """

    def __init__(
        self,
        token: str,
        base_url: str,
        proxy: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_RETRY_COUNT,
        language: str = "en",
    ) -> None:
        try:
            import requests  # type: ignore[import]
        except ImportError as exc:
            raise ImportError(
                "The 'requests' package is required for sync usage. "
                "Install it with: pip install requests"
            ) from exc

        self._session = requests.Session()
        self._session.headers.update(
            {
                AUTH_HEADER: f"Bearer {token}",
                "Accept-Language": language,
            }
        )
        if proxy:
            self._session.proxies = {"http": proxy, "https": proxy}

        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._max_retries = max_retries

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        use_json: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        url = self._base_url + path
        # Strip None values
        params = {k: v for k, v in (params or {}).items() if v is not None}
        body = {k: v for k, v in (json or {}).items() if v is not None} or None

        backoff = DEFAULT_RETRY_BACKOFF
        for attempt in range(self._max_retries + 1):
            logger.debug("→ %s %s (attempt %d)", method, url, attempt + 1)
            resp = self._session.request(
                method,
                url,
                params=params or None,
                json=body if use_json else None,
                data=body if not use_json else None,
                timeout=self._timeout,
                **kwargs,
            )
            if resp.status_code in RETRY_STATUSES and attempt < self._max_retries:
                wait = _parse_retry_after(resp.headers.get("Retry-After")) or backoff
                logger.warning(
                    "⚠ %s %s — status %d, retrying in %.1fs …",
                    method,
                    url,
                    resp.status_code,
                    wait,
                )
                time.sleep(wait)
                backoff = min(backoff * 2, 60)
                continue

            try:
                body = resp.json()
            except Exception:
                body = resp.text

            if not resp.ok:
                if resp.status_code == 429:
                    raise RateLimitError(resp.status_code, body)
                raise LolzteamHTTPError(resp.status_code, body)

            logger.debug("← %d %s", resp.status_code, url)
            return body  # type: ignore[return-value]

        raise RateLimitError(429, "Max retries exceeded")

    def close(self) -> None:
        self._session.close()

    def __enter__(self) -> SyncHTTPClient:
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()


# ── Async client ─────────────────────────────────────────────────────────────
class AsyncHTTPClient:
    """
    Thin wrapper around *httpx* for async API calls.

    Same parameters as :class:`SyncHTTPClient`.
    """

    def __init__(
        self,
        token: str,
        base_url: str,
        proxy: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_RETRY_COUNT,
        language: str = "en",
    ) -> None:
        try:
            import httpx  # type: ignore[import]
        except ImportError as exc:
            raise ImportError(
                "The 'httpx' package is required for async usage. "
                "Install it with: pip install httpx"
            ) from exc

        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._max_retries = max_retries

        headers = {
            AUTH_HEADER: f"Bearer {token}",
            "Accept-Language": language,
        }

        kwargs: dict[str, Any] = {
            "headers": headers,
            "timeout": timeout,
        }
        if proxy:
            # httpx >= 0.23 uses `proxy=` (single string).
            # httpx <  0.23 uses `proxies=`.
            # For SOCKS5, also install: pip install "httpx[socks]"
            _ver = tuple(int(x) for x in httpx.__version__.split(".")[:2])
            if _ver >= (0, 23):
                kwargs["proxy"] = proxy
            else:
                kwargs["proxies"] = proxy

        self._client = httpx.AsyncClient(**kwargs)

    async def request_async(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        use_json: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        url = self._base_url + path
        params = {k: v for k, v in (params or {}).items() if v is not None}
        body = {k: v for k, v in (json or {}).items() if v is not None} or None

        backoff = DEFAULT_RETRY_BACKOFF
        for attempt in range(self._max_retries + 1):
            logger.debug("→ %s %s (attempt %d)", method, url, attempt + 1)
            resp = await self._client.request(
                method,
                url,
                params=params or None,
                json=body if use_json else None,
                data=body if not use_json else None,
                **kwargs,
            )
            if resp.status_code in RETRY_STATUSES and attempt < self._max_retries:
                wait = _parse_retry_after(resp.headers.get("Retry-After")) or backoff
                logger.warning(
                    "⚠ %s %s — status %d, retrying in %.1fs …",
                    method,
                    url,
                    resp.status_code,
                    wait,
                )
                await asyncio.sleep(wait)
                backoff = min(backoff * 2, 60)
                continue

            try:
                body = resp.json()
            except Exception:
                body = resp.text

            if not resp.is_success:
                if resp.status_code == 429:
                    raise RateLimitError(resp.status_code, body)
                raise LolzteamHTTPError(resp.status_code, body)

            logger.debug("← %d %s", resp.status_code, url)
            return body  # type: ignore[return-value]

        raise RateLimitError(429, "Max retries exceeded")

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> AsyncHTTPClient:
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.aclose()


# ── Unified dual-mode transport ─────────────────────────────────────────────
class Transport:
    """
    Dual-mode transport: delegates ``request`` to :class:`SyncHTTPClient`
    and ``request_async`` to :class:`AsyncHTTPClient`.

    Both clients are created lazily on first use.
    """

    def __init__(
        self,
        token: str,
        base_url: str,
        proxy: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_RETRY_COUNT,
        language: str = "en",
    ) -> None:
        self._kwargs = dict(
            token=token,
            base_url=base_url,
            proxy=proxy,
            timeout=timeout,
            max_retries=max_retries,
            language=language,
        )
        self._sync: SyncHTTPClient | None = None
        self._async: AsyncHTTPClient | None = None

    @property
    def sync(self) -> SyncHTTPClient:
        if self._sync is None:
            self._sync = SyncHTTPClient(**self._kwargs)
        return self._sync

    @property
    def asynchronous(self) -> AsyncHTTPClient:
        if self._async is None:
            self._async = AsyncHTTPClient(**self._kwargs)
        return self._async

    def request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        return self.sync.request(method, path, **kwargs)

    async def request_async(
        self, method: str, path: str, **kwargs: Any
    ) -> dict[str, Any]:
        return await self.asynchronous.request_async(method, path, **kwargs)

    def close(self) -> None:
        if self._sync:
            self._sync.close()

    async def aclose(self) -> None:
        if self._async:
            await self._async.aclose()


# ── Helpers ──────────────────────────────────────────────────────────────────
def _parse_retry_after(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None
