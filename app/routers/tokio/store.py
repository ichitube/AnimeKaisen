from datetime import datetime, timedelta

from contextlib import suppress
from aiogram import Router, F, Bot

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InputMediaAnimation, LabeledPrice, Message
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import PreCheckoutQuery

from app.keyboards.builders import inline_builder
from ..slaves import slave_info
from app.data import mongodb, character_photo
from app.keyboards import builders
from app.filters.chat_type import ChatTypeFilter

router = Router()


@router.message(ChatTypeFilter(chat_type=["private"]), F.text == "🏮 Рынок")
@router.callback_query(F.data == "store")
async def store(callback: CallbackQuery | Message):
    user_id = callback.from_user.id
    account = await mongodb.get_user(user_id)

    ticket_data = account['inventory']['items']['tickets']
    keys = ticket_data['keys']
    golden = ticket_data['golden']
    common = ticket_data['common']

    money = account['account']['money']
    pattern = dict(
        caption=f"❖  🏮  <b>Рынок</b>"
                f"\n── •✧✧• ──────────"  # ❖ Вы можете купить 🎫🎟 билеты и недвижку за 💴 ¥"
                f"\n❖ Вы можете купить за 🌟:"
                f"\n<blockquote>• 🌟 Эксклюзивные персонажи"
                f"\n• 🧧Священный билет"
                f"\n• 💮Pass и 🔖Рабынь</blockquote>"
                # f"\n❖⚖️ Цены:"
                # f"\n<blockquote> • 🏠 = 5000 💴"
                # f"\n • 🎫 = 1000 💴"
                # f"\n • 🎟 = 100 💴</blockquote>"
                # f"\n── •✧✧• ──────────"
                "\n➖➖➖➖➖➖➖➖➖➖➖"
                f"\n💴 {money} ¥  🧧 ⋗ <b>{keys}</b>  🎫 ⋗ <b>{golden}</b>  🎟 ⋗ <b>{common}</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=inline_builder(
            ["🌟 Эксклюзивные персонажи", "💮Pass", "🧧 Купить ", "⛓ Торг", "🏠 Недвижка", "🎫 Купить", "🎟 Купить", "🔙 Назад"],
            ["exclusive_char", "buy_pass", "buy_keys", "slaves_store", "buy_home", "buy_golden", "buy_common", "tokio"],
            row_width=[1, 2, 2, 2, 1]
            )
    )

    media_id = "CgACAgIAAx0CfstymgACIBlnE7j9A6EltliDF5gpy4mJSQHuQQAC01gAAqiJoEiAQXKi8JylYDYE"
    # "CgACAgIAAxkBAAIVAmXMvH4t4RtOQzePYbQgdnNEbFEeAAKOOwACeyZoSiAP4_7nfuBVNAQ"
    media = InputMediaAnimation(media=media_id)
    if isinstance(callback, CallbackQuery):
        inline_id = callback.inline_message_id
        await callback.message.edit_media(media, inline_id)
        await callback.message.edit_caption(inline_id, **pattern)
    else:
        await callback.answer_animation(media_id, **pattern)


@router.callback_query(F.data == "buy_common")
async def buy_common(callback: CallbackQuery):
    inline_id = callback.inline_message_id
    user_id = callback.from_user.id
    account = await mongodb.get_user(user_id)

    money = account['account']['money']
    pattern = dict(
        caption=f"❖  🏪  <b>Купить обычные билеты</b>"
                f"\n── •✧✧• ──────────"
                f"\n<blockquote>❖  Вы можете купить 🎟 обычные билеты за 💴 ¥"
                f"\n • 🎟 = 100 💴"
                f"\nУ вас есть {money} 💴 ¥"
                f"\nСколько билетов вы хотите купить?</blockquote>",
        parse_mode=ParseMode.HTML,
        reply_markup=inline_builder(
            ["💴 Все деньги", "1 🎟", "5 🎟", "10 🎟", "🔙 Назад"],
            ["buy_common_all", "buy_common_1", "buy_common_5", "buy_common_10", "store"],
            row_width=[1, 3, 1]
        )
    )

    await callback.message.edit_caption(inline_id, **pattern)


