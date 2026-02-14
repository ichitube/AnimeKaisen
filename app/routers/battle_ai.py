import asyncio
import random
from datetime import datetime

from aiogram import Router, F, Bot
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from app.data import characters, character_photo, mongodb
from app.filters.chat_type import ChatTypeFilter
from app.keyboards.builders import reply_builder, abilities_kb, menu_button
from app.routers import gacha

router = Router()

# ВАЖНО: battle_k.py импортирует ЭТИ объекты отсюда
battle_data: dict[int, characters.Character] = {}

# --- UI / тексты (как в battle_k.py, чтобы было консистентно) ---
win_animation = "CgACAgIAAx0CfstymgACU89phx6oGOEat9rGuAhVXm28HWT1GwACkY4AAjB7OUjIDO3nHKlgqjoE"
lose_animation = "CgACAgIAAx0CfstymgACU79phx1P2AbZPMsRGLMAAdL0Qd5c87wAAj2MAAIGgTlIRjDPzyWMboM6BA"
draw_animation = "CgACAgQAAx0CfstymgACU8tphx2kMdBisOdfwnspIHL49_y_HAACxwcAAh8stFOn_pYtCKSEoToE"

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

TURN_TIMEOUT = 61  # секунд


def account_text(character: characters.Character) -> str:
    return (
        f'                 {character.name}'
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
        f'\n\n<tg-emoji emoji-id="5341772463804002252">❌</tg-emoji>Пассивки: {character.passive_names}'
    )


def _rar_key(rus_rarity: str) -> str:
    return {
        "Божественная": "divine",
        "Мифическая": "mythical",
        "Легендарная": "legendary",
        "Эпическая": "epic",
        "Редкая": "rare",
        "Обычная": "common",
    }.get(rus_rarity, "common")


async def _finish_ai_battle(player_id: int, bot: Bot, result: str) -> None:
    """
    result: 'win' | 'lose' | 'draw' относительно игрока.
    """
    now = datetime.utcnow()

    if result == "win":
        await bot.send_animation(player_id, animation=win_animation, caption=win_text, reply_markup=menu_button())
        inc = {"battle.stats.wins": 1, "stats.exp": 100, "account.money": 200}
    elif result == "lose":
        await bot.send_animation(player_id, animation=lose_animation, caption=lose_text, reply_markup=menu_button())
        inc = {"battle.stats.loses": 1, "stats.exp": 55, "account.money": 100}
    else:
        await bot.send_animation(player_id, animation=draw_animation, caption=draw_text, reply_markup=menu_button())
        inc = {"battle.stats.ties": 1, "stats.exp": 80, "account.money": 150}

    await mongodb.update_ops(player_id, {
        "$set": {
            "battle.battle.finished": True,
            "battle.battle.status": 0,
            "battle.battle.rid": "",
            "tasks.last_arena_fight": now,
        },
        "$inc": inc
    })

    # чистим память
    battle_data.pop(player_id, None)
    battle_data.pop(player_id * 10, None)


