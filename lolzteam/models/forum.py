"""
lolzteam.models.forum
~~~~~~~~~~~~~~~~~~~~~
Typed response models for Forum API.
Pydantic v2 is used when available; falls back to plain dataclasses.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

try:
    from pydantic import BaseModel, Field

    _USE_PYDANTIC = True
except ImportError:
    from dataclasses import dataclass, field  # type: ignore[assignment]

    _USE_PYDANTIC = False


if _USE_PYDANTIC:

    class UserLinks(BaseModel):
        permalink: Optional[str] = None
        detail: Optional[str] = None
        avatar: Optional[str] = None
        followers: Optional[str] = None
        followings: Optional[str] = None
        ignored: Optional[str] = None
        timeline: Optional[str] = None
        report: Optional[str] = None

    class User(BaseModel):
        user_id: int
        username: str
        user_email: Optional[str] = None
        user_title: Optional[str] = None
        user_message_count: Optional[int] = None
        user_register_date: Optional[int] = None
        user_like_count: Optional[int] = None
        user_is_valid: Optional[int] = None
        user_is_verified: Optional[int] = None
        user_is_followed: Optional[int] = None
        links: Optional[UserLinks] = None
        extra: Dict[str, Any] = Field(default_factory=dict)

        model_config = {"extra": "allow"}

    class Forum(BaseModel):
        forum_id: int
        forum_title: str
        forum_description: Optional[str] = None
        forum_post_count: Optional[int] = None
        forum_thread_count: Optional[int] = None
        links: Optional[Dict[str, Any]] = None

        model_config = {"extra": "allow"}

    class Category(BaseModel):
        category_id: int
        category_title: str
        links: Optional[Dict[str, Any]] = None

        model_config = {"extra": "allow"}

    class Post(BaseModel):
        post_id: int
        thread_id: Optional[int] = None
        poster_user_id: Optional[int] = None
        poster_username: Optional[str] = None
        post_create_date: Optional[int] = None
        post_body: Optional[str] = None
        post_body_html: Optional[str] = None
        post_like_count: Optional[int] = None
        links: Optional[Dict[str, Any]] = None

        model_config = {"extra": "allow"}

    class Thread(BaseModel):
        thread_id: int
        forum_id: Optional[int] = None
        thread_title: str
        thread_view_count: Optional[int] = None
        thread_post_count: Optional[int] = None
        thread_like_count: Optional[int] = None
        creator_user_id: Optional[int] = None
        thread_create_date: Optional[int] = None
        thread_update_date: Optional[int] = None
        first_post: Optional[Post] = None
        links: Optional[Dict[str, Any]] = None

        model_config = {"extra": "allow"}

    class Conversation(BaseModel):
        conversation_id: int
        conversation_title: str
        message_count: Optional[int] = None
        creator_user_id: Optional[int] = None
        conversation_create_date: Optional[int] = None
        links: Optional[Dict[str, Any]] = None

        model_config = {"extra": "allow"}

    class ConversationMessage(BaseModel):
        message_id: int
        conversation_id: Optional[int] = None
        message_create_date: Optional[int] = None
        sender_user_id: Optional[int] = None
        message_body: Optional[str] = None
        links: Optional[Dict[str, Any]] = None

        model_config = {"extra": "allow"}

    class Notification(BaseModel):
        notification_id: int
        notification_type: Optional[str] = None
        notification_create_date: Optional[int] = None
        notification_is_unread: Optional[int] = None
        links: Optional[Dict[str, Any]] = None

        model_config = {"extra": "allow"}

    class ProfilePost(BaseModel):
        post_id: int
        poster_user_id: Optional[int] = None
        profile_user_id: Optional[int] = None
        post_create_date: Optional[int] = None
        post_body: Optional[str] = None
        post_like_count: Optional[int] = None
        links: Optional[Dict[str, Any]] = None

        model_config = {"extra": "allow"}

    class Tag(BaseModel):
        tag_id: int
        tag_text: str
        tag_use_count: Optional[int] = None
        links: Optional[Dict[str, Any]] = None

        model_config = {"extra": "allow"}

else:
    # Fallback plain dataclasses (no validation, just structure)
    from dataclasses import dataclass, field  # type: ignore[no-redef]

    @dataclass
    class User:  # type: ignore[no-redef]
        user_id: int
        username: str
        user_email: Optional[str] = None
        user_title: Optional[str] = None
        user_message_count: Optional[int] = None
        user_register_date: Optional[int] = None
        user_like_count: Optional[int] = None

    @dataclass
    class Forum:  # type: ignore[no-redef]
        forum_id: int
        forum_title: str
        forum_description: Optional[str] = None

    @dataclass
    class Category:  # type: ignore[no-redef]
        category_id: int
        category_title: str

    @dataclass
    class Post:  # type: ignore[no-redef]
        post_id: int
        thread_id: Optional[int] = None
        post_body: Optional[str] = None

    @dataclass
    class Thread:  # type: ignore[no-redef]
        thread_id: int
        thread_title: str
        forum_id: Optional[int] = None

    @dataclass
    class Conversation:  # type: ignore[no-redef]
        conversation_id: int
        conversation_title: str

    @dataclass
    class ConversationMessage:  # type: ignore[no-redef]
        message_id: int
        message_body: Optional[str] = None

    @dataclass
    class Notification:  # type: ignore[no-redef]
        notification_id: int
        notification_type: Optional[str] = None

    @dataclass
    class ProfilePost:  # type: ignore[no-redef]
        post_id: int
        post_body: Optional[str] = None

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
