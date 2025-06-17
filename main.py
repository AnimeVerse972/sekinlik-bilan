import os
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import CommandStart
from aiogram.client.bot import DefaultBotProperties

# ENV variables dan token olish
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Render.com dagi Environmentga qo'yilgan token
CHANNEL_USERNAME = "@SIZNING_KANAL"  # <- O'zingizning kanal nomingizni yozing

# Bot va dispatcher
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
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
    kb = InlineKeyboardBuilder()
    kb.button(text="📢 Kanalga obuna bo‘lish", url=f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}")
    kb.button(text="✅ Tekshirish", callback_data="check_sub")
    return kb.as_markup()

# /start komandasi
@dp.message(CommandStart())
async def cmd_start(message: Message):
    is_subscribed = await is_user_subscribed(message.from_user.id)
    if not is_subscribed:
        await message.answer(
            f"👋 Salom, {message.from_user.full_name}!\n\n"
            f"Botdan foydalanish uchun avval bizning kanalga obuna bo‘ling:",
            reply_markup=subscribe_keyboard()
        )
    else:
        await message.answer("✅ Siz kanalga obuna bo‘lgansiz!\nBotdan foydalanishingiz mumkin.")

# Callback: Tekshirish
@dp.callback_query(F.data == "check_sub")
async def check_subscription(callback: CallbackQuery):
    is_subscribed = await is_user_subscribed(callback.from_user.id)
    if is_subscribed:
        await callback.message.edit_text("✅ Siz kanalga obuna bo‘lgansiz!\nBotdan foydalanishingiz mumkin.")
    else:
        await callback.answer("❌ Hali obuna bo‘lmagansiz!", show_alert=True)

# Asosiy ishga tushirish
async def main():
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
