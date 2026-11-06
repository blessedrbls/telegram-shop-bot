"""
All bot texts, grouped by language.

To add a new language, copy the "en" block, translate the values
and add a button for it in keyboards.language_kb().
"""
from html import escape

from config import CURRENCY

DEFAULT_LANG = "en"

LANGUAGES = {
    "en": "🇬🇧 English",
    "uk": "🇺🇦 Українська",
}

TEXTS = {
    "en": {
        # --- start & language ---
        "choose_lang": "🌐 Choose your language / Оберіть мову:",
        "lang_set": "✅ Language: English",
        "welcome": (
            "Hi! 👋\n\n"
            "Welcome to <b>Coffee Shop Bot</b> ☕\n"
            "Browse the menu, add items to your cart and place an order in a couple of taps.\n\n"
            "Use the menu below 👇"
        ),
        "cancelled": "❌ Cancelled. You are back in the main menu.",
        "button_expired": "⚠️ This button is no longer active.",
        "not_found": "⚠️ Not found. It may have been deleted.",

        # --- main menu & common buttons ---
        "btn_catalog": "🛍 Catalog",
        "btn_cart": "🛒 Cart",
        "btn_orders": "📦 My orders",
        "btn_language": "🌐 Language",
        "btn_cancel": "❌ Cancel",
        "btn_back": "⬅️ Back",

        # --- catalog ---
        "choose_category": "🛍 <b>Catalog</b>\n\nChoose a category:",
        "no_categories": "😔 The catalog is empty for now.",
        "choose_product": "{category}\n\nChoose a product:",
        "no_products": "{category}\n\n😔 No products in this category yet.",
        "product_card": "{emoji} <b>{name}</b>\n\n{description}\n\n💰 Price: <b>{price}</b>",
        "qty_label": "{qty} pcs",
        "btn_add_to_cart": "🛒 Add to cart",
        "added_to_cart": "✅ Added to cart: {name} × {qty}",

        # --- cart ---
        "cart_empty": "🛒 Your cart is empty.\nOpen the 🛍 Catalog and pick something tasty!",
        "cart_title": "🛒 <b>Your cart</b>\n\n",
        "cart_item": "{emoji} <b>{name}</b>\n{qty} × {price} = {sum}",
        "cart_total": "\n\n💰 Total: <b>{total}</b>",
        "btn_clear_cart": "🧹 Clear cart",
        "btn_checkout": "✅ Checkout",

        # --- checkout ---
        "ask_name": "📝 <b>Checkout</b>\n\nStep 1/4. What is your name?",
        "bad_name": "⚠️ Please enter a name from 2 to 50 characters.",
        "ask_phone": (
            "📱 Step 2/4. Tap the button below to share your phone number "
            "or type it manually (e.g. +380501234567)."
        ),
        "btn_share_phone": "📱 Share phone number",
        "bad_phone": "⚠️ That doesn't look like a phone number. Try again, e.g. +380501234567",
        "ask_address": "📍 Step 3/4. Enter the delivery address (city, street, house, apartment):",
        "bad_address": "⚠️ The address is too short, please be more specific.",
        "ask_comment": (
            "💬 Step 4/4. Any wishes for your order?\n"
            "For example: <i>2 coffees without sugar, 1 with mint syrup</i> "
            "or <i>I'll pick it up near the house</i>.\n\n"
            "Type a comment or tap ⏭ Skip."
        ),
        "btn_skip": "⏭ Skip",
        "bad_comment": "⚠️ The comment is too long (max 300 characters).",
        "comment_line": "\n💬 Comment: {comment}",
        "confirm_order": (
            "🧾 <b>Please check your order:</b>\n\n{items}\n\n"
            "💰 Total: <b>{total}</b>\n\n"
            "👤 Name: {name}\n📱 Phone: {phone}\n📍 Address: {address}{comment}\n\n"
            "Is everything correct?"
        ),
        "order_item_line": "• {name} × {qty} = {sum}",
        "btn_confirm": "✅ Confirm",
        "order_placed": (
            "🎉 Thank you! Your order <b>#{order_id}</b> has been placed.\n"
            "We will notify you when its status changes."
        ),

        # --- my orders ---
        "my_orders_empty": "📦 You have no orders yet.",
        "my_orders_title": "📦 <b>Your orders</b>\n\n",
        "order_line": "<b>#{id}</b> · {date}\n{items}{comment}\n💰 {total} · {status}\n",
        "status_changed": "🔔 Your order <b>#{order_id}</b> status has changed: <b>{status}</b>",

        # --- order statuses ---
        "status_new": "🆕 New",
        "status_accepted": "✅ Accepted",
        "status_shipped": "🚚 Shipped",
        "status_delivered": "📬 Delivered",
        "status_cancelled": "❌ Cancelled",

        # --- admin panel ---
        "admin_panel": "🛠 <b>Admin panel</b>\n\nChoose an action:",
        "adm_btn_add": "➕ Add product",
        "adm_btn_delete": "🗑 Delete product",
        "adm_btn_orders": "📋 Latest orders",
        "adm_btn_stats": "📊 Statistics",
        "adm_btn_broadcast": "📢 Broadcast",
        "adm_btn_panel": "⬅️ Admin panel",

        "new_order_alert": "🔔 <b>New order!</b>\n\n",
        "admin_order": (
            "🧾 <b>Order #{order_id}</b>\n🕒 {date}\n\n{items}\n\n"
            "💰 Total: <b>{total}</b>\n\n"
            "👤 {name}\n📱 {phone}\n📍 {address}{comment}\n🆔 Customer: {customer}\n\n"
            "Status: <b>{status}</b>"
        ),
        "status_updated": "Status updated: {status}",
        "status_same": "This status is already set",

        "last_orders_empty": "📋 No orders yet.",
        "last_orders_title": "📋 <b>Latest orders</b>\n\n",
        "last_order_line": "<b>#{id}</b> · {date} · {total}\n{status} · 👤 {name}\n",
        "last_orders_hint": "\nTap an order number to manage its status 👇",

        "stats": (
            "📊 <b>Statistics</b>\n\n"
            "👥 Users: <b>{users}</b>\n"
            "📦 Orders: <b>{orders}</b>\n"
            "💰 Revenue: <b>{revenue}</b>\n"
            "<i>(cancelled orders are not counted)</i>\n\n"
            "<b>By status:</b>\n{by_status}"
        ),

        "add_choose_category": "➕ <b>New product</b>\n\nStep 1/5. Choose a category:",
        "add_category_chosen": "➕ <b>New product</b>\nCategory: {category}",
        "add_ask_name": "Step 2/5. Enter the product name:",
        "add_bad_name": "⚠️ The name must be from 2 to 64 characters.",
        "add_ask_description": "Step 3/5. Enter the product description:",
        "add_bad_description": "⚠️ The description must be from 5 to 800 characters.",
        "add_ask_price": "Step 4/5. Enter the price (e.g. 3.50):",
        "add_bad_price": "⚠️ Enter a positive number, e.g. 3.50",
        "add_ask_photo": (
            "Step 5/5. Send a photo of the product or a link to an image.\n"
            "Send /skip to use an emoji placeholder."
        ),
        "add_bad_photo": "⚠️ Send a photo, an image link (http...) or /skip.",
        "product_added": "✅ Product <b>{name}</b> added to {category}!",

        "delete_choose": "🗑 <b>Delete product</b>\n\nChoose a product:",
        "delete_confirm": (
            "Delete <b>{name}</b>?\n\n"
            "It will be removed from the catalog and from customers' carts. "
            "Order history is kept."
        ),
        "btn_delete_yes": "🗑 Yes, delete",
        "product_deleted": "🗑 Product deleted",
        "admin_no_products": "😔 There are no products.",

        "broadcast_ask": (
            "📢 <b>Broadcast</b>\n\n"
            "Send the message that all users will receive (text, photo, video...).\n"
            "/cancel to abort."
        ),
        "broadcast_confirm": "☝️ Send this message to <b>{count}</b> users?",
        "btn_send": "📢 Send",
        "broadcast_started": "⏳ Sending...",
        "broadcast_done": "✅ Broadcast finished.\n\n📬 Delivered: {ok}\n🚫 Failed: {fail}",
        "broadcast_cancelled": "❌ Broadcast cancelled.",
    },

    "uk": {
        # --- start & language ---
        "choose_lang": "🌐 Choose your language / Оберіть мову:",
        "lang_set": "✅ Мова: українська",
        "welcome": (
            "Привіт! 👋\n\n"
            "Ласкаво просимо до <b>Coffee Shop Bot</b> ☕\n"
            "Переглядайте меню, додавайте товари в кошик і оформлюйте замовлення в кілька дотиків.\n\n"
            "Користуйтеся меню нижче 👇"
        ),
        "cancelled": "❌ Скасовано. Ви в головному меню.",
        "button_expired": "⚠️ Ця кнопка вже неактивна.",
        "not_found": "⚠️ Не знайдено. Можливо, його вже видалили.",

        # --- main menu & common buttons ---
        "btn_catalog": "🛍 Каталог",
        "btn_cart": "🛒 Кошик",
        "btn_orders": "📦 Мої замовлення",
        "btn_language": "🌐 Мова",
        "btn_cancel": "❌ Скасувати",
        "btn_back": "⬅️ Назад",

        # --- catalog ---
        "choose_category": "🛍 <b>Каталог</b>\n\nОберіть категорію:",
        "no_categories": "😔 Каталог поки порожній.",
        "choose_product": "{category}\n\nОберіть товар:",
        "no_products": "{category}\n\n😔 У цій категорії поки немає товарів.",
        "product_card": "{emoji} <b>{name}</b>\n\n{description}\n\n💰 Ціна: <b>{price}</b>",
        "qty_label": "{qty} шт.",
        "btn_add_to_cart": "🛒 Додати в кошик",
        "added_to_cart": "✅ Додано в кошик: {name} × {qty}",

        # --- cart ---
        "cart_empty": "🛒 Ваш кошик порожній.\nЗазирніть у 🛍 Каталог — там багато смачного!",
        "cart_title": "🛒 <b>Ваш кошик</b>\n\n",
        "cart_item": "{emoji} <b>{name}</b>\n{qty} × {price} = {sum}",
        "cart_total": "\n\n💰 Разом: <b>{total}</b>",
        "btn_clear_cart": "🧹 Очистити",
        "btn_checkout": "✅ Оформити",

        # --- checkout ---
        "ask_name": "📝 <b>Оформлення замовлення</b>\n\nКрок 1/4. Як вас звати?",
        "bad_name": "⚠️ Введіть ім'я від 2 до 50 символів.",
        "ask_phone": (
            "📱 Крок 2/4. Натисніть кнопку нижче, щоб поділитися номером, "
            "або введіть його вручну (наприклад, +380501234567)."
        ),
        "btn_share_phone": "📱 Поділитися номером",
        "bad_phone": "⚠️ Схоже, це не номер телефону. Спробуйте ще раз, наприклад: +380501234567",
        "ask_address": "📍 Крок 3/4. Введіть адресу доставки (місто, вулиця, будинок, квартира):",
        "bad_address": "⚠️ Адреса занадто коротка, вкажіть детальніше.",
        "ask_comment": (
            "💬 Крок 4/4. Є побажання до замовлення?\n"
            "Наприклад: <i>2 кави без цукру, 1 з м'ятним сиропом</i> "
            "або <i>заберу біля будинку</i>.\n\n"
            "Напишіть коментар або натисніть ⏭ Пропустити."
        ),
        "btn_skip": "⏭ Пропустити",
        "bad_comment": "⚠️ Коментар занадто довгий (максимум 300 символів).",
        "comment_line": "\n💬 Коментар: {comment}",
        "confirm_order": (
            "🧾 <b>Перевірте замовлення:</b>\n\n{items}\n\n"
            "💰 Разом: <b>{total}</b>\n\n"
            "👤 Ім'я: {name}\n📱 Телефон: {phone}\n📍 Адреса: {address}{comment}\n\n"
            "Усе правильно?"
        ),
        "order_item_line": "• {name} × {qty} = {sum}",
        "btn_confirm": "✅ Підтвердити",
        "order_placed": (
            "🎉 Дякуємо! Замовлення <b>#{order_id}</b> оформлено.\n"
            "Ми повідомимо вас, коли зміниться його статус."
        ),

        # --- my orders ---
        "my_orders_empty": "📦 У вас ще немає замовлень.",
        "my_orders_title": "📦 <b>Ваші замовлення</b>\n\n",
        "order_line": "<b>#{id}</b> · {date}\n{items}{comment}\n💰 {total} · {status}\n",
        "status_changed": "🔔 Статус замовлення <b>#{order_id}</b> змінено: <b>{status}</b>",

        # --- order statuses ---
        "status_new": "🆕 Нове",
        "status_accepted": "✅ Прийнято",
        "status_shipped": "🚚 Відправлено",
        "status_delivered": "📬 Доставлено",
        "status_cancelled": "❌ Скасовано",

        # --- admin panel ---
        "admin_panel": "🛠 <b>Панель адміністратора</b>\n\nОберіть дію:",
        "adm_btn_add": "➕ Додати товар",
        "adm_btn_delete": "🗑 Видалити товар",
        "adm_btn_orders": "📋 Останні замовлення",
        "adm_btn_stats": "📊 Статистика",
        "adm_btn_broadcast": "📢 Розсилка",
        "adm_btn_panel": "⬅️ До панелі",

        "new_order_alert": "🔔 <b>Нове замовлення!</b>\n\n",
        "admin_order": (
            "🧾 <b>Замовлення #{order_id}</b>\n🕒 {date}\n\n{items}\n\n"
            "💰 Разом: <b>{total}</b>\n\n"
            "👤 {name}\n📱 {phone}\n📍 {address}{comment}\n🆔 Клієнт: {customer}\n\n"
            "Статус: <b>{status}</b>"
        ),
        "status_updated": "Статус оновлено: {status}",
        "status_same": "Цей статус уже встановлено",

        "last_orders_empty": "📋 Замовлень поки немає.",
        "last_orders_title": "📋 <b>Останні замовлення</b>\n\n",
        "last_order_line": "<b>#{id}</b> · {date} · {total}\n{status} · 👤 {name}\n",
        "last_orders_hint": "\nНатисніть номер замовлення, щоб змінити статус 👇",

        "stats": (
            "📊 <b>Статистика</b>\n\n"
            "👥 Користувачів: <b>{users}</b>\n"
            "📦 Замовлень: <b>{orders}</b>\n"
            "💰 Виручка: <b>{revenue}</b>\n"
            "<i>(без скасованих замовлень)</i>\n\n"
            "<b>За статусами:</b>\n{by_status}"
        ),

        "add_choose_category": "➕ <b>Новий товар</b>\n\nКрок 1/5. Оберіть категорію:",
        "add_category_chosen": "➕ <b>Новий товар</b>\nКатегорія: {category}",
        "add_ask_name": "Крок 2/5. Введіть назву товару:",
        "add_bad_name": "⚠️ Назва має містити від 2 до 64 символів.",
        "add_ask_description": "Крок 3/5. Введіть опис товару:",
        "add_bad_description": "⚠️ Опис має містити від 5 до 800 символів.",
        "add_ask_price": "Крок 4/5. Введіть ціну (наприклад, 3.50):",
        "add_bad_price": "⚠️ Введіть додатне число, наприклад: 3.50",
        "add_ask_photo": (
            "Крок 5/5. Надішліть фото товару або посилання на картинку.\n"
            "Надішліть /skip, щоб використати емодзі-заглушку."
        ),
        "add_bad_photo": "⚠️ Надішліть фото, посилання (http...) або /skip.",
        "product_added": "✅ Товар <b>{name}</b> додано до категорії {category}!",

        "delete_choose": "🗑 <b>Видалення товару</b>\n\nОберіть товар:",
        "delete_confirm": (
            "Видалити <b>{name}</b>?\n\n"
            "Товар зникне з каталогу та з кошиків покупців. "
            "Історія замовлень збережеться."
        ),
        "btn_delete_yes": "🗑 Так, видалити",
        "product_deleted": "🗑 Товар видалено",
        "admin_no_products": "😔 Товарів немає.",

        "broadcast_ask": (
            "📢 <b>Розсилка</b>\n\n"
            "Надішліть повідомлення, яке отримають усі користувачі (текст, фото, відео...).\n"
            "/cancel — скасувати."
        ),
        "broadcast_confirm": "☝️ Надіслати це повідомлення <b>{count}</b> користувачам?",
        "btn_send": "📢 Надіслати",
        "broadcast_started": "⏳ Надсилаю...",
        "broadcast_done": "✅ Розсилку завершено.\n\n📬 Доставлено: {ok}\n🚫 Не доставлено: {fail}",
        "broadcast_cancelled": "❌ Розсилку скасовано.",
    },
}


def t(lang: str, key: str, **kwargs) -> str:
    """Return the text `key` in language `lang` (falls back to English)."""
    texts = TEXTS.get(lang, TEXTS[DEFAULT_LANG])
    text = texts.get(key, TEXTS[DEFAULT_LANG][key])
    return text.format(**kwargs) if kwargs else text


def variants(key: str) -> set:
    """All translations of one text. Used to catch reply-button presses in any language."""
    return {texts[key] for texts in TEXTS.values()}


def price(value: float) -> str:
    """3.5 -> '$3.50'"""
    return f"{CURRENCY}{value:.2f}"


def format_comment(comment, lang: str) -> str:
    """A '💬 Comment: ...' line (starting with a line break), or '' if there is no comment."""
    return t(lang, "comment_line", comment=escape(comment)) if comment else ""


def format_items(items: list, lang: str) -> str:
    """Turn a list of {name, price, quantity} into '• Latte × 2 = $7.80' lines."""
    return "\n".join(
        t(lang, "order_item_line",
          name=escape(item["name"]),
          qty=item["quantity"],
          sum=price(item["price"] * item["quantity"]))
        for item in items
    )
