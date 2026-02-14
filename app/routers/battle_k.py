import asyncio
import random
from datetime import datetime

from aiogram import Router, F, Bot
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from app.data import characters, character_photo
from app.data import mongodb
from app.filters.chat_type import ChatTypeFilter, CallbackChatTypeFilter
from app.keyboards.builders import reply_builder, abilities_kb, menu_button
from app.routers import arena
from app.routers.battle_ai import ai, battle_data

router = Router()

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


TURN_TIMEOUT = 61  # секунд

async def _timeout_defeat(user_id: int, bot: Bot):
    account = await mongodb.get_user(user_id)
    rival = await mongodb.get_user(account["battle"]["battle"]["rid"])

    await bot.send_message(
        chat_id=user_id,
        text='<tg-emoji emoji-id="5947158686974610777">❌</tg-emoji> Время вышло'
    )

    await bot.send_animation(
        chat_id=user_id,
        animation=lose_animation,
        caption=surrender_text,
        reply_markup=menu_button()
    )

    now = datetime.utcnow()

    await mongodb.update_value(user_id, {"battle.stats.loses": 1})
    await mongodb.update_value(rival["_id"], {"battle.stats.wins": 1})
    await mongodb.update_value(rival["_id"], {"stats.exp": 100})
    await mongodb.update_value(rival["_id"], {"account.money": 200})
    await mongodb.update_user(rival["_id"], {"tasks.last_arena_fight": now})

    await mongodb.update_many(
        {"_id": {"$in": [user_id, rival["_id"]]}},
        {"$set": {"battle.battle.status": 0, "battle.battle.rid": ""}}
    )

    await bot.send_animation(
        chat_id=rival["_id"],
        animation=win_animation,
        caption=time_out_text,
        reply_markup=menu_button()
    )

    # чистим память
    battle_data.pop(user_id, None)
    battle_data.pop(rival["_id"], None)


async def surrender_f(user_id, r, mes, bot: Bot):
    # получаем актуальные данные
    account = await mongodb.get_user(user_id)
    if account["battle"]["battle"].get("finished"):
        return
    battle = account.get("battle", {}).get("battle", {})

    # базовые защиты
    if battle.get("status") != 2:
        return

    if battle.get("round") != r:
        return

    started_at = battle.get("turn_started_at")

    # если по какой-то причине timestamp отсутствует
    if not started_at:
        started_at = datetime.utcnow()
        await mongodb.update_user(
            user_id,
            {"battle.battle.turn_started_at": started_at}
        )

    elapsed = (datetime.utcnow() - started_at).total_seconds()
    remaining = TURN_TIMEOUT - elapsed

    # если время уже вышло (например, после рестарта)
    if remaining <= 0:
        await _timeout_defeat(user_id, bot)
        return

    # иначе ждём ОСТАТОК времени
    await asyncio.sleep(remaining)

    # после сна — ПОВТОРНАЯ проверка (очень важно)
    account = await mongodb.get_user(user_id)
    battle = account.get("battle", {}).get("battle", {})

    if (
            battle.get("status") == 2
            and battle.get("round") == r
            and battle.get("turn") == user_id
    ):
        await _timeout_defeat(user_id, bot)


def can_fight(account: dict, rival_id: int) -> bool:
    recent = account.get("battle", {}).get("recent_opponents", [])
    return rival_id not in recent


