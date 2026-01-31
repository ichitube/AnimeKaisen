import random
from datetime import datetime

from aiogram import Router, F, Bot
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from app.data import characters, character_photo
from app.data import mongodb
from app.routers.arena import arena
from app.filters.chat_type import ChatTypeFilter
from app.keyboards.builders import reply_builder, inline_builder, menu_card_button
from app.routers import gacha

router = Router()

battle_data = {}

user_data = {}

win_text = ("👑 Победа: 💀Соперник мертв"
            "\n<blockquote expandable>── •✧✧• ──────────"
            "\n  + 10🀄️ xp, "
            "\n  + 20💴 ¥</blockquote>")
lose_text = ("💀 Поражение"
             "\n<blockquote expandable>── •✧✧• ──────────"
             "\n  + 5🀄️ xp, "
             "\n  + 10💴 ¥</blockquote>")
draw_text = ("☠️ Ничья"
             "\n<blockquote expandable>── •✧✧• ──────────"
             "\n  + 8🀄️ xp, "
             "\n  + 15💴 ¥</blockquote>")
surrender_text = "🏴‍☠️ Поражение"
surrender_r_text = ("👑 Победа: 🏴‍☠️Соперник сдался"
                    "\n<blockquote expandable>── •✧✧• ──────────"
                    "\n  + 100🀄️ xp, "
                    "\n  + 200💴 ¥</blockquote>")
time_out_text = ("👑 Победа: ⏱️Время вышло"
                 "\n<blockquote expandable>── •✧✧• ──────────"
                 "\n  + 100🀄️ xp, "
                 "\n  + 200💴 ¥</blockquote>")


def account_text(character):
    text = (f"                 {character.name}"
            f"\n\n❤️{character.health}"
            f" 🗡{character.attack}"
            f" 🛡{character.defense}"
            f" 🧪{character.mana}"
            f" 🪫{character.energy}"
            f"\n🩸К.ур: {character.crit_dmg}"
            f" 🩸К.шн: {character.crit_ch}"
            f" 🌐Щит: {character.shield}"
            f"\n\n✊🏻Сила: {character.strength}"
            f" 👣Лов.: {character.agility}"
            f" 🧠Инт.: {character.intelligence}"
            f"\n\n❤️‍🔥Пассивки: {character.passive_names}")
    return text


win_animation = "CgACAgQAAx0CfstymgACDfFmFCIV11emoqYRlGWGZRTtrA46oQACAwMAAtwWDVNLf3iCB-QL9jQE"
lose_animation = "CgACAgQAAx0CfstymgACDfJmEvqMok4D9NPyOY0bevepOE4LpQAC9gIAAu-0jFK0picm9zwgKzQE"
draw_animation = "CgACAgQAAx0CfstymgACDfFmFCIV11emoqYRlGWGZRTtrA46oQACAwMAAtwWDVNLf3iCB-QL9jQE"


