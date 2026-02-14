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
from app.keyboards.builders import reply_builder, abilities_kb, menu_card_button
from app.routers import gacha

router = Router()

battle_data = {}

user_data = {}

win_text = ('<tg-emoji emoji-id="5465465194056525619">❌</tg-emoji>Победа: <tg-emoji emoji-id="5463186335948878489">❌</tg-emoji>Соперник мертв"'
            '\n<blockquote expandable>── •✧✧• ──────────'
            '\n  + 100<tg-emoji emoji-id="5380033625909634211">❌</tg-emoji> xp, '
            '\n  + 200<tg-emoji emoji-id="5201873447554145566">❌</tg-emoji> ¥</blockquote>')

lose_text = ('<tg-emoji emoji-id="5463186335948878489">❌</tg-emoji>Поражение'
             '\n<blockquote expandable>── •✧✧• ──────────'
             '\n  + 55<tg-emoji emoji-id="5380033625909634211">❌</tg-emoji> xp, '
             '\n  + 100<tg-emoji emoji-id="5201873447554145566">❌</tg-emoji> ¥</blockquote>')

draw_text = ('<tg-emoji emoji-id="5465465194056525619">❌</tg-emoji>Ничья'
             '\n<blockquote expandable>── •✧✧• ──────────'
             '\n  + 80<tg-emoji emoji-id="5380033625909634211">❌</tg-emoji> xp, '
             '\n  + 150<tg-emoji emoji-id="5201873447554145566">❌</tg-emoji> ¥</blockquote>')

surrender_text = '<tg-emoji emoji-id="5316560584869690299">❌</tg-emoji> Поражение'

surrender_r_text = ('<tg-emoji emoji-id="5465465194056525619">❌</tg-emoji>Победа: <tg-emoji emoji-id="5316560584869690299">❌</tg-emoji>Соперник сдался'
                    '\n<blockquote expandable>── •✧✧• ──────────'
                    '\n  + 100<tg-emoji emoji-id="5380033625909634211">❌</tg-emoji> xp, '
                    '\n  + 200<tg-emoji emoji-id="5201873447554145566">❌</tg-emoji> ¥</blockquote>')

time_out_text = ('<tg-emoji emoji-id="5465465194056525619">❌</tg-emoji>Победа: <tg-emoji emoji-id="5462990652943904884">❌</tg-emoji>Соперник афк'
                 '\n<blockquote expandable>── •✧✧• ──────────'
                 '\n  + 100<tg-emoji emoji-id="5380033625909634211">❌</tg-emoji> xp, '
                 '\n  + 200<tg-emoji emoji-id="5201873447554145566">❌</tg-emoji> ¥</blockquote>')


def account_text(character):
    text = (f'                 {character.name}'
            f'\n\n<tg-emoji emoji-id="5395343431973238126">❌</tg-emoji>{character.health}'
            f' <tg-emoji emoji-id="5201665489532638627">❌</tg-emoji>{character.attack}'
            f' <tg-emoji emoji-id="5465154440287757794">❌</tg-emoji>{character.defense}'
            f' <tg-emoji emoji-id="5794242604103110904">❌</tg-emoji>{character.mana}'
            f' <tg-emoji emoji-id="5371058888017715839">❌</tg-emoji>{character.energy}'
            f'\n<tg-emoji emoji-id="5373342608028352831">❌</tg-emoji>К.ур: {character.crit_dmg}'
            f' <tg-emoji emoji-id="5267373056027803452">❌</tg-emoji>К.шн: {character.crit_ch}'
            f' <tg-emoji emoji-id="5251203410396458957">❌</tg-emoji>Щит: {character.shield}'
            f'\n\n<tg-emoji emoji-id="5316791950462950306">❌</tg-emoji>Сила: {character.strength}'
            f' <tg-emoji emoji-id="5949588538952518773">❌</tg-emoji>Лов.: {character.agility}'
            f' <tg-emoji emoji-id="5371053287380361807">❌</tg-emoji>Инт.: {character.intelligence}'
            f'\n\n<tg-emoji emoji-id="5341772463804002252">❌</tg-emoji>Пассивки: {character.passive_names}')
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
                 "name": 'AI <tg-emoji emoji-id="5134472688986756318">❌</tg-emoji>',
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

        user_text = (f'<tg-emoji emoji-id="5454014806950429357">❌</tg-emoji> Cоперник Найден! '
                         # f"\n── •✧✧• ──────────"
                         f'\n<blockquote expandable><tg-emoji emoji-id="5936017305585586269">❌</tg-emoji>  〢 {rival['name']} '
                         f'\n── •✧✧• ───────'
                         f'\n❖ <tg-emoji emoji-id="5415624997689381048">❌</tg-emoji> Редкость: {r_rarity}'
                         f'\n❖ <tg-emoji emoji-id="5341294339454675575">❌</tg-emoji> Вселенная: {r_universe}'
                         f'\n   <tg-emoji emoji-id="5316791950462950306">❌</tg-emoji> Сила: {r_strength}'
                         f'\n   <tg-emoji emoji-id="5949588538952518773">❌</tg-emoji> Ловкость: {r_agility}'
                         f'\n   <tg-emoji emoji-id="5371053287380361807">❌</tg-emoji> Интелект: {r_intelligence}'
                         f'\n   <tg-emoji emoji-id="5431420156532235514">❌</tg-emoji> Мощь: {r_power}</blockquote>'
                         # f"\n── •✧✧• ──────────"
                         f'\n<i><tg-emoji emoji-id="5380033625909634211">❌</tg-emoji> Опыт: 1000 XP </i>')
        now = datetime.utcnow()

        await mongodb.update_user(
            account["_id"],
            {
                "battle.battle.status": 2,
                "battle.battle.rid": r_ident,
                "battle.battle.round": 1,
                "battle.battle.turn": r_ident,
                "battle.battle.turn_started_at": now
            }
        )

        if r_avatar_type == 'photo':
            await bot.send_photo(chat_id=user_id, photo=r_avatar, caption=user_text,
                                 reply_markup=reply_builder("🏴‍☠️ Сдаться"))
        else:
            await bot.send_animation(chat_id=user_id, animation=r_avatar, caption=user_text,
                                     reply_markup=reply_builder("🏴‍☠️ Сдаться"))

        await bot.send_message(account["_id"], text='<tg-emoji emoji-id="6005552426675868041">❌</tg-emoji> Ход соперника <tg-emoji emoji-id="5010636296373142479">❌</tg-emoji>')
        # Инициализируем состояние пользователя
        user_data[r_ident] = {rb_character.round: False}
        user_data[user_id] = {b_character.round: True}
        await ai(rb_character, bot, callback, account)

    elif account["battle"]["battle"]["status"] == 1:
        if isinstance(callback, CallbackQuery):
            await callback.answer(
                text="💢 Вы уже находитесь в поиске соперника!",
                show_alert=True
            )
        else:
            await callback.answer(text='<tg-emoji emoji-id="6039884526929317741">❌</tg-emoji> Вы уже находитесь в поиске соперника!')

    elif account["battle"]["battle"]["status"] == 2:
        if isinstance(callback, CallbackQuery):
            await callback.answer(
                text="💢 Вы уже находитесь в битве!",
                show_alert=True
            )
        else:
            await callback.answer(text='<tg-emoji emoji-id="6039884526929317741">❌</tg-emoji> Вы уже находитесь в битве!')


