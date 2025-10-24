import re
from typing import Any, Dict

from aiogram import F, Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ContentType, Message

from ..callbacks.factory import RegistrationCallbackFactory
from ..database.mongodb import save_application
from ..keyboards.inline import confirmation_keyboard, registration_keyboard
from ..states.registration import VisaRegistration

router = Router()

PHONE_PATTERN = re.compile(r"^\+?[0-9\s()-]{6,20}$")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


async def _reset_state(state: FSMContext) -> None:
    await state.clear()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await _reset_state(state)
    await message.answer(
        "Assalomu alaykum! Vizaga ariza topshirish uchun botga xush kelibsiz. "
        "Ro'yxatdan o'tish jarayonini boshlash uchun tugmani bosing.",
        reply_markup=registration_keyboard(),
    )


@router.callback_query(RegistrationCallbackFactory.filter(F.action == "start"))
async def start_registration(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    if callback.message:
        await callback.message.edit_reply_markup()
    await state.set_state(VisaRegistration.first_name)
    await callback.message.answer(
        "Iltimos, ismingizni kiriting (lotin alifbosida)."
    )


@router.message(StateFilter(VisaRegistration.first_name))
async def process_first_name(message: Message, state: FSMContext) -> None:
    if not message.text or len(message.text) < 2:
        await message.answer("Ism juda qisqa. Iltimos, qayta kiriting.")
        return

    await state.update_data(first_name=message.text.strip())
    await state.set_state(VisaRegistration.last_name)
    await message.answer("Familiyangizni kiriting (lotin alifbosida).")


@router.message(StateFilter(VisaRegistration.last_name))
async def process_last_name(message: Message, state: FSMContext) -> None:
    if not message.text or len(message.text) < 2:
        await message.answer("Familiya juda qisqa. Iltimos, qayta kiriting.")
        return

    await state.update_data(last_name=message.text.strip())
    await state.set_state(VisaRegistration.phone_number)
    await message.answer(
        "Telefon raqamingizni kiriting. Masalan: +998901234567"
    )


@router.message(StateFilter(VisaRegistration.phone_number))
async def process_phone_number(message: Message, state: FSMContext) -> None:
    if not message.text or not PHONE_PATTERN.match(message.text.strip()):
        await message.answer(
            "Telefon raqami noto'g'ri formatda. Iltimos, +998 bilan boshlanuvchi raqamni kiriting."
        )
        return

    await state.update_data(phone_number=message.text.strip())
    await state.set_state(VisaRegistration.email)
    await message.answer("Elektron pochtangizni kiriting. Masalan: user@example.com")


@router.message(StateFilter(VisaRegistration.email))
async def process_email(message: Message, state: FSMContext) -> None:
    if not message.text or not EMAIL_PATTERN.match(message.text.strip()):
        await message.answer(
            "Elektron pochta formati noto'g'ri. Iltimos, qayta urinib ko'ring."
        )
        return

    await state.update_data(email=message.text.strip())
    await state.set_state(VisaRegistration.passport_photo)
    await message.answer(
        "Pasportingizning fotosuratini yuboring. Ilova sifatida fayl yoki surat yuborishingiz mumkin.",
    )


@router.message(StateFilter(VisaRegistration.passport_photo), F.content_type.in_({ContentType.PHOTO, ContentType.DOCUMENT}))
async def process_passport_photo(message: Message, state: FSMContext) -> None:
    file_id = message.photo[-1].file_id if message.photo else message.document.file_id
    await state.update_data(passport_photo=file_id)
    await state.set_state(VisaRegistration.personal_photo)
    await message.answer(
        "Endi o'zingizning aniq ko'rinadigan fotosuratingizni yuboring."
    )


@router.message(StateFilter(VisaRegistration.passport_photo))
async def process_passport_photo_invalid(message: Message) -> None:
    await message.answer("Iltimos, pasport fotosuratini yuboring.")


@router.message(StateFilter(VisaRegistration.personal_photo), F.content_type == ContentType.PHOTO)
async def process_personal_photo(message: Message, state: FSMContext) -> None:
    await state.update_data(personal_photo=message.photo[-1].file_id)
    await state.set_state(VisaRegistration.confirmation)

    data = await state.get_data()
    await message.answer(
        "Ma'lumotlaringiz:\n"
        f"Ism: {data['first_name']}\n"
        f"Familiya: {data['last_name']}\n"
        f"Telefon: {data['phone_number']}\n"
        f"Email: {data['email']}\n"
        "\nHammasi to'g'rimi?", 
        reply_markup=confirmation_keyboard(),
    )


@router.message(StateFilter(VisaRegistration.personal_photo))
async def process_personal_photo_invalid(message: Message) -> None:
    await message.answer("Iltimos, o'zingizning fotosuratingizni yuboring.")


@router.callback_query(RegistrationCallbackFactory.filter(F.action == "restart"), StateFilter(VisaRegistration.confirmation))
async def restart_registration(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    if callback.message:
        await callback.message.edit_reply_markup()
    await _reset_state(state)
    await callback.message.answer(
        "Ma'lumotlarni boshidan kiritish uchun ismni qayta kiriting."
    )
    await state.set_state(VisaRegistration.first_name)


@router.callback_query(RegistrationCallbackFactory.filter(F.action == "confirm"), StateFilter(VisaRegistration.confirmation))
async def confirm_registration(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer("Ma'lumotlar saqlandi")
    if callback.message:
        await callback.message.edit_reply_markup()
    data: Dict[str, Any] = await state.get_data()
    data.update(user_id=callback.from_user.id)
    await save_application(data)
    await callback.message.answer(
        "Rahmat! Arizangiz qabul qilindi. Tez orada operatorlarimiz siz bilan bog'lanadi."
    )
    await _reset_state(state)


@router.message()
async def fallback_handler(message: Message) -> None:
    await message.answer(
        "Iltimos, /start buyrug'i orqali ro'yxatdan o'tishni boshlang."
    )
