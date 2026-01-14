import random
import asyncio
from datetime import datetime

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from routers import gacha
from data import mongodb, character_photo, card_characters
from filters.chat_type import ChatTypeFilter, CallbackChatTypeFilter
from keyboards.builders import inline_builder, reply_builder, menu_button
from routers.card_battle import battle_data, user_data
from aiogram.exceptions import TelegramBadRequest

# from caches.redis_ram import RedisDict

router = Router()

# battle_data = RedisDict("battle_data")
# user_data = RedisDict("user_data")

# battle_data = {}
# user_data = {}

win_animation = "CgACAgQAAx0CfstymgACDfFmFCIV11emoqYRlGWGZRTtrA46oQACAwMAAtwWDVNLf3iCB-QL9jQE"
lose_animation = "CgACAgQAAx0CfstymgACDfJmEvqMok4D9NPyOY0bevepOE4LpQAC9gIAAu-0jFK0picm9zwgKzQE"
draw_animation = "CgACAgQAAx0CfstymgACDfFmFCIV11emoqYRlGWGZRTtrA46oQACAwMAAtwWDVNLf3iCB-QL9jQE"


def end_text(user_id, rival_id, txt, sts):
    ttext, status, cb, sound = account_text(user_id)
    rival_text, rival_status, rival_cb, rival_round = account_text(rival_id)
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
win_sts = (f"\n  + 10🀄️ xp"
           f"\n  + 20💴 ¥")

lose_text = "💀 Поражение"
lose_sts =("\n  + 5🀄️ xp"
           "\n  + 10💴 ¥")

draw_text = "☠️ Ничья"
draw_sts = ("\n  + 8🀄️ xp"
            "\n  + 15💴 ¥")

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
    text = (f".              <b>˗ˋˏ🃏 Ваша колода:ˎˊ˗</b>"
            f"\n✧•───────────────────────•✧"
            f"\n<blockquote expandable> • {d1.status}  {d1.name}"
            f"\n ┗➤ ┏➤ • ♥️{d1.health} • ⚔️{d1.attack} • 🛡️{d1.defense}"
            f"\n     ┗➤ • ✊{d1.strength} • 👣{d1.agility} • 🧠{d1.intelligence} ✧ {d1.clas}"
            f"\n\n • {d2.status}  {d2.name} "
            f"\n ┗➤ ┏➤ • ♥️{d2.health} • ⚔️{d2.attack} • 🛡️{d2.defense}"
            f"\n     ┗➤ • ✊{d2.strength} • 👣{d2.agility} • 🧠{d2.intelligence} ✧ {d2.clas}"
            f"\n\n • {d3.status}  {d3.name}"
            f"\n ┗➤ ┏➤ • ♥️{d3.health} • ⚔️{d3.attack} • 🛡️{d3.defense}"
            f"\n     ┗➤ • ✊{d3.strength} • 👣{d3.agility} • 🧠{d3.intelligence} ✧ {d3.clas}"
            f"\n\n • {d4.status}  {d4.name}"
            f"\n ┗➤ ┏➤ • ♥️{d4.health} • ⚔️{d4.attack} • 🛡️{d4.defense}"
            f"\n     ┗➤ • ✊{d4.strength} • 👣{d4.agility} • 🧠{d4.intelligence} ✧ {d4.clas}"
            f"\n\n • {d5.status}  {d5.name}"
            f"\n ┗➤ ┏➤ • ♥️{d5.health} • ⚔️{d5.attack} • 🛡️{d5.defense}"
            f"\n     ┗➤ • ✊{d5.strength} • 👣{d5.agility} • 🧠{d5.intelligence} ✧ {d5.clas}"
            f"\n\n • {d6.status}  {d6.name}"
            f"\n ┗➤ ┏➤ • ♥️{d6.health} • ⚔️{d6.attack} • 🛡️{d6.defense}"
            f"\n     ┗➤ • ✊{d6.strength} • 👣{d6.agility} • 🧠{d6.intelligence} ✧ {d6.clas}</blockquote>"
            f"\n✧•───────────────────────•✧")
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

    text = (f" • 🎴 {character} "
            f"\n ┗➤ • ♥️{hp} • ⚔️{attack} • 🛡️{defense}"
            f"\n     ┗➤ • ✊{strength} • 👣{agility} • 🧠{intelligence} ✧ {clas}")
    return text


