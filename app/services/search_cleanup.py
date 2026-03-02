from datetime import datetime, timedelta
from aiogram import Bot
import asyncio

from aiogram.types import ReplyKeyboardRemove

from app.data import mongodb
from app.keyboards.builders import menu_button

async def cancel_expired_searches(bot: Bot):
    timeout = datetime.utcnow() - timedelta(minutes=5)

    expired_users = await mongodb.db.users.find(
        {
            "battle.battle.status": 1,
            "battle.battle.search_started_at": {"$lt": timeout}
        },
        {"_id": 1}
    ).to_list(None)

    if not expired_users:
        return

    ids = [u["_id"] for u in expired_users]

    # 1️⃣ Сбрасываем поиск
    await mongodb.db.users.update_many(
        {"_id": {"$in": ids}},
        {
            "$set": {
                "battle.battle.status": 0,
                "battle.battle.search_started_at": None
            }
        }
    )

    # 2️⃣ Уведомляем игроков
    for user_id in ids:
        try:
            await bot.send_message(
                user_id,
                '<tg-emoji emoji-id="5193004760994685438">⌛</tg-emoji> Поиск соперника отменён.\n'
                "Сейчас нет активных игроков. Попробуйте позже.",
                reply_markup=menu_button())

        except Exception:
            pass
