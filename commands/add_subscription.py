import logging

from telegram import Update
from telegram.ext import ContextTypes

from models import Subscription
from repositories import SubscriptionRepository, UserRepository



async def add_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    connection_pool = context.application.bot_data["pool"]

    title = update.message.text

    telegram_id = update.message.from_user.id

    async with connection_pool.connection() as connection:
        user_repo = UserRepository(connection)
        status, user = await user_repo.get_by_telegram_id(telegram_id)

        sub_repo = SubscriptionRepository(connection)
        status, res = await sub_repo.add(Subscription(id=None, user_id=user.id, title=title))
        if not status:
            logging.error(res)
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Не удалось добавить подписку, попробуйте позже."
            )
            return

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Подписка на «{title}» успешно добавлена!"
    )
