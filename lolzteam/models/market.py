"""
lolzteam.models.market
~~~~~~~~~~~~~~~~~~~~~~
Typed response models for Market API.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

try:
    from pydantic import BaseModel, Field

    _USE_PYDANTIC = True
except ImportError:
    _USE_PYDANTIC = False

if _USE_PYDANTIC:

    class Item(BaseModel):
        item_id: int
        item_state: Optional[str] = None
        published_date: Optional[int] = None
        title: Optional[str] = None
        description: Optional[str] = None
        price: Optional[float] = None
        currency: Optional[str] = None
        category_id: Optional[int] = None
        seller_id: Optional[int] = None
        buyer_id: Optional[int] = None
        views: Optional[int] = None
        is_sticky: Optional[int] = None
        update_stat_date: Optional[int] = None
        links: Optional[Dict[str, Any]] = None

        model_config = {"extra": "allow"}

    class MarketCategory(BaseModel):
        id: int
        title: str
        description: Optional[str] = None
        links: Optional[Dict[str, Any]] = None

        model_config = {"extra": "allow"}

    class Payment(BaseModel):
        payment_id: Optional[str] = None
        operation_type: Optional[str] = None
        created_at: Optional[int] = None
        incoming_sum: Optional[float] = None
        outgoing_sum: Optional[float] = None
        currency: Optional[str] = None
        comment: Optional[str] = None
        links: Optional[Dict[str, Any]] = None

        model_config = {"extra": "allow"}

    class Balance(BaseModel):
        balance: Optional[float] = None
        hold: Optional[float] = None
        currency: Optional[str] = None

        model_config = {"extra": "allow"}

else:
    from dataclasses import dataclass  # type: ignore[no-redef]

    @dataclass
    class Item:  # type: ignore[no-redef]
        item_id: int
        title: Optional[str] = None
        price: Optional[float] = None
        currency: Optional[str] = None

    @dataclass
    class MarketCategory:  # type: ignore[no-redef]
        id: int
        title: str

    @dataclass
    class Payment:  # type: ignore[no-redef]
        payment_id: Optional[str] = None
        operation_type: Optional[str] = None

    @dataclass
    class Balance:  # type: ignore[no-redef]
        balance: Optional[float] = None
        currency: Optional[str] = None


__all__ = ["Item", "MarketCategory", "Payment", "Balance"]
