import logging

from telegram import InlineKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes

from keyboards import timezone_keyboard
from repositories import UserRepository


async def choose_timezone(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Пожалуйста, выберите часовой пояс:",
        reply_markup=InlineKeyboardMarkup(timezone_keyboard))

    return


async def handle_timezone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    connection_pool = context.application.bot_data["pool"]

    query = update.callback_query

    await query.answer()

    offset = query.data

    async with connection_pool.connection() as connection:
        user_repo = UserRepository(connection)

        status, res = await user_repo.update(update.callback_query.from_user.id, {"timezone": offset})
        if not status:
            logging.error(res)
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Что-то пошло не так, попробуйте позже!")
            return

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Отлично! Вы выбрали часовой пояс: МСК {offset}. Какие передачи вы бы хотели отслеживать?",
        reply_markup=ReplyKeyboardRemove()
    )
    return
