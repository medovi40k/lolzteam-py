"""
tests/test_clients.py
~~~~~~~~~~~~~~~~~~~~~
Unit tests for ForumClient and MarketClient — all network calls mocked.
"""
from __future__ import annotations
from unittest.mock import MagicMock, AsyncMock, patch
import pytest
from lolzteam import ForumClient, MarketClient


def _forum(**kwargs):
    with patch("requests.Session"):
        c = ForumClient(token="test_token", **kwargs)
    c._transport._sync = MagicMock()
    c._transport._sync.request.return_value = {}
    return c

def _market(**kwargs):
    with patch("requests.Session"):
        c = MarketClient(token="test_token", **kwargs)
    c._transport._sync = MagicMock()
    c._transport._sync.request.return_value = {}
    return c


# ── ForumClient ───────────────────────────────────────────────────────────────
class TestForumClient:
    def test_sections_exist(self):
        c = _forum()
        for s in ("categories","forums","users","threads","posts",
                  "profile_posts","conversations","notifications",
                  "search","tags","batch"):
            assert hasattr(c, s), f"missing section: {s}"

    def test_get_user(self):
        c = _forum()
        c._transport._sync.request.return_value = {"user": {"user_id": 42}}
        c.users.users_get(user_id=42)
        args = c._transport._sync.request.call_args[0]
        assert args[0] == "GET" and "42" in args[1]

    def test_get_me(self):
        c = _forum()
        c.users.users_me()
        assert "/users/me" in c._transport._sync.request.call_args[0][1]

    def test_create_thread(self):
        c = _forum()
        c.threads.threads_create(forum_id=1, post_body="B", title="Test thread title")
        assert c._transport._sync.request.call_args[0][0] == "POST"

    def test_create_post(self):
        c = _forum()
        c.posts.posts_create(thread_id=100, post_body="Reply")
        assert c._transport._sync.request.call_args[0][0] == "POST"

    def test_delete_thread(self):
        c = _forum()
        c.threads.threads_delete(thread_id=55)
        assert c._transport._sync.request.call_args[0][0] == "DELETE"

    def test_follow_user(self):
        c = _forum()
        c.users.users_follow(user_id=10)
        assert c._transport._sync.request.call_args[0][0] == "POST"

    def test_search_threads(self):
        c = _forum()
        c.search.search_threads(q="python")
        assert c._transport._sync.request.call_args[0][0] == "POST"

    def test_context_manager(self):
        with _forum() as c:
            c._transport._sync.request.return_value = {"ok": True}
            assert c.request("GET", "/forums") == {"ok": True}

    def test_raw_request(self):
        c = _forum()
        c._transport._sync.request.return_value = {"raw": True}
        assert c.request("GET", "/categories") == {"raw": True}

    def test_notifications_list(self):
        c = _forum()
        c.notifications.notifications_list()
        assert c._transport._sync.request.call_args[0][0] == "GET"

    def test_like_post(self):
        c = _forum()
        c.posts.posts_like(post_id=777)
        assert c._transport._sync.request.call_args[0][0] == "POST"

    def test_unlike_post(self):
        c = _forum()
        c.posts.posts_unlike(post_id=777)
        assert c._transport._sync.request.call_args[0][0] == "DELETE"

    def test_conversation_create(self):
        c = _forum()
        c.conversations.conversations_create(
            recipient_id=5, message_body="Hey"
        )
        assert c._transport._sync.request.call_args[0][0] == "POST"

    def test_tags_popular(self):
        c = _forum()
        c.tags.tags_popular()
        assert "/tags" in c._transport._sync.request.call_args[0][1]

    def test_batch_execute(self):
        c = _forum()
        c.batch.batch_execute()
        assert c._transport._sync.request.call_args[0][0] == "POST"


