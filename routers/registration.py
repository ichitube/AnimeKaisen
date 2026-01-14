import re

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InputMediaAnimation
from data import mongodb
from filters.chat_type import ChatTypeFilter
from keyboards.builders import inline_builder, profile, rm, get_common, menu_card_button, menu_button
from routers import main_menu
from routers.gacha import first_summon
from utils.states import Form
from routers import settings

router = Router()

EMOJI_PATTERN = re.compile("[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F700-\U0001F77F\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF]+")


@router.message(ChatTypeFilter(chat_type=["private"]), Command("start"))
async def fill_profile(message: Message,  state: FSMContext):
    user_id = message.from_user.id

    # Разделите текст сообщения на части
    parts = message.text.split()
    # Если есть аргументы команды, они будут во второй части
    referral_id = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else None

    account = await mongodb.get_user(user_id)
    if account is not None and account['_id'] == user_id:
        await main_menu.main_menu(message)
    else:
        await state.set_state(Form.name)
        await message.answer_animation(
            animation="CgACAgIAAx0CfstymgACHXpm3-JUbweB3b06B_W3bAgiVWRycQACI1wAAvfAAAFLc8MF1Rvq7R02BA",
            caption='❖ 💮 Добро пожаловать!'
                    f'\n── •✧✧• ──────────'
                    f'\n🎴Здесь вы будете собрать своих персонажей и 🗡 сражаться'
                    f'\n<blockquote expandable>🔥 Соревнуйтесь, у кого круче карты'
                    f'\n🃏 Собирайте колоду'
                    f'\n⚔️ Сражайтесь на арене'
                    f'\n🏆 Выиграйте платные призы'
                    f'\n🃏 Обмениваетесь картами'
                    f'\n🎫 Покупайте билетов'
                    f'\n💠 Соберите ресурсы в подземелье'
                    f'\n🐦‍🔥Убейте боссов'
                    f'\n🔮 Попытайте удачу в «Гаче»</blockquote>'
                    f'\n── •✧✧• ──────────'
                    '\n❖ 📜 Пройдите регистрацию')
        await message.answer("❖ 🪪  Введите никнейм: ", reply_markup=profile(message.from_user.first_name))
        if referral_id and referral_id != user_id:
            await state.update_data(referral=referral_id)
        # Если пользователь уже существует и у него есть referral_id, проверьте, существует ли реферал


@router.message(Form.name)
async def form_name(message: Message, state: FSMContext):
    if not EMOJI_PATTERN.search(message.text):
        if len(message.text) <= 10:

            await state.update_data(name=f"<a href='https://t.me/{message.from_user.username}'><b>{message.text}</b></a>") # f"{message.from_user.username}"
            await state.set_state(Form.universe)
            media_id = "AgACAgIAAx0CfstymgACCxNl4ie8goZjHQ1rAV5rxcz2a9XLnQACBs8xG7-XGUsGHmby9061bgEAAwIAA3kAAzQE"
            await message.answer(f"\n\n ❖ ⚙️ Чтобы бот работал корректно и динамично, включите автозагрузку фото "
                                 f"и видео в настройках телеграм и автовоспроизведение видео в настройках чата телеграм",
                                 reply_markup=rm())
            pattern = dict(
                caption="❖ 🗺 Выбирайте вселенную"
                        "\n── •✧✧• ──────────"
                        "\n❖ 🗺 Вселенные постепенно будут добавляться и дополняться"
                        f"\n<blockquote><b>💡 Примечание</b>"
                        f"\n • 🏟️ <b>Арена</b> - существует в других вселенных, кроме ⭐️ Allstars, "
                        f"где вы можете применять навыки 🎴 персонажей из аниме"
                        f"\n • 🃏 <b>Битва</b> - сильно отличается от 🏟️ арены и только для вселенной ⭐️ Allstars, "
                        f"здесь вы можете сражаться в режиме карточный битвы с 🃏 колодой карт.</blockquote>"
                        "\n❖ 🔄 Всегда можно сменить вселенную в ⚙️ ️настройки",
                reply_markup=inline_builder(['⭐️ Allstars', '🗡 Bleach', '🍥 Naruto', '🔥 Jujutsu Kaisen'],
                                            ['Allstars', 'Bleach', 'Naruto', 'Jujutsu Kaisen'], row_width=1),
            )
            await message.answer_photo(media_id, **pattern)
        else:
            await message.answer("✖️ Ник слишком длинный. Введите вручную с помощью клавиатуры: ")
    else:
        await message.answer("✖️ Ник не должен содержать эмодзи. Введите вручную с помощью клавиатуры: ")


