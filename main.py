import os
import logging
import json  # yoki import csv
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keep_alive import keep_alive

API_TOKEN = os.environ.get('BOT_TOKEN')
CHANNELS = ['@AniVerseClip', '@StudioNovaOfficial']
ADMINS = ['6486825926', '757504100']  # ID shaklida

bot = Bot(token=API_TOKEN, parse_mode='HTML')
dp = Dispatcher(bot)

# 🔹 Keyboard tugmalar
def get_admin_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("📊 Admin panel"))
    return keyboard

# 🔹 Kanal obuna tekshiruvi
async def is_subscribed(user_id):
    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in ['left', 'kicked']:
                return False
        except Exception:
            return False
    return True

# 🔹 Start komandasi
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    user_id = str(message.from_user.id)

    if not await is_subscribed(user_id):
        btn = InlineKeyboardMarkup()
        for ch in CHANNELS:
            btn.add(InlineKeyboardButton(f"Obuna bo‘lish: {ch}", url=f"https://t.me/{ch[1:]}"))
        await message.answer("Botdan foydalanish uchun quyidagi kanallarga obuna bo‘ling:", reply_markup=btn)
        return

    if user_id in ADMINS:
        await message.answer("Xush kelibsiz, admin!", reply_markup=get_admin_keyboard())
    else:
        await message.answer("Xush kelibsiz! Kod yuboring:")

# 🔹 Admin panel tugmasi
@dp.message_handler(lambda message: message.text == "📊 Admin panel")
async def admin_panel(message: types.Message):
    if str(message.from_user.id) not in ADMINS:
        return
    await message.answer("Bu yerda admin statistikasi yoki tugmalar chiqishi mumkin.")

# 🔹 Anime kodini yuborish
@dp.message_handler()
async def handle_code(message: types.Message):
    code = message.text.strip().lower()

    try:
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        await message.reply("Ma'lumotlar yuklab bo‘lmadi.")
        return

    if code in data:
        await message.reply(data[code])
    else:
        await message.reply("Bunday kod topilmadi!")

# 🔹 Flask orqali botni doimiy yoqish
keep_alive()

# 🔹 Logging
logging.basicConfig(level=logging.INFO)

# 🔹 Botni ishga tushirish
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
