from aiogram import Router, F
from aiogram.types import CallbackQuery, InputMediaAnimation
from data import mongodb
from keyboards import builders

router = Router()


@router.callback_query(F.data == "battles")
async def battles(callback: CallbackQuery):
    inline_id = callback.inline_message_id
    media_id = "CgACAgIAAx0CfstymgACBMRlr8Vb3T5DyVkPXoV_MUnfSukjtwACpEMAAlw4gUmZk2SI3nXsMDQE"
    media = InputMediaAnimation(media=media_id)
    account = await mongodb.get_user(callback.from_user.id)
    total_divine = len(account['inventory']['characters']['divine'])
    total_mythical = len(account['inventory']['characters']['mythical'])
    total_legendary = len(account['inventory']['characters']['legendary'])
    total_epic = len(account['inventory']['characters']['epic'])
    total_rare = len(account['inventory']['characters']['rare'])
    total_common = len(account['inventory']['characters']['common'])
    total_elements = sum(len(account['inventory']['characters'][sublist]) for sublist in account['inventory']['characters'])
    await callback.message.edit_media(media, inline_id)
    await callback.message.edit_caption(inline_id, f"🥡 Инвентарь"
                                                   f"\n── •✧✧• ──────────"
                                                   f"\n 🌠 Божественные 🎴 карты: {total_divine}"
                                                   f"\n\n 🌌 Мифические 🎴 карты: {total_mythical}"
                                                   f"\n\n 🌅 Легендарные 🎴 карты: {total_legendary}"
                                                   f"\n\n 🎆 Эпические 🎴 карты: {total_epic}"
                                                   f"\n\n 🎇 Редкие 🎴 карты: {total_rare}"
                                                   f"\n\n 🌁 Обычные 🎴 карты: {total_common}"
                                                   f"\n── •✧✧• ──────────"
                                                   f"\n❖ 🎴 Количество карт: {total_elements}",
                                        reply_markup=builders.inline_builder(
                                            ["🌠 Божественные карты", "🌌 Мифические карты", "🌅 Легендарные карты",
                                             "🎆 Эпические карт"]))

