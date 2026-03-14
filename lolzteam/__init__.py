"""lolzteam — Python API wrapper for lolz.live (Forum) and lzt.market (Market)."""

from .clients.forum import ForumClient
from .clients.market import MarketClient
from ._http import LolzteamHTTPError, RateLimitError

__all__ = [
    "ForumClient",
    "MarketClient",
    "LolzteamHTTPError",
    "RateLimitError",
]

__version__ = "0.1.0"
__author__ = "lolzteam"
__license__ = "MIT"
