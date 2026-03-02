from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery, Message, InputMediaPhoto
from app.data import character_photo
from app.data import mongodb
from app.recycling import profile
from app.filters.chat_type import ChatTypeFilter
from app.keyboards.builders import inline_builder

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

        msg = (f'\n  •  <tg-emoji emoji-id="5316791950462950306">❌</tg-emoji> Сила: {strength}'
               f'\n  •  <tg-emoji emoji-id="5949588538952518773">❌</tg-emoji> Ловкость: {agility}'
               f'\n  •  <tg-emoji emoji-id="5371053287380361807">❌</tg-emoji> Интелект: {intelligence}'
               f'\n  •  <tg-emoji emoji-id="5431420156532235514">❌</tg-emoji> Мощь: {power}')

        pattern = dict(
            caption=f'❖      <tg-emoji emoji-id="5454014806950429357">❌</tg-emoji> <b>Арена</b> <tg-emoji emoji-id="5206198853283377523">❌</tg-emoji>'
                     # f"\n── •✧✧• ──────"
                    f'\n<tg-emoji emoji-id="5314365873761302196">❌</tg-emoji><tg-emoji emoji-id="5314312126540561977">❌</tg-emoji><tg-emoji emoji-id="5294189049412598712">❌</tg-emoji><tg-emoji emoji-id="5294211542156330171">❌</tg-emoji><tg-emoji emoji-id="5294446055960623166">❌</tg-emoji><tg-emoji emoji-id="5294189049412598712">❌</tg-emoji><tg-emoji emoji-id="5314516781732214873">❌</tg-emoji><tg-emoji emoji-id="5314575051553520578">❌</tg-emoji>'
                    f'\n<blockquote><tg-emoji emoji-id="5399959611283356481">❌</tg-emoji> <b>{character}</b>'
                    f'\n<tg-emoji emoji-id="5269717137508805226">❌</tg-emoji> Ранг: <b>{rank}</b>'
                    f"{msg}</blockquote>"
                    f'\n<tg-emoji emoji-id="5195286329226706640">❌</tg-emoji><tg-emoji emoji-id="5195102113784414350">❌</tg-emoji><tg-emoji emoji-id="5195102113784414350">❌</tg-emoji><tg-emoji emoji-id="5195102113784414350">❌</tg-emoji><tg-emoji emoji-id="5195102113784414350">❌</tg-emoji><tg-emoji emoji-id="5195102113784414350">❌</tg-emoji><tg-emoji emoji-id="5195102113784414350">❌</tg-emoji><tg-emoji emoji-id="5195439792703162670">❌</tg-emoji>'
                    f'\n<b><i> <tg-emoji emoji-id="5447112111605964162">❌</tg-emoji> {wins} Побед | <tg-emoji emoji-id="5380033625909634211">❌</tg-emoji> {exp} XP </i></b>',
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
        txt = '❖            <tg-emoji emoji-id="5454014806950429357">❌</tg-emoji> <b>Арена</b> <tg-emoji emoji-id="5206198853283377523">❌</tg-emoji>'
        rows = [2, 2]
    await profile.update_rank(callback.from_user.id, account.get("battle", {}).get("stats", {}).get("wins", 0))

    in_battle = await mongodb.in_battle()

    pattern = dict(
        caption=f"{txt}"
                # f"\n── •✧✧• ──────────"
                f'\n<tg-emoji emoji-id="5314365873761302196">❌</tg-emoji><tg-emoji emoji-id="5314312126540561977">❌</tg-emoji><tg-emoji emoji-id="5294189049412598712">❌</tg-emoji><tg-emoji emoji-id="5294189049412598712">❌</tg-emoji><tg-emoji emoji-id="5294211542156330171">❌</tg-emoji><tg-emoji emoji-id="5294446055960623166">❌</tg-emoji><tg-emoji emoji-id="5294189049412598712">❌</tg-emoji><tg-emoji emoji-id="5294189049412598712">❌</tg-emoji><tg-emoji emoji-id="5314516781732214873">❌</tg-emoji><tg-emoji emoji-id="5314575051553520578">❌</tg-emoji>'
                f'\n<blockquote><tg-emoji emoji-id="5375161616872520280">❌</tg-emoji> PvP - Битва против реального <tg-emoji emoji-id="5192998928429113725">❌</tg-emoji> игрока, который так же <tg-emoji emoji-id="5010357961017524878">❌</tg-emoji> ищет соперника</blockquote>'
                # f"\n➖➖➖➖➖➖➖➖➖➖➖"
                f'\n<blockquote><tg-emoji emoji-id="5226639745106330551">❌</tg-emoji> AI - Битва против <tg-emoji emoji-id="5134472688986756318">❌</tg-emoji> Искуственного Интелекта. Удобно для <tg-emoji emoji-id="5463274047771000031">❌</tg-emoji> тренировок</blockquote>'
                f'\n<tg-emoji emoji-id="5195286329226706640">❌</tg-emoji><tg-emoji emoji-id="5195102113784414350">❌</tg-emoji><tg-emoji emoji-id="5195102113784414350">❌</tg-emoji><tg-emoji emoji-id="5195102113784414350">❌</tg-emoji><tg-emoji emoji-id="5195102113784414350">❌</tg-emoji><tg-emoji emoji-id="5195102113784414350">❌</tg-emoji><tg-emoji emoji-id="5195102113784414350">❌</tg-emoji><tg-emoji emoji-id="5195102113784414350">❌</tg-emoji><tg-emoji emoji-id="5195102113784414350">❌</tg-emoji><tg-emoji emoji-id="5195439792703162670">❌</tg-emoji>'
                f'\n<i><tg-emoji emoji-id="5195086398499087308">❌</tg-emoji> Сейчас в битве <tg-emoji emoji-id="5341772463804002252">❌</tg-emoji> {in_battle} игроков.</i>',
        parse_mode=ParseMode.HTML,
        reply_markup=inline_builder(
            buttons,
            calls,
            rows)
    )

    media = InputMediaPhoto(
        media='AgACAgIAAx0CfstymgACU_hpiDvANrlbFmiwNPOHRh6OaO1Q_gAC1hJrG5GhSUhtSq4yXI39HAEAAwIAA3kAAzoE'
    )
    await callback.message.edit_media(media)
    await callback.message.edit_caption(**pattern)
