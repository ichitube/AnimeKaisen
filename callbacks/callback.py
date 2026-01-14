from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from data import mongodb
from routers import main_menu

router = Router()


@router.callback_query(F.data == "cancel_search")
async def search_opponent(message: Message, callback: CallbackQuery):
    user_id = callback.from_user.id
    await mongodb.update_user(user_id, {"battle.battle.status": 0})
    await main_menu.fill_profile(message)
    await callback.answer()
