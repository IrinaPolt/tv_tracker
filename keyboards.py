from telegram import KeyboardButton, InlineKeyboardButton, ReplyKeyboardMarkup


add_show_keyboard = ReplyKeyboardMarkup(
    [[KeyboardButton("Добавить передачу")]],
    resize_keyboard=True,
    one_time_keyboard=False
)

menu_keyboard = ReplyKeyboardMarkup(
    [[KeyboardButton("Выбрать часовой пояс"), KeyboardButton("Мои передачи")],
    [KeyboardButton("Добавить передачу"), KeyboardButton("Удалить передачу")],
    [KeyboardButton("Ближайшие передачи (2 дня)"), KeyboardButton("Программа на 7 дней")]],
    resize_keyboard=True,
    one_time_keyboard=False
)


timezone_keyboard = [
    [
        InlineKeyboardButton("Калининград (мск - 1)", callback_data="-1"),
        InlineKeyboardButton("Москва", callback_data="0"),
    ],
    [
        InlineKeyboardButton("Самара (мск + 1)", callback_data="1"),
        InlineKeyboardButton("Екатеринбург (мск + 2)", callback_data="2"),
    ],
    [
        
        InlineKeyboardButton("Омск (мск + 3)", callback_data="3"),
        InlineKeyboardButton("Красноярск (мск + 4)", callback_data="4")
    ],
    [
        InlineKeyboardButton("Иркутск (мск + 5)", callback_data="5"),
        InlineKeyboardButton("Чита (мск + 6)", callback_data="6"),
        
    ],
    [
        InlineKeyboardButton("Владивосток (мск + 7)", callback_data="7"),
        InlineKeyboardButton("Магадан (мск + 8)", callback_data="8")
    ],
    [
        InlineKeyboardButton("Камчатка (мск + 9)", callback_data="9"),
    ]
]