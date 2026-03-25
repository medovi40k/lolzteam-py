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
        for s in ("categories", "forums", "users", "threads", "posts",
                  "profile_posts", "conversations", "notifications",
                  "search", "tags", "batch"):
            assert hasattr(c, s), f"missing section: {s}"

    def test_get_user(self):
        c = _forum()
        c._transport._sync.request.return_value = {"user": {"user_id": 42}}
        c.users.users__get(user_id=42)
        args = c._transport._sync.request.call_args[0]
        assert args[0] == "GET" and "42" in args[1]

    def test_create_thread(self):
        c = _forum()
        c.threads.threads__create(forum_id=1, post_body="B", title="Test thread title")
        assert c._transport._sync.request.call_args[0][0] == "POST"

    def test_create_post(self):
        c = _forum()
        c.posts.posts__create(thread_id=100, post_body="Reply")
        assert c._transport._sync.request.call_args[0][0] == "POST"

    def test_delete_thread(self):
        c = _forum()
        c.threads.threads__delete(thread_id=55)
        assert c._transport._sync.request.call_args[0][0] == "DELETE"

    def test_follow_user(self):
        c = _forum()
        c.users.users__follow(user_id=10)
        assert c._transport._sync.request.call_args[0][0] == "POST"

    def test_search_threads(self):
        c = _forum()
        c.search.search__threads(q="python")
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
        c.notifications.notifications__list()
        assert c._transport._sync.request.call_args[0][0] == "GET"

    def test_like_post(self):
        c = _forum()
        c.posts.posts__like(post_id=777)
        assert c._transport._sync.request.call_args[0][0] == "POST"

    def test_unlike_post(self):
        c = _forum()
        c.posts.posts__unlike(post_id=777)
        assert c._transport._sync.request.call_args[0][0] == "DELETE"

    def test_conversation_create(self):
        c = _forum()
        c.conversations.conversations__create(recipient_id=5)
        assert c._transport._sync.request.call_args[0][0] == "POST"

    def test_tags_popular(self):
        c = _forum()
        c.tags.tags__popular()
        assert "/tags" in c._transport._sync.request.call_args[0][1]

    def test_batch_execute(self):
        c = _forum()
        c.batch.batch__execute()
        assert c._transport._sync.request.call_args[0][0] == "POST"


