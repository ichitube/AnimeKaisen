import random
import string

from aiogram import Router, Bot

from aiogram.types import Message
from aiogram.filters import Command
# from keyboards.builders import inline_builder
from data import mongodb
from data.mongodb import db

router = Router()

admins = [6946183730, 6462809130]

from datetime import datetime, timedelta
from aiogram import Bot


@router.message(Command("cheat_defense"))
async def file_id(message: Message):
    if message.from_user.id in admins:
        await mongodb.set_money(message)
    else:
        await message.reply(text="❖ ✖️ Ты не админ")


@router.message(Command("moneys"))
async def file_id(message: Message):
    if message.from_user.id in admins:
        await mongodb.give_to_all({"account.money": 5000}, message)
    else:
        await message.reply(text="❖ ✖️ Ты не админ")


@router.message(Command("reset_refs"))
async def reset_refs_cmd(message: Message):
    user_id = message.from_user.id
    account = await mongodb.get_user(user_id)
    if message.from_user.id in admins:  # проверка на админа
        text = await mongodb.reset_referrals(account)
        await message.answer(text, parse_mode="HTML", reply_markup=None, disable_web_page_preview=True)
    else:
        await message.reply("❖ ✖️ Ты не админ")


@router.message(Command("reset_wins"))
async def reset_wins(message: Message):
    users_id = message.from_user.id
    account = await mongodb.get_user(users_id)
    if message.from_user.id in admins:  # проверка на админа
        text = await mongodb.reset_wins(account)
        await message.answer(text, parse_mode="HTML", reply_markup=None, disable_web_page_preview=True)
    else:
        await message.reply("❖ ✖️ Ты не админ")


@router.message(Command("users"))
async def users_count(message: Message):
    if message.from_user.id in admins:
        users_c = await mongodb.users() + 1000
        await message.reply(f"{users_c}")
    else:
        await message.reply("❖ ✖️ Ты не админ")


@router.message(Command("chats"))
async def chats_count(message: Message):
    if message.from_user.id in admins:
        await message.reply(f"{mongodb.chats()}")
    else:
        await message.reply("❖ ✖️ Ты не админ")


@router.message(Command("slaves_0000"))
async def chats_count(message: Message):
    if message.from_user.id in admins:
        await mongodb.clear_slaves_for_all_users()
        await message.reply("успешно")
    else:
        await message.reply("❖ ✖️ Ты не админ")


@router.message(Command("slave_0000"))
async def chats_count(message: Message):
    if message.from_user.id in admins:
        await mongodb.clear_slave_for_all_users()
        await message.reply("успешно")
    else:
        await message.reply("❖ ✖️ Ты не админ")


@router.message(Command("user_id"))
async def chats_count(message: Message):
    await message.reply(f"{message.from_user.id}")


def generate_promo_code(length=6):
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


@router.message(Command("promo_generate"))
async def chats_count(message: Message):
    if message.from_user.id in admins:
        promo_code = generate_promo_code()
        await mongodb.add_promo_code(promo_code, "5000¥💴  3🎫 5🎟")
        await message.reply(f"📦 New Promo: {promo_code}")
    else:
        await message.reply("❖ ✖️ Ты не админ")


@router.message(Command("del_emoji"))
async def chats_count(message: Message):
    if message.from_user.id in admins:
        await mongodb.remove_emojis()
    else:
        await message.reply("❖ ✖️ Ты не админ")


@router.message(Command("reset_grab"))
async def chats_count(message: Message):
    if message.from_user.id in admins:
        await mongodb.install_zero()
    else:
        await message.reply("❖ ✖️ Ты не админ")


