import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from .routers import registration

logging.basicConfig(level=logging.INFO)


def get_bot_token() -> str:
    token = os.getenv("VISA_BOT_TOKEN")
    if not token:
        raise RuntimeError("VISA_BOT_TOKEN muhiti o'zgaruvchisi topilmadi")
    return token


async def main() -> None:
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.include_router(registration)

    bot = Bot(
        token=get_bot_token(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