# ── MarketClient ───────────────────────────────────────────────────────────────
class TestMarketClient:
    def test_sections_exist(self):
        c = _market()
        for s in ("profile","categories","accounts_list","managing","steam",
                  "telegram","publishing","purchasing","cart","payments",
                  "invoices","custom_discounts","proxy","imap","batch"):
            assert hasattr(c, s), f"missing section: {s}"

    def test_profile_get(self):
        c = _market()
        c.profile.profile_get()
        assert c._transport._sync.request.call_args[0][0] == "GET"
        assert "/me" in c._transport._sync.request.call_args[0][1]

    def test_profile_edit(self):
        c = _market()
        c.profile.profile_edit(currency="rub")
        assert c._transport._sync.request.call_args[0][0] == "PUT"

    def test_categories_get(self):
        c = _market()
        c.categories.categories_get()
        assert c._transport._sync.request.call_args[0][0] == "GET"

    def test_accounts_search(self):
        c = _market()
        c.accounts_list.accounts_search(price_max=500)
        assert c._transport._sync.request.call_args[0][0] == "GET"

    def test_accounts_search_steam(self):
        c = _market()
        c.accounts_list.accounts_search_steam(price_max=1000)
        assert "/steam" in c._transport._sync.request.call_args[0][1]

    def test_list_orders(self):
        c = _market()
        c.accounts_list.list_orders()
        assert "/user/orders" in c._transport._sync.request.call_args[0][1]

    def test_list_favorites(self):
        c = _market()
        c.accounts_list.list_favorites()
        assert "/user/favorites" in c._transport._sync.request.call_args[0][1]

    def test_managing_get(self):
        c = _market()
        c.managing.managing_get(item_id=12345)
        assert "12345" in c._transport._sync.request.call_args[0][1]

    def test_managing_edit(self):
        c = _market()
        c.managing.managing_edit(item_id=999, price=200.0)
        assert c._transport._sync.request.call_args[0][0] == "PUT"

    def test_managing_delete(self):
        c = _market()
        c.managing.managing_delete(item_id=999)
        assert c._transport._sync.request.call_args[0][0] == "DELETE"

    def test_managing_bump(self):
        c = _market()
        c.managing.managing_bump(item_id=12345)
        assert c._transport._sync.request.call_args[0][0] == "POST"

    def test_managing_transfer(self):
        c = _market()
        c.managing.managing_transfer(item_id=999, username="alice", secret_answer="x")
        assert c._transport._sync.request.call_args[0][0] == "POST"

    def test_managing_favorite(self):
        c = _market()
        c.managing.managing_favorite(item_id=12345)
        assert c._transport._sync.request.call_args[0][0] == "POST"

    def test_managing_unfavorite(self):
        c = _market()
        c.managing.managing_unfavorite(item_id=12345)
        assert c._transport._sync.request.call_args[0][0] == "DELETE"

    def test_steam_get_mafile(self):
        c = _market()
        c.steam.steam_get_mafile(item_id=12345)
        assert c._transport._sync.request.call_args[0][0] == "GET"
        assert "mafile" in c._transport._sync.request.call_args[0][1]

    def test_steam_guard_code(self):
        c = _market()
        c.steam.steam_guard_code(item_id=12345)
        assert c._transport._sync.request.call_args[0][0] == "GET"

    def test_telegram_code(self):
        c = _market()
        c.telegram.telegram_confirmation_code(item_id=12345)
        assert c._transport._sync.request.call_args[0][0] == "GET"

    def test_purchasing_fast_buy(self):
        c = _market()
        c.purchasing.purchasing_fast_buy(item_id=12345, price=199.0)
        assert c._transport._sync.request.call_args[0][0] == "POST"

    def test_purchasing_check(self):
        c = _market()
        c.purchasing.purchasing_check(item_id=12345)
        assert c._transport._sync.request.call_args[0][0] == "POST"

    def test_purchasing_confirm(self):
        c = _market()
        c.purchasing.purchasing_confirm(item_id=12345)
        assert c._transport._sync.request.call_args[0][0] == "POST"

    def test_purchasing_discount_request(self):
        c = _market()
        c.purchasing.purchasing_discount_request(item_id=12345, price=100.0)
        assert c._transport._sync.request.call_args[0][0] == "POST"

    def test_publishing_fast_sell(self):
        c = _market()
        c.publishing.publishing_fast_sell(
            category_id=1, price=100.0, currency="rub",
            item_origin="hand", login="user", password="pass"
        )
        assert c._transport._sync.request.call_args[0][0] == "POST"

    def test_cart_get(self):
        c = _market()
        c.cart.cart_get()
        assert "/cart" in c._transport._sync.request.call_args[0][1]

    def test_cart_add(self):
        c = _market()
        c.cart.cart_add(item_id=12345)
        assert c._transport._sync.request.call_args[0][0] == "POST"

    def test_cart_delete(self):
        c = _market()
        c.cart.cart_delete(item_id=12345)
        assert c._transport._sync.request.call_args[0][0] == "DELETE"

    def test_payments_history(self):
        c = _market()
        c.payments.payments_history()
        assert "/user/payments" in c._transport._sync.request.call_args[0][1]

    def test_payments_balance_list(self):
        c = _market()
        c.payments.payments_balance_list()
        assert "/balance/list" in c._transport._sync.request.call_args[0][1]

    def test_payments_transfer(self):
        c = _market()
        c.payments.payments_transfer(amount=100, currency="rub", secret_answer="x")
        assert c._transport._sync.request.call_args[0][0] == "POST"
        assert "/money/transfer" in c._transport._sync.request.call_args[0][1]

    def test_payments_balance_exchange(self):
        c = _market()
        c.payments.payments_balance_exchange(
            from_balance="main", to_balance="hold", amount=500
        )
        assert c._transport._sync.request.call_args[0][0] == "POST"

    def test_payments_payout(self):
        c = _market()
        c.payments.payments_payout(
            service="CryptoLove", wallet="addr", amount=1000, currency="rub"
        )
        assert c._transport._sync.request.call_args[0][0] == "POST"

    def test_invoices_create(self):
        c = _market()
        c.invoices.invoices_create(currency="rub", amount=150, payment_id="INV-001")
        assert c._transport._sync.request.call_args[0][0] == "POST"

    def test_invoices_list(self):
        c = _market()
        c.invoices.invoices_list()
        assert c._transport._sync.request.call_args[0][0] == "GET"

    def test_proxy_get(self):
        c = _market()
        c.proxy.proxy_get()
        assert "/proxy" in c._transport._sync.request.call_args[0][1]

    def test_proxy_add(self):
        c = _market()
        c.proxy.proxy_add(proxy_row="1.2.3.4:1080:user:pass")
        assert c._transport._sync.request.call_args[0][0] == "POST"

    def test_custom_discounts_get(self):
        c = _market()
        c.custom_discounts.custom_discounts_get()
        assert c._transport._sync.request.call_args[0][0] == "GET"

    def test_batch_execute(self):
        c = _market()
        c.batch.batch_execute(requests=[{"method": "GET", "uri": "/me"}])
        assert c._transport._sync.request.call_args[0][0] == "POST"

    def test_context_manager(self):
        with _market() as c:
            c._transport._sync.request.return_value = {"ok": True}
            assert c.request("GET", "/me") == {"ok": True}


# ── Async ─────────────────────────────────────────────────────────────────────
class TestAsyncClients:
    @pytest.mark.asyncio
    async def test_async_forum_get_user(self):
        with patch("requests.Session"):
            c = ForumClient(token="test")

        async def fake(method, path, **kw):
            return {"user": {"user_id": 42}}

        c._transport.request_async = fake
        result = await c.users.users_get_async(user_id=42)
        assert result["user"]["user_id"] == 42

    @pytest.mark.asyncio
    async def test_async_market_profile_get(self):
        with patch("requests.Session"):
            c = MarketClient(token="test")

        async def fake(method, path, **kw):
            return {"user": {"user_id": 1}}

        c._transport.request_async = fake
        result = await c.profile.profile_get_async()
        assert result["user"]["user_id"] == 1

    @pytest.mark.asyncio
    async def test_async_market_accounts_search(self):
        with patch("requests.Session"):
            c = MarketClient(token="test")

        async def fake(method, path, **kw):
            return {"items": [{"item_id": 1}]}

        c._transport.request_async = fake
        result = await c.accounts_list.accounts_search_async()
        assert result["items"][0]["item_id"] == 1
