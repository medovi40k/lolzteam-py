"""
lolzteam.models.forum
~~~~~~~~~~~~~~~~~~~~~
Typed response models for Forum API.
Pydantic v2 is used when available; falls back to plain dataclasses.
"""

from __future__ import annotations

from typing import Any

try:
    from pydantic import BaseModel, Field

    _USE_PYDANTIC = True
except ImportError:
    from dataclasses import dataclass  # type: ignore[assignment]

    _USE_PYDANTIC = False


if _USE_PYDANTIC:

    class UserLinks(BaseModel):
        permalink: str | None = None
        detail: str | None = None
        avatar: str | None = None
        followers: str | None = None
        followings: str | None = None
        ignored: str | None = None
        timeline: str | None = None
        report: str | None = None

    class User(BaseModel):
        user_id: int
        username: str
        user_email: str | None = None
        user_title: str | None = None
        user_message_count: int | None = None
        user_register_date: int | None = None
        user_like_count: int | None = None
        user_is_valid: int | None = None
        user_is_verified: int | None = None
        user_is_followed: int | None = None
        links: UserLinks | None = None
        extra: dict[str, Any] = Field(default_factory=dict)

        model_config = {"extra": "allow"}

    class Forum(BaseModel):
        forum_id: int
        forum_title: str
        forum_description: str | None = None
        forum_post_count: int | None = None
        forum_thread_count: int | None = None
        links: dict[str, Any] | None = None

        model_config = {"extra": "allow"}

    class Category(BaseModel):
        category_id: int
        category_title: str
        links: dict[str, Any] | None = None

        model_config = {"extra": "allow"}

    class Post(BaseModel):
        post_id: int
        thread_id: int | None = None
        poster_user_id: int | None = None
        poster_username: str | None = None
        post_create_date: int | None = None
        post_body: str | None = None
        post_body_html: str | None = None
        post_like_count: int | None = None
        links: dict[str, Any] | None = None

        model_config = {"extra": "allow"}

    class Thread(BaseModel):
        thread_id: int
        forum_id: int | None = None
        thread_title: str
        thread_view_count: int | None = None
        thread_post_count: int | None = None
        thread_like_count: int | None = None
        creator_user_id: int | None = None
        thread_create_date: int | None = None
        thread_update_date: int | None = None
        first_post: Post | None = None
        links: dict[str, Any] | None = None

        model_config = {"extra": "allow"}

    class Conversation(BaseModel):
        conversation_id: int
        conversation_title: str
        message_count: int | None = None
        creator_user_id: int | None = None
        conversation_create_date: int | None = None
        links: dict[str, Any] | None = None

        model_config = {"extra": "allow"}

    class ConversationMessage(BaseModel):
        message_id: int
        conversation_id: int | None = None
        message_create_date: int | None = None
        sender_user_id: int | None = None
        message_body: str | None = None
        links: dict[str, Any] | None = None

        model_config = {"extra": "allow"}

    class Notification(BaseModel):
        notification_id: int
        notification_type: str | None = None
        notification_create_date: int | None = None
        notification_is_unread: int | None = None
        links: dict[str, Any] | None = None

        model_config = {"extra": "allow"}

    class ProfilePost(BaseModel):
        post_id: int
        poster_user_id: int | None = None
        profile_user_id: int | None = None
        post_create_date: int | None = None
        post_body: str | None = None
        post_like_count: int | None = None
        links: dict[str, Any] | None = None

        model_config = {"extra": "allow"}

    class Tag(BaseModel):
        tag_id: int
        tag_text: str
        tag_use_count: int | None = None
        links: dict[str, Any] | None = None

        model_config = {"extra": "allow"}

else:
    # Fallback plain dataclasses (no validation, just structure)
    from dataclasses import dataclass  # type: ignore[no-redef]

    @dataclass
    class User:  # type: ignore[no-redef]
        user_id: int
        username: str
        user_email: str | None = None
        user_title: str | None = None
        user_message_count: int | None = None
        user_register_date: int | None = None
        user_like_count: int | None = None

    @dataclass
    class Forum:  # type: ignore[no-redef]
        forum_id: int
        forum_title: str
        forum_description: str | None = None

    @dataclass
    class Category:  # type: ignore[no-redef]
        category_id: int
        category_title: str

    @dataclass
    class Post:  # type: ignore[no-redef]
        post_id: int
        thread_id: int | None = None
        post_body: str | None = None

    @dataclass
    class Thread:  # type: ignore[no-redef]
        thread_id: int
        thread_title: str
        forum_id: int | None = None

    @dataclass
    class Conversation:  # type: ignore[no-redef]
        conversation_id: int
        conversation_title: str

    @dataclass
    class ConversationMessage:  # type: ignore[no-redef]
        message_id: int
        message_body: str | None = None

    @dataclass
    class Notification:  # type: ignore[no-redef]
        notification_id: int
        notification_type: str | None = None

    @dataclass
    class ProfilePost:  # type: ignore[no-redef]
        post_id: int
        post_body: str | None = None

    @dataclass
    class Tag:  # type: ignore[no-redef]
        tag_id: int
        tag_text: str


__all__ = [
    "User",
    "Forum",
    "Category",
    "Post",
    "Thread",
    "Conversation",
    "ConversationMessage",
    "Notification",
    "ProfilePost",
    "Tag",
]
