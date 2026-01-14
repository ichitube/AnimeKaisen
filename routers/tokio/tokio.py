import random

from aiogram import Router, F

from aiogram.types import CallbackQuery, InputMediaAnimation, Message
from aiogram.enums import ParseMode

from keyboards.builders import inline_builder
from data import mongodb
from filters.chat_type import ChatTypeFilter


router = Router()

menu = ["CgACAgIAAxkBAAIVCWXMvbya7qFOU8F85SXUu24hM5wgAAKfOwACeyZoShH4z6iUPi8kNAQ",
        "CgACAgIAAxkBAAIVCGXMva_F1yC11Mw3o1gv27ZgOmICAAKdOwACeyZoSqKFTee3GFhiNAQ",
        "CgACAgIAAxkBAAIVBmXMvQTWWfC3KX66Wy4evn7cWtHuAAKUOwACeyZoSsragGfIS2gINAQ",
        "CgACAgIAAxkBAAIVAWXMvHhsXaPhuLALMBuumsH-TO4dAAKNOwACeyZoSjQXaqlcQ_ZPNAQ",
        "CgACAgIAAxkBAAIU_mXMvCAB6-_wn8o6hpUwwaR-EF6IAAJ4RQACzLBpSgF57_JwVq60NAQ",
        "CgACAgIAAxkBAAIVAAFlzLxX7B3NqbKxkBbz_SAosLc8eQACjDsAAnsmaEo-TETgyUqmcjQE",
        "CgACAgIAAxkBAAIU_2XMvDvTFeOYOdwd5QRQsPUdhGPlAAKKOwACeyZoSpr5AQNXbnVENAQ",
        "CgACAgIAAxkBAAIU_WXMvB2fCF7pcS9cZDdEMNeeWIe2AAKFOwACeyZoSqkPzi4qGFdvNAQ",
        "CgACAgIAAxkBAAIU-GXMuu17Zb88QyTyVxOEwPFjeCRJAAJoOwACeyZoSp9AqDTjvy4lNAQ",
        "CgACAgIAAxkBAAIU-WXMuv67-KrxO8NKeQgUw4LsrDSSAAJqOwACeyZoSvtrR6TF1C2BNAQ",
        "CgACAgIAAxkBAAIVA2XMyQ7c7bzjIhd4ecf9W6TGWm6eAAKPOwACeyZoSsm5IEXYiJoKNAQ",
        "CgACAgIAAx0CfstymgACBd5lzO0zU05NJEIDdrzbQNLwSMi_XgACbUkAAsywaUqtbVk4cEzxrzQE",
        "CgACAgIAAx0CfstymgACBd1lzO0zAm8ov_iX9BAY7_QVIkf3NQACbEkAAsywaUoWn4BRgx1huTQE",
        "CgACAgIAAx0CfstymgACBdxlzO0yxbOLTRm_B0ttpbA7WYEFdgACa0kAAsywaUoVOJ0ILUcy3jQE",
        "CgACAgIAAx0CfstymgACIB5nE7mXOOMrHrWyLobEDbk85ehs7QAC6FgAAqiJoEg5NN5yufK0QzYE",
        "CgACAgIAAx0CfstymgACIBRnE7ipKamfva-CfgqsiZJ-EKMGxwACxFgAAqiJoEijvBsGD_fnpjYE",
        "CgACAgIAAx0CfstymgACIBJnE7ih9KNvH8o3P1Yy1rTY4o7YVQACwlgAAqiJoEiVpQSxmKi5sjYE",
        "CgACAgIAAx0CfstymgACIBBnE7ibsUe_hxrML0hwjTHC0jWZXQACwVgAAqiJoEhlPEBRZo_wlTYE",
        "CgACAgIAAx0CfstymgACIA5nE7iRTMe8cH8bBZgvI8ZbeAW0tAACv1gAAqiJoEi3kcjjLHSleDYE",
        "CgACAgIAAx0CfstymgACIAxnE7iJXL7xxL4a5vmYVhL3zTuYZwACvVgAAqiJoEgvOYe5dmhxFjYE",
        "CgACAgIAAx0CfstymgACIApnE7h9jBb9jkmJNh_KJ792kiapEAACu1gAAqiJoEjYTH71QJA-TjYE",
        "CgACAgIAAx0CfstymgACPWxnWiFG_Ozd_Bzji7nT0z-L_ARZXwACQWcAAvbt0Eotj1TRX6hROzYE",
        "CgACAgIAAx0CfstymgACPWpnWiFBKsoORGJWrPqbc0pYaOCJuQACQGcAAvbt0EpTkQsS84ej2TYE",
        "CgACAgIAAx0CfstymgACPWhnWiE2nNi6fRKFBoBXLch59Lm8TQACP2cAAvbt0EqaFIv-hxthITYE",
        "CgACAgIAAx0CfstymgACPWZnWiEd21kg7iZR5J90NSyUbaCmTgACPmcAAvbt0EpO8Nts7VfWyzYE",
        "CgACAgIAAx0CfstymgACPWRnWiD_BXM_xIf-m9Ow90yOnXfk3AACPWcAAvbt0ErlcZtAXNwlmDYE",
        "CgACAgIAAx0CfstymgACPWJnWiD0YmwQeePBQAZH2ovucj9wTQACPGcAAvbt0Eq_pNJLTLhWbzYE",
        "CgACAgIAAx0CfstymgACPWBnWiDro44e852CA6p1feMaEXj4RgACO2cAAvbt0EpBlZu2nfHgCzYE",
        "CgACAgIAAx0CfstymgACPV5nWiDeZjEomft3rYZcQDPytxg0_AACOmcAAvbt0EpOoiM0UTRHbDYE",
        "CgACAgIAAx0CfstymgACPUxnWiCIq87zNe39KMnI8-JNZtx1EwACMWcAAvbt0Epxs4C1GbPvKDYE",
        "CgACAgIAAx0CfstymgACPUpnWiB-NbaKrUwQ22XLu6vouMnJLAACL2cAAvbt0EriVWom9jD8YzYE",
        "CgACAgIAAx0CfstymgACPUhnWiB2zkpEDVGHHXI0LcJB0f3sigACLmcAAvbt0EoKxaZJcjFRzjYE",
        "CgACAgIAAx0CfstymgACPUZnWiBvTqtKwcpRBEAs2zPU6lq35QACLWcAAvbt0ErS50ZnIQgGFDYE",
        "CgACAgIAAx0CfstymgACPURnWiBpJUOx3egkYiNGig0bBIG49gACLGcAAvbt0ErohJICkiFXZTYE",
        "CgACAgIAAx0CfstymgACPUJnWiBZ8O38ba77vuFjMv8E02u7EwACK2cAAvbt0EqV6eyIs0E97zYE",
        "CgACAgIAAx0CfstymgACPUBnWiBPDPiSbtOh-T4ayoELgHGjIgACKmcAAvbt0EoJn6AWWGQxvTYE",
        "CgACAgIAAx0CfstymgACPT5nWiBCuN2Ho9onD5Ke63vQaPPjAQACKWcAAvbt0EpibjUOCvoGoDYE",
        "CgACAgIAAx0CfstymgACPTxnWiA6Jtv1xQ4jL3paAxcrrLPCdAACKGcAAvbt0Er3UO37vyDa5DYE",
        "CgACAgIAAx0CfstymgACPThnWiAmKGNBTzAXNNzM9DGD-DktyQACJmcAAvbt0Eo3tEKgNGF6-jYE",
        "CgACAgIAAx0CfstymgACPTZnWiAgQQs-N5EXbi1ieI9_i-KNbAACJWcAAvbt0Eo1qzujjm2IhjYE",
        "CgACAgIAAx0CfstymgACPTRnWiAbQeTOtBXeYqwn8_Wf3q-SxAACJGcAAvbt0ErKbpuEIuLQFzYE",
        "CgACAgIAAx0CfstymgACPSxnWh_pEIY22PoMRKtpTzp9HpBnMwACHWcAAvbt0EoAAQqwL0u9W4E2BA",
        "CgACAgIAAx0CfstymgACPSpnWh_bemTyeoohqmYZ_QFbRWe19QACHGcAAvbt0Er7bXBZpVUYEzYE",
        "CgACAgIAAx0CfstymgACPShnWh_STTrjZMHdujkXJ6oBH3TjkwACG2cAAvbt0ErnZ7uphAoFAAE2BA",
        "CgACAgIAAx0CfstymgACPSZnWh_Ki1NKworFqK9Afyha07fi3gACGmcAAvbt0EpnMJP9_PIdejYE",
        "CgACAgIAAx0CfstymgACPSRnWh_CYcOY2uxNrMnKeWv_6pXLUwACGWcAAvbt0Eox88h6ojD9DzYE",
        "CgACAgIAAx0CfstymgACPSJnWh-50rl67kXUSacccBosqX5_uAACGGcAAvbt0EpKv37i-gs8-jYE",
        "CgACAgIAAx0CfstymgACPSBnWh-w0HelUkGar6Vo4ryi2bmJHAACF2cAAvbt0EqucbkeYCP17TYE",
        "CgACAgIAAx0CfstymgACPR5nWh-gNJ7dFK1QTWjjrnXObIsMJwACFmcAAvbt0ErqSJLs8LBagTYE",
        "CgACAgIAAx0CfstymgACPRxnWh-VQDXlFrnvivfkY7cSNcSODQACFWcAAvbt0Eq_tl1KFXCi6TYE",
        "CgACAgIAAx0CfstymgACPRpnWh-Kn8M5V2wj1wAB07y_hW-hK4cAAhRnAAL27dBKNjyombw9a6o2BA",
        "CgACAgIAAx0CfstymgACPRhnWh-FRtSw6tO5Ft_C-QI824MMOQACE2cAAvbt0ErPoP801LqqwjYE",
        "CgACAgIAAx0CfstymgACPRZnWh9ujJDSxsW_aDmZLIhuMm3TAgACEWcAAvbt0EqXAzhsApsQNzYE",
        "CgACAgIAAx0CfstymgACPRRnWh9MZ8FXoClQoSCiEU8YRIIkNQACEGcAAvbt0Eq60nsfGdiGZzYE",
        "CgACAgIAAx0CfstymgACPRJnWh857hPoKWmZTcNwhFmCC7UEkwACD2cAAvbt0EpSfauk6fjrnDYE",
        "CgACAgIAAx0CfstymgACPQZnWh7rxf8BZaBSb1i4WdvCK6qTBAACBGcAAvbt0ErLzslLhn7R-DYE",
        "CgACAgIAAx0CfstymgACPPxnWh60G7fTkb9wp3MNVAnWm12CfQAC_WYAAvbt0EqqNLLhgcDqvzYE",
        "CgACAgIAAx0CfstymgACPPhnWh6Q_MWi4JYqLpQOMwtgXF7zCQAC-2YAAvbt0Eq8LwypWVJerjYE",
        "CgACAgIAAx0CfstymgACPPZnWh6H5gUUYNcOzZ8oumMC1JOUuAAC-mYAAvbt0Eo1PKd9BtAMqTYE",
        "CgACAgIAAx0CfstymgACPPRnWh6Dt0fHyC_yg0sYb71OHEkFbAAC-WYAAvbt0ErNHpUYMOvB7zYE",
        "CgACAgIAAx0CfstymgACPO5nWh5jFnCnaWGBCJW0slqasmxTUwAC9mYAAvbt0Epgn0leBeRc5DYE",
        "CgACAgIAAx0CfstymgACPOhnWh5OfXgafyd6Qz4f1ua8L9wQEQAC82YAAvbt0Eq6BCEtaoGO_TYE",
        "CgACAgIAAx0CfstymgACPNlnWh2Qso0ejPBx4Tm0siLjaLkn5gAC6WYAAvbt0EoYmNiXYP344TYE",
        "CgACAgIAAx0CfstymgACPNdnWh2AtS54L6E_7LRRnEMZwTIBQAAC6GYAAvbt0EpftyRKzk2sNjYE",
        "CgACAgIAAx0CfstymgACPM1nWh0wpYaRG3vUYhUAAVQydk9CmegAAuJmAAL27dBKou_bFw0e-Ng2BA",
        "CgACAgIAAx0CfstymgACIAxnE7iJXL7xxL4a5vmYVhL3zTuYZwACvVgAAqiJoEgvOYe5dmhxFjYE",
        "CgACAgIAAx0CfstymgACIA5nE7iRTMe8cH8bBZgvI8ZbeAW0tAACv1gAAqiJoEi3kcjjLHSleDYE",
        "CgACAgIAAx0CfstymgACIBBnE7ibsUe_hxrML0hwjTHC0jWZXQACwVgAAqiJoEhlPEBRZo_wlTYE",
        "CgACAgIAAx0CfstymgACIBJnE7ih9KNvH8o3P1Yy1rTY4o7YVQACwlgAAqiJoEiVpQSxmKi5sjYE",
        "CgACAgIAAx0CfstymgACIBRnE7ipKamfva-CfgqsiZJ-EKMGxwACxFgAAqiJoEijvBsGD_fnpjYE",
        "CgACAgIAAx0CfstymgACBdtlzO0rWNF9QoR6R4_5ZaHZDVb37wACakkAAsywaUpFT0CPnQYM5TQE",
        "CgACAgIAAx0CfstymgACIAhnE7hfoRhlTEwMXl0Olo7O0N33hQACuFgAAqiJoEirg1wj-bItjTYE",
        ]


