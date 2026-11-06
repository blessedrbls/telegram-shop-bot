"""
All keyboards of the bot.

Reply keyboards sit below the input field (main menu, "Share phone number").
Inline keyboards are attached to messages; their buttons send callback data
that we describe with CallbackData classes below.
"""
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from config import ADMIN_STATUSES
from texts import LANGUAGES, price, t


# ---------- callback data ----------
# A CallbackData class packs fields into a short string like "qty:inc:5:1:2"
# and unpacks it back when the button is pressed.

class LangCB(CallbackData, prefix="lang"):
    code: str


class CategoryCB(CallbackData, prefix="cat"):
    id: int


class ProductCB(CallbackData, prefix="prod"):
    id: int


class QtyCB(CallbackData, prefix="qty"):
    action: str  # "inc", "dec" or "add"
    product_id: int
    category_id: int
    qty: int


class CartCB(CallbackData, prefix="cart"):
    action: str  # "inc", "dec", "del", "clear" or "checkout"
    product_id: int = 0


class StatusCB(CallbackData, prefix="status"):
    order_id: int
    status: str


class AdminCB(CallbackData, prefix="adm"):
    action: str
    id: int = 0


# Buttons that only display information (e.g. quantity) use this callback
NOOP = "noop"


# ---------- reply keyboards ----------

def main_menu_kb(lang: str) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text=t(lang, "btn_catalog"))
    builder.button(text=t(lang, "btn_cart"))
    builder.button(text=t(lang, "btn_orders"))
    builder.button(text=t(lang, "btn_language"))
    builder.adjust(2)  # 2 buttons per row
    return builder.as_markup(resize_keyboard=True)


def cancel_kb(lang: str) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text=t(lang, "btn_cancel"))
    return builder.as_markup(resize_keyboard=True)


def comment_kb(lang: str) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text=t(lang, "btn_skip"))
    builder.button(text=t(lang, "btn_cancel"))
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


def phone_kb(lang: str) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text=t(lang, "btn_share_phone"), request_contact=True)
    builder.button(text=t(lang, "btn_cancel"))
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


# ---------- customer inline keyboards ----------

def language_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for code, title in LANGUAGES.items():
        builder.button(text=title, callback_data=LangCB(code=code))
    return builder.as_markup()


