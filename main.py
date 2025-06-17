import os
import json
import logging
from flask import Flask
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

API_TOKEN = os.environ.get("BOT_TOKEN")
CHANNELS = ['@AniVerseClip', '@StudioNovaOfficial']
ADMINS = ['6486825926', '757504100']

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

logging.basicConfig(level=logging.INFO)

# === Flask for Render Uptime ===
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

# === Custom Keyboard ===
def get_main_keyboard(user_id):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("🔎 Kod bo‘yicha izlash")
    if str(user_id) in ADMINS:
        keyboard.add("⚙️ Admin Panel")
    return keyboard

# === Kanal obuna tekshirish ===
async def is_user_subscribed(user_id):
    for channel in CHANNELS:
        chat_member = await bot.get_chat_member(channel, user_id)
        if chat_member.status in ["left", "kicked"]:
            return False
    return True

@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    if not await is_user_subscribed(message.from_user.id):
        channels_txt = "\n".join([f"👉 {ch}" for ch in CHANNELS])
        await message.answer(
            f"Botdan foydalanish uchun quyidagi kanallarga obuna bo‘ling:\n\n{channels_txt}",
            reply_markup=types.ReplyKeyboardRemove()
        )
    else:
        await message.answer("Assalomu alaykum!", reply_markup=get_main_keyboard(message.from_user.id))

# === Kod bo‘yicha post yuborish ===
@dp.message_handler(lambda message: message.text.startswith("CODE-"))
async def code_handler(message: types.Message):
    code = message.text.strip()
    try:
        with open("anime_codes.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        if code in data:
            await message.answer(data[code])
        else:
            await message.answer("❌ Bunday kod topilmadi.")
    except Exception as e:
        await message.answer("Xatolik yuz berdi.")
        logging.error(f"JSON o‘qishda xatolik: {e}")

# === Admin panel ===
@dp.message_handler(lambda message: message.text == "⚙️ Admin Panel")
async def admin_panel(message: types.Message):
    if str(message.from_user.id) not in ADMINS:
        return await message.answer("Siz admin emassiz.")
    await message.answer("👨‍💻 Admin paneliga xush kelibsiz!")

# === Kod orqali izlashni ko‘rsatish ===
@dp.message_handler(lambda message: message.text == "🔎 Kod bo‘yicha izlash")
async def search_instruction(message: types.Message):
    await message.answer("Iltimos, anime kodi yuboring. Masalan: `CODE-1234`")

# === Flask bilan botni tirik tutish ===
def keep_alive():
    from threading import Thread
    def run():
        app.run(host='0.0.0.0', port=8080)
    Thread(target=run).start()

if __name__ == "__main__":
    keep_alive()
    executor.start_polling(dp, skip_updates=True)