async def ai(character, bot, callback, account):
    # === НАЧАЛО ХОДА AI (ПРОВЕРКА STUN) ===
    if character.stun > 0:
        character.stun -= 1

        rival = battle_data.get(character.rid)
        next_round = character.round + 1
        character.round = next_round
        rival.round = next_round

        now = datetime.utcnow()

        await mongodb.update_user(
            rival.ident,
            {
                "battle.battle.round": next_round,
                "battle.battle.turn": rival.ident,
                "battle.battle.turn_started_at": now
            }
        )

        await mongodb.update_user(
            character.ident,
            {
                "battle.battle.round": next_round,
                "battle.battle.turn": rival.ident,
                "battle.battle.turn_started_at": now
            }
        )

        await bot.send_message(
            rival.ident,
            "💫 Противник оглушён и пропускает ход. Ваш ход."
        )

        return  # ← ВОТ ЭТОГО У ТЕБЯ НЕ ХВАТАЛО

    r_character = battle_data.get(character.rid)

    if character.ident != r_character.ident * 10:
        if account["battle"]["battle"].get("finished"):
            return

    if not r_character:
        return

    try:
        r_character = battle_data.get(character.rid)

        while True:
            action = random.choice(character.ability)
            # action = '˹🗡Атака˼'
            mana, energy = await characters.turn(character, bot, action, r_character, 0, ai=True)
            # КЛАМП ХП
            character.health = max(0, character.health)
            r_character.health = max(0, r_character.health)

            if not mana:
                continue  # Выбираем новую способность

            if not energy:
                continue  # Выбираем новую способность

            # Если хватает и маны, и энергии, выходим из цикла
            break

        battle_data[character.ident] = character
        battle_data[r_character.ident] = r_character

        async def ai_send_round_photo():

            if character.ident != r_character.ident*10:
                if account["battle"]["battle"].get("finished"):
                    return

            # ---------- ПЕРЕДАЧА ХОДА (AI ↔ PLAYER) ----------
            next_round = character.round + 1
            now = datetime.utcnow()

            # === ЕСЛИ НЕ ОГЛУШЁН — ПЕРЕДАЁМ ХОД ИГРОКУ ===
            character.round = next_round
            r_character.round = next_round

            await mongodb.update_user(
                character.ident,
                {
                    "battle.battle.round": next_round,
                    "battle.battle.turn": r_character.ident,
                    "battle.battle.turn_started_at": now
                }
            )

            await mongodb.update_user(
                r_character.ident,
                {
                    "battle.battle.round": next_round,
                    "battle.battle.turn": r_character.ident,
                    "battle.battle.turn_started_at": now
                }
            )

            # ---- НОРМАЛЬНЫЙ ХОД ИГРОКА ----
            mes = await bot.send_message(
                r_character.ident,
                text=(
                    f'. ˗ˋˏРаунд {r_character.round}ˎˊ˗\n'
                    f'<blockquote expandable>{account_text(r_character)}</blockquote>\n'
                    f'➖➖➖➖➖➖➖➖➖➖➖\n'
                    f'<blockquote expandable>{account_text(character)}</blockquote>\n'
                    f'<tg-emoji emoji-id="5449372823476777969">❌</tg-emoji> Ваш ход:'
                ),
                reply_markup=abilities_kb(
                    r_character.ability,
                    hp=r_character.health,
                    mana=r_character.mana,
                    energy=r_character.energy
                ),
                parse_mode=ParseMode.HTML
            )

            user_data[character.ident][character.round - 1] = True
            user_data[r_character.ident][r_character.round] = False

        if character.health <= 0 and r_character.health <= 0:
            if character.round != r_character.round:
                await mongodb.update_user(character.rid, {
                    "battle.battle.finished": True
                })

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
            else:
                await ai_send_round_photo()

        elif character.health <= 0:
            if character.round != r_character.round:
                await mongodb.update_user(character.rid, {
                    "battle.battle.finished": True
                })

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
            if character.round != r_character.round:
                await mongodb.update_user(character.rid, {
                    "battle.battle.finished": True
                })

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