@router.message(ChatTypeFilter(chat_type=["private"]), Command("search"))
@router.callback_query(F.data == "search_opponent")
async def search_opponent(callback: CallbackQuery | Message, bot: Bot):
    user_id = callback.from_user.id
    account = await mongodb.get_user(user_id)
    universe = account['universe']

    if account['universe'] in ['Allstars', 'Allstars(old)']:
        await callback.answer(
            text="💢 Пока не доступно в вашой вселеноой!",
            show_alert=True
        )
        return

    if isinstance(callback, CallbackQuery):
        await callback.message.delete()

    if account["battle"]["battle"]["status"] == 0:
        # 🔒 ПЫТАЕМСЯ ЗАЛОЧИТЬ ПОИСК (ЗАЩИТА ОТ ГОНКИ)
        updated = await mongodb.try_lock_search(user_id)
        if not updated:
            return

        # 1. СНАЧАЛА фиксируем себя как ищущего
        await mongodb.update_user(user_id, {
            "battle.battle.status": 1,
            "battle.battle.search_started_at": datetime.utcnow()
        })
        # 2. Обновляем account (ОБЯЗАТЕЛЬНО)
        account = await mongodb.get_user(user_id)

        # 3. Только теперь ищем соперника
        rival = await mongodb.find_opponent_safe(account)
        if rival is None:
            await bot.send_animation(
                user_id,
                animation="CgACAgQAAx0CfstymgACUxZpfhQexsDg_rmC1xwo1uYd4Sye9AACXggAAjfJ1VOz_eDIu7-WuTgE",
                caption=f'\n <blockquote expandable><tg-emoji emoji-id="5947043478771862917">❌</tg-emoji> {random.choice(character_photo.quotes[universe])}</blockquote>'
                        f'\n── •✧✧• ──────────'
                        f'\n❖ <tg-emoji emoji-id="5010357961017524878">❌</tg-emoji> Поиск соперника . . . . .',
                reply_markup=reply_builder("✖️ Отмена")
            )
            return

        else:
            fresh = await mongodb.get_user(rival["_id"])

            if not fresh or fresh["battle"]["battle"]["status"] != 1:
                # соперник уже не ищет — откатываем себя
                await mongodb.update_user(user_id, {"battle.battle.status": 0})
                return
            ident = account["_id"]
            name = account["name"]
            character = account['character'][account['universe']]
            avatar = character_photo.get_stats(universe, character, 'avatar')
            avatar_type = character_photo.get_stats(universe, character, 'type')
            rarity = character_photo.get_stats(universe, character, 'rarity')
            strength = character_photo.get_stats(universe, character, 'arena')['strength']
            agility = character_photo.get_stats(universe, character, 'arena')['agility']
            intelligence = character_photo.get_stats(universe, character, 'arena')['intelligence']
            ability = character_photo.get_stats(universe, character, 'arena')['ability']
            power = character_photo.get_stats(universe, character, 'arena')['power']
            slave = account.get("active", {}).get("slave")

            # защита
            if slave and slave not in account.get("inventory", {}).get("slaves", []):
                slave = None

            b_character = characters.Character(ident, name, character, strength, agility, intelligence, ability, 1,
                                               False, rival["_id"], slave, 0)

            battle_data[account["_id"]] = b_character

            r_ident = rival["_id"]
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
            if rival['inventory']['slaves']:
                r_slave = rival['inventory']['slaves'][0]

            rb_character = characters.Character(r_ident, r_name, r_character, r_strength, r_agility, r_intelligence,
                                                r_ability, 1, True, account["_id"], r_slave, 0)

            battle_data[rival["_id"]] = rb_character

            user_text = (f'<tg-emoji emoji-id="5454014806950429357">❌</tg-emoji> Cоперник Найден! '
                         # f"\n── •✧✧• ──────────"
                         f'\n<blockquote expandable><tg-emoji emoji-id="5936017305585586269">❌</tg-emoji>  〢 {rival['name']} '
                         f'\n── •✧✧• ───────'
                         f'\n❖ <tg-emoji emoji-id="5415624997689381048">❌</tg-emoji> Редкость: {r_rarity}'
                         f'\n❖ <tg-emoji emoji-id="5341294339454675575">❌</tg-emoji> Вселенная: {r_universe}'
                         f'\n\n   <tg-emoji emoji-id="5316791950462950306">❌</tg-emoji> Сила: {r_strength}'
                         f'\n   <tg-emoji emoji-id="5949588538952518773">❌</tg-emoji> Ловкость: {r_agility}'
                         f'\n   <tg-emoji emoji-id="5371053287380361807">❌</tg-emoji> Интелект: {r_intelligence}'
                         f'\n   <tg-emoji emoji-id="5431420156532235514">❌</tg-emoji> Мощь: {r_power}</blockquote>'
                         # f"\n── •✧✧• ──────────"
                         f'\n<i><tg-emoji emoji-id="5380033625909634211">❌</tg-emoji> Опыт: {rival['stats']['exp']} XP </i>')

            rival_text = (f'<tg-emoji emoji-id="5454014806950429357">❌</tg-emoji> Cоперник Найден! '
                          # f"\n── •✧✧• ──────────"
                          f'\n<blockquote expandable><tg-emoji emoji-id="5936017305585586269">❌</tg-emoji>  〢 {account['name']} '
                          f'\n── •✧✧• ───────'
                          f'\n❖ <tg-emoji emoji-id="5415624997689381048">❌</tg-emoji> Редкость: {rarity}'
                          f'\n❖ <tg-emoji emoji-id="5341294339454675575">❌</tg-emoji> Вселенная: {universe}'
                          f'\n\n   <tg-emoji emoji-id="5316791950462950306">❌</tg-emoji> Сила: {strength}'
                          f'\n   <tg-emoji emoji-id="5949588538952518773">❌</tg-emoji> Ловкость: {agility}'
                          f'\n   <tg-emoji emoji-id="5371053287380361807">❌</tg-emoji> Интелект: {intelligence}'
                          f'\n   <tg-emoji emoji-id="5431420156532235514">❌</tg-emoji> Мощь: {power}</blockquote>'
                          # f"\n── •✧✧• ──────────"
                          f'\n<i><tg-emoji emoji-id="5380033625909634211">❌</tg-emoji> Опыт: {account['stats']['exp']} XP </i>')

            now = datetime.utcnow()

            await mongodb.update_user(
                account["_id"],
                {
                    "battle.battle.status": 2,
                    "battle.battle.rid": rival["_id"],
                    "battle.battle.round": 1,
                    "battle.battle.turn": rival["_id"],
                    "battle.battle.turn_started_at": now,
                    "battle.battle.finished": False
                }
            )

            await mongodb.update_user(
                rival["_id"],
                {
                    "battle.battle.status": 2,
                    "battle.battle.rid": account["_id"],
                    "battle.battle.round": 1,
                    "battle.battle.turn": rival["_id"],
                    "battle.battle.turn_started_at": now,
                    "battle.battle.finished": False
                }
            )



            if rival["_id"] != account["_id"] * 10:
                # записываем соперников друг другу
                await mongodb.add_recent_opponent(account["_id"], rival["_id"])
                await mongodb.add_recent_opponent(rival["_id"], account["_id"])

            if r_avatar_type == 'photo':
                await bot.send_photo(photo=r_avatar, chat_id=account["_id"], caption=user_text,
                                     reply_markup=reply_builder("🏴‍☠️ Сдаться"))
            else:
                await bot.send_animation(animation=r_avatar, chat_id=account["_id"], caption=user_text,
                                         reply_markup=reply_builder("🏴‍☠️ Сдаться"))

            if avatar_type == 'photo':
                await bot.send_photo(photo=avatar, chat_id=rival["_id"], caption=rival_text,
                                     reply_markup=reply_builder("🏴‍☠️ Сдаться"))
            else:
                await bot.send_animation(animation=avatar, chat_id=rival["_id"], caption=rival_text,
                                         reply_markup=reply_builder("🏴‍☠️ Сдаться"))

            await bot.send_message(account["_id"], text=f'.               ˗ˋˏ<tg-emoji emoji-id="5215480011322042129">❌</tg-emoji> Раунд 1ˎˊ˗'
                                                            # f"\n✧•───────────────────────•✧"
                                                            f'\n<blockquote expandable>{account_text(b_character)}</blockquote>'
                                                            # f"\n✧•──────────────•✧"
                                                            f'\n➖➖➖➖➖➖➖➖➖➖➖'
                                                            f'\n<blockquote expandable>{account_text(rb_character)}</blockquote>')

            await bot.send_message(rival["_id"],   text=f'.               ˗ˋˏ<tg-emoji emoji-id="5215480011322042129">❌</tg-emoji> Раунд 1ˎˊ˗'
                                                            # f"\n✧•───────────────────────•✧"
                                                            f'\n<blockquote expandable>{account_text(rb_character)}</blockquote>'
                                                            # f"\n✧•──────────────•✧"
                                                            f'\n➖➖➖➖➖➖➖➖➖➖➖'
                                                            f'\n<blockquote expandable>{account_text(b_character)}</blockquote>')

            await bot.send_message(account["_id"], text='Ход соперника <tg-emoji emoji-id="5010636296373142479">❌</tg-emoji>', reply_markup=abilities_kb(ability, hp=b_character.health, mana=b_character.mana, energy=b_character.energy))
            mes = await bot.send_message(rival["_id"], text=f'\n<tg-emoji emoji-id="5449372823476777969">❌</tg-emoji> Ваш ход:',
                                         reply_markup=abilities_kb(r_ability, hp=rb_character.health, mana=rb_character.mana, energy=rb_character.energy),
                                         parse_mode=ParseMode.HTML)

            # Запускаем таймер
            if rival["_id"] != account["_id"] * 10:
                await surrender_f(rival["_id"], rb_character.round, mes, bot)

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
                text='💢 Вы уже находитесь в битве!',
                show_alert=True
            )
        else:
            await callback.answer(
                text="💢 Вы уже находитесь в битве!",
                show_alert=True
            )