@router.callback_query(F.data == "ai_card_opponent")
async def ai_opponent(callback: CallbackQuery | Message, bot: Bot):
    user_id = callback.from_user.id
    account = await mongodb.get_user(user_id)
    universe = account['universe']

    if isinstance(callback, CallbackQuery):
        await callback.message.delete()

    if account["battle"]["battle"]["status"] == 0:
        rival = user_id * 10

        await mongodb.update_user(user_id, {"battle.battle.status": 3})
        ident = account["_id"]
        name = account["name"]
        u_deck = account["deck"]
        character = account['character'][account['universe']]
        avatar = character_photo.get_stats(universe, character, 'avatar')
        avatar_type = character_photo.get_stats(universe, character, 'type')
        slave = None
        if account['inventory']['slaves']:
            slave = account['inventory']['slaves'][0]

        u1_character = card_characters.CardCharacters(ident, name, universe, f"×{u_deck["d1"]}×", u_deck["d1"], slave, ident * 10, "d1")
        u2_character = card_characters.CardCharacters(ident, name, universe, f"×{u_deck["d2"]}×", u_deck["d2"], slave, ident * 10, "d2")
        u3_character = card_characters.CardCharacters(ident, name, universe, f"×{u_deck["d3"]}×", u_deck["d3"], slave, ident * 10, "d3")
        u4_character = card_characters.CardCharacters(ident, name, universe, f"×{u_deck["d4"]}×", u_deck["d4"], slave, ident * 10, "d4")
        u5_character = card_characters.CardCharacters(ident, name, universe, f"×{u_deck["d5"]}×", u_deck["d5"], slave, ident * 10, "d5")
        u6_character = card_characters.CardCharacters(ident, name, universe, f"×{u_deck["d6"]}×", u_deck["d6"], slave, ident * 10, "d6")

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
            elif r == "halloween":
                return "halloween"

        r_ident = user_id * 10
        r_universe = 'Allstars'
        r_name = "AI"
        ru_deck = {
            "d1": random.choice(gacha.characters['Allstars'][rar(character_photo.get_stats(universe, u_deck["d1"], 'rarity'))]),
            "d2": random.choice(gacha.characters['Allstars'][rar(character_photo.get_stats(universe, u_deck["d2"], 'rarity'))]),
            "d3": random.choice(gacha.characters['Allstars'][rar(character_photo.get_stats(universe, u_deck["d3"], 'rarity'))]),
            "d4": random.choice(gacha.characters['Allstars'][rar(character_photo.get_stats(universe, u_deck["d4"], 'rarity'))]),
            "d5": random.choice(gacha.characters['Allstars'][rar(character_photo.get_stats(universe, u_deck["d5"], 'rarity'))]),
            "d6": random.choice(gacha.characters['Allstars'][rar(character_photo.get_stats(universe, u_deck["d6"], 'rarity'))])
        }
        r_avatar = character_photo.get_stats(r_universe, ru_deck["d1"], 'avatar')
        r_avatar_type = character_photo.get_stats(r_universe, ru_deck["d1"], 'type')
        r_slave = None
        # if rival['inventory']['slaves']:
        #     r_slave = rival['inventory']['slaves'][0]

        r1_character = card_characters.CardCharacters(r_ident, r_name, r_universe, f"×{ru_deck["d1"]}×", ru_deck["d1"], r_slave, ident, "d1")
        r2_character = card_characters.CardCharacters(r_ident, r_name, r_universe, f"×{ru_deck["d2"]}×", ru_deck["d2"], r_slave, ident, "d2")
        r3_character = card_characters.CardCharacters(r_ident, r_name, r_universe, f"×{ru_deck["d3"]}×", ru_deck["d3"], r_slave, ident, "d3")
        r4_character = card_characters.CardCharacters(r_ident, r_name, r_universe, f"×{ru_deck["d4"]}×", ru_deck["d4"], r_slave, ident, "d4")
        r5_character = card_characters.CardCharacters(r_ident, r_name, r_universe, f"×{ru_deck["d5"]}×", ru_deck["d5"], r_slave, ident, "d5")
        r6_character = card_characters.CardCharacters(r_ident, r_name, r_universe, f"×{ru_deck["d6"]}×", ru_deck["d6"], r_slave, ident, "d6")

        user_text = (f" ⚔️ Cоперник Найден! "
                     f"\n── •✧✧• ──────────"
                     f"\n 🪪  〢 {r_name} "
                     f"\n── •✧✧• ──────────"
                     f"\n<i>🀄️ Опыт: ? XP </i>")

        rival_text = (f"⚔️ Cоперник Найден! "
                      f"\n── •✧✧• ──────────"
                      f"\n 🪪  〢 {account['name']} "
                      f"\n── •✧✧• ──────────"
                      f"\n<i>🀄️ Опыт: {account['stats']['exp']} XP </i>")

        await mongodb.update_user(account["_id"], {"battle.battle.status": 4, "battle.battle.rid": r_ident})

        if r_avatar_type == 'photo':
            await bot.send_photo(chat_id=user_id, caption=user_text, photo=r_avatar,
                                 reply_markup=reply_builder("🏳️ Сдаться"))
        else:
            await bot.send_animation(chat_id=user_id, caption=user_text, animation=r_avatar,
                                     reply_markup=reply_builder("🏳️ Сдаться"))

        photo = 'AgACAgIAAx0CfstymgACPxhnpyOyMWhyizsk7AGoC0SRr47FdAACMewxG1EKQEkNebXgoiA-2wEAAwIAA3kAAzYE'

        text = (f"𝅄  ⭑  ꒰ 🪨 ✂️ 📃 ꒱  ⭑  𝅄"
                "\n⟬Игра камень ножницы бумага⟭"
                "\n\n × Вы: 『....』"
                "\n × Соперник: 『<tg-spoiler>.......</tg-spoiler>』"
                "\n\n✧ ❔ Определяем кто будеть ходить первым")
        buttons = ["🤜", "✌️", "🫱"]
        cb = ["stone_ai", "shears_ai", "paper_ai"]

        mes = await bot.send_photo(chat_id=user_id, photo=photo, caption=text,
                                   reply_markup=inline_builder(buttons, cb, row_width=[3]))

        battle_data[user_id] = {
            "rival": user_id * 10,
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
            "ms_id": None,
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
        user_data[r_ident] = {battle_data[r_ident]["round"]: True}

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


@router.callback_query(CallbackChatTypeFilter(chat_type=["private"]), F.data.in_(["stone_ai", "shears_ai", "paper_ai"]))
async def start_battle(callback: CallbackQuery, bot: Bot):
    cb = callback.data
    player_id = callback.from_user.id
    rival_id = battle_data[player_id]["rival"]
    battle_data[player_id]['status'] = cb
    if cb == "stone_ai":
        choice = "Камень 🤜"
    elif cb == "shears_ai":
        choice = "Ножницы ✌️"
    elif cb == "paper_ai":
        choice = "Бумагу 🫱"
    stt = ["stone_ai", "shears_ai", "paper_ai"]
    a = battle_data[rival_id]["status"] = random.choice(stt)
    player_tx = None
    rival_tx = None

    if battle_data[player_id]["status"] == battle_data[rival_id]["status"]:
        player_tx = "🎉 Ничья! Но вы выбрали раньше соперника, ходите вторым 2️⃣"
        battle_data[player_id]["is_first"] = False
        battle_data[rival_id]["is_first"] = True
        battle_data[player_id]["status"] = None
        battle_data[rival_id]["status"] = None
    elif battle_data[player_id]["status"] == "stone_ai" and battle_data[rival_id]["status"] == "shears_ai":
        player_tx = "🎉 Вы победили! 2️⃣ ходите вторым"
        rival_tx = "💔 Вы проиграли! 1️⃣ ходите первым"
        battle_data[player_id]["is_first"] = False
        battle_data[rival_id]["is_first"] = True
        battle_data[player_id]["status"] = None
        battle_data[rival_id]["status"] = None
    elif battle_data[player_id]["status"] == "stone_ai" and battle_data[rival_id]["status"] == "paper_ai":
        player_tx = "💔 Вы проиграли! 1️⃣ ходите первым"
        rival_tx = "🎉 Вы победили! 2️⃣ ходите вторым"
        battle_data[player_id]["is_first"] = True
        battle_data[rival_id]["is_first"] = False
        battle_data[player_id]["status"] = None
        battle_data[rival_id]["status"] = None
    elif battle_data[player_id]["status"] == "shears_ai" and battle_data[rival_id]["status"] == "stone_ai":
        player_tx = "💔 Вы проиграли! 1️⃣ ходите первым"
        rival_tx = "🎉 Вы победили! 2️⃣ ходите вторым"
        battle_data[player_id]["is_first"] = True
        battle_data[rival_id]["is_first"] = False
        battle_data[player_id]["status"] = None
        battle_data[rival_id]["status"] = None
    elif battle_data[player_id]["status"] == "shears_ai" and battle_data[rival_id]["status"] == "paper_ai":
        player_tx = "🎉 Вы победили! 2️⃣ ходите вторым"
        rival_tx = "💔 Вы проиграли! 1️⃣ ходите первым"
        battle_data[player_id]["is_first"] = False
        battle_data[rival_id]["is_first"] = True
        battle_data[player_id]["status"] = None
        battle_data[rival_id]["status"] = None
    elif battle_data[player_id]["status"] == "paper_ai" and battle_data[rival_id]["status"] == "stone_ai":
        player_tx = "🎉 Вы победили! 2️⃣ ходите вторым"
        rival_tx = "💔 Вы проиграли! 1️⃣ ходите первым"
        battle_data[player_id]["is_first"] = False
        battle_data[rival_id]["is_first"] = True
        battle_data[player_id]["status"] = None
        battle_data[rival_id]["status"] = None
    elif battle_data[player_id]["status"] == "paper_ai" and battle_data[rival_id]["status"] == "shears_ai":
        player_tx = "💔 Вы проиграли! 1️⃣ ходите первым"
        rival_tx = "🎉 Вы победили! 2️⃣ ходите вторым"
        battle_data[player_id]["is_first"] = True
        battle_data[rival_id]["is_first"] = False
        battle_data[player_id]["status"] = None
        battle_data[rival_id]["status"] = None

    r_cb = a
    if r_cb == "stone_ai":
        r_choice = "Камень 🤜"
    elif r_cb == "shears_ai":
        r_choice = "Ножницы ✌️"
    elif r_cb == "paper_ai":
        r_choice = "Бумагу 🫱"
    await bot.edit_message_caption(chat_id=player_id, message_id=battle_data[player_id]["ms_id"],
                                   caption=f"𝅄  ⭑  ꒰ 🪨 ✂️ 📃 ꒱  ⭑  𝅄"
                                           "\n⟬Игра камень ножницы бумага⟭"
                                           f"\n\n × Вы: 『{choice}』"
                                           f"\n × Соперник: 『{r_choice}』"
                                           f"\n\n✧ {player_tx}")
    await asyncio.sleep(1)

    if battle_data[player_id]["is_first"]:
        user_text, user_status, user_cb, u_round = account_text(player_id)
        mes = await bot.send_message(chat_id=player_id, text=f"{user_text}"
                                                             f"\n🔸Ваш ход:",
                                     reply_markup=inline_builder(user_status, user_cb, row_width=[3, 3]))
    elif battle_data[rival_id]["is_first"]:
        # Допустим, у вас есть deck
        deck = battle_data[rival_id]["deck"]

        # Флаг для проверки, если все мертвы
        all_dead = True

        # Попробуем выбрать случайного персонажа
        while True:
            # Случайный выбор ключа из deck
            char = random.choice(list(deck.keys()))
            char_object = deck[char]

            # Проверяем статус случайно выбранного объекта
            if getattr(char_object, "status", None) != "☠️":
                card, char_object = char, char_object
                all_dead = False  # Найден живой объект
                break
            elif all(getattr(obj, "status", None) == "☠️" for obj in deck.values()):
                # Если у всех объектов status == "☠️"
                await bot.send_message(chat_id=player_id, text="все мертвы")
                card, char_object = None, None
                break

        # turn_char = random.choice([battle_data[rival_id]["deck"].keys()])

        battle_data[rival_id]["current"] = char_object
        battle_data[rival_id]["current_c"] = card

        user_text = round_text("Вы", char_object)
        rival_text = round_text("Соперник", char_object)

        avatar = character_photo.get_stats(char_object.universe, char_object.name, 'avatar')
        avatar_type = character_photo.get_stats(char_object.universe, char_object.name, 'type')

        if avatar_type == 'photo':
            await bot.send_photo(photo=avatar, chat_id=player_id, caption=user_text)
        else:
            await bot.send_animation(animation=avatar, chat_id=player_id, caption=user_text)

        user_text, user_status, user_cb, u_round = account_text(player_id)
        mes = await bot.send_message(chat_id=player_id, text=f"{user_text}"
                                                             f"\n🔸Ваш ход:",
                                     reply_markup=inline_builder(user_status, user_cb, row_width=[3, 3]))


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
                                 caption=end_text(user_id, rival_id, draw_text, draw_sts), reply_markup=menu_button())

        await mongodb.update_value(char1.ident, {"battle.stats.ties": 1})
        await mongodb.update_value(char1.ident, {"stats.exp": 8})
        await mongodb.update_value(char1.ident, {"account.money": 15})
        await mongodb.update_many(
            {"_id": {"$in": [char1.ident]}},
            {"$set": {"battle.battle.status": 0, "battle.battle.rid": ""}}
        )
        battle_data[user_id]["round"] += 1

    elif all("🎴" not in status for status in user_statuses):
        cont = False
        user_data[user_id][battle_data[user_id]["round"]] = True
        user_data[rival_id][battle_data[rival_id]["round"]] = True
        await bot.send_animation(chat_id=user_id, animation=lose_animation,
                                 caption=end_text(user_id, rival_id, lose_text, lose_sts), reply_markup=menu_button())

        await mongodb.update_value(char1.ident, {"battle.stats.loses": 1})
        await mongodb.update_value(char1.ident, {"stats.exp": 5})
        await mongodb.update_value(char1.ident, {"account.money": 10})
        await mongodb.update_many(
            {"_id": {"$in": [char1.ident]}},
            {"$set": {"battle.battle.status": 0, "battle.battle.rid": ""}}
        )
    elif all("🎴" not in status for status in rival_statuses):
        cont = False
        user_data[user_id][battle_data[user_id]["round"]] = True
        user_data[rival_id][battle_data[rival_id]["round"]] = True
        await bot.send_animation(chat_id=user_id, animation=win_animation,
                                 caption=end_text(user_id, rival_id, win_text, win_sts), reply_markup=menu_button())
        await mongodb.update_value(char1.ident, {"battle.stats.wins": 1})
        await mongodb.update_value(char1.ident, {"stats.exp": 10})
        await mongodb.update_value(char1.ident, {"account.money": 20})
        await mongodb.update_many(
            {"_id": {"$in": [char1.ident]}},
            {"$set": {"battle.battle.status": 0, "battle.battle.rid": ""}}
        )
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
    current_text = format_msg()
    msg = await bot.send_message(user_id, format_msg())

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

            # В КАЖДОМ месте, где обновляешь сообщение, добавляй:
            new_text = format_msg()
            if new_text != current_text:
                try:
                    await bot.edit_message_text(chat_id=user_id, message_id=msg.message_id, text=new_text)
                    current_text = new_text  # Обновляем локальную переменную
                except TelegramBadRequest as e:
                    if "message is not modified" not in str(e):
                        raise
            cont = await win_lose(bot, char1, char2)

            if cont:
                photo = 'AgACAgIAAx0CfstymgACPxhnpyOyMWhyizsk7AGoC0SRr47FdAACMewxG1EKQEkNebXgoiA-2wEAAwIAA3kAAzYE'
                text = (f"𝅄  ⭑  ꒰ 🪨 ✂️ 📃 ꒱  ⭑  𝅄"
                        "\n⟬ Игра камень ножницы бумага ⟭"
                        "\n\n × Вы: 『....』"
                        "\n × Соперник: 『....』"
                        "\n\n✧ ❔ Определяем кто будеть ходить первым")
                buttons = ["🤜", "✌️", "🫱"]
                cb = ["stone_ai", "shears_ai", "paper_ai"]

                mes = await bot.send_photo(chat_id=user_id, photo=photo, caption=text,
                                           reply_markup=inline_builder(buttons, cb, row_width=[3]))
                battle_data[user_id]["ms_id"] = mes.message_id
        elif char1.health <= 0:
            battle_log.append(f"\n🏆 {char2.name} побеждает в битве!")
            battle_data[char2.ident]["deck"][card2].status = "🎴"
            battle_data[char1.ident]["deck"][card1].status = "☠️"
            user_data[user_id][battle_data[user_id]["round"]] = True
            user_data[rival_id][battle_data[rival_id]["round"]] = True

            cont = await win_lose(bot, char1, char2)

            if cont:
                user_text, user_status, user_cb, rd = account_text(user_id)
                mg = await bot.send_message(chat_id=user_id, text=f"{user_text}"
                                                                  f"\n🔸Ваш ход:",
                                            reply_markup=inline_builder(user_status, user_cb, row_width=[3, 3]))

                battle_data[char2.ident]["current"] = None
                battle_data[char1.ident]["current"] = None

                # В КАЖДОМ месте, где обновляешь сообщение, добавляй:
                new_text = format_msg()
                if new_text != current_text:
                    try:
                        await bot.edit_message_text(chat_id=user_id, message_id=msg.message_id, text=new_text)
                        current_text = new_text  # Обновляем локальную переменную
                    except TelegramBadRequest as e:
                        if "message is not modified" not in str(e):
                            raise
        elif char2.health <= 0:
            battle_log.append(f"\n🏆 {char1.name} побеждает в битве!")
            battle_data[char1.ident]["deck"][card1].status = "🎴"
            battle_data[char2.ident]["deck"][card2].status = "☠️"
            user_data[user_id][battle_data[user_id]["round"]] = True
            user_data[rival_id][battle_data[rival_id]["round"]] = True

            cont = await win_lose(bot, char1, char2)

            if cont:
                await bot.send_message(chat_id=user_id, text=f"⏳ Ждём ход соперника...")
                await asyncio.sleep(1)
                # Допустим, у вас есть deck
                deck = battle_data[rival_id]["deck"]

                # Флаг для проверки, если все мертвы
                all_dead = True

                # Попробуем выбрать случайного персонажа
                while True:
                    # Случайный выбор ключа из deck
                    char = random.choice(list(deck.keys()))
                    char_object = deck[char]

                    # Проверяем статус случайно выбранного объекта
                    if getattr(char_object, "status", None) != "☠️":
                        card, char_object = char, char_object
                        all_dead = False  # Найден живой объект
                        break
                    elif all(getattr(obj, "status", None) == "☠️" for obj in deck.values()):
                        # Если у всех объектов status == "☠️"
                        await bot.send_message(chat_id=user_id, text="все мертвы")
                        card, char_object = None, None
                        break

                # turn_char = random.choice([battle_data[rival_id]["deck"].keys()])

                battle_data[rival_id]["current"] = char_object
                battle_data[rival_id]["current_c"] = card

                user_text = round_text("Вы", char_object)
                rival_text = round_text("Соперник", char_object)

                avatar = character_photo.get_stats(char_object.universe, char_object.name, 'avatar')
                avatar_type = character_photo.get_stats(char_object.universe, char_object.name, 'type')

                if avatar_type == 'photo':
                    await bot.send_photo(photo=avatar, chat_id=user_id, caption=rival_text)
                else:
                    await bot.send_animation(animation=avatar, chat_id=user_id, caption=rival_text)
                await asyncio.sleep(1)
                user_text, user_status, user_cb, u_round = account_text(user_id)
                mes = await bot.send_message(chat_id=user_id, text=f"{user_text}"
                                                                   f"\n🔸Ваш ход:",
                                             reply_markup=inline_builder(user_status, user_cb, row_width=[3, 3]))

                battle_data[char2.ident]["current"] = None
                battle_data[char1.ident]["current"] = None
                # В КАЖДОМ месте, где обновляешь сообщение, добавляй:
                new_text = format_msg()
                if new_text != current_text:
                    try:
                        await bot.edit_message_text(chat_id=user_id, message_id=msg.message_id, text=new_text)
                        current_text = new_text  # Обновляем локальную переменную
                    except TelegramBadRequest as e:
                        if "message is not modified" not in str(e):
                            raise
        await asyncio.sleep(1.5)

        # Обновляем сообщение с новыми ходами
        new_text = format_msg()
        if new_text != current_text:
            try:
                await bot.edit_message_text(chat_id=user_id, message_id=msg.message_id, text=new_text)
                current_text = new_text  # Обновляем локальную переменную
            except TelegramBadRequest as e:
                if "message is not modified" not in str(e):
                    raise
    # Финальное обновление
    new_text = format_msg()
    if new_text != current_text:
        try:
            await bot.edit_message_text(chat_id=user_id, message_id=msg.message_id, text=new_text)
        except TelegramBadRequest as e:
            if "message is not modified" not in str(e):
                raise

