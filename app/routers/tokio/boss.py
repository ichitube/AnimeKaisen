from datetime import datetime, timedelta
from aiogram import Router, F, Bot
from contextlib import suppress
import asyncio

from aiogram.types import CallbackQuery, InputMediaAnimation, InputMediaPhoto, Message
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext

from app.data import mongodb, card_characters
from app.data import character_photo
from app.filters.chat_type import ChatTypeFilter
from app.data.character_photo import get_stats
from app.keyboards.builders import inline_builder, Pagination, pagination_boss

router = Router()

battle_data = []
user_data = []

BOSSES = [
    {"name": "🐉 Шадрагон", "hp": 100000, "damage": 1000, 'class': 'strength', 'defense': 20, "strength": 100,
     "agility": 75, "intelligence": 75, "ability": "🔥 Огненное дыхание",
     "avatar": "CgACAgIAAx0CfstymgACPolna-3ni4cLL39VwuvlFiUQ8kQVVgACMmMAArowYUshoYqGQ-S3bjYE"},
    {"name": "🐉 Омракс", "hp": 100000, "damage": 1000, 'class': 'agility', 'defense': 20, "strength": 75,
     "agility": 100, "intelligence": 75, "ability": "🌪 Торнадо",
     "avatar": "CgACAgIAAx0CfstymgACPn9na-1_e8cHSYA29Plm6gXFgBkzjQACK2MAArowYUsztOi5fvuTOTYE"},
    {"name": "🐉 Фиргарт", "hp": 100000, "damage": 1000, 'class': 'agility', 'defense': 20, "strength": 100,
     "agility": 75, "intelligence": 75, "ability": "◾️ Тёмная энергия",
     "avatar": "CgACAgIAAx0CfstymgACPoFna-2Pk-zLkdcvwZwTGyhajxslTQACLGMAArowYUvGtG_zdydYBjYE"},
    {"name": "🐉 Игниссер", "hp": 100000, "damage": 1000, 'class': 'intelligence', 'defense': 20, "strength": 100,
     "agility": 75, "intelligence": 75, "ability": "❄️ Ледяное дыхание",
     "avatar": "CgACAgIAAx0CfstymgACPndna-1PLFQrktyzqXUn-HhjY_NWagACI2MAArowYUu5DkXp68OLyjYE"},
    {"name": "🐉 Блейзрон", "hp": 100000, "damage": 1000, 'class': 'agility', 'defense': 20, "strength": 100,
     "agility": 75, "intelligence": 75, "ability": "◾️ Тёмный огонь",
     "avatar": "CgACAgIAAx0CfstymgACPn1na-1wj7ZjkXLLICHpUX4O9njL6QACJ2MAArowYUsKQNL5XBCDUTYE"},
    {"name": "🐉 Элдора", "hp": 100000, "damage": 1000, 'class': 'strength', 'defense': 20, "strength": 100,
     "agility": 75, "intelligence": 75, "ability": "🔥 Горячая лава",
     "avatar": "CgACAgIAAx0CfstymgACPoVna-2403qkX-omvqibT9DG4V5ACAACMGMAArowYUv3_Hw6LwtDXDYE"},
    {"name": "🐉 Эмберус", "hp": 100000, "damage": 1000, 'class': 'strength', 'defense': 20, "strength": 100,
     "agility": 75, "intelligence": 75, "ability": "⚡️ Чёрная молния",
     "avatar": "CgACAgIAAx0CfstymgACPoNna-2y5pckqJnzoK_D2h0cUUOJ1AACL2MAArowYUuiG_oGnCGt6zYE"},
    {"name": "🐉 Скайдрис", "hp": 100000, "damage": 1000, 'class': 'intelligence', 'defense': 20, "strength": 100,
     "agility": 75, "intelligence": 75, "ability": "☁️ Тёмная буря",
     "avatar": "CgACAgIAAx0CfstymgACPnVna-1Dhde65Wyr4GgklR1koBsNlgACIWMAArowYUtlr8P-LuT-dTYE"},
    {"name": "👺 Фэйрвин", "hp": 100000, "damage": 1000, 'class': 'strength', 'defense': 20, "strength": 100,
     "agility": 75, "intelligence": 75, "ability": "☄️ Огненный шар",
     "avatar": "CgACAgIAAx0CfstymgACPntna-1p3n5rFymAE88EEy20FWeipAACJmMAArowYUv9rKj5HJGmRDYE"},
]


