from telegram import Update
from telegram.ext import ContextTypes

from keyboards import menu_keyboard
from .add_subscription import add_subscription
from .remove_subscription import remove_subscription
from .choose_timezone import choose_timezone
from .my_shows import my_shows
from .show_next_seven_days import show_next_seven_days
from .show_next_two_days import show_next_two_days


async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text(
            text="Главное меню: выберите действие",
            reply_markup=menu_keyboard
        )
    elif update.callback_query:
        await update.callback_query.edit_message_text(
            text="Главное меню: выберите действие",
            reply_markup=menu_keyboard
        )


async def handle_menu_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "Выбрать часовой пояс":
        await choose_timezone(update, context)
    elif text == "Мои передачи":
        await my_shows(update, context)
    elif text == "Добавить передачу":
        context.user_data["awaiting_subscription"] = True
        await update.message.reply_text(
            "Пожалуйста, введите название шоу, которое хотите добавить в список отслеживания", reply_markup=menu_keyboard)
        return

    elif text == "Удалить передачу":
        context.user_data["awaiting_removal"] = True
        await update.message.reply_text(
            "Пожалуйста, введите название шоу, которое хотите удалить из списка отслеживания", reply_markup=menu_keyboard)
        return
    elif text == "Ближайшие передачи (2 дня)":
        await show_next_two_days(update, context)
    elif text == "Программа на 7 дней":
        await show_next_seven_days(update, context)
    else:
        # проверяем, в каком режиме пользователь
        if context.user_data.get("awaiting_subscription"):
            await add_subscription(update, context)
            context.user_data["awaiting_subscription"] = False
            return
        elif context.user_data.get("awaiting_removal"):
            await remove_subscription(update, context)
            context.user_data["awaiting_removal"] = False
            return

        await update.message.reply_text(
            "Неизвестная команда, используйте меню снизу.", reply_markup=menu_keyboard)
