# ☕ Telegram Shop Bot

A Telegram bot for an online shop (a coffee shop in the demo): customers browse the catalog, fill a cart and place orders, and the owner manages products, orders and broadcasts right inside Telegram, with no website or separate admin dashboard.

Built with **Python 3**, **aiogram 3** and **SQLite**. The bot is bilingual (🇬🇧 English / 🇺🇦 Ukrainian) and ships with a demo catalog, so it works right after launch.

---

## ✨ Features

### 🛍 For customers
- 🌐 **Language choice** on start: 🇬🇧 English / 🇺🇦 Українська (can be changed any time with `/language`)
- 📂 **Catalog**: categories → products
- 🖼 **Product cards** with photo, description and price
- ➕➖ **Quantity selector** right on the product card
- 🛒 **Cart**: change quantity, remove items, clear the cart, see the total
- 📝 **Step-by-step checkout**: name → phone → delivery address → comment → confirmation
- 💬 **Order comment** (optional): "2 coffees without sugar, 1 with mint syrup", "I'll pick it up near the house"
- 📱 **One-tap phone sharing** with the "Share phone number" button (or type it manually)
- 📦 **My orders**: order history with live statuses
- 🔔 **Notifications** when the order status changes
- ❌ **/cancel** to exit any step

### 🛠 For the admin
- 🔐 **Admin panel** (`/admin`), available only to the owner's Telegram ID
- 🆕 **Instant notification** about every new order, including the customer's comment
- 🔄 **Order statuses** in one tap: ✅ Accepted / 🚚 Shipped / 📬 Delivered / ❌ Cancelled (the customer is notified automatically)
- ➕ **Add products**: category, name, description, price and photo (upload, link or emoji placeholder)
- 🗑 **Delete products** with confirmation
- 📋 **Latest orders** list with quick access to each order
- 📊 **Statistics**: users, orders, revenue and orders by status
- 📢 **Broadcast**: send any message (text, photo, video...) to all users

---

## 📸 Screenshots

| Main menu | Catalog | Product card |
|:---:|:---:|:---:|
| ![Main menu](https://placehold.co/260x520/png?text=Main+menu) | ![Catalog](https://placehold.co/260x520/png?text=Catalog) | ![Product card](https://placehold.co/260x520/png?text=Product+card) |

| Cart | Checkout | Admin panel |
|:---:|:---:|:---:|
| ![Cart](https://placehold.co/260x520/png?text=Cart) | ![Checkout](https://placehold.co/260x520/png?text=Checkout) | ![Admin panel](https://placehold.co/260x520/png?text=Admin+panel) |

---

## ⚙️ How it works

1. **/start** → the customer picks a language → the main menu appears: 🛍 Catalog, 🛒 Cart, 📦 My orders, 🌐 Language.
2. In the **catalog**, the customer opens a category, then a product card, picks the quantity with ➕/➖ and taps **Add to cart**.
3. In the **cart**, quantities can be adjusted, and **Checkout** starts a short dialog (built with aiogram's FSM): name → phone → address → comment (optional) → confirmation.
4. Once the order is confirmed, it is saved to SQLite and the **admin gets a notification** with status buttons.
5. When the admin changes the status, the **customer gets a message** in their own language, and the status is updated in **📦 My orders**.
6. The admin uses **/admin** to manage products, view orders and statistics, and send broadcasts.

On the first launch, the database is created automatically and filled with a **demo catalog**: 3 categories (Coffee, Tea, Desserts) with 3 products each.

---

## 🧰 Tech stack

- **Python 3.9+**
- **[aiogram 3](https://docs.aiogram.dev/)**: asynchronous Telegram Bot API framework (routers, FSM, inline keyboards, callback data factories)
- **SQLite** + **[aiosqlite](https://github.com/omnilib/aiosqlite)**: async database access
- **[python-dotenv](https://github.com/theskumar/python-dotenv)**: secrets in a `.env` file

---

## 📁 Project structure

```
telegram-shop-bot/
├── bot.py              # Entry point: creates the bot, connects routers, starts polling
├── config.py           # Settings from .env (token, admin ID, DB path)
├── database.py         # SQLite tables, demo data and all queries
├── keyboards.py        # Reply & inline keyboards, callback data
├── texts.py            # All bot texts in English and Ukrainian
├── states.py           # FSM states (checkout, adding a product, broadcast)
├── handlers/
│   ├── user.py         # Customer side: language, catalog, cart, checkout, orders
│   └── admin.py        # Admin side: orders, statuses, products, stats, broadcast
├── requirements.txt
├── .env.example        # Template for your .env
└── .gitignore
```

---

## 🚀 Installation & launch

1. **Clone the repository**
   ```bash
   git clone https://github.com/blessedrbls/telegram-shop-bot.git
   cd telegram-shop-bot
   ```

2. **Create and activate a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the bot**
   ```bash
   cp .env.example .env
   ```
   Open `.env` and fill in:
   - `BOT_TOKEN`: create a bot with [@BotFather](https://t.me/BotFather) and paste its token
   - `ADMIN_ID`: your Telegram user ID (send any message to [@userinfobot](https://t.me/userinfobot) to get it)

5. **Run**
   ```bash
   python bot.py
   ```
   Open your bot in Telegram and press **/start**. Send **/admin** from the admin account to open the admin panel.

---

## 💡 Possible improvements

- 💳 **Online payments** via Telegram Payments (Stripe, LiqPay, etc.)
- 📊 **Google Sheets** export of orders for the shop owner
- 🗂 Managing categories and editing products from the admin panel
- 🔎 Product search and pagination for large catalogs
- 🎟 Promo codes and discounts
- 🗄 Redis storage for FSM and PostgreSQL for production
- 🐳 Docker and deployment to a VPS

---

## 📬 Contact

Need a bot like this? Contact me on Telegram: [@nonelyyo](https://t.me/nonelyyo)
