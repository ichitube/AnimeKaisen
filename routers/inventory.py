from contextlib import suppress

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InputMediaAnimation, InputMediaPhoto
from data import mongodb, character_photo
from filters.chat_type import ChatTypeFilter
from keyboards import builders

router = Router()


async def get_inventory(user_id, rarity):
    if rarity == "soccer_":
        rarity = "soccer"
    elif rarity == "halloween_":
        rarity = "halloween"
    elif rarity == "common_":
        rarity = "common"
    elif rarity == "rare_":
        rarity = "rare"
    elif rarity == "epic_":
        rarity = "epic"
    elif rarity == "legendary_":
        rarity = "legendary"
    elif rarity == "mythical_":
        rarity = "mythical"
    elif rarity == "divine_":
        rarity = "divine"
    account = await mongodb.get_user(user_id)
    universe = account['universe']
    invent = account['inventory']['characters'][universe]
    return invent[rarity], universe


@router.message(
    ChatTypeFilter(chat_type=["private"]),
    F.text == "🥡 Инвентарь"
)
@router.callback_query(F.data == "inventory")
async def inventory(callback: CallbackQuery | Message):
    media_id = "CgACAgIAAx0CfstymgACRv5orIILKQTm88Zac71MqWBr9tYTQwAC8ZkAAu8IaUknwseMmKsSyTYE"
    user_id = callback.from_user.id
    account = await mongodb.get_user(user_id)
    universe = account['universe']
    total_divine = len(account['inventory']['characters'][universe].get('divine', {}))
    total_mythical = len(account['inventory']['characters'][universe].get('mythical', {}))
    total_legendary = len(account['inventory']['characters'][universe].get('legendary', {}))
    total_epic = len(account['inventory']['characters'][universe].get('epic', {}))
    total_rare = len(account['inventory']['characters'][universe].get('rare', {}))
    total_common = len(account['inventory']['characters'][universe].get('common', {}))
    total_elements = 0
    for sublist in account['inventory']['characters'][universe].values():
        for item in sublist:
            if isinstance(item, str):
                total_elements += 1
    msg = (f"\n❖ 🃏 〢 Количество карт: {total_elements}"
           f"\n ── •✧✧• ──────────"
           f"<blockquote>"
           f"\n\n❖ 🌠 Божественные 🌟 {total_divine}"
           f"\n❖ 🌌 Мифические ⭐️ {total_mythical}"
           f"\n❖ 🌅 Легендарные ⭐️ {total_legendary}"
           f"\n❖ 🎆 Эпические ⭐️ {total_epic}"
           f"\n❖ 🎇 Редкие ⭐️ {total_rare}"
           f"\n❖ 🌁 Обычные ⭐️ {total_common}</blockquote>")
    buttons = [f"🌠 Божественные 🌟 {total_divine}", f"🌌 Мифические ⭐️ {total_mythical}", f"🌅 Легендарные ⭐️ {total_legendary}",
               f"🎆 Эпические ⭐️ {total_epic}", f"🎇 Редкие ⭐️ {total_rare}", f"🌁 Обычные ⭐️ {total_common}", "🔙 Назад"]
    callbacks = ["divine", "mythical", "legendary", "epic", "rare", "common", "main_page"]

    # buttons = ["🌠 Божественные", f"🌟 {total_divine}", "🌌 Мифические", f"⭐️ {total_mythical}", "🌅 Легендарные",
    #            f"⭐️ {total_legendary}",
    #            "🎆 Эпические", f"⭐️ {total_epic}", "🎇 Редкие", f"⭐️ {total_rare}", "🌁 Обычные", f"⭐️ {total_common}",
    #            "🔙 Назад"]
    # callbacks = ["divine", "divine", "mythical", "mythical", "legendary", "legendary", "epic", "epic", "rare", "rare",
    #              "common", "common", "main_page"]

    if universe == "Allstars":
        if "halloween" in account['inventory']['characters']['Allstars']:
            total_halloween = len(account['inventory']['characters']['Allstars'].get('halloween', {}))
            buttons.insert(0, f"👻 Halloween 🎃 {total_halloween}")
            callbacks.insert(0, "halloween")
        # if "soccer" not in account['inventory']['characters']['Allstars']:
        #     account = await mongodb.get_user(user_id)
        #     await mongodb.update_user(user_id, {"inventory.characters.Allstars.soccer": []})
        #     total_soccer = len(account['inventory']['items'].get('soccer', {}))
        #     buttons.insert(0, f"⚽️ Soccer {total_soccer}")
        #     callbacks.insert(0, "soccer")

    pattern = dict(caption=f"🥡 Инвентарь"
                           f"\n── •✧✧• ──────────"
                           f"\n<blockquote>❖ Здесь вы можете увидеть все ваши 🃏 карты "
                           f"и установить их в качестве основного 🎴 персонажа."
                           f"\n❖ Выберите ✨ редкость карты, чтобы посмотреть.</blockquote>"
                           # f"\n── •✧✧• ─────────"
                           "\n➖➖➖➖➖➖➖➖➖➖➖"
                           f"\n❖ 🃏 Количество карт: {total_elements}",
                   reply_markup=builders.inline_builder(
                       buttons,
                       callbacks, row_width=[1]))
    if isinstance(callback, CallbackQuery):
        inline_id = callback.inline_message_id
        media = InputMediaAnimation(media=media_id)
        await callback.message.edit_media(media, inline_id)
        await callback.message.edit_caption(inline_id, **pattern)
    else:
        await callback.answer_animation(media_id, **pattern)