@router.callback_query(F.data.in_(['Allstars']))
async def get_first_free(callback: CallbackQuery, state: FSMContext):
    account = await mongodb.get_user(callback.from_user.id)
    if account is not None and account['_id'] == callback.from_user.id:
        character = account.get('character', {}).get('Allstars')
        if character:
            await mongodb.update_user(callback.from_user.id, {'universe': 'Allstars'})
            await callback.answer("❖ 🗺 Вы успешно сменили вселенную", show_alert=True)
            await callback.message.answer("❖ 🗺 Вы успешно сменили вселенную", reply_markup=menu_card_button())
            await settings.settings(callback)
            return
    await state.update_data(universe=callback.data)
    media = InputMediaAnimation(media="CgACAgIAAx0CfstymgACEnpmnUiYllQQPMNY7B3y44Okelr6UgACsVEAApQD6UhAS-MzjVWVxTUE")
    await callback.message.edit_media(media=media)
    await callback.message.edit_caption(caption="❖ ⭐️ Allstars"
                                        "\n── •✧✧• ──────────"
                                        "\n<blockquote expandable>🗺 В этой вселенной находиться популярные 🎴 персонажи "
                                                "из разных аниме. Вы моежете собрать "
                                                "🃏 колоду и сражаться в 🃏 <b>Битве</b></blockquote>", reply_markup=get_common())


@router.callback_query(F.data.in_(['Bleach']))
async def get_first_free(callback: CallbackQuery, state: FSMContext):
    account = await mongodb.get_user(callback.from_user.id)
    if account is not None and account['_id'] == callback.from_user.id:
        character = account.get('character', {}).get('Bleach')
        if character:
            await mongodb.update_user(callback.from_user.id, {'universe': 'Bleach'})
            await callback.answer("❖ 🗺 Вы успешно сменили вселенную", show_alert=True)
            await callback.message.answer("❖ 🗺 Вы успешно сменили вселенную", reply_markup=menu_button())
            await settings.settings(callback)
            return
    await state.update_data(universe=callback.data)
    media = InputMediaAnimation(media="CgACAgIAAx0CfstymgACCxZl5FxQpuMBOz7tFM8BU88VOEvMXgACtjwAAkLSIEtSvf16OnsuwTQE")
    await callback.message.edit_media(media=media)
    await callback.message.edit_caption(caption="❖ 🗡 Bleach"
                                        "\n── •✧✧• ──────────"
                                        "\n<blockquote expandable>🗺 В этой вселенной находиться популярные 🎴 персонажи "
                                                "из аниме 🗡 Блич. Вы моежете собрать "
                                                "🎴 персонажей и сражаться в 🏟️ <b>Арене</b></blockquote>",
                                        reply_markup=get_common())


@router.callback_query(F.data.in_(['Naruto']))
async def get_first_free(callback: CallbackQuery, state: FSMContext):
    account = await mongodb.get_user(callback.from_user.id)
    if account is not None and account['_id'] == callback.from_user.id:
        character = account.get('character', {}).get('Naruto')
        if character:
            await mongodb.update_user(callback.from_user.id, {'universe': 'Naruto'})
            await callback.answer("❖ 🗺 Вы успешно сменили вселенную", show_alert=True)
            await callback.message.answer("❖ 🗺 Вы успешно сменили вселенную", reply_markup=menu_button())
            await settings.settings(callback)
            return
    await state.update_data(universe=callback.data)
    media = InputMediaAnimation(media="CgACAgIAAxkBAAKu-2bfz0QjhL_TZCnL-Zha1vsprdVLAAKCUQACzJcBS3N7PqOXSE2qNgQ")
    await callback.message.edit_media(media=media)
    await callback.message.edit_caption(caption="❖ 🍥 Naruto"
                                        "\n── •✧✧• ──────────"
                                        "\n<blockquote expandable>🗺 В этой вселенной находиться популярные 🎴 персонажи "
                                                "из аниме 🍥 Наруто. Вы моежете собрать "
                                                "🎴 персонажей и сражаться в 🏟️ <b>Арене</b></blockquote>",
                                        reply_markup=get_common())


