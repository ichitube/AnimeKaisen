import re

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InputMediaAnimation, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from datetime import datetime
from data import mongodb, character_photo
from utils.states import ClanCreateState, ClanInvite, ClanSetName, ClanSetDescription, ClanMessage
from keyboards.builders import inline_builder
from filters.chat_type import ChatTypeFilter

router = Router()

bot = Bot


@router.callback_query(F.data == "clan")
@router.message(ChatTypeFilter(chat_type=["private"]), F.text == "🎌 Клан")
async def clan(callback: CallbackQuery | Message):
    user_id = callback.from_user.id
    account = await mongodb.get_user(user_id)
    if 'clan' not in account:
        await mongodb.update_user(user_id, {"clan": ''})
    account = await mongodb.get_user(user_id)
    if account['clan'] == '':
        photo = "AgACAgIAAx0CfstymgACP5loE0hAO9ZGih89GqGD2Tx4AAGAcqIAArX1MRs4K3lImeuKFTTzxawBAAMCAAN5AAM2BA"
        pattern = dict(caption="❖ 🏯 Кланы 🎌"
                               "\n── •✧✧• ────────"
                               "\n 🏯 Кланы - это возможность объединиться с другими игроками и вместе достигать 📈 новых высот!"
                               "\n\n 🎌 Вы можете создать свой клан или отправить ✉️ заявку в уже существующий клан."
                               "\n\n 🔸 Чтобы создать клан и стать лидером, необходимо статус 💮Pass и 100 000 💴.",
                       reply_markup=inline_builder(
                        ["🎌 Создать клан • 100 000 💴", "✉️ Вступить в клан", "🔙 Назад"],
                        ["clan_create", "clan_join", "tokio"],
                       row_width=[1],
                       )
                )
        if isinstance(callback, CallbackQuery):
            await callback.message.edit_media(InputMediaPhoto(media=photo), inline_message_id=callback.inline_message_id)
            await callback.message.edit_caption(callback.inline_message_id, **pattern)
        else:
            await callback.answer_photo(photo, **pattern)
    else:
        clan = await mongodb.get_clan(account['clan'])
        members = clan.get("members", [])

        members_list = []

        for uid in members:
            user = await mongodb.get_user(uid)
            power = user.get("campaign", {}).get("power", 0)  # без краша, если нет campaign/power
            name = user.get("name", "Безымянный")
            members_list.append(f" • 🪪 {name} — ⚜️ {power}")

        leader = await mongodb.get_user(clan["leader_id"])
        leader_name = leader["name"]
        result_text = "\n ".join(members_list)
        text = (f"❖ 🏯 Клан {clan["_id"]} 🎌"
                f"\n── •✧✧• ───────"
                f"\n • 📃 {clan["description"]}"
                # f"\n📈 Статистика клана:"
                f"\n<blockquote> {result_text}</blockquote>"
                f"\n👑 Лидер: {leader_name}"
                "\n➖➖➖➖➖➖➖➖➖"
                # f"\n── •✧✧• ────────"
                f"\n 📇 участники {len(clan["members"])} из 10")

        if clan["leader_id"] == user_id:
            pattern = dict(
                caption=text,
                reply_markup=inline_builder(
                    ["⛺️ Лавка", "✉️ Пригласить", "📩 Заявки", "📇 Участники",
                     "⚙️ Настройки", "🔙 Назад", "🚪 Покинуть"],
                    ["clan_shop", "clan_invite", "clan_requests", "clan_members",
                     "clan_settings", "tokio", "clan_leave"],
                    row_width=[1, 2, 2, 2]
                ))
        else:
            pattern = dict(
                caption=text,
                reply_markup=inline_builder(
                    ["⛺️ Лавка", "📇 Участники", "✉️ Пригласить", "🔙 Назад", "🚪 Покинуть"],
                    ["clan_shop", "clan_members", "clan_invite", "tokio", "clan_leave"],
                    row_width=[1, 2, 2]
                ))
        photo = "AgACAgIAAx0CfstymgACP59oE0iWEKpBhEVlnGE4ImHCnb_rtwACvPUxGzgreUhUW6a7vrBxmgEAAwIAA3kAAzYE"
        if isinstance(callback, CallbackQuery):
            await callback.message.edit_media(InputMediaPhoto(media=photo), inline_message_id=callback.inline_message_id)
            await callback.message.edit_caption(inline_message_id=callback.inline_message_id, **pattern)
        else:
            await callback.answer_photo(photo, **pattern)


