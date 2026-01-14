from datetime import datetime, timedelta

from aiogram import Router, F

from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.enums import ParseMode, ContentType
from aiogram.exceptions import TelegramBadRequest

from filters.chat_type import ChatTypeFilter
from keyboards.builders import inline_builder
from data import mongodb

router = Router()

def _dt0() -> datetime:
    # «Давно в прошлом» — чтобы .date() точно != today
    return datetime(2000, 1, 1, 0, 0, 0)

def _done_today(ts: datetime, today) -> bool:
    try:
        return isinstance(ts, datetime) and ts.date() == today
    except Exception:
        return False

@router.message(ChatTypeFilter(chat_type=["private"]), F.text == "📜 Квесты")
@router.callback_query(F.data == "quests")
async def quests(entry: CallbackQuery | Message):
    user_id = entry.from_user.id
    now = datetime.now()
    today = now.date()

    account = await mongodb.get_user(user_id)
    tasks = account.get("tasks") or {}

    # Инициализация, НО без «сбросов»
    tasks.setdefault("last_summon", _dt0())
    tasks.setdefault("last_arena_fight", _dt0())
    tasks.setdefault("last_shop_purchase", _dt0())
    tasks.setdefault("last_free_summon", _dt0())
    tasks.setdefault("last_dungeon", _dt0())
    tasks.setdefault("last_get_reward", _dt0())
    tasks["last_tasks_view"] = now

    await mongodb.update_user(user_id, {"tasks": tasks})
    account["tasks"] = tasks

    # Статусы «выполнено сегодня»
    reward = "⌞⟡⌝" if _done_today(tasks["last_get_reward"], today) else "⌞   ⌝"
    summon = "⌞⟡⌝" if _done_today(tasks["last_summon"], today) else "⌞   ⌝"
    arena_fight = "⌞⟡⌝" if _done_today(tasks["last_arena_fight"], today) else "⌞   ⌝"
    dungeon = "⌞⟡⌝" if _done_today(tasks["last_dungeon"], today) else "⌞   ⌝"
    free_summon = "⌞⟡⌝" if _done_today(tasks["last_free_summon"], today) else "⌞   ⌝"
    shop_purchase = "⌞⟡⌝" if _done_today(tasks["last_shop_purchase"], today) else "⌞   ⌝"

    # PRIME и срок действия
    prime = account.get("account", {}).get("prime", False)
    pass_expires = account.get("pass_expiration")
    if prime:
        if not pass_expires:
            await mongodb.update_user(user_id, {"pass_expiration": now + timedelta(days=30)})
        elif now > pass_expires:
            await mongodb.update_user(user_id, {"account.prime": False})
            prime = False

    emoji = "💮" if prime else ""
    gold = "4" if prime else "2"
    money = "2500" if prime else "1400"
    msg = "" if prime else "\n💮Pass увеличивают награду"

    # Безопасная инициализация инвентаря
    if account.get("inventory", {}).get("items") is None:
        await mongodb.update_user(user_id, {"inventory.items": {}})
    if "halloween" not in account.get("inventory", {}).get("items", {}):
        await mongodb.update_user(user_id, {"inventory.items.halloween": 0})

    # Таймер до полуночи
    midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    delta = midnight - now
    hours, remainder = divmod(delta.seconds, 3600)
    minutes = remainder // 60
    time_until_reset = f"{hours}ч {minutes}м"

    caption = (
        "༯ 📜 Ежедневные квесты ᝰ."
        "\n· · · ─ ·𖥸· ─ · ·· · ─ ·𖥸· ─ · · ·"
        f"\n<blockquote>{summon} • 🔮 Совершите призыв"
        f"\n{arena_fight} • ⚔️ Сразитесь в арене"
        f"\n{free_summon} • 🎴 Бесплатный призыв"
        f"\n{dungeon} • ⛩ Продайте ресурсы"
        f"\n{shop_purchase} • 🏪 Совершите покупку</blockquote>"
        f"\n༯ 🎁 Награды:"
        f"\n<blockquote> {emoji} {reward} • 🎫 {gold}× золотой билет"
        f"\n {emoji} {reward} • 💴 {money} ¥</blockquote>"
        f"{msg}"
        # "\n── •✧✧• ─────────"
        "\n➖➖➖➖➖➖➖➖➖➖"
        f"\n♻️ Обнуление: ⏱️ {time_until_reset}"
    )

    pattern = dict(
        caption=caption,
        parse_mode=ParseMode.HTML,
        reply_markup=inline_builder(
            ["🎁 Получить", "🔙 Меню"],
            ["get_quest_reward", "main_page"],
            row_width=[1, 1]
        )
    )

    media_id = InputMediaPhoto(
        media='AgACAgIAAx0CfstymgACREJonaJZzJQmnV2NWIuC3llVipz-OAACB_cxG3oF8Uhwd3VJrmw1SgEAAwIAA3kAAzYE'
    )

    # Безопасное редактирование / отправка
    try:
        if isinstance(entry, CallbackQuery) and getattr(entry.message, "content_type", None) == ContentType.PHOTO:
            await entry.message.edit_media(media=media_id)
            await entry.message.edit_caption(**pattern)
            await entry.answer()
        else:
            if isinstance(entry, CallbackQuery):
                await entry.message.answer_photo(media_id.media, **pattern)
                await entry.answer()
            else:
                await entry.answer_photo(media_id.media, **pattern)
    except TelegramBadRequest:
        # Fallback на новый месседж
        if isinstance(entry, CallbackQuery):
            await entry.message.answer_photo(media_id.media, **pattern)
            await entry.answer()
        else:
            await entry.answer_photo(media_id.media, **pattern)


@router.callback_query(F.data == "get_quest_reward")
async def get_quest_reward(callback: CallbackQuery):
    user_id = callback.from_user.id
    now = datetime.now()
    today = now.date()

    account = await mongodb.get_user(user_id)
    tasks = account.get("tasks") or {}
    for k in ("last_summon","last_arena_fight","last_shop_purchase","last_free_summon","last_dungeon","last_get_reward"):
        tasks.setdefault(k, _dt0())

    if _done_today(tasks["last_get_reward"], today):
        await callback.answer("❖ ⏱️ Награды на сегодня уже получены, ♻️ возвращайтесь завтра!", show_alert=True)
        return

    all_done = all(_done_today(tasks[k], today) for k in (
        "last_summon","last_arena_fight","last_dungeon","last_free_summon","last_shop_purchase"
    ))
    if not all_done:
        await callback.answer("❖ ✖️ Не все задания выполнены", show_alert=True)
        return

    # Гарантируем наличие путей
    inv = account.setdefault("inventory", {}).setdefault("items", {})
    inv.setdefault("tickets", {}).setdefault("golden", 0)
    inv.setdefault("halloween", 0)

    prime = account.get("account", {}).get("prime", False)
    if prime:
        await mongodb.update_user(user_id, {
            "account.money": account["account"]["money"] + 2500,
            "inventory.items.tickets.golden": inv["tickets"]["golden"] + 5,
            "tasks.last_get_reward": now
        })
    else:
        await mongodb.update_user(user_id, {
            "account.money": account["account"]["money"] + 1400,
            "inventory.items.tickets.golden": inv["tickets"]["golden"] + 3,
            "inventory.items.halloween": inv["halloween"] + 65,
            "tasks.last_get_reward": now
        })

    await callback.answer("❖ ✅ Награды получены", show_alert=True)
