"""
tests/test_http.py
~~~~~~~~~~~~~~~~~~
Unit tests for the HTTP transport layer (retry, proxy, error handling).
Uses unittest.mock — no real network calls.
"""

from __future__ import annotations

import time
from typing import Any
from unittest.mock import MagicMock, patch, call
import pytest

from lolzteam._http import (
    SyncHTTPClient,
    LolzteamHTTPError,
    RateLimitError,
    Transport,
    _parse_retry_after,
)


# ── helpers ──────────────────────────────────────────────────────────────────
def _mock_response(status_code: int, json_body: Any = None, headers: dict | None = None):
    resp = MagicMock()
    resp.status_code = status_code
    resp.ok = 200 <= status_code < 300
    resp.headers = headers or {}
    resp.json.return_value = json_body or {}
    resp.text = str(json_body)
    return resp


# ── _parse_retry_after ───────────────────────────────────────────────────────
def test_parse_retry_after_none():
    assert _parse_retry_after(None) is None


def test_parse_retry_after_numeric():
    assert _parse_retry_after("3") == 3.0


def test_parse_retry_after_invalid():
    assert _parse_retry_after("Wed, 21 Oct 2025 07:28:00 GMT") is None


# ── SyncHTTPClient ────────────────────────────────────────────────────────────
class TestSyncHTTPClient:
    def _client(self, **kwargs):
        with patch("requests.Session"):
            return SyncHTTPClient(
                token="test_token",
                base_url="https://prod-api.lolz.live",
                max_retries=3,
                **kwargs,
            )

    def test_success_on_first_attempt(self):
        client = self._client()
        client._session.request.return_value = _mock_response(200, {"user": {"user_id": 1}})
        result = client.request("GET", "/users/me")
        assert result == {"user": {"user_id": 1}}

    def test_retries_on_429(self):
        client = self._client()
        # First two calls return 429, third succeeds
        client._session.request.side_effect = [
            _mock_response(429, {"error": "rate_limit"}),
            _mock_response(429, {"error": "rate_limit"}),
            _mock_response(200, {"ok": True}),
        ]
        with patch("time.sleep"):
            result = client.request("GET", "/posts")
        assert result == {"ok": True}
        assert client._session.request.call_count == 3

    def test_retries_on_502(self):
        client = self._client()
        client._session.request.side_effect = [
            _mock_response(502, {}),
            _mock_response(200, {"ok": True}),
        ]
        with patch("time.sleep"):
            result = client.request("GET", "/threads")
        assert result == {"ok": True}

    def test_retries_on_503(self):
        client = self._client()
        client._session.request.side_effect = [
            _mock_response(503, {}),
            _mock_response(200, {"data": "ok"}),
        ]
        with patch("time.sleep"):
            result = client.request("GET", "/forums")
        assert result == {"data": "ok"}

    def test_raises_rate_limit_after_max_retries(self):
        client = self._client()
        client._session.request.return_value = _mock_response(429, {"error": "rate_limit"})
        with patch("time.sleep"):
            with pytest.raises(RateLimitError):
                client.request("GET", "/users/me")

    def test_raises_http_error_on_4xx(self):
        client = self._client()
        client._session.request.return_value = _mock_response(403, {"error": "forbidden"})
        with pytest.raises(LolzteamHTTPError) as exc_info:
            client.request("GET", "/admin")
        assert exc_info.value.status_code == 403

    def test_raises_http_error_on_404(self):
        client = self._client()
        client._session.request.return_value = _mock_response(404, {"error": "not_found"})
        with pytest.raises(LolzteamHTTPError) as exc_info:
            client.request("GET", "/users/9999999")
        assert exc_info.value.status_code == 404

    def test_none_params_stripped(self):
        client = self._client()
        client._session.request.return_value = _mock_response(200, {})
        client.request("GET", "/threads", params={"forum_id": 1, "order": None})
        _, kwargs = client._session.request.call_args
        assert kwargs["params"] == {"forum_id": 1}

    def test_none_body_stripped(self):
        client = self._client()
        client._session.request.return_value = _mock_response(200, {})
        client.request(
            "POST",
            "/posts",
            json={"thread_id": 5, "post_body": "hello", "quote_post_id": None},
        )
        _, kwargs = client._session.request.call_args
        # Forum API uses form-encoded (data=), not json=
        assert kwargs["data"] == {"thread_id": 5, "post_body": "hello"}

    def test_proxy_passed_to_session(self):
        with patch("requests.Session") as mock_session_cls:
            mock_session = MagicMock()
            mock_session_cls.return_value = mock_session
            SyncHTTPClient(
                token="tok",
                base_url="https://prod-api.lolz.live",
                proxy="socks5://user:pass@127.0.0.1:1080",
            )
        assert mock_session.proxies == {
            "http": "socks5://user:pass@127.0.0.1:1080",
            "https": "socks5://user:pass@127.0.0.1:1080",
        }

    def test_proxy_http_with_auth(self):
        with patch("requests.Session") as mock_session_cls:
            mock_session = MagicMock()
            mock_session_cls.return_value = mock_session
            SyncHTTPClient(
                token="tok",
                base_url="https://prod-api.lolz.live",
                proxy="http://proxyuser:proxypass@10.0.0.1:8080",
            )
        assert mock_session.proxies["http"] == "http://proxyuser:proxypass@10.0.0.1:8080"
        assert mock_session.proxies["https"] == "http://proxyuser:proxypass@10.0.0.1:8080"

    def test_proxy_socks5h_with_auth(self):
        """socks5h routes DNS through the proxy too."""
        with patch("requests.Session") as mock_session_cls:
            mock_session = MagicMock()
            mock_session_cls.return_value = mock_session
            SyncHTTPClient(
                token="tok",
                base_url="https://prod-api.lolz.live",
                proxy="socks5h://user:pass@proxy.example.com:1080",
            )
        assert mock_session.proxies["https"].startswith("socks5h://")

    def test_no_proxy_sets_no_proxies(self):
        with patch("requests.Session") as mock_session_cls:
            mock_session = MagicMock()
            mock_session_cls.return_value = mock_session
            SyncHTTPClient(token="tok", base_url="https://prod-api.lolz.live")
        # proxies attribute should NOT be set when no proxy given
        assert not hasattr(mock_session, "proxies") or mock_session.proxies != {
            "http": None, "https": None
        }

    def test_retry_after_header_respected(self):
        client = self._client()
        client._session.request.side_effect = [
            _mock_response(429, {}, headers={"Retry-After": "2"}),
            _mock_response(200, {"ok": True}),
        ]
        sleep_calls = []
        with patch("time.sleep", side_effect=lambda s: sleep_calls.append(s)):
            client.request("GET", "/users/me")
        assert sleep_calls[0] == 2.0

    def test_auth_header_set(self):
        with patch("requests.Session") as mock_session_cls:
            mock_session = MagicMock()
            mock_session_cls.return_value = mock_session
            SyncHTTPClient(token="mytoken123", base_url="https://prod-api.lolz.live")
        mock_session.headers.update.assert_called_once()
        headers = mock_session.headers.update.call_args[0][0]
        assert headers["Authorization"] == "Bearer mytoken123"

    def test_language_header(self):
        with patch("requests.Session") as mock_session_cls:
            mock_session = MagicMock()
            mock_session_cls.return_value = mock_session
            SyncHTTPClient(token="t", base_url="https://x.com", language="ru")
        headers = mock_session.headers.update.call_args[0][0]
        assert headers["Accept-Language"] == "ru"

    def test_context_manager_closes(self):
        client = self._client()
        with client:
            pass
        client._session.close.assert_called_once()