@router.message(ChatTypeFilter(chat_type=["private"]), Command("ai_battle"))
@router.callback_query(F.data == "ai_battle")
async def search_opponent(callback: CallbackQuery | Message, bot: Bot):
    user_id = callback.from_user.id
    account = await mongodb.get_user(user_id)
    universe = account['universe']

    # if account['universe'] in ['Allstars', 'Allstars(old)']:
    #     await callback.answer(
    #         text="💢 Пока не доступно в вашой вселеноой!",
    #         show_alert=True
    #     )
    #     return

    if isinstance(callback, CallbackQuery):
        await callback.message.delete()

    # Список вселенных без 'Allstars' и 'Allstars(old)'
    universes = [key for key in gacha.characters.keys() if key not in ['Allstars', 'Allstars(old)']]

    # Рандомно выбираем вселенную
    universee = random.choice(universes)

    # Получаем категории редкости для выбранной вселенной
    rarity_levels = list(gacha.characters[universee].keys())

    # Рандомно выбираем уровень редкости
    rarity = random.choice(rarity_levels)

    # Рандомно выбираем персонажа из выбранной категории редкости

    def rar(r):
        if r == "Божественная":
            return "divine"
        elif r == "Мифическая":
            return "mythical"
        elif r == "Легендарная":
            return "legendary"
        elif r == "Эпическая":
            return "epic"
        elif r == "Редкая":
            return "rare"
        elif r == "Обычная":
            return "common"

    if account["battle"]["battle"]["status"] == 0:

        await mongodb.update_user(user_id, {"battle.battle.status": 1})

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

        r_character = random.choice(gacha.characters[universee][rar(character_photo.get_stats(universe, character, 'rarity'))])
        rival = {"_id": user_id * 10,
                 "name": "AI ✨",
                 "universe": universee,
                 "character": {
                     universee: r_character},
                 "battle": {
                     "battle": {
                         "status": 0,
                         "turn": False,
                         "rid": "",
                         "round": 1
                        }
                    },
                 }

        b_character = characters.Character(ident, name, character, strength, agility, intelligence, ability, 1,
                                           False, ident * 10, slave, 0)

        battle_data[account["_id"]] = b_character

        r_ident = ident * 10
        r_name = rival["name"]
        r_universe = rival['universe']
        r_character = rival['character'][rival['universe']]
        r_avatar = character_photo.get_stats(r_universe, r_character, 'avatar')
        r_avatar_type = character_photo.get_stats(r_universe, r_character, 'type')
        r_rarity = character_photo.get_stats(r_universe, r_character, 'rarity')
        r_strength = character_photo.get_stats(r_universe, r_character, 'arena')['strength']
        r_agility = character_photo.get_stats(r_universe, r_character, 'arena')['agility']
        r_intelligence = character_photo.get_stats(r_universe, r_character, 'arena')['intelligence']
        r_ability = character_photo.get_stats(r_universe, r_character, 'arena')['ability']
        r_power = character_photo.get_stats(r_universe, r_character, 'arena')['power']
        r_slave = None

        rb_character = characters.Character(r_ident, r_name, r_character, r_strength, r_agility, r_intelligence,
                                            r_ability, 1, False, account["_id"], r_slave, 0)

        battle_data[rival["_id"]] = rb_character

        user_text = (f" ⚔️ Cоперник Найден! "
                     # f"\n── •✧✧• ──────────"
                     f"\n<blockquote expandable> 🪪  〢 {rival['name']} "
                     f"\n── •✧✧• ───────"
                     f"\n❖ ✨ Редкость: {r_rarity}"
                     f"\n❖ 🗺 Вселенная: {r_universe}"
                     f"\n\n   ✊🏻 Сила: {r_strength}"
                     f"\n   👣 Ловкость: {r_agility}"
                     f"\n   🧠 Интелект: {r_intelligence}"
                     f"\n   ⚜️ Мощь: {r_power}</blockquote>"
                     # f"\n── •✧✧• ──────────"
                     )

        await mongodb.update_user(account["_id"], {"battle.battle.status": 2, "battle.battle.rid": r_ident})

        if r_avatar_type == 'photo':
            await bot.send_photo(chat_id=user_id, photo=r_avatar, caption=user_text,
                                 reply_markup=reply_builder("🏴‍☠️ Сдаться"))
        else:
            await bot.send_animation(chat_id=user_id, animation=r_avatar, caption=user_text,
                                     reply_markup=reply_builder("🏴‍☠️ Сдаться"))

        await bot.send_message(account["_id"], text="⏳ Ход соперника")
        # Инициализируем состояние пользователя
        user_data[r_ident] = {rb_character.b_round: False}
        user_data[user_id] = {b_character.b_round: True}
        await ai(rb_character, bot, callback, account)

    elif account["battle"]["battle"]["status"] == 1:
        if isinstance(callback, CallbackQuery):
            await callback.answer(
                text="💢 Вы уже находитесь в поиске соперника!",
                show_alert=True
            )
        else:
            await callback.answer(text="💢 Вы уже находитесь в поиске соперника!")

    elif account["battle"]["battle"]["status"] == 2:
        if isinstance(callback, CallbackQuery):
            await callback.answer(
                text="💢 Вы уже находитесь в битве!",
                show_alert=True
            )
        else:
            await callback.answer(text="💢 Вы уже находитесь в битве!")


