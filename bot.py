"""
Entry point: run `python bot.py` to start the bot.
"""
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeChat

import database as db
from config import ADMIN_ID, BOT_TOKEN
from handlers import admin, user


async def set_commands(bot: Bot) -> None:
    """Commands shown in the "Menu" button next to the input field."""
    commands = [
        BotCommand(command="start", description="Start / restart the bot"),
        BotCommand(command="language", description="Change language"),
        BotCommand(command="cancel", description="Cancel the current action"),
    ]
    await bot.set_my_commands(commands)
    # The admin additionally sees /admin
    try:
        await bot.set_my_commands(
            commands + [BotCommand(command="admin", description="Admin panel")],
            scope=BotCommandScopeChat(chat_id=ADMIN_ID),
        )
    except TelegramAPIError:
        logging.warning("Can't set admin commands: check ADMIN_ID and press /start in the bot")


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    await db.init_db()

    # parse_mode=HTML lets us use <b>bold</b> and <i>italic</i> in all texts
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    # MemoryStorage keeps FSM states in RAM (they reset when the bot restarts)
    dp = Dispatcher(storage=MemoryStorage())

    # Order matters: the user router goes first so /cancel works everywhere
    dp.include_routers(user.router, admin.router)

    await set_commands(bot)
    # Skip messages that were sent while the bot was offline
    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("Bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped")
