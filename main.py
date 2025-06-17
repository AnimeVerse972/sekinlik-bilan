import os
from flask import Flask
from threading import Thread
from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = os.environ.get("BOT_TOKEN")  # Render.com uchun
ADMINS = ['6486825926']  # Admin user ID lar ro'yxati
CHANNELS = ['@AniVerseClip', '@StudioNovaOfficial']  # Majburiy obuna kanallar

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Flask server
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot ishlayapti!"

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Obuna tekshirish funksiyasi
async def is_subscribed(user_id):
    for channel in CHANNELS:
        chat_member = await bot.get_chat_member(channel, user_id)
        if chat_member.status in ['left', 'kicked']:
            return False
    return True

# Start komandasi
@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    if not await is_subscribed(user_id):
        btn = types.InlineKeyboardMarkup()
        for ch in CHANNELS:
            btn.add(types.InlineKeyboardButton(text=f"Obuna bo‘lish ➕", url=f"https://t.me/{ch[1:]}"))
        btn.add(types.InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_subs"))
        await message.answer("Botdan foydalanish uchun quyidagi kanallarga obuna bo‘ling:", reply_markup=btn)
        return

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("📥 Kod yuborish")
    if str(user_id) in ADMINS:
        keyboard.add("🔐 Admin panel")
    await message.answer("Xush kelibsiz! Anime kodini yuboring:", reply_markup=keyboard)

# Tekshirish tugmasi
@dp.callback_query_handler(lambda c: c.data == 'check_subs')
async def check_subs(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if await is_subscribed(user_id):
        await callback.message.delete()
        await callback.message.answer("✅ Obuna tekshirildi. Endi botdan foydalanishingiz mumkin.")
    else:
        await callback.answer("❌ Hali ham obuna bo‘lmagansiz!", show_alert=True)

# Kod yuborish
@dp.message_handler(lambda message: message.text == "📥 Kod yuborish")
async def ask_code(message: types.Message):
    await message.answer("Anime kodini yuboring:")

# Kod qabul qilish
@dp.message_handler(lambda message: message.text.startswith("A"))
async def handle_code(message: types.Message):
    code = message.text.strip()
    # Bu yerga kod bo‘yicha javobni sozlashingiz mumkin
    await message.answer(f"📺 Siz yuborgan kod: {code}\nAnime haqida ma'lumot: ...")

# Admin panel
@dp.message_handler(lambda message: message.text == "🔐 Admin panel")
async def admin_panel(message: types.Message):
    if str(message.from_user.id) not in ADMINS:
        await message.answer("❌ Siz admin emassiz!")
        return

    panel = types.ReplyKeyboardMarkup(resize_keyboard=True)
    panel.add("📢 Post yuborish", "⬅️ Orqaga")
    await message.answer("🔐 Admin paneliga xush kelibsiz.", reply_markup=panel)

# Post yuborish
@dp.message_handler(lambda message: message.text == "📢 Post yuborish")
async def ask_post(message: types.Message):
    await message.answer("📨 Foydalanuvchilarga yuboriladigan xabarni yuboring:")

# Orqaga
@dp.message_handler(lambda message: message.text == "⬅️ Orqaga")
async def back(message: types.Message):
    await start_cmd(message)

# Flaskni ishga tushurish
keep_alive()

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
