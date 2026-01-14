from contextlib import suppress

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InputMediaAnimation
from data import mongodb, character_photo
from keyboards import builders
from keyboards.builders import inline_builder, pagination_slaves

router = Router()


def slave_info(clas, point):
    info = ''
    if clas == 'heal':
        info = f"Лечат на {point}❤️ hp каждый ход"
    elif clas == 'attack':
        info = f"наносит {point}🗡 урона каждый ход"
    return info


@router.callback_query(F.data == "slave")
async def slave(callback: CallbackQuery, state: FSMContext):
    inline_id = callback.inline_message_id
    account = await mongodb.get_user(callback.from_user.id)
    slaves = account['inventory']['slaves']
    if not slaves:
        await callback.answer(f"❖ ✖️  У вас нет рабыни, купите в торге рабынь ⛓", show_alert=True)
        return
    result = character_photo.slaves_stats(slaves[0])
    animation = InputMediaAnimation(media=result[0])
    info = slave_info(result[3], result[2])
    await state.update_data(slaves=slaves)
    await callback.message.edit_media(animation, inline_id)
    await callback.message.edit_caption(inline_id,
                                        caption=f"❖ 🔖 {result[1]}"
                                        f"\n──❀*̥˚──◌──◌──❀*̥˚────"
                                        f"\n💮 Служение: {result[6]}"
                                        f"\n\n{info}"
                                        f"\n──❀*̥˚──◌──◌──❀*̥˚────"
                                        f"\n❖ 🔖 1 из {len(slaves)}",
                                        reply_markup=pagination_slaves())


# @router.callback_query(F.data == "slaves")
# async def all_slaves(callback: CallbackQuery, state: FSMContext):
#     inline_id = callback.inline_message_id
#     account = await mongodb.get_user(callback.from_user.id)
#     slaves = account['inventory']['slaves']
#     result = character_photo.slaves_stats(slaves[0])
#     photo = InputMediaAnimation(media=result[0])
#     info = slave_info(result[3], result[2])
#     total_slaves = len(slaves)
#     await state.update_data(slaves=slaves)
#     await callback.message.edit_media(photo, inline_id)
#     await callback.message.edit_caption(
#         inline_id,
#         caption=f"❖ 🔖 {result[1]}"
#                 f"\n──❀*̥˚──◌──◌──❀*̥˚────"
#                 f"\n💮 Служение: {result[6]}"
#                 f"\n\n{info}"
#                 f"\n──❀*̥˚──◌──◌──❀*̥˚────"
#                 f"\n • Цена: {result[5]} 🌟",
#         reply_markup=pagination_slaves())


@router.callback_query(builders.Pagination.filter(F.action.in_(["prev_slave", "next_slave"])))
async def slaves_pagination(callback: CallbackQuery, callback_data: builders.Pagination, state: FSMContext):
    inline_id = callback.inline_message_id
    page_num = int(callback_data.page)
    data = await state.get_data()
    slaves = data.get('slaves')
    if callback_data.action == "next_slave":
        page_num = (page_num + 1) % len(slaves)
    elif callback_data.action == "prev_slave":
        page_num = (page_num - 1) % len(slaves)

    with suppress(TelegramBadRequest):
        result = character_photo.slaves_stats(slaves[page_num])
        photo = InputMediaAnimation(media=result[0])
        info = slave_info(result[3], result[2])
        await state.update_data(slave_set=slaves[page_num])
        await callback.message.edit_media(photo, inline_id)
        await callback.message.edit_caption(
            inline_id,
            caption=f"❖ 🔖 {result[1]}"
                    f"\n──❀*̥˚──◌──◌──❀*̥˚────"
                    f"\n💮 Служение: {result[6]}"
                    f"\n\n{info}"
                    f"\n──❀*̥˚──◌──◌──❀*̥˚────"
                    f"\n❖ 🔖 {page_num + 1} из {len(slaves)}",
            reply_markup=pagination_slaves(page_num)
        )
    await callback.answer()


@router.callback_query(F.data == "set_slave")
async def set_slave(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    data = await state.get_data()
    slaves = data.get('slaves')
    slave_set = data.get('slave_set')
    index = slaves.index(slave_set)
    item = slaves.pop(index)
    slaves.insert(0, item)
    await mongodb.update_user(user_id, {'inventory.slaves': slaves})
    await callback.answer(f"❖  🔖  Вы выбрали эту рабыню", show_alert=True)