def categories_kb(categories: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for cat in categories:
        builder.button(text=f"{cat['emoji']} {cat['name']}", callback_data=CategoryCB(id=cat["id"]))
    builder.adjust(1)
    return builder.as_markup()


def products_kb(products: list, lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for p in products:
        builder.button(
            text=f"{p['emoji']} {p['name']} — {price(p['price'])}",
            callback_data=ProductCB(id=p["id"]),
        )
    builder.button(text=t(lang, "btn_back"), callback_data="catalog")
    builder.adjust(1)
    return builder.as_markup()


def product_kb(product_id: int, category_id: int, qty: int, lang: str) -> InlineKeyboardMarkup:
    """Product card: [➖] [2 pcs] [➕] / [Add to cart] / [Back]"""
    def qty_button(text: str, action: str) -> InlineKeyboardButton:
        data = QtyCB(action=action, product_id=product_id, category_id=category_id, qty=qty)
        return InlineKeyboardButton(text=text, callback_data=data.pack())

    builder = InlineKeyboardBuilder()
    builder.row(
        qty_button("➖", "dec"),
        InlineKeyboardButton(text=t(lang, "qty_label", qty=qty), callback_data=NOOP),
        qty_button("➕", "inc"),
    )
    builder.row(qty_button(t(lang, "btn_add_to_cart"), "add"))
    builder.row(InlineKeyboardButton(
        text=t(lang, "btn_back"), callback_data=CategoryCB(id=category_id).pack()
    ))
    return builder.as_markup()


def cart_kb(items: list, lang: str) -> InlineKeyboardMarkup:
    """One row per item: [➖] [Latte × 2] [➕] [🗑], then [Clear] [Checkout]."""
    builder = InlineKeyboardBuilder()
    for item in items:
        pid = item["product_id"]
        builder.row(
            InlineKeyboardButton(text="➖", callback_data=CartCB(action="dec", product_id=pid).pack()),
            InlineKeyboardButton(text=f"{item['emoji']} {item['name']} × {item['quantity']}",
                                 callback_data=NOOP),
            InlineKeyboardButton(text="➕", callback_data=CartCB(action="inc", product_id=pid).pack()),
            InlineKeyboardButton(text="🗑", callback_data=CartCB(action="del", product_id=pid).pack()),
        )
    builder.row(
        InlineKeyboardButton(text=t(lang, "btn_clear_cart"), callback_data=CartCB(action="clear").pack()),
        InlineKeyboardButton(text=t(lang, "btn_checkout"), callback_data=CartCB(action="checkout").pack()),
    )
    return builder.as_markup()


def confirm_order_kb(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_confirm"), callback_data="order_confirm")
    builder.button(text=t(lang, "btn_cancel"), callback_data="order_cancel")
    return builder.as_markup()


# ---------- admin inline keyboards ----------

def admin_menu_kb(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "adm_btn_add"), callback_data=AdminCB(action="add"))
    builder.button(text=t(lang, "adm_btn_delete"), callback_data=AdminCB(action="delete"))
    builder.button(text=t(lang, "adm_btn_orders"), callback_data=AdminCB(action="orders"))
    builder.button(text=t(lang, "adm_btn_stats"), callback_data=AdminCB(action="stats"))
    builder.button(text=t(lang, "adm_btn_broadcast"), callback_data=AdminCB(action="broadcast"))
    builder.adjust(2, 2, 1)
    return builder.as_markup()


def back_to_panel_kb(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "adm_btn_panel"), callback_data=AdminCB(action="menu"))
    return builder.as_markup()


def admin_categories_kb(categories: list, lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for cat in categories:
        builder.button(text=f"{cat['emoji']} {cat['name']}",
                       callback_data=AdminCB(action="add_cat", id=cat["id"]))
    builder.button(text=t(lang, "adm_btn_panel"), callback_data=AdminCB(action="menu"))
    builder.adjust(1)
    return builder.as_markup()


def admin_products_kb(products: list, lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for p in products:
        builder.button(text=f"🗑 {p['emoji']} {p['name']} — {price(p['price'])}",
                       callback_data=AdminCB(action="del", id=p["id"]))
    builder.button(text=t(lang, "adm_btn_panel"), callback_data=AdminCB(action="menu"))
    builder.adjust(1)
    return builder.as_markup()


def admin_delete_confirm_kb(product_id: int, lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_delete_yes"), callback_data=AdminCB(action="del_yes", id=product_id))
    builder.button(text=t(lang, "btn_back"), callback_data=AdminCB(action="delete"))
    return builder.as_markup()


def admin_orders_kb(orders: list, lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for order in orders:
        builder.button(text=f"#{order['id']}", callback_data=AdminCB(action="order", id=order["id"]))
    builder.adjust(5)
    builder.row(InlineKeyboardButton(
        text=t(lang, "adm_btn_panel"), callback_data=AdminCB(action="menu").pack()
    ))
    return builder.as_markup()


def order_status_kb(order_id: int, current: str, lang: str) -> InlineKeyboardMarkup:
    """Status buttons under an order. The current status is marked with •"""
    builder = InlineKeyboardBuilder()
    for status in ADMIN_STATUSES:
        mark = "• " if status == current else ""
        builder.button(text=mark + t(lang, f"status_{status}"),
                       callback_data=StatusCB(order_id=order_id, status=status))
    builder.adjust(2)
    return builder.as_markup()


def broadcast_confirm_kb(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_send"), callback_data="bc_send")
    builder.button(text=t(lang, "btn_cancel"), callback_data="bc_cancel")
    return builder.as_markup()
