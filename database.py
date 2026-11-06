"""
Database layer (SQLite via aiosqlite).

Every function opens a short connection, runs its query and returns plain
dicts, so handlers never deal with SQL directly.
"""
from typing import Optional

import aiosqlite

from config import DB_PATH

# Demo catalog that is inserted on the first launch:
# (category name, category emoji, [(name, description, price, emoji, photo URL), ...])
_UNSPLASH = "https://images.unsplash.com/photo-{}?w=800&q=80"

DEMO_CATALOG = [
    ("Coffee", "☕", [
        ("Espresso", "A short, intense shot of freshly ground arabica. The classic morning boost.",
         2.50, "☕", _UNSPLASH.format("1510591509098-f4fdc6d0ff04")),
        ("Cappuccino", "Espresso with steamed milk and a thick layer of velvety foam.",
         3.50, "☕", _UNSPLASH.format("1572442388796-11668a67e53d")),
        ("Latte", "Mild and creamy: a shot of espresso with lots of steamed milk.",
         3.90, "🥛", _UNSPLASH.format("1541167760496-1628856ab772")),
    ]),
    ("Tea", "🍵", [
        ("Matcha Latte", "Japanese green matcha whisked with warm milk. Smooth and energizing.",
         4.20, "🍵", _UNSPLASH.format("1515823064-d6e0c04616a7")),
        ("Black Tea", "Strong Ceylon black tea, brewed fresh for every order.",
         2.20, "🫖", _UNSPLASH.format("1576092768241-dec231879fc3")),
        ("Iced Lemon Tea", "Chilled black tea with lemon and mint. Perfect for a hot day.",
         3.00, "🧊", _UNSPLASH.format("1556679343-c7306c1976bc")),
    ]),
    ("Desserts", "🍰", [
        ("Cheesecake", "Classic New York cheesecake on a crunchy biscuit base.",
         4.50, "🍰", _UNSPLASH.format("1524351199678-941a58a3df50")),
        ("Croissant", "Buttery French croissant, baked every morning.",
         2.80, "🥐", _UNSPLASH.format("1555507036-ab1f4038808a")),
        ("Chocolate Brownie", "Rich, fudgy brownie made with dark Belgian chocolate.",
         3.20, "🍫", _UNSPLASH.format("1606313564200-e75d5e30476c")),
    ]),
]


# ---------- small helpers ----------

async def _fetchall(query: str, params: tuple = ()) -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row  # rows behave like dicts: row["name"]
        async with db.execute(query, params) as cursor:
            return [dict(row) for row in await cursor.fetchall()]


async def _fetchone(query: str, params: tuple = ()) -> Optional[dict]:
    rows = await _fetchall(query, params)
    return rows[0] if rows else None