@router.callback_query(F.data == "clan_members")
async def show_members(callback: CallbackQuery):
    user_id = callback.from_user.id
    account = await mongodb.get_user(user_id)
    clan_name = account["clan"]
    clan = await mongodb.db.clans.find_one({"_id": clan_name})

    if not clan:
        await callback.answer("❖ ✖️ Клан не найден", show_alert=True)
        return

    members = clan.get("members", [])
    member_names = []
    for uid in members:
        user = await mongodb.get_user(uid)
        if uid == clan["leader_id"]:
            member_names.append(f" • 👑 {user['name']} (Лидер)")
        else:
            member_names.append(f" • 🪪 {user["name"]}")

    member_list = "\n".join(member_names)
    buttons = ["🔙 Назад"]
    callbacks = ["clan"]

    if account["_id"] == clan["leader_id"]:
        buttons.insert(0, "🚪 Выгнать участника")
        callbacks.insert(0, "clan_kick")
        buttons.insert(1, "📜 Написать сообщение")
        callbacks.insert(1, "clan_message")
    media = InputMediaPhoto(media="AgACAgIAAx0CfstymgACP5toE0hLvcp1ZPqf0PPhn0fg9Rq7zAACtPUxGzgreUht0_3v-laN7QEAAwIAA3kAAzYE")
    await callback.message.edit_media(media=media)
    await callback.message.edit_caption(
        caption=f"❖ 📇 Участники клана:"
                f"\n── •✧✧• ────────"
                f"\n{member_list}",
        reply_markup=inline_builder(
            buttons,
            callbacks,
            row_width=[1]
        )
    )