@router.callback_query(CallbackChatTypeFilter(chat_type=["private"]), F.data.startswith("×"))
async def start_battle(callback: CallbackQuery, bot: Bot):
    cb = callback.data
    player_id = callback.from_user.id
    rival_id = battle_data[player_id]["rival"]

    char = cb.replace("×", "")
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

    if not battle_data[rival_id]["current"]:
        await bot.send_message(chat_id=player_id, text=f"⏳ Ждём ход соперника...")
        await asyncio.sleep(1)
        # Допустим, у вас есть deck
        deck = battle_data[rival_id]["deck"]

        # Флаг для проверки, если все мертвы
        all_dead = True

        # Попробуем выбрать случайного персонажа
        while True:
            # Случайный выбор ключа из deck
            char = random.choice(list(deck.keys()))
            char_object = deck[char]

            # Проверяем статус случайно выбранного объекта
            if getattr(char_object, "status", None) != "☠️":
                card, char_object = char, char_object
                all_dead = False  # Найден живой объект
                break
            elif all(getattr(obj, "status", None) == "☠️" for obj in deck.values()):
                # Если у всех объектов status == "☠️"
                await bot.send_message(chat_id=player_id, text="все мертвы")
                card, char_object = None, None
                break

        # turn_char = random.choice([battle_data[rival_id]["deck"].keys()])

        battle_data[rival_id]["current"] = char_object
        battle_data[rival_id]["current_c"] = card

        user_text = round_text("Вы", char_object)
        rival_text = round_text("Соперник", char_object)

        avatar = character_photo.get_stats(char_object.universe, char_object.name, 'avatar')
        avatar_type = character_photo.get_stats(char_object.universe, char_object.name, 'type')
        await asyncio.sleep(1)
        if avatar_type == 'photo':
            await bot.send_photo(photo=avatar, chat_id=player_id, caption=rival_text)
        else:
            await bot.send_animation(animation=avatar, chat_id=player_id, caption=rival_text)
        await asyncio.sleep(1)
        user_text, user_status, user_cb, u_round = account_text(player_id)
        user_char = battle_data[player_id]["current"]
        rival_char = battle_data[rival_id]["current"]
        user_card = battle_data[player_id]["current_c"]
        rival_card = battle_data[rival_id]["current_c"]
        await battle(bot, player_id, rival_id, user_char, rival_char, user_card, rival_card)
        # mes = await bot.send_message(chat_id=player_id, text=f"{user_text}"
        #                                                      f"\n🔸Ваш ход:",
        #                              reply_markup=inline_builder(user_status, user_cb, row_width=[3, 3]))

    else:
        user_char = battle_data[player_id]["current"]
        rival_char = battle_data[rival_id]["current"]
        user_card = battle_data[player_id]["current_c"]
        rival_card = battle_data[rival_id]["current_c"]
        await battle(bot, player_id, rival_id, user_char, rival_char, user_card, rival_card)