@router.callback_query(F.data == "buy_common_1")
async def buy_common_1(callback: CallbackQuery):
    await buy_common_ticket(callback, 1)


@router.callback_query(F.data == "buy_common_5")
async def buy_common_5(callback: CallbackQuery):
    await buy_common_ticket(callback, 5)


@router.callback_query(F.data == "buy_common_10")
async def buy_common_10(callback: CallbackQuery):
    await buy_common_ticket(callback, 10)


@router.callback_query(F.data == "buy_common_all")
async def buy_common_all(callback: CallbackQuery):
    user_id = callback.from_user.id
    account = await mongodb.get_user(user_id)
    money = account['account']['money']

    max_count = money // 100
    if max_count > 0:
        await buy_common_ticket(callback, max_count)
    else:
        await callback.answer("❖  🏪  У вас недостаточно 💴 ¥", show_alert=True)


async def buy_common_ticket(callback: CallbackQuery, count: int):
    user_id = callback.from_user.id
    account = await mongodb.get_user(user_id)

    money = account['account']['money']
    if money >= 100 * count:
        await mongodb.update_user(user_id, {'account.money': money - 100 * count})
        await mongodb.update_user(
            user_id, {'inventory.items.tickets.common': account['inventory']['items']['tickets']['common'] + count}
        )
        current_date = datetime.today().date()
        current_datetime = datetime.combine(current_date, datetime.time(datetime.now()))
        await mongodb.update_user(user_id, {"tasks.last_shop_purchase": current_datetime})
        await callback.answer(f"❖  🏪  Вы успешно приобрели {count} 🎟 обычных билетов", show_alert=True)
    else:
        await callback.answer(f"❖  🏪  У вас недостаточно 💴 ¥", show_alert=True)
    await store(callback)


@router.callback_query(F.data == "buy_golden")
async def buy_golden(callback: CallbackQuery):
    inline_id = callback.inline_message_id
    user_id = callback.from_user.id
    account = await mongodb.get_user(user_id)

    money = account['account']['money']
    pattern = dict(
        caption=f"❖  🏪  <b>Купить золотые билеты</b>"
                f"\n── •✧✧• ──────────"
                f"\n<blockquote>Вы можете купить 🎫 золотые билеты за 💴 ¥"
                f"\n • 🎫 = 1000 💴"
                f"\nУ вас есть {money} 💴 ¥"
                f"\nСколько билетов вы хотите купить?</blockquote>",
        parse_mode=ParseMode.HTML,
        reply_markup=inline_builder(
            ["💴 Все деньги", "1 🎫", "5 🎫", "10 🎫", "🔙 Назад"],
            ["buy_golden_all", "buy_golden_1", "buy_golden_5", "buy_golden_10", "store"],
            row_width=[1, 3, 1]
        )
    )

    await callback.message.edit_caption(inline_id, **pattern)


@router.callback_query(F.data == "buy_golden_1")
async def buy_golden_1(callback: CallbackQuery):
    await buy_golden_ticket(callback, 1)


@router.callback_query(F.data == "buy_golden_5")
async def buy_golden_5(callback: CallbackQuery):
    await buy_golden_ticket(callback, 5)


@router.callback_query(F.data == "buy_golden_10")
async def buy_golden_10(callback: CallbackQuery):
    await buy_golden_ticket(callback, 10)


@router.callback_query(F.data == "buy_golden_all")
async def buy_golden_all(callback: CallbackQuery):
    user_id = callback.from_user.id
    account = await mongodb.get_user(user_id)
    money = account['account']['money']

    max_count = money // 1000
    if max_count > 0:
        await buy_golden_ticket(callback, max_count)
    else:
        await callback.answer("❖  🏪  У вас недостаточно 💴 ¥", show_alert=True)