# ── MarketClient ───────────────────────────────────────────────────────────────
class TestMarketClient:
    def test_sections_exist(self):
        c = _market()
        for s in ("profile", "categories", "category_search", "accounts_list",
                  "managing", "publishing", "purchasing", "cart", "payments",
                  "invoices", "custom_discounts", "proxy", "imap", "batch"):
            assert hasattr(c, s), f"missing section: {s}"

    def test_profile_get(self):
        c = _market()
        c.profile.profile__get()
        assert c._transport._sync.request.call_args[0][0] == "GET"
        assert "/me" in c._transport._sync.request.call_args[0][1]

    def test_categories_get(self):
        c = _market()
        c.categories.category__list()
        assert c._transport._sync.request.call_args[0][0] == "GET"

    def test_accounts_search(self):
        c = _market()
        c.accounts_list.list__user(user_id=123)
        assert c._transport._sync.request.call_args[0][0] == "GET"

    def test_accounts_search_steam(self):
        c = _market()
        c.category_search.category__steam()
        assert "/steam" in c._transport._sync.request.call_args[0][1]

    def test_list_orders(self):
        c = _market()
        c.accounts_list.list__orders()
        assert "/user/orders" in c._transport._sync.request.call_args[0][1]

    def test_list_favorites(self):
        c = _market()
        c.accounts_list.list__favorites()
        assert "/fave" in c._transport._sync.request.call_args[0][1]

    def test_managing_get(self):
        c = _market()
        c.managing.managing__get(item_id=12345)
        assert "12345" in c._transport._sync.request.call_args[0][1]

    def test_managing_edit(self):
        c = _market()
        c.managing.managing__edit(item_id=999, price=200.0)
        assert c._transport._sync.request.call_args[0][0] == "PUT"

    def test_managing_delete(self):
        c = _market()
        c.managing.manging__delete(item_id=999, reason="test")
        assert c._transport._sync.request.call_args[0][0] == "DELETE"

    def test_managing_bump(self):
        c = _market()
        c.managing.managing__bump(item_id=12345)
        assert c._transport._sync.request.call_args[0][0] == "POST"

    def test_managing_transfer(self):
        c = _market()
        c.managing.managing__transfer(item_id=999, username="alice", secret_answer="x")
        assert c._transport._sync.request.call_args[0][0] == "POST"

    def test_managing_favorite(self):
        c = _market()
        c.managing.managing__favorite(item_id=12345)
        assert c._transport._sync.request.call_args[0][0] == "POST"

    def test_managing_unfavorite(self):
        c = _market()
        c.managing.managing__unfavorite(item_id=12345)
        assert c._transport._sync.request.call_args[0][0] == "DELETE"

    def test_steam_get_mafile(self):
        c = _market()
        c.managing.managing__steam__get_mafile(item_id=12345)
        assert c._transport._sync.request.call_args[0][0] == "GET"
        assert "mafile" in c._transport._sync.request.call_args[0][1]

    def test_steam_guard_code(self):
        c = _market()
        c.managing.managing__steam_mafile_code(item_id=12345)
        assert c._transport._sync.request.call_args[0][0] == "GET"

    def test_telegram_code(self):
        c = _market()
        c.managing.managing__telegram_code(item_id=12345)
        assert c._transport._sync.request.call_args[0][0] == "GET"

    def test_purchasing_fast_buy(self):
        c = _market()
        c.purchasing.purchasing__fast_buy(item_id=12345, price=199.0)
        assert c._transport._sync.request.call_args[0][0] == "POST"

    def test_purchasing_check(self):
        c = _market()
        c.purchasing.purchasing__check(item_id=12345)
        assert c._transport._sync.request.call_args[0][0] == "POST"

    def test_purchasing_confirm(self):
        c = _market()
        c.purchasing.purchasing__confirm(item_id=12345)
        assert c._transport._sync.request.call_args[0][0] == "POST"

    def test_purchasing_discount_request(self):
        c = _market()
        c.purchasing.purchasing__discount_request(item_id=12345, discount_price=100.0)
        assert c._transport._sync.request.call_args[0][0] == "POST"

    def test_publishing_fast_sell(self):
        c = _market()
        c.publishing.publishing__fast_sell(
            category_id=1, price=100.0, currency="rub", item_origin="hand"
        )
        assert c._transport._sync.request.call_args[0][0] == "POST"

    def test_cart_get(self):
        c = _market()
        c.cart.cart__get()
        assert "/cart" in c._transport._sync.request.call_args[0][1]

    def test_cart_add(self):
        c = _market()
        c.cart.cart__add(item_id=12345)
        assert c._transport._sync.request.call_args[0][0] == "POST"

    def test_cart_delete(self):
        c = _market()
        c.cart.cart__delete(item_id=12345)
        assert c._transport._sync.request.call_args[0][0] == "DELETE"

    def test_payments_history(self):
        c = _market()
        c.payments.payments__history()
        assert "/user/payments" in c._transport._sync.request.call_args[0][1]

    def test_payments_balance_list(self):
        c = _market()
        c.payments.payments__balance__list()
        assert "/balance/exchange" in c._transport._sync.request.call_args[0][1]

    def test_payments_transfer(self):
        c = _market()
        c.payments.payments__transfer(amount=100, currency="rub")
        assert c._transport._sync.request.call_args[0][0] == "POST"
        assert "/balance/transfer" in c._transport._sync.request.call_args[0][1]

    def test_payments_balance_exchange(self):
        c = _market()
        c.payments.payments__balance_exchange(
            from_balance="main", to_balance="hold", amount=500
        )
        assert c._transport._sync.request.call_args[0][0] == "POST"

    def test_payments_payout(self):
        c = _market()
        c.payments.payments__payout(
            payment_system="CryptoLove", wallet="addr", amount=1000, currency="rub"
        )
        assert c._transport._sync.request.call_args[0][0] == "POST"

    def test_invoices_create(self):
        c = _market()
        c.invoices.payments__invoice__create(
            currency="rub", amount=150, payment_id="INV-001",
            comment="test", url_success="https://example.com", merchant_id=1
        )
        assert c._transport._sync.request.call_args[0][0] == "POST"

    def test_invoices_list(self):
        c = _market()
        c.invoices.payments__invoice__list()
        assert c._transport._sync.request.call_args[0][0] == "GET"

    def test_proxy_get(self):
        c = _market()
        c.proxy.proxy__get()
        assert "/proxy" in c._transport._sync.request.call_args[0][1]

    def test_proxy_add(self):
        c = _market()
        c.proxy.proxy__add(proxy_row="1.2.3.4:1080:user:pass")
        assert c._transport._sync.request.call_args[0][0] == "POST"

    def test_custom_discounts_get(self):
        c = _market()
        c.custom_discounts.custom_discounts__get()
        assert c._transport._sync.request.call_args[0][0] == "GET"

    def test_batch_execute(self):
        c = _market()
        c.batch.batch()
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
        result = await c.users.users__get_async(user_id=42)
        assert result["user"]["user_id"] == 42

    @pytest.mark.asyncio
    async def test_async_market_profile_get(self):
        with patch("requests.Session"):
            c = MarketClient(token="test")

        async def fake(method, path, **kw):
            return {"user": {"user_id": 1}}

        c._transport.request_async = fake
        result = await c.profile.profile__get_async()
        assert result["user"]["user_id"] == 1

    @pytest.mark.asyncio
    async def test_async_market_accounts_search(self):
        with patch("requests.Session"):
            c = MarketClient(token="test")

        async def fake(method, path, **kw):
            return {"items": [{"item_id": 1}]}

        c._transport.request_async = fake
        result = await c.accounts_list.list__user_async()
        assert result["items"][0]["item_id"] == 1
