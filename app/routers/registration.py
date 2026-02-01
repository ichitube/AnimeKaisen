import re

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InputMediaAnimation, InputMediaPhoto
from app.data import mongodb
from app.filters.chat_type import ChatTypeFilter
from app.keyboards.builders import inline_builder, profile, rm, get_common, menu_card_button, menu_button
from app.routers import main_menu
from app.routers.gacha import first_summon
from app.utils.states import Form
from app.routers import settings

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
            caption='❖ <tg-emoji emoji-id="5454380420336466255">❌</tg-emoji> Добро пожаловать!'
                    f'\n── •✧✧• ──────────'
                    f'\n<tg-emoji emoji-id="5399959611283356481">❌</tg-emoji>Здесь вы будете собирать своих персонажей и <tg-emoji emoji-id="5399959611283356481">❌</tg-emoji> сражаться'
                    f'\n<blockquote expandable><tg-emoji emoji-id="5453921696354419743">❌</tg-emoji> Соревнуйтесь, у кого круче карты'
                    f'\n<tg-emoji emoji-id="5399908355143645853">❌</tg-emoji> Соберите колоду'
                    f'\n<tg-emoji emoji-id="5104960787579929462">❌</tg-emoji> Поговорите с вашим персонажем'
                    f'\n<tg-emoji emoji-id="5454014806950429357">❌</tg-emoji> Сражайтесь на арене'
                    f'\n<tg-emoji emoji-id="5010650336621233058">❌</tg-emoji> Выиграйте платные призы'
                    f'\n<tg-emoji emoji-id="5213223087612371830">❌</tg-emoji> Обмениваетесь картами'
                    f'\n<tg-emoji emoji-id="5278306114323099155">❌</tg-emoji> Покупайте билетов'
                    f'\n<tg-emoji emoji-id="5199633166842736536">❌</tg-emoji> Убейте боссов'
                    f'\n<tg-emoji emoji-id="6037426946642546018">❌</tg-emoji> Выполняйте квесты'
                    f'\n<tg-emoji emoji-id="5199498841740553143">❌</tg-emoji> Соберите ресурсы в подземелье'
                    f'\n<tg-emoji emoji-id="6039404804852158797">❌</tg-emoji> Попытайте удачу в «Гаче»</blockquote>'
                    f'\n── •✧✧• ──────────'
                    '\n❖ <tg-emoji emoji-id="5195198887987520417">❌</tg-emoji> Пройдите регистрацию')
        await message.answer('❖ <tg-emoji emoji-id="5936017305585586269">❌</tg-emoji>  Введите никнейм: ', reply_markup=profile(message.from_user.first_name))
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
            await message.answer(f'\n\n ❖ <tg-emoji emoji-id="5350396951407895212">❌</tg-emoji> Чтобы бот работал корректно и динамично, включите автозагрузку фото '
                                 f'и видео в настройках телеграм и автовоспроизведение видео в настройках чата телеграм',
                                 reply_markup=rm())
            pattern = dict(
                caption='❖ <tg-emoji emoji-id="5370845694431076232">❌</tg-emoji> Выбирайте вселенную'
                        '\n── •✧✧• ──────────'
                        f'\n<blockquote><tg-emoji emoji-id="5947043478771862917">❌</tg-emoji><b> Примечание</b>'
                        '\n❖ <tg-emoji emoji-id="5370845694431076232">❌</tg-emoji> Вселенные постепенно будут добавляться и дополняться'
                        # f'\n • 🏟️ <b>Арена</b> - существует в других вселенных, кроме ⭐️ Allstars, '
                        # f'где вы можете применять навыки 🎴 персонажей из аниме'
                        # f'\n • 🃏 <b>Битва</b> - сильно отличается от 🏟️ арены и только для вселенной ⭐️ Allstars, '
                        # f'здесь вы можете сражаться в режиме карточный битвы с 🃏 колодой карт.</blockquote>'
                       '\n❖ <tg-emoji emoji-id="6005843436479975944">❌</tg-emoji> Всегда можно сменить вселенную в <tg-emoji emoji-id="5350396951407895212">❌</tg-emoji> ️настройки</blockquote>',
                reply_markup=inline_builder(['🗡 Bleach', '🍥 Naruto', '🔥 Jujutsu Kaisen'], # '⭐️ Allstars',
                                            ['Bleach', 'Naruto', 'Jujutsu Kaisen'], row_width=1), # 'Allstars',
            )
            await message.answer_photo(media_id, **pattern)
        else:
            await message.answer("✖️ Ник слишком длинный. Введите вручную с помощью клавиатуры: ")
    else:
        await message.answer("✖️ Ник не должен содержать эмодзи. Введите вручную с помощью клавиатуры: ")