@router.callback_query(F.data.in_(['soccer', 'halloween', 'common', 'rare',
                                   'epic', 'legendary', 'mythical', 'divine']))
async def inventory(callback: CallbackQuery, state: FSMContext):
    try:
        await state.update_data(rarity=callback.data)
        inline_id = callback.inline_message_id
        user_id = callback.from_user.id
        invent, universe = await get_inventory(user_id, callback.data)
        if invent == []:
            await callback.answer("❖ ✖️ У вас нет карт данной редкости", show_alert=True)
            return
        await state.update_data(character=invent[0])
        await state.update_data(universe=universe)
        avatar = character_photo.get_stats(universe, invent[0], 'avatar')
        avatar_type = character_photo.get_stats(universe, invent[0], 'type')
        if avatar_type == 'photo':
            photo = InputMediaPhoto(media=avatar)
        else:
            photo = InputMediaAnimation(media=avatar)
        rarity = character_photo.get_stats(universe, invent[0], 'rarity')
        msg = f"❖ ✨ Редкость: {rarity}"
        if universe not in ['Allstars', 'Allstars(old)']:
            strength = character_photo.get_stats(universe, invent[0], 'arena')['strength']
            agility = character_photo.get_stats(universe, invent[0], 'arena')['agility']
            intelligence = character_photo.get_stats(universe, invent[0], 'arena')['intelligence']
            power = character_photo.get_stats(universe, invent[0], 'arena')['power']
            msg = (f"❖ ✨ Редкость: {rarity}"
                   f"\n❖ 🗺 Вселенная: {universe}"
                   f"\n\n   ✊🏻 Сила: {strength}"
                   f"\n   👣 Ловкость: {agility}"
                   f"\n   🧠 Интелект: {intelligence}"
                   f"\n   ⚜️ Мощь: {power}")
        await callback.message.edit_media(photo, inline_id)
        await callback.message.edit_caption(inline_id, caption=f"🎴 {invent[0]}"
                                                               # f"\n ── •✧✧• ───────"
                                                               f"<blockquote>{msg}</blockquote>"
                                                               f"\n──❀*̥˚──◌──◌──❀*̥˚"
                                                               f"\n❖ 🔖 1 из {len(invent)}",
                                            reply_markup=builders.pagination_keyboard(universe, invent[0]))
    except KeyError:
        await callback.message.edit_caption(caption="❖ 〰️ В процессе обновления сессия была остановлена, вызовите "
                              "🥡 Инвентарь еще раз", reply_markup=None)


