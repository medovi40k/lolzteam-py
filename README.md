# lolzteam-py

> **Python API wrapper for [lolz.live](https://lolz.live) (Forum) and [lzt.market](https://lzt.market) (Market)**

[![PyPI](https://img.shields.io/pypi/v/lolzteam)](https://pypi.org/project/lolzteam/)
[![Python](https://img.shields.io/pypi/pyversions/lolzteam)](https://pypi.org/project/lolzteam/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/lolzteam/lolzteam-py/actions/workflows/ci.yml/badge.svg)](https://github.com/lolzteam/lolzteam-py/actions/workflows/ci.yml)

---

## Features

- ✅ **Full Forum API** — categories, forums, threads, posts, profile posts, conversations, notifications, search, tags, batch
- ✅ **Full Market API** — listings, buy/reserve, cart, payments, invoices, payouts, managing, Steam accounts
- ⚡ **Sync & Async** — every method has a synchronous version and an `_async` twin
- 🔄 **Auto-retry** — automatic retry on `429` (rate limit), `502` and `503` with exponential back-off
- 🌐 **Proxy support** — pass any `socks5://` or `http://` proxy
- 🔧 **Code generator** — all methods are generated from OpenAPI schemas; regenerate any time
- 📦 **Optional deps** — use only `requests` for sync, only `httpx` for async, or both

---

## Installation

```bash
# Sync usage (uses requests)
pip install "lolzteam[sync]"

# Async usage (uses httpx)
pip install "lolzteam[async]"

# Both + Pydantic models
pip install "lolzteam[all]"
```

Requires **Python 3.9+**.

---

## Quick start

### Sync

```python
from lolzteam import ForumClient, MarketClient

# Forum
forum = ForumClient(token="YOUR_TOKEN")

me = forum.users.users_me()
print(me["user"]["username"])

threads = forum.threads.threads_list(forum_id=176, limit=20)
for t in threads["threads"]:
    print(t["thread_id"], t["thread_title"])

forum.close()

# Market
market = MarketClient(token="YOUR_TOKEN")

# Профиль
me = market.profile.profile_get()
print(me)

# Поиск аккаунтов
items = market.accounts_list.accounts_search(price_max=500)
for item in items.get("items", []):
    print(item["item_id"], item["price"])

# Покупка
market.purchasing.purchasing_fast_buy(item_id=12345, price=199.0)

# История платежей
history = market.payments.payments_history()

# Балансы
balances = market.payments.payments_balance_list()

market.close()
```

### Async

```python
import asyncio
from lolzteam import ForumClient, MarketClient

async def main():
    forum = ForumClient(token="YOUR_TOKEN")

    me = await forum.users.users_me_async()
    print(me["user"]["username"])

    # Create a post
    post = await forum.posts.posts_create_async(
        thread_id=12345,
        post_body="Hello from lolzteam-py!",
    )

    await forum.aclose()

asyncio.run(main())
```

### Context managers

```python
# Sync
with ForumClient(token="YOUR_TOKEN") as forum:
    me = forum.users.users_me()

# Async
async with ForumClient(token="YOUR_TOKEN") as forum:
    me = await forum.users.users_me_async()
```

---

## Proxy support

Pass any proxy URL via the `proxy=` parameter. Authorization credentials go directly in the URL.

```python
# SOCKS5 с авторизацией (sync)
client = ForumClient(
    token="YOUR_TOKEN",
    proxy="socks5://user:pass@192.168.1.1:1080",
)

# SOCKS5 без авторизации (sync)
client = ForumClient(
    token="YOUR_TOKEN",
    proxy="socks5://192.168.1.1:1080",
)

# HTTP прокси с авторизацией (sync + async)
client = MarketClient(
    token="YOUR_TOKEN",
    proxy="http://user:pass@192.168.1.1:8080",
)

# HTTPS прокси (sync + async)
client = ForumClient(
    token="YOUR_TOKEN",
    proxy="https://user:pass@proxy.example.com:3128",
)
```

### Поддерживаемые форматы

| Формат | Sync (`requests`) | Async (`httpx`) |
|--------|:-----------------:|:---------------:|
| `http://host:port` | ✅ | ✅ |
| `http://user:pass@host:port` | ✅ | ✅ |
| `https://user:pass@host:port` | ✅ | ✅ |
| `socks5://host:port` | ✅ (нужен `requests[socks]`) | ✅ (нужен `httpx[socks]`) |
| `socks5://user:pass@host:port` | ✅ | ✅ |
| `socks5h://user:pass@host:port` | ✅ | ✅ |

> **SOCKS5 для async** требует пакет `socksio`:
> ```bash
> pip install "httpx[socks]"
> # или через extras:
> pip install "lolzteam[async]"   # уже включает httpx[socks]
> ```

> **SOCKS5 для sync** требует `PySocks`:
> ```bash
> pip install "requests[socks]"
> ```

---

## Retry behaviour

By default the library retries up to **5 times** on:

| Status | Meaning |
|--------|---------|
| `429`  | Rate limited |
| `502`  | Bad Gateway |
| `503`  | Service Unavailable |

Retry delay starts at **1 second** and doubles each attempt (capped at 60 s).
If a `Retry-After` header is present it takes precedence.

Customise:

```python
client = ForumClient(
    token="YOUR_TOKEN",
    max_retries=10,   # more retries
    timeout=60.0,     # longer timeout
)
```

---

## Raw requests

Need an endpoint not covered by generated methods? Use the raw helper:

```python
result = forum.request("GET", "/navigation")
result = await forum.request_async("POST", "/batch", json={"requests": [...]})
```

---

## Forum API sections

| Section | Attribute | Methods |
|---------|-----------|---------|
| Categories | `forum.categories` | `categories_list`, `categories_get` |
| Forums | `forum.forums` | `forums_list`, `forums_tree`, `forums_get`, `forums_follow`, … |
| Users | `forum.users` | `users_me`, `users_get`, `users_find`, `users_edit`, `users_follow`, … |
| Threads | `forum.threads` | `threads_list`, `threads_get`, `threads_create`, `threads_edit`, `threads_delete`, `threads_bump`, … |
| Posts | `forum.posts` | `posts_list`, `posts_get`, `posts_create`, `posts_edit`, `posts_delete`, `posts_like`, … |
| Profile Posts | `forum.profile_posts` | `profile_posts_list`, `profile_posts_create`, `profile_posts_like`, … |
| Conversations | `forum.conversations` | `conversations_list`, `conversations_get`, `conversations_create`, `conversations_messages_list`, … |
| Notifications | `forum.notifications` | `notifications_list`, `notifications_get`, `notifications_read` |
| Search | `forum.search` | `search_all`, `search_threads`, `search_posts`, `search_users` |
| Tags | `forum.tags` | `tags_list`, `tags_popular` |
| Batch | `forum.batch` | `batch_execute` |

Every method has a `_async` counterpart (`threads_create` → `threads_create_async`).

---

## Market API sections

| Section | Attribute | Ключевые методы |
|---------|-----------|-----------------|
| Profile | `market.profile` | `profile_get`, `profile_edit`, `profile_claims` |
| Categories | `market.categories` | `categories_get`, `categories_params`, `categories_games` |
| Accounts list | `market.accounts_list` | `accounts_search`, `accounts_search_steam`, `accounts_search_fortnite`, `accounts_search_telegram`, `list_orders`, `list_favorites`, `list_viewed`, `list_user_items` |
| Managing | `market.managing` | `managing_get`, `managing_edit`, `managing_delete`, `managing_bump`, `managing_auto_bump`, `managing_transfer`, `managing_favorite`, `managing_open`, `managing_close`, `managing_tag`, `managing_stick`, `managing_change_password`, `managing_check_guarantee`, `managing_ai_price` |
| Steam | `market.steam` | `steam_get_mafile`, `steam_add_mafile`, `steam_remove_mafile`, `steam_guard_code`, `steam_confirm_sda`, `steam_inventory_value`, `steam_update_inventory_value` |
| Telegram | `market.telegram` | `telegram_confirmation_code`, `telegram_reset_auth` |
| Publishing | `market.publishing` | `publishing_fast_sell`, `publishing_add`, `publishing_check` |
| Purchasing | `market.purchasing` | `purchasing_fast_buy`, `purchasing_check`, `purchasing_confirm`, `purchasing_discount_request`, `purchasing_discount_cancel` |
| Cart | `market.cart` | `cart_get`, `cart_add`, `cart_delete` |
| Payments | `market.payments` | `payments_history`, `payments_balance_list`, `payments_transfer`, `payments_cancel_transfer`, `payments_balance_exchange`, `payments_payout`, `payments_payout_services`, `payments_fee`, `payments_currency`, `payments_auto_list`, `payments_auto_create`, `payments_auto_delete` |
| Invoices | `market.invoices` | `invoices_list`, `invoices_get`, `invoices_create` |
| Custom Discounts | `market.custom_discounts` | `custom_discounts_get`, `custom_discounts_create`, `custom_discounts_edit`, `custom_discounts_delete` |
| Proxy | `market.proxy` | `proxy_get`, `proxy_add`, `proxy_delete` |
| IMAP | `market.imap` | `imap_create`, `imap_delete` |
| Batch | `market.batch` | `batch_execute` |

Every method has a `_async` counterpart (`purchasing_fast_buy` → `purchasing_fast_buy_async`).

---

## Code generator

All API methods are **auto-generated** from OpenAPI JSON schemas in `codegen/`.

```bash
# Regenerate all sections (after editing a schema)
python codegen/generate.py --all

# Or generate a specific schema
python codegen/generate.py \
  --schema codegen/forum_openapi.json \
  --output lolzteam/sections/_forum_generated.py
```

The generator produces:
- One class per tag (e.g. `UsersSection`, `ThreadsSection`)
- One sync method per operation (e.g. `threads_create`)
- One async method per operation (e.g. `threads_create_async`)

---

## Development

```bash
git clone https://github.com/lolzteam/lolzteam-py.git
cd lolzteam-py
pip install -e ".[dev]"

# Regenerate sections
python codegen/generate.py --all

# Run tests
pytest

# Run tests with coverage
pytest --cov=lolzteam --cov-report=term-missing

# Lint
ruff check lolzteam/ codegen/

# Type check
mypy lolzteam/
```

---

## Release

Releases are fully automated via GitHub Actions:

1. Bump the version in `pyproject.toml`
2. Commit and push
3. Create a tag: `git tag v0.2.0 && git push origin v0.2.0`
4. GitHub Actions will:
   - Run tests on Python 3.9 – 3.12
   - Build the wheel and sdist
   - Publish to PyPI via OIDC trusted publishing (no API token needed)
   - Create a GitHub Release with changelog

---

## Error handling

```python
from lolzteam import ForumClient, LolzteamHTTPError, RateLimitError

client = ForumClient(token="YOUR_TOKEN")

try:
    result = client.threads.threads_get(thread_id=999999)
except RateLimitError:
    print("Rate limited even after retries")
except LolzteamHTTPError as e:
    print(f"HTTP {e.status_code}: {e.response_body}")
```

---

## License

MIT — see [LICENSE](LICENSE).
