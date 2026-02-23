import logging
from psycopg_pool import AsyncConnectionPool
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, filters, MessageHandler

import config
from commands.start import start
from commands.my_shows import my_shows
from commands.choose_timezone import handle_timezone
from commands.show_menu import handle_menu_choice


logging.basicConfig(
    filename="bot.log",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.ERROR
)



async def on_startup(app):
    global connection_pool
    connection_pool = AsyncConnectionPool(
        max_size=config.DB_MAX_CONNECTIONS,
        conninfo=config.DB_URL,
    )
    
    await connection_pool.open()
    app.bot_data["pool"] = connection_pool


async def on_shutdown(app):
    await app.bot_data["pool"].close()



if __name__ == "__main__":
    app = ApplicationBuilder().token(config.TOKEN).post_init(on_startup).post_shutdown(on_shutdown).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("my_shows", my_shows))
    app.add_handler(CallbackQueryHandler(handle_timezone))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_choice))

    print("Бот запущен...")

    app.run_polling()
