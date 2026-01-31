from aiogram import Router, F
from contextlib import suppress

from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, InputMediaAnimation

from app.keyboards import builders
from app.keyboards.builders import inline_builder, pagination_home
from app.data import mongodb, character_photo

router = Router()


@router.callback_query(F.data == "home")
async def home(callback: CallbackQuery):
    inline_id = callback.inline_message_id
    account = await mongodb.get_user(callback.from_user.id)
    homes = account['inventory']['home']
    if homes == []:
        await callback.answer(f"❖  🔑 У вас нет домов, купите в 🏮 рынке", show_alert=True)
        return
    result = character_photo.home_stats(homes[0])
    photo = InputMediaAnimation(media=result[0])
    await callback.message.edit_media(photo, inline_id)
    await callback.message.edit_caption(inline_id, f"❖ ⚜️ Сила: {result[1]}"
                                        f"\n ── •✧✧• ──────────",
                                        reply_markup=inline_builder(["🔙 Назад", "🏠 Дома"], ["tokio", "invent_home"],
                                                                    row_width=[2]))


@router.callback_query(F.data == "invent_home")
async def inventory_home(callback: CallbackQuery, state: FSMContext):
    inline_id = callback.inline_message_id
    account = await mongodb.get_user(callback.from_user.id)
    homes = account['inventory']['home']
    result = character_photo.home_stats(homes[0])
    photo = InputMediaAnimation(media=result[0])
    total_homes = len(account['inventory']['home'])
    await state.update_data(homes=homes)
    await callback.message.edit_media(photo, inline_id)
    await callback.message.edit_caption(inline_id, f"❖ ⚜️ Сила: {result[1]}"
                                        f"\n ── •✧✧• ──────────"
                                        f"\n❖ 🏠 дома: {total_homes}",
                                        reply_markup=pagination_home())


@router.callback_query(builders.Pagination.filter(F.action.in_(["prev_home", "next_home"])))
async def home_pagination(callback: CallbackQuery, callback_data: builders.Pagination, state: FSMContext):
    inline_id = callback.inline_message_id
    page_num = int(callback_data.page)
    data = await state.get_data()
    homes = data.get('homes')
    if callback_data.action == "next_home":
        page_num = (page_num + 1) % len(homes)
    elif callback_data.action == "prev_home":
        page_num = (page_num - 1) % len(homes)

    with suppress(TelegramBadRequest):
        total_homes = len(homes)
        result = character_photo.home_stats(homes[page_num])
        photo = InputMediaAnimation(media=result[0])
        await state.update_data(home_set=homes[page_num])
        await callback.message.edit_media(photo, inline_id)
        await callback.message.edit_caption(
            inline_id,
            f"❖ ⚜️ Сила: {result[1]}"
            f"\n ── •✧✧• ──────────"
            f"\n❖ 🏠 дома: {total_homes}",
            reply_markup=pagination_home(page_num)
        )
    await callback.answer()


@router.callback_query(F.data == "set_home")
async def set_home(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    data = await state.get_data()
    homes = data.get('homes')
    home_set = data.get('home_set')
    index = homes.index(home_set)
    item = homes.pop(index)
    homes.insert(0, item)
    await mongodb.update_user(user_id, {'inventory.home': homes})
    await callback.answer(f"❖  🏠  Вы переехали в этот дом", show_alert=True)
