"""
tests/test_http_extra.py
~~~~~~~~~~~~~~~~~~~~~~~~~
Covers remaining uncovered branches in _http.py:
  - AsyncHTTPClient proxy version detection
  - Transport lazy async init + aclose
  - RateLimitError / LolzteamHTTPError repr
  - models fallback (dataclass path when pydantic absent)
"""

from __future__ import annotations

import sys
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock

from lolzteam._http import (
    Transport,
    LolzteamHTTPError,
    RateLimitError,
    AsyncHTTPClient,
    SyncHTTPClient,
    _parse_retry_after,
)


# ── Error classes ─────────────────────────────────────────────────────────────

class TestErrorClasses:
    def test_lolzteam_http_error_attrs(self):
        e = LolzteamHTTPError(404, {"error": "not_found"})
        assert e.status_code == 404
        assert e.response_body == {"error": "not_found"}
        assert "404" in str(e)

    def test_rate_limit_error_is_http_error(self):
        e = RateLimitError(429, {"error": "rate_limit"})
        assert isinstance(e, LolzteamHTTPError)
        assert e.status_code == 429

    def test_rate_limit_error_str(self):
        e = RateLimitError(429, "Too many requests")
        assert "429" in str(e)


# ── Transport async lazy init + aclose ───────────────────────────────────────

class TestTransportAsync:
    def test_async_lazy_init(self):
        t = Transport(token="t", base_url="https://prod-api.lolz.live")
        assert t._async is None

    @pytest.mark.asyncio
    async def test_aclose_when_no_async_client(self):
        """aclose() should be safe even if async client was never created."""
        t = Transport(token="t", base_url="https://prod-api.lolz.live")
        # Should not raise
        await t.aclose()

    @pytest.mark.asyncio
    async def test_aclose_calls_client_aclose(self):
        t = Transport(token="t", base_url="https://prod-api.lolz.live")
        mock_async = MagicMock()
        mock_async.aclose = AsyncMock()
        t._async = mock_async
        await t.aclose()
        mock_async.aclose.assert_awaited_once()

    def test_close_when_no_sync_client(self):
        """close() should be safe even if sync client was never created."""
        t = Transport(token="t", base_url="https://prod-api.lolz.live")
        t.close()  # should not raise

    def test_close_calls_sync_close(self):
        t = Transport(token="t", base_url="https://prod-api.lolz.live")
        mock_sync = MagicMock()
        t._sync = mock_sync
        t.close()
        mock_sync.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_request_async_delegates_to_async_client(self):
        t = Transport(token="t", base_url="https://prod-api.lolz.live")
        mock_async = MagicMock()
        mock_async.request_async = AsyncMock(return_value={"ok": True})
        t._async = mock_async
        result = await t.request_async("GET", "/users/me")
        assert result == {"ok": True}
        mock_async.request_async.assert_awaited_once_with("GET", "/users/me")


# ── AsyncHTTPClient proxy version detection ──────────────────────────────────

class TestAsyncHTTPClientProxy:
    """Test that proxy= vs proxies= is chosen based on httpx version."""

    def _make_client(self, proxy: str, httpx_version: str):
        """Create AsyncHTTPClient with a mocked httpx version."""
        import httpx as real_httpx

        with patch.object(type(real_httpx), "__version__", httpx_version, create=True):
            with patch("httpx.AsyncClient") as mock_cls:
                mock_instance = MagicMock()
                mock_cls.return_value = mock_instance
                # Patch httpx.__version__ at module attribute level
                with patch("httpx.__version__", httpx_version):
                    client = AsyncHTTPClient(
                        token="tok",
                        base_url="https://prod-api.lolz.live",
                        proxy=proxy,
                    )
                return mock_cls, client

    def test_new_httpx_uses_proxy_kwarg(self):
        """httpx >= 0.23 should use proxy= keyword."""
        try:
            import httpx
        except ImportError:
            pytest.skip("httpx not installed")

        captured_kwargs = {}

        with patch("httpx.AsyncClient") as mock_cls:
            with patch("httpx.__version__", "0.24.0"):
                mock_cls.side_effect = lambda **kw: captured_kwargs.update(kw) or MagicMock()
                AsyncHTTPClient(
                    token="tok",
                    base_url="https://prod-api.lolz.live",
                    proxy="socks5://user:pass@127.0.0.1:1080",
                )
        assert "proxy" in captured_kwargs
        assert captured_kwargs["proxy"] == "socks5://user:pass@127.0.0.1:1080"

    def test_old_httpx_uses_proxies_kwarg(self):
        """httpx < 0.23 should use proxies= keyword."""
        try:
            import httpx
        except ImportError:
            pytest.skip("httpx not installed")

        captured_kwargs = {}

        with patch("httpx.AsyncClient") as mock_cls:
            with patch("httpx.__version__", "0.22.0"):
                mock_cls.side_effect = lambda **kw: captured_kwargs.update(kw) or MagicMock()
                AsyncHTTPClient(
                    token="tok",
                    base_url="https://prod-api.lolz.live",
                    proxy="http://user:pass@127.0.0.1:8080",
                )
        assert "proxies" in captured_kwargs

    def test_no_proxy_no_proxy_kwarg(self):
        """Without proxy, neither proxy= nor proxies= should be set."""
        try:
            import httpx
        except ImportError:
            pytest.skip("httpx not installed")

        captured_kwargs = {}

        with patch("httpx.AsyncClient") as mock_cls:
            mock_cls.side_effect = lambda **kw: captured_kwargs.update(kw) or MagicMock()
            AsyncHTTPClient(token="tok", base_url="https://prod-api.lolz.live")

        assert "proxy" not in captured_kwargs
        assert "proxies" not in captured_kwargs


