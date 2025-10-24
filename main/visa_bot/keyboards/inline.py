from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ..callbacks.factory import RegistrationCallbackFactory


def registration_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Ro'yxatdan o'tishni boshlash",
        callback_data=RegistrationCallbackFactory(action="start").pack()
    )
    builder.adjust(1)
    return builder.as_markup()


def confirmation_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Tasdiqlash",
        callback_data=RegistrationCallbackFactory(action="confirm").pack()
    )
    builder.button(
        text="Qayta kiritish",
        callback_data=RegistrationCallbackFactory(action="restart").pack()
    )
    builder.adjust(1)
    return builder.as_markup()
