"""
tests/test_async_coverage.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Covers async method paths in generated sections, client aclose(),
and Transport async delegation — all mocked, no real network.
"""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from lolzteam import ForumClient, MarketClient


# ── helpers ───────────────────────────────────────────────────────────────────

def _forum(token="test") -> ForumClient:
    with patch("requests.Session"):
        c = ForumClient(token=token)
    # Inject async mock transport
    c._transport.request_async = AsyncMock(return_value={"ok": True})
    return c


def _market(token="test") -> MarketClient:
    with patch("requests.Session"):
        c = MarketClient(token=token)
    c._transport.request_async = AsyncMock(return_value={"ok": True})
    return c


# ── Forum async methods ───────────────────────────────────────────────────────

class TestForumAsyncMethods:

    @pytest.mark.asyncio
    async def test_users_me_async(self):
        c = _forum()
        c._transport.request_async.return_value = {"user": {"user_id": 1}}
        result = await c.users.users__get_async(user_id=1)
        assert result["user"]["user_id"] == 1
        c._transport.request_async.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_users_get_async(self):
        c = _forum()
        await c.users.users__get_async(user_id=42)
        args = c._transport.request_async.call_args
        assert args[0][0] == "GET"
        assert "42" in args[0][1]

    @pytest.mark.asyncio
    async def test_threads_list_async(self):
        c = _forum()
        await c.threads.threads__list_async(forum_id=176, limit=10)
        c._transport.request_async.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_threads_create_async(self):
        c = _forum()
        await c.threads.threads__create_async(
            forum_id=1, post_body="Body", title="Test thread"
        )
        args = c._transport.request_async.call_args
        assert args[0][0] == "POST"

    @pytest.mark.asyncio
    async def test_threads_get_async(self):
        c = _forum()
        await c.threads.threads__get_async(thread_id=100)
        args = c._transport.request_async.call_args
        assert "100" in args[0][1]

    @pytest.mark.asyncio
    async def test_threads_edit_async(self):
        c = _forum()
        await c.posts.posts__edit_async(post_id=100, post_body="Edited content")
        args = c._transport.request_async.call_args
        assert args[0][0] == "PUT"

    @pytest.mark.asyncio
    async def test_threads_delete_async(self):
        c = _forum()
        await c.threads.threads__delete_async(thread_id=100)
        args = c._transport.request_async.call_args
        assert args[0][0] == "DELETE"

    @pytest.mark.asyncio
    async def test_threads_bump_async(self):
        c = _forum()
        await c.threads.threads__bump_async(thread_id=100)
        args = c._transport.request_async.call_args
        assert args[0][0] == "POST"

    @pytest.mark.asyncio
    async def test_posts_list_async(self):
        c = _forum()
        await c.posts.posts__list_async(thread_id=100)
        c._transport.request_async.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_posts_get_async(self):
        c = _forum()
        await c.posts.posts__get_async(post_id=55)
        args = c._transport.request_async.call_args
        assert "55" in args[0][1]

    @pytest.mark.asyncio
    async def test_posts_create_async(self):
        c = _forum()
        await c.posts.posts__create_async(thread_id=100, post_body="Hello!")
        args = c._transport.request_async.call_args
        assert args[0][0] == "POST"

    @pytest.mark.asyncio
    async def test_posts_edit_async(self):
        c = _forum()
        await c.posts.posts__edit_async(post_id=55, post_body="Edited")
        args = c._transport.request_async.call_args
        assert args[0][0] == "PUT"

    @pytest.mark.asyncio
    async def test_posts_delete_async(self):
        c = _forum()
        await c.posts.posts__delete_async(post_id=55)
        args = c._transport.request_async.call_args
        assert args[0][0] == "DELETE"

    @pytest.mark.asyncio
    async def test_posts_like_async(self):
        c = _forum()
        await c.posts.posts__like_async(post_id=55)
        args = c._transport.request_async.call_args
        assert args[0][0] == "POST"

    @pytest.mark.asyncio
    async def test_posts_unlike_async(self):
        c = _forum()
        await c.posts.posts__unlike_async(post_id=55)
        args = c._transport.request_async.call_args
        assert args[0][0] == "DELETE"

    @pytest.mark.asyncio
    async def test_categories_list_async(self):
        c = _forum()
        await c.categories.categories__list_async()
        c._transport.request_async.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_categories_get_async(self):
        c = _forum()
        await c.categories.categories__get_async(category_id=3)
        args = c._transport.request_async.call_args
        assert "3" in args[0][1]

    @pytest.mark.asyncio
    async def test_forums_list_async(self):
        c = _forum()
        await c.forums.forums__list_async()
        c._transport.request_async.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_forums_get_async(self):
        c = _forum()
        await c.forums.forums__get_async(forum_id=10)
        args = c._transport.request_async.call_args
        assert "10" in args[0][1]

    @pytest.mark.asyncio
    async def test_forums_follow_async(self):
        c = _forum()
        await c.forums.forums__follow_async(forum_id=10)
        args = c._transport.request_async.call_args
        assert args[0][0] == "POST"

    @pytest.mark.asyncio
    async def test_forums_unfollow_async(self):
        c = _forum()
        await c.forums.forums__unfollow_async(forum_id=10)
        args = c._transport.request_async.call_args
        assert args[0][0] == "DELETE"

    @pytest.mark.asyncio
    async def test_users_follow_async(self):
        c = _forum()
        await c.users.users__follow_async(user_id=5)
        args = c._transport.request_async.call_args
        assert args[0][0] == "POST"

    @pytest.mark.asyncio
    async def test_users_unfollow_async(self):
        c = _forum()
        await c.users.users__unfollow_async(user_id=5)
        args = c._transport.request_async.call_args
        assert args[0][0] == "DELETE"

    @pytest.mark.asyncio
    async def test_users_ignore_async(self):
        c = _forum()
        await c.users.users__ignore_async(user_id=5)
        args = c._transport.request_async.call_args
        assert args[0][0] == "POST"

    @pytest.mark.asyncio
    async def test_users_unignore_async(self):
        c = _forum()
        await c.users.users__unignore_async(user_id=5)
        args = c._transport.request_async.call_args
        assert args[0][0] == "DELETE"

    @pytest.mark.asyncio
    async def test_conversations_list_async(self):
        c = _forum()
        await c.conversations.conversations__list_async()
        c._transport.request_async.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_conversations_get_async(self):
        c = _forum()
        await c.conversations.conversations__get_async(conversation_id=1)
        args = c._transport.request_async.call_args
        assert "1" in args[0][1]

    @pytest.mark.asyncio
    async def test_conversations_create_async(self):
        c = _forum()
        await c.conversations.conversations__create_async(recipient_id=5)
        args = c._transport.request_async.call_args
        assert args[0][0] == "POST"

    @pytest.mark.asyncio
    async def test_conversations_messages_list_async(self):
        c = _forum()
        await c.conversations.conversations__messages__list_async(conversation_id=1)
        c._transport.request_async.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_conversations_messages_create_async(self):
        c = _forum()
        await c.conversations.conversations__messages__create_async(
            conversation_id=1, message_body="Reply"
        )
        args = c._transport.request_async.call_args
        assert args[0][0] == "POST"

    @pytest.mark.asyncio
    async def test_notifications_list_async(self):
        c = _forum()
        await c.notifications.notifications__list_async()
        c._transport.request_async.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_notifications_get_async(self):
        c = _forum()
        await c.notifications.notifications__get_async(notification_id=99)
        args = c._transport.request_async.call_args
        assert "99" in args[0][1]

    @pytest.mark.asyncio
    async def test_notifications_read_async(self):
        c = _forum()
        await c.notifications.notifications__read_async()
        args = c._transport.request_async.call_args
        assert args[0][0] == "POST"

    @pytest.mark.asyncio
    async def test_search_all_async(self):
        c = _forum()
        await c.search.search__all_async(q="python")
        args = c._transport.request_async.call_args
        assert args[0][0] == "POST"

    @pytest.mark.asyncio
    async def test_search_threads_async(self):
        c = _forum()
        await c.search.search__threads_async(q="tutorial")
        c._transport.request_async.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_search_posts_async(self):
        c = _forum()
        await c.search.search__posts_async(q="hello")
        c._transport.request_async.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_search_users_async(self):
        c = _forum()
        await c.search.search__users_async(q="alice")
        c._transport.request_async.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_tags_list_async(self):
        c = _forum()
        await c.tags.tags__list_async()
        c._transport.request_async.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_tags_popular_async(self):
        c = _forum()
        await c.tags.tags__popular_async()
        c._transport.request_async.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_batch_execute_async(self):
        c = _forum()
        await c.batch.batch__execute_async()
        args = c._transport.request_async.call_args
        assert args[0][0] == "POST"

    @pytest.mark.asyncio
    async def test_profile_posts_list_async(self):
        c = _forum()
        await c.profile_posts.profile_posts__list_async(user_id=1)
        c._transport.request_async.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_profile_posts_create_async(self):
        c = _forum()
        await c.profile_posts.profile_posts__create_async(
            user_id=1, post_body="Hi!"
        )
        args = c._transport.request_async.call_args
        assert args[0][0] == "POST"

    @pytest.mark.asyncio
    async def test_profile_posts_like_async(self):
        c = _forum()
        await c.profile_posts.profile_posts__like_async(profile_post_id=10)
        args = c._transport.request_async.call_args
        assert args[0][0] == "POST"

    @pytest.mark.asyncio
    async def test_profile_posts_unlike_async(self):
        c = _forum()
        await c.profile_posts.profile_posts__unlike_async(profile_post_id=10)
        args = c._transport.request_async.call_args
        assert args[0][0] == "DELETE"

    @pytest.mark.asyncio
    async def test_threads_followed_async(self):
        c = _forum()
        await c.threads.threads__followed_async()
        c._transport.request_async.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_threads_unread_async(self):
        c = _forum()
        await c.threads.threads__unread_async()
        c._transport.request_async.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_threads_recent_async(self):
        c = _forum()
        await c.threads.threads__recent_async()
        c._transport.request_async.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_threads_follow_async(self):
        c = _forum()
        await c.threads.threads__follow_async(thread_id=100)
        args = c._transport.request_async.call_args
        assert args[0][0] == "POST"

    @pytest.mark.asyncio
    async def test_threads_unfollow_async(self):
        c = _forum()
        await c.threads.threads__unfollow_async(thread_id=100)
        args = c._transport.request_async.call_args
        assert args[0][0] == "DELETE"

    @pytest.mark.asyncio
    async def test_posts_report_async(self):
        c = _forum()
        await c.posts.posts__report_async(post_id=55, message="spam")
        args = c._transport.request_async.call_args
        assert args[0][0] == "POST"

    @pytest.mark.asyncio
    async def test_raw_request_async(self):
        c = _forum()
        c._transport.request_async.return_value = {"categories": []}
        result = await c.request_async("GET", "/categories")
        assert result == {"categories": []}


