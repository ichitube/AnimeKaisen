import asyncio
from datetime import datetime

from aiogram import Router, F, Bot
from contextlib import suppress
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message, InputMediaPhoto, InputMediaAnimation
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from app.data import mongodb, character_photo, card_characters
from app.filters.chat_type import ChatTypeFilter, CallbackChatTypeFilter
from app.keyboards.builders import inline_builder, Pagination, pagination_card, reply_builder, menu_card_button

# from caches.redis_ram import RedisDict

router = Router()

# battle_data = RedisDict("battle_data")
# user_data = RedisDict("user_data")

battle_data = {}
user_data = {}

win_animation = "CgACAgQAAx0CfstymgACDfFmFCIV11emoqYRlGWGZRTtrA46oQACAwMAAtwWDVNLf3iCB-QL9jQE"
lose_animation = "CgACAgQAAx0CfstymgACDfJmEvqMok4D9NPyOY0bevepOE4LpQAC9gIAAu-0jFK0picm9zwgKzQE"
draw_animation = "CgACAgQAAx0CfstymgACDfFmFCIV11emoqYRlGWGZRTtrA46oQACAwMAAtwWDVNLf3iCB-QL9jQE"


def end_text(user_id, rival_id, txt, sts):
    if rival_id == user_id * 10:
        rival_status = [battle_data[rival_id]["deck"]["d1"].status,
                        battle_data[rival_id]["deck"]["d2"].status,
                        battle_data[rival_id]["deck"]["d3"].status,
                        battle_data[rival_id]["deck"]["d4"].status,
                        battle_data[rival_id]["deck"]["d5"].status,
                        battle_data[rival_id]["deck"]["d6"].status]
    else:
        rival_text, rival_status, rival_cb, rival_round = account_text(rival_id)
    ttext, status, cb, sound = account_text(user_id)
    text = (f"{txt}"
            f"\n<blockquote expandable>── •✧✧• ──────────"
            f"\n ❖  🃏<b> Ваша колода:</b>"
            f"\n 「{status[0]} 「{status[1]}」「{status[2]}」"
            f"\n 「{status[3]}」「{status[4]}」「{status[5]}」"
            f"\n\n❖  🃏<b> Колода соперника:</b>"
            f"\n 「{rival_status[0]}」「{rival_status[1]}」「{rival_status[2]}」"
            f"\n 「{rival_status[3]}」「{rival_status[4]}」「{rival_status[5]}」"
            f"\n── •✧✧• ──────────</blockquote>"
            f"{sts}")
    return text


win_text = "👑 Победа: 💀Соперник мертв"
win_sts = (f"\n  + 100🀄️ xp"
           f"\n  + 200💴 ¥")

lose_text = "💀 Поражение"
lose_sts =("\n  + 55🀄️ xp"
           "\n  + 100💴 ¥")

draw_text = "☠️ Ничья"
draw_sts = ("\n  + 80🀄️ xp"
            "\n  + 150💴 ¥")

surrender_text = "🏴‍☠️ Поражение"
surrender_sts = " "

time_out_text = "👑 Победа: ⏱️Время вышло"
time_out_sts = ("\n  + 100🀄️ xp"
                "\n  + 200💴 ¥")

time_out_lose_text = "💀 Поражение: ⏱️Время вышло"
time_out_lose_sts = " "


def round_text(side, character):
    text = (f"     『{side}』"
            f"\n\n༺⟬{character.name}⟭༻"
            f"\n\n❤️{character.health}"
            f" 🗡{character.attack}"
            f" 🛡{character.defense}"
            f"\n\n✊🏻Сила: {character.strength}"
            f" 👣Лов.: {character.agility}"
            f" 🧠Инт.: {character.intelligence}")
    return text


def account_text(ident):
    nested_dict = user_data[ident]  # Получаем вложенный словарь
    key = list(nested_dict.keys())[0]

    d1 = battle_data[ident]["deck"]["d1"]
    d2 = battle_data[ident]["deck"]["d2"]
    d3 = battle_data[ident]["deck"]["d3"]
    d4 = battle_data[ident]["deck"]["d4"]
    d5 = battle_data[ident]["deck"]["d5"]
    d6 = battle_data[ident]["deck"]["d6"]
    text = (f"<b>˗ˋˏ🃏 Ваша колода:ˎˊ˗</b>"
            f"\n┅┅━─━┅┄ ⟛ ┄┅━─━┅┅"
            f"\n<blockquote>╭┈๋જ‌›<b>{d1.name}</b> ♥️{d1.health}"
            f"\n{d1.status}┄⚔️{d1.attack} 🛡️{d1.defense} ✊{d1.strength} 👣{d1.agility} 🧠{d1.intelligence}"
            f"\n╭┈๋જ‌›<b>{d2.name}</b> ♥️{d2.health} "
            f"\n{d2.status}┄⚔️{d2.attack} 🛡️{d2.defense} ✊{d2.strength} 👣{d2.agility} 🧠{d2.intelligence}"
            f"\n╭┈๋જ‌›<b>{d3.name}</b> ♥️{d3.health}"
            f"\n{d3.status}┄⚔️{d3.attack} 🛡️{d3.defense} ✊{d3.strength} 👣{d3.agility} 🧠{d3.intelligence}"
            f"\n╭┈๋જ‌›<b>{d4.name}</b> ♥️{d4.health}"
            f"\n{d4.status}┄⚔️{d4.attack} 🛡️{d4.defense} ✊{d4.strength} 👣{d4.agility} 🧠{d4.intelligence}"
            f"\n╭┈๋જ‌›<b>{d5.name}</b> ♥️{d5.health}"
            f"\n{d5.status}┄⚔️{d5.attack} 🛡️{d5.defense} ✊{d5.strength} 👣{d5.agility} 🧠{d5.intelligence}"
            f"\n╭┈๋જ‌›<b>{d6.name}</b> ♥️{d6.health}"
            f"\n{d6.status}┄⚔️{d6.attack} 🛡️{d6.defense} ✊{d6.strength} 👣{d6.agility} 🧠{d6.intelligence}"
            f"\n╰────────────╯ </blockquote expandable>")
    status = [d1.status, d2.status, d3.status, d4.status, d5.status, d6.status]
    user_cb = [f"{d1.cb}", f"{d2.cb}", f"{d3.cb}", f"{d4.cb}", f"{d5.cb}", f"{d6.cb}"]
    return text, status, user_cb, key


