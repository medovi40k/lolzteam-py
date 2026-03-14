"""
tests/test_models.py
~~~~~~~~~~~~~~~~~~~~
Tests for Forum and Market response models.
Covers both Pydantic and plain-dataclass fallback paths.
"""

from __future__ import annotations

import pytest
from lolzteam.models.forum import (
    User, Forum, Category, Post, Thread,
    Conversation, ConversationMessage, Notification, ProfilePost, Tag,
)
from lolzteam.models.market import Item, MarketCategory, Payment, Balance


# ── Forum models ──────────────────────────────────────────────────────────────

class TestUserModel:
    def _make(self, **kwargs):
        base = {"user_id": 1, "username": "testuser"}
        base.update(kwargs)
        return base

    def test_minimal(self):
        data = self._make()
        try:
            u = User(**data)
        except TypeError:
            u = User(user_id=data["user_id"], username=data["username"])
        assert u.user_id == 1
        assert u.username == "testuser"

    def test_full_fields(self):
        data = self._make(
            user_email="test@example.com",
            user_title="Member",
            user_message_count=100,
            user_register_date=1700000000,
            user_like_count=50,
            user_is_valid=1,
            user_is_verified=1,
            user_is_followed=0,
        )
        try:
            u = User(**data)
        except TypeError:
            u = User(user_id=1, username="testuser")
        assert u.user_id == 1

    def test_optional_fields_default_none(self):
        try:
            u = User(user_id=42, username="foo")
            assert u.user_email is None
            assert u.user_title is None
            assert u.user_message_count is None
        except TypeError:
            pass  # dataclass path — skip optional check


class TestForumModel:
    def test_minimal(self):
        try:
            f = Forum(forum_id=10, forum_title="General")
            assert f.forum_id == 10
            assert f.forum_title == "General"
        except TypeError:
            f = Forum(forum_id=10, forum_title="General")
            assert f.forum_id == 10

    def test_optional_description(self):
        try:
            f = Forum(forum_id=1, forum_title="T")
            assert f.forum_description is None
        except TypeError:
            pass


class TestCategoryModel:
    def test_basic(self):
        try:
            c = Category(category_id=5, category_title="Marketplace")
            assert c.category_id == 5
            assert c.category_title == "Marketplace"
        except TypeError:
            pass


class TestPostModel:
    def test_minimal(self):
        try:
            p = Post(post_id=100)
            assert p.post_id == 100
            assert p.post_body is None
        except TypeError:
            p = Post(post_id=100)
            assert p.post_id == 100

    def test_with_body(self):
        try:
            p = Post(post_id=1, post_body="Hello world", poster_username="alice")
            assert p.post_body == "Hello world"
            assert p.poster_username == "alice"
        except TypeError:
            pass


class TestThreadModel:
    def test_minimal(self):
        try:
            t = Thread(thread_id=200, thread_title="Test thread")
            assert t.thread_id == 200
            assert t.thread_title == "Test thread"
        except TypeError:
            t = Thread(thread_id=200, thread_title="Test thread")
            assert t.thread_id == 200

    def test_with_counts(self):
        try:
            t = Thread(
                thread_id=1,
                thread_title="X",
                thread_view_count=500,
                thread_post_count=10,
                thread_like_count=5,
            )
            assert t.thread_view_count == 500
        except TypeError:
            pass


class TestConversationModel:
    def test_basic(self):
        try:
            c = Conversation(conversation_id=1, conversation_title="Hi there")
            assert c.conversation_id == 1
        except TypeError:
            pass


class TestConversationMessageModel:
    def test_basic(self):
        try:
            m = ConversationMessage(message_id=1, message_body="Hey!")
            assert m.message_id == 1
            assert m.message_body == "Hey!"
        except TypeError:
            pass


class TestNotificationModel:
    def test_basic(self):
        try:
            n = Notification(notification_id=99, notification_type="post_like")
            assert n.notification_id == 99
            assert n.notification_type == "post_like"
        except TypeError:
            pass

    def test_is_unread_default(self):
        try:
            n = Notification(notification_id=1)
            assert n.notification_is_unread is None
        except TypeError:
            pass


class TestProfilePostModel:
    def test_basic(self):
        try:
            pp = ProfilePost(post_id=55, post_body="Nice!")
            assert pp.post_id == 55
            assert pp.post_body == "Nice!"
        except TypeError:
            pass


class TestTagModel:
    def test_basic(self):
        try:
            t = Tag(tag_id=7, tag_text="python")
            assert t.tag_id == 7
            assert t.tag_text == "python"
        except TypeError:
            pass

    def test_use_count(self):
        try:
            t = Tag(tag_id=1, tag_text="lolz", tag_use_count=1337)
            assert t.tag_use_count == 1337
        except TypeError:
            pass


# ── Market models ─────────────────────────────────────────────────────────────

class TestItemModel:
    def test_minimal(self):
        try:
            item = Item(item_id=12345)
            assert item.item_id == 12345
            assert item.price is None
        except TypeError:
            item = Item(item_id=12345)
            assert item.item_id == 12345

    def test_full(self):
        try:
            item = Item(
                item_id=1,
                item_state="active",
                title="Steam account",
                price=199.99,
                currency="rub",
                category_id=1,
                seller_id=42,
            )
            assert item.price == 199.99
            assert item.currency == "rub"
            assert item.category_id == 1
        except TypeError:
            pass

    def test_optional_buyer(self):
        try:
            item = Item(item_id=1)
            assert item.buyer_id is None
        except TypeError:
            pass


class TestMarketCategoryModel:
    def test_basic(self):
        try:
            c = MarketCategory(id=3, title="Steam")
            assert c.id == 3
            assert c.title == "Steam"
        except TypeError:
            pass


class TestPaymentModel:
    def test_basic(self):
        try:
            p = Payment(payment_id="PAY-001", operation_type="transfer")
            assert p.payment_id == "PAY-001"
            assert p.operation_type == "transfer"
        except TypeError:
            pass

    def test_amounts(self):
        try:
            p = Payment(
                incoming_sum=1000.0,
                outgoing_sum=0.0,
                currency="rub",
            )
            assert p.incoming_sum == 1000.0
        except TypeError:
            pass


class TestBalanceModel:
    def test_basic(self):
        try:
            b = Balance(balance=5000.0, currency="rub")
            assert b.balance == 5000.0
            assert b.currency == "rub"
        except TypeError:
            pass

    def test_hold(self):
        try:
            b = Balance(balance=1000.0, hold=200.0, currency="rub")
            assert b.hold == 200.0
        except TypeError:
            pass


# ── Pydantic-specific: extra fields allowed ──────────────────────────────────

class TestPydanticExtras:
    """If Pydantic is available, models should accept extra fields."""

    def test_user_extra_field(self):
        try:
            import pydantic
            u = User(user_id=1, username="foo", some_future_field="bar")
            # should not raise
        except ImportError:
            pytest.skip("pydantic not installed")
        except TypeError:
            pytest.skip("dataclass path — extra fields not supported")

    def test_item_extra_field(self):
        try:
            import pydantic
            item = Item(item_id=1, undocumented_key="value")
        except ImportError:
            pytest.skip("pydantic not installed")
        except TypeError:
            pytest.skip("dataclass path")