@router.message(ChatTypeFilter(chat_type=["private"]), Command("cancel"))
@router.message(F.text.lower().contains("✖️ отмена"))
async def cancel_search(message: Message):

    user_id = message.from_user.id
    account = await mongodb.get_user(user_id)

    if account["battle"]["battle"]["status"] in (1, 3):
        await mongodb.update_user(user_id, {"battle.battle.status": 0})
        await message.answer('<tg-emoji emoji-id="6037269274098143378">❌</tg-emoji> Поиск отменен', reply_markup=menu_button())
        await arena.arena(message)


@router.message(ChatTypeFilter(chat_type=["private"]), Command("surrender"))
@router.message(F.text == "🏴‍☠️ Сдаться")
async def surrender(message: Message, bot: Bot):
    user_id = message.from_user.id
    account = await mongodb.get_user(user_id)
    if account["battle"]["battle"].get("finished"):
        return
    rival = None

    if account["battle"]["battle"]["status"] in (2, 4):
        if account["battle"]["battle"]["rid"] != user_id * 10:
            rival = await mongodb.get_user(account["battle"]["battle"]["rid"])
        await bot.send_animation(chat_id=user_id, animation=lose_animation,
                                 caption=surrender_text, reply_markup=menu_button())

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
                                     caption=surrender_r_text, reply_markup=menu_button())