# ── Transport ────────────────────────────────────────────────────────────────
class TestTransport:
    def test_sync_lazy_init(self):
        t = Transport(token="t", base_url="https://prod-api.lolz.live")
        assert t._sync is None
        with patch("requests.Session"):
            _ = t.sync
        assert t._sync is not None

    def test_request_delegates_to_sync(self):
        t = Transport(token="t", base_url="https://prod-api.lolz.live")
        mock_client = MagicMock()
        mock_client.request.return_value = {"ok": True}
        t._sync = mock_client
        result = t.request("GET", "/users/me")
        mock_client.request.assert_called_once_with("GET", "/users/me")
        assert result == {"ok": True}


# ── Async tests ───────────────────────────────────────────────────────────────
class TestAsyncHTTPClient:
    @pytest.mark.asyncio
    async def test_async_success(self):
        try:
            import httpx
        except ImportError:
            pytest.skip("httpx not installed")

        from lolzteam._http import AsyncHTTPClient

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.is_success = True
        mock_resp.json.return_value = {"user": {"user_id": 42}}
        mock_resp.text = ""

        with patch("httpx.AsyncClient") as mock_cls:
            mock_httpx = MagicMock()
            mock_cls.return_value = mock_httpx

            import asyncio

            async def fake_request(*args, **kwargs):
                return mock_resp

            mock_httpx.request = fake_request

            client = AsyncHTTPClient(token="tok", base_url="https://prod-api.lolz.live")
            client._client = mock_httpx
            result = await client.request_async("GET", "/users/me")
            assert result["user"]["user_id"] == 42

    @pytest.mark.asyncio
    async def test_async_retries_on_429(self):
        try:
            import httpx
        except ImportError:
            pytest.skip("httpx not installed")

        from lolzteam._http import AsyncHTTPClient

        resp_429 = MagicMock()
        resp_429.status_code = 429
        resp_429.is_success = False
        resp_429.json.return_value = {}
        resp_429.headers = {}
        resp_429.text = ""

        resp_200 = MagicMock()
        resp_200.status_code = 200
        resp_200.is_success = True
        resp_200.json.return_value = {"ok": True}
        resp_200.text = ""

        responses = [resp_429, resp_200]
        idx = 0

        async def fake_request(*args, **kwargs):
            nonlocal idx
            r = responses[idx]
            idx += 1
            return r

        with patch("httpx.AsyncClient"):
            client = AsyncHTTPClient(
                token="tok", base_url="https://prod-api.lolz.live", max_retries=3
            )
            client._client = MagicMock()
            client._client.request = fake_request

            with patch("asyncio.sleep"):
                result = await client.request_async("GET", "/posts")
            assert result == {"ok": True}