# ── AsyncHTTPClient 503 retry ─────────────────────────────────────────────────

class TestAsyncRetries:
    @pytest.mark.asyncio
    async def test_retries_on_503(self):
        try:
            import httpx
        except ImportError:
            pytest.skip("httpx not installed")

        resp_503 = MagicMock()
        resp_503.status_code = 503
        resp_503.is_success = False
        resp_503.json.return_value = {}
        resp_503.headers = {}
        resp_503.text = ""

        resp_200 = MagicMock()
        resp_200.status_code = 200
        resp_200.is_success = True
        resp_200.json.return_value = {"ok": True}
        resp_200.text = ""

        calls = [resp_503, resp_200]
        idx = 0

        async def fake_request(*args, **kwargs):
            nonlocal idx
            r = calls[idx]; idx += 1
            return r

        with patch("httpx.AsyncClient"):
            client = AsyncHTTPClient(
                token="tok", base_url="https://prod-api.lolz.live", max_retries=3
            )
            client._client = MagicMock()
            client._client.request = fake_request

            with patch("asyncio.sleep"):
                result = await client.request_async("GET", "/forums")
        assert result == {"ok": True}

    @pytest.mark.asyncio
    async def test_raises_rate_limit_after_max_retries(self):
        try:
            import httpx
        except ImportError:
            pytest.skip("httpx not installed")

        resp_429 = MagicMock()
        resp_429.status_code = 429
        resp_429.is_success = False
        resp_429.json.return_value = {}
        resp_429.headers = {}
        resp_429.text = ""

        async def fake_request(*args, **kwargs):
            return resp_429

        with patch("httpx.AsyncClient"):
            client = AsyncHTTPClient(
                token="tok", base_url="https://prod-api.lolz.live", max_retries=2
            )
            client._client = MagicMock()
            client._client.request = fake_request

            with patch("asyncio.sleep"):
                with pytest.raises(RateLimitError):
                    await client.request_async("GET", "/posts")

    @pytest.mark.asyncio
    async def test_raises_http_error_on_404(self):
        try:
            import httpx
        except ImportError:
            pytest.skip("httpx not installed")

        resp = MagicMock()
        resp.status_code = 404
        resp.is_success = False
        resp.json.return_value = {"error": "not_found"}
        resp.text = ""

        async def fake_request(*args, **kwargs):
            return resp

        with patch("httpx.AsyncClient"):
            client = AsyncHTTPClient(token="tok", base_url="https://prod-api.lolz.live")
            client._client = MagicMock()
            client._client.request = fake_request

            with pytest.raises(LolzteamHTTPError) as exc_info:
                await client.request_async("GET", "/missing")
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        try:
            import httpx
        except ImportError:
            pytest.skip("httpx not installed")

        with patch("httpx.AsyncClient") as mock_cls:
            mock_instance = MagicMock()
            mock_instance.aclose = AsyncMock()
            mock_cls.return_value = mock_instance

            client = AsyncHTTPClient(token="tok", base_url="https://prod-api.lolz.live")
            async with client:
                pass
            mock_instance.aclose.assert_awaited_once()


# ── Models fallback (dataclass path) ──────────────────────────────────────────

class TestModelsFallback:
    """Test that models work when pydantic is NOT installed (dataclass path)."""

    def _reload_models_without_pydantic(self, module_name: str):
        """Temporarily hide pydantic and reload the models module."""
        import importlib
        # Save original module
        orig_pydantic = sys.modules.get("pydantic")
        # Block pydantic import
        sys.modules["pydantic"] = None  # type: ignore[assignment]
        # Remove cached module so it reimports
        if module_name in sys.modules:
            del sys.modules[module_name]
        try:
            mod = importlib.import_module(module_name)
            return mod
        finally:
            # Restore
            if orig_pydantic is not None:
                sys.modules["pydantic"] = orig_pydantic
            else:
                sys.modules.pop("pydantic", None)
            if module_name in sys.modules:
                del sys.modules[module_name]

    def test_forum_models_fallback(self):
        mod = self._reload_models_without_pydantic("lolzteam.models.forum")
        # These should be importable even without pydantic
        assert hasattr(mod, "User")
        assert hasattr(mod, "Thread")
        assert hasattr(mod, "Post")
        assert hasattr(mod, "Forum")
        assert hasattr(mod, "Category")

    def test_market_models_fallback(self):
        mod = self._reload_models_without_pydantic("lolzteam.models.market")
        assert hasattr(mod, "Item")
        assert hasattr(mod, "Payment")
        assert hasattr(mod, "Balance")

    def test_forum_user_dataclass(self):
        mod = self._reload_models_without_pydantic("lolzteam.models.forum")
        u = mod.User(user_id=1, username="test")
        assert u.user_id == 1
        assert u.username == "test"

    def test_forum_thread_dataclass(self):
        mod = self._reload_models_without_pydantic("lolzteam.models.forum")
        t = mod.Thread(thread_id=10, thread_title="Hello")
        assert t.thread_id == 10

    def test_market_item_dataclass(self):
        mod = self._reload_models_without_pydantic("lolzteam.models.market")
        item = mod.Item(item_id=99)
        assert item.item_id == 99

    def test_market_balance_dataclass(self):
        mod = self._reload_models_without_pydantic("lolzteam.models.market")
        b = mod.Balance(balance=1000.0, currency="rub")
        assert b.balance == 1000.0
