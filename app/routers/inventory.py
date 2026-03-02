from contextlib import suppress
from typing import Tuple, List, Optional, Union

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    Message,
    InputMediaAnimation,
    InputMediaPhoto,
    InputMedia,
)

from app.data import mongodb, character_photo
from app.filters.chat_type import ChatTypeFilter
from app.keyboards import builders

router = Router()


async def get_inventory(user_id: int, rarity: str) -> Tuple[List[str], Optional[str]]:
    """
    Возвращает (invent_list, universe) или ([], None) при ошибке.
    Принимает как "common", так и "common_" варианты.
    """
    rarity_map = {
        "soccer_": "soccer",
        "halloween_": "halloween",
        "common_": "common",
        "rare_": "rare",
        "epic_": "epic",
        "legendary_": "legendary",
        "mythical_": "mythical",
        "divine_": "divine",
    }
    rarity = rarity_map.get(rarity, rarity)

    account = await mongodb.get_user(user_id)
    if not account:
        return [], None

    universe = account.get("universe")
    if not universe:
        return [], None

    characters = (
        account
        .get("inventory", {})
        .get("characters", {})
        .get(universe, {})
    )

    invent = characters.get(rarity, [])
    if invent is None:
        invent = []

    return invent, universe


# ----- Вспомогательная функция для безопасного редактирования сообщений/inline -----
async def _edit_media_and_caption(
    callback: Union[CallbackQuery, Message],
    media: Optional[InputMedia] = None,
    caption: Optional[str] = None,
    reply_markup=None,
    parse_mode: str = "HTML"
):
    """
    Безопасно редактирует media и/или caption у callback (inline или обычное сообщение).
    Если callback — Message (отправили команду), редактируем message.
    Если callback — CallbackQuery и inline_message_id присутствует — используем bot.edit_... с inline_message_id.
    """
    # callback может быть CallbackQuery или Message
    # у CallbackQuery есть поля .inline_message_id, .message, .bot
    inline_id = None
    bot = None
    message_obj = None

    if isinstance(callback, CallbackQuery):
        inline_id = callback.inline_message_id
        bot = callback.bot
        message_obj = callback.message
    else:
        # Message
        message_obj = callback

    try:
        if inline_id:
            # inline message (нет message_obj)
            if media is not None:
                await bot.edit_message_media(media=media, inline_message_id=inline_id)
            if caption is not None:
                await bot.edit_message_caption(
                    caption=caption,
                    inline_message_id=inline_id,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode
                )
        else:
            # Обычное сообщение — используем методы объекта message
            if media is not None and message_obj:
                await message_obj.edit_media(media)
            if caption is not None and message_obj:
                await message_obj.edit_caption(caption=caption, reply_markup=reply_markup, parse_mode=parse_mode)
    except TelegramBadRequest:
        # Пробрасываем, чтобы вызывающий мог обработать (или с suppress)
        raise


# ----- Открытие инвентаря (команда / кнопка в главном меню) -----
@router.message(
    ChatTypeFilter(chat_type=["private"]),
    F.text == "🥡 Инвентарь"
)
@router.callback_query(F.data == "inventory")
async def inventory_open(callback: Union[CallbackQuery, Message]):
    media_id = "CgACAgIAAx0CfstymgACRv5orIILKQTm88Zac71MqWBr9tYTQwAC8ZkAAu8IaUknwseMmKsSyTYE"

    # определим user_id и получим аккаунт (без фанатизма — если нет, корректно падаем)
    user_id = callback.from_user.id
    account = await mongodb.get_user(user_id)
    if not account:
        # если аккаунта нет — просим пользователя зарегистрироваться
        if isinstance(callback, CallbackQuery):
            await callback.answer("❖ ✖️ Вы не зарегистрированы. Введите /start", show_alert=True)
        else:
            await callback.answer("❖ ✖️ Вы не зарегистрированы. Введите /start")
        return

    universe = account.get('universe') or "Allstars"

    # безопасное получение количества по редкостям
    inv_chars = account.get('inventory', {}).get('characters', {}).get(universe, {})

    total_divine = len(inv_chars.get('divine', []))
    total_mythical = len(inv_chars.get('mythical', []))
    total_legendary = len(inv_chars.get('legendary', []))
    total_epic = len(inv_chars.get('epic', []))
    total_rare = len(inv_chars.get('rare', []))
    total_common = len(inv_chars.get('common', []))
    total_elements = 0
    for sublist in inv_chars.values():
        if isinstance(sublist, (list, tuple)):
            for item in sublist:
                if isinstance(item, str):
                    total_elements += 1

    buttons = [
        f"🌠 Божественные 🌟 {total_divine}",
        f"🌌 Мифические ⭐️ {total_mythical}",
        f"🌅 Легендарные ⭐️ {total_legendary}",
        f"🎆 Эпические ⭐️ {total_epic}",
        f"🎇 Редкие ⭐️ {total_rare}",
        f"🌁 Обычные ⭐️ {total_common}",
        "🔙 Назад"
    ]
    callbacks = ["divine", "mythical", "legendary", "epic", "rare", "common", "main_page"]

    if universe == "Allstars":
        if "halloween" in inv_chars:
            total_halloween = len(inv_chars.get('halloween', []))
            buttons.insert(0, f"👻 Halloween 🎃 {total_halloween}")
            callbacks.insert(0, "halloween")

    caption = (
        f"🥡 Инвентарь\n"
        f"── •✧✧• ──────────\n"
        f"<blockquote>❖ Здесь вы можете увидеть все ваши 🃏 карты и установить их в качестве основного 🎴 персонажа."
        f"\n❖ Выберите ✨ редкость карты, чтобы посмотреть.</blockquote>\n"
        f"➖➖➖➖➖➖➖➖➖\n"
        f"❖ 🃏 Количество карт: {total_elements}"
    )

    reply = builders.inline_builder(buttons, callbacks, row_width=[1])

    if isinstance(callback, CallbackQuery):
        # редактирование (inline или обычное сообщение)
        try:
            media = InputMediaAnimation(media=media_id)
            await _edit_media_and_caption(callback, media=media, caption=caption, reply_markup=reply)
        except TelegramBadRequest:
            # fallback — отправим просто ответ-анимацию (если редактирование не получилось)
            await callback.answer("Открываю инвентарь...")
            await callback.message.answer_animation(media=media_id, caption=caption, reply_markup=reply, parse_mode="HTML")
    else:
        # Message — просто отправляем анимацию с подписью
        await callback.answer_animation(
            animation=media_id,
            caption=caption,
            reply_markup=reply,
            parse_mode="HTML"
        )


