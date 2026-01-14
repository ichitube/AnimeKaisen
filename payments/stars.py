from aiogram import Router, F

from aiogram.types import CallbackQuery, LabeledPrice, PreCheckoutQuery, Message
router = Router()

@router.message(F.text.lower().in_(['донат', 'купить билет', 'купить билеты']))
@router.callback_query(F.data == "buy_keys")
async def buy_keys(message: Message | CallbackQuery):
    if isinstance(message, CallbackQuery):
        await message.message.answer_invoice(
            title="🌟 Покупка билет 🧧",
            description="❖ 🧧 Священный билет имеет высокий шанс выпадения редких персонажей",
                        # "\n\n\n\n • Цена: 25 🌟",
            payload="buy_ticket",
            currency="XTR",
            prices=[LabeledPrice(label="XTR", amount=25)],
        )
    else:
        await message.answer_invoice(
            title="🌟 Покупка билет 🧧",
            description="❖ 🧧 Священный билет имеет высокий шанс выпадения редких персонажей",
                       # f"\n\n • Цена: 25 🌟",
            payload="buy_ticket",
            currency="XTR",
            prices=[LabeledPrice(label="XTR", amount=25)]
        )


@router.message(F.text.lower().in_(['купить', 'пасс', 'пас', 'купить пасс', 'pass', 'pas']))
@router.callback_query(F.data == "buy_pass")
async def buy_pass(message: Message | CallbackQuery):
    if isinstance(message, CallbackQuery):
        await message.message.answer_invoice(
            title="🌟 Покупка 💮Pass",
            description="❖ 💮Pass даёт вам доступ к уникальным возможностям и удвоенным наградам",
                        # "\n\n\n\n • Цена: 150 🌟",
            payload="buy_pass",
            currency="XTR",
            prices=[LabeledPrice(label="XTR", amount=150)],
        )
    else:
        await message.answer_invoice(
            title="🌟 Покупка 💮Pass",
            description="❖ 💮Pass даёт вам доступ к уникальным возможностям и удвоенным наградам",
                       # f"\n\n • Цена: 150 🌟",
            payload="buy_pass",
            currency="XTR",
            prices=[LabeledPrice(label="XTR", amount=150)]
        )


@router.pre_checkout_query()
async def process_pre_checkout_query(event: PreCheckoutQuery):
    await event.answer(ok=True)


@router.message(F.text.lower().in_(['донат', 'купить билет', 'купить билеты']))
@router.callback_query(F.data == "buy_keys")
async def buy_keys(message: Message | CallbackQuery):
    if isinstance(message, CallbackQuery):
        await message.message.answer_invoice(
            title="🌟 Покупка билет 🧧",
            description="❖ 🧧 Священный билет имеет высокий шанс выпадения редких персонажей",
                        # "\n\n\n\n • Цена: 25 🌟",
            payload="buy_ticket",
            currency="XTR",
            prices=[LabeledPrice(label="XTR", amount=25)],
        )
    else:
        await message.answer_invoice(
            title="🌟 Покупка билет 🧧",
            description="❖ 🧧 Священный билет имеет высокий шанс выпадения редких персонажей",
                       # f"\n\n • Цена: 25 🌟",
            payload="buy_ticket",
            currency="XTR",
            prices=[LabeledPrice(label="XTR", amount=25)]
        )


@router.message(F.text.lower().in_(['купить', 'пасс', 'пас', 'купить пасс', 'pass', 'pas']))
@router.callback_query(F.data == "buy_pass")
async def buy_pass(message: Message | CallbackQuery):
    if isinstance(message, CallbackQuery):
        await message.message.answer_invoice(
            title="🌟 Покупка 💮Pass",
            description="❖ 💮Pass даёт вам доступ к уникальным возможностям и удвоенным наградам",
                        # "\n\n\n\n • Цена: 150 🌟",
            payload="buy_pass",
            currency="XTR",
            prices=[LabeledPrice(label="XTR", amount=150)],
        )
    else:
        await message.answer_invoice(
            title="🌟 Покупка 💮Pass",
            description="❖ 💮Pass даёт вам доступ к уникальным возможностям и удвоенным наградам",
                       # f"\n\n • Цена: 150 🌟",
            payload="buy_pass",
            currency="XTR",
            prices=[LabeledPrice(label="XTR", amount=150)]
        )


@router.pre_checkout_query()
async def process_pre_checkout_query(event: PreCheckoutQuery):
    await event.answer(ok=True)
