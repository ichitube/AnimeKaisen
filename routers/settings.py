from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from data import mongodb, character_photo
from keyboards.builders import inline_builder
from utils.states import Name
from filters.chat_type import ChatTypeFilter

router = Router()


@router.message(ChatTypeFilter(chat_type=["private"]), F.text == "⚙️ Настройки")
@router.callback_query(F.data == "settings")
async def settings(message: Message | CallbackQuery):
    account = await mongodb.get_user(message.from_user.id)

    pattern = dict(
        caption=f"❖  ⚙️ <b>Настройки</b>"
                f"\n── •✧✧• ──────────"
                f"\n<blockquote><b>🪪 Имя: {account['name']}"
                f"\n🗺 Вселенная: {account['universe']}"
                f"\n🎴 Персонаж: {account['character'][account['universe']]}</b></blockquote>"
                f"\n── •✧✧• ──────────",
        parse_mode=ParseMode.HTML,
        reply_markup=inline_builder(
            ["🪪 Изменить", "🎴 Изменить", "🗺 Сменить вселенную", "🔙 Назад"],
            ["change_name", "inventory", "change_universe", "main_page"],
            row_width=[2, 1, 1])
    )

    if isinstance(message, CallbackQuery):
        await message.message.edit_caption(**pattern)
    else:
        universe = account['universe']
        character = account['character'][account['universe']]
        avatar = character_photo.get_stats(universe, character, 'avatar')
        avatar_type = character_photo.get_stats(universe, character, 'type')

        if avatar_type == 'photo':
            await message.answer_photo(avatar, **pattern)
        else:
            await message.answer_animation(avatar, **pattern)


@router.callback_query(F.data == "change_name")
async def change_n(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.set_state(Name.name)
    await callback.message.answer("❖ 🪪 Введи новое имя: ")


@router.message(Name.name)
async def form_name(message: Message, state: FSMContext):
    name = message.text
    if len(name) < 15:
        await state.update_data(name=f"<a href='https://t.me/{message.from_user.username}'><b>{message.text}</b></a>")
        data = await state.get_data()
        await state.clear()
        await change_name(message.from_user.id, data['name'])
        await settings(message)
    else:
        await message.answer("❖  ✖️ Имя слишком длинное \n\n🪪 Введи другое: ")


async def change_name(user_id: int, name: str):
    await mongodb.update_user(user_id, {'name': name})


@router.callback_query(F.data == "change_universe")
async def change_universe(callback: CallbackQuery):
    await callback.message.edit_caption(caption="❖ 🗺 Выбери вселенную: ",
                                        reply_markup=inline_builder(
                                            ['⭐️ Allstars', '🗡 Bleach', '🍥 Naruto', '🔥 Jujutsu Kaisen'],
                                            ['Allstars', 'Bleach', 'Naruto', 'Jujutsu Kaisen'],
                                            row_width=1))


# @router.callback_query(F.data.in_(['Allstars', 'Bleach']))
# async def change_universe(callback: CallbackQuery, state: FSMContext):
#     await state.update_data(universe=callback.data)
#     data = await state.get_data()
#     await state.clear()
#     await change_universe_db(callback.from_user.id, data['universe'])
#     await settings(callback)
