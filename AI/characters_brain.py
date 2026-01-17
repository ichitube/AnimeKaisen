import asyncio
import os, logging
from dotenv import load_dotenv

load_dotenv()  # подхватит .env из корня
from openai import OpenAI

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaAnimation, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from keyboards.builders import reply_builder, menu_button

from data import mongodb, character_photo
from utils.states import AI

router = Router()

# ===== OpenAI config =====
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logging.warning("OPENAI_API_KEY is not set")
client = OpenAI(api_key=OPENAI_API_KEY)

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
TEMP = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "200"))

async def ask_ai(messages: list[dict], model: str = MODEL) -> str:
    """Без блокировки event loop — зовём SDK в отдельном потоке."""
    def _call():
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=TEMP,
            max_tokens=MAX_TOKENS,
        )
        return resp.choices[0].message.content.strip()

    return await asyncio.to_thread(_call)

# ===== Старт диалога =====
@router.callback_query(F.data == "talk")
async def tokio(cb: CallbackQuery, state: FSMContext):
    user_id = cb.from_user.id
    account = await mongodb.get_user(user_id)
    universe = account["universe"]
    character = account["character"][universe]
    avatar = character_photo.get_stats(universe, character, "avatar")
    avatar_type = character_photo.get_stats(universe, character, "type")

    caption = f"Входим в мир Multiverse..."
    await asyncio.sleep(2)

    # корректное редактирование медиа в aiogram v3
    if avatar_type == "photo":
        await cb.message.edit_media(
            media=InputMediaPhoto(media=avatar, caption=caption, parse_mode="HTML")
        )
    else:
        await cb.message.edit_media(
            media=InputMediaAnimation(media=avatar, caption=caption, parse_mode="HTML")
        )

    await cb.message.answer("<blockquote>Привет</blockquote>", parse_mode="HTML", reply_markup=reply_builder("👋 Пока"))
    await state.set_state(AI.msg)
    await cb.answer()  # закрываем "часики" у инлайн-кнопки

# ===== Продолжение диалога =====
@router.message(AI.msg)
async def form_name(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    if not text:
        await message.answer("<i>Напишите что-нибудь…</i>", parse_mode="HTML")
        return

    user_id = message.from_user.id
    account = await mongodb.get_user(user_id)
    universe = account["universe"]
    character = account["character"][universe]

    context = f"Ты {character} из вселенной {universe}. Общайся с игроком по характеру персонажа."
    msgs = [
        {"role": "system", "content": "Ты — персонаж игрока. Отвечай кратко, естественно и в стиле персонажа."},
        {"role": "system", "content": context},
        {"role": "user", "content": text},
    ]

    try:
        answer = await ask_ai(msgs)
        await message.answer(f"<blockquote>{answer}</blockquote>", parse_mode="HTML")
        # остаёмся в состоянии для следующего реплая
        if text in ["👋 Пока", "пока", "Пока", "до свидания", "До свидания", "/stop_talk"]:
            await state.clear()
            await asyncio.sleep(2)
            await message.answer("возвращаемся в обычный мир...", reply_markup=menu_button())
        else:
            await state.set_state(AI.msg)
    except Exception as e:
        logging.exception("AI error")
        await message.answer(f"<blockquote>Ошибка AI: {e}</blockquote>", parse_mode="HTML")
        # состояние не сбрасываем — пользователь может повторить
