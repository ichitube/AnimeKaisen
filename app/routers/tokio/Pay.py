from aiogram import Router, F

from aiogram.types import CallbackQuery
from aiogram.enums import ParseMode

from app.keyboards.builders import inline_builder
from app.data import mongodb
from .store import store
from .crystalpay_sdk import CrystalPAY, InvoiceType

crystalpayAPI = CrystalPAY("direbilling", "3fd18bf80390f19f80679409d4a3ae8e8ea14048",
                           "d06aee367b2b5053c1f064cc48798a73a1adefa7")

router = Router()

tasks = {}



# @router.callback_query(F.data == "buy_keys")
# async def buy_keys(callback: CallbackQuery):
#     await callback.message.delete()
#
#     billing = crystalpayAPI.Invoice.create(100, InvoiceType.purchase, 15)
#     billing_id = billing['id']
#     tasks[callback.from_user.id] = billing_id
#     pattern = dict(caption=f"\n── •✧✧• ──────────"
#                            f"\n❖  💮 Если вы из следющих стран:\n🇺🇸 $  🇺🇦 ₴  🇰🇿 ₸ (или другие страны) оплатите через "
#                            f"  <b>💳 Paysend</b>"
#                            f"\n── •✧✧• ──────────"
#                            f"\n❖  💮 Если вы из РФ 🇷🇺 ₽ оплатите через <b>💎 CrystalPay либо</b> "
#                            f"свяжитесь с\n<a href='https://t.me/falcon_blackhawk'><b>👤 Админом</b></a> и купите лично."
#                            f"\n── •✧✧• ──────────",
#                    parse_mode=ParseMode.HTML,
#                    reply_markup=inline_builder(["💳 Paysend", "💎 CrystalPay", "✖️ Отмена"],
#                                                ["paysend", "buy_crypt", "store"], row_width=[2, 1])
#                    )
#
#     media_id = "CgACAgIAAx0CfstymgACBQVluXo_n-FnFfBB1XW8zCIU7_Ed0QAC6TsAAtfz0Enh8jW0yBuKgzQE"
#
#     await callback.message.answer_animation(animation=media_id, **pattern)
#
#
# @router.callback_query(F.data == "paysend")
# async def buy_keys(callback: CallbackQuery):
#     inline_id = callback.inline_message_id
#     pattern = dict(caption=f"❖  💳 Для оплаты через Paysend:"
#                            f"\n── •✧✧• ──────────"
#                            f"\n 1. <a href='https://paysend.com/login?from_page=send'>"
#                            f"<b>Перейдите в Paysend</b></a>\n 2. Переведите 🇺🇸 1$ = 🇺🇦 35₴ = 🇰🇿 390₸ \n "
#                            f"3. Отправьте <a href='https://t.me/falcon_blackhawk'><b>👤 Админу</b></a> скриншот с "
#                            f"\n🧾 чеком и id: "
#                            f"<a href='tg://user?id={callback.from_user.id}'>{callback.from_user.id}</a>",
#                    parse_mode=ParseMode.HTML,
#                    reply_markup=inline_builder(["✖️ Отмена"], ["buy_keys"], row_width=[1])
#                    )
#
#     await callback.message.edit_caption(inline_id, **pattern)
#
#
# @router.callback_query(F.data == "buy_crypt")
# async def buy_keys(callback: CallbackQuery):
#     inline_id = callback.inline_message_id
#
#     billing = crystalpayAPI.Invoice.create(100, InvoiceType.purchase, 15)
#     billing_id = billing['id']
#     tasks[callback.from_user.id] = billing_id
#     pattern = dict(caption=f"\n── •✧✧• ──────────"
#                    f"\n❖  🪙 Для оплаты <a href='{billing['url']}'><b> перейдите сюда</b></a>",
#                    parse_mode=ParseMode.HTML,
#                    reply_markup=inline_builder(["✔️ Оплатил", "✖️ Отмена"], ["check", "buy_keys"], row_width=[1])
#                    )
#
#     await callback.message.edit_caption(inline_id, **pattern)
#
#
# @router.callback_query(F.data == "check")
# async def buy_keys(callback: CallbackQuery):
#     billing_id = tasks[callback.from_user.id]
#     billing = crystalpayAPI.Invoice.getinfo(billing_id)
#     if billing['state'] == 'notpayed':
#         await callback.answer("❖  💎 Вы ещё не оплатили", show_alert=True)
#     else:
#         await callback.answer("❖  💎 Вы успешно приобрели 🧧 священный билет", show_alert=True)
#         tasks.pop(callback.from_user.id)
#         await mongodb.update_value(callback.from_user.id, {'inventory.items.tickets.keys': 1})
#         await store(callback)
