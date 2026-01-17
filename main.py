import os
import sys
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from routers import (
    registration, battle_k, gacha, banner, settings, navigation, main_menu, inventory,
    craft, slaves, arena, battle_ai, card_battle, card_battle_ai
)
from data import character_photo, mongodb
from routers.tokio import tokio, dungeon, store, Pay, home, quests, clans, boss
from AI import characters_brain
from handlers import chat_commands, admins
from payments import stars
from chat_handlers import chat_battle
from callbacks import callback
# from middlewares.AntiFloodMiddleWare import AntiFloodMiddleware, AntiFloodMiddlewareM
from keyboards.builders import menu_button

# --- МИНИМАЛЬНО: просто приглушаем логи ---
logging.basicConfig(level=logging.WARNING)
logging.getLogger("aiogram").setLevel(logging.WARNING)
logging.getLogger("aiogram.event").setLevel(logging.WARNING)
logging.getLogger("aiogram.dispatcher").setLevel(logging.WARNING)
# ------------------------------------------

# Чтобы гарантировать корректные импорты при запуске из разных мест
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Токен можно держать в переменной окружения BOT_TOKEN
BOT_TOKEN = os.getenv("BOT_TOKEN", "Если нет берется этот")

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)

# Передаём инстанс бота в модуль БД (для рассылок/служебных уведомлений)
mongodb.set_bot(bot)

async def on_startup() -> None:
    await mongodb.ensure_indexes()
    """Хук старта: мягко сбрасываем только активные/в бою бои и шлём меню этим пользователям."""
    stats = await mongodb.reset_active_battles_and_notify(menu_button)
    # Это INFO теперь не видно при уровне WARNING, но пусть останется на будущее
    logging.info("[startup] active reset: %s", stats)

async def on_shutdown() -> None:
    """Хук завершения: аккуратно закрываем HTTP-сессию бота."""
    await bot.session.close()
    logging.info("[shutdown] bot session closed")

dp = Dispatcher()
dp.startup.register(on_startup)
dp.shutdown.register(on_shutdown)

async def main() -> None:
    # Роутеры
    dp.include_routers(
        registration.router,
        callback.router,
        main_menu.router,
        navigation.router,
        battle_k.router,
        chat_battle.router,
        gacha.router,
        banner.router,
        settings.router,
        tokio.router,
        dungeon.router,
        store.router,
        Pay.router,
        inventory.router,
        craft.router,
        chat_commands.router,
        character_photo.router,
        slaves.router,
        home.router,
        admins.router,
        stars.router,
        arena.router,
        battle_ai.router,
        card_battle.router,
        card_battle_ai.router,
        quests.router,
        clans.router,
        boss.router,
        characters_brain.router,
    )

    # Мидлвари
    # dp.callback_query.middleware(AntiFloodMiddleware())
    # dp.message.middleware(AntiFloodMiddlewareM())

    # снимаем вебхук
    await bot.delete_webhook(drop_pending_updates=True)

    # Запуск поллинга
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