@router.callback_query(builders.Pagination.filter(F.action.in_(["prev", "next"])))
async def inventory(callback: CallbackQuery, callback_data: builders.Pagination, state: FSMContext):
    try:
        inline_id = callback.inline_message_id
        page_num = int(callback_data.page)
        user_data = await state.get_data()
        invent, universe = await get_inventory(callback.from_user.id, user_data['rarity'])

        if callback_data.action == "next":
            page_num = (page_num + 1) % len(invent)
        elif callback_data.action == "prev":
            page_num = (page_num - 1) % len(invent)

        with suppress(TelegramBadRequest):
            await state.update_data(character=invent[page_num])
            avatar = character_photo.get_stats(universe, invent[page_num], 'avatar')
            avatar_type = character_photo.get_stats(universe, invent[page_num], 'type')
            if avatar_type == 'photo':
                photo = InputMediaPhoto(media=avatar)
            else:
                photo = InputMediaAnimation(media=avatar)
            rarity = character_photo.get_stats(universe, invent[page_num], 'rarity')
            msg = f"❖ ✨ Редкость: {rarity}"
            if universe not in ['Allstars', 'Allstars(old)']:
                strength = character_photo.get_stats(universe, invent[page_num], 'arena')['strength']
                agility = character_photo.get_stats(universe, invent[page_num], 'arena')['agility']
                intelligence = character_photo.get_stats(universe, invent[page_num], 'arena')['intelligence']
                power = character_photo.get_stats(universe, invent[page_num], 'arena')['power']
                msg = (f"❖ ✨ Редкость: {rarity}"
                       f"\n❖ 🗺 Вселенная: {universe}"
                       f"\n\n   ✊🏻 Сила: {strength}"
                       f"\n   👣 Ловкость: {agility}"
                       f"\n   🧠 Интелект: {intelligence}"
                       f"\n   ⚜️ Мощь: {power}")

            await callback.message.edit_media(photo, inline_id)
            await callback.message.edit_caption(
                inline_id,
                caption=f"🎴 {invent[page_num]}"
                        # f"\n ── •✧✧• ───────"
                        f"<blockquote>{msg}</blockquote>"
                        f"\n──❀*̥˚──◌──◌──❀*̥˚"
                        f"\n❖ 🔖 {page_num + 1} из {len(invent)}",
                reply_markup=builders.pagination_keyboard(universe=universe, character=invent[page_num], page=page_num)
            )
        await callback.answer()
    except KeyError:
        await callback.message.edit_caption(caption="❖ 〰️ В процессе обновления сессия была остановлена, вызовите "
                                            "🥡 Инвентарь еще раз", reply_markup=None)


@router.callback_query(F.data == "change_character")
async def change_ch(callback: CallbackQuery, state: FSMContext):
    try:
        user_id = callback.from_user.id
        data = await state.get_data()
        await mongodb.change_char(user_id, data.get('universe'), data.get('character'))
        await callback.answer("🎴 Вы успешно изменили персонажа", show_alert=True)
    except KeyError:
        await callback.message.edit_caption(caption="❖ 〰️ В процессе обновления сессия была остановлена, вызовите "
                                            "🥡 Инвентарь еще раз", reply_markup=None)


@router.message(
    F.text.in_(["Карты", "карты", "инвентарь", "Инвентарь"])
)
@router.callback_query(F.data.startswith("inventory_"))
async def inventory(callback: CallbackQuery | Message, state: FSMContext):
    user_id = callback.from_user.id
    if isinstance(callback, CallbackQuery):
        user_data = await state.get_data()
        user_id = user_data.get('user_id')
        user_cb_id = int(callback.data.replace("inventory_", ""))
        if user_cb_id != user_id:
            await callback.answer("❖ ✖️ Это не ваш инвентарь", show_alert=True)
            return
    await state.update_data(user_id=user_id)
    media_id = "CgACAgIAAx0CfstymgACRv5orIILKQTm88Zac71MqWBr9tYTQwAC8ZkAAu8IaUknwseMmKsSyTYE"
    user_id = callback.from_user.id
    account = await mongodb.get_user(user_id)
    universe = account['universe']
    total_divine = len(account['inventory']['characters'][universe].get('divine', {}))
    total_mythical = len(account['inventory']['characters'][universe].get('mythical', {}))
    total_legendary = len(account['inventory']['characters'][universe].get('legendary', {}))
    total_epic = len(account['inventory']['characters'][universe].get('epic', {}))
    total_rare = len(account['inventory']['characters'][universe].get('rare', {}))
    total_common = len(account['inventory']['characters'][universe].get('common', {}))
    total_elements = 0
    for sublist in account['inventory']['characters'][universe].values():
        for item in sublist:
            if isinstance(item, str):
                total_elements += 1
    msg = (f"\n❖ 🃏 Количество карт: {total_elements}"
           f"\n\n❖ 🌠 Божественные 🌟 {total_divine}"
           f"\n❖ 🌌 Мифические ⭐️ {total_mythical}"
           f"\n❖ 🌅 Легендарные ⭐️ {total_legendary}"
           f"\n❖ 🎆 Эпические ⭐️ {total_epic}"
           f"\n❖ 🎇 Редкие ⭐️ {total_rare}"
           f"\n❖ 🌁 Обычные ⭐️ {total_common}")
    buttons = [f"🌠 Божественные 🌟 {total_divine}", f"🌌 Мифические ⭐️ {total_mythical}", f"🌅 Легендарные ⭐️ {total_legendary}",
               f"🎆 Эпические ⭐️ {total_epic}", f"🎇 Редкие ⭐️ {total_rare}", f"🌁 Обычные ⭐️ {total_common}"]
    callbacks = [f"divine_{user_id}", f"mythical_{user_id}", f"legendary_{user_id}", f"epic_{user_id}",
                 f"rare_{user_id}", f"common_{user_id}"]

    if universe == "Allstars":
        if "halloween" in account['inventory']['characters']['Allstars']:
            total_halloween = len(account['inventory']['characters']['Allstars'].get('halloween', {}))
            buttons.insert(0, f"👻 Halloween 🎃 {total_halloween}")
            callbacks.insert(0, f"halloween_{user_id}")
        # if "soccer" not in account['inventory']['characters']['Allstars']:
        #     account = await mongodb.get_user(user_id)
        #     await mongodb.update_user(user_id, {"inventory.characters.Allstars.soccer": []})
        #     total_soccer = len(account['inventory']['items'].get('soccer', {}))
        #     buttons.insert(0, f"⚽️ Soccer {total_soccer}")
        #     callbacks.insert(0, "soccer")

    pattern = dict(caption=f"🥡 Инвентарь"
                           f"\n── •✧✧• ──────────"
                           f"\n<blockquote>❖ Здесь вы можете увидеть все ваши 🃏 карты "
                           f"и установить их в качестве основного 🎴 персонажа."
                           f"\n❖ Выберите ✨ редкость карты, чтобы посмотреть.</blockquote>"
                           "\n➖➖➖➖➖➖➖➖➖"
                           # f"\n── •✧✧• ──────────"
                           f"\n❖ 🃏 Количество карт: {total_elements}",
                   reply_markup=builders.inline_builder(
                       buttons,
                       callbacks, row_width=[1]))
    if isinstance(callback, CallbackQuery):
        inline_id = callback.inline_message_id
        media = InputMediaAnimation(media=media_id)
        await callback.message.edit_media(media, inline_id)
        await callback.message.edit_caption(inline_id, **pattern)
    else:
        await callback.answer_animation(media_id, **pattern)