# ── Market async methods ───────────────────────────────────────────────────────

class TestMarketAsyncMethods:

    @pytest.mark.asyncio
    async def test_profile_get_async(self):
        c = _market()
        await c.profile.profile__get_async()
        assert "/me" in c._transport.request_async.call_args[0][1]

    @pytest.mark.asyncio
    async def test_categories_get_async(self):
        c = _market()
        await c.categories.category__list_async()
        c._transport.request_async.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_accounts_search_async(self):
        c = _market()
        await c.accounts_list.list__user_async(user_id=123)
        c._transport.request_async.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_accounts_search_steam_async(self):
        c = _market()
        await c.category_search.category__steam_async()
        assert "/steam" in c._transport.request_async.call_args[0][1]

    @pytest.mark.asyncio
    async def test_list_orders_async(self):
        c = _market()
        await c.accounts_list.list__orders_async()
        assert "/user/orders" in c._transport.request_async.call_args[0][1]

    @pytest.mark.asyncio
    async def test_managing_get_async(self):
        c = _market()
        await c.managing.managing__get_async(item_id=12345)
        assert "12345" in c._transport.request_async.call_args[0][1]

    @pytest.mark.asyncio
    async def test_managing_edit_async(self):
        c = _market()
        await c.managing.managing__edit_async(item_id=999, price=200.0)
        assert c._transport.request_async.call_args[0][0] == "PUT"

    @pytest.mark.asyncio
    async def test_managing_delete_async(self):
        c = _market()
        await c.managing.manging__delete_async(item_id=999, reason="test")
        assert c._transport.request_async.call_args[0][0] == "DELETE"

    @pytest.mark.asyncio
    async def test_managing_bump_async(self):
        c = _market()
        await c.managing.managing__bump_async(item_id=999)
        assert c._transport.request_async.call_args[0][0] == "POST"

    @pytest.mark.asyncio
    async def test_managing_transfer_async(self):
        c = _market()
        await c.managing.managing__transfer_async(
            item_id=999, username="alice", secret_answer="ans"
        )
        assert c._transport.request_async.call_args[0][0] == "POST"

    @pytest.mark.asyncio
    async def test_managing_favorite_async(self):
        c = _market()
        await c.managing.managing__favorite_async(item_id=12345)
        assert c._transport.request_async.call_args[0][0] == "POST"

    @pytest.mark.asyncio
    async def test_managing_unfavorite_async(self):
        c = _market()
        await c.managing.managing__unfavorite_async(item_id=12345)
        assert c._transport.request_async.call_args[0][0] == "DELETE"

    @pytest.mark.asyncio
    async def test_publishing_fast_sell_async(self):
        c = _market()
        await c.publishing.publishing__fast_sell_async(
            category_id=1, price=100.0, currency="rub", item_origin="hand"
        )
        assert c._transport.request_async.call_args[0][0] == "POST"

    @pytest.mark.asyncio
    async def test_purchasing_fast_buy_async(self):
        c = _market()
        await c.purchasing.purchasing__fast_buy_async(item_id=12345, price=150.0)
        assert c._transport.request_async.call_args[0][0] == "POST"

    @pytest.mark.asyncio
    async def test_purchasing_check_async(self):
        c = _market()
        await c.purchasing.purchasing__check_async(item_id=12345)
        assert c._transport.request_async.call_args[0][0] == "POST"

    @pytest.mark.asyncio
    async def test_purchasing_confirm_async(self):
        c = _market()
        await c.purchasing.purchasing__confirm_async(item_id=12345)
        assert c._transport.request_async.call_args[0][0] == "POST"

    @pytest.mark.asyncio
    async def test_cart_get_async(self):
        c = _market()
        await c.cart.cart__get_async()
        c._transport.request_async.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_cart_add_async(self):
        c = _market()
        await c.cart.cart__add_async(item_id=12345)
        assert c._transport.request_async.call_args[0][0] == "POST"

    @pytest.mark.asyncio
    async def test_cart_delete_async(self):
        c = _market()
        await c.cart.cart__delete_async(item_id=12345)
        assert c._transport.request_async.call_args[0][0] == "DELETE"

    @pytest.mark.asyncio
    async def test_payments_history_async(self):
        c = _market()
        await c.payments.payments__history_async()
        assert "/user/payments" in c._transport.request_async.call_args[0][1]

    @pytest.mark.asyncio
    async def test_payments_balance_list_async(self):
        c = _market()
        await c.payments.payments__balance__list_async()
        assert "/balance/exchange" in c._transport.request_async.call_args[0][1]

    @pytest.mark.asyncio
    async def test_payments_transfer_async(self):
        c = _market()
        await c.payments.payments__transfer_async(
            amount=100, currency="rub"
        )
        assert c._transport.request_async.call_args[0][0] == "POST"

    @pytest.mark.asyncio
    async def test_payments_balance_exchange_async(self):
        c = _market()
        await c.payments.payments__balance_exchange_async(
            from_balance="main", to_balance="hold", amount=500
        )
        assert c._transport.request_async.call_args[0][0] == "POST"

    @pytest.mark.asyncio
    async def test_invoices_create_async(self):
        c = _market()
        await c.invoices.payments__invoice__create_async(
            currency="rub", amount=150, payment_id="INV-001",
            comment="test", url_success="https://example.com", merchant_id=1
        )
        assert c._transport.request_async.call_args[0][0] == "POST"

    @pytest.mark.asyncio
    async def test_invoices_list_async(self):
        c = _market()
        await c.invoices.payments__invoice__list_async()
        c._transport.request_async.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_payments_payout_async(self):
        c = _market()
        await c.payments.payments__payout_async(
            payment_system="CryptoLove", wallet="addr", amount=1000, currency="rub"
        )
        assert c._transport.request_async.call_args[0][0] == "POST"

    @pytest.mark.asyncio
    async def test_steam_get_mafile_async(self):
        c = _market()
        await c.managing.managing__steam__get_mafile_async(item_id=12345)
        assert c._transport.request_async.call_args[0][0] == "GET"

    @pytest.mark.asyncio
    async def test_steam_guard_code_async(self):
        c = _market()
        await c.managing.managing__steam_mafile_code_async(item_id=12345)
        assert c._transport.request_async.call_args[0][0] == "GET"

    @pytest.mark.asyncio
    async def test_proxy_get_async(self):
        c = _market()
        await c.proxy.proxy__get_async()
        c._transport.request_async.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_raw_request_async(self):
        c = _market()
        c._transport.request_async.return_value = {"ok": True}
        result = await c.request_async("GET", "/me")
        assert result == {"ok": True}


# ── Client lifecycle (close / aclose) ─────────────────────────────────────────

class TestClientLifecycle:

    @pytest.mark.asyncio
    async def test_forum_aclose(self):
        c = _forum()
        c._transport.aclose = AsyncMock()
        await c.aclose()
        c._transport.aclose.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_market_aclose(self):
        c = _market()
        c._transport.aclose = AsyncMock()
        await c.aclose()
        c._transport.aclose.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_forum_async_context_manager(self):
        c = _forum()
        c._transport.aclose = AsyncMock()
        async with c as client:
            assert client is c
        c._transport.aclose.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_market_async_context_manager(self):
        c = _market()
        c._transport.aclose = AsyncMock()
        async with c as client:
            assert client is c
        c._transport.aclose.assert_awaited_once()

    def test_forum_close(self):
        c = _forum()
        c._transport.close = MagicMock()
        c.close()
        c._transport.close.assert_called_once()

    def test_market_close(self):
        c = _market()
        c._transport.close = MagicMock()
        c.close()
        c._transport.close.assert_called_once()
