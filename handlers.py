import requests
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
import keyboards as kb
from database import log_selection

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Вітаю! Я допоможу підібрати ноутбук під ваші потреби.", reply_markup=kb.main_menu)

@router.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer("Доступні команди:\n/start - запуск\n/info - про бота\n/help - допомога")

@router.message(Command('info'))
async def cmd_info(message: Message):
    await message.answer("Цей бот створений для підбору ноутбуків.")


@router.message(F.text == "💻 Ігрові")
async def gaming_laptops(message: Message):
    photo_url = "https://content.rozetka.com.ua/goods/images/big/643597835.jpg"
    log_selection(message.from_user.id, "Ігрові")
    await message.answer_photo(
        photo=photo_url,
        caption="💻 **Категорія: Ігрові**\n\n"
                "Рекомендуємо: **ASUS ROG Strix G16**\n"
                "Особливості: Процесор Intel Core i7, відеокарта RTX 40-ї серії та екран 165 Гц для максимально плавного геймінгу.\n"
                "Орієнтовна ціна: ~65 000 грн",
        reply_markup=kb.get_laptop_link("ASUS ROG")
    )
@router.message(F.text == "🎨 Для дизайну")
async def design_laptops(message: Message):
    photo_url = "https://content1.rozetka.com.ua/goods/images/big/609302730.jpg"
    log_selection(message.from_user.id, "Для дизайну")
    await message.answer_photo(
        photo=photo_url,
        caption="🎨 **Категорія: Для дизайну**\n\n"
                "Рекомендуємо: **Apple MacBook Pro 14**\n"
                "Особливості: Дисплей Liquid Retina XDR, ідеальна передача кольору.\n"
                "Орієнтовна ціна: ~85 000 грн",
        reply_markup=kb.get_laptop_link("MacBook Pro")
    )
@router.message(F.text == "💼 Для офісу")
async def office_laptops(message: Message):
    photo_url = "https://content.rozetka.com.ua/goods/images/big/638558595.jpg"
    log_selection(message.from_user.id, "Для офісу")
    await message.answer_photo(
        photo=photo_url,
        caption="💼 **Категорія: Для офісу**\n\n"
                "Рекомендуємо: **Lenovo ThinkPad E15**\n"
                "Особливості: Надійність, зручна клавіатура та тривалий час роботи.\n"
                "Орієнтовна ціна: ~40 000 грн",
        reply_markup=kb.get_laptop_link("ThinkPad")
    )
@router.message(F.text == "💳 Курс валют")
async def get_currency(message: Message):
    response = requests.get("https://api.monobank.ua/bank/currency")
    if response.status_code == 200:
        data = response.json()
        usd_rate = data[0]['rateBuy']
        await message.answer(f"Поточний курс купівлі USD: {usd_rate} грн.\nЦе допоможе вам розрахувати бюджет у валюті.")
    else:
        await message.answer("Не вдалося отримати дані з API.")


@router.message(F.text)
async def handle_unknown_text(message: Message):
    text = message.text.lower()

    if "привіт" in text or "hi" in text:
        await message.reply("Привіт! Чим можу допомогти з вибором ноутбука? 😊")
    elif "ціна" in text:
        await message.reply(
            "Ціни на ноутбуки зараз дуже залежать від курсу. Натисніть кнопку 'Курс валют', щоб дізнатися актуальний курс!")
    else:
        await message.reply(f"Ви сказали: {message.text}\nВикористовуйте кнопки меню для вибору ноутбука!")

@router.message(F.photo)
async def handle_photo(message: Message):
    await message.answer(f"Дякую за фото! Його ID: `{message.photo[-1].file_id}`", parse_mode="Markdown")