# ----- Выбор редкости (главная логика просмотра персонажа) -----
@router.callback_query(F.data.in_(['soccer', 'halloween', 'common', 'rare', 'epic', 'legendary', 'mythical', 'divine']))
async def inventory_show_rarity(callback: CallbackQuery, state: FSMContext):
    # сохраняем выбранную редкость в state (и в случае падения позже — fallback в Mongo)
    await state.update_data(rarity=callback.data)

    inline_id = callback.inline_message_id
    user_id = callback.from_user.id
    invent, universe = await get_inventory(user_id, callback.data)
    if not invent:
        await callback.answer("❖ ✖️ У вас нет карт данной редкости", show_alert=True)
        return
    await mongodb.update_user(
        user_id,
        {
            "ui.inventory.rarity": callback.data,
            "ui.inventory.page": 0
        }
    )
    # Берём первую карточку как текущую
    character = invent[0]
    # сохраняем character/universe в state (чтобы пагинация/изменение работали быстро)
    await state.update_data(character=character, universe=universe, user_id=user_id)

    avatar = character_photo.get_stats(universe, character, 'avatar')
    avatar_type = character_photo.get_stats(universe, character, 'type')
    media = InputMediaPhoto(media=avatar) if avatar_type == 'photo' else InputMediaAnimation(media=avatar)

    rarity_text = character_photo.get_stats(universe, character, 'rarity')
    msg = f"❖ ✨ Редкость: {rarity_text}"
    if universe not in ['Allstars', 'Allstars(old)']:
        arena = character_photo.get_stats(universe, character, 'arena')
        msg = (
            f"❖ ✨ Редкость: {rarity_text}\n"
            f"❖ 🗺 Вселенная: {universe}\n\n"
            f"   ✊🏻 Сила: {arena.get('strength')}\n"
            f"   👣 Ловкость: {arena.get('agility')}\n"
            f"   🧠 Интелект: {arena.get('intelligence')}\n"
            f"   ⚜️ Мощь: {arena.get('power')}"
        )

    caption = (
        f"🎴 {character}"
        f"<blockquote>{msg}</blockquote>"
        f"\n──❀*̥˚──◌──◌──❀*̥˚"
        f"\n❖ 🔖 1 из {len(invent)}"
    )

    # reply_markup: пагинация
    reply_kb = builders.pagination_keyboard(universe, character)
    try:
        await _edit_media_and_caption(callback, media=media, caption=caption, reply_markup=reply_kb)
    except TelegramBadRequest:
        # если редактирование не удалось — присылаем alert
        await callback.answer("❖ ✖️ Не удалось отобразить карту. Повторите ещё раз.", show_alert=True)


