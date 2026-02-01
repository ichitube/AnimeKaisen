"""
from aiogram import Router, F

from aiogram.types import CallbackQuery, Message, InputMediaPhoto
from aiogram.filters import Command
from aiogram.enums import ParseMode

from keyboards.builders import reply_builder, main_menu_button, inline_builder, menu_button
from filters.chat_type import ChatTypeFilter
from recycling import profile
from routers import main_menu
from data import characters, character_photo
from data import mongodb
from data.mongodb import db

router = Router()

round_photo = "AgACAgIAAx0CfstymgACCxll6jkC8aLSgDmD1mPEvcXdHcsvTQACptoxG6bRUEuafYTvY5hVygEAAwIAA3gAAzQE"

battle_data = {}


@router.message(Command("post"))
async def fill_profile(message: Message):
    if message.from_user.id == 6946183730:
        async def forward_post_to_all_users(channel_id, message_id):
            users = db.users.find()  # замените 'users' на имя вашей коллекции пользователей
            async for user in users:
                try:
                    await bot.forward_message(chat_id=user['_id'], from_chat_id=channel_id, message_id=message_id)
                except Exception as e:
                    print(f"Не удалось переслать сообщение пользователю {user['_id']}: {e}")

        await forward_post_to_all_users(channel_id=-1002042458477, message_id=23)
    else:
        await message.answer("У вас нет прав на выполнение этой команды")


@router.message(
    ChatTypeFilter(chat_type=["private"]),
    F.text == "🏟️ Арена"
)
@router.callback_query(F.data == "arena")
async def arena(callback: CallbackQuery | Message):
    account = await mongodb.get_user(callback.from_user.id)
    await profile.update_rank(callback.from_user.id, account["battle"]["stats"]['wins'])

    rank = await profile.rerank(account['stats']['rank'])
    in_battle = await mongodb.in_battle()
    universe = account['universe']
    character = account['character'][account['universe']]
    exp = account['stats']['exp']
    wins = account['battle']['stats']['wins']
    strength = character_photo.get_stats(universe, character, 'arena')['strength']
    agility = character_photo.get_stats(universe, character, 'arena')['agility']
    intelligence = character_photo.get_stats(universe, character, 'arena')['intelligence']
    ability = character_photo.get_stats(universe, character, 'arena')['ability']
    power = character_photo.get_stats(universe, character, 'arena')['power']

    skills = '\n'
    for skill in ability:
        skills += skill + '\n'

    pattern = dict(
        caption=f"❖  🏟️  <b>Арена</b>  ⚔️"
                f"\n── •✧✧• ──────────"
                f"\n❖🎴 <b>{character}</b>"
                f"\n❖🎐 <b>{rank}</b>"
                f"\n\n   ✊🏻 Сила: {strength}"
                f"\n   👣 Ловкость: {agility}"
                f"\n   🧠 Интелект: {intelligence}"
                f"\n   ⚜️ Мощь: {power}"
                f"\n{skills} "
                f"\n 👑 {wins} Побед | 🀄️ {exp} XP"
                f"\n── •✧✧• ──────────"
                f"\n<i>🌊 В битве ⚔️ {in_battle} игроков</i> 🌊",
        parse_mode=ParseMode.HTML,
        reply_markup=inline_builder(
            ["⚔️ Битва", "🎴 Навыки", "🏆 Рейтинг", "📜 Правила", "🔙 Назад"],
            ["search_opponent", "ch_info", "battle_rating", "battle_rules", "main_page"],
            row_width=[1, 2, 2])
    )

    if isinstance(callback, CallbackQuery):
        media = InputMediaPhoto(
            media='AgACAgIAAx0CfstymgACBaJly1EK8HvqMmJjmPe7B4Uf4uiDHAACldcxG1pyWEqTZtRfQzuM-gEAAwIAA3kAAzQE'
        )
        await callback.message.edit_media(media)
        await callback.message.edit_caption(**pattern)
    else:
        media = 'AgACAgIAAx0CfstymgACBaJly1EK8HvqMmJjmPe7B4Uf4uiDHAACldcxG1pyWEqTZtRfQzuM-gEAAwIAA3kAAzQE'
        await callback.answer_photo(media, **pattern)


@router.callback_query(F.data == "search_opponent")
async def search_opponent(callback: CallbackQuery):
    await callback.message.delete()
    user_id = callback.from_user.id
    account = await mongodb.get_user(user_id)

    if account["battle"]["battle"]["status"] == 0:
        rival = await mongodb.find_opponent()

        await mongodb.update_user(user_id, {"battle.battle.status": 1})

        if rival is None:
            await bot.send_animation(
                user_id, animation="CgACAgIAAx0CfstymgACBaNly1ESV41gB1s-k4M3VITaGbHvHwACPj8AAlpyWEpUUFtvRlRcpjQE",
                caption=f"\n── •✧✧• ──────────"
                f"\n❖ 🔎 Поиск соперника . . . . .", reply_markup=reply_builder("✖️ Отмена"))
        else:

            universe = account['universe']
            character = account['character'][account['universe']]
            avatar = character_photo.get_stats(universe, character, 'avatar')
            avatar_type = character_photo.get_stats(universe, character, 'type')
            rarity = character_photo.get_stats(universe, character, 'rarity')
            strength = character_photo.get_stats(universe, character, 'arena')['strength']
            agility = character_photo.get_stats(universe, character, 'arena')['agility']
            intelligence = character_photo.get_stats(universe, character, 'arena')['intelligence']
            ability = character_photo.get_stats(universe, character, 'arena')['ability']
            power = character_photo.get_stats(universe, character, 'arena')['power']

            shield, stun, p_passive, n_passive = 0, 0, 0, 0
            passive = []
            health = strength * 50
            attack = strength + agility + (intelligence // 2)
            defense = (strength + agility + (intelligence // 2)) // 4
            mana = intelligence * 10
            crit_dmg = strength + (strength // 2) + (intelligence // 4)
            crit_ch = agility + (strength // 2) + (intelligence // 4)

            b_character = characters.Character(character, strength, agility, intelligence, shield, stun, p_passive,
                                               n_passive, passive, health, attack, defense, mana, crit_dmg, crit_ch)

            character_data = {
                "id": account["_id"],
                "name": account["name"],
                "character": b_character.name,
                "strength": b_character.strength,
                "agility": b_character.agility,
                "intelligence": b_character.intelligence,
                "shield": b_character.shield,
                "stun": b_character.stun,
                "p_passive": b_character.p_passive,
                "n_passive": b_character.n_passive,
                "passive": b_character.passive,
                "health": b_character.health,
                "attack": b_character.attack,
                "defense": b_character.defense,
                "mana": b_character.mana,
                "crit_dmg": b_character.crit_dmg,
                "crit_ch": b_character.crit_ch,
                "abilities": ability,
                "round": 1,
                "turn": False,
                "rid": rival["_id"]
            }

            battle_data[account["_id"]] = character_data

            skills = '\n'
            for skill in ability:
                skills += skill + '\n'

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

            r_health = r_strength * 50
            r_attack = r_strength + r_agility + (r_intelligence // 2)
            r_defense = (r_strength + r_agility + (r_intelligence // 2)) // 4
            r_mana = r_intelligence * 10
            r_crit_dmg = r_strength + (r_strength // 2) + (r_intelligence // 4)
            r_crit_ch = r_agility + (r_strength // 2) + (r_intelligence // 4)

            rb_character = characters.Character(
                r_character, r_strength, r_agility, r_intelligence, shield, stun, p_passive, n_passive, passive,
                r_health, r_attack, r_defense, r_mana, r_crit_dmg, r_crit_ch)

            r_character_data = {
                "id": rival["_id"],
                "name": rival["name"],
                "character": rb_character.name,
                "strength": rb_character.strength,
                "agility": rb_character.agility,
                "intelligence": rb_character.intelligence,
                "shield": rb_character.shield,
                "stun": rb_character.stun,
                "p_passive": rb_character.p_passive,
                "n_passive": rb_character.n_passive,
                "passive": rb_character.passive,
                "health": rb_character.health,
                "attack": rb_character.attack,
                "defense": rb_character.defense,
                "mana": rb_character.mana,
                "crit_dmg": rb_character.crit_dmg,
                "crit_ch": rb_character.crit_ch,
                "abilities": r_ability,
                "round": 1,
                "turn": False,
                "rid": account["_id"]
            }

            battle_data[rival["_id"]] = r_character_data

            r_skills = '\n'
            for r_skill in r_ability:
                r_skills += r_skill + '\n'

            user_text = (f" ⚔️ Cоперник Найден! "
                         f"\n── •✧✧• ──────────"
                         f"\n 🪪  〢 {rival['name']} "
                         f"\n── •✧✧• ──────────"
                         f"\n❖ ✨ Редкость: {r_rarity}"
                         f"\n❖ 🗺 Вселенная: {r_universe}"
                         f"\n\n   ✊🏻 Сила: {r_strength}"
                         f"\n   👣 Ловкость: {r_agility}"
                         f"\n   🧠 Интелект: {r_intelligence}"
                         f"\n   ⚜️ Мощь: {r_power}"
                         f"\n{r_skills} "
                         f"\n── •✧✧• ──────────"
                         f"\n<i>🀄️ Опыт: {rival['stats']['exp']} XP </i>")

            rival_text = (f"⚔️ Cоперник Найден! "
                          f"\n── •✧✧• ──────────"
                          f"\n 🪪  〢 {account['name']} "
                          f"\n── •✧✧• ──────────"
                          f"\n❖ ✨ Редкость: {rarity}"
                          f"\n❖ 🗺 Вселенная: {universe}"
                          f"\n\n   ✊🏻 Сила: {strength}"
                          f"\n   👣 Ловкость: {agility}"
                          f"\n   🧠 Интелект: {intelligence}"
                          f"\n   ⚜️ Мощь: {power}"
                          f"\n{skills} "
                          f"\n── •✧✧• ──────────"
                          f"\n<i>🀄️ Опыт: {account['stats']['exp']} XP </i>")

            await mongodb.update_user(account["_id"], {"battle.battle.status": 2, "battle.battle.rid": rival["_id"]})
            await mongodb.update_user(rival["_id"], {"battle.battle.status": 2, "battle.battle.rid": account["_id"]})

            if r_avatar_type == 'photo':
                await bot.send_photo(photo=r_avatar, chat_id=account["_id"], caption=user_text,
                                     reply_markup=reply_builder("🏴‍☠️ Покинут бой"))
            else:
                await bot.send_animation(animation=r_avatar, chat_id=account["_id"], caption=user_text,
                                         reply_markup=reply_builder("🏴‍☠️ Покинут бой"))

            if avatar_type == 'photo':
                await bot.send_photo(photo=avatar, chat_id=rival["_id"], caption=rival_text,
                                     reply_markup=reply_builder("🏴‍☠️ Покинут бой"))
            else:
                await bot.send_animation(animation=avatar, chat_id=rival["_id"], caption=rival_text,
                                         reply_markup=reply_builder("🏴‍☠️ Покинут бой"))

            if avatar_type == 'photo':
                await bot.send_photo(account["_id"], photo=round_photo,
                                     caption=f"❖ 🏟 {account['name']} ⚔️ {rival['name']}"
                                             f"\n── •✧✧• ──────────"
                                             f"\n ⏳ Раунд 1"
                                             f"\n\n   ✊🏻 Сила: {strength}"
                                             f"\n   👣 Ловкость: {agility}"
                                             f"\n   🧠 Интелект: {intelligence}"
                                             f"\n\nЗдоровье: {b_character.health}"
                                             f"\nАтака: {b_character.attack}"
                                             f"\nЗащита: {b_character.defense}"
                                             f"\nМана: {b_character.mana}"
                                             f"\nКрит. урон: {b_character.crit_dmg}"
                                             f"\nКрит. шанс: {b_character.crit_ch}"
                                             f"\n\nПассивки: "
                                             f"\n── •✧✧• ──────────"
                                             f"\n🔸 Ждем хода соперника: ",
                                     parse_mode=ParseMode.HTML)

            await bot.send_photo(rival["_id"], photo=round_photo,
                                 caption=f"❖ 🏟 {rival['name']} ⚔️ {account['name']}"
                                         f"\n── •✧✧• ──────────"
                                         f"\n ⏳ Раунд 1"
                                         f"\n\n   ✊🏻 Сила: {r_strength}"
                                         f"\n   👣 Ловкость: {r_agility}"
                                         f"\n   🧠 Интелект: {r_intelligence}"
                                         f"\n\nЗдоровье: {rb_character.health}"
                                         f"\nАтака: {rb_character.attack}"
                                         f"\nЗащита: {rb_character.defense}"
                                         f"\nМана: {rb_character.mana}"
                                         f"\nКрит. урон: {rb_character.crit_dmg}"
                                         f"\nКрит. шанс: {rb_character.crit_ch}"
                                         f"\n\nПассивки: "
                                         f"\n── •✧✧• ──────────"
                                         f"\n🔸 Ваш ход: ",
                                 reply_markup=inline_builder(r_ability, r_ability, row_width=[2, 2]),
                                 parse_mode=ParseMode.HTML)

    elif account["battle"]["battle"]["status"] == 1:
        await callback.answer(
            text="💢 Вы уже находитесь в поиске соперника!",
            show_alert=True
        )

    elif account["battle"]["battle"]["status"] == 2:
        await callback.answer(
            text="💢 Вы уже находитесь в битве!",
            show_alert=True
        )


@router.message(F.text.lower().contains("✖️ отмена"))
async def cancel_search(message: Message):

    user_id = message.from_user.id
    account = await mongodb.get_user(user_id)

    if account["battle"]["battle"]["status"] == 1:
        await mongodb.update_user(user_id, {"battle.battle.status": 0})
        await message.answer("✖️ Поиск отменен", reply_markup=menu_button())
        await main_menu.main_menu(message)


@router.message(F.text == "🏴‍☠️ Покинут бой")
async def surrender(message: Message):

    user_id = message.from_user.id
    account = await mongodb.get_user(user_id)

    if account["battle"]["battle"]["status"] == 2:
        media = "CgACAgIAAx0CfstymgACBbRlzDgYWpgLO50Lgeg0HImQEC9GEAAC7D4AAsywYUo5sbjTkVkCRjQE"
        rival = await mongodb.get_user(account["battle"]["battle"]["rid"])
        await message.answer("🏴‍☠️ Ты покинул битву", reply_markup=menu_button())

        await mongodb.update_many(
            {"_id": {"$in": [account["_id"]]}},
            {"$set": {"battle.battle.status": 0, "battle.battle.rid": ""}}
        )
        await mongodb.update_many(
            {"_id": {"$in": [rival["_id"]]}},
            {"$set": {"battle.battle.status": 0, "battle.battle.rid": ""}}
        )
        await main_menu.main_menu(message)
        await bot.send_message(rival["_id"], "🏴‍☠️ Соперник покинул битву", reply_markup=menu_button())
        await bot.send_animation(rival["_id"], animation=media, caption="✖️ Бой окончен. Ты сражался достойно.",
                                 reply_markup=main_menu_button())


@router.callback_query(F.data.startswith("˹"))
async def battle(callback: CallbackQuery):

    action = callback.data
    # Словарь для сопоставления имен персонажей и классов
    await bot.edit_message_reply_markup(callback.from_user.id, callback.message.message_id)
    user_id = callback.from_user.id
    account = await mongodb.get_user(user_id)

    character_d = battle_data.get(account["_id"])
    r_character_d = battle_data.get(character_d["rid"])

    character = characters.Character(
        character_d['character'], character_d['strength'], character_d['agility'], character_d['intelligence'],
        character_d['shield'], character_d['stun'], character_d['p_passive'], character_d['n_passive'],
        character_d['passive'], character_d['health'], character_d['attack'], character_d['defense'],
        character_d['mana'], character_d['crit_dmg'], character_d['crit_ch'])

    r_character = characters.Character(
        r_character_d['character'], r_character_d['strength'], r_character_d['agility'], r_character_d['intelligence'],
        r_character_d['shield'], r_character_d['stun'], r_character_d['p_passive'], r_character_d['n_passive'],
        r_character_d['passive'], r_character_d['health'], r_character_d['attack'], r_character_d['defense'],
        r_character_d['mana'], r_character_d['crit_dmg'], r_character_d['crit_ch'])

    if account["battle"]["battle"]["status"] == 2:
        if character_d["turn"]:
            return await bot.send_message(user_id, "✖️ Вы уже сделали ход!")

        await character.turn(bot, user_id, character_d["rid"], action, r_character)

        account_text = (f"        {account['character'][account['universe']]}"
                        f"\n\n❤️{character.health}"
                        f" 🗡{character.attack}"
                        f" 🛡{character.defense}"
                        f" 🧪{character.mana}"
                        f"\n🩸Кр. ур: {character.crit_dmg}"
                        f" 🩸Кр. шанс: {character.crit_ch}"
                        f"\n\n✊🏻Сл: {character.strength}"
                        f" 👣Лв: {character.agility}"
                        f" 🧠Ин: {character.intelligence}"
                        f"\n\n❤️‍🔥Пассивки: {character.passive}")
        rival_text = (f"        {r_character.name}"
                      f"\n\n❤️{r_character.health}"
                      f" 🗡{r_character.attack}"
                      f" 🛡{r_character.defense}"
                      f" 🧪{r_character.mana}"
                      f"\n🩸Кр. ур: {r_character.crit_dmg}"
                      f" 🩸Кр. шанс: {r_character.crit_ch}"
                      f"\n\n✊🏻Сл: {r_character.strength}"
                      f" 👣Лв: {r_character.agility}"
                      f" 🧠Ин: {r_character.intelligence}"
                      f"\n\n❤️‍🔥Пассивки: {r_character.passive}")

        async def send_round_photo():
            await bot.send_message(user_id,
                                   text=f".            ˗ˋˏ<tg-emoji emoji-id="5215480011322042129">❌</tg-emoji> Раунд {r_character_d['round']}ˎˊ˗"
                                        f"\n✧•────────────────•✧"
                                        f"\n{account_text}"
                                        f"\n✧•────────────────•✧"
                                        f"\n{rival_text}"
                                        f"\n✧•────────────────•✧"
                                        f"\n⏳ Ждём соперника...",
                                   parse_mode=ParseMode.HTML)
            await bot.send_message(r_character_d["id"],
                                   text=f".            ˗ˋˏ<tg-emoji emoji-id="5215480011322042129">❌</tg-emoji> Раунд {r_character_d['round']}ˎˊ˗"
                                        f"\n✧•────────────────•✧"
                                        f"\n{rival_text}"
                                        f"\n✧•────────────────•✧"
                                        f"\n{account_text}"
                                        f"\n✧•────────────────•✧"
                                        f"\n🔸 Ваш ход",
                                   reply_markup=inline_builder(r_character_d['abilities'], r_character_d['abilities'],
                                   row_width=[2, 2]),
                                   parse_mode=ParseMode.HTML)

        if character.health <= 0 and r_character.health <= 0:
            media = "CgACAgIAAx0CfstymgACBbRlzDgYWpgLO50Lgeg0HImQEC9GEAAC7D4AAsywYUo5sbjTkVkCRjQE"
            await bot.send_message(chat_id=user_id, text="☠️ Ничья! + 80🀄️ очки опыта", reply_markup=menu_button())
            await bot.send_animation(chat_id=user_id, animation=media, caption="✖️ Бой окончен. Ты сражался достойно",
                                     reply_markup=main_menu_button())
            await bot.send_message(chat_id=r_character, text="☠️ Ничья! + 80🀄️ очки опыта",
                                   reply_markup=menu_button())
            await bot.send_animation(chat_id=character_d["rid"], animation=media,
                                     caption="✖️ Бой окончен. Ты сражался достойно",
                                     reply_markup=main_menu_button())

            await mongodb.update_many(
                {"_id": {"$in": [account["_id"], character_d["rid"]]}},
                {"$set": {"battle.battle.status": 0, "battle.battle.rid": ""}}
            )

            await mongodb.update_many(
                {"_id": {"$in": [account["_id"], character_d["rid"]]}},
                {"$inc": {"stats.exp": 80, "battle.stats.ties": 1}}
            )

        elif character.health <= 0:
            if character_d["round"] != r_character_d["round"]:
                media = "CgACAgIAAx0CfstymgACBbRlzDgYWpgLO50Lgeg0HImQEC9GEAAC7D4AAsywYUo5sbjTkVkCRjQE"
                await bot.send_message(chat_id=user_id, text="💀 Поражение. + 55🀄️ очки опыта",
                                       reply_markup=menu_button())
                await bot.send_animation(chat_id=user_id, animation=media,
                                         caption="✖️ Бой окончен. Ты сражался достойно",
                                         reply_markup=main_menu_button())
                await bot.send_message(chat_id=character_d["rid"], text="👑 Победа. + 100🀄️ очки опыта",
                                       reply_markup=menu_button())
                await bot.send_animation(chat_id=character_d["rid"], animation=media,
                                         caption="✖️ Бой окончен. Ты сражался достойно",
                                         reply_markup=main_menu_button())

                await mongodb.update_many(
                    {"_id": {"$in": [account["_id"], character_d["rid"]]}},
                    {"$set": {"battle.battle.status": 0, "battle.battle.rid": ""}}
                )

                await mongodb.update_value(account["_id"], {"battle.stats.loses": 1})
                await mongodb.update_value(account["_id"], {"stats.exp": 55})
                await mongodb.update_value(character_d["rid"], {"battle.stats.wins": 1})
                await mongodb.update_value(character_d["rid"], {"stats.exp": 100})

            else:
                await send_round_photo()

        elif r_character.health <= 0:
            if character_d["round"] != r_character_d["round"]:
                media = "CgACAgIAAx0CfstymgACBbRlzDgYWpgLO50Lgeg0HImQEC9GEAAC7D4AAsywYUo5sbjTkVkCRjQE"
                await bot.send_message(chat_id=character_d["rid"], text="💀 Поражение. + 55🀄️ очки опыта",
                                       reply_markup=menu_button())
                await bot.send_animation(chat_id=character_d["rid"], animation=media,
                                         caption="✖️ Бой окончен. Ты сражался достойно",
                                         reply_markup=main_menu_button())
                await bot.send_message(chat_id=user_id, text="👑 Победа. + 100🀄️ очки опыта",
                                       reply_markup=menu_button())
                await bot.send_animation(chat_id=user_id, animation=media,
                                         caption="✖️ Бой окончен. Ты сражался достойно",
                                         reply_markup=main_menu_button())

                await mongodb.update_many(
                    {"_id": {"$in": [account["_id"], character_d["rid"]]}},
                    {"$set": {"battle.battle.status": 0, "battle.battle.rid": ""}}
                )

                await mongodb.update_value(character_d["rid"], {"battle.stats.loses": 1})
                await mongodb.update_value(character_d["rid"], {"stats.exp": 55})
                await mongodb.update_value(account["_id"], {"battle.stats.wins": 1})
                await mongodb.update_value(account["_id"], {"stats.exp": 100})

            else:
                await send_round_photo()

        else:
            await send_round_photo()

        character_stats = {
            "id": account["_id"],
            "name": account["name"],
            "character": character.name,
            "strength": character.strength,
            "agility": character.agility,
            "intelligence": character.intelligence,
            "shield": character.shield,
            "stun": character.stun,
            "p_passive": character.p_passive,
            "n_passive": character.n_passive,
            "passive": character.passive,
            "health": character.health,
            "attack": character.attack,
            "defense": character.defense,
            "mana": character.mana,
            "crit_dmg": character.crit_dmg,
            "crit_ch": character.crit_ch,
            "abilities": character_d["abilities"],
            "round": character_d["round"] + 1,
            "turn": True,
            "rid": character_d["rid"]

        }

        r_character_stats = {
            "id": r_character_d["id"],
            "name": r_character_d["name"],
            "character": r_character.name,
            "strength": r_character.strength,
            "agility": r_character.agility,
            "intelligence": r_character.intelligence,
            "shield": r_character.shield,
            "stun": r_character.stun,
            "p_passive": r_character.p_passive,
            "n_passive": r_character.n_passive,
            "passive": r_character.passive,
            "health": r_character.health,
            "attack": r_character.attack,
            "defense": r_character.defense,
            "mana": r_character.mana,
            "crit_dmg": r_character.crit_dmg,
            "crit_ch": r_character.crit_ch,
            "abilities": r_character_d["abilities"],
            "round": r_character_d["round"],
            "turn": False,
            "rid": r_character_d["rid"]
        }

        battle_data[account["_id"]] = character_stats
        battle_data[character_d["rid"]] = r_character_stats
"""