async def _execute(query: str, params: tuple = ()) -> int:
    """Run INSERT/UPDATE/DELETE and return the id of the inserted row."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(query, params)
        await db.commit()
        return cursor.lastrowid


# ---------- setup ----------

async def init_db() -> None:
    """Create tables (if they don't exist yet) and add demo products on the first launch."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id    INTEGER PRIMARY KEY,
                username   TEXT,
                lang       TEXT DEFAULT 'en',
                created_at TEXT DEFAULT (datetime('now', 'localtime'))
            );
            CREATE TABLE IF NOT EXISTS categories (
                id    INTEGER PRIMARY KEY AUTOINCREMENT,
                name  TEXT NOT NULL,
                emoji TEXT DEFAULT '🛍'
            );
            CREATE TABLE IF NOT EXISTS products (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER NOT NULL REFERENCES categories(id),
                name        TEXT NOT NULL,
                description TEXT,
                price       REAL NOT NULL,
                emoji       TEXT DEFAULT '🛍',
                photo       TEXT  -- Telegram file_id or image URL, NULL = emoji placeholder
            );
            CREATE TABLE IF NOT EXISTS cart (
                user_id    INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity   INTEGER NOT NULL,
                PRIMARY KEY (user_id, product_id)
            );
            CREATE TABLE IF NOT EXISTS orders (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id       INTEGER NOT NULL,
                customer_name TEXT,
                phone         TEXT,
                address       TEXT,
                comment       TEXT,  -- optional wishes from the customer
                total         REAL,
                status        TEXT DEFAULT 'new',
                created_at    TEXT DEFAULT (datetime('now', 'localtime'))
            );
            -- Name and price are copied into the order, so the history
            -- stays correct even if the product is later edited or deleted.
            CREATE TABLE IF NOT EXISTS order_items (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id     INTEGER NOT NULL REFERENCES orders(id),
                product_name TEXT,
                price        REAL,
                quantity     INTEGER
            );
        """)

        # Migration: databases created before the comment feature don't have this column
        cursor = await db.execute("PRAGMA table_info(orders)")
        columns = [row[1] for row in await cursor.fetchall()]
        if "comment" not in columns:
            await db.execute("ALTER TABLE orders ADD COLUMN comment TEXT")

        cursor = await db.execute("SELECT COUNT(*) FROM categories")
        (count,) = await cursor.fetchone()
        if count == 0:
            for cat_name, cat_emoji, products in DEMO_CATALOG:
                cursor = await db.execute(
                    "INSERT INTO categories (name, emoji) VALUES (?, ?)", (cat_name, cat_emoji)
                )
                category_id = cursor.lastrowid
                await db.executemany(
                    "INSERT INTO products (category_id, name, description, price, emoji, photo) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    [(category_id, *product) for product in products],
                )
        await db.commit()


# ---------- users ----------

async def add_user(user_id: int, username: Optional[str]) -> None:
    await _execute(
        "INSERT INTO users (user_id, username) VALUES (?, ?) "
        "ON CONFLICT(user_id) DO UPDATE SET username = excluded.username",
        (user_id, username),
    )


async def set_lang(user_id: int, lang: str) -> None:
    await _execute(
        "INSERT INTO users (user_id, lang) VALUES (?, ?) "
        "ON CONFLICT(user_id) DO UPDATE SET lang = excluded.lang",
        (user_id, lang),
    )


async def get_lang(user_id: int) -> str:
    row = await _fetchone("SELECT lang FROM users WHERE user_id = ?", (user_id,))
    return row["lang"] if row else "en"


async def get_all_user_ids() -> list:
    rows = await _fetchall("SELECT user_id FROM users")
    return [row["user_id"] for row in rows]


# ---------- catalog ----------

async def get_categories() -> list:
    return await _fetchall("SELECT * FROM categories ORDER BY id")


async def get_category(category_id: int) -> Optional[dict]:
    return await _fetchone("SELECT * FROM categories WHERE id = ?", (category_id,))


async def get_products(category_id: int) -> list:
    return await _fetchall(
        "SELECT * FROM products WHERE category_id = ? ORDER BY id", (category_id,)
    )


async def get_all_products() -> list:
    return await _fetchall("SELECT * FROM products ORDER BY category_id, id")


async def get_product(product_id: int) -> Optional[dict]:
    return await _fetchone("SELECT * FROM products WHERE id = ?", (product_id,))


async def add_product(category_id: int, name: str, description: str,
                      price: float, emoji: str, photo: Optional[str]) -> int:
    return await _execute(
        "INSERT INTO products (category_id, name, description, price, emoji, photo) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (category_id, name, description, price, emoji, photo),
    )


async def set_product_photo(product_id: int, photo: str) -> None:
    await _execute("UPDATE products SET photo = ? WHERE id = ?", (photo, product_id))


async def delete_product(product_id: int) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM cart WHERE product_id = ?", (product_id,))
        await db.execute("DELETE FROM products WHERE id = ?", (product_id,))
        await db.commit()


# ---------- cart ----------

async def add_to_cart(user_id: int, product_id: int, quantity: int) -> None:
    # If the product is already in the cart, increase its quantity (max 99)
    await _execute(
        "INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, ?) "
        "ON CONFLICT(user_id, product_id) "
        "DO UPDATE SET quantity = MIN(quantity + excluded.quantity, 99)",
        (user_id, product_id, quantity),
    )


async def get_cart(user_id: int) -> list:
    return await _fetchall(
        "SELECT c.product_id, c.quantity, p.name, p.price, p.emoji "
        "FROM cart c JOIN products p ON p.id = c.product_id "
        "WHERE c.user_id = ? ORDER BY c.rowid",
        (user_id,),
    )


async def change_cart_qty(user_id: int, product_id: int, delta: int) -> None:
    """Add delta (+1 / -1) to the quantity; an item that drops to 0 is removed."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE cart SET quantity = MIN(quantity + ?, 99) WHERE user_id = ? AND product_id = ?",
            (delta, user_id, product_id),
        )
        await db.execute("DELETE FROM cart WHERE user_id = ? AND quantity <= 0", (user_id,))
        await db.commit()


