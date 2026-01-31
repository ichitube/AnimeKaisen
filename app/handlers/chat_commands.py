import re

from app.keyboards.builders import start_button

from aiogram import Router, F, Bot
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
from app.data import character_photo
from app.data import mongodb
from app.keyboards.builders import inline_builder, menu_button, rm, menu_card_button
from app.recycling import profile
from app.filters.chat_type import ChatTypeFilter

router = Router()


async def get_inventory(data):
    rarity, user_id = data.split('/')

    rarity_dict = {
        'gd': 'divine',
        'gm': 'mythical',
        'gl': 'legendary',
        'ge': 'epic',
        'gr': 'rare',
        'gc': 'common'
    }
    rarity = rarity_dict[rarity]

    account = await mongodb.get_user(int(user_id))
    invent = account['inventory']['characters']
    return invent[rarity]


@router.message(F.text.lower().in_(['моя карта', 'профиль']))
async def main_chat(message: Message):
    user_id = message.from_user.id
    account = await mongodb.get_user(user_id)

    if account is not None and account['_id'] == user_id:

        universe = account['universe']
        character = account['character'][account['universe']]
        avatar = character_photo.get_stats(universe, character, 'avatar')
        avatar_type = character_photo.get_stats(universe, character, 'type')

        await profile.update_rank(user_id, account.get("battle", {}).get("stats", {}).get("wins", 0))


        await profile.update_level(user_id, account["campaign"]["count"])

        rank = await profile.rerank(account['stats']['rank'])
        level = await profile.level(account['campaign']['level'])

        characters = account['inventory']['characters']

        total_characters = 0
        for outer_key in characters:
            for inner_key in characters[outer_key]:
                total_characters += len(characters[outer_key][inner_key])

        pattern = dict(
            caption=# f"\n── •✧✧• ──────────"
                    f"\n 🪪  〢 Профиль {account['name']} "
                    f"\n── •✧✧• ──────────"
                    f"\n<blockquote>🎴 <b>{character}</b>"
                    f"\n🗺 Вселенная: {universe}"
                    f"\n🎐 <b>{rank}</b>"
                    f"\n⛩️ <b>{level}</b></blockquote>"
                    f"\n── •✧✧• ──────────"
                    f"\n<i><b>❃💴 {account['account']['money']} ¥ ❃ {account['campaign']['power']} ⚜️ Мощи"
                    f"\n❃🀄️ {account['stats']['exp']} XP ❃ {total_characters} 🃏 Карт</b></i>",
            parse_mode=ParseMode.HTML,
            # reply_markup=goto_bot()
        )
        if avatar_type == 'photo':
            await message.answer_photo(avatar, **pattern)
        else:
            await message.answer_animation(avatar, **pattern)
    else:
        media = "CgACAgIAAx0CfstymgACBbRlzDgYWpgLO50Lgeg0HImQEC9GEAAC7D4AAsywYUo5sbjTkVkCRjQE"
        await message.answer_animation(animation=media, caption="✧ • 📄 Ты не регистрирован"
                                                                f"\n── •✧✧• ──────────"
                                                                f"\n❖ 💮 Присоединяйся к нам и "
                                                                f"получи свою первую 🎴 карту"
                                                                f"\n── •✧✧• ──────────",
                                       reply_markup=start_button())


@router.message(F.text.lower().in_(['битвы', 'рейтинг']))
async def campaign_rank(message: Message):
    chat_id = message.chat.id
    rating = await mongodb.chat_rating(chat_id, '👑')

    await message.answer(f"❖  🏆  <b>Сильнейшие игроки чата</b>"
                         f"\n── •✧✧• ──────────"
                         f"{rating}", disable_web_page_preview=True)


@router.message(F.text.startswith('дать') | F.text.startswith('Дать')
                | F.text.startswith('перевести') | F.text.startswith('Перевести'))
