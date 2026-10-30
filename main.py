import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from keyboards import main_keyboard
from games import router


logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)

dp = Dispatcher(storage=MemoryStorage())

dp.include_router(router)


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        f"Assalomu alaykum, {message.from_user.first_name}! 👋\n\n"
        "🎮 **10 ta o‘yin markaziga xush kelibsiz!**\n\n"
        "Bu yerda mantiq, xotira, tezlik va bilimlaringizni "
        "sinab ko‘rishingiz mumkin.\n\n"
        "O‘yinlardan birini tanlang:",
        reply_markup=main_keyboard(),
        parse_mode="Markdown",
    )


async def main():
    print("Telegram bot ishga tushmoqda...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot to‘xtatildi.")