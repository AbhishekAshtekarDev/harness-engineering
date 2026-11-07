"""A fake order database for a small online shop (deterministic, no network)."""
from __future__ import annotations

import random
import uuid
from datetime import date, timedelta

PRODUCTS = [("Blue running shoes", 89.0), ("Trail socks (3 pack)", 18.5), ("Rain jacket", 120.0),
            ("Water bottle", 24.0), ("Headlamp", 39.9), ("Yoga mat", 45.0), ("Gym bag", 60.0)]
STATUSES = ["delivered", "delivered", "delivered", "shipped", "processing", "refunded"]
TODAY = date(2026, 3, 25)


def build_orders() -> list[dict]:
    rng = random.Random(42)
    orders = []
    customers = ["maya@example.com", "li.wei@example.com", "sam@example.com"]
    for n in range(40):
        name, price = rng.choice(PRODUCTS)
        qty = rng.choice([1, 1, 1, 2])
        orders.append({
            "id": str(uuid.UUID(int=rng.getrandbits(128))),       # internal key
            "number": f"A{1000 + n}",                              # what customers see
            "customer": customers[n % 3],
            "created": (TODAY - timedelta(days=rng.randint(0, 400))).isoformat(),
            "items": [{"sku": f"SKU-{rng.randint(10000, 99999)}", "name": name, "qty": qty, "unit_price": price}],
            "total": round(price * qty, 2),
            "status": rng.choice(STATUSES),
            "warehouse_code": f"WH-{rng.randint(1, 9)}-{rng.randint(100, 999)}",
            "shipping_address": f"{rng.randint(1, 99)} Example Street",
        })
    rng.shuffle(orders)  # the database returns rows in no useful order
    return orders


ORDERS = build_orders()