async def give_money(message: Message):
    user_id = message.from_user.id
    friend_id = message.reply_to_message.from_user.id
    account = await mongodb.get_user(user_id)
    friend = await mongodb.get_user(friend_id)

    # Извлекаем цифры из сообщения
    text = message.text.lower()
    numbers = re.findall(r'\d+', text)
    if numbers:
        amount = int(numbers[0])  # Первое найденное число
        if user_id != friend_id:
            if account is not None and account['_id'] == user_id:
                if friend is not None and friend['_id'] == friend_id:
                    if account['account']['money'] >= amount:
                        if account['account']['prime']:
                            if amount <= 1000:
                                await mongodb.update_user(user_id, {'account.money': account['account']['money'] - amount})
                                await mongodb.update_user(friend_id, {'account.money': friend['account']['money'] + amount})
                                await message.reply(
                                    f"❖ ✨ {account['name']} отправил {amount} 💴 ¥ пользователю {friend['name']}",
                                    disable_web_page_preview=True)
                            else:
                                await message.reply("❖ ✖️ Максимальная сумма перевода 1000 💴 ¥")
                        else:
                            await message.reply("❖ ✖️ Для перевода денег необходимо иметь 💮Pass")
                    else:
                        await message.reply(f"❖ ✖️ Недостаточно средст. \nБаланс: {account['account']['money']} 💴 ¥")
                else:
                    await message.reply("❖ ✖️ Пользователь не зарегистрирован")
            else:
                await message.reply("❖ ✖️ Ты не зарегистриров")
        else:
            await message.reply("❖ ✖️ Нельзя перевести деньги самому себе")
    else:
        await message.reply("❖ ✖️ Не указана сумму. Пожалуйста, укажите цифры после команды 'дать'")


def is_character_in_inventory(character, inventory):
    """
    Рекурсивно проверяет, содержится ли персонаж в любом из списков внутри inventory, игнорируя регистр.
    """
    character_lower = character
    for key, value in inventory.items():
        if isinstance(value, dict):
            if is_character_in_inventory(character, value):
                return True
        elif isinstance(value, list):
            for item in value:
                if item == character_lower:
                    return True
    return False


@router.message(F.text.startswith('отдать') | F.text.startswith('Отдать'))
async def give_character(message: Message):
    user_id = message.from_user.id
    if not message.reply_to_message:
        await message.reply("❖ ✖️ Нужно ответить на сообщение пользователя, которому хотите отдать персонажа.")
        return

    friend_id = message.reply_to_message.from_user.id
    account = await mongodb.get_user(user_id)
    friend = await mongodb.get_user(friend_id)
    universe = account.get('universe')

    if not account:
        await message.reply("❖ ✖️ Вы не зарегистрированы.")
        return

    if not friend:
        await message.reply("❖ ✖️ Пользователь, которому вы хотите отдать персонажа, не зарегистрирован.")
        return

    text = message.text
    match = re.search(r'отдать\s(.+)', text)
    if not match:
        await message.reply("❖ ✖️ Неверный формат команды. Пожалуйста, используйте 'отдать [персонаж]'.")
        return

    character = match.group(1).strip()

    # Проверяем наличие персонажа в инвентаре пользователя
    user_characters = account.get('inventory', {}).get('characters', {})

    if not is_character_in_inventory(character, user_characters):
        await message.reply("❖ ✖️ У вас нет такого персонажа, либо вы находитесь в другой вселенной.")
        return

    # Проверяем наличие персонажа у друга
    friend_characters = friend.get('inventory', {}).get('characters', {})
    if is_character_in_inventory(character, friend_characters):
        await message.reply("❖ ✖️ У пользователя уже есть такой персонаж.")
        return

    # Проверяем, является ли персонаж основным
    if character == account.get('character', {}).get(account.get('universe')):
        await message.reply("❖ ✖️ Нельзя отдать своего основного персонажа.")
        return

    avatar = character_photo.get_stats(universe, character, 'avatar')
    avatar_type = character_photo.get_stats(universe, character, 'type')
    ch_universe = character_photo.get_stats(universe, character, 'universe')
    rarity = character_photo.get_stats(universe, character, 'rarity')

    if rarity == 'Обычная':
        rarity = 'common'
    elif rarity == 'Редкая':
        rarity = 'rare'
    elif rarity == 'Эпическая':
        rarity = 'epic'
    elif rarity == 'Легендарная':
        rarity = 'legendary'
    elif rarity == 'Мифическая':
        rarity = 'mythical'
    elif rarity == 'Божественная':
        rarity = 'divine'

    # Отправляем сообщение с информацией о передаче персонажа
    if account['account']['prime']:
        # Обновляем инвентари
        await mongodb.push(universe, rarity, character, friend_id)
        await mongodb.pull(universe, rarity, character, user_id)
        if avatar_type == 'photo':
            await message.reply_photo(
                avatar,
                caption=f"❖ ✨ {account['name']} отправил персонажа {character} пользователю {friend['name']} на 🗺 вселенную {ch_universe}",
                disable_web_page_preview=True
            )
        else:
            await message.reply_animation(
                avatar,
                caption=f"❖ ✨ {account['name']} отправил персонажа {character} пользователю {friend['name']} на 🗺 вселенную {ch_universe}",
                disable_web_page_preview=True
            )
    else:
        await message.reply("❖ ✖️ Для передачи персонажа необходимо иметь 💮 Pass")


