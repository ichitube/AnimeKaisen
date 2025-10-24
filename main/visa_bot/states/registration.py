from aiogram.fsm.state import State, StatesGroup


class VisaRegistration(StatesGroup):
    first_name = State()
    last_name = State()
    phone_number = State()
    email = State()
    passport_photo = State()
    personal_photo = State()
    confirmation = State()
