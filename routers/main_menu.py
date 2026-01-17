from datetime import datetime, timedelta

from aiogram import Router, F, Bot
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InputMediaAnimation, InputMediaPhoto
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from data import mongodb, character_photo
from filters.chat_type import ChatTypeFilter
from keyboards.builders import inline_builder
from recycling import profile
from utils.states import Promo
from aiogram.exceptions import TelegramBadRequest

router = Router()


@router.message(ChatTypeFilter(chat_type=["private"]), Command("menu"))
@router.message(ChatTypeFilter(chat_type=["private"]), F.text == "🪪 〢 Профиль")
@router.callback_query(F.data == "main_page")
async def main_menu(message: Message | CallbackQuery):
    user_id = message.from_user.id
    account = await mongodb.get_user(user_id)

    if account is not None and account['_id'] == user_id:
        if account['account']['prime']:
            # Получаем текущую дату
            current_date = datetime.today().date()
            emoji = "💮"
            current_datetime = datetime.combine(current_date, datetime.time(datetime.now()))

            # Извлекаем дату истечения пасса из базы данных (предполагаем, что это объект даты)
            if 'pass_expiration' in account:
                pass_expires = account['pass_expiration']
            else:
                expiration_date = current_datetime + timedelta(days=30)
                await mongodb.update_user(user_id, {"pass_expiration": expiration_date})
                pass_expires = expiration_date

            # Проверяем, истек ли пасс
            if current_datetime > pass_expires:
                # Обновляем статус prime на False
                await mongodb.update_user(user_id, {'account.prime': False})
        else:
            emoji = ""

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
            caption=f"\n 🪪  〢 Профиль {account['name']} {emoji}"
                    f"\n₊⊹ . . ݁ ⟡ ݁ . ⊹ ₊ ݁. ݁₊ ⊹ . ݁ ⟡ ݁ . . ⊹₊"
                    f"\n<blockquote>🎴 <b>{character}</b>"
                    f"\n🗺 Вселенная: {universe}"
                    f"\n🎐 <b>{rank}</b>"
                    f"\n⛩️ <b>{level}</b></blockquote>"
                    f"\n➖➖➖➖➖➖➖➖➖"
                    f"\n<i><b>❃💴 {account['account']['money']} ¥ " # ❃ {account['campaign']['power']} ⚜️ Мощи"
                    f"\n❃🀄️ {account['stats']['exp']} XP ❃ {total_characters} 🃏 Карт</b></i>",
            parse_mode=ParseMode.HTML,
            reply_markup=inline_builder(
                [f"🗯 {character}", "🎐 Баннеры", "〽️ Меню", "📜 Квесты", "🪄 Крафт", "🥡 Инвентарь", "⚙️ Настройки", "🎁 Рефераль"],
                ["talk", "banner", "tokio", "quests", "craft", "inventory", "settings", "referral"],
                row_width=[1, 2, 2, 2])
        )
        if isinstance(message, CallbackQuery):
            if avatar_type == 'photo':
                media = InputMediaPhoto(media=avatar)
            else:
                media = InputMediaAnimation(media=avatar)
            inline_id = message.inline_message_id
            await message.message.edit_media(media, inline_id)
            await message.message.edit_caption(inline_id, **pattern)
        else:
            if avatar_type == 'photo':
                await message.answer_photo(avatar, **pattern)
            else:
                await message.answer_animation(avatar, **pattern)
    else:
        await message.answer("📄 Ты не регистрирован"
                             "\n── •✧✧• ──────────"
                             "\n ❖ Нужно зарегистрироваться "
                             "и получить первую 🎴 карту. "
                             "\n ❖ Для этого отправь команду /start")


@router.message(F.animation)
async def file_id(message: Message):
    if message.chat.id == -1002127262362:
        await message.answer_animation(f"{message.animation.file_id}",
                                       caption=(f"❖ ✨ Редкость: None"
                                                f"\n❖ 🗺 Вселенная: None"
                                                f"\n\n   ✊🏻 Сила: 0"
                                                f"\n   👣 Ловкость: 0"
                                                f"\n   🧠 Интелект: 0"
                                                f"\n   ⚜️ Мощь: 000"))
                                       # caption=f"ID гифа, на который вы ответили: {message.animation.file_id}")

CAPTION = (
    "❖ ✨ Редкость: None"
    "\n❖ 🗺 Вселенная: None"
    "\n\n   ✊🏻 Сила: 0"
    "\n   👣 Ловкость: 0"
    "\n   🧠 Интелект: 0"
    "\n   ⚜️ Мощь: 000"
)

CHAT_ID = [-1002127262362, -1003227937544]

@router.message()
async def capture_any_message(message: Message):
    if message.chat.id not in CHAT_ID or not message.text:
        return
    try:
        file_id, flag = message.text.strip().rsplit(maxsplit=1)
    except ValueError:
        return

    flag = flag.lower()

    try:
        if flag == "p":
            await message.answer_photo(photo=file_id, caption=CAPTION)
        elif flag == "g":
            await message.answer_animation(animation=file_id, caption=CAPTION)
        else:
            return
    except TelegramBadRequest as e:
        await message.answer(
            f"Не получилось отправить как '{flag}'. Скорее всего file_id другого типа.\nОшибка: {e}"
        )