@router.message(ChatTypeFilter(chat_type=["private"]), Command("ai_battle"))
@router.callback_query(F.data == "ai_battle")
async def ai_battle_start(callback: CallbackQuery | Message, bot: Bot):
    user_id = callback.from_user.id
    account = await mongodb.get_user(user_id)
    universe = account["universe"]

    if isinstance(callback, CallbackQuery):
        await callback.message.delete()

    if account["battle"]["battle"]["status"] != 0:
        txt = "💢 Вы уже в бою или в поиске!"
        if isinstance(callback, CallbackQuery):
            await callback.answer(text=txt, show_alert=True)
        else:
            await callback.answer(text=txt)
        return

    # выбираем случайного AI персонажа
    universes = [k for k in gacha.characters.keys() if k not in ["Allstars", "Allstars(old)"]]
    ai_universe = random.choice(universes)
    rarity = character_photo.get_stats(universe, account["character"][universe], "rarity")
    ai_pool = gacha.characters[ai_universe][_rar_key(rarity)]
    ai_character_name = random.choice(ai_pool)

    # Игрок
    ident = user_id
    name = account["name"]
    char_name = account["character"][universe]
    strength = character_photo.get_stats(universe, char_name, "arena")["strength"]
    agility = character_photo.get_stats(universe, char_name, "arena")["agility"]
    intelligence = character_photo.get_stats(universe, char_name, "arena")["intelligence"]
    ability = character_photo.get_stats(universe, char_name, "arena")["ability"]
    slave = None
    if account.get("inventory", {}).get("slaves"):
        slave = account["inventory"]["slaves"][0]

    player = characters.Character(
        ident, name, char_name, strength, agility, intelligence, ability,
        1, False, ident * 10, slave, 0
    )
    battle_data[user_id] = player

    # AI
    ai_id = user_id * 10
    ai_name = 'AI <tg-emoji emoji-id="5134472688986756318">❌</tg-emoji>'
    ai_strength = character_photo.get_stats(ai_universe, ai_character_name, "arena")["strength"]
    ai_agility = character_photo.get_stats(ai_universe, ai_character_name, "arena")["agility"]
    ai_intelligence = character_photo.get_stats(ai_universe, ai_character_name, "arena")["intelligence"]
    ai_ability = character_photo.get_stats(ai_universe, ai_character_name, "arena")["ability"]

    ai_char = characters.Character(
        ai_id, ai_name, ai_character_name, ai_strength, ai_agility, ai_intelligence, ai_ability,
        1, False, user_id, None, 0
    )
    battle_data[ai_id] = ai_char

    # Показ соперника
    r_avatar = character_photo.get_stats(ai_universe, ai_character_name, "avatar")
    r_avatar_type = character_photo.get_stats(ai_universe, ai_character_name, "type")
    r_rarity = character_photo.get_stats(ai_universe, ai_character_name, "rarity")
    r_power = character_photo.get_stats(ai_universe, ai_character_name, "arena")["power"]

    user_text = (
        f'<tg-emoji emoji-id="5454014806950429357">❌</tg-emoji> Cоперник Найден! '
        f'\n<blockquote expandable><tg-emoji emoji-id="5936017305585586269">❌</tg-emoji>  〢 {ai_name} '
        f'\n── •✧✧• ───────'
        f'\n❖ <tg-emoji emoji-id="5415624997689381048">❌</tg-emoji> Редкость: {r_rarity}'
        f'\n❖ <tg-emoji emoji-id="5341294339454675575">❌</tg-emoji> Вселенная: {ai_universe}'
        f'\n   <tg-emoji emoji-id="5316791950462950306">❌</tg-emoji> Сила: {ai_strength}'
        f'\n   <tg-emoji emoji-id="5949588538952518773">❌</tg-emoji> Ловкость: {ai_agility}'
        f'\n   <tg-emoji emoji-id="5371053287380361807">❌</tg-emoji> Интелект: {ai_intelligence}'
        f'\n   <tg-emoji emoji-id="5431420156532235514">❌</tg-emoji> Мощь: {r_power}</blockquote>'
        f'\n<i><tg-emoji emoji-id="5380033625909634211">❌</tg-emoji> Опыт: 1000 XP </i>'
    )

    now = datetime.utcnow()
    await mongodb.update_user(user_id, {
        "battle.battle.status": 2,
        "battle.battle.rid": ai_id,
        "battle.battle.round": 1,
        "battle.battle.turn": ai_id,  # AI ходит первым (как было у тебя)
        "battle.battle.turn_started_at": now,
        "battle.battle.finished": False
    })

    if r_avatar_type == "photo":
        await bot.send_photo(user_id, photo=r_avatar, caption=user_text, reply_markup=reply_builder("🏴‍☠️ Сдаться"))
    else:
        await bot.send_animation(user_id, animation=r_avatar, caption=user_text, reply_markup=reply_builder("🏴‍☠️ Сдаться"))

    await bot.send_message(user_id, text='Ход соперника <tg-emoji emoji-id="5010636296373142479">❌</tg-emoji>')

    # стартуем AI ход
    await asyncio.sleep(1)
    await ai(ai_char, bot, None, account)


