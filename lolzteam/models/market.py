"""
lolzteam.models.market
~~~~~~~~~~~~~~~~~~~~~~
Typed response models for Market API.
"""

from __future__ import annotations

from typing import Any

try:
    from pydantic import BaseModel

    _USE_PYDANTIC = True
except ImportError:
    _USE_PYDANTIC = False

if _USE_PYDANTIC:

    class Item(BaseModel):
        item_id: int
        item_state: str | None = None
        published_date: int | None = None
        title: str | None = None
        description: str | None = None
        price: float | None = None
        currency: str | None = None
        category_id: int | None = None
        seller_id: int | None = None
        buyer_id: int | None = None
        views: int | None = None
        is_sticky: int | None = None
        update_stat_date: int | None = None
        links: dict[str, Any] | None = None

        model_config = {"extra": "allow"}

    class MarketCategory(BaseModel):
        id: int
        title: str
        description: str | None = None
        links: dict[str, Any] | None = None

        model_config = {"extra": "allow"}

    class Payment(BaseModel):
        payment_id: str | None = None
        operation_type: str | None = None
        created_at: int | None = None
        incoming_sum: float | None = None
        outgoing_sum: float | None = None
        currency: str | None = None
        comment: str | None = None
        links: dict[str, Any] | None = None

        model_config = {"extra": "allow"}

    class Balance(BaseModel):
        balance: float | None = None
        hold: float | None = None
        currency: str | None = None

        model_config = {"extra": "allow"}

else:
    from dataclasses import dataclass  # type: ignore[no-redef]

    @dataclass
    class Item:  # type: ignore[no-redef]
        item_id: int
        title: str | None = None
        price: float | None = None
        currency: str | None = None

    @dataclass
    class MarketCategory:  # type: ignore[no-redef]
        id: int
        title: str

    @dataclass
    class Payment:  # type: ignore[no-redef]
        payment_id: str | None = None
        operation_type: str | None = None

    @dataclass
    class Balance:  # type: ignore[no-redef]
        balance: float | None = None
        currency: str | None = None


__all__ = ["Item", "MarketCategory", "Payment", "Balance"]
