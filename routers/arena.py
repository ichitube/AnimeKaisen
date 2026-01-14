from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery, Message, InputMediaPhoto
from data import character_photo
from data import mongodb
from recycling import profile
from filters.chat_type import ChatTypeFilter
from keyboards.builders import inline_builder

router = Router()


@router.message(ChatTypeFilter(chat_type=["private"]), F.text.in_(["🏟️ Арена", "🃏 Битва"]))
@router.callback_query(F.data == "arena")
async def arena(callback: CallbackQuery | Message, stop=0):
    account = await mongodb.get_user(callback.from_user.id)
    await profile.update_rank(callback.from_user.id, account.get("battle", {}).get("stats", {}).get("wins", 0))


    rank = await profile.rerank(account['stats']['rank'])
    universe = account['universe']
    character = account['character'][account['universe']]
    exp = account['stats']['exp']
    wins = account['battle']['stats']['wins']

    if account['universe'] not in ['Allstars']:
        buttons = ["⚔️ Битва", "⛓ Рабыня", "🏆 Рейтинг", "🔙 Назад"]
        calls = ["battle_arena", "slave", "battle_rating", "tokio"]
        strength = character_photo.get_stats(universe, character, 'arena')['strength']
        agility = character_photo.get_stats(universe, character, 'arena')['agility']
        intelligence = character_photo.get_stats(universe, character, 'arena')['intelligence']
        power = character_photo.get_stats(universe, character, 'arena')['power']

        msg = (f"\n  •  ✊🏻 Сила: {strength}"
               f"\n  •  👣 Ловкость: {agility}"
               f"\n  •  🧠 Интелект: {intelligence}"
               f"\n  •  ⚜️ Мощь: {power}")

        pattern = dict(
            caption=f"❖ 🏟️ <b>Арена</b>  ⚔️"
                    f"\n── •✧✧• ──────"
                    f"\n<blockquote>🎴 <b>{character}</b>"
                    f"\n🎐 <b>{rank}</b>"
                    f"{msg}</blockquote>"
                    f"\n 👑 {wins} Побед | 🀄️ {exp} XP",
            parse_mode=ParseMode.HTML,
            reply_markup=inline_builder(
                buttons,
                calls,
                row_width=[1, 2, 1])
        )

        if isinstance(callback, CallbackQuery):
            if stop == 0:
                media = InputMediaPhoto(
                    media='AgACAgIAAx0CfstymgACGt1mw15fTEgmIIHqVhdpBhzEZVm-lAACnOwxG2zEGUqsfpo-_pkKnAEAAwIAA3kAAzUE'
                )
                await callback.message.edit_media(media)
                await callback.message.edit_caption(**pattern)
            else:
                media = 'AgACAgIAAx0CfstymgACGt1mw15fTEgmIIHqVhdpBhzEZVm-lAACnOwxG2zEGUqsfpo-_pkKnAEAAwIAA3kAAzUE'
                await callback.message.answer_photo(media, **pattern)
        else:
            media = 'AgACAgIAAx0CfstymgACGt1mw15fTEgmIIHqVhdpBhzEZVm-lAACnOwxG2zEGUqsfpo-_pkKnAEAAwIAA3kAAzUE'
            await callback.answer_photo(media, **pattern)
    else:
        buttons = ["⚔️ Битва", "⛓ Рабыня", "🏆 Рейтинг", "🔙 Назад"]
        calls = ["battle_arena", "slave", "battle_rating", "tokio"]
        strength = character_photo.get_stats(universe, character, 'arena')['strength']
        agility = character_photo.get_stats(universe, character, 'arena')['agility']
        intelligence = character_photo.get_stats(universe, character, 'arena')['intelligence']
        power = character_photo.get_stats(universe, character, 'arena')['power']

        msg = (f"\n  •  ✊🏻 Сила: {strength}"
               f"\n  •  👣 Ловкость: {agility}"
               f"\n  •  🧠 Интелект: {intelligence}"
               f"\n  •  ⚜️ Мощь: {power}")

        pattern = dict(
            caption=f"❖  🃏 <b>Битва</b>  ⚔️"
                    f"\n── •✧✧• ──────"
                    f"\n<blockquote>🎴 <b>{character}</b>"
                    f"\n🎐 <b>{rank}</b>"
                    f"{msg}</blockquote>"
                    "\n➖➖➖➖➖➖➖➖"
                    f"\n 👑 {wins} Побед | 🀄️ {exp} XP",
            parse_mode=ParseMode.HTML,
            reply_markup=inline_builder(
                buttons,
                calls,
                row_width=[1, 2, 1])
        )

        if isinstance(callback, CallbackQuery):
            if stop == 0:
                media = InputMediaPhoto(
                    media='AgACAgIAAx0CfstymgACP51oE0hoi_mMTaOVSUAOmYomfKVqRAACtvUxGzgreUijp7grm4wDXgEAAwIAA3kAAzYE'
                )
                await callback.message.edit_media(media)
                await callback.message.edit_caption(**pattern)
            else:
                media = 'AgACAgIAAx0CfstymgACP51oE0hoi_mMTaOVSUAOmYomfKVqRAACtvUxGzgreUijp7grm4wDXgEAAwIAA3kAAzYE'
                await callback.message.answer_photo(media, **pattern)
        else:
            media = 'AgACAgIAAx0CfstymgACP51oE0hoi_mMTaOVSUAOmYomfKVqRAACtvUxGzgreUijp7grm4wDXgEAAwIAA3kAAzYE'
            await callback.answer_photo(media, **pattern)


@router.callback_query(F.data == "battle_arena")
async def b_arena(callback: CallbackQuery | Message):
    account = await mongodb.get_user(callback.from_user.id)
    if account['universe'] in ['Allstars']:
        buttons = ["⚔️ PvP", "✨ AI", "🃏 Колода", "🔙 Назад", "📜 Правила"]
        calls = ["card_opponent", "ai_card_opponent", "deck", "arena", "battle_rules"]
        txt = "❖  🃏 <b>Битва</b>  ⚔️"
        rows = [2, 1, 2]
    else:
        buttons = ["⚔️ PvP", "✨ AI", "🔙 Назад", "📜 Правила"]
        calls = ["search_opponent", "ai_battle", "arena", "battle_rules"]
        txt = "❖  🏟️ <b>Арена</b>  ⚔️"
        rows = [2, 2]
    await profile.update_rank(callback.from_user.id, account.get("battle", {}).get("stats", {}).get("wins", 0))

    in_battle = await mongodb.in_battle()

    pattern = dict(
        caption=f"{txt}"
                f"\n── •✧✧• ──────────"
                f"\n<blockquote>⚔️ PvP - Битва против реального 👤 игрока который так же 🔎 ищет соперника</blockquote>"
                f"\n➖➖➖➖➖➖➖➖➖➖➖"
                f"\n<blockquote>✨ AI - Битва против 🤖 Искуственного Интелекта. Удобно для 🎯 тренировок</blockquote>"
                f"\n<i>🌊 В битве ⚔️ {in_battle} игроков</i> 🌊",
        parse_mode=ParseMode.HTML,
        reply_markup=inline_builder(
            buttons,
            calls,
            rows)
    )

    media = InputMediaPhoto(
        media='AgACAgIAAxkBAAEBGppm6oI246rBQNH-lZFRiZFD6TbJlgACeuUxG1fhUEt5QK8VqfcCQQEAAwIAA3gAAzYE'
    )
    await callback.message.edit_media(media)
    await callback.message.edit_caption(**pattern)
