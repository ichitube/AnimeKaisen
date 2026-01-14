import asyncio

from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import Command, ChatMemberUpdatedFilter, JOIN_TRANSITION
from aiogram.types import CallbackQuery, Message, ChatMemberUpdated
from data import characters, character_photo
from data import mongodb
from filters.chat_type import ChatTypeFilter, CallbackChatTypeFilter
from keyboards.builders import inline_builder

from main import bot

router = Router()

duel_battle_data = {}

duel_user_data = {}

request_data = {}


@router.my_chat_member(ChatMemberUpdatedFilter(JOIN_TRANSITION))
async def on_bot_join(event: ChatMemberUpdated):
    chat_id = event.chat.id
    title = event.chat.title
    link = event.chat.username
    await mongodb.start_chat(chat_id, title, link, 'Bleach')
    await bot.send_message(chat_id, text=f"💮 Привет, я рад присоединиться к вашей группе {title}!")


def duel_text(character):
    text = (f"        {character.name}"
            f"\n\n❤️{character.health}"
            f" 🗡{character.attack}"
            f" 🛡{character.defense}"
            f"\n🌐{character.shield}"
            f"  🧪Мн: {character.mana}"
            f"  🪫Эн: {character.energy}"
            f"\n🩸К.ур: {character.crit_dmg}"
            f" 🩸К.шн: {character.crit_ch}"
            f"\n\n✊🏻Сл: {character.strength}"
            f" 👣Лв: {character.agility}"
            f" 🧠Ин: {character.intelligence}"
            f"\n\n❤️‍🔥Пассивки: {character.passive_names}")
    return text


async def duel_timeout(chat_id, user_id, r, mes):
    await asyncio.sleep(60)
    if not duel_user_data[chat_id][user_id][r]:
        del request_data[chat_id]
        duel_user_data[chat_id][user_id][r] = True  # Обновляем состояние
        account = await mongodb.get_user(user_id)

        if account["battle"]["battle"]["status"] == 2:
            rival = await mongodb.get_user(account["battle"]["battle"]["rid"])
            universe = rival['universe']
            character = rival['character'][rival['universe']]
            avatar = character_photo.get_stats(universe, character, 'avatar')
            avatar_type = character_photo.get_stats(universe, character, 'type')
            await mongodb.update_many(
                {"_id": {"$in": [account["_id"]]}},
                {"$set": {"battle.battle.status": 0, "battle.battle.rid": ""}}
            )
            await mongodb.update_many(
                {"_id": {"$in": [rival["_id"]]}},
                {"$set": {"battle.battle.status": 0, "battle.battle.rid": ""}}
            )
            if avatar_type == 'photo':
                await bot.send_photo(chat_id=chat_id, photo=avatar,
                                     caption=f"👑 {rival['character'][rival['universe']]} Победил")
            else:
                await bot.send_animation(chat_id=chat_id, animation=avatar,
                                         caption=f"👑 {rival['character'][rival['universe']]} Победил")
            await bot.edit_message_text(chat_id=chat_id, message_id=mes.message_id,
                                        text=f"✖️ Время вышло 🕘", reply_markup=None)

            await mongodb.insert_win(chat_id, rival["_id"], rival['name'])


async def request_timeout(chat_id, user_id, mes):
    await asyncio.sleep(30)
    if not request_data[chat_id][user_id]:
        del request_data[chat_id]
        await bot.edit_message_caption(chat_id=chat_id, message_id=mes.message_id,
                                       caption=f"✖️ Время истекло 🕘", reply_markup=None)