async def buy_golden_ticket(callback: CallbackQuery, count: int):
    user_id = callback.from_user.id
    account = await mongodb.get_user(user_id)

    money = account['account']['money']
    if money >= 1000 * count:
        await mongodb.update_user(user_id, {'account.money': money - 1000 * count})
        await mongodb.update_user(
            user_id, {'inventory.items.tickets.golden': account['inventory']['items']['tickets']['golden'] + count}
        )
        current_date = datetime.today().date()
        current_datetime = datetime.combine(current_date, datetime.time(datetime.now()))
        await mongodb.update_user(user_id, {"tasks.last_shop_purchase": current_datetime})
        await callback.answer(f"❖  🏪  Вы успешно приобрели {count} 🎫 золотых билетов", show_alert=True)
    else:
        await callback.answer(f"❖  🏪  У вас недостаточно 💴 ¥", show_alert=True)
    await store(callback)


homes = character_photo.h_stats


@router.callback_query(F.data == "buy_home")
async def inventory(callback: CallbackQuery, state: FSMContext):
    inline_id = callback.inline_message_id
    result = character_photo.home_stats(list(homes.keys())[0])
    photo = InputMediaAnimation(media=result[0])
    await state.update_data(home=list(homes.keys())[0])

    await mongodb.update_user(
        callback.from_user.id,
        {
            "ui.store.homes.page": 0,
            "ui.store.homes.key": list(homes.keys())[0],
        }
    )

    await callback.message.edit_media(photo, inline_id)
    await callback.message.edit_caption(inline_id, caption=f"❖ ⚜️ Сила: {result[1]}"
                                                           f"\n ── •✧✧• ──────────"
                                                           f"\n<blockquote>Вы можете 🔑 купить этот дом за {result[1]} 💴 ¥ </blockquote>",
                                        reply_markup=builders.pagination_store())


@router.callback_query(builders.Pagination.filter(F.action.in_(["prevv", "nextt"])))
async def inventory(callback: CallbackQuery, callback_data: builders.Pagination, state: FSMContext):
    inline_id = callback.inline_message_id
    page_num = int(callback_data.page)
    data = await state.get_data()

    # 🔁 FALLBACK
    if "home" not in data:
        account = await mongodb.get_user(callback.from_user.id)
        ui = account.get("ui", {}).get("store", {}).get("homes", {})

        page_num = ui.get("page", 0)

    if callback_data.action == "nextt":
        page_num = (page_num + 1) % len(homes)
    elif callback_data.action == "prevv":
        page_num = (page_num - 1) % len(homes)

    home_key = list(homes.keys())[page_num]

    await state.update_data(home=home_key)

    await mongodb.update_user(
        callback.from_user.id,
        {
            "ui.store.homes.page": page_num,
            "ui.store.homes.key": home_key,
        }
    )

    with suppress(TelegramBadRequest):
        result = character_photo.home_stats(list(homes.keys())[page_num])
        photo = InputMediaAnimation(media=result[0])
        await state.update_data(home=list(homes.keys())[page_num])
        await callback.message.edit_media(photo, inline_id)
        await callback.message.edit_caption(
            inline_id,
            caption=f"❖ ⚜️ Сила: {result[1]}"
            f"\n ── •✧✧• ──────────"
            f"\n<blockquote>Вы можете 🔑 купить этот дом за {result[1]} 💴 ¥</blockquote>",
            reply_markup=builders.pagination_store(page_num)
        )
    await callback.answer()