@router.callback_query(F.data == "reg")
async def back_to_universe(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    data = await state.get_data()

    # если ника нет — возвращаем на ввод ника
    if "name" not in data:
        await state.set_state(Form.name)
        await callback.message.edit_caption(
            caption='❖ Введите никнейм:',
            reply_markup=None
        )
        return

    # ✅ возвращаем на выбор вселенной
    await state.set_state(Form.universe)

    media_id = "AgACAgIAAx0CfstymgACCxNl4ie8goZjHQ1rAV5rxcz2a9XLnQACBs8xG7-XGUsGHmby9061bgEAAwIAA3kAAzQE"

    caption = (
        '❖ <tg-emoji emoji-id="5370845694431076232">❌</tg-emoji> Выбирайте вселенную'
        '\n── •✧✧• ──────────'
        f'\n<blockquote><tg-emoji emoji-id="5947043478771862917">❌</tg-emoji><b> Примечание</b>'
        '\n❖ <tg-emoji emoji-id="5370845694431076232">❌</tg-emoji> Вселенные постепенно будут добавляться и дополняться'
        '\n❖ <tg-emoji emoji-id="6005843436479975944">❌</tg-emoji> Всегда можно сменить вселенную в <tg-emoji emoji-id="5350396951407895212">❌</tg-emoji> ️настройки</blockquote>'
    )

    # 1) меняем картинку/гиф
    await callback.message.edit_media(
        media=InputMediaPhoto(media=media_id, caption=caption, parse_mode="HTML")
    )

    # 2) меняем клавиатуру
    await callback.message.edit_reply_markup(
        reply_markup=inline_builder(
            ['🗡 Bleach', '🍥 Naruto', '🔥 Jujutsu Kaisen'],
            ['Bleach', 'Naruto', 'Jujutsu Kaisen'],
            row_width=1
        )
    )


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
            await callback.message.answer('❖ <tg-emoji emoji-id="5370845694431076232">❌</tg-emoji> Вы успешно сменили вселенную', reply_markup=menu_button())
            await settings.settings(callback)
            return
    await state.update_data(universe=callback.data)
    media = InputMediaAnimation(media="CgACAgIAAx0CfstymgACCxZl5FxQpuMBOz7tFM8BU88VOEvMXgACtjwAAkLSIEtSvf16OnsuwTQE")
    await callback.message.edit_media(media=media)
    await callback.message.edit_caption(caption='❖ <tg-emoji emoji-id="5416080380186863674">❌</tg-emoji> Bleach'
                                        '\n── •✧✧• ──────────'
                                        '\n<blockquote expandable><tg-emoji emoji-id="5370845694431076232">❌</tg-emoji> В этой вселенной находиться популярные <tg-emoji emoji-id="5415810600406099166">❌</tg-emoji> персонажи '
                                                'из аниме <tg-emoji emoji-id="5269514187419167010">❌</tg-emoji> Блич. Вы моежете собрать '
                                                '<tg-emoji emoji-id="5269636228914883132">❌</tg-emoji> персонажей и сражаться в <tg-emoji emoji-id="5269433450623935911">❌</tg-emoji> <b>Арене</b></blockquote>',
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
    await callback.message.edit_caption(caption='❖ <tg-emoji emoji-id="5425055431611393158">❌</tg-emoji> Naruto'
                                        '\n── •✧✧• ──────────'
                                        '\n<blockquote expandable><tg-emoji emoji-id="5370845694431076232">❌</tg-emoji> В этой вселенной находиться популярные <tg-emoji emoji-id="5426895906702107044">❌</tg-emoji> персонажи '
                                                'из аниме <tg-emoji emoji-id="5427394299002101953">❌</tg-emoji> Наруто. Вы моежете собрать '
                                                '<tg-emoji emoji-id="5425013375291629746">❌</tg-emoji> персонажей и сражаться в <tg-emoji emoji-id="5305464601284977538">❌</tg-emoji> <b>Арене</b></blockquote>',
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
    await callback.message.edit_caption(caption='❖ <tg-emoji emoji-id="5445259279894333861">❌</tg-emoji> Jujutsu Kaisen'
                                        '\n── •✧✧• ──────────'
                                        '\n<blockquote expandable><tg-emoji emoji-id="5370845694431076232">❌</tg-emoji> В этой вселенной находиться популярные <tg-emoji emoji-id="5406940114255366351">❌</tg-emoji> персонажи '
                                                'из аниме <tg-emoji emoji-id="5406989935876002012">❌</tg-emoji> Магической битвы. Вы моежете собрать '
                                                '<tg-emoji emoji-id="5406911118931151893">❌</tg-emoji> персонажей и сражаться в <tg-emoji emoji-id="5404408505912282371">❌</tg-emoji> <b>Арене</b></blockquote>',
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
