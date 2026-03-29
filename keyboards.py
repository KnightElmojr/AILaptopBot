from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="💻 Ігрові"), KeyboardButton(text="💼 Для офісу")],
    [KeyboardButton(text="🎨 Для дизайну"), KeyboardButton(text="💳 Курс валют")]
], resize_keyboard=True)

def get_laptop_link(model_name):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Переглянути деталі", url="https://rozetka.com.ua/")]
    ])