from aiogram.filters.callback_data import CallbackData


class RegistrationCallbackFactory(CallbackData, prefix="visa"):
    action: str
