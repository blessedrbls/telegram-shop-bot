"""
Admin handlers (available only to ADMIN_ID from .env):
new order notifications and statuses, adding/deleting products,
latest orders, statistics and broadcast.
"""
import asyncio
import logging
from html import escape

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest, TelegramRetryAfter
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import database as db
import keyboards as kb
from config import ADMIN_ID, ORDER_STATUSES
from states import AddProduct, Broadcast
from texts import format_comment, format_items, price, t

router = Router()

# Every handler in this router ignores everyone except the admin
router.message.filter(F.from_user.id == ADMIN_ID)
router.callback_query.filter(F.from_user.id == ADMIN_ID)


# ---------- orders: notification & statuses ----------

async def format_order(order: dict, lang: str) -> str:
    """Full order description for the admin."""
    items = await db.get_order_items(order["id"])
    customer = f'<a href="tg://user?id={order["user_id"]}">{order["user_id"]}</a>'
    if order.get("username"):
        customer += f" (@{order['username']})"
    return t(
        lang, "admin_order",
        order_id=order["id"],
        date=order["created_at"][:16],
        items=format_items(items, lang),
        total=price(order["total"]),
        name=escape(order["customer_name"]),
        phone=escape(order["phone"]),
        address=escape(order["address"]),
        comment=format_comment(order["comment"], lang),
        customer=customer,
        status=t(lang, f"status_{order['status']}"),
    )


async def notify_new_order(bot: Bot, order_id: int) -> None:
    """Called from the customer handlers right after an order is placed."""
    order = await db.get_order(order_id)
    lang = await db.get_lang(ADMIN_ID)
    text = t(lang, "new_order_alert") + await format_order(order, lang)
    try:
        await bot.send_message(ADMIN_ID, text,
                               reply_markup=kb.order_status_kb(order_id, order["status"], lang))
    except TelegramAPIError as e:
        # E.g. the admin has never pressed /start in this bot
        logging.warning("Can't notify admin about order #%s: %s", order_id, e)


@router.callback_query(kb.StatusCB.filter())
async def change_status(callback: CallbackQuery, callback_data: kb.StatusCB, bot: Bot) -> None:
    lang = await db.get_lang(callback.from_user.id)
    order = await db.get_order(callback_data.order_id)
    if not order:
        await callback.answer(t(lang, "not_found"), show_alert=True)
        return
    if order["status"] == callback_data.status:
        await callback.answer(t(lang, "status_same"))
        return

    await db.set_order_status(order["id"], callback_data.status)
    order["status"] = callback_data.status

    # Update the admin's message so it shows the new status
    await callback.message.edit_text(
        await format_order(order, lang),
        reply_markup=kb.order_status_kb(order["id"], order["status"], lang),
    )
    await callback.answer(t(lang, "status_updated", status=t(lang, f"status_{order['status']}")))

    # Tell the customer about the change, in the customer's language
    client_lang = await db.get_lang(order["user_id"])
    try:
        await bot.send_message(
            order["user_id"],
            t(client_lang, "status_changed", order_id=order["id"],
              status=t(client_lang, f"status_{order['status']}")),
        )
    except TelegramAPIError as e:
        # E.g. the customer has blocked the bot
        logging.warning("Can't notify user %s: %s", order["user_id"], e)


# ---------- admin panel ----------

@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext) -> None:
    await state.clear()
    lang = await db.get_lang(message.from_user.id)
    await message.answer(t(lang, "admin_panel"), reply_markup=kb.admin_menu_kb(lang))