def deck_text(character, universe):
    strength = character_photo.get_stats(universe, character, 'arena')['strength']
    agility = character_photo.get_stats(universe, character, 'arena')['agility']
    intelligence = character_photo.get_stats(universe, character, 'arena')['intelligence']
    clas = character_photo.get_stats(universe, character, 'arena')['class']
    hp = strength * 75
    attack = strength * 5 + agility * 5 + intelligence * 5
    defense = (strength + agility + (intelligence // 2)) // 4

    text = (f"\n╭┈๋જ‌›<b>{character}</b> ♥️{hp}"
            f"\n🎴┄⚔️{attack} 🛡️{defense} ✊{strength} 👣{agility} 🧠{intelligence}"
        # f" • 🎴 {character} "
        #     f"\n ┗➤ • ♥️{hp} • ⚔️{attack} • 🛡️{defense}"
        #     f"\n     ┗➤ • ✊{strength} • 👣{agility} • 🧠{intelligence} ✧ {clas}"
            )
    return text


@router.callback_query(F.data == "deck")
async def choose_card(callback: CallbackQuery):
    user_id = callback.from_user.id
    account = await mongodb.get_user(user_id)
    universe = account['universe']
    if "deck" not in account:
        await mongodb.update_user(user_id, {"deck": {
            "d1": "empty",
            "d2": "empty",
            "d3": "empty",
            "d4": "empty",
            "d5": "empty",
            "d6": "empty"
        }})
        account = await mongodb.get_user(user_id)

    deck = account.get("deck", {})

    required_fields = {
        "d1": "empty",
        "d2": "empty",
        "d3": "empty",
        "d4": "empty",
        "d5": "empty",
        "d6": "empty"
    }

    for field, value in required_fields.items():
        if field not in deck:
            deck[field] = value

    await mongodb.update_user(user_id, {"deck": deck})
    account = await mongodb.get_user(user_id)

    deck_data = account["deck"]
    first = deck_data["d1"]
    second = deck_data["d2"]
    third = deck_data["d3"]
    fourth = deck_data["d4"]
    fifth = deck_data["d5"]
    sixth = deck_data["d6"]

    if first == "empty":
        f1_msg = "\n╭┈๋જ‌›<b><i> Пустое место </i></b> \n🎴┄ <i> empty </i>"
        f1_icon = "ℹ️"
    else:
        f1_msg = deck_text(first, universe)
        f1_icon = "✅"
    if second == "empty":
        f2_msg = "\n╭┈๋જ‌›<b><i> Пустое место </i></b> \n🎴┄ <i> empty </i>"
        f2_icon = "ℹ️"
    else:
        f2_msg = deck_text(second, universe)
        f2_icon = "✅"
    if third == "empty":
        f3_msg = "\n╭┈๋જ‌›<b><i> Пустое место </i></b> \n🎴┄ <i> empty </i>"
        f3_icon = "ℹ️"
    else:
        f3_msg = deck_text(third, universe)
        f3_icon = "✅"
    if fourth == "empty":
        f4_msg = "\n╭┈๋જ‌›<b><i> Пустое место </i></b> \n🎴┄ <i> empty </i>"
        f4_icon = "ℹ️"
    else:
        f4_msg = deck_text(fourth, universe)
        f4_icon = "✅"
    if fifth == "empty":
        f5_msg = "\n╭┈๋જ‌›<b><i> Пустое место </i></b> \n🎴┄ <i> empty </i>"
        f5_icon = "ℹ️"
    else:
        f5_msg = deck_text(fifth, universe)
        f5_icon = "✅"
    if sixth == "empty":
        f6_msg = "\n╭┈๋જ‌›<b><i> Пустое место </i></b> \n🎴┄ <i> empty </i>"
        f6_icon = "ℹ️"
    else:
        f6_msg = deck_text(sixth, universe)
        f6_icon = "✅"

    if "empty" in deck_data.values():
        msg = "❃ ℹ️ Есть пустые слоты в колоде"
    else:
        msg = "❃ ✅ Ваша колода готова к битве"

    pattern = dict(
        caption=f"❖  🃏<b> Ваша колода:</b>"
                f"\n┅┅━─━┅┄ ⟛ ┄┅━─━┅┅"
                f"<blockquote expandable>"
                f"{f1_msg}"
                f"{f2_msg}"
                f"{f3_msg}"
                f"{f4_msg}"
                f"{f5_msg}"
                f"{f6_msg}"
                f"\n╰──────────────────╯</blockquote>"
                f"\n{msg}",
        reply_markup=inline_builder(
            [f"{f1_icon}", f"{f2_icon}", f"{f3_icon}",
             f"{f4_icon}", f"{f5_icon}", f"{f6_icon}",
             "🔙 Назад"],
            ["d1", "d2", "d3",
             "d4", "d5", "d6",
             "battle_arena"],
            row_width=[3, 3, 1]
        )
    )

    media_id = InputMediaPhoto(media='AgACAgIAAx0CfstymgACPb1nWiwJUdQC-37DUnytEI6vUZd25wACMvQxG_bt0Epw17D9NcuZQAEAAwIAA3kAAzYE')

    inline_id = callback.inline_message_id
    await callback.message.edit_media(media_id, inline_id)
    await callback.message.edit_caption(inline_id, **pattern)


async def get_inventory(user_id, rarity):
    account = await mongodb.get_user(user_id)
    universe = account['universe']
    invent = account['inventory']['characters'][universe]
    if rarity == "d_divine":
        rarity = "divine"
    elif rarity == "d_mythical":
        rarity = "mythical"
    elif rarity == "d_legendary":
        rarity = "legendary"
    elif rarity == "d_epic":
        rarity = "epic"
    elif rarity == "d_rare":
        rarity = "rare"
    elif rarity == "d_common":
        rarity = "common"
    elif rarity == "d_halloween":
        rarity = "halloween"
    elif rarity == "d_soccer":
        rarity = "soccer"
    return invent[rarity], universe


@router.callback_query(F.data.in_(['d1', 'd2', 'd3', 'd4', 'd5', 'd6']))
async def inventory(callback: CallbackQuery | Message, state: FSMContext):
    await state.update_data(deck=callback.data)
    media_id = "CgACAgIAAxkBAAIVCmXMvbzs7hde-fvY9_4JCwU8W6HpAAKgOwACeyZoSuedvZenkxDNNAQ"
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
    buttons = [f"🌠 Божественные 🌟 {total_divine}", f"🌌 Мифические ⭐️ {total_mythical}", f"🌅 Легендарные ⭐️ {total_legendary}",
               f"🎆 Эпические ⭐️ {total_epic}", f"🎇 Редкие ⭐️ {total_rare}", f"🌁 Обычные ⭐️ {total_common}", "🔙 Назад"]
    callbacks = ["d_divine", "d_mythical", "d_legendary", "d_epic", "d_rare", "d_common", f"{callback.data}"]

    if universe == "Allstars":
        if "halloween" in account['inventory']['characters']['Allstars']:
            total_halloween = len(account['inventory']['characters']['Allstars'].get('halloween', {}))
            buttons.insert(0, f"👻 Halloween 🎃 {total_halloween}")
            callbacks.insert(0, "d_halloween")
        # if "soccer" not in account['inventory']['characters']['Allstars']:
        #     account = await mongodb.get_user(user_id)
        #     await mongodb.update_user(user_id, {"inventory.characters.Allstars.soccer": []})
        #     total_soccer = len(account['inventory']['items'].get('soccer', {}))
        #     buttons.insert(0, f"⚽️ Soccer {total_soccer}")
        #     callbacks.insert(0, "d_soccer")

    pattern = dict(caption=f"🥡 Инвентарь"
                           f"\n── •✧✧• ──────────"
                           f"\n<blockquote>❖ Здесь вы можете увидеть все ваши 🃏 карты "
                           f"и установить их в качестве 🎴 персонажа на слот в колоде."
                           f"\n❖ Выберите ✨ редкость карты, чтобы посмотреть.</blockquote>"
                           f"\n── •✧✧• ──────────"
                           f"\n❖ 🃏 Количество карт: {total_elements}",
                   reply_markup=inline_builder(
                       buttons,
                       callbacks, row_width=[1]))
    if isinstance(callback, CallbackQuery):
        inline_id = callback.inline_message_id
        media = InputMediaAnimation(media=media_id)
        await callback.message.edit_media(media, inline_id)
        await callback.message.edit_caption(inline_id, **pattern)
    else:
        await callback.answer_animation(animation=media_id, **pattern)


@router.callback_query(F.data.in_(['d_soccer', 'd_halloween', 'd_common', 'd_rare',
                                   'd_epic', 'd_legendary', 'd_mythical', 'd_divine']))
async def inventory(callback: CallbackQuery, state: FSMContext):
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
    msg = f"\n❖ ✨ Редкость: {rarity}"
    if universe not in ['Allstars', 'Allstars(old)']:
        strength = character_photo.get_stats(universe, invent[0], 'arena')['strength']
        agility = character_photo.get_stats(universe, invent[0], 'arena')['agility']
        intelligence = character_photo.get_stats(universe, invent[0], 'arena')['intelligence']
        power = character_photo.get_stats(universe, invent[0], 'arena')['power']
        msg = (f"\n❖ ✨ Редкость: {rarity}"
               f"\n❖ 🗺 Вселенная: {universe}"
               f"\n\n   ✊🏻 Сила: {strength}"
               f"\n   👣 Ловкость: {agility}"
               f"\n   🧠 Интелект: {intelligence}"
               f"\n   ⚜️ Мощь: {power}")
    await callback.message.edit_media(photo, inline_id)
    await callback.message.edit_caption(inline_id, caption=f"🎴 {invent[0]}"
                                                           f"\n ── •✧✧• ──────────"
                                                           f"<blockquote>{msg}</blockquote>"
                                                           f"\n──❀*̥˚──◌──◌──❀*̥˚────"
                                                           f"\n❖ 🔖 1 из {len(invent)}",
                                        reply_markup=pagination_card())


@router.callback_query(Pagination.filter(F.action.in_(["d_prev", "d_next"])))
async def inventory(callback: CallbackQuery, callback_data: Pagination, state: FSMContext):
    try:
        inline_id = callback.inline_message_id
        page_num = int(callback_data.page)
        user_data = await state.get_data()
        invent, universe = await get_inventory(callback.from_user.id, user_data['rarity'])

        if callback_data.action == "d_next":
            page_num = (page_num + 1) % len(invent)
        elif callback_data.action == "d_prev":
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
            msg = f"\n❖ ✨ Редкость: {rarity}"
            if universe not in ['Allstars', 'Allstars(old)']:
                strength = character_photo.get_stats(universe, invent[page_num], 'arena')['strength']
                agility = character_photo.get_stats(universe, invent[page_num], 'arena')['agility']
                intelligence = character_photo.get_stats(universe, invent[page_num], 'arena')['intelligence']
                power = character_photo.get_stats(universe, invent[page_num], 'arena')['power']
                msg = (f"\n❖ ✨ Редкость: {rarity}"
                       f"\n❖ 🗺 Вселенная: {universe}"
                       f"\n\n   ✊🏻 Сила: {strength}"
                       f"\n   👣 Ловкость: {agility}"
                       f"\n   🧠 Интелект: {intelligence}"
                       f"\n   ⚜️ Мощь: {power}")

            await callback.message.edit_media(photo, inline_id)
            await callback.message.edit_caption(
                inline_id,
                caption=f"🎴 {invent[page_num]}"
                        f"\n ── •✧✧• ──────────"
                        f"<blockquote>{msg}</blockquote>"
                        f"\n──❀*̥˚──◌──◌──❀*̥˚────"
                        f"\n❖ 🔖 {page_num + 1} из {len(invent)}",
                reply_markup=pagination_card(page=page_num)
            )
        await callback.answer()
    except KeyError:
        await callback.answer("❖ 🔂 Идёт разработка бота связи с чем сессия была остановлена, вызовите "
                              "🥡 Инвентарь еще раз", show_alert=True)


@router.callback_query(F.data == "d_choice_card")
async def change_ch(callback: CallbackQuery, state: FSMContext):
    try:
        user_id = callback.from_user.id
        account = await mongodb.get_user(user_id)
        deck = account["deck"]
        data = await state.get_data()
        if data.get('character') in deck.values():
            await callback.answer("❖ 🔂 Этот персонаж уже есть в колоде", show_alert=True)
            return
        else:
            await mongodb.update_user(user_id, {f"deck.{data.get('deck')}": data.get('character')})
            await callback.answer("🎴 Вы успешно выбрали персонажа", show_alert=True)
            await choose_card(callback)
    except KeyError:
        await callback.answer("❖ 🔂 Идёт разработка бота связи с чем сессия была остановлена, вызовите "
                              "🥡 Инвентарь еще раз", show_alert=True)


async def surrender_f(user_id, r, mes, bot):
    await asyncio.sleep(60)
    if not user_data[user_id][r]:
        user_data[user_id][r] = True  # Обновляем состояние
        account = await mongodb.get_user(user_id)

        if account["battle"]["battle"]["status"] == 4:
            rival = await mongodb.get_user(account["battle"]["battle"]["rid"])
            await bot.send_animation(chat_id=user_id, animation=lose_animation,
                                     caption=surrender_text, reply_markup=menu_card_button())
            current_date = datetime.today().date()
            current_datetime = datetime.combine(current_date, datetime.time(datetime.now()))
            await mongodb.update_user(account["battle"]["battle"]["rid"], {"tasks.last_arena_fight": current_datetime})
            await mongodb.update_value(account["_id"], {"battle.stats.loses": 1})
            await mongodb.update_value(account["battle"]["battle"]["rid"], {"battle.stats.wins": 1})
            await mongodb.update_value(account["battle"]["battle"]["rid"], {"stats.exp": 100})
            await mongodb.update_value(account["battle"]["battle"]["rid"], {"account.money": 200})
            await mongodb.update_many(
                {"_id": {"$in": [account["_id"]]}},
                {"$set": {"battle.battle.status": 0, "battle.battle.rid": ""}}
            )
            await mongodb.update_many(
                {"_id": {"$in": [rival["_id"]]}},
                {"$set": {"battle.battle.status": 0, "battle.battle.rid": ""}}
            )
            await bot.send_animation(chat_id=rival["_id"], animation=win_animation,
                                     caption=time_out_text, reply_markup=menu_card_button())
        await bot.edit_message_text(chat_id=user_id, message_id=mes.message_id,
                                    text=f"✖️ Время вышло ⏱️", reply_markup=None)


@router.callback_query(F.data == "card_opponent")
async def search_opponent(callback: CallbackQuery | Message, bot: Bot):
    user_id = callback.from_user.id
    account = await mongodb.get_user(user_id)
    universe = account['universe']

    if isinstance(callback, CallbackQuery):
        await callback.message.delete()

    if account["battle"]["battle"]["status"] == 0:
        rival = await mongodb.find_card_opponent()

        await mongodb.update_user(user_id, {"battle.battle.status": 3})

        if rival is None:
            await bot.send_animation(
                chat_id=user_id,
                animation="CgACAgIAAx0CfstymgACBaNly1ESV41gB1s-k4M3VITaGbHvHwACPj8AAlpyWEpUUFtvRlRcpjQE",
                caption=f"\n<blockquote expandable>💡 В разработке...</blockquote>"
                        f"\n── •✧✧• ──────────"
                        f"\n❖ 🔎 Поиск соперника . . . . .",
                reply_markup=reply_builder("✖️ Отмена"))
        else:
            ident = account["_id"]
            name = account["name"]
            u_deck = account["deck"]
            character = account['character'][account['universe']]
            avatar = character_photo.get_stats(universe, character, 'avatar')
            avatar_type = character_photo.get_stats(universe, character, 'type')
            slave = None
            if account['inventory']['slaves']:
                slave = account['inventory']['slaves'][0]

            u1_character = card_characters.CardCharacters(ident, name, universe, f"┋{u_deck["d1"]}┋", u_deck["d1"], slave, rival["_id"], "d1")
            u2_character = card_characters.CardCharacters(ident, name, universe, f"┋{u_deck["d2"]}┋", u_deck["d2"], slave, rival["_id"], "d2")
            u3_character = card_characters.CardCharacters(ident, name, universe, f"┋{u_deck["d3"]}┋", u_deck["d3"], slave, rival["_id"], "d3")
            u4_character = card_characters.CardCharacters(ident, name, universe, f"┋{u_deck["d4"]}┋", u_deck["d4"], slave, rival["_id"], "d4")
            u5_character = card_characters.CardCharacters(ident, name, universe, f"┋{u_deck["d5"]}┋", u_deck["d5"], slave, rival["_id"], "d5")
            u6_character = card_characters.CardCharacters(ident, name, universe, f"┋{u_deck["d6"]}┋", u_deck["d6"], slave, rival["_id"], "d6")

            r_ident = rival["_id"]
            r_universe = rival['universe']
            r_name = rival["name"]
            ru_deck = rival["deck"]
            r_character = rival['character'][rival['universe']]
            r_avatar = character_photo.get_stats(r_universe, r_character, 'avatar')
            r_avatar_type = character_photo.get_stats(r_universe, r_character, 'type')
            r_slave = None
            if rival['inventory']['slaves']:
                r_slave = rival['inventory']['slaves'][0]

            r1_character = card_characters.CardCharacters(r_ident, r_name, r_universe, f"┋{ru_deck["d1"]}┋", ru_deck["d1"], r_slave, ident, "d1")
            r2_character = card_characters.CardCharacters(r_ident, r_name, r_universe, f"┋{ru_deck["d2"]}┋", ru_deck["d2"], r_slave, ident, "d2")
            r3_character = card_characters.CardCharacters(r_ident, r_name, r_universe, f"┋{ru_deck["d3"]}┋", ru_deck["d3"], r_slave, ident, "d3")
            r4_character = card_characters.CardCharacters(r_ident, r_name, r_universe, f"┋{ru_deck["d4"]}┋", ru_deck["d4"], r_slave, ident, "d4")
            r5_character = card_characters.CardCharacters(r_ident, r_name, r_universe, f"┋{ru_deck["d5"]}┋", ru_deck["d5"], r_slave, ident, "d5")
            r6_character = card_characters.CardCharacters(r_ident, r_name, r_universe, f"┋{ru_deck["d6"]}┋", ru_deck["d6"], r_slave, ident, "d6")

            user_text = (f" ⚔️ Cоперник Найден! "
                         f"\n── •✧✧• ──────────"
                         f"\n 🪪  〢 {rival['name']} "
                         f"\n── •✧✧• ──────────"
                         f"\n<i>🀄️ Опыт: {rival['stats']['exp']} XP </i>")

            rival_text = (f"⚔️ Cоперник Найден! "
                          f"\n── •✧✧• ──────────"
                          f"\n 🪪  〢 {account['name']} "
                          f"\n── •✧✧• ──────────"
                          f"\n<i>🀄️ Опыт: {account['stats']['exp']} XP </i>")

            await mongodb.update_user(account["_id"], {"battle.battle.status": 4, "battle.battle.rid": rival["_id"]})
            await mongodb.update_user(rival["_id"], {"battle.battle.status": 4, "battle.battle.rid": account["_id"]})

            if r_avatar_type == 'photo':
                await bot.send_photo(chat_id=user_id, caption=user_text, photo=r_avatar,
                                     reply_markup=reply_builder("🏳️ Сдаться"))
            else:
                await bot.send_animation(chat_id=user_id, caption=user_text, animation=r_avatar,
                                         reply_markup=reply_builder("🏳️ Сдаться"))

            if avatar_type == 'photo':
                await bot.send_photo(chat_id=rival["_id"], caption=rival_text, photo=avatar,
                                     reply_markup=reply_builder("🏳️ Сдаться"))
            else:
                await bot.send_animation(chat_id=rival["_id"], caption=rival_text, animation=avatar,
                                         reply_markup=reply_builder("🏳️ Сдаться"))

            photo = 'AgACAgIAAx0CfstymgACPxhnpyOyMWhyizsk7AGoC0SRr47FdAACMewxG1EKQEkNebXgoiA-2wEAAwIAA3kAAzYE'

            text = (f"𝅄  ⭑  ꒰ 🪨 ✂️ 📃 ꒱  ⭑  𝅄"
                    "\n⟬Игра камень ножницы бумага⟭"
                    "\n\n × Вы: 『....』"
                    "\n × Соперник: 『....』"
                    "\n\n✧ ❔ Определяем кто будеть ходить первым")
            buttons = ["🤜", "✌️", "🫱"]
            cb = ["stone", "shears", "paper"]

            mes = await bot.send_photo(chat_id=user_id, photo=photo, caption=text,
                                       reply_markup=inline_builder(buttons, cb, row_width=[3]))

            mis = await bot.send_photo(chat_id=rival["_id"], photo=photo, caption=text,
                                       reply_markup=inline_builder(buttons, cb, row_width=[3]))

            battle_data[user_id] = {
                "rival": rival["_id"],
                "round": 0,
                "faze": 1,
                "turn": False,
                "current": None,
                "current_c": None,
                "status": None,
                "ms_id": mes.message_id,
                "is_first": False,
                "deck": {"d1": u1_character,
                         "d2": u2_character,
                         "d3": u3_character,
                         "d4": u4_character,
                         "d5": u5_character,
                         "d6": u6_character,
                         }
            }

            battle_data[r_ident] = {
                "rival": ident,
                "round": 0,
                "faze": 1,
                "turn": False,
                "current": None,
                "current_c": None,
                "status": None,
                "ms_id": mis.message_id,
                "is_first": False,
                "deck": {"d1": r1_character,
                         "d2": r2_character,
                         "d3": r3_character,
                         "d4": r4_character,
                         "d5": r5_character,
                         "d6": r6_character
                         }
            }
            user_data[user_id] = {battle_data[user_id]["round"]: True}
            user_data[rival["_id"]] = {battle_data[r_ident]["round"]: True}

            # await surrender_f(rival["_id"], battle_data[user_id]["round"], mis, bot)
            # await surrender_f(rival["_id"], battle_data[r_ident]["round"], mes, bot)

    elif account["battle"]["battle"]["status"] == 1 or account["battle"]["battle"]["status"] == 3:
        if isinstance(callback, CallbackQuery):
            await callback.answer(
                text="💢 Вы уже находитесь в поиске соперника!",
                show_alert=True
            )
        else:
            await callback.answer(text="💢 Вы уже находитесь в поиске соперника!")

    elif account["battle"]["battle"]["status"] == 2 or account["battle"]["battle"]["status"] == 4:
        if isinstance(callback, CallbackQuery):
            await callback.answer(
                text="💢 Вы уже находитесь в битве!",
                show_alert=True
            )
        else:
            await callback.answer(text="💢 Вы уже находитесь в битве!")


@router.callback_query(CallbackChatTypeFilter(chat_type=["private"]), F.data.in_(["stone", "shears", "paper"]))
async def start_battle(callback: CallbackQuery, bot: Bot):
    cb = callback.data
    player_id = callback.from_user.id
    rival_id = battle_data[player_id]["rival"]
    battle_data[player_id]['status'] = cb
    if cb == "stone":
        choice = "Камень 🤜"
    elif cb == "shears":
        choice = "Ножницы ✌️"
    else:
        choice = "Бумага 🫱"
    buttons = ["🤜", "✌️", "🫱"]
    cb = ["stone", "shears", "paper"]
    user_data[player_id][battle_data[player_id]["round"]] = True
    if battle_data[rival_id]["status"] is None:
        battle_data[player_id]["round"] += 1
        user_data[rival_id][battle_data[rival_id]["round"]] = False
        await bot.edit_message_caption(chat_id=player_id, message_id=battle_data[player_id]["ms_id"],
                                       caption=f"𝅄  ⭑  ꒰ 🪨 ✂️ 📃 ꒱  ⭑  𝅄"
                                               "\n⟬Игра камень ножницы бумага⟭"
                                               f"\n\n × Вы: 『{choice}』"
                                               "\n × Соперник: 『....』"
                                               "\n\n✧ ⏳ Ожидаем соперника...")
        mes = await bot.edit_message_caption(chat_id=rival_id, message_id=battle_data[rival_id]["ms_id"],
                                             caption=f"𝅄  ⭑  ꒰ 🪨 ✂️ 📃 ꒱  ⭑  𝅄"
                                                     "\n⟬Игра камень ножницы бумага⟭"
                                                     f"\n\n × Вы: 『....』"
                                                     f"\n × Соперник: 『<tg-spoiler>.......</tg-spoiler>』"
                                                     "\n\n✧ ❕ Соперник сделал выбор",
                                             reply_markup=inline_builder(buttons, cb, row_width=[3]))
        await surrender_f(rival_id, battle_data[rival_id]["round"], mes, bot)
    else:
        player_tx = None
        rival_tx = None
        if battle_data[player_id]["status"] == battle_data[rival_id]["status"]:
            player_tx = "💔 Ничья! Но вы выбрали после соперника, ходите первым 1️⃣"
            rival_tx = "🎉 Ничья! Но вы выбрали раньше соперника, ходите вторым 2️⃣"
            battle_data[player_id]["is_first"] = True
            battle_data[rival_id]["is_first"] = False
            battle_data[player_id]["status"] = None
            battle_data[rival_id]["status"] = None
        elif battle_data[player_id]["status"] == "stone" and battle_data[rival_id]["status"] == "shears":
            player_tx = "🎉 Вы победили! 2️⃣ ходите вторым"
            rival_tx = "💔 Вы проиграли! 1️⃣ ходите первым"
            battle_data[player_id]["is_first"] = False
            battle_data[rival_id]["is_first"] = True
            battle_data[player_id]["status"] = None
            battle_data[rival_id]["status"] = None
        elif battle_data[player_id]["status"] == "stone" and battle_data[rival_id]["status"] == "paper":
            player_tx = "💔 Вы проиграли! 1️⃣ ходите первым"
            rival_tx = "🎉 Вы победили! 2️⃣ ходите вторым"
            battle_data[player_id]["is_first"] = True
            battle_data[rival_id]["is_first"] = False
            battle_data[player_id]["status"] = None
            battle_data[rival_id]["status"] = None
        elif battle_data[player_id]["status"] == "shears" and battle_data[rival_id]["status"] == "stone":
            player_tx = "💔 Вы проиграли! 1️⃣ ходите первым"
            rival_tx = "🎉 Вы победили! 2️⃣ ходите вторым"
            battle_data[player_id]["is_first"] = True
            battle_data[rival_id]["is_first"] = False
            battle_data[player_id]["status"] = None
            battle_data[rival_id]["status"] = None
        elif battle_data[player_id]["status"] == "shears" and battle_data[rival_id]["status"] == "paper":
            player_tx = "🎉 Вы победили! 2️⃣ ходите вторым"
            rival_tx = "💔 Вы проиграли! 1️⃣ ходите первым"
            battle_data[player_id]["is_first"] = False
            battle_data[rival_id]["is_first"] = True
            battle_data[player_id]["status"] = None
            battle_data[rival_id]["status"] = None
        elif battle_data[player_id]["status"] == "paper" and battle_data[rival_id]["status"] == "stone":
            player_tx = "🎉 Вы победили! 2️⃣ ходите вторым"
            rival_tx = "💔 Вы проиграли! 1️⃣ ходите первым"
            battle_data[player_id]["is_first"] = False
            battle_data[rival_id]["is_first"] = True
            battle_data[player_id]["status"] = None
            battle_data[rival_id]["status"] = None
        elif battle_data[player_id]["status"] == "paper" and battle_data[rival_id]["status"] == "shears":
            player_tx = "💔 Вы проиграли! 1️⃣ ходите первым"
            rival_tx = "🎉 Вы победили! 2️⃣ ходите вторым"
            battle_data[player_id]["is_first"] = True
            battle_data[rival_id]["is_first"] = False
            battle_data[player_id]["status"] = None
            battle_data[rival_id]["status"] = None

        r_cb = battle_data[rival_id]["status"]
        if r_cb == "stone":
            r_choice = "Камень 🤜"
        elif r_cb == "shears":
            r_choice = "Ножницы ✌️"
        else:
            r_choice = "Бумагу 🫱"
        await bot.edit_message_caption(chat_id=player_id, message_id=battle_data[player_id]["ms_id"],
                                       caption=f"𝅄  ⭑  ꒰ 🪨 ✂️ 📃 ꒱  ⭑  𝅄"
                                               "\n⟬Игра камень ножницы бумага⟭"
                                               f"\n\n × Вы: 『{choice}』"
                                               f"\n × Соперник: 『{r_choice}』"
                                               f"\n\n✧ {player_tx}")
        await bot.edit_message_caption(chat_id=rival_id, message_id=battle_data[rival_id]["ms_id"],
                                       caption=f"𝅄  ⭑  ꒰ 🪨 ✂️ 📃 ꒱  ⭑  𝅄"
                                               "\n⟬Игра камень ножницы бумага⟭"
                                               f"\n\n × Вы: 『{r_choice}』"
                                               f"\n × Соперник: 『{choice}』"
                                               f"\n\n✧ {rival_tx}")
        await asyncio.sleep(1)

        if battle_data[player_id]["is_first"]:
            battle_data[player_id]["round"] += 1
            user_data[player_id][battle_data[player_id]["round"]] = False
            user_data[rival_id][battle_data[rival_id]["round"]] = True
            user_text, user_status, user_cb, u_round = account_text(player_id)
            mes = await bot.send_message(chat_id=player_id, text=f"{user_text}"
                                                                 f"\n🔸Ваш ход:",
                                         reply_markup=inline_builder(user_status, user_cb, row_width=[3, 3]))
            await surrender_f(player_id, battle_data[player_id]["round"], mes, bot)
        elif battle_data[rival_id]["is_first"]:
            user_data[player_id][battle_data[player_id]["round"]] = True
            battle_data[rival_id]["round"] += 1
            user_data[rival_id][battle_data[rival_id]["round"]] = False

            rival_text, rival_status, rival_cb, r_round = account_text(rival_id)
            mis = await bot.send_message(chat_id=rival_id, text=f"{rival_text}"
                                                                f"\n🔸Ваш ход:",
                                         reply_markup=inline_builder(rival_status, rival_cb, row_width=[3, 3]))
            await surrender_f(rival_id, battle_data[rival_id]["round"], mis, bot)


def calculate_damage(attacker, defender):
    base_damage = max(attacker.attack - defender.defense, 1)  # Минимальный урон 1

    # Проверяем классовое преимущество
    class_advantage = {
        "strength": "agility",
        "agility": "intelligence",
        "intelligence": "strength"
    }

    if class_advantage[attacker.clas] == defender.clas:
        base_damage = int(base_damage * 1.4)  # 1.4x урон

    return base_damage


async def win_lose(bot, char1, char2):
    user_id = char1.ident
    rival_id = char2.ident
    user_statuses = [
        battle_data[char1.ident]["deck"]["d1"].status,
        battle_data[char1.ident]["deck"]["d2"].status,
        battle_data[char1.ident]["deck"]["d3"].status,
        battle_data[char1.ident]["deck"]["d4"].status,
        battle_data[char1.ident]["deck"]["d5"].status,
        battle_data[char1.ident]["deck"]["d6"].status,
    ]

    rival_statuses = [
        battle_data[char2.ident]["deck"]["d1"].status,
        battle_data[char2.ident]["deck"]["d2"].status,
        battle_data[char2.ident]["deck"]["d3"].status,
        battle_data[char2.ident]["deck"]["d4"].status,
        battle_data[char2.ident]["deck"]["d5"].status,
        battle_data[char2.ident]["deck"]["d6"].status,
    ]

    all_statuses = user_statuses + rival_statuses

    if all("🎴" not in status for status in all_statuses):
        cont = False
        user_data[user_id][battle_data[user_id]["round"]] = True
        user_data[rival_id][battle_data[rival_id]["round"]] = True
        await bot.send_animation(chat_id=user_id, animation=draw_animation,
                                 caption=end_text(user_id, rival_id, draw_text, draw_sts), reply_markup=menu_card_button())

        await mongodb.update_value(char1.ident, {"battle.stats.ties": 1})
        await mongodb.update_value(char1.ident, {"stats.exp": 75})
        await mongodb.update_value(char1.ident, {"account.money": 150})
        await mongodb.update_value(char2.ident, {"battle.stats.ties": 1})
        await mongodb.update_value(char2.ident, {"stats.exp": 75})
        await mongodb.update_value(char2.ident, {"account.money": 150})
        await mongodb.update_many(
            {"_id": {"$in": [char1.ident]}},
            {"$set": {"battle.battle.status": 0, "battle.battle.rid": ""}}
        )
        battle_data[user_id]["round"] += 1
        await mongodb.update_many(
            {"_id": {"$in": [char2.ident]}},
            {"$set": {"battle.battle.status": 0, "battle.battle.rid": ""}}
        )
        await bot.send_animation(chat_id=char2.ident, animation=draw_animation,
                                 caption=end_text(rival_id, user_id, draw_text, draw_sts), reply_markup=menu_card_button())

    elif all("🎴" not in status for status in user_statuses):
        cont = False
        user_data[user_id][battle_data[user_id]["round"]] = True
        user_data[rival_id][battle_data[rival_id]["round"]] = True
        await bot.send_animation(chat_id=user_id, animation=lose_animation,
                                 caption=end_text(user_id, rival_id, lose_text, lose_sts), reply_markup=menu_card_button())

        await mongodb.update_value(char1.ident, {"battle.stats.loses": 1})
        await mongodb.update_value(char1.ident, {"stats.exp": 55})
        await mongodb.update_value(char1.ident, {"account.money": 100})
        await mongodb.update_value(char2.ident, {"battle.stats.wins": 1})
        await mongodb.update_value(char2.ident, {"stats.exp": 100})
        await mongodb.update_value(char2.ident, {"account.money": 200})
        current_date = datetime.today().date()
        current_datetime = datetime.combine(current_date, datetime.time(datetime.now()))
        await mongodb.update_user(char2.ident, {"tasks.last_arena_fight": current_datetime})
        await mongodb.update_many(
            {"_id": {"$in": [char1.ident]}},
            {"$set": {"battle.battle.status": 0, "battle.battle.rid": ""}}
        )
        await mongodb.update_many(
            {"_id": {"$in": [char2.ident]}},
            {"$set": {"battle.battle.status": 0, "battle.battle.rid": ""}}
        )
        await bot.send_animation(chat_id=char2.ident, animation=win_animation,
                                 caption=end_text(rival_id, user_id, win_text, win_sts), reply_markup=menu_card_button())
    elif all("🎴" not in status for status in rival_statuses):
        cont = False
        user_data[user_id][battle_data[user_id]["round"]] = True
        user_data[rival_id][battle_data[rival_id]["round"]] = True
        await bot.send_animation(chat_id=user_id, animation=win_animation,
                                 caption=end_text(user_id, rival_id, win_text, win_sts), reply_markup=menu_card_button())
        await mongodb.update_value(char1.ident, {"battle.stats.wins": 1})
        await mongodb.update_value(char1.ident, {"stats.exp": 100})
        await mongodb.update_value(char1.ident, {"account.money": 200})
        await mongodb.update_value(char2.ident, {"battle.stats.loses": 1})
        await mongodb.update_value(char2.ident, {"stats.exp": 55})
        await mongodb.update_value(char2.ident, {"account.money": 100})
        current_date = datetime.today().date()
        current_datetime = datetime.combine(current_date, datetime.time(datetime.now()))
        await mongodb.update_user(char2.ident, {"tasks.last_arena_fight": current_datetime})
        await mongodb.update_many(
            {"_id": {"$in": [char1.ident]}},
            {"$set": {"battle.battle.status": 0, "battle.battle.rid": ""}}
        )
        await mongodb.update_many(
            {"_id": {"$in": [char2.ident]}},
            {"$set": {"battle.battle.status": 0, "battle.battle.rid": ""}}
        )
        await bot.send_animation(chat_id=char2.ident, animation=lose_animation,
                                 caption=end_text(rival_id, user_id, lose_text, lose_sts), reply_markup=menu_card_button())
    else:
        cont = True

    return cont


async def battle(bot: Bot, user_id: int, rival_id: int, char1, char2, card1, card2):
    battle_log = []  # Лог битвы

    def format_msg():
        return (f"\n✧ • 🃜 ×    ×    ×    ×    ×    ×    ×    × 🃜 • ✧"
                f"\n<blockquote>"  # expandable
                f"{'\n'.join(battle_log)}"  # Показываем последние 6 ходов
                f"</blockquote>"
                f"\n✧ • 🃜 ×    ×    ×    ×    ×    ×    ×    × 🃜 • ✧")

    msg = await bot.send_message(user_id, format_msg())
    msg_rival = await bot.send_message(rival_id, format_msg())

    while char1.health > 0 and char2.health > 0:
        # Оба атакуют одновременно
        damage1 = calculate_damage(char1, char2)
        damage2 = calculate_damage(char2, char1)

        char2.health -= damage1
        char1.health -= damage2

        if char1.health < 0:
            char1.health = 0
        if char2.health < 0:
            char2.health = 0

        battle_log.append(f"\n{char1.name} нанес {damage1}⚔ урона \n{char2.name} нанес {damage2} урона")
        battle_log.append(f"\n{char1.name} {max(char1.health, 0)}❤️ {char2.name} {max(char2.health, 0)}❤️")

        # Проверка победителя
        if char1.health <= 0 and char2.health <= 0:
            battle_log.append("\n☠️ Бой окончен! Ничья!")
            battle_data[char1.ident]["deck"][card1].status = "☠️"
            battle_data[char2.ident]["deck"][card2].status = "☠️"
            battle_data[char2.ident]["current"] = None
            battle_data[char1.ident]["current"] = None
            user_data[user_id][battle_data[user_id]["round"]] = True
            user_data[rival_id][battle_data[rival_id]["round"]] = True

            battle_data[char1.ident]["round"] += 1
            battle_data[char2.ident]["round"] += 1

            new_text = format_msg()
            if msg.text != new_text:
                await bot.edit_message_text(chat_id=user_id, message_id=msg.message_id, text=format_msg())
            if msg_rival.text != new_text:
                await bot.edit_message_text(chat_id=rival_id, message_id=msg_rival.message_id, text=format_msg())

            cont = await win_lose(bot, char1, char2)

            if cont:
                photo = 'AgACAgIAAx0CfstymgACPxhnpyOyMWhyizsk7AGoC0SRr47FdAACMewxG1EKQEkNebXgoiA-2wEAAwIAA3kAAzYE'
                text = (f"𝅄  ⭑  ꒰ 🪨 ✂️ 📃 ꒱  ⭑  𝅄"
                        "\n⟬ Игра камень ножницы бумага ⟭"
                        "\n\n × Вы: 『....』"
                        "\n × Соперник: 『....』"
                        "\n\n✧ ❔ Определяем кто будеть ходить первым")
                buttons = ["🤜", "✌️", "🫱"]
                cb = ["stone", "shears", "paper"]

                mes = await bot.send_photo(chat_id=user_id, photo=photo, caption=text,
                                           reply_markup=inline_builder(buttons, cb, row_width=[3]))

                mis = await bot.send_photo(chat_id=rival_id, photo=photo, caption=text,
                                           reply_markup=inline_builder(buttons, cb, row_width=[3]))

                battle_data[user_id]["ms_id"] = mes.message_id
                battle_data[rival_id]["ms_id"] = mis.message_id
                user_data[user_id][battle_data[user_id]["round"]] = False
                user_data[rival_id][battle_data[rival_id]["round"]] = False

                await surrender_f(rival_id, battle_data[rival_id]["round"], mis, bot)
                await surrender_f(user_id, battle_data[user_id]["round"], mes, bot)

        elif char1.health <= 0:
            battle_log.append(f"\n🏆 {char2.name} побеждает в битве!")
            battle_data[char2.ident]["deck"][card2].status = "🎴"
            battle_data[char1.ident]["deck"][card1].status = "☠️"
            user_data[user_id][battle_data[user_id]["round"]] = True
            user_data[rival_id][battle_data[rival_id]["round"]] = True

            battle_data[char1.ident]["round"] += 1
            battle_data[char2.ident]["round"] += 1

            cont = await win_lose(bot, char1, char2)

            if cont:
                user_text, user_status, user_cb, rd = account_text(user_id)
                mg = await bot.send_message(chat_id=user_id, text=f"{user_text}"
                                                                  f"\n🔸Ваш ход:",
                                            reply_markup=inline_builder(user_status, user_cb, row_width=[3, 3]))
                await bot.send_message(chat_id=rival_id, text=f"⏳ Ждём ход соперника...")

                battle_data[char2.ident]["current"] = None
                battle_data[char1.ident]["current"] = None
                user_data[user_id][battle_data[user_id]["round"]] = False
                await surrender_f(user_id, battle_data[user_id]["round"], mg, bot)
                new_text = format_msg()
                if msg.text != new_text:
                    await bot.edit_message_text(chat_id=user_id, message_id=msg.message_id, text=format_msg())
                if msg_rival.text != new_text:
                    await bot.edit_message_text(chat_id=rival_id, message_id=msg_rival.message_id, text=format_msg())

        elif char2.health <= 0:
            battle_log.append(f"\n🏆 {char1.name} побеждает в битве!")
            battle_data[char1.ident]["deck"][card1].status = "🎴"
            battle_data[char2.ident]["deck"][card2].status = "☠️"
            user_data[user_id][battle_data[user_id]["round"]] = True
            user_data[rival_id][battle_data[rival_id]["round"]] = True

            battle_data[char1.ident]["round"] += 1
            battle_data[char2.ident]["round"] += 1

            cont = await win_lose(bot, char1, char2)
            if cont:
                rival_text, rival_status, rival_cb, r_round = account_text(rival_id)
                mes = await bot.send_message(chat_id=rival_id, text=f"{rival_text}"
                                                                    f"\n🔸Ваш ход:",
                                             reply_markup=inline_builder(rival_status, rival_cb, row_width=[3, 3]))
                await bot.send_message(chat_id=user_id, text=f"⏳ Ждём ход соперника...")

                battle_data[char2.ident]["current"] = None
                battle_data[char1.ident]["current"] = None
                user_data[rival_id][battle_data[rival_id]["round"]] = False
                await surrender_f(rival_id, battle_data[rival_id]["round"], mes, bot)
                new_text = format_msg()
                if msg.text != new_text:
                    await bot.edit_message_text(chat_id=user_id, message_id=msg.message_id, text=format_msg())
                if msg_rival.text != new_text:
                    await bot.edit_message_text(chat_id=rival_id, message_id=msg_rival.message_id, text=format_msg())

        # Обновляем сообщение с новыми ходами

        new_text = format_msg()
        if msg.text != new_text:
            await bot.edit_message_text(chat_id=user_id, message_id=msg.message_id, text=format_msg())
        if msg_rival.text != new_text:
            await bot.edit_message_text(chat_id=rival_id, message_id=msg_rival.message_id, text=format_msg())
        await asyncio.sleep(1.5)  # Задержка перед следующим раундом

    new_text = format_msg()
    if msg.text != new_text:
        await bot.edit_message_text(chat_id=user_id, message_id=msg.message_id, text=format_msg())
    if msg_rival.text != new_text:
        await bot.edit_message_text(chat_id=rival_id, message_id=msg_rival.message_id, text=format_msg())


@router.callback_query(CallbackChatTypeFilter(chat_type=["private"]), F.data.startswith("┋"))
async def start_battle(callback: CallbackQuery, bot: Bot):
    cb = callback.data
    player_id = callback.from_user.id
    rival_id = battle_data[player_id]["rival"]

    char = cb.replace("┋", "")
    card, char_object = None, None
    for card_key, card_obj in battle_data[player_id]["deck"].items():
        if getattr(card_obj, "name", None) == char:  # Проверяем имя персонажа
            card, char_object = card_key, card_obj
            break  # Прерываем, если нашли

    if card and battle_data[player_id]["deck"][card].status == "☠️":
        await callback.answer("❖ ☠️ Этот персонаж уже проиграл, используйте другую 🃜 карту", show_alert=True)
        return

    user_data[player_id][battle_data[player_id]["round"]] = True
    battle_data[player_id]["round"] += 1

    battle_data[player_id]["current"] = char_object
    battle_data[player_id]["current_c"] = card

    user_text = round_text("Вы", char_object)
    rival_text = round_text("Соперник", char_object)

    avatar = character_photo.get_stats(char_object.universe, char_object.name, 'avatar')
    avatar_type = character_photo.get_stats(char_object.universe, char_object.name, 'type')

    await callback.message.delete()

    if avatar_type == 'photo':
        await bot.send_photo(photo=avatar, chat_id=player_id, caption=user_text)
    else:
        await bot.send_animation(animation=avatar, chat_id=player_id, caption=user_text)

    if avatar_type == 'photo':
        await bot.send_photo(photo=avatar, chat_id=rival_id, caption=rival_text)
    else:
        await bot.send_animation(animation=avatar, chat_id=rival_id, caption=rival_text)

    if not battle_data[rival_id]["current"]:
        await asyncio.sleep(1)
        rival_text, rival_status, rival_cb, r_round = account_text(rival_id)
        mes = await bot.send_message(chat_id=rival_id, text=f"{rival_text}"
                                                            f"\n🔸Ваш ход:",
                                     reply_markup=inline_builder(rival_status, rival_cb, row_width=[3, 3]))
        await bot.send_message(chat_id=player_id, text=f"⏳ Ждём ход соперника...")

        battle_data[rival_id]["round"] += 1
        user_data[rival_id][battle_data[rival_id]["round"]] = False
        await surrender_f(rival_id, battle_data[rival_id]["round"], mes, bot)
    else:
        user_char = battle_data[player_id]["current"]
        rival_char = battle_data[rival_id]["current"]
        user_card = battle_data[player_id]["current_c"]
        rival_card = battle_data[rival_id]["current_c"]
        await battle(bot, player_id, rival_id, user_char, rival_char, user_card, rival_card)


@router.message(ChatTypeFilter(chat_type=["private"]), Command("card_surrender"))
@router.message(F.text == "🏳️ Сдаться")
async def surrender(message: Message, bot: Bot):
    user_id = message.from_user.id
    account = await mongodb.get_user(user_id)
    rival = None
    if account["battle"]["battle"]["status"] == 4:
        if account["battle"]["battle"]["rid"] != user_id * 10:
            await bot.send_message(chat_id=user_id, text=f"{account['battle']['battle']['rid']}")
            rival = await mongodb.get_user(account["battle"]["battle"]["rid"])
        await bot.send_animation(chat_id=user_id, animation=lose_animation,
                                 caption="💀 Поражение "
                                         "\n── •✧✧• ──────────"
                                         "\n  + 55🀄️ xp "
                                         "\n  + 100💴 ¥", reply_markup=menu_card_button())

        await mongodb.update_value(account["_id"], {"battle.stats.loses": 1})
        if account["battle"]["battle"]["rid"] != user_id * 10:
            await mongodb.update_value(account["battle"]["battle"]["rid"], {"battle.stats.wins": 1})
            await mongodb.update_value(account["battle"]["battle"]["rid"], {"stats.exp": 100})
            await mongodb.update_value(account["battle"]["battle"]["rid"], {"account.money": 200})
            current_date = datetime.today().date()
            current_datetime = datetime.combine(current_date, datetime.time(datetime.now()))
            await mongodb.update_user(account["battle"]["battle"]["rid"], {"tasks.last_arena_fight": current_datetime})
        await mongodb.update_many(
            {"_id": {"$in": [account["_id"]]}},
            {"$set": {"battle.battle.status": 0, "battle.battle.rid": ""}}
        )
        if account["battle"]["battle"]["rid"] != user_id * 10:
            await mongodb.update_many(
                {"_id": {"$in": [rival["_id"]]}},
                {"$set": {"battle.battle.status": 0, "battle.battle.rid": ""}}
            )
            await bot.send_animation(chat_id=rival["_id"], animation=win_animation,
                                     caption="👑 Победа: 🏳️ Соперник сдался"
                                             "\n── •✧✧• ──────────"
                                             "\n  + 100🀄️ xp "
                                             "\n  + 200💴 ¥", reply_markup=menu_card_button())