@router.callback_query(F.data == "clan_message")
async def send_message(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("❖ ✍️ Введите сообщение для участников клана:")
    await state.set_state(ClanMessage.waiting_for_message)


@router.message(ClanMessage.waiting_for_message)
async def process_message(message: Message, bot: Bot):
    user_id = message.from_user.id
    account = await mongodb.get_user(user_id)
    clan_name = account["clan"]
    clan = await mongodb.db.clans.find_one({"_id": clan_name})

    if not clan:
        await message.answer("❖ ✖️ Клан не найден", show_alert=True)
        return

    members = clan.get("members", [])
    message_text = message.text

    for uid in members:
        if uid != user_id:
            await bot.send_message(
                chat_id=uid,
                text=f"❖ 📜 Сообщение от лидера клана:\n  •  {message_text}"
            )
    await message.answer("❖ ✅ Сообщение отправлено всем участникам клана")


@router.callback_query(F.data == "clan_create")
async def start_clan_creation(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    # Проверка: уже в клане?
    account = await mongodb.get_user(user_id)

    if not account['account']['prime']:
        await callback.answer("❖ 🔸 Для создание клана необходимо статус 💮Pass", show_alert=True)
        return

    if account["account"]["money"] < 100000:
        amount = 100000 - account["account"]["money"]
        await callback.answer(f"❖ ✖️ Не хватает {amount} денег для создания клана", show_alert=True)
        return

    if account["clan"] != '':
        await callback.answer("❖ ✖️ Вы уже состоите в клане")
        return

    await state.set_state(ClanCreateState.waiting_for_name)
    await callback.message.answer("❖ 🏷 Введите название нового клана:")


@router.message(ClanCreateState.waiting_for_name)
async def clan_set_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(ClanCreateState.waiting_for_description)
    await message.answer("❖ 📃 Введите описание клана:")


@router.message(ClanCreateState.waiting_for_description)
async def clan_set_description(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    name = data["name"]
    desc = message.text
    account = await mongodb.get_user(user_id)

    if account["account"]["money"] < 100000:
        amount = 100000 - account["account"]["money"]
        await message.answer(f"❖ ✖️ Не хватает {amount} денег для создания клана")
        return

    # Проверка на существование
    clan_exists = await mongodb.clan_exists(name)
    if clan_exists:
        await message.answer("❖ ✖️ Клан с таким названием уже существует")
        return

    # Проверка на длину названия
    if len(name) > 20:
        await message.answer("❖ ✖️ Название клана слишком длинное (максимум 20 символов)")
        return

    # отнимаем 100000
    money = account["account"]["money"]
    await mongodb.update_user(user_id, {"account.money": money - 100000})

    # Создание в базе
    await mongodb.create_clan({
        "_id": name,
        "leader_id": user_id,
        "members": [user_id],
        "invites": [],
        "requests": [],
        "description": desc,
        "created_at": datetime.now(),
        "total_members": 1
    })

    # Привязка клана к пользователю
    await mongodb.update_user(user_id, {"clan": name})

    await state.clear()
    await message.answer(f"❖ ✅ Клан {name} создан! Вы стали его лидером")


MAX_CLAN_MEMBERS = 10


@router.callback_query(F.data == "clan_join")
async def show_available_clans(callback: CallbackQuery):
    available_clans = await mongodb.db.clans.find({
        "$expr": {
            "$lt": [{"$size": "$members"}, 10]
        }}).to_list(length=100)

    if not available_clans:
        await callback.message.edit_caption("❖ 🏯 Кланы 🎌"
                                            "\n── •✧✧• ────────"
                                            "\n❖ ✖️ Нет кланов с доступными местами",
                                            reply_markup=inline_builder(
                                                ["🔙 Назад"],
                                                ["clan"],
                                                row_width=[1]
                                            ))
        return

    buttons = []
    callbacks = []

    for clan in available_clans:
        buttons.append(f"🏯 {clan['_id']} ({len(clan['members'])}/{MAX_CLAN_MEMBERS})")
        callbacks.append(f"clan_request_{clan['_id']}")

    buttons.append("🔙 Назад")
    callbacks.append("clan")
    await callback.message.edit_caption(
        inline_message_id=callback.inline_message_id,
        caption="❖ 🏯 Кланы 🎌"
                "\n── •✧✧• ────────"
                "\n❖ 📜 Список кланов с доступными местами:",
        reply_markup=inline_builder(buttons, callbacks, row_width=[1])
    )


@router.callback_query(F.data.startswith("clan_request_"))
async def request_to_clan(callback: CallbackQuery):
    user_id = callback.from_user.id
    clan_name = callback.data.replace("clan_request_", "")

    user = await mongodb.get_user(user_id)
    if user["clan"] != "":
        await callback.answer("❖ ✖️ Вы уже состоите в клане", show_alert=True)
        return

    clan = await mongodb.db.clans.find_one({"_id": clan_name})
    if not clan:
        await callback.answer("❖ ✖️ Клан не найден", show_alert=True)
        return

    if user_id in clan.get("requests", []):
        await callback.answer("❖ ✅ Вы уже подали заявку", show_alert=True)
        return

    if len(clan["members"]) >= MAX_CLAN_MEMBERS:
        await callback.answer("❖ 🙁 В клане больше нет мест", show_alert=True)
        return

    await mongodb.db.clans.update_one(
        {"_id": clan_name},
        {"$addToSet": {"requests": user_id}}
    )
    await callback.answer("❖ ✅ Заявка на вступление отправлена", show_alert=True)


@router.callback_query(F.data == "clan_invite")
async def invite_prompt(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("❖ Введите ID пользователя, которого хотите пригласить:")
    await state.set_state(ClanInvite.waiting_for_user_id)
    await state.update_data(leader_id=callback.from_user.id)


@router.message(ClanInvite.waiting_for_user_id)
async def process_invite_id(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    leader_id = data["leader_id"]

    try:
        invited_id = int(message.text)
    except ValueError:
        await message.answer("❖ ✖️ Неверный формат ID. попробуйте заново и введите числом")
        await state.clear()
        return

    user = await mongodb.get_user(invited_id)
    if "clan" in user:
        await message.answer("❖ ✖️ Пользователь уже в клане")
        return

    clan_name = (await mongodb.get_user(leader_id)).get("clan")
    await mongodb.db.clans.update_one({"_id": clan_name}, {"$addToSet": {"invites": invited_id}})

    await bot.send_message(
        chat_id=invited_id,
        text=f"❖ 🎌 Вас пригласили в клан {clan_name}. Принять приглашение?",
        reply_markup=inline_builder(["✅ Принять", "✖️ Отказаться"],
                                    [f"accept_invite_{clan_name}", f"decline_invite_{clan_name}"])
    )

    await message.answer("❖ ✅ Приглашение отправлено")
    await state.clear()


@router.callback_query(F.data.startswith("accept_invite_"))
async def accept_invite(callback: CallbackQuery, bot: Bot):
    clan_name = callback.data.split("_")[-1]
    user_id = callback.from_user.id
    account = await mongodb.get_user(user_id)
    name = account["name"]

    clan = await mongodb.db.clans.find_one({"_id": clan_name})
    if not clan:
        await callback.answer("❖ ✖️ Клан не найден")
        return

    if user_id in clan.get("members", []):
        await callback.answer("❖ ✖️ Вы уже в этом клане")
        return

    if len(clan["members"]) >= MAX_CLAN_MEMBERS:
        await callback.answer("❖ ✖️ В клане больше нет мест")
        return

    await mongodb.db.clans.update_one(
        {"_id": clan_name},
        {"$addToSet": {"members": user_id}, "$pull": {"invites": user_id}}
    )
    await mongodb.update_user(user_id, {"clan": clan_name})

    await bot.send_message(chat_id=user_id, text=f"❖ ✅ Вы вступили в клан {clan_name}")
    await bot.send_message(
        chat_id=clan["leader_id"],
        text=f"❖ ✅ {name} принял приглашение в клан {clan_name}"
    )
    await callback.answer("❖ ✅ Вы приняли приглашение")
    await callback.message.delete()


@router.callback_query(F.data.startswith("decline_invite_"))
async def decline_invite(callback: CallbackQuery, bot: Bot):
    clan_name = callback.data.split("_")[-1]
    user_id = callback.from_user.id
    account = await mongodb.get_user(user_id)
    name = account["name"]

    clan = await mongodb.db.clans.find_one({"_id": clan_name})
    if not clan:
        await callback.answer("❖ ✖️ Клан не найден")
        return

    await mongodb.db.clans.update_one(
        {"_id": clan_name},
        {"$pull": {"invites": user_id}}
    )
    await bot.send_message(chat_id=clan["leader_id"], text=f"❖ ✖️ {name} отклонил приглашение в клан {clan_name}")
    await callback.answer("❖ ✖️ Вы отклонили приглашение")
    await callback.message.delete()


@router.callback_query(F.data == "clan_requests")
async def show_requests(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await mongodb.get_user(user_id)
    clan_name = user.get("clan")
    clan = await mongodb.db.clans.find_one({"_id": clan_name})

    if not clan or clan["leader_id"] != user_id:
        await callback.answer("❖ ✖️ Только лидер может просматривать заявки")
        return

    requests = clan.get("requests", [])
    if not requests:
        await callback.message.edit_caption(caption="❖ 📭 Заявок на вступление нет",
                                            reply_markup=inline_builder(
                                                ["🔙 Назад"],
                                                ["clan"],
                                                row_width=[1]
                                            ))
        return

    ids = [uid for uid in requests]
    names = []

    for uid in ids:
        user = await mongodb.get_user(uid)
        if user and "name" in user:
            names.append(user["name"])
        else:
            names.append("❓Неизвестно")
    callbacks = [f"accept_or_reject_req_{uid}" for uid in requests]

    button = []

    if len(requests) > 5:
        requests = requests[:5]
        button += ["➡️", "🔙 Назад"]
        callbacks += ["next_requests", "clan"]
    else:
        button += ["🔙 Назад"]
        callbacks += ["clan"]

    buttons = [f"📨 {uid}" for uid in requests] + button

    us = ""
    for i in range(len(names)):
        us += f"\n • 🪪 {names[i]} | 🆔 {ids[i]}"

    await callback.message.edit_caption(
        caption="❖ 📭 Заявки на вступление в клан:"
                f"\n── •✧✧• ────────"
                f"{us}",
        reply_markup=inline_builder(buttons, callbacks, row_width=[1])
    )


@router.callback_query(F.data.startswith("accept_or_reject_req_"))
async def accept_or_reject_request(callback: CallbackQuery):
    user_id = callback.from_user.id
    target_id = int(callback.data.split("_")[-1])
    account = await mongodb.get_user(target_id)
    universe = account["universe"]
    character = account['character'][account['universe']]

    if target_id == user_id:
        await callback.answer("❖ ✖️ Вы не можете принять свою заявку")
        return

    avatar = character_photo.get_stats(universe, character, 'avatar')
    avatar_type = character_photo.get_stats(universe, character, 'type')

    if avatar_type == 'photo':
        media = InputMediaPhoto(media=avatar)
    else:
        media = InputMediaAnimation(media=avatar)

    await callback.message.edit_media(media)
    await callback.message.edit_caption(
        caption=f"\n ❖ 🪪 {account["name"]}:"
                f"\n── •✧✧• ────────"
                f"\n • 🀄️ exp: {account["stats"]["exp"]}  💴 money: {account["account"]["money"]}",
        reply_markup=inline_builder(["✅ Принять", "✖️ Отклонить", "🔙 Назад"],
                                    [f"accept_req_{target_id}", f"decline_req_{target_id}", "clan_requests"])
    )


@router.callback_query(F.data.startswith("accept_req_"))
async def accept_request(callback: CallbackQuery, bot: Bot):
    target_id = int(callback.data.split("_")[-1])
    leader_id = callback.from_user.id
    user = await mongodb.get_user(leader_id)
    clan_name = user.get("clan")
    account = await mongodb.get_user(target_id)
    name = account["name"]

    clan = await mongodb.db.clans.find_one({"_id": clan_name})
    if len(clan["members"]) >= MAX_CLAN_MEMBERS:
        await callback.answer("❖ ✖️ В клане уже максимум участников")
        return

    await mongodb.db.clans.update_one(
        {"_id": clan_name},
        {"$pull": {"requests": target_id}, "$addToSet": {"members": target_id}}
    )
    await mongodb.update_user(target_id, {"clan": clan_name})
    await bot.send_message(chat_id=target_id, text=f"✅ Ваша заявка в клан {clan_name} была одобрена!")
    await callback.answer("❖ ✅ Участник добавлен", show_alert=True)
    await callback.message.answer(f"❖ ➕ {name} вступил в клан")
    await show_requests(callback)


@router.callback_query(F.data.startswith("decline_req_"))
async def decline_request(callback: CallbackQuery, bot: Bot):
    target_id = int(callback.data.split("_")[-1])
    user = await mongodb.get_user(callback.from_user.id)
    clan_name = user.get("clan")
    await mongodb.db.clans.update_one({"_id": clan_name}, {"$pull": {"requests": target_id}})
    await bot.send_message(chat_id=target_id, text=f"❖ ✖️ Ваша заявка в клан {clan_name} была отклонена")
    await callback.answer("❖ ✖️ Заявка отклонена", show_alert=True)
    await show_requests(callback)


@router.callback_query(F.data == "clan_pass_leader")
async def pass_leadership(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    clan_name = (await mongodb.get_user(user_id)).get("clan")
    clan = await mongodb.db.clans.find_one({"_id": clan_name})

    members = [uid for uid in clan["members"] if uid != user_id]
    if not members:
        await callback.answer("❖ ✖️ Некому передать лидерство")
        return
    # берем первых 5 участников
    buttons = [f"🎴 {uid}" for uid in members[:5]]
    callbacks = [f"new_leader_{uid}" for uid in members]
    if len(members) > 5:
        buttons += ["➡️", "🔙 Назад"]
        callbacks += ["next_leader", "clan"]
    else:
        buttons += ["🔙 Назад"]
        callbacks += ["clan"]

    await callback.message.answer("❖ Кому передать лидерство?", reply_markup=inline_builder(buttons, callbacks, row_width=[1]))


@router.callback_query(F.data == "next_leader")
async def prev_leader(callback: CallbackQuery, state: FSMContext):
    # показываем участников с 6 по 11
    user_id = callback.from_user.id
    clan_name = (await mongodb.get_user(user_id)).get("clan")
    clan = await mongodb.db.clans.find_one({"_id": clan_name})
    members = [uid for uid in clan["members"] if uid != user_id]
    if len(members) <= 5:
        await callback.answer("❖ ✖️ Некому передать лидерство")
        return
    # берем участников с 6 по 11
    buttons = [f"🎴 {uid}" for uid in members[5:11]]
    callbacks = [f"new_leader_{uid}" for uid in members[5:11]]
    buttons += ["⬅️", "🔙 Назад"]
    callbacks += ["prev_leader", "clan"]

    await callback.message.edit_reply_markup(reply_markup=inline_builder(buttons, callbacks, row_width=[1]))


@router.callback_query(F.data == "prev_leader")
async def prev_leader(callback: CallbackQuery, state: FSMContext):
    # показываем участников с 0 по 5
    user_id = callback.from_user.id
    clan_name = (await mongodb.get_user(user_id)).get("clan")
    clan = await mongodb.db.clans.find_one({"_id": clan_name})
    members = [uid for uid in clan["members"] if uid != user_id]
    if len(members) <= 5:
        await callback.answer("❖ ✖️ Некому передать лидерство")
        return
    # берем участников с 0 по 5
    buttons = [f"🎴 {uid}" for uid in members[:5]]
    callbacks = [f"new_leader_{uid}" for uid in members[:5]]
    if len(members) > 5:
        buttons += ["➡️", "🔙 Назад"]
        callbacks += ["next_leader", "clan"]
    else:
        buttons += ["🔙 Назад"]
        callbacks += ["clan"]

    await callback.message.edit_reply_markup(reply_markup=inline_builder(buttons, callbacks, row_width=[1]))


@router.callback_query(F.data.startswith("new_leader_"))
async def confirm_new_leader(callback: CallbackQuery, bot: Bot):
    new_leader = int(callback.data.split("_")[-1])
    old_leader = callback.from_user.id
    clan_name = (await mongodb.get_user(old_leader)).get("clan")
    await mongodb.db.clans.update_one({"_id": clan_name}, {"$set": {"leader_id": new_leader}})
    await callback.answer("❖ ✅ Лидерство передано")
    await bot.send_message(chat_id=new_leader, text=f"❖ 👑 Вы стали лидером клана {clan_name}")


@router.callback_query(F.data == "clan_settings")
async def clan_settings(callback: CallbackQuery):
    user_id = callback.from_user.id
    account = await mongodb.get_user(user_id)
    clan_name = account["clan"]
    clan = await mongodb.db.clans.find_one({"_id": clan_name})

    if not clan or clan["leader_id"] != user_id:
        await callback.answer("❖ ✖️ Только лидер может изменять настройки клана")
        return

    await callback.message.edit_caption(
        caption=f"❖ ⚙️ Настройки клана"
                f"\n── •✧✧• ────────"
                f"\n • 🏷 Название: {clan["_id"]}"
                f"\n\n • 📃 Описание: {clan["description"]}",
        reply_markup=inline_builder(
            ["📝 Изменить описание", "🏷 Переименовать", "🔥 Удалить клан", "🔙 Назад"],
            ["clan_edit_desc", "clan_rename", "delete_clan", "clan"],
            row_width=[1]
        )
    )


@router.callback_query(F.data == "delete_clan")
async def delete_clan(callback: CallbackQuery):
    user_id = callback.from_user.id
    account = await mongodb.get_user(user_id)
    clan_name = account["clan"]
    clan = await mongodb.db.clans.find_one({"_id": clan_name})

    await mongodb.delete_clan(clan_name)
    await mongodb.update_user(user_id, {"clan": ""})
    for uid in clan["members"]:
        await mongodb.update_user(uid, {"clan": ""})
    await callback.message.answer("🔥")
    await callback.answer("❖ ✅ Клан удален", show_alert=True)
    await callback.message.delete()


@router.callback_query(F.data == "clan_edit_desc")
async def edit_desc_prompt(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ClanSetDescription.waiting_for_description)
    await callback.message.answer("❖ 📃 Введите новое описание клана:")


@router.message(ClanSetDescription.waiting_for_description)
async def edit_clan_desc(message: Message, state: FSMContext):
    user_id = message.from_user.id
    new_desc = message.text
    clan_name = (await mongodb.get_user(user_id)).get("clan")

    await mongodb.update_clan(clan_name, {"description": new_desc})
    await message.answer("❖ ✅ Описание клана обновлено")
    await state.clear()


@router.callback_query(F.data == "clan_rename")
async def rename_prompt(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ClanSetName.waiting_for_name)
    await callback.message.answer("❖ 🏷 Введите новое название клана:")


@router.message(ClanSetName.waiting_for_name)
async def rename_clan(message: Message, state: FSMContext):
    user_id = message.from_user.id
    new_name = message.text

    # Проверка на существование
    clan_exists = await mongodb.clan_exists(new_name)
    if clan_exists:
        await message.answer("❖ ✖️ Клан с таким названием уже существует", show_alert=True)
        return


     # проверка на переименование или создание
    account = await mongodb.get_user(user_id)
    clan = account["clan"]
    # переименуем клана
    await mongodb.rename_clan(clan, new_name)
    # # обновляем название у всех участников клана
    # for uid in clan["members"]:
    #     await mongodb.update_user(uid, {"clan": new_name})
    await message.answer(f"❖ ✅ Клан переименован в {new_name}", show_alert=True)
    await state.clear()


@router.callback_query(F.data == "clan_kick")
async def kick_prompt(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    clan_name = (await mongodb.get_user(user_id)).get("clan")
    clan = await mongodb.db.clans.find_one({"_id": clan_name})

    if clan["leader_id"] != user_id:
        await callback.answer("❖ ✖️ Только лидер может кикать участников")
        return

    members = [uid for uid in clan["members"] if uid != user_id]
    # получаем имена этих участников
    member_names = []
    for uid in members:
        user = await mongodb.get_user(uid)
        if uid == clan["leader_id"]:
            member_names.append(f" • 👑 {user['name']} (Лидер)")
        else:
            member_names.append(f" • 🪪 {user['name']}")
    if not members:
        await callback.answer("❖ ✖️ Некого кикать")
        return

    clean_names = []

    for line in member_names:
        match = re.search(r"<b>(.*?)</b>", line)
        if match:
            clean_names.append(match.group(1))  # Взяли только текст из <b>Имя</b>
        else:
            clean_names.append(line)

    # берем первых 5 участников
    buttons = [f"{uid}" for uid in clean_names[:5]]
    callbacks = [f"kick_{uid}" for uid in members[:5]]
    if len(members) > 5:
        buttons += ["➡️", "🔙 Назад"]
        callbacks += ["next_kick", "clan"]
    else:
        buttons += ["🔙 Назад"]
        callbacks += ["clan"]
    await callback.message.edit_reply_markup(inline_message_id=callback.inline_message_id,
                                             reply_markup=inline_builder(buttons, callbacks, row_width=[1]))


@router.callback_query(F.data == "next_kick")
async def next_kick(callback: CallbackQuery):
    # показываем участников с 6 по 11
    user_id = callback.from_user.id
    clan_name = (await mongodb.get_user(user_id)).get("clan")
    clan = await mongodb.db.clans.find_one({"_id": clan_name})
    members = [uid for uid in clan["members"] if uid != user_id]
    if len(members) <= 5:
        await callback.answer("❖ ✖️ Некого кикать")
        return
    # берем участников с 6 по 11
    member_names = []
    for uid in members:
        user = await mongodb.get_user(uid)
        if uid == clan["leader_id"]:
            member_names.append(f" • 👑 {user['name']} (Лидер)")
        else:
            member_names.append(f" • 🪪 {user['name']}")
    if not members:
        await callback.answer("❖ ✖️ Некого кикать")
        return
    clean_names = []

    for line in member_names:
        match = re.search(r"<b>(.*?)</b>", line)
        if match:
            clean_names.append(match.group(1))  # Взяли только текст из <b>Имя</b>
        else:
            clean_names.append(line)
    buttons = [f"{uid}" for uid in clean_names[5:11]]
    callbacks = [f"kick_{uid}" for uid in members[5:11]]
    buttons += ["⬅️", "🔙 Назад"]
    callbacks += ["prev_kick", "clan"]

    await callback.message.edit_reply_markup(reply_markup=inline_builder(buttons, callbacks, row_width=[1]))


@router.callback_query(F.data == "prev_kick")
async def prev_kick(callback: CallbackQuery):
    # показываем участников с 0 по 5
    user_id = callback.from_user.id
    clan_name = (await mongodb.get_user(user_id)).get("clan")
    clan = await mongodb.db.clans.find_one({"_id": clan_name})
    members = [uid for uid in clan["members"] if uid != user_id]
    if len(members) <= 5:
        await callback.answer("❖ ✖️ Некого кикать")
        return
    # берем участников с 0 по 5
    member_names = []
    for uid in members:
        user = await mongodb.get_user(uid)
        if uid == clan["leader_id"]:
            member_names.append(f" • 👑 {user['name']} (Лидер)")
        else:
            member_names.append(f" • 🪪 {user['name']}")
    if not members:
        await callback.answer("❖ ✖️ Некого кикать")
        return
    clean_names = []

    for line in member_names:
        match = re.search(r"<b>(.*?)</b>", line)
        if match:
            clean_names.append(match.group(1))  # Взяли только текст из <b>Имя</b>
        else:
            clean_names.append(line)
    # берем первых 5 участников
    buttons = [f"{uid}" for uid in clean_names[:5]]
    callbacks = [f"kick_{uid}" for uid in members[:5]]
    if len(members) > 5:
        buttons += ["➡️", "🔙 Назад"]
        callbacks += ["next_kick", "clan"]
    else:
        buttons += ["🔙 Назад"]
        callbacks += ["clan"]

    await callback.message.edit_reply_markup(reply_markup=inline_builder(buttons, callbacks, row_width=[1]))


@router.callback_query(F.data.startswith("kick_"))
async def kick_member(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    target_id = int(callback.data.split("_")[-1])
    clan_name = (await mongodb.get_user(user_id)).get("clan")
    clan = await mongodb.db.clans.find_one({"_id": clan_name})

    if target_id == user_id:
        await callback.answer("❖ ✖️ Вы не можете кикнуть себя", show_alert=True)
        return
    if target_id not in clan["members"]:
        await callback.answer("❖ ✖️ Участник уже покинул клан", show_alert=True)
        return

    await mongodb.db.clans.update_one({"_id": clan_name}, {"$pull": {"members": target_id}})
    await mongodb.update_user(target_id, {"clan": ''})
    await bot.send_message(chat_id=target_id, text=f"❖ ✖️ Вы были исключены из клана {clan_name}")
    await callback.answer("❖ ✅ Участник исключен", show_alert=True)


@router.callback_query(F.data == "clan_leave")
async def leave_clan(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    user = await mongodb.get_user(user_id)
    name = user["name"]
    clan_name = user.get("clan")
    clan = await mongodb.db.clans.find_one({"_id": clan_name})

    if not clan:
        await callback.answer("❖ ✖️ Клан не найден")
        return

    await mongodb.update_user(user_id, {"clan": ""})
    await mongodb.db.clans.update_one({"_id": clan_name}, {"$pull": {"members": user_id}})

    if clan["leader_id"] == user_id:
        remaining = clan["members"]
        if not remaining:
            await mongodb.db.clans.delete_one({"_id": clan_name})
            await callback.message.answer("❖ 👑 Вы покинули клан. Клан был распущен")
        else:
            new_leader = remaining[0]
            await mongodb.db.clans.update_one({"_id": clan_name}, {"$set": {"leader_id": new_leader}})
            await callback.message.answer(f"❖ 👑 Вы покинули клан. Лидерство передано участнику {new_leader}")
            await bot.send_message(new_leader, f"👑 Вы стали новым лидером клана {clan_name}")
    else:
        await callback.message.answer("❖ ✅ Вы покинули клан", show_alert=True)
        # уведомление лидеру и участникам
        await bot.send_message(clan["leader_id"], f"❖ ➖ {name} покинул клан")
        await callback.message.delete()


@router.callback_query(F.data == "clan_shop")
async def clan_shop(callback: CallbackQuery):
    user_id = callback.from_user.id
    account = await mongodb.get_user(user_id)

    ticket_data = account['inventory']['items']['tickets']
    golden = ticket_data['golden']
    common = ticket_data['common']

    if 'clan_coins' not in account['account']:
        await mongodb.update_user(user_id, {"account.clan_coins": 0})
        account = await mongodb.get_user(user_id)

    if 'boss_keys' not in account['account']:
        await mongodb.update_user(user_id, {"account.boss_keys": 0})
        account = await mongodb.get_user(user_id)

    coins = account['account']['clan_coins']
    keys = account['account']['boss_keys']
    pattern = dict(
        caption=f"❖  ⛺️ <b> Лавка</b>"
                f"\n── •✧✧• ────────"
                f"\n❖  Вы можете купить 🎫 золотые, 🎟 обычные билеты за 🪙 монетки клана"
                f"\n ❃ ⚖️ Цены за предметы:"
                f"\n  •  🗝 = 15 🪙"
                f"\n  •  🎫 = 10 🪙"
                f"\n  •  🎟 = 1 🪙"
                # f"\n── •✧✧• ────────"
                "\n➖➖➖➖➖➖➖➖➖➖"
                f"\n🪙⋗ <b>{coins}</b> 🗝⋗ <b>{keys}</b> 🎫⋗ <b>{golden}</b> 🎟⋗ <b>{common}</b>",
        reply_markup=inline_builder(
            ["🗝 Купить", "🎫 Купить", "🎟 Купить", "🔙 Назад"],
            ["buy_boss_keys", "buy_golden_clan", "buy_common_clan", "clan"],
            row_width=[1, 2, 1]
            )
    )

    media_id = "AgACAgIAAx0CfstymgACP5doE0gyCfK2CcVmKMvfh8l7mCkcNAAC0vQxG-82mEjnVLaNNbOfRQEAAwIAA3kAAzYE"
    # "CgACAgIAAxkBAAIVAmXMvH4t4RtOQzePYbQgdnNEbFEeAAKOOwACeyZoSiAP4_7nfuBVNAQ"
    media = InputMediaPhoto(media=media_id)
    if isinstance(callback, CallbackQuery):
        inline_id = callback.inline_message_id
        await callback.message.edit_media(media, inline_id)
        await callback.message.edit_caption(inline_id, **pattern)
    else:
        await callback.answer_animation(media_id, **pattern)


@router.callback_query(F.data == "buy_boss_keys")
async def buy_boss_keys(callback: CallbackQuery):
    inline_id = callback.inline_message_id
    user_id = callback.from_user.id
    account = await mongodb.get_user(user_id)

    pattern = dict(
        caption=f"❖ 🗝 <b>Купить ключи</b>"
                f"\n── •✧✧• ────────"
                f"\n • Сколько 🗝 ключей вы хотите купить?",
        reply_markup=inline_builder(
            ["1🗝 • 15🪙", "5🗝 • 75🪙", "🔙 Назад"],
            ["buy_boss_keys_1_c", "buy_boss_keys_5_c", "clan_shop"],
            row_width=[2, 1]
            )
    )

    await callback.message.edit_caption(inline_id, **pattern)


@router.callback_query(F.data == "buy_boss_keys_1_c")
async def buy_boss_keys_1(callback: CallbackQuery):
    await buy_boss_keys_clan(callback, 1)


@router.callback_query(F.data == "buy_boss_keys_5_c")
async def buy_boss_keys_5(callback: CallbackQuery):
    await buy_boss_keys_clan(callback, 5)


@router.callback_query(F.data == "buy_common_clan")
async def buy_common(callback: CallbackQuery):
    inline_id = callback.inline_message_id
    user_id = callback.from_user.id
    account = await mongodb.get_user(user_id)

    pattern = dict(
        caption=f"❖ 🎟 <b>Купить обычные билеты</b>"
                f"\n── •✧✧• ────────"
                f"\n • Сколько 🎟 билетов вы хотите купить?",
        reply_markup=inline_builder(
            ["1🎟 • 1🪙", "5🎟 • 5🪙", "🔙 Назад"],
            ["buy_common_1_c", "buy_common_5_c", "clan_shop"],
            row_width=[2, 1]
            )
    )

    await callback.message.edit_caption(inline_id, **pattern)


@router.callback_query(F.data == "buy_common_1_c")
async def buy_common_1(callback: CallbackQuery):
    await buy_common_ticket_clan(callback, 1)


@router.callback_query(F.data == "buy_common_5_c")
async def buy_common_5(callback: CallbackQuery):
    await buy_common_ticket_clan(callback, 5)


async def buy_common_ticket_clan(callback: CallbackQuery, count: int):
    user_id = callback.from_user.id
    account = await mongodb.get_user(user_id)

    coins = account['account']['clan_coins']
    if coins >= 1 * count:
        await mongodb.update_user(user_id, {'account.money': coins - 1 * count})
        await mongodb.update_user(
            user_id, {'inventory.items.tickets.common': account['inventory']['items']['tickets']['common'] + count}
        )
        current_date = datetime.today().date()
        current_datetime = datetime.combine(current_date, datetime.time(datetime.now()))
        await mongodb.update_user(user_id, {"tasks.last_shop_purchase": current_datetime})
        await callback.answer(f"❖  ⛺️  Вы успешно приобрели {count} 🎟 обычных билетов", show_alert=True)
    else:
        await callback.answer(f"❖  ⛺️  У вас недостаточно 🪙 монетки клана", show_alert=True)
    await clan_shop(callback)


async def buy_boss_keys_clan(callback: CallbackQuery, count: int):
    user_id = callback.from_user.id
    account = await mongodb.get_user(user_id)

    coins = account['account']['clan_coins']
    if coins >= 15 * count:
        await mongodb.update_user(user_id, {'account.money': coins - 15 * count})
        await mongodb.update_user(
            user_id, {'inventory.items.keys': account['inventory']['items']['keys'] + count}
        )
        current_date = datetime.today().date()
        current_datetime = datetime.combine(current_date, datetime.time(datetime.now()))
        await mongodb.update_user(user_id, {"tasks.last_shop_purchase": current_datetime})
        await callback.answer(f"❖  ⛺️  Вы успешно приобрели {count} 🗝 ключей", show_alert=True)
    else:
        await callback.answer(f"❖  ⛺️  У вас недостаточно 🪙 монетки клана", show_alert=True)
    await clan_shop(callback)


@router.callback_query(F.data == "buy_golden_clan")
async def buy_golden(callback: CallbackQuery):
    inline_id = callback.inline_message_id
    user_id = callback.from_user.id
    account = await mongodb.get_user(user_id)
    pattern = dict(
        caption=f"❖ 🎫 <b>Купить золотые билеты</b>"
                f"\n── •✧✧• ────────"
                f"\n • Сколько билетов вы хотите купить?",
        reply_markup=inline_builder(
            ["1🎫 • 10🪙", "5🎫 • 50🪙", "🔙 Назад"],
            ["buy_golden_1_c", "buy_golden_5_с", "clan_shop"],
            row_width=[2, 1]
            )
    )

    await callback.message.edit_caption(inline_id, **pattern)


@router.callback_query(F.data == "buy_golden_1_c")
async def buy_golden_1(callback: CallbackQuery):
    await buy_golden_ticket_clan(callback, 1)


@router.callback_query(F.data == "buy_golden_5_c")
async def buy_golden_5(callback: CallbackQuery):
    await buy_golden_ticket_clan(callback, 5)


async def buy_golden_ticket_clan(callback: CallbackQuery, count: int):
    user_id = callback.from_user.id
    account = await mongodb.get_user(user_id)

    coins = account['account']['clan_coins']
    if coins >= 10 * count:
        await mongodb.update_user(user_id, {'account.money': coins - 10 * count})
        await mongodb.update_user(
            user_id, {'inventory.items.tickets.golden': account['inventory']['items']['tickets']['golden'] + count}
        )
        current_date = datetime.today().date()
        current_datetime = datetime.combine(current_date, datetime.time(datetime.now()))
        await mongodb.update_user(user_id, {"tasks.last_shop_purchase": current_datetime})
        await callback.answer(f"❖  ⛺️  Вы успешно приобрели {count} 🎫 золотых билетов", show_alert=True)
    else:
        await callback.answer(f"❖  ⛺️  У вас недостаточно 🪙 монетки клана", show_alert=True)
    await clan_shop(callback)
