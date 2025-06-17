import os
import json
import logging
from flask import Flask
from threading import Thread
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# .env yoki Render'dan token va sozlamalar
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMINS = ['6486825926', '757504100']  # o'zingizni ID kiritasiz
CHANNELS = ['@AniVerseClip', '@StudioNovaOfficial']

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# 📁 JSON'dan anime kodlar bazasini yuklaymiz
with open("anime_data.json", "r", encoding="utf-8") as f:
    anime_db = json.load(f)

# ✅ Majburiy obuna tekshiruv
async def check_subscription(user_id):
    for channel in CHANNELS:
        chat_member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
        if chat_member.status not in ['member', 'creator', 'administrator']:
            return False
    return True

# 🎛️ Start komandasi
@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    if not await check_subscription(user_id):
        btn = types.InlineKeyboardMarkup()
        for ch in CHANNELS:
            btn.add(types.InlineKeyboardButton(f"➕ Obuna bo'lish", url=f"https://t.me/{ch[1:]}"))
        btn.add(types.InlineKeyboardButton("✅ Tekshirish", callback_data="check_subs"))
        await message.answer("📛 Iltimos, quyidagi kanallarga obuna bo‘ling:", reply_markup=btn)
    else:
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        if str(user_id) in ADMINS:
            markup.add(KeyboardButton("🔧 Admin panel"))
        await message.answer("🎬 Anime kodini yuboring:", reply_markup=markup)

# 🔄 Obuna qayta tekshirish
@dp.callback_query_handler(lambda c: c.data == "check_subs")
async def callback_check(call: types.CallbackQuery):
    if await check_subscription(call.from_user.id):
        await call.message.delete()
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        if str(call.from_user.id) in ADMINS:
            markup.add(KeyboardButton("🔧 Admin panel"))
        await call.message.answer("✅ Rahmat! Endi anime kodini yuboring:", reply_markup=markup)
    else:
        await call.answer("❌ Hali ham obuna emassiz", show_alert=True)

# 🛠 Admin panel
@dp.message_handler(lambda message: message.text == "🔧 Admin panel")
async def admin_panel(message: types.Message):
    if str(message.from_user.id) in ADMINS:
        await message.answer("👑 Admin panelga xush kelibsiz.\nHozircha bu yer bo‘sh.")

# 🔎 Kod qidirish
@dp.message_handler(lambda message: message.text)
async def handle_anime_code(message: types.Message):
    code = message.text.strip().lower()
    if not await check_subscription(message.from_user.id):
        await start_cmd(message)
        return

    if code in anime_db:
        await message.answer(f"🔍 Topildi:\n{anime_db[code]}")
    else:
        await message.answer("❗ Kod bo‘yicha ma'lumot topilmadi.")

# 🌐 Flask server (24/7 hosting uchun)
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot ishlayapti!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    Thread(target=run).start()

# ▶️ Botni ishga tushirish
if __name__ == '__main__':
    keep_alive()
    executor.start_polling(dp, skip_updates=True)