async def remove_from_cart(user_id: int, product_id: int) -> None:
    await _execute("DELETE FROM cart WHERE user_id = ? AND product_id = ?", (user_id, product_id))


async def clear_cart(user_id: int) -> None:
    await _execute("DELETE FROM cart WHERE user_id = ?", (user_id,))


# ---------- orders ----------

async def create_order(user_id: int, name: str, phone: str, address: str,
                       comment: Optional[str] = None) -> Optional[int]:
    """Turn the user's cart into an order. Returns the order id, or None if the cart is empty."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT p.name, p.price, c.quantity "
            "FROM cart c JOIN products p ON p.id = c.product_id WHERE c.user_id = ?",
            (user_id,),
        )
        items = await cursor.fetchall()
        if not items:
            return None

        total = round(sum(item["price"] * item["quantity"] for item in items), 2)
        cursor = await db.execute(
            "INSERT INTO orders (user_id, customer_name, phone, address, comment, total) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, name, phone, address, comment, total),
        )
        order_id = cursor.lastrowid
        await db.executemany(
            "INSERT INTO order_items (order_id, product_name, price, quantity) VALUES (?, ?, ?, ?)",
            [(order_id, item["name"], item["price"], item["quantity"]) for item in items],
        )
        await db.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
        await db.commit()  # everything above is saved together, or not at all
        return order_id


async def get_order(order_id: int) -> Optional[dict]:
    return await _fetchone(
        "SELECT o.*, u.username FROM orders o "
        "LEFT JOIN users u ON u.user_id = o.user_id WHERE o.id = ?",
        (order_id,),
    )


async def get_order_items(order_id: int) -> list:
    return await _fetchall(
        "SELECT product_name AS name, price, quantity FROM order_items WHERE order_id = ?",
        (order_id,),
    )


async def get_user_orders(user_id: int, limit: int = 10) -> list:
    return await _fetchall(
        "SELECT * FROM orders WHERE user_id = ? ORDER BY id DESC LIMIT ?", (user_id, limit)
    )


async def get_last_orders(limit: int = 10) -> list:
    return await _fetchall("SELECT * FROM orders ORDER BY id DESC LIMIT ?", (limit,))


async def set_order_status(order_id: int, status: str) -> None:
    await _execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))


async def get_stats() -> dict:
    totals = await _fetchone(
        "SELECT COUNT(*) AS orders, "
        "COALESCE(SUM(CASE WHEN status != 'cancelled' THEN total END), 0) AS revenue "
        "FROM orders"
    )
    users = await _fetchone("SELECT COUNT(*) AS count FROM users")
    by_status = await _fetchall("SELECT status, COUNT(*) AS count FROM orders GROUP BY status")
    return {
        "users": users["count"],
        "orders": totals["orders"],
        "revenue": totals["revenue"],
        "by_status": {row["status"]: row["count"] for row in by_status},
    }
