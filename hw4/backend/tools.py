"""Tools the chat agent uses to read the shop's catalogue and inventory.

These are plain functions over a read-only database connection; `agent.py` registers
them as agent tools. Every price and quantity comes straight from `campus_customs.db`,
so the agent never has to invent product info or stock. Keeping the tools here (separate
from the agent wiring) makes them easy to read and test on their own.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path

from models import Customer, ProductDetails, ProductSummary, SizeAvailability, SizeStock

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DB_PATH = DATA_DIR / "campus_customs.db"
SIZE_ORDER = ["XS", "S", "M", "L", "XL", "XXL"]


@dataclass
class ChatDeps:
    """Per-request context handed to the agent's tools.

    - `customer`: who is chatting (None for guests), so the agent can greet and personalize.
    - `current_product_id`: the product the shopper is viewing, so "this"/"it" resolves.
    - `last_search_ids`: product_ids the most recent `search_catalogue` returned, so the output
      validator can insist the model actually surfaces them as cards.
    """

    customer: Customer | None = None
    current_product_id: str | None = None
    last_search_ids: list[str] = field(default_factory=list)

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        return conn


def who_is_chatting(deps: ChatDeps) -> Customer:
    """The current shopper's identity, or a guest marker if they aren't signed in."""
    return deps.customer or Customer(logged_in=False)


def product_name(deps: ChatDeps, product_id: str) -> str | None:
    """The display name for a product id, or None if it's unknown."""
    with deps.connect() as conn:
        row = conn.execute("SELECT name FROM catalogue WHERE product_id = ?", (product_id,)).fetchone()
    return row["name"] if row else None


def _size_key(size: str) -> int:
    return SIZE_ORDER.index(size) if size in SIZE_ORDER else len(SIZE_ORDER)


def _load_sizes(conn: sqlite3.Connection, product_id: str) -> list[SizeStock]:
    rows = conn.execute(
        "SELECT size, quantity FROM inventory WHERE product_id = ?", (product_id,)
    ).fetchall()
    sizes = [SizeStock(size=r["size"], quantity=r["quantity"], available=r["quantity"] > 0) for r in rows]
    sizes.sort(key=lambda s: _size_key(s.size))
    return sizes


def search_catalogue(
    deps: ChatDeps,
    query: str,
    limit: int = 8,
    max_price: float | None = None,
    min_price: float | None = None,
) -> list[ProductSummary]:
    """Find products by keyword across name, type, description, colors, and tags.

    Optional `max_price` / `min_price` (USD) filter by budget, so "hoodies under $70" is exact.
    Results are ranked in-stock first, then by keyword relevance, and each carries an `in_stock`
    flag. Use get_product_details or check_size_stock for full price and per-size stock.
    """
    terms = [t for t in query.lower().split() if t]
    with deps.connect() as conn:
        rows = conn.execute(
            """
            SELECT c.*, COALESCE(SUM(i.quantity), 0) AS total_stock
            FROM catalogue c
            LEFT JOIN inventory i ON i.product_id = c.product_id
            GROUP BY c.product_id
            """
        ).fetchall()
    scored: list[tuple[int, bool, sqlite3.Row]] = []
    for row in rows:
        if max_price is not None and row["price"] > max_price:
            continue
        if min_price is not None and row["price"] < min_price:
            continue
        haystack = " ".join(
            [row["name"], row["garment_type"], row["description"], row["colors"], row["search_tags"]]
        ).lower()
        score = sum(haystack.count(term) for term in terms)
        if score:
            scored.append((score, row["total_stock"] > 0, row))
    # In-stock first, then higher keyword relevance.
    scored.sort(key=lambda t: (t[1], t[0]), reverse=True)
    hits = [
        ProductSummary(
            product_id=row["product_id"],
            name=row["name"],
            garment_type=row["garment_type"],
            colors=json.loads(row["colors"]),
            price=row["price"],
            in_stock=in_stock,
        )
        for _, in_stock, row in scored[: max(1, min(limit, 20))]
    ]
    # Remember what we found so the agent is nudged to actually show these as cards.
    deps.last_search_ids = [h.product_id for h in hits]
    return hits


def get_product_details(deps: ChatDeps, product_id: str) -> ProductDetails | None:
    """Full info for one product: description, price, colors, and per-size stock.

    Returns None if no product has that id (the agent should search first).
    """
    with deps.connect() as conn:
        row = conn.execute("SELECT * FROM catalogue WHERE product_id = ?", (product_id,)).fetchone()
        if row is None:
            return None
        sizes = _load_sizes(conn, product_id)
    return ProductDetails(
        product_id=row["product_id"],
        name=row["name"],
        garment_type=row["garment_type"],
        description=row["description"],
        colors=json.loads(row["colors"]),
        price=row["price"],
        sizes=sizes,
        in_stock=any(s.available for s in sizes),
    )


def check_size_stock(deps: ChatDeps, product_id: str, size: str) -> SizeAvailability | None:
    """Stock for one product in one size, with a clear in/out-of-stock message.

    Returns None if the product id is unknown.
    """
    size = size.strip().upper()
    with deps.connect() as conn:
        row = conn.execute(
            "SELECT name FROM catalogue WHERE product_id = ?", (product_id,)
        ).fetchone()
        if row is None:
            return None
        stock = conn.execute(
            "SELECT quantity FROM inventory WHERE product_id = ? AND size = ?", (product_id, size)
        ).fetchone()

    name = row["name"]
    if stock is None:
        return SizeAvailability(
            product_id=product_id, name=name, size=size, quantity=0, available=False,
            message=f"{name} doesn't come in size {size}.",
        )
    quantity = stock["quantity"]
    if quantity <= 0:
        message = f"{name} is sold out in size {size}."
    elif quantity <= 5:
        message = f"{name} in size {size}: only {quantity} left."
    else:
        message = f"{name} is in stock in size {size}."
    return SizeAvailability(
        product_id=product_id, name=name, size=size, quantity=quantity, available=quantity > 0, message=message,
    )