@router.message(
    ChatTypeFilter(chat_type=["private"]),
    F.text == "〽️ Меню"
)
@router.callback_query(F.data == "tokio")
async def tokio(callback: CallbackQuery | Message):
    user_id = callback.from_user.id
    account = await mongodb.get_user(user_id)

    money = account['account']['money']
    if account["universe"] == "Allstars":
        area = "🃏 Битва"
        area_cb = "arena"
    else:
        area = "🏟️ Арена"
        area_cb = "arena"
    power = account['campaign']['power']
    top_text = await mongodb.get_top10_text()
    pattern = dict(
        caption=f"𓂃 ࣪˖ ִֶཐི༏ཋྀ󠀮 〽️  <b>Меню</b> ᓚᘏᗢ"
                f"\n── •✧✧• ──────────"
                f"\n🌊 Добро пожаловать в мир карт"
                "\n<blockquote>🏟️ Захватывающие битвы!"
                "\n🎴 Собирай персонажей "
                "\n⚔️ Сражайся с противниками"
                "\n🔥 Навыки из аниме в боях"
                "\n♟ Придумай свою стратегию"
                "\n🌟 Зарабатывай Telegram Stars"
                "\n🐦‍🔥 Уничтожай боссов с 🎌 кланом"
                "\n💬 Вступай в сообщество </blockquote>"
                "\n➖➖➖➖➖➖➖➖➖➖➖"
                f"\n❁ 💴 {money} ¥ ", # ❁ ⚜️ Мощь: {power}",
        parse_mode=ParseMode.HTML,
        reply_markup=inline_builder(
            [area, "🪪 Профиль", "🏯 Клан 🎌", " 🐦‍🔥Босс", "⛩️ Подземелье", "🏮 Рынок", "🏠 Дом"],
            [area_cb, "main_page", "clan", "boss", "dungeon", "store", "home"],
            row_width=[1, 2, 2, 2]
            )
    )

    media_id = random.choice(menu)

    if isinstance(callback, CallbackQuery):
        inline_id = callback.inline_message_id
        media = InputMediaAnimation(media=media_id)

        await callback.message.edit_media(media, inline_id)
        await callback.message.edit_caption(inline_id, **pattern)
    else:
        await callback.answer_animation(media_id, **pattern)


homes_photo = {'🏠 home_1': 'CgACAgIAAxkBAAIU-2XMuzNmOsXp4JxBcGGDbpD_XENiAAJwOwACeyZoSsgIg-cm-c8iNAQ',
               '🏠 home_2': 'CgACAgIAAxkBAAIU_GXMuza-voX5wQABXHuYInkx0vGpQwACcTsAAnsmaEr83Z9UehDa5jQE',
               '🏠 home_3': 'CgACAgIAAxkBAAIU-mXMuxgz2RBDeRa8TE0AAaSXD_mKSAACbDsAAnsmaEqm72YZnRGekjQE',
               '🏠 home_4': 'CgACAgIAAx0CfstymgACBSZlxMJQZb7FFLh9iPFdSpXOklwDqQACaD4AAgrXEEpTmie8hGfs1zQE',
               '🏠 home_5': 'CgACAgIAAx0CfstymgACBdtlzO0rWNF9QoR6R4_5ZaHZDVb37wACakkAAsywaUpFT0CPnQYM5TQE'
               }