@router.message(ChatTypeFilter(chat_type=["group", "supergroup"]), Command("duel"))
async def duel(message: Message):
    user_id = message.from_user.id
    if not message.reply_to_message:
        return await message.reply("✖️ Нужно ответить на сообщение соперника!")
    rival_id = message.reply_to_message.from_user.id
    if user_id == rival_id:
        return await message.reply("✖️ Нельзя бросить вызов самому себе!")
    chat_id = message.chat.id
    account = await mongodb.get_user(user_id)
    rival = await mongodb.get_user(rival_id)
    if rival is None:
        await message.reply(text="✖️ Соперник не регистрирован!")
        return
    if account is None:
        await message.reply(text="✖️ Ты не регистрирован!")
        return

    if request_data.get(chat_id):
        return await message.reply("✖️ Идёт битва!")

    elif account['universe'] in ['Allstars', 'Allstars(old)']:
        return await message.reply("✖️ Ты не из вселенной где доступна арена!")

    elif rival['universe'] in ['Allstars', 'Allstars(old)']:
        return await message.reply("✖️ Соперник не из вселенной где доступна арена!")

    elif account["battle"]["battle"]["status"] == 1:
        await message.reply(text="💢 Вы уже находитесь в поиске соперника!")
        return

    elif account["battle"]["battle"]["status"] == 2:
        await message.reply(text="💢 Вы уже находитесь в битве!")
        return

    elif rival["battle"]["battle"]["status"] == 1:
        await message.reply(text="💢 Соперник находится в поиске соперника!")
        return

    elif rival["battle"]["battle"]["status"] == 2:
        await message.reply(text="💢 Соперник находится в битве!")
        return

    request_data[chat_id] = {}
    request_data[chat_id][user_id] = False
    request_data[chat_id][rival_id] = user_id

    message = await bot.send_animation(
        animation='CgACAgQAAx0CfstymgACDfJmEvqMok4D9NPyOY0bevepOE4LpQAC9gIAAu-0jFK0picm9zwgKzQE', chat_id=chat_id,
        caption=f"❖ {account['name']} бросил вызов {rival['name']}"
                f"\n⏳ Ждём ответа 30 секунд. . .",
        reply_markup=inline_builder(["🗡 Принять", "✖️ Отказать"], ["accept_duel", "refuse_duel"], row_width=[2, 2]))
    await request_timeout(chat_id, user_id, message)


@router.callback_query(F.data == "refuse_duel")
async def refuse_duel(callback: CallbackQuery):
    user_id = callback.from_user.id
    chat_id = callback.message.chat.id
    rival_id = False
    if user_id in request_data[chat_id]:
        rival_id = request_data[chat_id][user_id]
    if not rival_id:
        return await callback.answer("✖️ Не ваш вызов!", show_alert=True)
    del request_data[chat_id]
    await callback.message.edit_caption(caption=f"✖️ Вызов отказан", reply_markup=None)


@router.callback_query(F.data == "accept_duel")
async def start_duel(callback: CallbackQuery):
    user_id = callback.from_user.id
    chat_id = callback.message.chat.id
    rival_id = False
    if user_id in request_data[chat_id]:
        rival_id = request_data[chat_id][user_id]

    if not rival_id:
        return await callback.answer("✖️ Не ваш вызов!", show_alert=True)

    account = await mongodb.get_user(user_id)
    rival = await mongodb.get_user(rival_id)

    if account["battle"]["battle"]["status"] == 1:
        await callback.answer(text="💢 Вы уже находитесь в поиске соперника!", show_alert=True)
        return

    elif account["battle"]["battle"]["status"] == 2:
        await callback.answer(text="💢 Вы уже находитесь в битве!", show_alert=True)
        return

    elif rival["battle"]["battle"]["status"] == 1:
        await callback.answer(text="💢 Соперник находится в поиске соперника!", show_alert=True)
        return

    elif rival["battle"]["battle"]["status"] == 2:
        await callback.answer(text="💢 Соперник находится в битве!", show_alert=True)
        return

    await callback.message.edit_caption(caption=f"❖ Вызов принять"
                                                f"\n{account['name']} ⚔️ {rival['name']}", reply_markup=None)

    request_data[chat_id][rival_id] = True
    universe = account['universe']

    if account["battle"]["battle"]["status"] == 0:
        await mongodb.update_user(account["_id"], {"battle.battle.status": 2, "battle.battle.rid": rival["_id"]})
        await mongodb.update_user(rival["_id"], {"battle.battle.status": 2, "battle.battle.rid": account["_id"]})
        if rival is None:
            await bot.send_message(user_id, text="✖️ Соперник не регистрирован")
        else:
            ident = account["_id"]
            name = account["name"]
            character = account['character'][account['universe']]
            strength = character_photo.get_stats(universe, character, 'arena')['strength']
            agility = character_photo.get_stats(universe, character, 'arena')['agility']
            intelligence = character_photo.get_stats(universe, character, 'arena')['intelligence']
            ability = character_photo.get_stats(universe, character, 'arena')['ability']
            slave = None
            if account['inventory']['slaves']:
                slave = account['inventory']['slaves'][0]

            b_character = characters.Character(ident, name, character, strength, agility, intelligence, ability, 0,
                                               True, rival["_id"], slave, chat_id)

            duel_battle_data[chat_id] = {}
            duel_battle_data[chat_id][account["_id"]] = b_character

            r_ident = rival["_id"]
            r_name = rival["name"]
            r_universe = rival['universe']
            r_character = rival['character'][rival['universe']]
            r_strength = character_photo.get_stats(r_universe, r_character, 'arena')['strength']
            r_agility = character_photo.get_stats(r_universe, r_character, 'arena')['agility']
            r_intelligence = character_photo.get_stats(r_universe, r_character, 'arena')['intelligence']
            r_ability = character_photo.get_stats(r_universe, r_character, 'arena')['ability']
            r_slave = None
            if rival['inventory']['slaves']:
                r_slave = rival['inventory']['slaves'][0]

            rb_character = characters.Character(r_ident, r_name, r_character, r_strength, r_agility, r_intelligence,
                                                r_ability, 0, False, account["_id"], r_slave, chat_id)

            duel_battle_data[chat_id][rival["_id"]] = rb_character
            await bot.send_message(chat_id,
                                   text=f"\n✧•────────────────•✧"
                                        f"\n<blockquote expandable>{duel_text(rb_character)}"
                                        f"\n✧•────────────────•✧"
                                        f"\n{duel_text(b_character)}</blockquote>"
                                        f"\n✧•────────────────•✧")

            mes = await bot.send_message(chat_id, text=f"🔸 Ход {rb_character.name}:",
                                         reply_markup=inline_builder(r_ability, r_ability, row_width=[2, 2]),
                                         parse_mode=ParseMode.HTML)
            # Инициализируем состояние пользователя
            duel_user_data[chat_id] = {}
            duel_user_data[chat_id][rival["_id"]] = {b_character.b_round: False}
            duel_user_data[chat_id][user_id] = {rb_character.b_round: True}

            # Запускаем таймер
            await duel_timeout(chat_id, rival["_id"], b_character.b_round, mes)

    elif account["battle"]["battle"]["status"] == 1:
        await callback.answer(text="💢 Вы уже находитесь в поиске соперника!", show_alert=True)

    elif account["battle"]["battle"]["status"] == 2:
        await callback.answer(text="💢 Вы уже находитесь в битве!", show_alert=True)


