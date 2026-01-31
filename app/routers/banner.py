from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery, InputMediaAnimation, Message
from app.data import mongodb
from app.keyboards.builders import inline_builder
from app.routers import gacha
from app.filters.chat_type import ChatTypeFilter

router = Router()


@router.message(ChatTypeFilter(chat_type=["private"]), F.text == "🎐 Баннеры")
@router.callback_query(F.data == "banner")
async def banner(callback: CallbackQuery | Message):
    user_id = callback.from_user.id
    account = await mongodb.get_user(user_id)

    pattern = dict(
        caption=f"🎐 <b><i>Текущие баннеры:</i></b>"
                f"\n── •✧✧• ──────────"
                # f"\n\n ☆ • 👻 <b>Хэллоуин</b>"
                f"\n<blockquote> ☆ 🔮 <b>Стандартный баннер</b></blockquote>",
        parse_mode=ParseMode.HTML,
        reply_markup=inline_builder(
            ["🔮 Ст. баннер", " 🔙 Назад"],
            ["standard", "main_page"],
            row_width=[1, 1, 1]
            )
    )

    media_id = "CgACAgIAAx0CfstymgACPnlna-1cMqyMz6QaXP9vAcL_PlGkPAACJGMAArowYUvHL8VjyDqLszYE"
    media = InputMediaAnimation(media=media_id)
    if isinstance(callback, CallbackQuery):
        inline_id = callback.inline_message_id
        await callback.message.edit_media(media, inline_id)
        await callback.message.edit_caption(inline_id, **pattern)
    else:
        await callback.answer_animation(media_id, **pattern)


@router.callback_query(F.data == "halloween_banner")
async def halloween(callback: CallbackQuery):
    inline_id = callback.inline_message_id
    user_id = callback.from_user.id
    account = await mongodb.get_user(user_id)
    if account['universe'] != "Allstars":
        await callback.answer("❖ Этот баннер доступен только во вселенной Allstars", show_alert=True)
        return
    if "halloween" not in account['inventory']['items']:
        await mongodb.update_user(user_id, {"inventory.items.halloween": 0})
    account = await mongodb.get_user(user_id)
    items = account['inventory']['items']['halloween']

    pattern = dict(
        caption=f"❖  👻  <b>Хэллоуин</b>"
                f"\n── •✧✧• ──────────"
                f"\n❖ <b><i>🧛 Ивент Хэллоуин:</i></b>"
                f"\n • 🧟 Соберите специальные 🎃 предметы события и учвствуйте в ивентовом банере"
                f"\n • ⚰️ В баннере присутствуют только специальные карты события 🕸Хэллоуин"
                f"\n── •✧✧• ──────────"
                f"\n❃  🎃 ⋗ <b>{items}</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=inline_builder(
            ["Использовать 🎃100", " 🔙 Назад"],
            ["halloween_item", "banner"],
            row_width=[1]
            )
    )

    media_id = "CgACAgIAAx0CfstymgACJCdnF97OgftOVAIKHpJeXHyLC_xF2gAC2VsAAo5AwUgkkLpf0fTTtTYE"
    media = InputMediaAnimation(media=media_id)
    await callback.message.edit_media(media, inline_id)
    await callback.message.edit_caption(inline_id, **pattern)


@router.callback_query(F.data == "soccer")
async def soccer_item(callback: CallbackQuery):
    inline_id = callback.inline_message_id
    user_id = callback.from_user.id
    account = await mongodb.get_user(user_id)
    if account['universe'] != "Allstars":
        await callback.answer("❖ Этот баннер доступен только во вселенной Allstars", show_alert=True)
        return
    if "soccer" not in account['inventory']['items']:
        await mongodb.update_user(user_id, {"inventory.items.soccer": 0})
    account = await mongodb.get_user(user_id)
    items = account['inventory']['items']['soccer']

    pattern = dict(
        caption=f"❖  ⚽️  <b>Soccer</b>"
                f"\n── •✧✧• ──────────"
                f"\n❖ <b><i>⚽️ Футбольный ивент:</i></b>"
                f"\n── •✧✧• ──────────"
                f"\n • ⚽️ Соберите специальные ⚽️ предметы события и учвствуйте в ивентовом банере"
                f"\n • ⚽️ В баннере присутствуют только специальные карты события ⚽️ Soccer"
                f"\n── •✧✧• ──────────"
                f"\n❃  ⚽️ ⋗ <b>{items}</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=inline_builder(
            ["Использовать ⚽️100", " 🔙 Назад"],
            ["soccer_item", "banner"],
            row_width=[1]
            )
    )

    media_id = "CgACAgIAAx0CfstymgACI35nF2VmP_Vl5dPIu44-L8KsHVHNFQACQVwAAo5AuUhHh35J13Kc5jYE"
    media = InputMediaAnimation(media=media_id)
    await callback.message.edit_media(media, inline_id)
    await callback.message.edit_caption(inline_id, **pattern)