@router.callback_query(F.data == "buy_store_home")
async def buy_home(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    account = await mongodb.get_user(user_id)
    data = await state.get_data()
    # 🔁 FALLBACK
    if "home" not in data:
        account = await mongodb.get_user(callback.from_user.id)
        ui = account.get("ui", {}).get("store", {}).get("homes", {})
        page_num = ui.get("page", 0)
    home = data.get("home")

    if not home:
        ui = account.get("ui", {}).get("home", {})
        home = ui.get("key")

        if not home:
            await callback.answer(
                "❖ ✖️ Сессия устарела. Откройте дома заново.",
                show_alert=True
            )
            return

    result = character_photo.home_stats(home)

    money = account['account']['money']
    if data.get('home') in account['inventory']['home']:
        await callback.answer(f"❖  🏪  У вас уже есть этот дом", show_alert=True)
        return
    else:
        if money >= result[1]:
            await mongodb.update_user(user_id, {'account.money': money - result[1]})
            await mongodb.update_value(user_id, {'campaign.power': result[1]})
            await mongodb.push_home(user_id, data.get('home'))
            current_date = datetime.today().date()
            current_datetime = datetime.combine(current_date, datetime.time(datetime.now()))
            await mongodb.update_user(user_id, {"tasks.last_shop_purchase": current_datetime})
            await callback.answer(f"❖  🏪  Вы успешно приобрели дом 🔑", show_alert=True)
        else:
            await callback.answer(f"❖  🏪  У вас недостаточно 💴 ¥", show_alert=True)
    await store(callback)


slaves = character_photo.s_stats


@router.callback_query(F.data == "slaves_store")
async def store_slaves(callback: CallbackQuery, state: FSMContext):
    inline_id = callback.inline_message_id
    result = character_photo.slaves_stats(list(slaves.keys())[0])
    photo = InputMediaAnimation(media=result[0])
    info = slave_info(result[3], result[2])
    await state.update_data(slave=list(slaves.keys())[0])

    await mongodb.update_user(
        callback.from_user.id,
        {
            "ui.store.slaves.page": 0,
            "ui.store.slaves.key": list(slaves.keys())[0],
        }
    )
    await callback.message.edit_media(photo, inline_id)
    await callback.message.edit_caption(inline_id,
                                        caption=f"❖ 🔖 {result[1]}"
                                        f"\n──❀*̥˚──◌──◌──❀*̥˚────"
                                        f"\n<blockquote>💮 Служение: {result[6]}"
                                        f"\n{info}</blockquote>"
                                        f"\n──❀*̥˚──◌──◌──❀*̥˚────"
                                        f"\n • Цена: {result[5]} 🌟",
                                        reply_markup=builders.slaves_store())


@router.callback_query(builders.Pagination.filter(F.action.in_(["prev_s", "next_s"])))
async def inventory(callback: CallbackQuery, callback_data: builders.Pagination, state: FSMContext):
    inline_id = callback.inline_message_id
    page_num = int(callback_data.page)

    data = await state.get_data()

    if "slave" not in data:
        account = await mongodb.get_user(callback.from_user.id)
        ui = account.get("ui", {}).get("store", {}).get("slaves", {})

        page_num = ui.get("page", 0)

    if callback_data.action == "next_s":
        page_num = (page_num + 1) % len(slaves)
    elif callback_data.action == "prev_s":
        page_num = (page_num - 1) % len(slaves)

    slave_key = list(slaves.keys())[page_num]

    await state.update_data(slave=slave_key)

    await mongodb.update_user(
        callback.from_user.id,
        {
            "ui.store.slaves.page": page_num,
            "ui.store.slaves.key": slave_key,
        }
    )

    with suppress(TelegramBadRequest):
        result = character_photo.slaves_stats(list(slaves.keys())[page_num])
        photo = InputMediaAnimation(media=result[0])
        info = slave_info(result[3], result[2])
        await state.update_data(slave=list(slaves.keys())[page_num])
        await callback.message.edit_media(photo, inline_id)
        await callback.message.edit_caption(
            inline_id,
            caption=f"❖ 🔖 {result[1]}"
            f"\n──❀*̥˚──◌──◌──❀*̥˚────"
            f"\n<blockquote>💮 Служение: {result[6]}"
            f"\n{info}</blockquote>"
            f"\n──❀*̥˚──◌──◌──❀*̥˚────"
            f"\n • Цена: {result[5]} 🌟",
            reply_markup=builders.slaves_store(page_num)
        )
    await callback.answer()


# @router.callback_query(F.data == "buy_slave")
# async def buy_home(callback: CallbackQuery, state: FSMContext):
#     user_id = callback.from_user.id
#     account = await mongodb.get_user(user_id)
#     data = await state.get_data()
#     result = character_photo.slaves_stats(data['slave'])
#     money = account['account']['money']
#     if data.get('slave') in account['inventory']['slaves']:
#         await callback.answer(f"❖  ✖️  У вас уже есть эта рабыня", show_alert=True)
#         return
#     else:
#         if money >= result[4]:
#             await mongodb.update_user(user_id, {'account.money': money - result[4]})
#             await mongodb.push_slave(user_id, data.get('slave'))
#             current_date = datetime.today().date()
#             current_datetime = datetime.combine(current_date, datetime.time(datetime.now()))
#             await mongodb.update_user(user_id, {"tasks.last_shop_purchase": current_datetime})
#             await callback.answer(f"❖  🔖  Вы успешно приобрели рабыню", show_alert=True)
#         else:
#             await callback.answer(f"❖  ✖️  У вас недостаточно 💴 ¥", show_alert=True)
#     await store(callback)


@router.callback_query(F.data == "buy_slave")
async def buy_keys(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    account = await mongodb.get_user(user_id)
    data = await state.get_data()

    slave = data.get("slave")

    # 🔁 FALLBACK В MONGODB
    if not slave:
        ui = account.get("ui", {}).get("slave", {})
        slave = ui.get("key")

        if not slave:
            await callback.answer(
                "❖ ✖️ Сессия устарела. Откройте рабынь заново.",
                show_alert=True
            )
            return

    result = character_photo.slaves_stats(slave)

    if slave in account.get("inventory", {}).get("slaves", []):
        await callback.answer(
            "❖ ✖️ У вас уже есть эта рабыня",
            show_alert=True
        )
        return

    payload = f"buy_slave:{callback.from_user.id}:{slave}"

    await callback.message.answer_invoice(
        title=f"❖ 🔖 {result[1]}",
        description="──❀*̥˚──◌──◌──❀*̥˚────",
        payload=payload,
        currency="XTR",
        prices=[LabeledPrice(label="XTR", amount=result[5])],
    )


cards = character_photo.c_stats


@router.callback_query(F.data == "exclusive_char")
async def store_slaves(callback: CallbackQuery, state: FSMContext):
    inline_id = callback.inline_message_id
    card = list(cards.keys())[0]
    result = character_photo.card_stats(card)
    photo = InputMediaAnimation(media=result['avatar'])
    await state.update_data(excard=card)

    await mongodb.update_user(
        callback.from_user.id,
        {
            "ui.store.excards.page": 0,
            "ui.store.excards.key": card,
        }
    )

    rarity = result['rarity']
    universe = result['universe']
    strength = result['arena']['strength']
    agility = result['arena']['agility']
    intelligence = result['arena']['intelligence']
    power = result['arena']['power']
    msg = (f"\n❖ ✨ Редкость: {rarity}"
           f"\n❖ 🗺 Вселенная: {universe}"
           f"\n\n   ✊🏻 Сила: {strength}"
           f"\n   👣 Ловкость: {agility}"
           f"\n   🧠 Интелект: {intelligence}"
           f"\n   ⚜️ Мощь: {power}")
    await callback.message.edit_media(photo, inline_id)
    await callback.message.edit_caption(inline_id,
                                        caption=f"🔖 {card}"
                                        f"\n──❀*̥˚──◌──◌──❀*̥˚────"
                                        f"<blockquote>{msg}</blockquote>"
                                        f"\n──❀*̥˚──◌──◌──❀*̥˚────"
                                        f"\n🔸Эксклюзивная аватарка",
                                        reply_markup=builders.excard_store())


@router.callback_query(builders.Pagination.filter(F.action.in_(["prev_excard", "next_excard"])))
async def inventory(callback: CallbackQuery, callback_data: builders.Pagination, state: FSMContext):
    inline_id = callback.inline_message_id
    page_num = int(callback_data.page)

    data = await state.get_data()

    if "excard" not in data:
        account = await mongodb.get_user(callback.from_user.id)
        ui = account.get("ui", {}).get("store", {}).get("excards", {})

        page_num = ui.get("page", 0)

    if callback_data.action == "next_excard":
        page_num = (page_num + 1) % len(cards)
    elif callback_data.action == "prev_excard":
        page_num = (page_num - 1) % len(cards)

    card = list(cards.keys())[page_num]

    await state.update_data(excard=card)

    await mongodb.update_user(
        callback.from_user.id,
        {
            "ui.store.excards.page": page_num,
            "ui.store.excards.key": card,
        }
    )

    with suppress(TelegramBadRequest):
        card = list(cards.keys())[page_num]
        result = character_photo.card_stats(card)
        photo = InputMediaAnimation(media=result['avatar'])
        await state.update_data(excard=card)
        rarity = result['rarity']
        universe = result['universe']
        strength = result['arena']['strength']
        agility = result['arena']['agility']
        intelligence = result['arena']['intelligence']
        power = result['arena']['power']
        msg = (f"\n❖ ✨ Редкость: {rarity}"
               f"\n❖ 🗺 Вселенная: {universe}"
               f"\n\n   ✊🏻 Сила: {strength}"
               f"\n   👣 Ловкость: {agility}"
               f"\n   🧠 Интелект: {intelligence}"
               f"\n   ⚜️ Мощь: {power}")
        await callback.message.edit_media(photo, inline_id)
        await callback.message.edit_caption(inline_id,
                                            caption=f"🔖 {card}"
                                                    f"\n──❀*̥˚──◌──◌──❀*̥˚────"
                                                    f"<blockquote>{msg}</blockquote>"
                                                    f"\n──❀*̥˚──◌──◌──❀*̥˚────"
                                                    f"\n🔸Эксклюзивная аватарка",
                                            reply_markup=builders.excard_store(page_num))
    await callback.answer()


@router.callback_query(F.data == "buy_excard")
async def buy_keys(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    account = await mongodb.get_user(user_id)
    data = await state.get_data()

    card = data.get("excard")

    # 🔁 FALLBACK В MONGODB
    if not card:
        ui = account.get("ui", {}).get("excard", {})
        card = ui.get("key")

        if not card:
            await callback.answer(
                "❖ ✖️ Сессия устарела. Откройте эксклюзивных персонажей заново.",
                show_alert=True
            )
            return

    result = character_photo.card_stats(card)
    universe = result['universe']
    rarity = 'divine'

    characters = account.get('inventory', {}).get('characters', {})
    universe_chars = characters.get(universe, {})
    rarity_chars = universe_chars.get(rarity, [])

    if card in rarity_chars:
        await callback.answer(
            "❖ ✖️ У вас уже есть этот персонаж",
            show_alert=True
        )
        return

    await callback.message.answer_invoice(
        title=f"🔖 {card}",
        description="──❀*̥˚──◌──◌──❀*̥˚────",
        payload = f"buy_excard:{callback.from_user.id}:{card}",
        currency="XTR",
        prices=[LabeledPrice(label="XTR", amount=170)],
    )

@router.pre_checkout_query()
async def pre_checkout(pre: PreCheckoutQuery):
    payload = pre.invoice_payload

    if payload.startswith("buy_slave:"):
        _, user_id, slave = payload.split(":")
        account = await mongodb.get_user(int(user_id))
        if slave in account.get("inventory", {}).get("slaves", []):
            await pre.answer(ok=False, error_message="Эта рабыня уже у вас есть.")
            return

    if payload.startswith("buy_excard:"):
        _, user_id, card = payload.split(":")
        account = await mongodb.get_user(int(user_id))
        # можно повторить проверку карты

    if payload.startswith("buy_pass:"):
        _, user_id = payload.split(":")
        account = await mongodb.get_user(int(user_id))
        if account.get("account", {}).get("prime"):
            await pre.answer(ok=False, error_message="💮Pass уже активен.")
            return

    await pre.answer(ok=True)

@router.message(F.successful_payment)
async def successful_payment(message: Message, bot: Bot, state: FSMContext):
    payload = message.successful_payment.invoice_payload

    if payload.startswith("buy_slave:"):
        _, user_id, slave = payload.split(":")
        user_id = int(user_id)

        account = await mongodb.get_user(user_id)
        inventory_slaves = account.get("inventory", {}).get("slaves", [])

        # ⛔ защита от повторной покупки
        if slave in inventory_slaves:
            await message.answer(
                "❖ ⚠️ Эта рабыня у вас уже есть.\n"
                "Платёж отклонён."
            )
            return

        result = character_photo.slaves_stats(slave)

        await mongodb.push_slave(user_id, slave)
        await mongodb.update_user(
            user_id,
            {"tasks.last_shop_purchase": datetime.now()}
        )

        await message.answer(f"❖ 🔖 Вы успешно приобрели {result[1]}")

    if payload.startswith("buy_excard:"):
        _, user_id, card = payload.split(":")
        user_id = int(user_id)

        account = await mongodb.get_user(user_id)
        result = character_photo.card_stats(card)

        universe = result["universe"]
        rarity = "divine"

        inventory_cards = (
            account.get("inventory", {})
            .get("characters", {})
            .get(universe, {})
            .get(rarity, [])
        )

        if card in inventory_cards:
            await message.answer(
                "❖ ⚠️ Этот персонаж уже у вас есть.\n"
                "Покупка отменена."
            )
            return

        await mongodb.push(universe, rarity, card, user_id)
        await mongodb.update_user(
            user_id,
            {"tasks.last_shop_purchase": datetime.now()}
        )

        await message.answer(
            f"❖ 🔖 Вы успешно приобрели\n<blockquote>{card}</blockquote>"
        )


    elif payload == "buy_ticket":
        # Обработка покупки билета
        # await bot.refund_star_payment(message.from_user.id, message.successful_payment.telegram_payment_charge_id)
        await mongodb.update_value(message.from_user.id, {'inventory.items.tickets.keys': 1})
        await message.answer("❖ Вы успешно приобрели 🧧 священный билет")

    if payload.startswith("buy_pass:"):
        _, user_id = payload.split(":")
        user_id = int(user_id)
        account = await mongodb.get_user(user_id)

        if account.get("account", {}).get("prime"):
            await message.answer(
                "❖ ⚠️ У вас уже активирован 💮Pass.\n"
                "Повторная покупка невозможна."
            )
            return

        now = datetime.now()
        expiration = now + timedelta(days=30)

        await mongodb.update_user(
            user_id,
            {
                "account.prime": True,
                "pass_purchase": now,
                "pass_expiration": expiration,
            }
        )

        await message.answer(
            f"❖ ❇️ Вы успешно приобрели 💮Pass\n"
            f"<blockquote>⏱️ Действует до {expiration:%Y-%m-%d}</blockquote>"
        )

# @router.pre_checkout_query()
# async def process_pre_checkout_query(event: PreCheckoutQuery):
#     await event.answer(ok=True)


# @router.message(F.successful_payment)
# async def successful_payment(message: Message, bot: Bot):
#     data = await state.get_data()
#     result = character_photo.slaves_stats(data['slave'])
#     # await bot.refund_star_payment(message.from_user.id, message.successful_payment.telegram_payment_charge_id)
#     await mongodb.push_slave(user_id, data.get('slave'))
#     current_date = datetime.today().date()
#     current_datetime = datetime.combine(current_date, datetime.time(datetime.now()))
#     await mongodb.update_user(user_id, {"tasks.last_shop_purchase": current_datetime})
#
#     await message.answer(f"❖ 🔖 Вы успешно приобрели {result[1]}")
