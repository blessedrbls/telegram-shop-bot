"""
Customer handlers: /start and language, catalog, cart,
checkout (FSM) and order history.
"""
import re
from html import escape

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import database as db
import keyboards as kb
from handlers.admin import notify_new_order
from states import OrderForm
from texts import format_comment, format_items, price, t, variants

router = Router()

# Optional "+", then 7-20 digits, spaces, dashes or brackets
PHONE_RE = re.compile(r"^\+?[\d\s\-()]{7,20}$")


# ---------- helpers ----------

async def safe_delete(message: Message) -> None:
    """Delete a message, ignoring errors (e.g. it is older than 48 hours)."""
    try:
        await message.delete()
    except TelegramBadRequest:
        pass


async def show_screen(callback: CallbackQuery, text: str, markup=None) -> None:
    """
    Replace the current inline "screen" with a new one.
    A text message can simply be edited, but a photo message (product card)
    can't turn into text, so we delete it and send a new message.
    """
    if callback.message.photo:
        await safe_delete(callback.message)
        await callback.message.answer(text, reply_markup=markup)
    else:
        try:
            await callback.message.edit_text(text, reply_markup=markup)
        except TelegramBadRequest:
            pass  # "message is not modified" - the screen is already up to date


# ---------- start, language, cancel ----------

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await db.add_user(message.from_user.id, message.from_user.username)
    await message.answer(t("en", "choose_lang"), reply_markup=kb.language_kb())


