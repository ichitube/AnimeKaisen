from typing import Optional

from aiogram.filters.callback_data import CallbackData
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardButton, KeyboardButton
from aiogram.utils.keyboard import (ReplyKeyboardBuilder, InlineKeyboardBuilder,
                                    InlineKeyboardMarkup, ReplyKeyboardMarkup)


class Ability(CallbackData, prefix="fabnum"):
    action: str
    universe: Optional[str] = None
    character: Optional[str] = None
    back: Optional[str] = None


def profile(text: str | list):
    builder = ReplyKeyboardBuilder()

    if isinstance(text, str):
        text = [text]

    [builder.button(text=item) for item in text]
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def menu_button():
    kb = [
        [
            KeyboardButton(text='🪪 〢 Профиль'),
            KeyboardButton(text='〽️ Меню')
        ],
        [
            KeyboardButton(text='🎐 Баннеры'),
            KeyboardButton(text='🎌 Клан'),
            KeyboardButton(text='🏟️ Арена'),
            KeyboardButton(text='🏮 Рынок'),
        ],
        [
            KeyboardButton(text='🎴 Grab'),
            KeyboardButton(text='📜 Квесты'),
            KeyboardButton(text='🐦‍🔥Босс'),
            KeyboardButton(text='⛩️ Подземелье')
        ],
        [
            KeyboardButton(text='🥡 Инвентарь'),
            KeyboardButton(text='⚙️ Настройки')
        ]
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder='Anime Kaisen'
    )
    return keyboard


def menu_card_button():
    kb = [
        [
            KeyboardButton(text='🪪 〢 Профиль'),
            KeyboardButton(text='〽️ Меню')
        ],
        [
            KeyboardButton(text='🎐 Баннеры'),
            KeyboardButton(text='🎌 Клан'),
            KeyboardButton(text='🃏 Битва'),
            KeyboardButton(text='🏮 Рынок'),
        ],
        [
            KeyboardButton(text='🎴 Grab'),
            KeyboardButton(text='📜 Квесты'),
            KeyboardButton(text='🐦‍🔥Босс'),
            KeyboardButton(text='⛩️ Подземелье')
        ],
        [
            KeyboardButton(text='🥡 Инвентарь'),
            KeyboardButton(text='⚙️ Настройки')
        ]
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder='Anime Kaisen'
    )
    return keyboard


def registration():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text='Регистрироваться',
        callback_data="registration",
        url='https://t.me/AnimeKaisenBot?start=start')
    )

    return builder.as_markup()


def inline_builder(
    text: str | list[str],
    callback_data: str | list[str],
    row_width: int | list[int] = 2,
    **kwargs
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if isinstance(text, str):
        text = [text]
    if isinstance(callback_data, str):
        callback_data = [callback_data]
    if isinstance(row_width, int):
        row_width = [row_width]

    [
        builder.button(text=item, callback_data=cb)
        for item, cb in zip(text, callback_data)
    ]

    builder.adjust(*row_width)
    return builder.as_markup(**kwargs)


def abilities_kb(
    abilities: list[str] | tuple[str, ...],
    *,
    hp: int,
    mana: int,
    energy: int,
    cancel_text: str = "🏴‍☠️ Сдаться",
    columns: int = 2,
) -> ReplyKeyboardMarkup:

    # 1) Первая строка: статы
    rows: list[list[KeyboardButton]] = [
        [KeyboardButton(text=f"❤️ {hp} | 🧪 {mana} | 🪫 {energy}")]
    ]

    # 2) Навыки: раскладка по columns
    abilities = list(abilities)
    for i in range(0, len(abilities), columns):
        chunk = abilities[i:i + columns]
        rows.append([KeyboardButton(text=name) for name in chunk])

    # 3) Последняя строка: Сдаться
    rows.append([KeyboardButton(text=cancel_text)])

    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)

def reply_builder(
    text: str | list[str],
    row_width: int | list[int] = 2,
    **kwargs
) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    text = [text] if isinstance(text, str) else text
    row_width = [row_width] if isinstance(row_width, int) else row_width

    [
        builder.button(text=item)
        for item in text
    ]

    builder.adjust(*row_width)
    return builder.as_markup(resize_keyboard=True, **kwargs)


def get_common():
    builder = InlineKeyboardBuilder()

    builder.button(text="🎴 Схватить карту", callback_data="get_first_free")
    builder.button(text="🔙 Назад", callback_data="reg")

    builder.adjust(1)
    return builder.as_markup()


def success():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text='〽️ Меню',
        callback_data="main_page")
    )
    return builder.as_markup()


def subscribe():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text='⛩ Канал',
        url='https://t.me/Aniland_channel')
    )
    builder.add(InlineKeyboardButton(
        text='🍥 Группа',
        url='https://t.me/Comfort_chatick')
    )


def main_menu_button() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text='Главное меню', callback_data="arena")
    return builder.as_markup()


def start_button() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text='🪪 Регистрироваться', url='https://t.me/AnimeKaisenBot?start')
    return builder.as_markup()


def goto_bot() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text='💮 Перейти', url='https://t.me/AnimeKaisenBot')
    return builder.as_markup()


def channel_check() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text='🔓 Разблокировать', url='https://t.me/multiverse_card')
    return builder.as_markup()


class Pagination(CallbackData, prefix="pagination"):
    action: str
    page: int


