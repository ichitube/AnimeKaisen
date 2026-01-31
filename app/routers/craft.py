import asyncio
import random

from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery, InputMediaAnimation, InputMediaPhoto
from app.data import mongodb, character_photo
from app.keyboards.builders import inline_builder, Ability
from app.routers.gacha import characters

router = Router()

craft = {'divine': 6000, 'mythical': 3500, 'legendary': 2000, 'epic': 200, 'rare': 50, 'common': 20}


@router.callback_query(F.data == "craft")
async def craft_menu(callback: CallbackQuery):
    inline_id = callback.inline_message_id
    user_id = callback.from_user.id
    account = await mongodb.get_user(user_id)

    fragments = account['account']['fragments']
    pattern = dict(
        caption=f"❖  🪄  <b>Крафт</b>"
                f"\n── •✧✧• ──────────"
                f"\n❃ 🧩 Стоимость крафта 🃏 карт 🂡: <blockquote>"
                # f"\n\n  🌠 Божественных карт 🂡: 6000 🧩"
                # f"\n\n  🌌 Мифических карт 🂡: 3500 🧩"
                f"\n  🌅 Легендарных карт 🂡: 2000 🧩"
                f"\n  🎆 Эпических карт 🂡: 200 🧩"
                f"\n  🎇 Редких карт 🂡: 50 🧩"
                f"\n  🌁 Обычных карт 🂡: 20 🧩</blockquote>"
                f"\n── •✧✧• ──────────"
                f"\n❖  У вас есть: <b>{fragments}</b> 🧩 осколков",
        reply_markup=inline_builder(
            ["🌅 Скрафтить", "🎆 Скрафтить", "🎇 Скрафтить", "🌁 Скрафтить", "🔙 Назад"],
            ["craft_legendary",
             "craft_epic", "craft_rare", "craft_common", "main_page"],
            row_width=[2]
            )  # "🌠 Скрафтить", "🌌 Скрафтить", "craft_divine", "craft_mythical",
    )

    media_id = "AgACAgIAAx0CfstymgACGthmw1rLV0WxGrbzW3MkaOQIfIaRXwACkuExG8b4GEq8rJRTnK_PFQEAAwIAA3kAAzUE"
    media = InputMediaPhoto(media=media_id)
    await callback.message.edit_media(media, inline_id)
    await callback.message.edit_caption(inline_id, **pattern)


@router.callback_query(F.data.in_(['craft_divine', 'craft_mythical', 'craft_legendary',
                                   'craft_epic', 'craft_rare', 'craft_common']))
async def craft_card(callback: CallbackQuery):
    user_id = callback.from_user.id
    account = await mongodb.get_user(user_id)
    fragments = account['account']['fragments']
    rarity_ch = callback.data.split('_')[1]
    universe = account['universe']
    if fragments < craft[rarity_ch]:
        await callback.answer(f"❖ ✖️ У вас недостаточно 🧩 осколков для 🪄 крафта", show_alert=True)
        return
    fragments -= craft[rarity_ch]
    character = random.choice(characters[universe][rarity_ch])  # Выбираем случайного персонажа из списка
    avatar = character_photo.get_stats(universe, character, 'avatar')
    avatar_type = character_photo.get_stats(universe, character, 'type')
    ch_universe = character_photo.get_stats(universe, character, 'universe')
    rarity = character_photo.get_stats(universe, character, 'rarity')
    strength = character_photo.get_stats(universe, character, 'arena')['strength']
    agility = character_photo.get_stats(universe, character, 'arena')['agility']
    intelligence = character_photo.get_stats(universe, character, 'arena')['intelligence']
    power = character_photo.get_stats(universe, character, 'arena')['power']

    media = InputMediaAnimation(media='CgACAgIAAx0CfstymgACBOll-IQ6qKzfUIdcMca9yMGq80GergACMEAAAkPekElgios1nCJOCjQE')

    await callback.message.edit_media(media, callback.inline_message_id)

    await asyncio.sleep(4)

    if avatar_type == 'photo':
        media = InputMediaPhoto(media=avatar, has_spoiler=True)
    else:
        media = InputMediaAnimation(media=avatar, has_spoiler=True)

    async def is_in_inventory():
        get_account = await mongodb.get_user(user_id)
        ch_characters = get_account['inventory'].get('characters')
        if characters:
            universe_characters = ch_characters.get(universe)
            if universe_characters:
                return character in universe_characters.get(rarity_ch, [])
        return False

    if await is_in_inventory():
        msg = (f"\n❖ ♻️ Вам попалась повторка"
               f"\n❖ 🧩 Осколки не потрачены")
    else:
        await mongodb.update_user(user_id, {"account.fragments": fragments})
        await mongodb.push(universe, rarity_ch, character, user_id)
        await mongodb.update_value(user_id, {'campaign.power': power})
        await mongodb.update_value(user_id, {'account.characters': 1})
        msg = (f"\n❖ ✨ Редкость: {rarity}"
               f"\n❖ 🗺 Вселенная: {ch_universe}"
               f"\n • ✊🏻 Сила: {strength}"
               f"\n • 👣 Ловкость: {agility}"
               f"\n • 🧠 Интелект: {intelligence}"
               f"\n • ⚜️ Мощь: {power}"
               f"\n──❀*̥˚──◌──◌──❀*̥˚────"
               f"\n + {power} ⚜️ Мощи")

    pattern = dict(
        caption=f"\n ── •✧✧• ──────────"
                f"\n  🃏  〢 {character} "
                f"\n ── •✧✧• ──────────"
                f"<blockquote>{msg}</blockquote>",
        reply_markup=inline_builder(["🎴 Навыки", " 🔙 "],
                                    [Ability(action="ability", universe=universe,
                                             character=character, back='craft'), "craft"],
                                    row_width=[1, 2]),
        parse_mode=ParseMode.HTML)
    await callback.message.edit_media(media, callback.inline_message_id)
    await callback.message.edit_caption(callback.inline_message_id, **pattern)