@router.message(F.text.lower().in_(['баланс', 'б']))
async def balance(message: Message):
    user_id = message.from_user.id
    account = await mongodb.get_user(user_id)

    if account is not None and account['_id'] == user_id:
        await message.answer(f"❖ 💴 Ваш баланс: {account['account']['money']} ¥")
    else:
        await message.answer("❖ ✖️ Ты не зарегистрирован", reply_markup=start_button())


@router.message(Command("rm"))
async def fill_profile(message: Message, bot: Bot):
    await bot.send_message(message.chat.id, '❖ ✖️ Кнопки удалены', reply_markup=rm())


@router.message(Command("help"))
async def fill_profile(message: Message, bot: Bot):
    await bot.send_message(message.chat.id, '❖ 📋 <a href="https://teletype.in/@dire_hazard/x1">Руководство</a>',
                           reply_markup=inline_builder(
                               ["☑️"],
                               ["delete"], row_width=[1])
                           )


@router.message(ChatTypeFilter(chat_type=["private"]), Command("menu_button"))
async def call_button(message: Message):
    account = await mongodb.get_user(message.from_user.id)
    if account['universe'] == 'Allstars':
        await message.answer(text='˗ˋˏ🛠 Кнопки восстановленыˎˊ˗', reply_markup=menu_card_button())
    else:
        await message.answer(text='˗ˋˏ🛠 Кнопки восстановленыˎˊ˗', reply_markup=menu_button())

@router.message(F.text.startswith('гиф') | F.text.startswith('Гиф'))
async def give_character(message: Message):
    user_id = message.from_user.id

    text = message.text
    match = re.search(r'гиф\s(.+)', text)
    if not match:
        await message.reply("❖ ✖️ Неверный формат команды.")
        return

    gif = match.group(1).strip()

    await message.reply_animation(gif)

@router.message(F.text.startswith('ф') | F.text.startswith('ф'))
async def give_character(message: Message):
    user_id = message.from_user.id

    text = message.text
    match = re.search(r'ф\s(.+)', text)
    if not match:
        await message.reply("❖ ✖️ Неверный формат команды.")
        return

    photo = match.group(1).strip()

    await message.reply_photo(photo)