@router.message(Command("language"))
@router.message(F.text.in_(variants("btn_language")))
async def cmd_language(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(t("en", "choose_lang"), reply_markup=kb.language_kb())


@router.callback_query(kb.LangCB.filter())
async def set_language(callback: CallbackQuery, callback_data: kb.LangCB) -> None:
    lang = callback_data.code
    await db.set_lang(callback.from_user.id, lang)
    await callback.message.edit_text(t(lang, "lang_set"))
    # Greeting without the user's name, as required: just "Hi!"
    await callback.message.answer(t(lang, "welcome"), reply_markup=kb.main_menu_kb(lang))
    await callback.answer()


# /cancel works in any state: during checkout and in admin dialogs too
@router.message(Command("cancel"))
@router.message(F.text.in_(variants("btn_cancel")))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    lang = await db.get_lang(message.from_user.id)
    await message.answer(t(lang, "cancelled"), reply_markup=kb.main_menu_kb(lang))


@router.callback_query(F.data == kb.NOOP)
async def noop(callback: CallbackQuery) -> None:
    """Buttons that only show information (quantity, item name) do nothing."""
    await callback.answer()


# ---------- catalog ----------

@router.message(F.text.in_(variants("btn_catalog")))
async def show_catalog(message: Message, state: FSMContext) -> None:
    await state.clear()
    lang = await db.get_lang(message.from_user.id)
    categories = await db.get_categories()
    if not categories:
        await message.answer(t(lang, "no_categories"))
        return
    await message.answer(t(lang, "choose_category"), reply_markup=kb.categories_kb(categories))


@router.callback_query(F.data == "catalog")
async def back_to_categories(callback: CallbackQuery) -> None:
    lang = await db.get_lang(callback.from_user.id)
    categories = await db.get_categories()
    await show_screen(callback, t(lang, "choose_category"), kb.categories_kb(categories))
    await callback.answer()


@router.callback_query(kb.CategoryCB.filter())
async def open_category(callback: CallbackQuery, callback_data: kb.CategoryCB) -> None:
    lang = await db.get_lang(callback.from_user.id)
    category = await db.get_category(callback_data.id)
    if not category:
        await callback.answer(t(lang, "not_found"), show_alert=True)
        return
    products = await db.get_products(category["id"])
    title = f"{category['emoji']} <b>{escape(category['name'])}</b>"
    text = t(lang, "choose_product" if products else "no_products", category=title)
    await show_screen(callback, text, kb.products_kb(products, lang))
    await callback.answer()


async def send_product_card(message: Message, product: dict, lang: str) -> None:
    """Send a product card: photo with caption, or just text if there is no photo."""
    caption = t(
        lang, "product_card",
        emoji=product["emoji"],
        name=escape(product["name"]),
        description=escape(product["description"] or ""),
        price=price(product["price"]),
    )
    markup = kb.product_kb(product["id"], product["category_id"], 1, lang)

    if product["photo"]:
        try:
            sent = await message.answer_photo(product["photo"], caption=caption, reply_markup=markup)
            # Telegram gave the photo a file_id. Saving it instead of the URL makes
            # the next sends instant and independent of the external website.
            if product["photo"].startswith("http"):
                await db.set_product_photo(product["id"], sent.photo[-1].file_id)
            return
        except TelegramBadRequest:
            pass  # broken link or file_id - fall back to the emoji placeholder below

    await message.answer(caption, reply_markup=markup)


@router.callback_query(kb.ProductCB.filter())
async def open_product(callback: CallbackQuery, callback_data: kb.ProductCB) -> None:
    lang = await db.get_lang(callback.from_user.id)
    product = await db.get_product(callback_data.id)
    if not product:
        await callback.answer(t(lang, "not_found"), show_alert=True)
        return
    await safe_delete(callback.message)
    await send_product_card(callback.message, product, lang)
    await callback.answer()


@router.callback_query(kb.QtyCB.filter(F.action.in_({"inc", "dec"})))
async def change_card_qty(callback: CallbackQuery, callback_data: kb.QtyCB) -> None:
    """➕ / ➖ on a product card: only the keyboard changes, the photo stays."""
    step = 1 if callback_data.action == "inc" else -1
    qty = min(max(callback_data.qty + step, 1), 99)
    if qty != callback_data.qty:
        lang = await db.get_lang(callback.from_user.id)
        await callback.message.edit_reply_markup(
            reply_markup=kb.product_kb(callback_data.product_id, callback_data.category_id, qty, lang)
        )
    await callback.answer()


@router.callback_query(kb.QtyCB.filter(F.action == "add"))
async def add_to_cart(callback: CallbackQuery, callback_data: kb.QtyCB) -> None:
    lang = await db.get_lang(callback.from_user.id)
    product = await db.get_product(callback_data.product_id)
    if not product:
        await callback.answer(t(lang, "not_found"), show_alert=True)
        return
    await db.add_to_cart(callback.from_user.id, product["id"], callback_data.qty)
    # A small pop-up at the top of the chat
    await callback.answer(t(lang, "added_to_cart", name=product["name"], qty=callback_data.qty))


# ---------- cart ----------

async def render_cart(user_id: int, lang: str) -> tuple:
    """Build the cart text and keyboard. Returns (text, keyboard or None)."""
    items = await db.get_cart(user_id)
    if not items:
        return t(lang, "cart_empty"), None

    lines = [
        t(lang, "cart_item",
          emoji=item["emoji"], name=escape(item["name"]), qty=item["quantity"],
          price=price(item["price"]), sum=price(item["price"] * item["quantity"]))
        for item in items
    ]
    total = sum(item["price"] * item["quantity"] for item in items)
    text = t(lang, "cart_title") + "\n\n".join(lines) + t(lang, "cart_total", total=price(total))
    return text, kb.cart_kb(items, lang)


@router.message(F.text.in_(variants("btn_cart")))
async def show_cart(message: Message, state: FSMContext) -> None:
    await state.clear()
    lang = await db.get_lang(message.from_user.id)
    text, markup = await render_cart(message.from_user.id, lang)
    await message.answer(text, reply_markup=markup)


@router.callback_query(kb.CartCB.filter())
async def cart_action(callback: CallbackQuery, callback_data: kb.CartCB, state: FSMContext) -> None:
    user_id = callback.from_user.id
    lang = await db.get_lang(user_id)
    action = callback_data.action

    if action == "checkout":
        await start_checkout(callback, state, lang)
        return
    if action == "inc":
        await db.change_cart_qty(user_id, callback_data.product_id, +1)
    elif action == "dec":
        await db.change_cart_qty(user_id, callback_data.product_id, -1)
    elif action == "del":
        await db.remove_from_cart(user_id, callback_data.product_id)
    elif action == "clear":
        await db.clear_cart(user_id)

    text, markup = await render_cart(user_id, lang)
    await show_screen(callback, text, markup)
    await callback.answer()


# ---------- checkout (FSM): name -> phone -> address -> comment -> confirm ----------

async def start_checkout(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    if not await db.get_cart(callback.from_user.id):
        await callback.answer(t(lang, "cart_empty"), show_alert=True)
        return
    await state.set_state(OrderForm.name)
    await callback.message.answer(t(lang, "ask_name"), reply_markup=kb.cancel_kb(lang))
    await callback.answer()


@router.message(OrderForm.name, F.text)
async def process_name(message: Message, state: FSMContext) -> None:
    lang = await db.get_lang(message.from_user.id)
    name = message.text.strip()
    if not 2 <= len(name) <= 50:
        await message.answer(t(lang, "bad_name"))
        return
    await state.update_data(name=name)
    await state.set_state(OrderForm.phone)
    await message.answer(t(lang, "ask_phone"), reply_markup=kb.phone_kb(lang))


@router.message(OrderForm.phone, F.contact)
async def process_contact(message: Message, state: FSMContext) -> None:
    """The user pressed "Share phone number"."""
    phone = message.contact.phone_number
    if not phone.startswith("+"):
        phone = "+" + phone
    await save_phone_and_ask_address(message, state, phone)


@router.message(OrderForm.phone, F.text)
async def process_phone_text(message: Message, state: FSMContext) -> None:
    """The user typed the number manually."""
    phone = message.text.strip()
    if not PHONE_RE.match(phone):
        lang = await db.get_lang(message.from_user.id)
        await message.answer(t(lang, "bad_phone"))
        return
    await save_phone_and_ask_address(message, state, phone)


async def save_phone_and_ask_address(message: Message, state: FSMContext, phone: str) -> None:
    lang = await db.get_lang(message.from_user.id)
    await state.update_data(phone=phone)
    await state.set_state(OrderForm.address)
    await message.answer(t(lang, "ask_address"), reply_markup=kb.cancel_kb(lang))


@router.message(OrderForm.address, F.text)
async def process_address(message: Message, state: FSMContext) -> None:
    lang = await db.get_lang(message.from_user.id)
    address = message.text.strip()
    if len(address) < 5:
        await message.answer(t(lang, "bad_address"))
        return
    await state.update_data(address=address)
    await state.set_state(OrderForm.comment)
    await message.answer(t(lang, "ask_comment"), reply_markup=kb.comment_kb(lang))


@router.message(OrderForm.comment, F.text)
async def process_comment(message: Message, state: FSMContext) -> None:
    """Optional wishes: "2 coffees without sugar", "I'll pick it up near the house"..."""
    lang = await db.get_lang(message.from_user.id)
    if message.text in variants("btn_skip"):
        comment = None
    else:
        comment = message.text.strip()
        if len(comment) > 300:
            await message.answer(t(lang, "bad_comment"))
            return

    items = await db.get_cart(message.from_user.id)
    if not items:  # the cart could have been emptied in the meantime
        await state.clear()
        await message.answer(t(lang, "cart_empty"), reply_markup=kb.main_menu_kb(lang))
        return

    await state.update_data(comment=comment)
    await state.set_state(OrderForm.confirm)
    data = await state.get_data()
    total = sum(item["price"] * item["quantity"] for item in items)
    await message.answer(
        t(lang, "confirm_order",
          items=format_items(items, lang), total=price(total),
          name=escape(data["name"]), phone=escape(data["phone"]),
          address=escape(data["address"]), comment=format_comment(comment, lang)),
        reply_markup=kb.confirm_order_kb(lang),
    )


@router.callback_query(OrderForm.confirm, F.data == "order_confirm")
async def confirm_order(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    lang = await db.get_lang(callback.from_user.id)
    data = await state.get_data()
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=None)  # no double clicks

    order_id = await db.create_order(callback.from_user.id, data["name"], data["phone"],
                                     data["address"], data.get("comment"))
    if order_id is None:
        await callback.message.answer(t(lang, "cart_empty"), reply_markup=kb.main_menu_kb(lang))
        await callback.answer()
        return

    await callback.message.answer(t(lang, "order_placed", order_id=order_id),
                                  reply_markup=kb.main_menu_kb(lang))
    await callback.answer()
    await notify_new_order(bot, order_id)


@router.callback_query(OrderForm.confirm, F.data == "order_cancel")
async def cancel_order(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await db.get_lang(callback.from_user.id)
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(t(lang, "cancelled"), reply_markup=kb.main_menu_kb(lang))
    await callback.answer()


@router.callback_query(F.data.in_({"order_confirm", "order_cancel"}))
async def old_order_buttons(callback: CallbackQuery) -> None:
    """Confirm/Cancel pressed on an old message, when checkout is already finished."""
    lang = await db.get_lang(callback.from_user.id)
    await callback.answer(t(lang, "button_expired"), show_alert=True)


# ---------- my orders ----------

@router.message(F.text.in_(variants("btn_orders")))
async def my_orders(message: Message, state: FSMContext) -> None:
    await state.clear()
    lang = await db.get_lang(message.from_user.id)
    orders = await db.get_user_orders(message.from_user.id, limit=10)
    if not orders:
        await message.answer(t(lang, "my_orders_empty"))
        return

    parts = []
    for order in orders:
        items = await db.get_order_items(order["id"])
        parts.append(t(
            lang, "order_line",
            id=order["id"], date=order["created_at"][:16],
            items=format_items(items, lang), comment=format_comment(order["comment"], lang),
            total=price(order["total"]), status=t(lang, f"status_{order['status']}"),
        ))
    await message.answer(t(lang, "my_orders_title") + "\n".join(parts))