async def ai(character, bot, callback, account):
    try:
        r_character = battle_data.get(character.rid)

        while True:
            action = random.choice(character.ability)
            # action = '˹🗡Атака˼'
            mana, energy = await characters.turn(character, bot, action, r_character, 0, ai=True)

            if not mana:
                continue  # Выбираем новую способность

            if not energy:
                continue  # Выбираем новую способность

            # Если хватает и маны, и энергии, выходим из цикла
            break

        battle_data[character.ident] = character
        battle_data[r_character.ident] = r_character

        async def ai_send_round_photo():
            if r_character.stun == 0:
                character.b_round += 1
                battle_data[r_character.ident].b_turn = False
                battle_data[character.ident].b_turn = True
                mes = await bot.send_message(r_character.ident,
                                             text=f".               ˗ˋˏ💮 Раунд {r_character.b_round}ˎˊ˗"
                                                  # f"\n✧•───────────────────────•✧"
                                                  f"\n<blockquote expandable>{account_text(r_character)}</blockquote>"
                                                  # f"\n✧•──────────────•✧"
                                                  f"\n➖➖➖➖➖➖➖➖➖➖➖"
                                                  f"\n<blockquote expandable>{account_text(character)}</blockquote>"
                                                  # f"\n✧•───────────────────────•✧"
                                                  f"\n🔸 Ваш ход:",
                                             reply_markup=inline_builder(r_character.ability, r_character.ability,
                                                                         row_width=[2, 2]),
                                             parse_mode=ParseMode.HTML)
                user_data[character.ident][character.b_round - 1] = True  # Обновляем состояние
                # Инициализируем состояние пользователя
                user_data[r_character.ident][r_character.b_round] = False
                # Запускаем таймер
            else:
                character.b_round += 1
                r_character.b_round += 1
                battle_data[character.rid].b_turn = True
                battle_data[character.ident].b_turn = False
                await bot.send_message(r_character.ident,
                                       text=f".                    ˗ˋˏ💮 Раунд {r_character.b_round - 1}ˎˊ˗"
                                            # f"\n✧•───────────────────────•✧"
                                            f"\n<blockquote expandable>{account_text(r_character)}</blockquote>"
                                            # f"\n✧•──────────────•✧"
                                            f"\n➖➖➖➖➖➖➖➖➖➖➖"
                                            f"\n<blockquote expandable>{account_text(character)}</blockquote>"
                                            # f"\n✧•───────────────────────•✧"
                                            f"\n💫 Вы под действием оглушения",
                                       parse_mode=ParseMode.HTML)

                user_data[r_character.ident][r_character.b_round - 1] = True  # Обновляем состояние
                user_data[character.ident][character.b_round - 1] = True  # Обновляем состояние
                # Инициализируем состояние пользователя
                user_data[r_character.rid][character.b_round] = False
                # Запускаем таймер
                await bot.send_message(r_character.ident, "⏳ Ход соперника")
                await ai(character, bot, callback, account)

        if character.health <= 0 and r_character.health <= 0:
            await bot.send_animation(chat_id=r_character, animation=draw_animation,
                                     caption=draw_text, reply_markup=menu_card_button())

            await mongodb.update_many(
                {"_id": {"$in": [character.rid]}},
                {"$set": {"battle.battle.status": 0, "battle.battle.rid": ""}}
            )

            await mongodb.update_many(
                {"_id": {"$in": [character.rid]}},
                {"$inc": {"stats.exp": 8, "battle.stats.ties": 1, "account.money": 15}}
            )
            battle_data.pop(character.rid, None)
            battle_data.pop(character.rid * 10, None)
            user_data.pop(character.rid, None)
            user_data.pop(character.rid * 10, None)

            current_date = datetime.today().date()
            current_datetime = datetime.combine(current_date, datetime.time(datetime.now()))
            await mongodb.update_user(character.rid, {"tasks.last_arena_fight": current_datetime})

        elif character.health <= 0:
            if character.b_round != r_character.b_round:
                await bot.send_animation(chat_id=character.rid, animation=win_animation,
                                         caption=win_text, reply_markup=menu_card_button())

                await mongodb.update_many(
                    {"_id": {"$in": [character.rid]}},
                    {"$set": {"battle.battle.status": 0, "battle.battle.rid": ""}}
                )

                await mongodb.update_value(character.rid, {"stats.exp": 10})
                await mongodb.update_value(character.rid, {"account.money": 20})
                current_date = datetime.today().date()
                current_datetime = datetime.combine(current_date, datetime.time(datetime.now()))
                await mongodb.update_user(character.rid, {"tasks.last_arena_fight": current_datetime})
                battle_data.pop(character.rid, None)
                battle_data.pop(character.rid * 10, None)
                user_data.pop(character.rid, None)
                user_data.pop(character.rid * 10, None)
            else:
                await ai_send_round_photo()

        elif r_character.health <= 0:
            if character.b_round != r_character.b_round:
                await bot.send_animation(chat_id=character.rid, animation=lose_animation,
                                         caption=lose_text, reply_markup=menu_card_button())

                await mongodb.update_many(
                    {"_id": {"$in": [character.rid]}},
                    {"$set": {"battle.battle.status": 0, "battle.battle.rid": ""}}
                )

                await mongodb.update_value(character.rid, {"stats.exp": 5})
                await mongodb.update_value(character.rid, {"account.money": 10})
                current_date = datetime.today().date()
                current_datetime = datetime.combine(current_date, datetime.time(datetime.now()))
                await mongodb.update_user(character.rid, {"tasks.last_arena_fight": current_datetime})
                battle_data.pop(character.rid, None)
                battle_data.pop(character.rid * 10, None)
                user_data.pop(character.rid, None)
                user_data.pop(character.rid * 10, None)

            else:
                await ai_send_round_photo()
        else:
            await ai_send_round_photo()

    except AttributeError as e:
        # Обработка ошибки AttributeError
        await callback.message.edit_text("〰️ Бой был прерван", reply_markup=None)
        # await callback.message.answer("❖ 🔂 Идёт разработка бота связи с чем битва была остановлена",
        #                               reply_markup=menu_card_button())
        await mongodb.update_many(
            {"_id": {"$in": [account["_id"]]}},
            {"$set": {"battle.battle.status": 0, "battle.battle.rid": ""}}
        )
        await arena(callback, stop=1)
