from datetime import datetime
from aiogram import Router, F
from contextlib import suppress

from aiogram.exceptions import TelegramBadRequest
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery, InputMediaAnimation, InputMediaPhoto, Message

from app.data import mongodb
from app.data.character_photo import get_stats
from app.keyboards.builders import inline_builder, Pagination, pagination_dungeon
from app.recycling import profile
from app.filters.chat_type import ChatTypeFilter
from app.data import character_photo
from aiogram.fsm.context import FSMContext

router = Router()


@router.message(ChatTypeFilter(chat_type=["private"]), F.text == "⛩️ Подземелье")
@router.callback_query(F.data == "dungeon")
async def dungeon(callback: CallbackQuery | Message):
    user_id = callback.from_user.id
    account = await mongodb.get_user(user_id)
    universe = account['universe']

    # Текущее время
    current_datetime = datetime.now()

    # Последняя продажа
    last_sell_datetime = account['tasks'].get('last_dungeon', current_datetime)
    if isinstance(last_sell_datetime, str):  # Преобразуем строку, если нужно
        last_sell_datetime = datetime.fromisoformat(last_sell_datetime)

    # Рассчитываем прошедшее время в секундах
    elapsed_seconds = int((current_datetime - last_sell_datetime).total_seconds())

    if "deck_dungeon" not in account:
        await mongodb.update_user(user_id, {"deck_dungeon": {
            "dg1": "empty",
            "dg1_universe": "empty",
            "dg2": "empty",
            "dg2_universe": "empty",
            "dg3": "empty",
            "dg3_universe": "empty",
            "dg4": "empty",
            "dg4_universe": "empty",
            "dg5": "empty",
            "dg5_universe": "empty",
            "dg6": "empty",
            "dg6_universe": "empty"
        }})
        account = await mongodb.get_user(user_id)
        text = "‼️ Отряд пустой"
        power = 0

    deck_data = account["deck_dungeon"]
    first = deck_data["dg1"]
    first_universe = deck_data["dg1_universe"]
    second = deck_data["dg2"]
    second_universe = deck_data["dg2_universe"]
    third = deck_data["dg3"]
    third_universe = deck_data["dg3_universe"]
    fourth = deck_data["dg4"]
    fourth_universe = deck_data["dg4_universe"]
    fifth = deck_data["dg5"]
    fifth_universe = deck_data["dg5_universe"]
    sixth = deck_data["dg6"]
    sixth_universe = deck_data["dg6_universe"]

    if first == "empty":
        first = 0
    else:
        p = get_stats(first_universe, first, 'arena')
        first = p.get('power')
    if second == "empty":
        second = 0
    else:
        p = get_stats(second_universe, second, 'arena')
        second = p.get('power')
    if third == "empty":
        third = 0
    else:
        p = get_stats(third_universe, third, 'arena')
        third = p.get('power')
    if fourth == "empty":
        fourth = 0
    else:
        p = get_stats(fourth_universe, fourth, 'arena')
        fourth = p.get('power')
    if fifth == "empty":
        fifth = 0
    else:
        p = get_stats(fifth_universe, fifth, 'arena')
        fifth = p.get('power')
    if sixth == "empty":
        sixth = 0
    else:
        p = get_stats(sixth_universe, sixth, 'arena')
        sixth = p.get('power')

    power = first + second + third + fourth + fifth + sixth
    text = f"⚜️ Сила отряда: {power}🗡"

    # Прирост ресурсов за час
    nephritis_per_hour = power // 1000
    gold_per_hour = power // 200
    silver_per_hour = power // 40

    # Рассчитываем прирост ресурсов с момента последней продажи
    current_nephritis = max(0, int(account['campaign']['nephritis'] + (nephritis_per_hour * (elapsed_seconds // 60 // 60))))
    current_gold = max(0, int(account['campaign']['gold'] + (gold_per_hour * (elapsed_seconds // 60 // 60))))
    current_silver = max(0, int(account['campaign']['silver'] + (silver_per_hour * (elapsed_seconds // 60 // 60))))

    if current_nephritis < 1:
        current_nephritis = "0.~"

    if nephritis_per_hour < 1:
        nephritis_per_hour = "0.~"
    level = await profile.level(account['campaign']['level'])

    pattern = dict(
        caption=f"❖ ⛩️ <b>๑۩Подземелье۩๑</b>"
                f"\n── •✧✧• ──────────"
                f"\n🕯 Авантюристы 🗡 убивая 👾 монстров очищает подземелье, из убитых монстров выпадают 💰 Ресурсы"
                f"\n<blockquote>╭┈๋જ‌›<b>Алмазы ⚖️ ⊱ 26 ¥💴</b> "
                f"\n💎┄ <i>{nephritis_per_hour} в час</i> ⋗ {current_nephritis} "
                f"\n╭┈๋જ‌›<b>Золото ⚖️ ⊱ 10 ¥💴</b> "
                f"\n📀┄ <i>{gold_per_hour} в час</i> ⋗ {current_gold} "
                f"\n╭┈๋જ‌›<b>Золото ⚖️ ⊱ 4 ¥💴</b> "
                f"\n💿┄ <i>{silver_per_hour} в час</i> ⋗ {current_silver} "
                f"\n╰──{text}──╯</blockquote>"
                f"\nВы можете продать 💰 ресурсы на ⚖️ рынке за указанные цены выше",
        reply_markup=inline_builder(
            ["🕯 Авантюристы 🗡", "💰 Продать 💴", "⚜️ Рейтинг", "🔙 Назад", "📋 Правила"],
            ["deck_dungeon", "sell_resources", "campaign_rank", "tokio", "campaign_rules"],
            row_width=[1, 2, 2]
        )
    )

    media_id = "AgACAgIAAx0CfstymgACGttmw1rY8-Urz0Hyjku-8S34cRDuMgACk-ExG8b4GEr9GXvbgCanOgEAAwIAA3kAAzUE"
    media = InputMediaPhoto(media=media_id)

    if isinstance(callback, CallbackQuery):
        await callback.message.edit_media(media)
        await callback.message.edit_caption(**pattern)
    else:
        await callback.answer_photo(photo=media_id, **pattern)


@router.callback_query(F.data == "sell_resources")
async def sell_resources(callback: CallbackQuery):
    user_id = callback.from_user.id
    account = await mongodb.get_user(user_id)

    universe = account['universe']

    # Текущее время
    current_datetime = datetime.now()

    # Рассчитываем прошедшее время
    last_sell_datetime = account['tasks'].get('last_dungeon', current_datetime)
    if isinstance(last_sell_datetime, str):  # Преобразуем строку, если нужно
        last_sell_datetime = datetime.fromisoformat(last_sell_datetime)

    elapsed_seconds = int((current_datetime - last_sell_datetime).total_seconds())

    deck_data = account["deck_dungeon"]
    if all(value == "empty" for value in deck_data.values()):
        await callback.answer("❖ ✖️ Отряд пустой", show_alert=True)
        return
    if "deck_dungeon" not in account:
        await mongodb.update_user(user_id, {"deck_dungeon": {
            "dg1": "empty",
            "dg1_universe": "empty",
            "dg2": "empty",
            "dg2_universe": "empty",
            "dg3": "empty",
            "dg3_universe": "empty",
            "dg4": "empty",
            "dg4_universe": "empty",
            "dg5": "empty",
            "dg5_universe": "empty",
            "dg6": "empty",
            "dg6_universe": "empty"
        }})
        account = await mongodb.get_user(user_id)
        text = "‼️ Отряд пустой"
        power = 0

    deck_data = account["deck_dungeon"]
    first = deck_data["dg1"]
    first_universe = deck_data["dg1_universe"]
    second = deck_data["dg2"]
    second_universe = deck_data["dg2_universe"]
    third = deck_data["dg3"]
    third_universe = deck_data["dg3_universe"]
    fourth = deck_data["dg4"]
    fourth_universe = deck_data["dg4_universe"]
    fifth = deck_data["dg5"]
    fifth_universe = deck_data["dg5_universe"]
    sixth = deck_data["dg6"]
    sixth_universe = deck_data["dg6_universe"]

    if first == "empty":
        first = 0
    else:
        p = get_stats(first_universe, first, 'arena')
        first = p.get('power')
    if second == "empty":
        second = 0
    else:
        p = get_stats(second_universe, second, 'arena')
        second = p.get('power')
    if third == "empty":
        third = 0
    else:
        p = get_stats(third_universe, third, 'arena')
        third = p.get('power')
    if fourth == "empty":
        fourth = 0
    else:
        p = get_stats(fourth_universe, fourth, 'arena')
        fourth = p.get('power')
    if fifth == "empty":
        fifth = 0
    else:
        p = get_stats(fifth_universe, fifth, 'arena')
        fifth = p.get('power')
    if sixth == "empty":
        sixth = 0
    else:
        p = get_stats(sixth_universe, sixth, 'arena')
        sixth = p.get('power')

    power = first + second + third + fourth + fifth + sixth

    # Прирост ресурсов за час
    nephritis_per_hour = power // 1000
    gold_per_hour = power // 200
    silver_per_hour = power // 40

    # Рассчитываем прирост ресурсов
    nephritis_earned = max(0, int(account['campaign']['nephritis'] + (nephritis_per_hour * (elapsed_seconds // 60 // 60))))
    gold_earned = max(0, int(account['campaign']['gold'] + (gold_per_hour * (elapsed_seconds // 60 // 60))))
    silver_earned = max(0, int(account['campaign']['silver'] + (silver_per_hour * (elapsed_seconds // 60 // 60))))

    # Проверяем минимальные значения для продажи
    if nephritis_earned < 1 and gold_earned < 1 and silver_earned < 1:
        await callback.answer("❖ ✖️ Недостаточно ресурсов для продажи", show_alert=True)
        return

    nephritis = 0
    gold = 0
    silver = 0

    if nephritis_earned < 1:
        nephritis = nephritis_earned
        nephritis_earned = 0
    if gold_earned < 1:
        gold = gold_earned
        gold_earned = 0
    if silver_earned < 1:
        silver = silver_earned
        silver_earned = 0

    # Считаем общую сумму
    total_money = nephritis_earned * 26 + gold_earned * 10 + silver_earned * 4

    # Обновляем ресурсы и деньги
    await mongodb.update_user(
        user_id, {
            'campaign.nephritis': nephritis,  # Оставляем остаток
            'campaign.gold': gold,
            'campaign.silver': silver,
            'tasks.last_dungeon': current_datetime.isoformat()
        }
    )

    await mongodb.update_user(user_id, {'account.money': total_money})

    level = await profile.level(account['campaign']['level'])

    account = await mongodb.get_user(user_id)
    current_nephritis = max(0, int(account['campaign']['nephritis'] + (nephritis_per_hour * (elapsed_seconds // 60 // 60))))
    current_gold = max(0, int(account['campaign']['gold'] + (gold_per_hour * (elapsed_seconds // 60 // 60))))
    current_silver = max(0, int(account['campaign']['silver'] + (silver_per_hour * (elapsed_seconds // 60 // 60))))
    power = first + second + third + fourth + fifth + sixth
    text = f"⚜️ Сила отряда: {power}🗡"

    caption = (f"❖  ⛩️  <b>๑۩Подземелье۩๑</b>"
                f"\n── •✧✧• ──────────"
                f"\n🕯 Авантюристы 🗡 убивая 👾 монстров очищает подземелье, из убитых монстров выпадают 💰 Ресурсы"
                f"\n<blockquote>╭┈๋જ‌›<b>Алмазы ⚖️ ⊱ 26 ¥💴</b> "
                f"\n💎┄ <i>{nephritis_per_hour} в час</i> ⋗ {current_nephritis} "
                f"\n╭┈๋જ‌›<b>Золото ⚖️ ⊱ 10 ¥💴</b> "
                f"\n📀┄ <i>{gold_per_hour} в час</i> ⋗ {current_gold} "
                f"\n╭┈๋જ‌›<b>Золото ⚖️ ⊱ 4 ¥💴</b> "
                f"\n💿┄ <i>{silver_per_hour} в час</i> ⋗ {current_silver} "
                f"\n╰──{text}──╯</blockquote>"
                f"\nВы можете продать 💰 ресурсы на ⚖️ рынке за указанные цены выше")

    await callback.message.edit_caption(inline_message_id=callback.inline_message_id, caption=caption, reply_markup=inline_builder(
            ["🕯 Авантюристы 🗡", "💰 Продать 💴", "📋 Правила", "🔙 Назад"], # , "⚜️ Рейтинг"
            ["deck_dungeon", "sell_resources", "campaign_rules", "tokio"], # "campaign_rank"
            row_width=[1, 2, 1]))
    await callback.answer(f"❖ 💰 Ресурсы проданы за {total_money}¥ 💴", show_alert=True)


@router.callback_query(F.data == "campaign_rank")
async def campaign_rank(callback: CallbackQuery):
    account = await mongodb.get_user(callback.from_user.id)
    rating = await mongodb.send_rating("campaign.power", account, '⚜️')

    media = InputMediaAnimation(media="CgACAgIAAx0CfstymgACRwABaKyCDrQV6vglI9aMJ9esarQbaO0AAvKZAALvCGlJzouYInNTMGQ2BA")
    await callback.message.edit_media(media=media)

    await callback.message.edit_caption(
        caption=f"❖  ⚜️  <b>Рейтинг сильных игроков</b>"
                f"\n┅┅━─━┅┄ ⟛ ┄┅━─━┅┅"
                f"<blockquote expandable>"
                f"{rating}"
                f"</blockquote>",
        parse_mode=ParseMode.HTML,
        reply_markup=inline_builder(
            ["🔙 Назад"],
            ["dungeon"],
            row_width=[2, 2])
    )
    await callback.answer()


@router.callback_query(F.data == "campaign_rules")
async def campaign_rules(callback: CallbackQuery):
    await callback.message.answer(
        f"❖ 📋 Правила Подземелье"
        "\n── •✧✧• ──────────"
        "\nhttps://teletype.in/@dire_hazard/x1#DZdC",
        reply_markup=inline_builder(["☑️"], ["delete"], row_width=[1]))

    await callback.answer()


def deck_text(character, universe):
    strength = character_photo.get_stats(universe, character, 'arena')['strength']
    agility = character_photo.get_stats(universe, character, 'arena')['agility']
    intelligence = character_photo.get_stats(universe, character, 'arena')['intelligence']
    clas = character_photo.get_stats(universe, character, 'arena')['class']
    hp = strength * 75
    attack = strength * 5 + agility * 5 + intelligence * 5
    defense = (strength + agility + (intelligence // 2)) // 4

    text = (f"╭┈๋જ‌›<b>{character}</b> ♥️{hp}\n"
            f"🎴┄⚔️{attack} 🛡️{defense} ✊{strength} 👣{agility} 🧠{intelligence}\n"
        # f" • 🎴 {character} "
        #     f"\n ┗➤ • ♥️{hp} • ⚔️{attack} • 🛡️{defense}"
        #     f"\n     ┗➤ • ✊{strength} • 👣{agility} • 🧠{intelligence} ✧ {clas}"
    )
    return text


@router.callback_query(F.data == "deck_dungeon")
async def choose_card(callback: CallbackQuery):
    user_id = callback.from_user.id
    account = await mongodb.get_user(user_id)
    universe = account['universe']

    deck = account.get("deck_dungeon", {})

    required_fields = {
        "dg1": "empty",
        "dg1_universe": "empty",
        "dg2": "empty",
        "dg2_universe": "empty",
        "dg3": "empty",
        "dg3_universe": "empty",
        "dg4": "empty",
        "dg4_universe": "empty",
        "dg5": "empty",
        "dg5_universe": "empty",
        "dg6": "empty",
        "dg6_universe": "empty"
    }

    for field, value in required_fields.items():
        if field not in deck:
            deck[field] = value

    await mongodb.update_user(user_id, {"deck_dungeon": deck})
    account = await mongodb.get_user(user_id)

    deck_data = account["deck_dungeon"]
    first = deck_data["dg1"]
    first_universe = deck_data["dg1_universe"]
    second = deck_data["dg2"]
    second_universe = deck_data["dg2_universe"]
    third = deck_data["dg3"]
    third_universe = deck_data["dg3_universe"]
    fourth = deck_data["dg4"]
    fourth_universe = deck_data["dg4_universe"]
    fifth = deck_data["dg5"]
    fifth_universe = deck_data["dg5_universe"]
    sixth = deck_data["dg6"]
    sixth_universe = deck_data["dg6_universe"]

    cards = [first, second, third, fourth, fifth, sixth]
    card_universes = [first_universe, second_universe, third_universe, fourth_universe, fifth_universe, sixth_universe]
    messages = []
    icons = []
    powers = []

    for card in cards:
        if card == "empty":
            messages.append("╭┈๋જ‌›<b><i> Пустое место </i></b>\n"
                "🎴┄ <i> empty </i>\n")
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
        msg = "❃ ☑️ Ваш отряд готов к походу"

    pattern = dict(
        caption=f"<b>❖ 🕯 Авантюристы 🗡</b>"
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
            ["dg1", "dg2", "dg3",
             "dg4", "dg5", "dg6",
             "dungeon"],
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
    if rarity == "dg_divine":
        rarity = "divine"
    elif rarity == "dg_mythical":
        rarity = "mythical"
    elif rarity == "dg_legendary":
        rarity = "legendary"
    elif rarity == "dg_epic":
        rarity = "epic"
    elif rarity == "dg_rare":
        rarity = "rare"
    elif rarity == "dg_common":
        rarity = "common"
    elif rarity == "dg_halloween":
        rarity = "halloween"
    elif rarity == "dg_soccer":
        rarity = "soccer"
    return invent[rarity], universe


@router.callback_query(F.data.in_(['dg1', 'dg2', 'dg3', 'dg4', 'dg5', 'dg6']))
async def inventory(callback: CallbackQuery | Message, state: FSMContext):
    slot = callback.data

    await mongodb.update_user(
        callback.from_user.id,
        {
            "ui.dungeon.deck_slot": slot,
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
    callbacks = ["dg_divine", "dg_mythical", "dg_legendary", "dg_epic", "dg_rare", "dg_common", f"deck_dungeon"]

    if universe == "Allstars":
        if "halloween" in account['inventory']['characters']['Allstars']:
            total_halloween = len(account['inventory']['characters']['Allstars'].get('halloween', {}))
            buttons.insert(0, f"👻 Halloween 🎃 {total_halloween}")
            callbacks.insert(0, "dg_halloween")
        # if "soccer" not in account['inventory']['characters']['Allstars']:
        #     account = await mongodb.get_user(user_id)
        #     await mongodb.update_user(user_id, {"inventory.characters.Allstars.soccer": []})
        #     total_soccer = len(account['inventory']['items'].get('soccer', {}))
        #     buttons.insert(0, f"⚽️ Soccer {total_soccer}")
        #     callbacks.insert(0, "soccer")

    pattern = dict(caption=f"🥡 Инвентарь"
                           f"\n── •✧✧• ──────────"
                           f"\n<blockquote>❖ Здесь вы можете увидеть все ваши 🃏 карты "
                           f"и установить их в качестве 🎴 персонажа к 🏴отряду в подземелья."
                           f"\n❖ Выберите ✨ редкость карты, чтобы выбрать персонажа.</blockquote>"
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


@router.callback_query(F.data.in_(['dg_soccer', 'dg_halloween', 'dg_common', 'dg_rare',
                                   'dg_epic', 'dg_legendary', 'dg_mythical', 'dg_divine']))
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
            "ui.dungeon.rarity": callback.data,
            "ui.dungeon.page": 0,
            "ui.dungeon.character": invent[0],
            "ui.dungeon.universe": universe
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
                                        reply_markup=pagination_dungeon())


@router.callback_query(Pagination.filter(F.action.in_(["dg_prev", "dg_next"])))
async def inventory(callback: CallbackQuery, callback_data: Pagination, state: FSMContext):
    try:
        inline_id = callback.inline_message_id
        account = await mongodb.get_user(callback.from_user.id)
        ui = account.get("ui", {}).get("dungeon", {})

        rarity = ui.get("rarity")
        page_num = ui.get("page", 0)

        if not rarity:
            await callback.answer(
                "❖ ✖️ Сессия устарела. Откройте инвентарь заново.",
                show_alert=True
            )
            return

        invent, universe = await get_inventory(callback.from_user.id, rarity)

        if callback_data.action == "dg_next":
            page_num = (page_num + 1) % len(invent)
        elif callback_data.action == "dg_prev":
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
                reply_markup=pagination_dungeon(page=page_num)
            )

        await mongodb.update_user(
            callback.from_user.id,
            {
                "ui.dungeon.page": page_num,
                "ui.dungeon.character": invent[page_num],
                "ui.dungeon.universe": universe
            }
        )

        await callback.answer()
    except KeyError:
        await callback.answer('❖ <tg-emoji emoji-id="5462921117423384478">❌</tg-emoji> Идёт разработка бота связи с чем сессия была остановлена, вызовите '
                              '🥡 Инвентарь еще раз', show_alert=True)


@router.callback_query(F.data == "dg_choice_card")
async def change_ch(callback: CallbackQuery, state: FSMContext):
    try:
        user_id = callback.from_user.id
        account = await mongodb.get_user(user_id)
        deck = account["deck_dungeon"]
        account = await mongodb.get_user(user_id)
        ui = account.get("ui", {}).get("dungeon", {})

        character = ui.get("character")
        deck_slot = ui.get("deck_slot")
        universe = ui.get("universe")

        if not all([character, deck_slot, universe]):
            await callback.answer(
                "❖ ✖️ Сессия устарела. Откройте инвентарь заново.",
                show_alert=True
            )
            return

        if character in deck.values():
            await callback.answer(
                "❖ ❌ Этот персонаж уже есть в отряде",
                show_alert=True
            )
            return

        else:
            await mongodb.update_user(
                user_id,
                {
                    f"deck_dungeon.{deck_slot}": character,
                    f"deck_dungeon.{deck_slot}_universe": universe
                }
            )

            await callback.answer("🎴 Вы успешно выбрали персонажа", show_alert=True)
            await choose_card(callback)
    except KeyError:
        await callback.answer('❖ <tg-emoji emoji-id="5462921117423384478">❌</tg-emoji> Идёт разработка бота связи с чем сессия была остановлена, вызовите '
                              '🥡 Инвентарь еще раз', show_alert=True)