async def ai(character: characters.Character, bot: Bot, _callback, _account):
    """
    AI ход. Вызывается:
    - из battle_k.py после хода игрока, когда ход переходит AI
    - из ai_battle_start(), когда AI ходит первым
    """
    # соперник (игрок)
    rival = battle_data.get(character.rid)
    if not rival:
        return

    # актуальное состояние боя из БД (источник истины для turn/round/status)
    acc = await mongodb.get_user(rival.ident)
    battle = acc.get("battle", {}).get("battle", {})
    if battle.get("status") != 2 or battle.get("rid") != character.ident or battle.get("finished"):
        return

    round_no = battle.get("round", character.round)
    lock_id = f"pve:turn:{character.ident}:{round_no}"

    # идемпотентность AI хода (на случай двойного вызова)
    is_first = await mongodb.claim_once(lock_id, character.ident, ttl_sec=TURN_TIMEOUT)
    if not is_first:
        return

    # если внезапно не ход AI — выходим
    if battle.get("turn") != character.ident:
        await mongodb.db.once.delete_one({"_id": lock_id})
        return

    # --- STUN в начале хода AI (как в battle_k.py у игрока) ---
    # --- STUN в начале хода AI ---
    if character.stun > 0:
        character.stun = max(0, character.stun - 1)

        next_round = round_no + 1
        now = datetime.utcnow()

        character.round = next_round
        rival.round = next_round

        # ✅ PvE: обновляем ТОЛЬКО игрока
        await mongodb.update_user(
            rival.ident,
            {
                "battle.battle.round": next_round,
                "battle.battle.turn": rival.ident,
                "battle.battle.turn_started_at": now
            }
        )

        battle_data[character.ident] = character
        battle_data[rival.ident] = rival

        await bot.send_message(
            rival.ident,
            '<tg-emoji emoji-id="5967744293425646719">💫</tg-emoji> Противник оглушён и пропускает ход. Ваш ход:',
            reply_markup=abilities_kb(
                rival.ability, hp=rival.health, mana=rival.mana, energy=rival.energy
            )
        )

        await mongodb.db.once.delete_one({"_id": lock_id})
        return

    # --- AI выбирает действие (пока не хватит ресурсов) ---
    while True:
        action = random.choice(character.ability)
        mana, energy = await characters.turn(character, bot, action, rival, 0, ai=True)

        character.health = max(0, character.health)
        rival.health = max(0, rival.health)

        if mana and energy:
            break

    battle_data[character.ident] = character
    battle_data[rival.ident] = rival

    # --- ФИНАЛ (ВАЖНО: если AI убил игрока, игрок уже не сможет "дожать" финал своим ходом) ---
    if character.health <= 0 and rival.health <= 0:
        await mongodb.db.once.delete_one({"_id": lock_id})
        await _finish_ai_battle(rival.ident, bot, "draw")
        return
    if rival.health <= 0:
        await mongodb.db.once.delete_one({"_id": lock_id})
        await _finish_ai_battle(rival.ident, bot, "lose")  # игрок проиграл
        return
    if character.health <= 0:
        await mongodb.db.once.delete_one({"_id": lock_id})
        await _finish_ai_battle(rival.ident, bot, "win")   # игрок выиграл
        return

    # --- ПЕРЕДАЧА ХОДА (как в battle_k.py) ---
    next_round = round_no + 1
    now = datetime.utcnow()

    if rival.stun > 0:
        # игрок оглушён -> списываем 1 пропуск и ход остаётся у AI
        rival.stun = max(0, rival.stun - 1)

        character.round = next_round
        rival.round = next_round

        # ✅ PvE: в БД обновляем только игрока, turn остаётся AI
        await mongodb.update_user(
            rival.ident,
            {
                "battle.battle.round": next_round,
                "battle.battle.turn": character.ident,
                "battle.battle.turn_started_at": now
            }
        )

        battle_data[character.ident] = character
        battle_data[rival.ident] = rival

        await bot.send_message(
            rival.ident,
            text='Ход соперника <tg-emoji emoji-id="5010636296373142479">❌</tg-emoji>',
            reply_markup=abilities_kb(
                rival.ability, hp=rival.health, mana=rival.mana, energy=rival.energy
            )
        )

        await mongodb.db.once.delete_one({"_id": lock_id})

        # AI ходит ещё раз (пауза чтобы не спамить)
        await asyncio.sleep(1)
        await ai(character, bot, None, acc)
        return

    # иначе — обычная передача хода игроку
    character.round = next_round
    rival.round = next_round

    await mongodb.update_user(
        rival.ident,
        {
            "battle.battle.round": next_round,
            "battle.battle.turn": rival.ident,
            "battle.battle.turn_started_at": now
        }
    )

    battle_data[character.ident] = character
    battle_data[rival.ident] = rival

    # вывод раунда + кнопки игроку
    await bot.send_message(
        rival.ident,
        text=(
            f'.               ˗ˋˏ<tg-emoji emoji-id="5215480011322042129">❌</tg-emoji> Раунд {next_round}ˎˊ˗'
            f'\n<blockquote expandable>{account_text(rival)}</blockquote>'
            f'\n➖➖➖➖➖➖➖➖➖➖➖'
            f'\n<blockquote expandable>{account_text(character)}</blockquote>'
        ),
        parse_mode=ParseMode.HTML
    )

    await bot.send_message(
        rival.ident,
        text='\n<tg-emoji emoji-id="5449372823476777969">❌</tg-emoji> Ваш ход:',
        reply_markup=abilities_kb(
            rival.ability, hp=rival.health, mana=rival.mana, energy=rival.energy
        )
    )

    await mongodb.db.once.delete_one({"_id": lock_id})
