import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters import CommandStart
from aiogram.dispatcher.router import Router
from aiogram.dispatcher.dispatcher import Dispatcher as LegacyDispatcher

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = "@AniVerseClip"

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()

async def is_user_subscribed(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ("member", "administrator", "creator")
    except:
        return False

def subscribe_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Kanalga obuna bo‘lish", url=f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}")],
        [InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_sub")]
    ])

@dp.message_handler(CommandStart())
async def start_handler(message: types.Message):
    if not await is_user_subscribed(message.from_user.id):
        await message.answer(
            f"👋 Salom, {message.from_user.full_name}!\n\n"
            f"Botdan foydalanish uchun avval kanalga obuna bo‘ling:",
            reply_markup=subscribe_keyboard()
        )
    else:
        await message.answer("✅ Siz kanalga obuna bo‘lgansiz!\nBotdan foydalanishingiz mumkin.")

@dp.callback_query_handler(lambda c: c.data == "check_sub")
async def check_subscription(callback_query: types.CallbackQuery):
    if await is_user_subscribed(callback_query.from_user.id):
        await callback_query.message.edit_text("✅ Siz kanalga obuna bo‘lgansiz!\nBotdan foydalanishingiz mumkin.")
    else:
        await callback_query.answer("❌ Hali obuna bo‘lmagansiz!", show_alert=True)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