prefixes = ['soccer_', 'halloween_', 'common_', 'rare_',
            'epic_', 'legendary_', 'mythical_', 'divine_']


@router.callback_query(lambda c: any(c.data == p or c.data.startswith(p) for p in prefixes))
async def inventory(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    try:
        data = callback.data
        # Найти префикс, который присутствует в начале строки
        cb_rarity = next((p for p in prefixes if data.startswith(p)), None)
        user_data = await state.get_data()
        user_id_s = user_data.get('user_id')
        user_cb_id = int(data[len(cb_rarity):])  # удалить префикс
        if user_cb_id != user_id_s:
            await callback.answer("❖ ✖️ Это не ваш инвентарь", show_alert=True)
            return

        await state.update_data(rarity=cb_rarity)
        inline_id = callback.inline_message_id
        user_id = callback.from_user.id
        invent, universe = await get_inventory(user_id, cb_rarity.split("_", 1)[0])
        if invent == []:
            await callback.answer("❖ ✖️ У вас нет карт данной редкости", show_alert=True)
            return
        await state.update_data(character=invent[0])
        await state.update_data(universe=universe)
        await state.update_data(user_id=user_id)
        avatar = character_photo.get_stats(universe, invent[0], 'avatar')
        avatar_type = character_photo.get_stats(universe, invent[0], 'type')
        if avatar_type == 'photo':
            photo = InputMediaPhoto(media=avatar)
        else:
            photo = InputMediaAnimation(media=avatar)
        rarity = character_photo.get_stats(universe, invent[0], 'rarity')
        msg = f"❖ ✨ Редкость: {rarity}"
        if universe not in ['Allstars', 'Allstars(old)']:
            strength = character_photo.get_stats(universe, invent[0], 'arena')['strength']
            agility = character_photo.get_stats(universe, invent[0], 'arena')['agility']
            intelligence = character_photo.get_stats(universe, invent[0], 'arena')['intelligence']
            power = character_photo.get_stats(universe, invent[0], 'arena')['power']
            msg = (f"❖ ✨ Редкость: {rarity}"
                   f"\n❖ 🗺 Вселенная: {universe}"
                   f"\n\n   ✊🏻 Сила: {strength}"
                   f"\n   👣 Ловкость: {agility}"
                   f"\n   🧠 Интелект: {intelligence}"
                   f"\n   ⚜️ Мощь: {power}")
        await callback.message.edit_media(photo, inline_id)
        await callback.message.edit_caption(inline_id, caption=f"🎴 {invent[0]}"
                                                               # f"\n ── •✧✧• ───────"
                                                               f"<blockquote>{msg}</blockquote>"
                                                               f"\n──❀*̥˚──◌──◌──❀*̥˚"
                                                               f"\n❖ 🔖 1 из {len(invent)}",
                                            reply_markup=builders.pagination_keyboard_chat(universe, user_id, invent[0]))
    except KeyError:
        await callback.message.edit_caption(caption="❖ 〰️ В процессе обновления сессия была остановлена, вызовите "
                                            "🥡 Инвентарь еще раз", reply_markup=None)


act = ["prev_", "next_"]


@router.callback_query(builders.Pagination.filter(F.action.startswith("prev_") | F.action.startswith("next_")))
async def inventory(callback: CallbackQuery, callback_data: builders.Pagination, state: FSMContext):
    try:
        user_id = callback.from_user.id
        data = callback.data
        action = callback_data.action  # "prev_" или "next_"
        prefix = data.split("_", 1)[0]

        # Удаляем префикс и оставляем только user_id
        user_cb_id = int(data.split("_", 1)[1].split(":", 1)[0])

        user_data = await state.get_data()
        user_id_s = user_data.get('user_id')

        if user_cb_id != user_id_s:
            await callback.answer("❖ ✖️ Это не ваш инвентарь", show_alert=True)
            return
        inline_id = callback.inline_message_id
        page_num = int(callback_data.page)
        user_data = await state.get_data()
        invent, universe = await get_inventory(callback.from_user.id, user_data['rarity'])

        print(page_num)

        if prefix == "pagination:next":
            page_num = (page_num + 1) % len(invent)
        elif prefix == "pagination:prev":
            page_num = (page_num - 1) % len(invent)

        with suppress(TelegramBadRequest):
            await state.update_data(character=invent[page_num])
            await state.update_data(user_id=user_id)
            avatar = character_photo.get_stats(universe, invent[page_num], 'avatar')
            avatar_type = character_photo.get_stats(universe, invent[page_num], 'type')
            if avatar_type == 'photo':
                photo = InputMediaPhoto(media=avatar)
            else:
                photo = InputMediaAnimation(media=avatar)
            rarity = character_photo.get_stats(universe, invent[page_num], 'rarity')
            msg = f"❖ ✨ Редкость: {rarity}"
            if universe not in ['Allstars', 'Allstars(old)']:
                strength = character_photo.get_stats(universe, invent[page_num], 'arena')['strength']
                agility = character_photo.get_stats(universe, invent[page_num], 'arena')['agility']
                intelligence = character_photo.get_stats(universe, invent[page_num], 'arena')['intelligence']
                power = character_photo.get_stats(universe, invent[page_num], 'arena')['power']
                msg = (f"❖ ✨ Редкость: {rarity}"
                       f"\n❖ 🗺 Вселенная: {universe}"
                       f"\n\n   ✊🏻 Сила: {strength}"
                       f"\n   👣 Ловкость: {agility}"
                       f"\n   🧠 Интелект: {intelligence}"
                       f"\n   ⚜️ Мощь: {power}")

            await callback.message.edit_media(photo, inline_id)
            await callback.message.edit_caption(
                inline_id,
                caption=f"🎴 {invent[page_num]}"
                        # f"\n ── •✧✧• ───────"
                        f"<blockquote>{msg}</blockquote>"
                        f"\n──❀*̥˚──◌──◌──❀*̥˚"
                        f"\n❖ 🔖 {page_num + 1} из {len(invent)}",
                reply_markup=builders.pagination_keyboard_chat(universe=universe, character=invent[page_num],
                                                               user_id=user_id, page=page_num)
            )
        await callback.answer()
    except KeyError:
        await callback.message.edit_caption(caption="❖ 〰️ В процессе обновления сессия была остановлена, вызовите "
                                            "🥡 Инвентарь еще раз", reply_markup=None)


@router.callback_query(F.data.startswith("change_character_"))
async def change_ch(callback: CallbackQuery, state: FSMContext):
    try:
        user_id = callback.from_user.id
        user_cb_id = int(callback.data.replace("change_character_", ""))
        user_data = await state.get_data()
        user_id_s = user_data.get('user_id')
        if user_cb_id != user_id_s:
            await callback.answer("❖ ✖️ Это не ваш инвентарь", show_alert=True)
            return
        data = await state.get_data()
        await mongodb.change_char(user_id, data.get('universe'), data.get('character'))
        await callback.answer("🎴 Вы успешно изменили персонажа", show_alert=True)
    except KeyError:
        await callback.message.edit_caption(caption="❖ 〰️ В процессе обновления сессия была остановлена, вызовите "
                                            "🥡 Инвентарь еще раз", reply_markup=None)