@router.message(ChatTypeFilter(chat_type=["private"]), F.text == "🐦‍🔥Босс")
@router.callback_query(F.data == "boss")
async def boss_func(callback: CallbackQuery | Message, account: dict = None, user_id: int = None):
    if user_id is None:
        user_id = callback.from_user.id
    if account is None:
        account = await mongodb.get_user(user_id)

    # Текущее время
    current_datetime = datetime.now()
    if 'boss' not in account:
        # Если босса нет, создаем его
        account['boss'] = {
            "boss_id": 0,
            "name": BOSSES[0]["name"],
            "current_hp": BOSSES[0]["hp"],
            "hp": BOSSES[0]["hp"],
            "avatar": BOSSES[0]["avatar"],
            "damage": BOSSES[0]["damage"],
            "class": BOSSES[0]["class"],
            "defense": BOSSES[0]["defense"],
            "strength": BOSSES[0]["strength"],
            "agility": BOSSES[0]["agility"],
            "intelligence": BOSSES[0]["intelligence"],
            "ability": BOSSES[0]["ability"],
            "is_alive": True,
            "last_spawn": current_datetime.isoformat(),
            "damage_dealt": 0
        }
        await mongodb.update_user(user_id, {"boss": account['boss']})
    account = await mongodb.get_user(user_id)
    last_spawn_raw = account['boss'].get('last_spawn')

    # Преобразуем last_spawn в datetime
    if isinstance(last_spawn_raw, str):
        last_spawn = datetime.fromisoformat(last_spawn_raw)
    else:
        last_spawn = last_spawn_raw or current_datetime

    # Вычисляем, сколько прошло времени
    elapsed = current_datetime - last_spawn

    # if elapsed >= timedelta(seconds=200):
    # Если прошло больше 72 часов (3 дня)
    if elapsed >= timedelta(hours=72):
        current_boss_id = account['boss'].get("boss_id", 0)
        next_boss_id = (current_boss_id + 1) % len(BOSSES)  # Переход по кругу
        next_boss = BOSSES[next_boss_id]

        # Обновляем данные аккаунта
        account['boss'] = {
            "boss_id": next_boss_id,
            "name": next_boss["name"],
            "current_hp": next_boss["hp"],
            "hp": next_boss["hp"],
            "avatar": next_boss["avatar"],
            "class": next_boss["class"],
            "damage": next_boss["damage"],
            "defense": next_boss["defense"],
            "is_alive": True,
            "strength": next_boss["strength"],
            "agility": next_boss["agility"],
            "intelligence": next_boss["intelligence"],
            "ability": next_boss["ability"],
            "last_spawn": current_datetime.isoformat(),
            "damage_dealt": 0
        }

        # ❗ не забудь сохранить обратно в базу, если используешь MongoDB:
        await mongodb.update_user(user_id, {"boss": account['boss']})
        account = await mongodb.get_user(user_id)  # добавить это здесь
        last_spawn_raw = account['boss'].get('last_spawn')

        # Преобразуем last_spawn в datetime
        if isinstance(last_spawn_raw, str):
            last_spawn = datetime.fromisoformat(last_spawn_raw)
        else:
            last_spawn = last_spawn_raw or current_datetime


    # Время следующего респавна (72 часа после спавна)
    next_respawn = last_spawn + timedelta(hours=72)

    # Сколько осталось
    remaining = next_respawn - current_datetime

    total_minutes = int(remaining.total_seconds() // 60)
    days = total_minutes // (60 * 24)
    hours = (total_minutes // 60) % 24
    minutes = total_minutes % 60

    time = f"{days}д {hours}ч {minutes}м"

    # Отправляем сообщение с информацией о новом боссе

    if account['boss']['class'] == 'strength':
        clas = "💪 Сила"
    elif account['boss']['class'] == 'agility':
        clas = "🦶 Ловкость"
    else:
        clas = "🧠 Интеллект"

    if "boss_squad" not in account:
        await mongodb.update_user(user_id, {"boss_squad": {
            "bg1": "empty",
            "bg1_universe": "empty",
            "bg2": "empty",
            "bg2_universe": "empty",
            "bg3": "empty",
            "bg3_universe": "empty",
            "bg4": "empty",
            "bg4_universe": "empty",
            "bg5": "empty",
            "bg5_universe": "empty",
            "bg6": "empty",
            "bg6_universe": "empty"
        }})
        account = await mongodb.get_user(user_id)

    boss_data = account["boss"]
    bos = Boss(
        name=boss_data["name"],
        hp=boss_data["current_hp"],
        strength=boss_data["strength"],
        agility=boss_data["agility"],
        intelligence=boss_data["intelligence"],
        ability=boss_data["ability"],
        clas=boss_data["class"]
    )

    if 'boss_keys' not in account['account']:
        await mongodb.update_user(user_id, {"account.boss_keys": 0})
        account = await mongodb.get_user(user_id)

    if 'clan_coins' not in account['account']:
        await mongodb.update_user(user_id, {"account.clan_coins": 0})
        account = await mongodb.get_user(user_id)
    keys = account['account']['boss_keys']

    if not account['boss']['is_alive']:
        media_id = "CgACAgIAAx0CfstymgACQApoLhMZydd6r6wQCGjwaMzc-QyEmgAC6noAAsTQcUkwGF1ofkEWljYE"
        buttons = ["🏴 Отряд", "🔙 Назад"]
        callbacks = ["boss_squad", "tokio"]
        text = (f"´ཀ` 💔 Босс повержен! ´ཀ`"
                f"\n꒷꒦꒷꒦꒷꒦꒷꒷꒦꒷꒷꒷꒦꒷꒷꒦꒷꒦꒷꒦꒷"
                f"\n💰 Выбывшие ресурсы:"
                f"\n<blockquote> • 50 🪙 клановых монет"
                f"\n • 100 💠 нефритов"
                f"\n • 250 📀 золота "
                f"\n • 500 💿 серебра</blockquote>")
    else:
        media_id = account['boss']['avatar']
        buttons = ["🗡 Атаковать • 🗝", "🏴 Отряд", "🔙 Назад"]
        callbacks = ["battle_boss", "boss_squad", "tokio"]
        text = (f"´ཀ`  <b>{account['boss']['name']}</b>  ´ཀ`"
                f"\n⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘"
                f"\n<b>Класс: {clas}</b>"
                f"\n<blockquote> • ❤️ <b>{bos.health}</b> из {BOSSES[account['boss']['boss_id']]['hp']}"
                f"\n • ⚔️ <b>{bos.attack}</b>"
                f"\n • 🛡 <b>{bos.defense}</b>"
                f"\n • <b>{bos.ability}</b></blockquote>"
                f"\nКлючи: {keys}🗝")

    pattern = dict(
        caption=f"{text}"
                f"\n꒷꒦꒷꒦꒷꒦꒷꒷꒦꒷꒷꒷꒦꒷꒷꒦꒷꒦꒷꒦꒷"
                f"\n⏱️ <b>Respawn:</b> {time}",
        reply_markup=inline_builder(buttons, callbacks, row_width=[1, 1, 1])
    )

    media = InputMediaAnimation(media=media_id)
    if isinstance(callback, CallbackQuery):
        await callback.message.edit_media(media)
        await callback.message.edit_caption(**pattern)
    else:
        await callback.answer_animation(animation=media_id, **pattern)


def deck_text(character, universe):
    strength = character_photo.get_stats(universe, character, 'arena')['strength']
    agility = character_photo.get_stats(universe, character, 'arena')['agility']
    intelligence = character_photo.get_stats(universe, character, 'arena')['intelligence']
    clas = character_photo.get_stats(universe, character, 'arena')['class']
    hp = strength * 75
    attack = strength * 5 + agility * 5 + intelligence * 5
    defense = (strength + agility + (intelligence // 2)) // 4

    text = (f"╭┈๋જ‌›<b>{character}</b> ♥️{hp}\n" # ✧ {clas}
            f'<tg-emoji emoji-id="5399959611283356481">❌</tg-emoji>┄⚔️{attack} 🛡️{defense} ✊{strength} 👣{agility} 🧠{intelligence}\n'
            # f" • 🎴  "
            # f"\n ┗➤ • ♥️{hp} • ⚔️{attack} • 🛡️{defense}"
            # f"\n     ┗➤ • ✊{strength} • 👣{agility} • 🧠{intelligence} ✧ {clas}"
            )
    return text


@router.callback_query(F.data == "boss_squad")
async def boss_squad(callback: CallbackQuery):
    user_id = callback.from_user.id
    account = await mongodb.get_user(user_id)
    universe = account['universe']

    deck = account.get("boss_squad", {})

    required_fields = {
        "bg1": "empty",
        "bg1_universe": "empty",
        "bg2": "empty",
        "bg2_universe": "empty",
        "bg3": "empty",
        "bg3_universe": "empty",
        "bg4": "empty",
        "bg4_universe": "empty",
        "bg5": "empty",
        "bg5_universe": "empty",
        "bg6": "empty",
        "bg6_universe": "empty"
    }

    for field, value in required_fields.items():
        if field not in deck:
            deck[field] = value

    await mongodb.update_user(user_id, {"boss_squad": deck})
    account = await mongodb.get_user(user_id)

    deck_data = account["boss_squad"]
    first = deck_data["bg1"]
    first_universe = deck_data["bg1_universe"]
    second = deck_data["bg2"]
    second_universe = deck_data["bg2_universe"]
    third = deck_data["bg3"]
    third_universe = deck_data["bg3_universe"]
    fourth = deck_data["bg4"]
    fourth_universe = deck_data["bg4_universe"]
    fifth = deck_data["bg5"]
    fifth_universe = deck_data["bg5_universe"]
    sixth = deck_data["bg6"]
    sixth_universe = deck_data["bg6_universe"]

    cards = [first, second, third, fourth, fifth, sixth]
    card_universes = [first_universe, second_universe, third_universe, fourth_universe, fifth_universe, sixth_universe]
    messages = []
    icons = []
    powers = []

    for card in cards:
        if card == "empty":
            messages.append("╭┈๋જ‌›<b><i> Пустое место </i></b>\n"
                '<tg-emoji emoji-id="5399959611283356481">❌</tg-emoji>┄ <i> empty </i>\n'
                )
            icons.append("ℹ️")
            powers.append(0)
        else:
            p = get_stats(card_universes[cards.index(card)], card, 'arena')
            power = p.get('power')
            messages.append(deck_text(card, card_universes[cards.index(card)]))
            icons.append("☑️")
            powers.append(power)

    # Доступ к результатам
    f1_msg, f2_msg, f3_msg, f4_msg, f5_msg, f6_msg = messages
    f1_icon, f2_icon, f3_icon, f4_icon, f5_icon, f6_icon = icons
    first, second, third, fourth, fifth, sixth = powers

    power = first + second + third + fourth + fifth + sixth

    if "empty" in deck_data.values():
        msg = "❃ ℹ️ Есть пустые места в отряде"
    else:
        msg = "❃ ☑️ Ваш отряд готов к битве"

    pattern = dict(
        caption=f"<b>❖ 🏴 Отряд 🗡</b>"
                f"\n┅┅━─━┅┄ ⟛ ┄┅━─━┅┅"
                f"<blockquote expandable>"
                f"{f1_msg}"
                f"{f2_msg}"
                f"{f3_msg}"
                f"{f4_msg}"
                f"{f5_msg}"
                f"{f6_msg}"
                f"╰──⚜️ Сила отряда: {power}🗡──╯</blockquote>"
                f"\n{msg}",
        reply_markup=inline_builder(
            [f"{f1_icon}", f"{f2_icon}", f"{f3_icon}",
             f"{f4_icon}", f"{f5_icon}", f"{f6_icon}",
             "🔙 Назад"],
            ["bg1", "bg2", "bg3",
             "bg4", "bg5", "bg6",
             "boss"],
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
    if rarity == "bg_divine":
        rarity = "divine"
    elif rarity == "bg_mythical":
        rarity = "mythical"
    elif rarity == "bg_legendary":
        rarity = "legendary"
    elif rarity == "bg_epic":
        rarity = "epic"
    elif rarity == "bg_rare":
        rarity = "rare"
    elif rarity == "bg_common":
        rarity = "common"
    elif rarity == "bg_halloween":
        rarity = "halloween"
    elif rarity == "bg_soccer":
        rarity = "soccer"
    return invent[rarity], universe


@router.callback_query(F.data.in_(['bg1', 'bg2', 'bg3', 'bg4', 'bg5', 'bg6']))
async def inventory(callback: CallbackQuery | Message, state: FSMContext):
    slot = callback.data

    await mongodb.update_user(
        callback.from_user.id,
        {
            "ui.boss.slot": slot,
        }
    )

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
    msg = (f"\n❖ 🃏 Количество карт: {total_elements}"
           f"\n\n❖ 🌠 Божественные 🌟 {total_divine}"
           f"\n❖ 🌌 Мифические ⭐️ {total_mythical}"
           f"\n❖ 🌅 Легендарные ⭐️ {total_legendary}"
           f"\n❖ 🎆 Эпические ⭐️ {total_epic}"
           f"\n❖ 🎇 Редкие ⭐️ {total_rare}"
           f"\n❖ 🌁 Обычные ⭐️ {total_common}")
    buttons = [f"🌠 Божественные 🌟 {total_divine}", f"🌌 Мифические ⭐️ {total_mythical}", f"🌅 Легендарные ⭐️ {total_legendary}",
               f"🎆 Эпические ⭐️ {total_epic}", f"🎇 Редкие ⭐️ {total_rare}", f"🌁 Обычные ⭐️ {total_common}", "🔙 Назад"]
    callbacks = ["bg_divine", "bg_mythical", "bg_legendary", "bg_epic", "bg_rare", "bg_common", "boss_squad"]

    if universe == "Allstars":
        if "halloween" in account['inventory']['characters']['Allstars']:
            total_halloween = len(account['inventory']['characters']['Allstars'].get('halloween', {}))
            buttons.insert(0, f"👻 Halloween 🎃 {total_halloween}")
            callbacks.insert(0, "bg_halloween")
        # if "soccer" not in account['inventory']['characters']['Allstars']:
        #     account = await mongodb.get_user(user_id)
        #     await mongodb.update_user(user_id, {"inventory.characters.Allstars.soccer": []})
        #     total_soccer = len(account['inventory']['items'].get('soccer', {}))
        #     buttons.insert(0, f"⚽️ Soccer {total_soccer}")
        #     callbacks.insert(0, "soccer")

    pattern = dict(caption=f"🥡 Инвентарь"
                           f"\n── •✧✧• ──────────"
                           f"\n<blockquote>❖ Здесь вы можете увидеть все ваши 🃏 карты "
                           f"и установить их в качестве основного 🎴 персонажа к 🏴отряду на битву с боссом."
                           f"\n❖ Выберите ✨ редкость карты, чтобы чтобы выбрать персонажа.</blockquote>"
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


@router.callback_query(F.data.in_(['bg_soccer', 'bg_halloween', 'bg_common', 'bg_rare',
                                   'bg_epic', 'bg_legendary', 'bg_mythical', 'bg_divine']))
async def inventory(callback: CallbackQuery, state: FSMContext):

    inline_id = callback.inline_message_id
    user_id = callback.from_user.id
    invent, universe = await get_inventory(user_id, callback.data)

    if invent == []:
        await callback.answer("❖ ✖️ У вас нет карт данной редкости", show_alert=True)
        return

    await mongodb.update_user(
        callback.from_user.id,
        {
            "ui.boss.rarity": callback.data,
            "ui.boss.page": 0,
            "ui.boss.character": invent[0],
            "ui.boss.universe": universe,
        }
    )

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
                                                           f"{msg}"
                                                           f"\n──❀*̥˚──◌──◌──❀*̥˚────"
                                                           f"\n❖ 🔖 1 из {len(invent)}",
                                        reply_markup=pagination_boss())


@router.callback_query(Pagination.filter(F.action.in_(["bg_prev", "bg_next"])))
async def inventory(callback: CallbackQuery, callback_data: Pagination, state: FSMContext):
    try:
        inline_id = callback.inline_message_id

        account = await mongodb.get_user(callback.from_user.id)
        ui = account.get("ui", {}).get("boss", {})

        rarity = ui.get("rarity")
        page_num = ui.get("page", 0)

        if not rarity:
            await callback.answer(
                "❖ ✖️ Сессия устарела. Откройте отряд заново.",
                show_alert=True
            )
            return

        invent, universe = await get_inventory(callback.from_user.id, rarity)

        if callback_data.action == "bg_next":
            page_num = (page_num + 1) % len(invent)
        elif callback_data.action == "bg_prev":
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
                        f"{msg}"
                        f"\n──❀*̥˚──◌──◌──❀*̥˚────"
                        f"\n❖ 🔖 {page_num + 1} из {len(invent)}",
                reply_markup=pagination_boss(page=page_num)
            )

        await mongodb.update_user(
            callback.from_user.id,
            {
                "ui.boss.page": page_num,
                "ui.boss.character": invent[page_num],
                "ui.boss.universe": universe,
            }
        )

        await callback.answer()
    except KeyError:
        await callback.answer('❖ <tg-emoji emoji-id="5462921117423384478">❌</tg-emoji>Идёт разработка бота связи с чем сессия была остановлена, вызовите '
                              '🥡 Инвентарь еще раз', show_alert=True)


@router.callback_query(F.data == "bg_choice_card")
async def change_ch(callback: CallbackQuery, state: FSMContext):
    try:
        user_id = callback.from_user.id
        account = await mongodb.get_user(user_id)
        deck = account["boss_squad"]
        data = await state.get_data()
        user_id = callback.from_user.id
        account = await mongodb.get_user(user_id)
        deck = account["boss_squad"]

        ui = account.get("ui", {}).get("boss", {})

        character = ui.get("character")
        slot = ui.get("slot")
        universe = ui.get("universe")

        if not all([character, slot, universe]):
            await callback.answer(
                "❖ ✖️ Сессия устарела. Откройте отряд заново.",
                show_alert=True
            )
            return

        if character in deck.values():
            await callback.answer(
                "❖ 🔂 Этот персонаж уже есть в отряде",
                show_alert=True
            )
            return

        await mongodb.update_user(
            user_id,
            {
                f"boss_squad.{slot}": character,
                f"boss_squad.{slot}_universe": universe,
            }
        )

        await callback.answer("🎴 Персонаж успешно добавлен", show_alert=True)
        await boss_squad(callback)

    except KeyError:
        await callback.answer('❖ <tg-emoji emoji-id="5462921117423384478">❌</tg-emoji> Идёт разработка бота связи с чем сессия была остановлена, вызовите '
                              '🥡 Инвентарь еще раз', show_alert=True)


class Passive:
    def __init__(self, name, effect, undo_effect, duration, points=None, apply_once=False):
        self.name = name
        self.effect = effect
        self.undo_effect = undo_effect
        self.duration = duration
        self.points = points
        self.applied = False
        self.apply_once = apply_once


def calculate_damage(attacker, defender):
    base_damage = max(attacker.attack - defender.defense, 1)  # Минимальный урон 1

    # # Проверяем классовое преимущество
    # class_advantage = {
    #     "strength": "agility",
    #     "agility": "intelligence",
    #     "intelligence": "strength"
    # }
    #
    # if class_advantage[attacker.clas] == defender.clas:
    #     base_damage = int(base_damage * 1.4)  # 1.4x урон

    return base_damage


class Boss:
    def __init__(self, name, hp, strength, agility, intelligence, ability, clas):
        self.name = name
        self.strength = strength
        self.agility = agility
        self.intelligence = intelligence
        self.shield = 0
        self.health = hp
        self.attack = strength + agility + (intelligence // 2) * 35
        self.defense = (strength + agility + (intelligence // 2)) // 4 * 4
        self.mana = intelligence * 10
        self.crit_dmg = strength + (agility // 2) + (intelligence // 4)
        self.crit_ch = agility + (strength // 2) + (intelligence // 4)
        self.ability = ability
        self.clas = clas


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


async def auto_boss_battle(bot: Bot, user_id: int, characters: list, boss: Boss, account: dict, callback):
    alive_characters = characters[:]
    boss_is_alive = True
    turn_count = 0

    # Сообщение стартовое
    callback = await callback.message.edit_caption(caption="⏳ Битва начинается...")
    await asyncio.sleep(1.5)

    while boss.health > 0 and alive_characters:
        turn_count += 1

        # 💥 Атака отряда (поочерёдно, с паузой и редактированием)
        for char in alive_characters:
            damage = calculate_damage(char, boss)
            boss.health -= damage
            if boss.health < 0:
                boss.health = 0
            text = (
                f"˹{char.name}˼ атакует {boss.name} на {damage}🗡 урона\n"
                f"\nHP босса: {boss.health}❤️ "
            )
            await callback.edit_caption(caption=text)
            await asyncio.sleep(1.5)

        # 📍 Победа
        if boss.health <= 0:
            await callback.edit_caption(caption=f"🏆 {boss.name} повержен!\n❤️ HP: 0")
            break

        # 🔥 Атака босса (по всем, одной строкой)
        boss_damage = boss.attack + 50 if turn_count % 3 == 0 else boss.attack
        ability_text = f"💥 Босс использует способность: {boss.ability}" if turn_count % 3 == 0 else ""

        await callback.edit_caption(caption=f"{ability_text}\n☠️ {boss.name} наносит {boss_damage} урона всем!")
        await asyncio.sleep(1.5)

        dead_chars = []
        for char in alive_characters:
            char.health -= boss_damage
            if char.health <= 0:
                dead_chars.append(char)

        for char in dead_chars:
            alive_characters.remove(char)
            await callback.edit_caption(caption=f"💀 {char.name} пал в бою!")
            await asyncio.sleep(1.2)

    # 🧾 Сохранение
    account['boss']['current_hp'] = boss.health
    account['boss']['is_alive'] = boss.health > 0
    await mongodb.update_user(user_id, {"boss": account['boss']})

    if boss.health > 0:
        await bot.send_message(user_id, "🏴‍☠️ Битва завершена. ❤️‍🩹 Босс выжил.")
        await mongodb.update_user(user_id, {"boss.is_alive": True})
        await callback.delete()
        await boss_func(callback, account, user_id)
    else:
        # даем анграду
        account['account']['clan_coins'] += 50
        account['campaign']['nephritis'] += 100
        account['campaign']['gold'] += 250
        account['campaign']['silver'] += 500

        await mongodb.update_user(user_id, {
            "account.clan_coins": account['account']['clan_coins'],
            "campaign.nephritis": account['campaign']['nephritis'],
            "campaign.gold": account['campaign']['gold'],
            "campaign.silver": account['campaign']['silver'],
            "boss.is_alive": False,
            "boss.current_hp": 0
        })
        await callback.delete()
        await boss_func(callback, account, user_id)


@router.callback_query(F.data == "battle_boss")
async def battle_boss(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    account = await mongodb.get_user(user_id)

    if "empty" in account["boss_squad"].values():
        await callback.answer("❖ 🔂 У вас есть пустые места в отряде", show_alert=True)
        return

    if account['account']['boss_keys'] <= 0:
        await callback.answer("❖ 🗝 У вас недостаточно ключей для битвы с боссом", show_alert=True)
        return

    account['account']['boss_keys'] -= 1
    await mongodb.update_user(user_id, {"account.boss_keys": account['account']['boss_keys']})

    await callback.message.delete_reply_markup()
    await callback.message.edit_caption(caption="⚔ Битва с боссом начинается...")
    squad = account["boss_squad"]
    characters = []
    slave = account["inventory"]["slaves"][0] if account["inventory"]["slaves"] else None

    for i in range(1, 7):
        name = squad[f"bg{i}"]
        universe = squad[f"bg{i}_universe"]
        cb = f"┋{name}┋"
        character = card_characters.CardCharacters(
            ident=account["_id"],
            player_nick_name=account["name"],
            universe=universe,
            cb=cb,
            name=name,
            slave=slave,
            rid=0,
            data=f"bg{i}"
        )
        characters.append(character)

    boss_data = account["boss"]
    bos = Boss(
        name=boss_data["name"],
        hp=boss_data["current_hp"],
        strength=boss_data["strength"],
        agility=boss_data["agility"],
        intelligence=boss_data["intelligence"],
        ability=boss_data["ability"],
        clas=boss_data["class"]
    )

    await auto_boss_battle(bot=callback.bot, user_id=user_id, characters=characters, boss=bos, account=account, callback=callback)
