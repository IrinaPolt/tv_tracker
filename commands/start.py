import logging

from telegram import Update
from telegram.ext import ContextTypes

from .choose_timezone import choose_timezone
from repositories import UserRepository
from .show_menu import show_menu



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    connection_pool = context.application.bot_data["pool"]

    telegram_id = update.message.from_user.id

    async with connection_pool.connection() as connection:
        user_repo = UserRepository(connection)

        status, res = await user_repo.get_by_telegram_id(telegram_id)

        if not status:
            logging.error(res)
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Что-то пошло не так, попробуйте позже!")
            return

        if not res:
            status, res = await user_repo.add(telegram_id)

            if not status:
                logging.error(res)
                await context.bot.send_message(chat_id=update.effective_chat.id, text="Что-то пошло не так, попробуйте позже!")
                return

            logging.info(f"Добавлен пользователь: {res}")

            await choose_timezone(update, context)
            return

        await show_menu(update, context)
        return
