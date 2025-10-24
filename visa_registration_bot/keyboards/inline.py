from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from ..callbacks import RegistrationCallbackFactory


def registration_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Ro'yxatdan o'tishni boshlash",
                    callback_data=RegistrationCallbackFactory(action="start").pack(),
                )
            ]
        ]
    )


def confirmation_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Tasdiqlash",
                    callback_data=RegistrationCallbackFactory(action="confirm").pack(),
                )
            ],
            [
                InlineKeyboardButton(
                    text="Qaytadan boshlash",
                    callback_data=RegistrationCallbackFactory(action="restart").pack(),
                )
            ],
        ]
    )