@router.callback_query(kb.AdminCB.filter(F.action == "menu"))
async def back_to_panel(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    lang = await db.get_lang(callback.from_user.id)
    await callback.message.edit_text(t(lang, "admin_panel"), reply_markup=kb.admin_menu_kb(lang))
    await callback.answer()


# ---------- latest orders ----------

@router.callback_query(kb.AdminCB.filter(F.action == "orders"))
async def last_orders(callback: CallbackQuery) -> None:
    lang = await db.get_lang(callback.from_user.id)
    orders = await db.get_last_orders(10)
    if not orders:
        await callback.message.edit_text(t(lang, "last_orders_empty"),
                                         reply_markup=kb.back_to_panel_kb(lang))
        await callback.answer()
        return

    lines = [
        t(lang, "last_order_line",
          id=o["id"], date=o["created_at"][:16], total=price(o["total"]),
          status=t(lang, f"status_{o['status']}"), name=escape(o["customer_name"]))
        for o in orders
    ]
    text = t(lang, "last_orders_title") + "\n".join(lines) + t(lang, "last_orders_hint")
    await callback.message.edit_text(text, reply_markup=kb.admin_orders_kb(orders, lang))
    await callback.answer()


@router.callback_query(kb.AdminCB.filter(F.action == "order"))
async def show_order(callback: CallbackQuery, callback_data: kb.AdminCB) -> None:
    """Send one order as a separate message with status buttons."""
    lang = await db.get_lang(callback.from_user.id)
    order = await db.get_order(callback_data.id)
    if not order:
        await callback.answer(t(lang, "not_found"), show_alert=True)
        return
    await callback.message.answer(
        await format_order(order, lang),
        reply_markup=kb.order_status_kb(order["id"], order["status"], lang),
    )
    await callback.answer()


# ---------- statistics ----------

@router.callback_query(kb.AdminCB.filter(F.action == "stats"))
async def show_stats(callback: CallbackQuery) -> None:
    lang = await db.get_lang(callback.from_user.id)
    stats = await db.get_stats()
    by_status = "\n".join(
        f"{t(lang, f'status_{status}')}: {stats['by_status'].get(status, 0)}"
        for status in ORDER_STATUSES
    )
    text = t(lang, "stats", users=stats["users"], orders=stats["orders"],
             revenue=price(stats["revenue"]), by_status=by_status)
    await callback.message.edit_text(text, reply_markup=kb.back_to_panel_kb(lang))
    await callback.answer()


# ---------- add product (FSM) ----------

@router.callback_query(kb.AdminCB.filter(F.action == "add"))
async def add_start(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await db.get_lang(callback.from_user.id)
    categories = await db.get_categories()
    await state.set_state(AddProduct.category)
    await callback.message.edit_text(t(lang, "add_choose_category"),
                                     reply_markup=kb.admin_categories_kb(categories, lang))
    await callback.answer()


@router.callback_query(AddProduct.category, kb.AdminCB.filter(F.action == "add_cat"))
async def add_category(callback: CallbackQuery, callback_data: kb.AdminCB, state: FSMContext) -> None:
    lang = await db.get_lang(callback.from_user.id)
    category = await db.get_category(callback_data.id)
    if not category:
        await callback.answer(t(lang, "not_found"), show_alert=True)
        return
    await state.update_data(category_id=category["id"])
    await state.set_state(AddProduct.name)
    await callback.message.edit_text(
        t(lang, "add_category_chosen", category=f"{category['emoji']} {escape(category['name'])}")
    )
    await callback.message.answer(t(lang, "add_ask_name"), reply_markup=kb.cancel_kb(lang))
    await callback.answer()


@router.message(AddProduct.name, F.text)
async def add_name(message: Message, state: FSMContext) -> None:
    lang = await db.get_lang(message.from_user.id)
    name = message.text.strip()
    if not 2 <= len(name) <= 64:
        await message.answer(t(lang, "add_bad_name"))
        return
    await state.update_data(name=name)
    await state.set_state(AddProduct.description)
    await message.answer(t(lang, "add_ask_description"))


@router.message(AddProduct.description, F.text)
async def add_description(message: Message, state: FSMContext) -> None:
    lang = await db.get_lang(message.from_user.id)
    description = message.text.strip()
    # Photo captions are limited to 1024 characters, so keep the description shorter
    if not 5 <= len(description) <= 800:
        await message.answer(t(lang, "add_bad_description"))
        return
    await state.update_data(description=description)
    await state.set_state(AddProduct.price)
    await message.answer(t(lang, "add_ask_price"))


@router.message(AddProduct.price, F.text)
async def add_price(message: Message, state: FSMContext) -> None:
    lang = await db.get_lang(message.from_user.id)
    try:
        value = round(float(message.text.replace(",", ".").strip()), 2)
    except ValueError:
        value = 0
    if not 0 < value < 1_000_000:
        await message.answer(t(lang, "add_bad_price"))
        return
    await state.update_data(price=value)
    await state.set_state(AddProduct.photo)
    await message.answer(t(lang, "add_ask_photo"))


@router.message(AddProduct.photo, F.photo)
async def add_photo(message: Message, state: FSMContext) -> None:
    # message.photo is a list of sizes; the last one is the biggest
    await save_product(message, state, photo=message.photo[-1].file_id)


@router.message(AddProduct.photo, Command("skip"))
async def add_skip_photo(message: Message, state: FSMContext) -> None:
    await save_product(message, state, photo=None)


@router.message(AddProduct.photo, F.text.startswith("http"))
async def add_photo_url(message: Message, state: FSMContext) -> None:
    await save_product(message, state, photo=message.text.strip())


@router.message(AddProduct.photo)
async def add_bad_photo(message: Message) -> None:
    lang = await db.get_lang(message.from_user.id)
    await message.answer(t(lang, "add_bad_photo"))


async def save_product(message: Message, state: FSMContext, photo) -> None:
    lang = await db.get_lang(message.from_user.id)
    data = await state.get_data()
    await state.clear()
    category = await db.get_category(data["category_id"])
    await db.add_product(
        category_id=category["id"],
        name=data["name"],
        description=data["description"],
        price=data["price"],
        emoji=category["emoji"],  # used as a placeholder when there is no photo
        photo=photo,
    )
    await message.answer(
        t(lang, "product_added", name=escape(data["name"]),
          category=f"{category['emoji']} {escape(category['name'])}"),
        reply_markup=kb.main_menu_kb(lang),
    )
    await message.answer(t(lang, "admin_panel"), reply_markup=kb.admin_menu_kb(lang))


# ---------- delete product ----------

@router.callback_query(kb.AdminCB.filter(F.action == "delete"))
async def delete_list(callback: CallbackQuery) -> None:
    lang = await db.get_lang(callback.from_user.id)
    products = await db.get_all_products()
    text = t(lang, "delete_choose") if products else t(lang, "admin_no_products")
    await callback.message.edit_text(text, reply_markup=kb.admin_products_kb(products, lang))
    await callback.answer()


@router.callback_query(kb.AdminCB.filter(F.action == "del"))
async def delete_ask(callback: CallbackQuery, callback_data: kb.AdminCB) -> None:
    lang = await db.get_lang(callback.from_user.id)
    product = await db.get_product(callback_data.id)
    if not product:
        await callback.answer(t(lang, "not_found"), show_alert=True)
        return
    await callback.message.edit_text(
        t(lang, "delete_confirm", name=f"{product['emoji']} {escape(product['name'])}"),
        reply_markup=kb.admin_delete_confirm_kb(product["id"], lang),
    )
    await callback.answer()


@router.callback_query(kb.AdminCB.filter(F.action == "del_yes"))
async def delete_confirm(callback: CallbackQuery, callback_data: kb.AdminCB) -> None:
    lang = await db.get_lang(callback.from_user.id)
    await db.delete_product(callback_data.id)
    await callback.answer(t(lang, "product_deleted"))
    # Show the updated list
    products = await db.get_all_products()
    text = t(lang, "delete_choose") if products else t(lang, "admin_no_products")
    await callback.message.edit_text(text, reply_markup=kb.admin_products_kb(products, lang))


# ---------- broadcast ----------

@router.callback_query(kb.AdminCB.filter(F.action == "broadcast"))
async def broadcast_start(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await db.get_lang(callback.from_user.id)
    await state.set_state(Broadcast.message)
    await callback.message.edit_text(t(lang, "broadcast_ask"))
    await callback.answer()


@router.message(Broadcast.message)
async def broadcast_preview(message: Message, state: FSMContext) -> None:
    """Remember which message to copy and ask for confirmation."""
    lang = await db.get_lang(message.from_user.id)
    await state.update_data(chat_id=message.chat.id, message_id=message.message_id)
    await state.set_state(Broadcast.confirm)
    count = len(await db.get_all_user_ids())
    await message.reply(t(lang, "broadcast_confirm", count=count),
                        reply_markup=kb.broadcast_confirm_kb(lang))


@router.callback_query(Broadcast.confirm, F.data == "bc_cancel")
async def broadcast_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await db.get_lang(callback.from_user.id)
    await state.clear()
    await callback.message.edit_text(t(lang, "broadcast_cancelled"),
                                     reply_markup=kb.back_to_panel_kb(lang))
    await callback.answer()


async def _copy_to(bot: Bot, user_id: int, chat_id: int, message_id: int) -> bool:
    """Copy one message to one user. Returns True if it was delivered."""
    try:
        await bot.copy_message(chat_id=user_id, from_chat_id=chat_id, message_id=message_id)
        return True
    except TelegramRetryAfter as e:
        # Telegram asks us to slow down: wait as long as it says and try again
        await asyncio.sleep(e.retry_after)
        return await _copy_to(bot, user_id, chat_id, message_id)
    except TelegramAPIError:
        # The user blocked the bot, deleted the account, etc.
        return False


@router.callback_query(Broadcast.confirm, F.data == "bc_send")
async def broadcast_send(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    lang = await db.get_lang(callback.from_user.id)
    data = await state.get_data()
    await state.clear()
    await callback.message.edit_text(t(lang, "broadcast_started"))
    await callback.answer()

    ok = fail = 0
    for user_id in await db.get_all_user_ids():
        if await _copy_to(bot, user_id, data["chat_id"], data["message_id"]):
            ok += 1
        else:
            fail += 1
        await asyncio.sleep(0.05)  # stay under Telegram's limit of ~30 messages per second

    try:
        await callback.message.edit_text(t(lang, "broadcast_done", ok=ok, fail=fail),
                                         reply_markup=kb.back_to_panel_kb(lang))
    except TelegramBadRequest:
        await callback.message.answer(t(lang, "broadcast_done", ok=ok, fail=fail))