@router.callback_query(F.data == "standard")
async def standard(callback: CallbackQuery):
    inline_id = callback.inline_message_id
    user_id = callback.from_user.id
    account = await mongodb.get_user(user_id)

    ticket_data = account['inventory']['items']['tickets']
    keys = ticket_data['keys']
    golden = ticket_data['golden']
    common = ticket_data['common']

    pattern = dict(
        caption=f"\n❖ ✨ <b><i>Шансы дропа 🂡</i></b>"
                f"\n┅┅━─━┅┄ ⟛ ┄┅━─━┅┅"
                "\n<blockquote>╭┈๋જ‌›<b>Divine cards</b> "
                "\n🌠┄🎟⋗ 0.1% 🎫⋗ 0.5% 🧧⋗ 10%"
                "\n╭┈๋જ‌›<b>Mythical cards</b> "
                "\n🌌┄🎟⋗ 0.4% 🎫⋗ 1% 🧧⋗ 25%"
                "\n╭┈๋જ‌›Legendary cards"
                "\n🌅┄🎟⋗ 2% 🎫⋗ 11.5% 🧧⋗ 65%"
                "\n╭┈๋જ‌›Epic cards"
                "\n🎆┄🎟⋗ 6.0% 🎫⋗ 24%"
                "\n╭┈๋જ‌›Rare cards"
                "\n🎇┄🎟⋗ 13.5% 🎫⋗ 33%"
                "\n╭┈๋જ‌›Common cards"
                "\n🌁┄🎟⋗ 78% 🎫⋗ 30%"
                "\n╰──────────────╯</blockquote>"
                f"\n❃  🧧 ⋗ <b>{keys}</b>   🎫 ⋗ <b>{golden}</b>   🎟 ⋗ <b>{common}</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=inline_builder(
            ["🧧 Открыть", "🎫 Призвать", "🎟 Призвать", " 🔙 Назад", "📋 Правила"],
            ["golden_key", "golden", "common_summon", "banner", "banner_rules"],
            row_width=[1, 2, 2]
            )
    )

    media_id = "CgACAgIAAx0CfstymgACPnlna-1cMqyMz6QaXP9vAcL_PlGkPAACJGMAArowYUvHL8VjyDqLszYE"
    media = InputMediaAnimation(media=media_id)
    await callback.message.edit_media(media, inline_id)
    await callback.message.edit_caption(inline_id, **pattern)


@router.callback_query(F.data == "soccer_item")
async def soccer_item(callback: CallbackQuery):
    await gacha.card_gacha(callback.from_user.id, callback)


@router.callback_query(F.data == "halloween_item")
async def halloween_item(callback: CallbackQuery):
    await gacha.card_gacha(callback.from_user.id, callback)


@router.callback_query(F.data == "golden_key")
async def golden_key(callback: CallbackQuery):
    await gacha.card_gacha(callback.from_user.id, callback)


@router.callback_query(F.data == "golden")
async def golden(callback: CallbackQuery):
    await gacha.card_gacha(callback.from_user.id, callback,)


@router.callback_query(F.data == "common_summon")
async def common(callback: CallbackQuery):
    await gacha.card_gacha(callback.from_user.id, callback)


@router.callback_query(F.data == "banner_rules")
async def banner_rules(callback: CallbackQuery):
    await callback.message.answer(
        f"❖ 📋 Правила Баннера"
        "\n── •✧✧• ──────────"
        "\nhttps://teletype.in/@dire_hazard/x1#S1Pc",
        reply_markup=inline_builder(["☑️"], ["delete"], row_width=[1])
    )
    await callback.answer()


@router.callback_query(F.data == "chance")
async def chance(callback: CallbackQuery):
    await callback.message.edit_caption(
        caption=f"❖  🔮 <b>Шансы Призыва</b>"
                f"\n── •✧✧• ──────────"
                f"\n 🧧 <b><i>Шансы священного призыва:</i></b>"
                f"\n\n   🌠 Божественные карты ⋗ <i>25%</i>"
                f"\n\n   🌌 Мифические карты ⋗ <i>35%</i>"
                f"\n\n   🌅 Легендарные карты ⋗ <i>40%</i>"
                f"\n── •✧✧• ──────────"
                f"\n 🎫 <b><i>Шансы золотого призыва:</i></b>"
                f"\n\n 🌠 Божественные карты ⋗ <i>1%</i>"
                f"\n\n   🌌 Мифические карты ⋗ <i>6%</i>"
                f"\n\n   🌅 Легендарные карты ⋗ <i>21%</i>"
                f"\n\n   🎆 Эпические карты ⋗ <i>46%</i>"
                f"\n\n   🎇 Редкие карты ⋗ <i>26%</i>"
                f"\n── •✧✧• ──────────"
                f"\n 🎟 <b><i>Шансы обычного призыва:</i></b>"
                f"\n\n 🌠 Божественные карты ⋗ <i>0.03%</i>"
                f"\n\n   🌌 Мифические карты ⋗ <i>0.3%</i>"
                f"\n\n   🌅 Легендарные карты ⋗ <i>2.3%</i>"
                f"\n\n   🎆 Эпические карты ⋗ <i>12.3%</i>"
                f"\n\n   🎇 Редкие карты ⋗ <i>30.3%</i>"
                f"\n\n   🌁 Обычные карты ⋗ <i>50.87%</i> "
                f"\n── •✧✧• ──────────",
        parse_mode=ParseMode.HTML,
        reply_markup=inline_builder(
            ["🔙 Назад"],
            ["banner_rules"],
            row_width=[2, 2]
        )
    )
    await callback.answer()