# ----- Пагинация: prev / next (простая версия для обычного inventory) -----
@router.callback_query(builders.Pagination.filter(F.action.in_(["prev", "next"])))
async def inventory_pagination(callback: CallbackQuery, callback_data: builders.Pagination, state: FSMContext):
    inline_id = callback.inline_message_id
    page_num = int(callback_data.page)

    # сначала пробуем взять редкость из state
    user_data = await state.get_data()
    rarity = user_data.get("rarity")

    # fallback в MongoDB, если state пустой
    if not rarity:
        account = await mongodb.get_user(callback.from_user.id)
        if not account:
            await callback.answer("❖ ✖️ Сессия устарела. Откройте инвентарь заново.", show_alert=True)
            return
        # безопасный дефолт — common (обычно есть)
        if not rarity:
            account = await mongodb.get_user(callback.from_user.id)
            ui_inv = account.get("ui", {}).get("inventory", {})

            rarity = ui_inv.get("rarity")
            page_num = ui_inv.get("page", 0)

            if not rarity:
                await callback.answer(
                    "❖ ✖️ Сессия устарела. Откройте инвентарь заново.",
                    show_alert=True
                )
                return

    invent, universe = await get_inventory(callback.from_user.id, rarity)
    if not invent:
        await callback.answer("❖ ✖️ У вас нет карт данной редкости", show_alert=True)
        return

    if callback_data.action == "next":
        page_num = (page_num + 1) % len(invent)
    elif callback_data.action == "prev":
        page_num = (page_num - 1) % len(invent)

    await mongodb.update_user(
        callback.from_user.id,
        {
            "ui.inventory.rarity": rarity,
            "ui.inventory.page": page_num
        }
    )

    # обновляем state
    await state.update_data(character=invent[page_num], universe=universe)

    avatar = character_photo.get_stats(universe, invent[page_num], 'avatar')
    avatar_type = character_photo.get_stats(universe, invent[page_num], 'type')
    media = InputMediaPhoto(media=avatar) if avatar_type == 'photo' else InputMediaAnimation(media=avatar)

    rarity_text = character_photo.get_stats(universe, invent[page_num], 'rarity')
    msg = f"❖ ✨ Редкость: {rarity_text}"
    if universe not in ['Allstars', 'Allstars(old)']:
        arena = character_photo.get_stats(universe, invent[page_num], 'arena')
        msg = (
            f"❖ ✨ Редкость: {rarity_text}\n"
            f"❖ 🗺 Вселенная: {universe}\n\n"
            f"   ✊🏻 Сила: {arena.get('strength')}\n"
            f"   👣 Ловкость: {arena.get('agility')}\n"
            f"   🧠 Интелект: {arena.get('intelligence')}\n"
            f"   ⚜️ Мощь: {arena.get('power')}"
        )

    caption = (
        f"🎴 {invent[page_num]}"
        f"<blockquote>{msg}</blockquote>"
        f"\n──❀*̥˚──◌──◌──❀*̥˚"
        f"\n❖ 🔖 {page_num + 1} из {len(invent)}"
    )

    reply_kb = builders.pagination_keyboard(universe=universe, character=invent[page_num], page=page_num)

    with suppress(TelegramBadRequest):
        try:
            await _edit_media_and_caption(callback, media=media, caption=caption, reply_markup=reply_kb)
        except TelegramBadRequest:
            # если редактирование упало — отправим alert
            await callback.answer("❖ ✖️ Ошибка обновления. Откройте инвентарь заново.", show_alert=True)
            return

    await callback.answer()


# ----- Изменить основной персонаж (кнопка "Установить") -----
@router.callback_query(F.data == "change_character")
async def change_ch(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    data = await state.get_data()

    character = data.get("character")
    universe = data.get("universe")

    # 🔁 FALLBACK В MONGODB
    if not character or not universe:
        account = await mongodb.get_user(user_id)
        if not account:
            await callback.answer("❖ ✖️ Сессия устарела. Откройте инвентарь заново.", show_alert=True)
            return
        universe = account.get("universe")
        character = account.get("character", {}).get(universe)

        if not character:
            await callback.answer("❖ ✖️ Сессия устарела. Откройте инвентарь заново.", show_alert=True)
            return

    await mongodb.change_char(user_id, universe, character)
    await callback.answer("🎴 Вы успешно изменили персонажа", show_alert=True)


# ----- Простая обработка текстовой команды "Карты" / chat-inventory (логика как у open) -----
@router.message(F.text.in_(["Карты", "карты", "инвентарь", "Инвентарь"]))
@router.callback_query(F.data.startswith("inventory_"))
async def inventory_chat(callback: Union[CallbackQuery, Message], state: FSMContext):
    # Эта функция делает практически то же, что inventory_open, но c user_id в callback (chat view).
    # Для простоты — делаем через inventory_open: просто переходим к тому же представлению.
    # Но тут есть проверка владельца (если callback содержит _{user_id}).
    if isinstance(callback, CallbackQuery) and callback.data.startswith("inventory_"):
        try:
            user_cb_id = int(callback.data.replace("inventory_", ""))
        except Exception:
            await callback.answer("❖ ✖️ Неправильный инвентарь.", show_alert=True)
            return

        # если callback инициирован не владельцем — запрет
        if user_cb_id != callback.from_user.id:
            await callback.answer("❖ ✖️ Это не ваш инвентарь", show_alert=True)
            return

    # просто вызываем тот же обработчик открытия
    await inventory_open(callback)