@router.message(F.photo)
async def file_id(message: Message):
    if message.chat.id == -1002127262362:
        await message.reply(f"ID фотографии, на которую вы ответили: {message.photo[-1].file_id}")


@router.message(Command("file_id"))
async def file_id(message: Message):
    if message.reply_to_message:
        if message.reply_to_message.photo:
            await message.reply(f"ID фотографии, на которую вы ответили: {message.reply_to_message.photo[-1].file_id} IDgroup{message.chat.id}")
        elif message.reply_to_message.animation:
            await message.reply(f"ID гифа, на который вы ответили: {message.reply_to_message.animation.file_id}")
    else:
        await message.reply("Пожалуйста, ответьте на сообщение с фотографией или гифкой.")


@router.callback_query(F.data == "referral")
async def referral_link(callback: CallbackQuery):
    user_id = callback.from_user.id
    account = await mongodb.get_user(user_id)
    media = InputMediaAnimation(media="CgACAgIAAx0CfstymgACBb9lzLfhJnj3lcZBeK1j3YTPUX6wfgACYkYAAsywaUpw0JLo7c7pRzQE")
    count = len(account['account']['referrals'])
    deep_link = f'https://t.me/AnimeKaisenbot?start={user_id}'
    text = (f'\n🎐 Ты получил особое приглашение в сообщество Multiverse!'
            f'\n🪽 Multiverse это мир где можешь насладиться плавной 🔮 Гачой, собирать своих 🎴 Персонажей, сражаться в '
            f'🏟️ Арене с другими игроками, стать ⚜️ сильным игроком, побеждать боссы 👾, вступить в кланы 🏯 и '
            f'найти друзей'
            f'\n Заходи по моей ссылке ниже и получай 🎁 Бонусы при регистрации:'
            f'\n{deep_link} '
            f'\n── •✧✧• ──────────'
            f'\nБудем рады тебя видеть :)')

    def share_keyboard():
        buttons = [
            [
                InlineKeyboardButton(text="👥 Рейтинг", callback_data="invite_rating"),
                InlineKeyboardButton(text="🎁 Получить", switch_inline_query=f"{text}")
            ],
            [
                InlineKeyboardButton(text="📦 Промокод", callback_data="promocode"),
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="main_page")
            ]
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        return keyboard

    await callback.message.edit_media(media)
    await callback.message.edit_caption(caption=
                                        f'\n ❖ ⛩️ Условия:'
                                        f'\n── •✧✧• ──────────'
                                        f'\n<blockquote expandable> • 🎁 Вы получите 🧧 священный билет за каждых 3 приглашенных игроков и 🌟 звезды телеграм если попадите в топ 👥 рейтинга приглашений'
                                        f'\n • ✅ Новые игроки считаються приглашенными только после того, '
                                        f'как они зарегистрировались по вашей реферальной ссылке и получили 🎴 первую карту.'
                                        f'\n • ⏱️ Рейтинг будет сбрасываться каждые две недели'
                                        f'\n • 📎 Игроки которые уже зарегистрировались не считаються приглашенными.'
                                        f'\n • 👥 Приглашая игроков вы поддерживаете развитие игры</blockquote>'
                                        f'\n🎐 Ваша реферальная ссылка:'
                                        f'\n<code>{deep_link}</code>'
                                        f'\n(Нажмите чтобы скопировать)'
                                        f'\n── •✧✧• ──────────'
                                        f'\n👥 вы пригласили {count} человек', reply_markup=share_keyboard())


@router.callback_query(F.data == "invite_rating")
async def invite_rating_handler(callback: CallbackQuery, bot: Bot):
    account = await mongodb.get_user(callback.from_user.id)
    rating = await mongodb.invite_rating("account.referrals", account)

    await callback.message.edit_caption(
        caption=rating,
        parse_mode="HTML",
        reply_markup=inline_builder(
            ["🔙 Назад"],
            ["referral"],
            row_width=[1])
    )
    await callback.answer()




@router.callback_query(F.data == "promocode")
async def apply_promo_code(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await state.set_state(Promo.promo)
    await callback.message.answer(text="❖ 📦 Введите промокод: ")


@router.message(Promo.promo)
async def form_name(message: Message, state: FSMContext):
    promo_code = message.text.upper().strip()
    user_id = message.from_user.id
    promo = await mongodb.find_promo(promo_code)
    if promo:
        if user_id not in promo.get('used_by', []):
            # Выдача награды
            reward = promo['reward']
            # Пример: Добавляем награду в инвентарь пользователя
            await mongodb.update_value(message.from_user.id, {'account.money': 5000})
            await mongodb.update_value(message.from_user.id, {'inventory.items.tickets.golden': 3})
            await mongodb.update_value(message.from_user.id, {'inventory.items.tickets.common': 5})

            # Обновляем список использовавших промокод

            await mongodb.update_promo(promo_code, user_id)

            await message.answer(f"❖ 📦 Промокод успешно применён! "
                                 f"\n • Ваша награда: "
                                 f"\n • {reward}")
            await state.clear()
        else:
            await message.answer("❖ ✅ Вы уже использовали этот промокод")
            await state.clear()
            return
    else:
        await message.answer("❖ ✖️ Промокод не найден")
        await state.clear()
        return
