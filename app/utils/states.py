from aiogram.fsm.state import State, StatesGroup


class Form(StatesGroup):
    name = State()
    universe = State()


class Name(StatesGroup):
    name = State()


class Mes(StatesGroup):
    msg = State()


class Character(StatesGroup):
    character = State()


class Universe(StatesGroup):
    universe = State()


class Promo(StatesGroup):
    promo = State()


class AI(StatesGroup):
    msg = State()


class ClanCreateState(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()


class ClanInvite(StatesGroup):
    waiting_for_user_id = State()


class ClanKick(StatesGroup):
    waiting_for_user_id = State()


class ClanSetName(StatesGroup):
    waiting_for_name = State()


class ClanSetDescription(StatesGroup):
    waiting_for_description = State()


class ClanMessage(StatesGroup):
    waiting_for_message = State()


class TestAvatar(StatesGroup):
    waiting_for_avatar = State()


class ClanDeleteConfirm(StatesGroup):
    waiting_confirm = State()


class ClanLeaveConfirm(StatesGroup):
    waiting_confirm = State()
