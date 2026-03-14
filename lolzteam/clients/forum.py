"""lolzteam.clients.forum — Forum API client."""
from __future__ import annotations
from typing import Any, Dict, Optional
from .._http import Transport, DEFAULT_TIMEOUT, DEFAULT_RETRY_COUNT
from ..sections._forum_generated import (
    AssetsSection, CategoriesSection, ForumsSection, LinksSection,
    NavigationSection, PagesSection, ThreadsSection, PostsSection,
    ProfilePostsSection, ConversationsSection, NotificationsSection,
    SearchSection, TagsSection, ChatboxSection, FormsSection,
    BatchSection, UsersSection, OauthSection,
)

class ForumClient:
    """
    Lolzteam Forum API client. Base URL: https://prod-api.lolz.live

    :param token:       Bearer token. Required scopes: read + post.
    :param proxy:       Proxy URL e.g. ``socks5://user:pass@host:1080``
    :param timeout:     Request timeout seconds (default 30).
    :param max_retries: Retries on 429/502/503 (default 5).
    :param language:    ``"ru"`` or ``"en"`` (default ``"en"``).

    Quick reference::

        forum.threads.threads_create(forum_id=876, post_body="Body", title="My Title")
        forum.posts.posts_create(thread_id=123, post_body="Reply")
        forum.users.users_me()
        forum.conversations.conversations_create(recipient_id=5, message_body="Hi")
        forum.conversations.conversations_messages_list(conversation_id=1)
        forum.chatbox.chatbox_post_message(room_id=1, message="Hello!")
    """

    BASE_URL = "https://prod-api.lolz.live"

    def __init__(self, token: str, proxy: Optional[str] = None,
                 timeout: float = DEFAULT_TIMEOUT, max_retries: int = DEFAULT_RETRY_COUNT,
                 language: str = "en") -> None:
        self._transport = Transport(
            token=token, base_url=self.BASE_URL, proxy=proxy,
            timeout=timeout, max_retries=max_retries, language=language,
        )
        self.assets         = AssetsSection(self._transport)
        self.oauth          = OauthSection(self._transport)
        self.categories     = CategoriesSection(self._transport)
        self.forums         = ForumsSection(self._transport)
        self.links          = LinksSection(self._transport)
        self.navigation     = NavigationSection(self._transport)
        self.pages          = PagesSection(self._transport)
        self.threads        = ThreadsSection(self._transport)
        self.posts          = PostsSection(self._transport)
        self.profile_posts  = ProfilePostsSection(self._transport)
        self.conversations  = ConversationsSection(self._transport)
        self.notifications  = NotificationsSection(self._transport)
        self.search         = SearchSection(self._transport)
        self.tags           = TagsSection(self._transport)
        self.chatbox        = ChatboxSection(self._transport)
        self.forms          = FormsSection(self._transport)
        self.batch          = BatchSection(self._transport)
        self.users          = UsersSection(self._transport)

    def request(self, method: str, path: str, **kwargs: Any) -> Dict[str, Any]:
        return self._transport.request(method, path, **kwargs)

    async def request_async(self, method: str, path: str, **kwargs: Any) -> Dict[str, Any]:
        return await self._transport.request_async(method, path, **kwargs)

    def close(self) -> None:
        self._transport.close()

    async def aclose(self) -> None:
        await self._transport.aclose()

    def __enter__(self) -> "ForumClient":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()

    async def __aenter__(self) -> "ForumClient":
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.aclose()