@router.callback_query(F.data.in_(['Jujutsu Kaisen']))
async def get_first_free(callback: CallbackQuery, state: FSMContext):
    account = await mongodb.get_user(callback.from_user.id)
    if account is not None and account['_id'] == callback.from_user.id:
        character = account.get('character', {}).get('Jujutsu Kaisen')
        if character:
            await mongodb.update_user(callback.from_user.id, {'universe': 'Jujutsu Kaisen'})
            await callback.answer("❖ 🗺 Вы успешно сменили вселенную", show_alert=True)
            await callback.message.answer("❖ 🗺 Вы успешно сменили вселенную", reply_markup=menu_button())
            await settings.settings(callback)
            return
    await state.update_data(universe=callback.data)
    media = InputMediaAnimation(media="CgACAgIAAx0CfstymgACQChoOuptItjKNzPwfRbEeo3pNgM08QACqnMAAmIAAdlJUKBfx75OSdU2BA")
    await callback.message.edit_media(media=media)
    await callback.message.edit_caption(caption="❖ 🔥 Jujutsu Kaisen"
                                        "\n── •✧✧• ──────────"
                                        "\n<blockquote expandable>🗺 В этой вселенной находиться популярные 🎴 персонажи "
                                                "из аниме 🔥 Магической битвы. Вы моежете собрать "
                                                "🎴 персонажей и сражаться в 🏟️ <b>Арене</b></blockquote>",
                                        reply_markup=get_common())


# @router.callback_query(F.data.in_(['Allstars(old)']))
# async def get_first_free(callback: CallbackQuery, state: FSMContext):
#     account = await mongodb.get_user(callback.from_user.id)
#     if account is not None and account['_id'] == callback.from_user.id:
#         character = account.get('character', {}).get('Allstars(old)')
#         if character:
#             await mongodb.update_user(callback.from_user.id, {'universe': 'Allstars(old)'})
#             await callback.answer("❖ 🗺 Вы успешно сменили вселенную", show_alert=True)
#             return
#     await state.update_data(universe=callback.data)
#     media = InputMediaAnimation(media="CgACAgIAAx0CfstymgACEnpmnUiYllQQPMNY7B3y44Okelr6UgACsVEAApQD6UhAS-MzjVWVxTUE")
#     await callback.message.edit_media(media=media)
#     await callback.message.edit_caption(caption="❖ 🗺 Allstars(old)"
#                                         "\n── •✧✧• ──────────"
#                                         "\n<blockquote expandable>💮 Эта самая первая версия. В Этой Вселенной "
#                                                 "находиться популярные персонажи из разных аниме но пока арена "
#                                                 "недоступна. Вы моежете просто собрать "
#                                                 "персонажей</blockquote>", reply_markup=get_common())


@router.callback_query(F.data == "get_first_free")
async def get_first_free(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = callback.from_user.id
    universe = data.get('universe')
    character, character_category, power = await first_summon(callback, universe)
    account = await mongodb.get_user(callback.from_user.id)
    if account is not None and account['_id'] == callback.from_user.id:
        await mongodb.update_user(callback.from_user.id, {'universe': universe, f'character.{universe}': character})
    else:
        await mongodb.input_user(user_id, data.get('name'), universe, character, power)

        referral_id = data.get('referral')
        # Если пользователь уже существует и у него есть referral_id, проверьте, существует ли реферал
        referral = await mongodb.get_user(referral_id)
        if referral:
            # Если реферал существует и новый пользователь еще не в списке приглашенных
            if user_id not in referral['account']['referrals']:
                # Добавьте нового пользователя в список приглашенных
                await mongodb.push_referral(referral_id, user_id)
                # Получите обновленные данные реферала
                updated_referral = await mongodb.get_user(referral_id)
                # Проверьте, достигло ли количество приглашенных 3
                if len(updated_referral['account']['referrals']) % 3 == 0:
                    # Если достигло, увеличьте количество ключей на 1
                    await mongodb.update_value(referral_id, {'inventory.items.tickets.keys': 1})
    await mongodb.push(universe, character_category, character, user_id)
    await state.clear()