@router.message(Command("post"))
async def fill_profile(bot: Bot, message: Message):
    if message.from_user.id == 6946183730:
        # Извлекаем message_id из команды
        command_parts = message.text.split()
        if len(command_parts) == 2 and command_parts[1].isdigit():
            message_id = int(command_parts[1])

            async def forward_post_to_all_users(channel_id, msg):
                users = db.users.find()  # замените 'users' на имя вашей коллекции пользователей
                async for user in users:
                    try:
                        await bot.forward_message(chat_id=user['_id'], from_chat_id=channel_id, message_id=msg)
                    except Exception as e:
                        print(f"Не удалось переслать сообщение пользователю {user['_id']}: {e}")

                chats = db.chats.find()  # замените 'chats' на имя вашей коллекции чатов
                async for chat in chats:
                    try:
                        await bot.forward_message(chat_id=chat['_id'], from_chat_id=channel_id, message_id=msg)
                    except Exception as e:
                        print(f"Не удалось переслать сообщение в чат {chat['_id']}: {e}")

            await forward_post_to_all_users(channel_id=-1002042458477, msg=message_id)
        else:
            await message.answer("Пожалуйста, укажите корректный message_id после команды /post")
    else:
        await message.answer("У вас нет прав на выполнение этой команды")


@router.message(Command("message"))
async def send_message_to_all(bot: Bot, message: Message):
    if message.from_user.id in admins:
        # Извлекаем текст сообщения из команды
        command_parts = message.text.split(maxsplit=1)
        if len(command_parts) == 2:
            text_message = command_parts[1]

            async def send_message_to_all_users(text):
                users = db.users.find()  # замените 'users' на имя вашей коллекции пользователей
                async for user in users:
                    try:
                        await bot.send_message(chat_id=user['_id'], text=text)
                    except Exception as e:
                        print(f"Не удалось отправить сообщение пользователю {user['_id']}: {e}")

            await send_message_to_all_users(text_message)
        else:
            await message.answer("Пожалуйста, укажите текст сообщения после команды /message")
    else:
        await message.answer("У вас нет прав на выполнение этой команды")


@router.message(Command("chats"))
async def fill_profile(message: Message):
    if message.from_user.id in admins:
        chats = await mongodb.chats()
        await message.answer(f"Всего чатов: {chats}")
    else:
        await message.answer("У вас нет прав на выполнение этой команды")


@router.message(Command("migrate_characters"))
async def fill_profile(message: Message):
    if message.from_user.id in admins:
        await mongodb.migrate_characters()
        await message.answer(f"успешно")
    else:
        await message.answer("У вас нет прав на выполнение этой команды")


@router.message(Command("res"))
async def fill_profile(message: Message):
    if message.from_user.id in admins:
        args = message.text.split()
        if len(args) != 2 or not args[1].isdigit():
            await message.reply("Используйте: /res <user_id>")
            return

        user_id = int(args[1])
        try:
            await mongodb.update_user(user_id, {"battle.battle.status": 0})

            await message.reply(f"Статус пользователя {user_id} успешно сброшен!")
        except Exception as e:
            await message.reply(f"Пользователь {user_id} не найден в базе. Error: {e}")
    else:
        await message.answer("У вас нет прав на выполнение этой команды")

@router.message(Command("res"))
async def fill_profile(message: Message):
    if message.from_user.id in admins:
        args = message.text.split()
        if len(args) != 2 or not args[1].isdigit():
            await message.reply("Используйте: /res <user_id>")
            return

        user_id = int(args[1])
        try:
            await mongodb.update_user(user_id, {"battle.battle.status": 0})

            await message.reply(f"Статус пользователя {user_id} успешно сброшен!")
        except Exception as e:
            await message.reply(f"Пользователь {user_id} не найден в базе. Error: {e}")
    else:
        await message.answer("У вас нет прав на выполнение этой команды")

# @router.message(Command("t_f"))
# async def ret(message: Message):
#     await message.answer_photo("",
#                                caption=
#                                )
#
# @router.message(Command("t_a"))
# async def ret(message: Message):
#     await message.answer_animation(""
#                                    caption=
#     )