def pagination_keyboard_chat(universe,  user_id, character, page: int = 0):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text='⬅️', callback_data=Pagination(action=f"prev_{user_id}", page=page).pack()),
        InlineKeyboardButton(text='➡️', callback_data=Pagination(action=f"next_{user_id}", page=page).pack())
    )
    # if universe not in ['Allstars', 'Allstars(old)']:
    #     builder.row(
    #         InlineKeyboardButton(text='🎴 Навыки', callback_data=Ability(action="ability", universe=universe,
    #                                                                     character=character, back='inventory').pack())
    #     )
    builder.row(
        InlineKeyboardButton(text='🪪 Установить', callback_data=f'change_character_{user_id}')
    )
    builder.row(
        InlineKeyboardButton(text='🔙 Назад', callback_data=f"inventory_{user_id}")
    )
    return builder.as_markup()


def pagination_keyboard(universe, character, page: int = 0):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text='⬅️', callback_data=Pagination(action="prev", page=page).pack()),
        InlineKeyboardButton(text='➡️', callback_data=Pagination(action="next", page=page).pack())
    )
    # if universe not in ['Allstars', 'Allstars(old)']:
    #     # builder.row(
    #     #     InlineKeyboardButton(text='🎴 Навыки', callback_data=Ability(action="ability", universe=universe,
    #     #                                                                 character=character, back='inventory').pack())
    #     # )
    builder.row(
        InlineKeyboardButton(text='🪪 Установить', callback_data='change_character')
    )
    builder.row(
        InlineKeyboardButton(text='🔙 Назад', callback_data="inventory")
    )
    return builder.as_markup()


def pagination_store(page: int = 0):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text='⬅️', callback_data=Pagination(action="prevv", page=page).pack()),
        InlineKeyboardButton(text='➡️', callback_data=Pagination(action="nextt", page=page).pack())
    )
    builder.row(
        InlineKeyboardButton(text='🔑 Купить', callback_data='buy_store_home')
    )
    builder.row(
        InlineKeyboardButton(text='🔙 Назад', callback_data="store")
    )
    return builder.as_markup()


def pagination_home(page: int = 0):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text='⬅️', callback_data=Pagination(action="prev_home", page=page).pack()),
        InlineKeyboardButton(text='➡️', callback_data=Pagination(action="next_home", page=page).pack())
    )
    builder.row(
        InlineKeyboardButton(text='🏠 Переехать', callback_data='set_home')
    )
    builder.row(
        InlineKeyboardButton(text='🔙 Назад', callback_data="home")
    )
    return builder.as_markup()


def pagination_slaves(page: int = 0):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text='⬅️', callback_data=Pagination(action="prev_slave", page=page).pack()),
        InlineKeyboardButton(text='➡️', callback_data=Pagination(action="next_slave", page=page).pack())
    )
    builder.row(
        InlineKeyboardButton(text='☑️ Выбрать', callback_data='set_slave')
    )
    builder.row(
        InlineKeyboardButton(text='🔙 Назад', callback_data="battle_arena")
    )
    return builder.as_markup()


def slaves_store(page: int = 0):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text='⬅️', callback_data=Pagination(action="prev_s", page=page).pack()),
        InlineKeyboardButton(text='➡️', callback_data=Pagination(action="next_s", page=page).pack())
    )
    builder.row(
        InlineKeyboardButton(text='🔖 Купить', callback_data='buy_slave')
    )
    builder.row(
        InlineKeyboardButton(text='🔙 Назад', callback_data="store")
    )
    return builder.as_markup()


def excard_store(page: int = 0):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text='⬅️', callback_data=Pagination(action="prev_excard", page=page).pack()),
        InlineKeyboardButton(text='➡️', callback_data=Pagination(action="next_excard", page=page).pack())
    )
    builder.row(
        InlineKeyboardButton(text='170🌟', callback_data='buy_excard')
    )
    builder.row(
        InlineKeyboardButton(text='🔙 Назад', callback_data="store")
    )
    return builder.as_markup()


def pagination_group(page: int = 0):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text='⬅️', callback_data=Pagination(action="g_prev", page=page).pack()),
        InlineKeyboardButton(text='➡️', callback_data=Pagination(action="g_next", page=page).pack())
    )
    builder.row(
        InlineKeyboardButton(text='🪪 Установить', callback_data='g_change_character')
    )
    builder.row(
        InlineKeyboardButton(text='🔙 Назад', callback_data="g_inventory")
    )
    return builder.as_markup()


def pagination_card(page: int = 0):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text='⬅️', callback_data=Pagination(action="d_prev", page=page).pack()),
        InlineKeyboardButton(text='➡️', callback_data=Pagination(action="d_next", page=page).pack())
    )
    builder.row(
        InlineKeyboardButton(text='✅ Выбрать', callback_data='d_choice_card')
    )
    builder.row(
        InlineKeyboardButton(text='🔙 Назад', callback_data="deck")
    )
    return builder.as_markup()


def pagination_dungeon(page: int = 0):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text='⬅️', callback_data=Pagination(action="dg_prev", page=page).pack()),
        InlineKeyboardButton(text='➡️', callback_data=Pagination(action="dg_next", page=page).pack())
    )
    builder.row(
        InlineKeyboardButton(text='✅ Выбрать', callback_data='dg_choice_card')
    )
    builder.row(
        InlineKeyboardButton(text='🔙 Назад', callback_data="dungeon")
    )
    return builder.as_markup()


def pagination_boss(page: int = 0):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text='⬅️', callback_data=Pagination(action="bg_prev", page=page).pack()),
        InlineKeyboardButton(text='➡️', callback_data=Pagination(action="bg_next", page=page).pack())
    )
    builder.row(
        InlineKeyboardButton(text='✅ Выбрать', callback_data='bg_choice_card')
    )
    builder.row(
        InlineKeyboardButton(text='🔙 Назад', callback_data="boss_squad")
    )
    return builder.as_markup()


def rm():
    return ReplyKeyboardRemove()