@router.message(ChatTypeFilter(chat_type=["private"]), F.text.startswith("˹"))
async def battle_message(message: Message, bot: Bot):
    user_id = message.from_user.id
    account = await mongodb.get_user(user_id)
    action = message.text.strip()  # <-- теперь это вместо callback.data

    battle = account.get("battle", {}).get("battle", {})

    if battle.get("status") != 2:
        return

    # --- LOCK ХОДА (идемпотентность) ---
    round_no = battle.get("round")
    lock_id = f"pvp:turn:{user_id}:{round_no}"

    # Достаём текущего персонажа боя из памяти
    character = battle_data.get(user_id)
    if not character:
        return  # или message.answer("Бой прерван") — как тебе нужно

    rival_character = battle_data.get(character.rid)
    if not rival_character:
        return

    # --- ПРОВЕРКА ОГЛУШЕНИЯ В НАЧАЛЕ ХОДА ---
    if character.stun > 0:
        await mongodb.db.once.delete_one({"_id": lock_id})
        await bot.send_message(
            user_id,
            '<tg-emoji emoji-id="5967744293425646719">💫</tg-emoji> Вы оглушены'
        )
        return

    if battle.get("turn") != user_id:
        await message.answer('<tg-emoji emoji-id="5307773751796964107">❌</tg-emoji> Сейчас не ваш ход')
        return

    is_first = await mongodb.claim_once(lock_id, user_id, ttl_sec=TURN_TIMEOUT)
    if not is_first:
        return

    if action not in character.ability:
        await mongodb.db.once.delete_one({"_id": lock_id})
        return

    if not character:
        await mongodb.db.once.delete_one({"_id": lock_id})
        await message.answer("〰️ Бой был прерван", reply_markup=menu_button())
        return

    # Нельзя ходить, если не в бою
    if account.get("battle", {}).get("battle", {}).get("status") != 2:
        await mongodb.db.once.delete_one({"_id": lock_id})
        await message.answer('<tg-emoji emoji-id="5931757621445924047">❌</tg-emoji> Сейчас нельзя ходить. Вы не в бою')
        return

    # Выполняем ход
    # ВАЖНО: если не хватит маны/энергии — снимаем блок, чтобы игрок мог выбрать другую кнопку.
    mana, energy = await characters.turn(character, bot, action, rival_character, 0)
    # КЛАМП ХП
    character.health = max(0, character.health)
    rival_character.health = max(0, rival_character.health)

    # === ПРОВЕРКА СМЕРТИ СРАЗУ ПОСЛЕ УДАРА ===
    if character.health <= 0 or rival_character.health <= 0:
        if character.round == rival_character.round:
            await mongodb.db.once.delete_one({"_id": lock_id})
        return

    if not mana or not energy:
        await mongodb.db.once.delete_one({"_id": lock_id})

        if not mana or not energy:
            if not mana:
                await message.answer('<tg-emoji emoji-id="6039884526929317741">❌</tg-emoji>Недостаточно маны <tg-emoji emoji-id="5794242604103110904">❌</tg-emoji>')
            elif not energy:
                await message.answer('<tg-emoji emoji-id="6039884526929317741">❌</tg-emoji>Недостаточно энергии <tg-emoji emoji-id="5371058888017715839">❌</tg-emoji>')
            return

    next_round = battle.get("round", 1) + 1
    now = datetime.utcnow()

    if rival_character.stun > 0:
        # 1) Списываем 1 "пропуск хода"
        rival_character.stun = max(0, rival_character.stun - 1)

        # 2) Ход остаётся у текущего игрока
        character.round = next_round
        rival_character.round = next_round

        await mongodb.update_user(
            user_id,
            {"battle.battle.round": character.round,
             "battle.battle.turn": character.ident,
             "battle.battle.turn_started_at": now}
        )
        if rival_character.ident != account["_id"] * 10:
            await mongodb.update_user(
                rival_character.ident,
                {"battle.battle.round": rival_character.round,
                 "battle.battle.turn": character.ident,
                 "battle.battle.turn_started_at": now}
            )
    else:

        # === ЕСЛИ НЕ ОГЛУШЁН — ОБЫЧНАЯ ПЕРЕДАЧА ХОДА ===
        character.round = next_round
        # rival_character.round = next_round

        await mongodb.update_user(
            character.ident,
            {
                "battle.battle.round": character.round,
                "battle.battle.turn": rival_character.ident,
                "battle.battle.turn_started_at": now
            }
        )

        await mongodb.update_user(
            rival_character.ident,
            {
                "battle.battle.round": rival_character.round,
                "battle.battle.turn": rival_character.ident,
                "battle.battle.turn_started_at": now
            }
        )

    battle_data[character.ident] = character
    battle_data[rival_character.ident] = rival_character

    async def send_round_photo():
        if account["battle"]["battle"].get("finished"):
            return

    # ЕСЛИ ХОД ПЕРЕДАН AI — ЗАПУСКАЕМ ЕГО
    if rival_character.ident == character.ident * 10:
        ai_character = battle_data.get(rival_character.ident)
        if ai_character:
            await asyncio.sleep(1)
            await ai(ai_character, bot, None, account)
        await mongodb.db.once.delete_one({"_id": lock_id})
        return

    # ЕСЛИ ХОД ПЕРЕДАН ЖИВОМУ СОПЕРНИКУ — ПРОВЕРЯЕМ ЕГО СТАТУС И ЛОГИРУЕМ ХОД
    if rival_character.ident != character.ident * 10:
        # защита от гонки (на случай, если соперник уже вышел из боя или сдался к моменту хода игрока)
        if account["battle"]["battle"]["status"] != 2:
            await mongodb.db.once.delete_one({"_id": lock_id})
            return
        if character.round == rival_character.round:

            user_txt = (
                f'.               ˗ˋˏ<tg-emoji emoji-id="5215480011322042129">❌</tg-emoji> Раунд {character.round}ˎˊ˗'
                f'\n<blockquote expandable>{account_text(character)}</blockquote>'
                f'\n➖➖➖➖➖➖➖➖➖➖➖'
                f'\n<blockquote expandable>{account_text(rival_character)}</blockquote>')

            rival_txt = (f'.               ˗ˋˏ<tg-emoji emoji-id="5215480011322042129">❌</tg-emoji> Раунд {rival_character.round}ˎˊ˗'
                         f'\n<blockquote expandable>{account_text(rival_character)}</blockquote>'
                         f'\n➖➖➖➖➖➖➖➖➖➖➖'
                         f'\n<blockquote expandable>{account_text(character)}</blockquote>')

            await bot.send_message(
                chat_id=user_id,
                text=user_txt
            )

            await bot.send_message(
                chat_id=rival_character.ident,
                text=rival_txt

            )

        if rival_character.stun > 0:

            await bot.send_message(
                rival_character.ident,
                text='Ход соперника <tg-emoji emoji-id="5010636296373142479">❌</tg-emoji>',
                reply_markup=abilities_kb(
                    rival_character.ability,
                    hp=rival_character.health,
                    mana=rival_character.mana,
                    energy=rival_character.energy
                )
            )

            mes = await bot.send_message(
                chat_id=user_id,
                text='\n<tg-emoji emoji-id="5449372823476777969">❌</tg-emoji> Ваш ход:',
                reply_markup=abilities_kb(
                    character.ability,
                    hp=character.health,
                    mana=character.mana,
                    energy=character.energy
                )
            )

        else:
            mes = await bot.send_message(
                rival_character.ident,
                text='\n<tg-emoji emoji-id="5449372823476777969">❌</tg-emoji> Ваш ход:',
                reply_markup=abilities_kb(
                    rival_character.ability,
                    hp=rival_character.health,
                    mana=rival_character.mana,
                    energy=rival_character.energy
                )
            )

            await bot.send_message(
                chat_id=user_id,
                text='Ход соперника <tg-emoji emoji-id="5010636296373142479">❌</tg-emoji>',
                reply_markup=abilities_kb(
                    character.ability,
                    hp=character.health,
                    mana=character.mana,
                    energy=character.energy
                )
            )

        await mongodb.db.once.delete_one({"_id": lock_id})

        if rival_character.ident != account["_id"] * 10:
            await surrender_f(rival_character.ident, next_round, mes, bot)

    now = datetime.utcnow()

    # ----- ВАША ИСХОДНАЯ ЛОГИКА ФИНАЛОВ/РАУНДОВ -----
    if character.health <= 0 and rival_character.health <= 0:
        if character.round == rival_character.round:
            await mongodb.db.once.delete_one({"_id": lock_id})

            await bot.send_animation(
                chat_id=user_id,
                animation=draw_animation,
                caption=draw_text,
                reply_markup=menu_button()
            )
            if rival_character.ident != character.ident * 10:
                await bot.send_animation(
                    chat_id=rival_character,
                    animation=draw_animation,
                    caption=draw_text,
                    reply_markup=menu_button()
                )

            await mongodb.update_ops(account["_id"], {
                "$set": {
                    "battle.battle.finished": True,
                    "battle.battle.status": 0,
                    "battle.battle.rid": "",
                    "tasks.last_arena_fight": now,
                },
                "$inc": {
                    "battle.stats.ties": 1,
                    "stats.exp": 80,
                    "account.money": 150,
                }
            })

            await mongodb.update_ops(rival_character.ident, {
                "$set": {"battle.battle.finished": True}  # если тебе нужно отдельно — но можно тоже всё сразу
            })

            if rival_character.ident != character.ident * 10:
                await mongodb.update_ops(character.rid, {
                    "$set": {
                        "battle.battle.finished": True,
                        "battle.battle.status": 0,
                        "battle.battle.rid": "",
                        "tasks.last_arena_fight": now,
                    },
                    "$inc": {
                        "battle.stats.ties": 1,
                        "stats.exp": 80,
                        "account.money": 150,
                    }
                })

                battle_data.pop(character.rid, None)
            else:
                battle_data.pop(character.ident * 10, None)
            battle_data.pop(account["_id"], None)

        else:
            await asyncio.sleep(1)
            await send_round_photo()

    elif character.health <= 0:
        if character.round == rival_character.round:
            await mongodb.db.once.delete_one({"_id": lock_id})

            await bot.send_animation(
                chat_id=user_id,
                animation=lose_animation,
                caption=lose_text,
                reply_markup=menu_button()
            )
            if rival_character.ident != character.ident * 10:
                await bot.send_animation(
                    chat_id=character.rid,
                    animation=lose_animation,
                    caption=win_text,
                    reply_markup=menu_button()
                )

            await mongodb.update_ops(account["_id"], {
                "$set": {
                    "battle.battle.finished": True,
                    "battle.battle.status": 0,
                    "battle.battle.rid": "",
                    "tasks.last_arena_fight": now,
                },
                "$inc": {
                    "battle.stats.loses": 1,
                    "stats.exp": 55,
                    "account.money": 100,
                }
            })

            if rival_character.ident != character.ident * 10:
                await mongodb.update_ops(character.rid, {
                    "$set": {
                        "battle.battle.finished": True,
                        "battle.battle.status": 0,
                        "battle.battle.rid": "",
                        "tasks.last_arena_fight": now,
                    },
                    "$inc": {
                        "battle.stats.wins": 1,
                        "stats.exp": 100,
                        "account.money": 200,
                    }
                })

                battle_data.pop(character.rid, None)
            else:
                battle_data.pop(character.ident * 10, None)
            battle_data.pop(account["_id"], None)

        else:
            await asyncio.sleep(1)
            await send_round_photo()

    elif rival_character.health <= 0:
        if character.round == rival_character.round:
            await mongodb.db.once.delete_one({"_id": lock_id})

            await bot.send_animation(
                chat_id=user_id,
                animation=win_animation,
                caption=win_text,
                reply_markup=menu_button()
            )
            if rival_character.ident != character.ident * 10:
                await bot.send_animation(
                    chat_id=character.rid,
                    animation=lose_animation,
                    caption=lose_text,
                    reply_markup=menu_button()
                )

            await mongodb.update_ops(account["_id"], {
                "$set": {
                    "battle.battle.finished": True,
                    "battle.battle.status": 0,
                    "battle.battle.rid": "",
                    "tasks.last_arena_fight": now,
                },
                "$inc": {
                    "battle.stats.wins": 1,
                    "stats.exp": 100,
                    "account.money": 200,
                }
            })

            if rival_character.ident != character.ident * 10:
                await mongodb.update_ops(character.rid, {
                    "$set": {
                        "battle.battle.finished": True,
                        "battle.battle.status": 0,
                        "battle.battle.rid": "",
                        "tasks.last_arena_fight": now,
                    },
                    "$inc": {
                        "battle.stats.loses": 1,
                        "stats.exp": 55,
                        "account.money": 100,
                    }
                })

                battle_data.pop(character.rid, None)
            else:
                battle_data.pop(character.ident * 10, None)
            battle_data.pop(account["_id"], None)

        else:
            await asyncio.sleep(1)
            await send_round_photo()

    else:
        await asyncio.sleep(1)
        await send_round_photo()