"""
@router.message((F.text == 'инвентарь') | (F.text == 'Инвентарь') | (F.text == 'карты')
                | (F.text == 'Карты') | (F.text == '🥡 Инвентарь'))
@router.callback_query(F.data.regexp("(g_inventory)\/([0-9]*)$").as_("data"))
async def inventory(message: Message | CallbackQuery, state: FSMContext):
    user_id = message.from_user.id
    account = await mongodb.get_user(user_id)

    if account is not None and account['_id'] == user_id:

        await state.update_data(id=user_id)
        media_id = "CgACAgIAAxkBAAIVCmXMvbzs7hde-fvY9_4JCwU8W6HpAAKgOwACeyZoSuedvZenkxDNNAQ"
        total_divine = len(account['inventory']['characters']['divine'])
        total_mythical = len(account['inventory']['characters']['mythical'])
        total_legendary = len(account['inventory']['characters']['legendary'])
        total_epic = len(account['inventory']['characters']['epic'])
        total_rare = len(account['inventory']['characters']['rare'])
        total_common = len(account['inventory']['characters']['common'])
        total_elements = sum(len(account['inventory']['characters'][sublist])
                             for sublist in account['inventory']['characters'])

        pattern = dict(caption=f"🥡 Инвентарь"
                               f"\n── •✧✧• ──────────"
                               f"\n❖ Здесь вы можете увидеть все ваши 🎴 карты"
                               f"\n\n❖ Выберите ✨ редкость карты, "
                               f"чтобы посмотреть их"
                               f"\n── •✧✧• ──────────"
                               f"\n❖ 🎴 Количество карт: {total_elements}",
                       reply_markup=inline_builder([f"🌠 Божественные 🌟 {total_divine}",
                                                    f"🌌 Мифические ⭐️ {total_mythical}",
                                                    f"🌅 Легендарные ⭐️ {total_legendary}",
                                                    f"🎆 Эпические ⭐️ {total_epic}",
                                                    f"🎇 Редкие ⭐️ {total_rare}",
                                                    f"🌁 Обычные ⭐️ {total_common}"],
                                                   [f"gd/{user_id}", f"gm/{user_id}", f"gl/{user_id}",
                                                    f"ge/{user_id}", f"gr/{user_id}", f"gc/{user_id}"], row_width=[1]))
        if isinstance(message, CallbackQuery):
            callback_id = message.inline_message_id
            await message.message.edit_caption(inline_message_id=callback_id, **pattern)
        else:
            await message.answer_animation(animation=media_id, **pattern)
    else:
        media = "CgACAgIAAx0CfstymgACBbRlzDgYWpgLO50Lgeg0HImQEC9GEAAC7D4AAsywYUo5sbjTkVkCRjQE"
        await message.answer_animation(animation=media, caption="✧ • 📄 Ты не регистрирован"
                                                                f"\n── •✧✧• ──────────"
                                                                f"\n❖ 💮 Присоединяйся к нам и "
                                                                f"получи свою первую 🎴 карту"
                                                                f"\n── •✧✧• ──────────",
                                       reply_markup=start_button())


@router.callback_query(F.data.regexp("(gd|gm|gl|ge|gr|gc)\/([0-9]*)$").as_("data"))
async def inventory(callback: CallbackQuery, state: FSMContext, data: Match[str]):
    g, user_id = data.groups()
    if callback.from_user.id != int(user_id):
        await callback.answer("❖ ✖️ Это не ваш инвентарь", show_alert=True)
        return

    await state.update_data(rarity=callback.data)
    inline_id = callback.inline_message_id
    user_id = callback.from_user.id
    invent = await get_inventory(callback.data)
    if invent == []:
        await callback.answer("❖ ✖️ У вас нет карт данной редкости", show_alert=True)
        return
    await state.update_data(character=invent[0])
    file, file_type = character_photo.get_file_id(invent[0])
    if file_type == 'photo':
        photo = InputMediaPhoto(media=file)
    else:
        photo = InputMediaAnimation(media=file)
    stats = character_photo.get_stats(invent[0])
    await callback.message.edit_media(photo, inline_id)
    await callback.message.edit_caption(inline_id, f"🎴 {invent[0]}"
                                                   f"\n ── •✧✧• ──────────"
                                                   f"\n❖ ✨ Редкость: {stats[5]}"
                                                   f"\n\n ⚜️ Сила: {stats[0]}"
                                                   f"\n ❤️ Здоровье: {stats[1]}"
                                                   f"\n 🗡 Атака: {stats[2]}"
                                                   f"\n 🧪 Мана: {stats[3]}"
                                                   f"\n 🛡 Защита {stats[4]}"
                                                   f"\n──❀*̥˚──◌──◌──❀*̥˚────"
                                                   f"\n❖ 🔖 1 из {len(invent)}",
                                        reply_markup=pagination_group(user_id))


@router.callback_query(Pagination.filter(F.action.regexp("(g_prev|g_next)\/([0-9]*)$").as_("data")))
async def inventory(callback: CallbackQuery, callback_data: Pagination, state: FSMContext, data: Match[str]):
    await callback.answer("Успешно")
    inline_id = callback.inline_message_id
    page_num = int(callback_data.page)
    user_data = await state.get_data()

    g, user_id = data.groups()
    if callback.from_user.id != int(user_id):
        await callback.answer("❖ ✖️ Это не ваш инвентарь", show_alert=True)
        return

    invent = await get_inventory(user_data['rarity'])

    action, user_id = callback_data.action.split('/')

    if action == "g_next":
        page_num = (page_num + 1) % len(invent)
    elif action == "g_prev":
        page_num = (page_num - 1) % len(invent)

    with suppress(TelegramBadRequest):
        await state.update_data(character=invent[page_num])
        stats = character_photo.get_stats(invent[page_num])
        file, file_type = character_photo.get_file_id(invent[page_num])
        if file_type == 'photo':
            photo = InputMediaPhoto(media=file)
        else:
            photo = InputMediaAnimation(media=file)
        await callback.message.edit_media(photo, inline_id)
        await callback.message.edit_caption(
            inline_id,
            f"🎴 {invent[page_num]}"
            f"\n ── •✧✧• ──────────"
            f"\n❖ 🌠 Редкость: {stats[5]}"
            f"\n\n ⚜️ Сила: {stats[0]}"
            f"\n ❤️ Здоровье: {stats[1]}"
            f"\n 🗡 Атака: {stats[2]}"
            f"\n 🧪 Мана: {stats[3]}"
            f"\n 🛡 Защита {stats[4]}"
            f"\n──❀*̥˚──◌──◌──❀*̥˚────"
            f"\n❖ 🔖 {page_num + 1} из {len(invent)}",
            reply_markup=pagination_group(page_num)
        )
    await callback.answer()


@router.callback_query(F.data.regexp("(g_change_character)\/([0-9]*)$").as_("data"))
async def change_ch(callback: CallbackQuery, state: FSMContext, data: Match[str]):

    g, user_id = data.groups()
    if callback.from_user.id != int(user_id):
        await callback.answer("❖ ✖️ Это не ваш инвентарь", show_alert=True)
        return
    else:
        data = await state.get_data()
        await mongodb.update_user(user_id, {'character': data.get('character')})
        await callback.answer("🎴 ВЫ успешно изменили персонажа", show_alert=True)
"""