@router.callback_query(CallbackChatTypeFilter(chat_type=["group", "supergroup"]), F.data.startswith("˹"))
async def duel_battle(callback: CallbackQuery):
    action = callback.data

    user_id = callback.from_user.id
    chat_id = callback.message.chat.id
    account = await mongodb.get_user(user_id)
    try:
        rival = await mongodb.get_user(account["battle"]["battle"]["rid"])

        chat_data = duel_battle_data.get(chat_id, {})
        character = chat_data.get(account["_id"])
        r_character = chat_data.get(character.rid)

        if account["battle"]["battle"]["status"] == 2:
            if user_id != character.ident:
                return await callback.answer("✖️ Не ваш ход!", show_alert=True)
            if character.b_turn:
                return await callback.answer("✖️ Не ваш ход!", show_alert=True)

            mana, energy = await characters.turn(character, bot, action, r_character, chat_id)

            if not mana:
                await callback.answer("✖️ Недостаточно маны 🧪", show_alert=True)
                return

            if not energy:
                await callback.answer("✖️ Недостаточно энергии 🪫", show_alert=True)
                return

            await bot.edit_message_reply_markup(chat_id=chat_id, message_id=callback.message.message_id)

            duel_battle_data[chat_id][character.ident] = character
            duel_battle_data[chat_id][r_character.ident] = r_character

            async def send_round_photo():
                if r_character.stun == 0:
                    duel_battle_data[chat_id][r_character.ident].b_turn = False
                    duel_battle_data[chat_id][character.ident].b_turn = True
                    if character.b_round != r_character.b_round:
                        await bot.send_message(chat_id,
                                               text=f".        ˗ˋˏ💮 Раунд {r_character.b_round}ˎˊ˗"
                                                    f"\n✧•────────────────•✧"
                                                    f"\n<blockquote expandable>{duel_text(r_character)}"
                                                    f"\n✧•────────────────•✧"
                                                    f"\n{duel_text(character)}</blockquote>"
                                                    f"\n✧•────────────────•✧")
                    mes = await bot.send_message(chat_id,
                                                 text=f"🔸 Ход {r_character.name}:",
                                                 reply_markup=inline_builder(r_character.ability, r_character.ability,
                                                                             row_width=[2, 2]),
                                                 parse_mode=ParseMode.HTML)
                    character.b_round += 1
                    duel_user_data[chat_id][user_id][character.b_round - 1] = True  # Обновляем состояние
                    # Инициализируем состояние пользователя
                    duel_user_data[chat_id][r_character.ident][r_character.b_round] = False
                    # Запускаем таймер
                    await duel_timeout(chat_id, r_character.ident, r_character.b_round, mes)
                else:
                    duel_battle_data[chat_id][character.rid].b_turn = True
                    duel_battle_data[chat_id][character.ident].b_turn = False
                    mes = await bot.send_message(chat_id,
                                                 text=f"🔸 Ход {character.name}:",
                                                 reply_markup=inline_builder(character.ability, character.ability,
                                                                             row_width=[2, 2]),
                                                 parse_mode=ParseMode.HTML)
                    character.b_round += 1
                    r_character.b_round += 1
                    duel_user_data[chat_id][r_character.ident][r_character.b_round - 1] = True  # Обновляем состояние
                    duel_user_data[chat_id][character.ident][character.b_round - 1] = True  # Обновляем состояние
                    # Инициализируем состояние пользователя
                    duel_user_data[chat_id][user_id][character.b_round] = False
                    # Запускаем таймер
                    await duel_timeout(chat_id, character.ident, character.b_round, mes)

            if character.health <= 0 and r_character.health <= 0:
                del request_data[chat_id]
                end_animation = 'CgACAgQAAx0CfstymgACDfFmFCIV11emoqYRlGWGZRTtrA46oQACAwMAAtwWDVNLf3iCB-QL9jQE'

                await bot.send_animation(chat_id=chat_id, animation=end_animation,
                                         caption=f"☠️ Ничья")

                await mongodb.update_many(
                    {"_id": {"$in": [account["_id"], character.rid]}},
                    {"$set": {"battle.battle.status": 0, "battle.battle.rid": ""}}
                )

            elif character.health <= 0:
                if character.b_round != r_character.b_round:
                    del request_data[chat_id]
                    universe = rival['universe']
                    character = rival['character'][rival['universe']]
                    avatar = character_photo.get_stats(universe, character, 'avatar')
                    avatar_type = character_photo.get_stats(universe, character, 'type')
                    if avatar_type == 'photo':
                        await bot.send_photo(chat_id=chat_id, photo=avatar,
                                             caption=f"👑 {r_character.name} Победил")
                    else:
                        await bot.send_animation(chat_id=chat_id, animation=avatar,
                                                 caption=f"👑 {r_character.name} Победил")

                    await mongodb.insert_win(rival["_id"], rival["_id"], r_character.p_name)

                    await mongodb.update_many(
                        {"_id": {"$in": [account["_id"], character.rid]}},
                        {"$set": {"battle.battle.status": 0, "battle.battle.rid": ""}}
                    )

                else:
                    await send_round_photo()

            elif r_character.health <= 0:
                if character.b_round != r_character.b_round:
                    del request_data[chat_id]
                    universe = account['universe']
                    character = account['character'][account['universe']]
                    avatar = character_photo.get_stats(universe, character, 'avatar')
                    avatar_type = character_photo.get_stats(universe, character, 'type')
                    if avatar_type == 'photo':
                        await bot.send_photo(chat_id=chat_id, photo=avatar,
                                             caption=f"👑 {character.name} Победил")
                    else:
                        await bot.send_animation(chat_id=user_id, animation=avatar,
                                                 caption=f"👑 {character.name} Победил")

                    await mongodb.update_many(
                        {"_id": {"$in": [account["_id"], character.rid]}},
                        {"$set": {"battle.battle.status": 0, "battle.battle.rid": ""}}
                    )

                    await mongodb.insert_win(rival["_id"], account["_id"], character.p_name)

                else:
                    await send_round_photo()
            else:
                await send_round_photo()
    except AttributeError as e:
        # Обработка ошибки AttributeError
        await callback.message.answer("❖ 🔂 Идёт разработка бота связи с чем битва была остановлена")
        await mongodb.update_many(
            {"_id": {"$in": [account["_id"]]}},
            {"$set": {"battle.battle.status": 0, "battle.battle.rid": ""}}
        )

        await bot.send_message(account["battle"]["battle"]["rid"],
                               "❖ 🔂 Идёт разработка бота связи с чем битва была остановлена")
        await mongodb.update_many(
            {"_id": {"$in": [account["battle"]["battle"]["rid"]]}},
            {"$set": {"battle.battle.status": 0, "battle.battle.rid": ""}}
        )
