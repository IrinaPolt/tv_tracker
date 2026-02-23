import logging

from telegram import Update
from telegram.ext import ContextTypes

from keyboards import add_show_keyboard
from repositories import SubscriptionRepository, UserRepository


async def my_shows(update: Update, context: ContextTypes.DEFAULT_TYPE):
    connection_pool = context.application.bot_data["pool"]

    telegram_id = update.message.from_user.id
    
    async with connection_pool.connection() as connection:
        user_repo = UserRepository(connection)

        status, res = await user_repo.get_by_telegram_id(telegram_id)

        if not status:
            logging.error(res)
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Что-то пошло не так, попробуйте позже!")
        
        if not res:
            return
        
        sub_repo = SubscriptionRepository(connection)
        shows = [item.title for item in await sub_repo.get_by_user_id(res.id)]
        if not shows:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="У вас пока нет отслеживаемых шоу!",
                reply_markup=add_show_keyboard)
            return

        text = "*Ваши отслеживаемые шоу:*\n\n"

        for i, show in enumerate(shows, 1):
            text += f"{i}. {show}\n"

        await context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode="Markdown")
