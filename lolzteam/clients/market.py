"""
lolzteam.clients.market
~~~~~~~~~~~~~~~~~~~~~~~
High-level Market API client. Base URL: https://prod-api.lzt.market

Sections match the official API documentation grouping:
  profile, categories, category_search, accounts_list, managing,
  publishing, purchasing, cart, payments, invoices, custom_discounts,
  proxy, imap, batch
"""
from __future__ import annotations

from typing import Any

from .._http import DEFAULT_RETRY_COUNT, DEFAULT_TIMEOUT, Transport
from ..sections._market_generated import (
    AccountPublishingSection,
    AccountPurchasingSection,
    AccountsListSection,
    AccountsManagingSection,
    BatchRequestsSection,
    CartSection,
    CategoriesSection,
    CategorySearchSection,
    CustomDiscountsSection,
    ImapSection,
    InvoicesSection,
    PaymentsSection,
    ProfileSection,
    ProxySection,
)


class MarketClient:
    """
    Lolzteam Market API client.

    :param token:       Bearer token (required).
    :param proxy:       Proxy URL e.g. ``socks5://user:pass@host:1080``
    :param timeout:     Request timeout seconds (default 30).
    :param max_retries: Retries on 429/502/503 (default 5).
    :param language:    ``"ru"`` or ``"en"`` (default ``"en"``).

    Quick reference
    ---------------
    market.profile.profile_get()
    market.accounts_list.accounts_search(price_max=500)
    market.managing.managing_get(item_id=12345)
    market.purchasing.purchasing_fast_buy(item_id=12345, price=199.0)
    market.payments.payments_history()
    market.payments.payments_balance_list()
    market.payments.payments_transfer(amount=100, currency="rub", secret_answer="x")
    market.invoices.invoices_create(currency="rub", amount=100, payment_id="INV-1")
    market.steam.steam_get_mafile(item_id=12345)
    market.cart.cart_get()
    market.batch.batch_execute(requests=[...])
    """

    BASE_URL = "https://prod-api.lzt.market"

    def __init__(
        self,
        token: str,
        proxy: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_RETRY_COUNT,
        language: str = "en",
    ) -> None:
        self._transport = Transport(
            token=token, base_url=self.BASE_URL, proxy=proxy,
            timeout=timeout, max_retries=max_retries, language=language,
        )
        self.profile          = ProfileSection(self._transport)
        self.categories       = CategoriesSection(self._transport)
        self.category_search  = CategorySearchSection(self._transport)
        self.accounts_list    = AccountsListSection(self._transport)
        self.managing         = AccountsManagingSection(self._transport)
        self.publishing       = AccountPublishingSection(self._transport)
        self.purchasing       = AccountPurchasingSection(self._transport)
        self.cart             = CartSection(self._transport)
        self.payments         = PaymentsSection(self._transport)
        self.invoices         = InvoicesSection(self._transport)
        self.custom_discounts = CustomDiscountsSection(self._transport)
        self.proxy            = ProxySection(self._transport)
        self.imap             = ImapSection(self._transport)
        self.batch            = BatchRequestsSection(self._transport)

    def request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        return self._transport.request(method, path, **kwargs)

    async def request_async(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        return await self._transport.request_async(method, path, **kwargs)

    def close(self) -> None:
        self._transport.close()

    async def aclose(self) -> None:
        await self._transport.aclose()

    def __enter__(self) -> MarketClient:
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()

    async def __aenter__(self) -> MarketClient:
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.aclose()
