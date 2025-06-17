import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery

# Token va kanal nomi
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = "@SIZNING_KANAL"  # <-- o'zingizning kanal username'ini yozing

# Bot va Dispatcher
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# Obuna tekshiruvchi funksiya
async def is_user_subscribed(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ("member", "administrator", "creator")
    except:
        return False

# Inline tugmalar
def subscribe_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Kanalga obuna bo‘lish", url=f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}")],
        [InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_sub")]
    ])
    return keyboard

# /start komandasi
@dp.message(CommandStart())
async def start_handler(message: Message):
    if not await is_user_subscribed(message.from_user.id):
        await message.answer(
            f"👋 Salom, {message.from_user.full_name}!\n\n"
            f"Botdan foydalanish uchun avval kanalga obuna bo‘ling:",
            reply_markup=subscribe_keyboard()
        )
    else:
        await message.answer("✅ Siz kanalga obuna bo‘lgansiz!\nBotdan foydalanishingiz mumkin.")

# Tekshirish callback tugmasi
@dp.callback_query(lambda c: c.data == "check_sub")
async def check_subscription(callback: CallbackQuery):
    if await is_user_subscribed(callback.from_user.id):
        await callback.message.edit_text("✅ Siz kanalga obuna bo‘lgansiz!\nBotdan foydalanishingiz mumkin.")
    else:
        await callback.answer("❌ Hali obuna bo‘lmagansiz!", show_alert=True)

# Botni ishga tushurish
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
