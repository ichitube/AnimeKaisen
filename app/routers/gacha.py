import asyncio
import random
from datetime import datetime, timedelta

from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.types import InputMediaAnimation, InputMediaPhoto, Message
from app.data import mongodb, character_photo
from app.keyboards.builders import inline_builder, start_button, menu_button, success, Ability, channel_check

CHANNEL_LINK = "https://t.me/multiverse_card"


async def check_user_subscription(user_id: int, bot):
    member = await bot.get_chat_member(chat_id='@multiverse_card', user_id=user_id)

    # Проверяем статус пользователя
    if member.status in ["member", "administrator", "creator"]:
        return True
    return False

router = Router()

characters = {
    "Bleach": {
        "divine": [
            "Toshiro Hitsuyaga 🌠",
            "Toshiro Hitsuyaga 🌠 ㊀",
            "Ulquiorra Cifer 🌠",
            "Urahara Kisuke 🌠",
            "Unohana Retsu 🌠",
            "Aizen Sosuke 🌠",
            "Aizen Sosuke 🌠 ㊀",
            "Aizen Sosuke 🌠 ㊁",
            "Aizen Sosuke 🌠 ㊂",
            "Ichigo Kurosaki 🌠",
            "Ichigo Kurosaki 🌠 ㊀",
            "Ichigo Kurosaki 🌠 ㊁",
            "Ichigo Kurosaki 🌠 ㊂",
            "Ichigo Kurosaki 🌠 ㊃",
            "Rukia Kuchiki 🌠",
            "Rukia Kuchiki 🌠 ㊀",
            "Rukia Kuchiki 🌠 ㊁",
            "Rukia Kuchiki 🌠 ㊂",
            "Rukia Kuchiki 🌠 ㊃",
            "Rukia Kuchiki 🌠 ㊄",
            "Byakuya Kuchiki 🌠",
            "Byakuya Kuchiki 🌠 ㊀",
            "Byakuya Kuchiki 🌠 ㊃",
            "Byakuya Kuchiki 🌠 ㊄",
            "Byakuya Kuchiki 🌠 ㊅",
        ],
        "mythical": [
            "Toshiro Hitsuyaga 🌌",
            "Ulquiorra Cifer 🌌",
            "Ulquiorra Cifer 🌌 ㊀",
            "Urahara Kisuke 🌌",
            "Urahara Kisuke 🌌 ㊀",
            "Urahara Kisuke 🌌 ㊁",
            "Urahara Kisuke 🌌 ㊂",
            "Unohana Retsu 🌌",
            "Aizen Sosuke 🌌",
            "Aizen Sosuke 🌌 ㊀",
            "Aizen Sosuke 🌌 ㊁",
            "Ichigo Kurosaki 🌌",
            "Ichigo Kurosaki 🌌 ㊀",
            "Ichigo Kurosaki 🌌 ㊁",
            "Rukia Kuchiki 🌌",
            "Rukia Kuchiki 🌌 ㊀",
            "Rukia Kuchiki 🌌 ㊁",
            "Rukia Kuchiki 🌌 ㊂",
            "Rukia Kuchiki 🌌 ㊃",
            "Rukia Kuchiki 🌌 ㊄",
            "Rukia Kuchiki 🌌 ㊅",
            "Byakuya Kuchiki 🌌",
            "Byakuya Kuchiki 🌌 ㊀",
            "Byakuya Kuchiki 🌌 ㊁",
            "Byakuya Kuchiki 🌌 ㊂",
            "Byakuya Kuchiki 🌌 ㊃",
            "Byakuya Kuchiki 🌌 ㊄",
        ],
        "legendary": [
            "Ichigo Kurosaki 🌅",
            "Ulquiorra Cifer 🌅",
            "Aizen Sosuke 🌅",
            "Kurosaki Ichigo 🌅",
            "Toshiro Hitsuyaga 🌅",
            "Byakuya Kuchiki 🌅",
        ],
        "epic": [
            "Toshiro Hitsuyaga 🎆",
            "Toshiro Hitsuyaga 🎆 ㊀",
            "Aizen Sosuke 🎆",
            "Ichigo Kurosaki 🎆",
            "Ichigo Kurosaki 🎆 ㊀",
            "Rukia Kuchiki 🎆",
        ],
        "rare": [
            "Toshiro Hitsuyaga 🎇",
            "Toshiro Hitsuyaga 🎇 ㊀",
            "Urahara Kisuke 🎇",
            "Unohana Retsu 🎇",
            "Unohana Retsu 🎇 ㊀",
            "Ichigo Kurosaki 🎇",
            "Ichigo Kurosaki 🎇 ㊀",
            "Ichigo Kurosaki 🎇 ㊁",
            "Aizen Sosuke 🎇",
            "Aizen Sosuke 🎇 ㊀",
            "Ulquiorra Cifer 🎇",
            "Ulquiorra Cifer 🎇 ㊀",
            "Rukia Kuchiki 🎇",
            "Rukia Kuchiki 🎇 ㊀",
            "Rukia Kuchiki 🎇 ㊁",
            "Byakuya Kuchiki 🎇",
            "Byakuya Kuchiki 🎇 ㊀",
        ],
        "common": [
            "Toshiro Hitsuyaga 🌁",
            "Toshiro Hitsuyaga 🌁 ㊀",
            "Toshiro Hitsuyaga 🌁 ㊁",
            "Toshiro Hitsuyaga 🌁 ㊂",
            "Urahara Kisuke 🌁",
            "Urahara Kisuke 🌁 ㊀",
            "Unohana Retsu 🌁",
            "Unohana Retsu 🌁 ㊀",
            "Unohana Retsu 🌁 ㊁",
            "Ulquiorra Cifer 🌁",
            "Ulquiorra Cifer 🌁 ㊀",
            "Aizen Sosuke 🌁",
            "Aizen Sosuke 🌁 ㊀",
            "Ichigo Kurosaki 🌁",
            "Ichigo Kurosaki 🌁 ㊀",
            "Ichigo Kurosaki 🌁 ㊁",
            "Ichigo Kurosaki 🌁 ㊂",
            "Rukia Kuchiki 🌁",
            "Rukia Kuchiki 🌁 ㊀",
            "Rukia Kuchiki 🌁 ㊁",
            "Rukia Kuchiki 🌁 ㊂",
            "Rukia Kuchiki 🌁 ㊃",
            "Rukia Kuchiki 🌁 ㊄",
            "Rukia Kuchiki 🌁 ㊅",
            "Byakuya Kuchiki 🌁",
            "Byakuya Kuchiki 🌁 ㊀",
            "Byakuya Kuchiki 🌁 ㊁",
            "Byakuya Kuchiki 🌁 ㊂",
            "Byakuya Kuchiki 🌁 ㊃"
            "Byakuya Kuchiki 🌁 ㊄",
            "Byakuya Kuchiki 🌁 ㊅"
            "Byakuya Kuchiki 🌁 ㊆"
        ]
    },
    "Naruto": {
        "divine": [
            "Naruto Uzumaki 🌠",
            "Naruto Uzumaki 🌠 ㊀",
            "Naruto Uzumaki 🌠 ㊁",
            "Naruto Uzumaki 🌠 ㊂",
            "Naruto Uzumaki 🌠 ㊃",
            "Naruto Uzumaki 🌠 ㊄",
            "Uchiha Sasuke 🌠",
            "Uchiha Sasuke 🌠 ㊀",
            "Uchiha Sasuke 🌠 ㊁",
            "Uchiha Sasuke 🌠 ㊂",
            "Uchiha Sasuke 🌠 ㊃",
            "Uchiha Sasuke 🌠 ㊄",
            "Itachi Uchiha 🌠",
            "Itachi Uchiha 🌠 ㊀",
            "Itachi Uchiha 🌠 ㊁",
            "Itachi Uchiha 🌠 ㊂",
            "Itachi Uchiha 🌠 ㊃",
            "Itachi Uchiha 🌠 ㊄",
            "Itachi Uchiha 🌠 ㊅",
            "Obito Uchiha 🌠",
            "Obito Uchiha 🌠 ㊀",
            "Obito Uchiha 🌠 ㊁",
            "Obito Uchiha 🌠 ㊂",
            "Obito Uchiha 🌠 ㊃",
            "Obito Uchiha 🌠 ㊄",
            "Obito Uchiha 🌠 ㊅",
            "Madara Uchiha 🌠",
            "Madara Uchiha 🌠 ㊀",
            "Madara Uchiha 🌠 ㊁",
            "Madara Uchiha 🌠 ㊂",
            "Madara Uchiha 🌠 ㊃",
            "Madara Uchiha 🌠 ㊄",
            "Madara Uchiha 🌠 ㊅",
            "Kakashi Hatake 🌠",
            "Kakashi Hatake 🌠 ㊀",
            "Kakashi Hatake 🌠 ㊁",
            "Kakashi Hatake 🌠 ㊂",
            "Kakashi Hatake 🌠 ㊃",
            "Kakashi Hatake 🌠 ㊄",
        ],
        "mythical": [
            "Itachi Uchiha 🌌",
            "Itachi Uchiha 🌌 ㊀",
            "Itachi Uchiha 🌌 ㊁",
            "Itachi Uchiha 🌌 ㊂",
            "Itachi Uchiha 🌌 ㊃",
            "Itachi Uchiha 🌌 ㊄",
            "Itachi Uchiha 🌌 ㊅",
            "Itachi Uchiha 🌌 ㊆",
            "Itachi Uchiha 🌌 ㊇",
            "Itachi Uchiha 🌌 ㊈",
            "Obito Uchiha 🌌",
            "Obito Uchiha 🌌 ㊀",
            "Obito Uchiha 🌌 ㊁",
            "Obito Uchiha 🌌 ㊂",
            "Obito Uchiha 🌌 ㊃",
            "Obito Uchiha 🌌 ㊄",
            "Obito Uchiha 🌌 ㊅",
            "Obito Uchiha 🌌 ㊆",
            "Obito Uchiha 🌌 ㊇",
            "Obito Uchiha 🌌 ㊈",
            "Obito Uchiha 🌌 ㊉",
            "Obito Uchiha 🌌 ㊉㊀",
            "Madara Uchiha 🌌",
            "Madara Uchiha 🌌 ㊀",
            "Madara Uchiha 🌌 ㊁",
            "Madara Uchiha 🌌 ㊂",
            "Madara Uchiha 🌌 ㊃",
            "Madara Uchiha 🌌 ㊄",
            "Madara Uchiha 🌌 ㊅",
            "Kakashi Hatake 🌌",
            "Kakashi Hatake 🌌 ㊀",
            "Kakashi Hatake 🌌 ㊁",
            "Kakashi Hatake 🌌 ㊂",
            "Kakashi Hatake 🌌 ㊃",
            "Kakashi Hatake 🌌 ㊄",
            "Kakashi Hatake 🌌 ㊅",
            "Naruto Uzumaki 🌌",
            "Naruto Uzumaki 🌌 ㊀",
            "Naruto Uzumaki 🌌 ㊁",
            "Naruto Uzumaki 🌌 ㊂",
            "Naruto Uzumaki 🌌 ㊃",
            "Uchiha Sasuke 🌌",
            "Uchiha Sasuke 🌌 ㊀",
            "Uchiha Sasuke 🌌 ㊁",
            "Uchiha Sasuke 🌌 ㊂",
            "Uchiha Sasuke 🌌 ㊃",
            "Uchiha Sasuke 🌌 ㊄",
            "Uchiha Sasuke 🌌 ㊅",
            "Uchiha Sasuke 🌌 ㊆",
            "Uchiha Sasuke 🌌 ㊇",
        ],
        "legendary": [
            "Naruto Uzumaki 🌅",
            "Uchiha Sasuke 🌅"
            "Itachi Uchiha 🌅",
            "Itachi Uchiha 🌅 ㊀",
            "Itachi Uchiha 🌅 ㊁",
            "Obito Uchiha 🌅",
            "Madara Uchiha 🌅",
            "Kakashi Hatake 🌅"
            "Kakashi Hatake 🌅 ㊀",
        ],
        "epic": [
            "Naruto Uzumaki 🎆",
            "Uchiha Sasuke 🎆",
            "Itachi Uchiha 🎆",
            "Obito Uchiha 🎆",
        ],
        "rare": [
            "Naruto Uzumaki 🎇",
            "Naruto Uzumaki 🎇 ㊀",
            "Uchiha Sasuke 🎇",
            "Uchiha Sasuke 🎇 ㊀",
            "Uchiha Sasuke 🎇 ㊁",
            "Uchiha Sasuke 🎇 ㊂",
            "Uchiha Sasuke 🎇 ㊃",
            "Itachi Uchiha 🎇",
            "Itachi Uchiha 🎇 ㊀",
            "Itachi Uchiha 🎇 ㊁",
            "Obito Uchiha 🎇",
        ],
        "common": [
            "Naruto Uzumaki 🌁",
            "Naruto Uzumaki 🌁 ㊀",
            "Naruto Uzumaki 🌁 ㊁",
            "Naruto Uzumaki 🌁 ㊂",
            "Uchiha Sasuke 🌁",
            "Uchiha Sasuke 🌁 ㊀",
            "Uchiha Sasuke 🌁 ㊁",
            "Uchiha Sasuke 🌁 ㊂",
            "Uchiha Sasuke 🌁 ㊃",
            "Uchiha Sasuke 🌁 ㊄",
            "Itachi Uchiha 🌁",
            "Itachi Uchiha 🌁 ㊀",
            "Itachi Uchiha 🌁 ㊁",
            "Itachi Uchiha 🌁 ㊂",
            "Itachi Uchiha 🌁 ㊃",
            "Itachi Uchiha 🌁 ㊄",
            "Obito Uchiha 🌁",
            "Obito Uchiha 🌁 ㊀",
            "Obito Uchiha 🌁 ㊁",
            "Obito Uchiha 🌁 ㊂",
            "Obito Uchiha 🌁 ㊃",
            "Obito Uchiha 🌁 ㊄",
            "Obito Uchiha 🌁 ㊅",
            "Obito Uchiha 🌁 ㊆",
            "Madara Uchiha 🌁",
            "Madara Uchiha 🌁 ㊀",
            "Madara Uchiha 🌁 ㊁",
            "Madara Uchiha 🌁 ㊂",
            "Madara Uchiha 🌁 ㊃",
            "Kakashi Hatake 🌁",
            "Kakashi Hatake 🌁 ㊀",
            "Kakashi Hatake 🌁 ㊁",
            "Kakashi Hatake 🌁 ㊂",
            "Kakashi Hatake 🌁 ㊃",
            "Kakashi Hatake 🌁 ㊄",
        ]
    },
    "Jujutsu Kaisen": {
        "divine": [
            "Gojo Satoru 🌠",
            "Gojo Satoru 🌠 ㊀",
            "Gojo Satoru 🌠 ㊁",
            "Gojo Satoru 🌠 ㊃",
            "Gojo Satoru 🌠 ㊄",
            "Sukuna x Itadori 🌠",
            "Sukuna x Itadori 🌠 ㊀",
            "Sukuna x Itadori 🌠 ㊁",
            "Sukuna x Itadori 🌠 ㊃",
            "Sukuna x Itadori 🌠 ㊄",
            "Megumi Fushiguro 🌠",
            "Megumi Fushiguro 🌠 ㊀",
            "Yuta Okkotsu 🌠",
            "Yuta Okkotsu 🌠 ㊀",
            "Geto Suguru 🌠",
            "Geto Suguru 🌠 ㊀",
            "Geto Suguru 🌠 ㊁",
            "Geto Suguru 🌠 ㊂",
            "Geto Suguru 🌠 ㊃",
            "Geto Suguru 🌠 ㊄",
            "Geto Suguru 🌠 ㊅",
        ],
        "mythical": [
            "Gojo Satoru 🌌",
            "Gojo Satoru 🌌 ㊀",
            "Gojo Satoru 🌌 ㊁",
            "Gojo Satoru 🌌 ㊃",
            "Gojo Satoru 🌌 ㊄",
            "Gojo Satoru 🌌 ㊅",
            "Gojo Satoru 🌌 ㊆",
            "Gojo Satoru 🌌 ㊇",
            "Gojo Satoru 🌌 ㊈",
            "Gojo Satoru 🌌 ㊉",
            "Gojo Satoru 🌌 ㊉㊀",
            "Gojo Satoru 🌌 ㊉㊁",
            "Sukuna x Itadori 🌌",
            "Sukuna x Itadori 🌌 ㊀",
            "Sukuna x Itadori 🌌 ㊁",
            "Sukuna x Itadori 🌌 ㊂",
            "Sukuna x Itadori 🌌 ㊃",
            "Sukuna x Itadori 🌌 ㊄",
            "Sukuna x Itadori 🌌 ㊅",
            "Sukuna x Itadori 🌌 ㊆",
            "Sukuna x Itadori 🌌 ㊇",
            "Megumi Fushiguro 🌌",
            "Megumi Fushiguro 🌌 ㊀",
            "Megumi Fushiguro 🌌 ㊁",
            "Megumi Fushiguro 🌌 ㊂",
            "Megumi Fushiguro 🌌 ㊃",
            "Yuta Okkotsu 🌌",
            "Yuta Okkotsu 🌌 ㊁",
            "Yuta Okkotsu 🌌 ㊂",
            "Yuta Okkotsu 🌌 ㊃",
            "Geto Suguru 🌌",
            "Geto Suguru 🌌 ㊀",
            "Geto Suguru 🌌 ㊁",
        ],
        "legendary": [
            "Sukuna x Itadori 🌅",
            "Gojo Satoru 🌅",
            "Gojo Satoru 🌅 ㊀",
            "Gojo Satoru 🌅 ㊁",
            "Yuta Okkotsu 🌅",
            "Geto Suguru 🌅",
            "Geto Suguru 🌅 ㊀",
            "Geto Suguru 🌅 ㊁",
        ],
        "epic": [
            "Gojo Satoru 🎆",
            "Gojo Satoru 🎆 ㊀",
            "Gojo Satoru 🎆 ㊁",
            "Gojo Satoru 🎆 ㊂",
            "Sukuna x Itadori 🎆",
            "Sukuna x Itadori 🎆 ㊀",
            "Sukuna x Itadori 🎆 ㊁",
            "Yuta Okkotsu 🎆",
            "Yuta Okkotsu 🎆 ㊁",
            "Yuta Okkotsu 🎆 ㊂",
            "Yuta Okkotsu 🎆 ㊃",
            "Megumi Fushiguro 🎆",
        ],
        "rare": [
            "Gojo Satoru 🎇 ㊀",
            "Gojo Satoru 🎇 ㊁",
            "Gojo Satoru 🎇 ㊂",
            "Gojo Satoru 🎇 ㊃",
            "Gojo Satoru 🎇 ㊄",
            "Gojo Satoru 🎇 ㊅",
            "Gojo Satoru 🎇",
            "Sukuna x Itadori 🎇 ㊀",
            "Sukuna x Itadori 🎇 ㊁",
            "Sukuna x Itadori 🎇 ㊂",
            "Sukuna x Itadori 🎇 ㊃",
            "Yuta Okkotsu 🎇",
            "Yuta Okkotsu 🎇 ㊀",
            "Yuta Okkotsu 🎇 ㊁",
            "Yuta Okkotsu 🎇 ㊂",
            "Megumi Fushiguro 🎇"
        ],
        "common": [
            "Gojo Satoru 🌁",
            "Gojo Satoru 🌁 ㊀",
            "Gojo Satoru 🌁 ㊁",
            "Gojo Satoru 🌁 ㊂",
            "Gojo Satoru 🌁 ㊃",
            "Gojo Satoru 🌁 ㊄",
            "Gojo Satoru 🌁 ㊅",
            "Gojo Satoru 🌁 ㊆",
            "Gojo Satoru 🌁 ㊇",
            "Gojo Satoru 🌁 ㊈",
            "Sukuna x Itadori 🌁",
            "Sukuna x Itadori 🌁 ㊀",
            "Sukuna x Itadori 🌁 ㊁",
            "Sukuna x Itadori 🌁 ㊂",
            "Sukuna x Itadori 🌁 ㊃",
            "Sukuna x Itadori 🌁 ㊄",
            "Sukuna x Itadori 🌁 ㊅",
            "Sukuna x Itadori 🌁 ㊆",
            "Sukuna x Itadori 🌁 ㊇",
            "Yuta Okkotsu 🌁",
            "Yuta Okkotsu 🌁 ㊀",
            "Yuta Okkotsu 🌁 ㊁",
            "Yuta Okkotsu 🌁 ㊂",
            "Yuta Okkotsu 🌁 ㊃",
            "Yuta Okkotsu 🌁 ㊄",
            "Yuta Okkotsu 🌁 ㊅",
            "Megumi Fushiguro 🌁",
            "Megumi Fushiguro 🌁 ㊀",
            "Megumi Fushiguro 🌁 ㊁",
            "Megumi Fushiguro 🌁 ㊂",
            "Megumi Fushiguro 🌁 ㊃",
            "Megumi Fushiguro 🌁 ㊄",
            "Megumi Fushiguro 🌁 ㊅",
            "Megumi Fushiguro 🌁 ㊆",
            "Geto Suguru 🌁",
            "Geto Suguru 🌁 ㊀",
            "Geto Suguru 🌁 ㊁",
            "Geto Suguru 🌁 ㊂",
            "Geto Suguru 🌁 ㊃",
            "Geto Suguru 🌁 ㊄",
            "Geto Suguru 🌁 ㊅",
            "Geto Suguru 🌁 ㊆",
            "Geto Suguru 🌁 ㊇",
            "Geto Suguru 🌁 ㊈",
        ]
    },
    # 'Bleach': {
    #     'divine': ['Toshiro Hitsuyaga 🌠', 'Unohana Retsu 🌠', 'Ulquiorra Cifer 🌠', 'Urahara Kisuke🌠', 'Toshiro Hitsuyaga🌠', 'Aizen Sosuke🌠', 'Aizen Sosuke 🌠', 'Aizen Sosuke 🌠 ', 'Aizen Sosuke  🌠', 'Ichigo Kurosaki 🌠', 'Ichigo Kurosaki  🌠', 'Ichigo Kurosaki 🌠 ', 'Ichigo Kurosaki🌠 ', 'Ichigo Kurosaki🌠'],
    #     'mythical': ['Toshiro Hitsuyaga 🌌', 'Unohana Retsu 🌌', 'Urahara Kisuke🌌', 'Urahara Kisuke 🌌', 'Urahara Kisuke 🌌 ', 'Urahara Kisuke  🌌', 'Ulquiorra Cifer 🌌', 'Ulquiorra Cifer🌌', 'Aizen Sosuke 🌌', 'Aizen Sosuke🌌', 'Aizen Sosuke 🌌 ', 'Ichigo Kurosaki 🌌', 'Ichigo Kurosaki  🌌', 'Ichigo Kurosaki 🌌 '],
    #     'legendary': ['Ichigo Kurosaki 🌅', 'Ulquiorra Cifer 🌅', 'Toshiro Hitsuyaga 🌅', 'Aizen Sosuke 🌅', 'Kurosaki Ichigo 🌅'],
    #     'epic': ['Toshiro Hitsuyaga 🎆', 'Toshiro Hitsuyaga🎆', 'Aizen Sosuke 🎆', 'Ichigo Kurosaki 🎆', 'Ichigo Kurosaki 🎆', 'Ichigo Kurosaki🎆'],
    #     'rare': ['Toshiro Hitsuyaga 🎇', 'Unohana Retsu 🎇', 'Toshiro Hitsuyaga🎇', 'Urahara Kisuke 🎇', 'Ichigo Kurosaki 🎇', 'Ichigo Kurosaki🎇', 'Ichigo Kurosaki 🎇 '],
    #     'common': ['Toshiro Hitsuyaga 🌁', 'Ulquiorra Cifer 🌁', 'Unohana Retsu 🌁', 'Unohana Retsu🌁', 'Ulquiorra Cifer🌁', 'Urahara Kisuke 🌁', 'Urahara Kisuke🌁', 'Aizen Sosuke 🌁', 'Aizen Sosuke🌁', 'Unohana Retsu 🌁 ', 'Toshiro Hitsuyaga🌁', 'Toshiro Hitsuyaga 🌁 ', 'Toshiro Hitsuyaga  🌁', 'Ichigo Kurosaki 🌁', 'Ichigo Kurosaki🌁', 'Ichigo Kurosaki 🌁 ', 'Ichigo Kurosaki  🌁']
    # },
    # 'Naruto': {
    #     'divine': ['Naruto Uzumaki 🌠', 'Uchiha▫️ 🌠', 'Naruto▫️ 🌠', 'Sasuke 🌠', 'Uchiha Sasuke◾️ 🌠', 'Uchiha◾️ 🌠', 'Sasuke Uchiha 🌠', 'Uzumaki Naruto 🌠', 'Naruto 🌠', 'Naruto Uzumaki◾️ 🌠', 'Naruto◾️ 🌠', 'Uchiha Sasuke 🌠'],
    #     'mythical': ['Naruto Uzumaki 🌌', 'Sasuke Uchiha 🌌', 'Naruto▫️ 🌌', 'Sasuke 🌌', 'Uchiha Sasuke◾️ 🌌', 'Sasuke◾️ 🌌', 'Sasuke▫️ 🌌', 'Sasuke Uchiha◾️ 🌌', 'Uchiha Sasuke▫️ 🌌', 'Naruto 🌌', 'Uzumaki Naruto 🌌', 'Naruto Uzumaki◾️ 🌌', 'Uchiha Sasuke 🌌'],
    #     'legendary': ['Naruto Uzumaki 🌅', 'Uchiha Sasuke 🌅'],
    #     'epic': ['Naruto Uzumaki 🎆', 'Uchiha Sasuke 🎆'],
    #     'rare': ['Naruto Uzumaki 🎇', 'Uchiha Sasuke◾️ 🎇', 'Sasuke◾️ 🎇', 'Uzumaki Naruto 🎇', 'Uchiha Sasuke 🎇', 'Sasuke Uchiha 🎇', 'Sasuke 🎇', 'Uchiha Sasuke 🎇'],
    #     'common': ['Naruto Uzumaki 🌁', 'Sasuke Uchiha 🌁', 'Sasuke 🌁', 'Sasuke◾️ 🌁', 'Sasuke Uchiha◾️ 🌁', 'Naruto Uzumaki◾️ 🌁', 'Naruto 🌁', 'Uzumaki Naruto 🌁', 'Uchiha Sasuke 🌁', 'Uchiha Sasuke◾️ 🌁']
    # },
    'Allstars': {
        'soccer': ['Gojo Satoru ⚽', 'Sukuna ⚽'],
        'halloween': ['Ichigo Kurosaki 👻', 'Rukia Kuchiki 👻', 'Ichigo 👻', 'Kurosaki Ichigo 👻', 'Hawk 👻', 'Zoro 👻', 'Sanji 👻', 'Luffi 👻', 'Kimiko 👻', 'Sasuke 👻', 'Gojo 👻', 'Gojo Satoru👻', 'Sukuna 👻', 'Ryomen Sukuna 👻', 'Megumi 👻', 'Kuchiki Rukia 👻', 'Robin 👻', 'Nami 👻', 'Kugisaki 👻', 'Kugisaki Nobara👻', 'Nobara Kugisaki 👻', '2b 👻', '2B 👻'],
        'divine': ['Arima Kishou 🌠', 'Uruma Shun 🌠', 'Gojo Satoru 🌠', 'Kaneki Ken 🌠', 'Gojo Satoru ▫️ ▫️ 🌠', 'Koji 🌠', 'Ulquiorra 🌠', 'Kurumi Tokisaki 🌠', 'Gabimaru 🌠', 'Renji 🌠', 'Grimmjow 🌠', 'Megumi Fushiguro 🌠', 'Geto Suguru ▫️ 🌠', 'Rangiku Matsumoto 🌠', 'Shutara Senjumaru 🌠', 'Gojo Satoru ▫️ ▫️ ▫️ 🌠', 'Gorgon 🌠', 'Urahara Kisuke 🌠', 'Rukia Kuchiki 🌠', 'Inoue Orihime 🌠', 'Soifon 🌠', 'Urahara Kisuke ▫️ 🌠', 'Yagami Light ▫️ 🌠', 'Sukuna 🌠', 'Aizen Sosuke 🌠', 'Yuta Okkotsu ▫️ 🌠', 'Yuta Okkotsu 🌠', 'Kakashi Hatake 🌠', 'Seishiro Nagi 🌠', 'Mitsuri Kanroji 🌠', 'Rengoku Kyojuro ▫️ 🌠', 'Temari Nara 🌠', 'Yagami Light 🌠', 'Tengen Uzui ▫️ 🌠', 'Itachi Uchiha 🌠', 'Geto Suguru 🌠', 'Rengoku Kyojuro 🌠', 'Yami Sukehiro 🌠', 'Choso Kamo 🌠', 'Gojo Satoru ▫️ 🌠', 'Uchiha Madara 🌠', 'Shinobu Kocho 🌠', 'Toji Fushiguro 🌠', 'Tengen Uzui 🌠', 'Toji Fushiguro ▫️ 🌠', 'Sylpha 🌠', 'Hinata Shoyo 🌠', 'Suguru Geto 🌠', 'Neji Hyuga 🌠', 'Suzuya Juzo 🌠', 'Juzo 🌠', 'Juzo Suzuya 🌠', 'Inoske 🌠', 'Todoroki Touya 🌠', 'Mirai Niki 🌠', 'Mich Atsumu 🌠', 'Zoro 🌠', 'Madara Uchiha 🌠', 'Blyu Lok 🌠', 'Mouchiro Tokito 🌠', 'Goku 🌠', 'Ayanokoji  🌠', 'Nagi Seishiro 🌠', 'Anos Voldigoad 🌠', 'Inosuke 🌠', 'Dabi Mha 🌠', 'Sanemi Shinazigawa 🌠', 'Shanks 🌠', 'Lucifer 🌠', 'Muzan Kibutsiju 🌠', 'Obito Uchiha 🌠', 'Will Serfort 🌠', 'Neito Monoma 🌠', 'Sae Itoshi 🌠', 'Choso 🌠', 'Ayanokoji 🌠', 'Polnareff 🌠', 'Jony 🌠', 'Rimuru Tempest 🌠', 'Sid Kageno 🌠', 'So Jin Wu 🌠', 'Zenitsu 🌠', 'Kyouko Hori 🌠', 'Aliya 🌠', 'Hizuru Minakata 🌠', 'Shizuku 🌠', 'Yoruichi 🌠'],
        'mythical': ['L 🌌', 'Juuzou Suzuya 🌌', 'Shinobu Kocho 🌌', 'Manjiro Sano 🌌', 'Eren Yeager ▫️ 🌌', 'Furina 🌌', 'Kurumi Tokisaki 🌌', 'Zenitsu Agatsuma 🌌', 'Apex girl 🌌', 'Mugetsu 🌌', 'Ichigo Kurosaki 🌌', 'Hokushin Mei 🌌', 'Delta 🌌', 'Scaramouche 🌌', 'Blade 🌌', 'Knave 🌌', 'Kazuha 🌌', 'Kaveh 🌌', 'Zhongli 🌌', 'Rei Ayanami 🌌', 'Ayato Kamisato 🌌', 'Sukuna 🌌', 'Makima ▫️ ▫️ 🌌', 'Yuta Okkotsu 🌌', 'Levi Ackerman ▫️ 🌌', 'Jean Kirstein 🌌', 'Mikasa Ackerman 🌌', 'Yuta Okkotsu ▫️ 🌌', 'Uruma Shun 🌌', 'Tanjiro Kamado ▫️ 🌌', 'Gojo Satoru 🌌', 'Guts 🌌', 'Akashi Seijuro 🌌', 'Yagami Light ▫️ 🌌', 'Garou 🌌', 'Urahara Kisuke 🌌', 'Itachi Uchiha 🌌', 'Yuta Okkotsu ▫️ ▫️ 🌌', 'Yato Noragami 🌌', 'Kaneki Ken ▫️ 🌌', 'Hisoka Morow 🌌', 'Kaneki Ken ▫️ ▫️ 🌌', 'Todoroki Shoto 🌌', 'Yagami Light 🌌', 'Makima ▫️ 🌌', 'Arima Kishou 🌌', 'Uchiha Madara 🌌', 'Kaneki Ken 🌌', 'Genos 🌌', '2B 🌌', 'Kokushibo 🌌', 'Power 🌌', 'Touya Todoroki 🌌', 'Makima 🌌', 'Ken Ryuguji 🌌', 'Kakashi Hatake ▫️ 🌌', 'Kakashi Hatake ▫️ ▫️ 🌌', 'Aki Hayakawa 🌌', 'Tanjiro Kamado 🌌', 'Eren Yeager 🌌', 'Kakashi Hatake 🌌', 'Levi Ackerman 🌌', 'Nobara Kugisaki 🌌', 'Gojo 🌌', 'Brodyaga 🌌', 'Akashi 🌌', 'Tomura 🌌', 'Dazai 🌌', 'Soshiro 🌌', 'Kaneki 🌌', 'Guts  🌌', 'Yato 🌌', 'Gyro 🌌', 'Sendju 🌌', 'Nakoshi 🌌', 'Zoro 🌌', 'Nagi 🌌', 'Kitano 🌌', 'Asta 🌌', 'Rimuru Tempest 🌌', 'Ryunosuke 🌌', 'Melodias 🌌', 'Naruto Uzumaki 🌌', 'Arturia Pendragon 🌌', 'Marin Katigawa 🌌', 'Arturia 🌌', 'Kiga 🌌', 'Raphtalia 🌌', 'Shikimori 🌌', 'Mikasa 🌌', 'Albedo 🌌', 'Fubuki 🌌', 'Lane 🌌', 'Mey 🌌', 'Yoruichi Shihoin 🌌', 'Nezuko 🌌', 'Kugisaki Nobara 🌌'],
        'legendary': ['F1 🌅', 'F2 🌅', 'F3 🌅', 'F4 🌅', 'F5 🌅', 'F6 🌅', 'F7 🌅', 'F8 🌅', 'F9 🌅', 'F10 🌅', 'F11 🌅', 'F12 🌅', 'F13 🌅', 'F14 🌅', 'F15 🌅', 'F16 🌅', 'F17 🌅', 'F18 🌅', 'F19 🌅', 'F20 🌅', 'F21 🌅', 'F22 🌅', 'F23 🌅', 'F24 🌅', 'F25 🌅', 'F26 🌅', 'F27 🌅', 'F28 🌅', 'F29 🌅', 'F30 🌅', 'F31 🌅', 'F32 🌅', 'F33 🌅', 'Artoria pendragon 🌅', 'Ichigo Kurosaki 🌅', 'Bell Cranel 🌅', 'Yuta Okkotsu 🌅', 'Roronoa Zoro 🌅', 'Todoroki Shoto 🌅', 'Giyu Tomioka 🌅', 'Zenitsu Agatsuma 🌅', 'Artoria pendragon ▫️ ▫️ ▫️ 🌅', 'Kurama 🌅', 'Monkey D. Luffy ▫️▫️ 🌅', 'Artoria pendragon ▫️ 🌅', 'Artoria pendragon ▫️ ▫️ 🌅', 'Monkey D. Luffy 🌅', 'Sukuna 🌅', 'Itachi Uchiha 🌅', 'Sasuke Uchiha 🌅', 'Naruto Uzumaki 🌅', 'Son Jin Woo 🌅', 'Son Jin Woo ▫️ 🌅', 'Sanji 🌅', 'Mikasa Ackerman 🌅', 'Garou 🌅', 'Shanks 🌅', 'Monkey D. Luffy ▫️ 🌅', 'Zenitsu 🌅', 'Goku 🌅', 'Orachimaru 🌅'],
        'epic': ['Yuta Okkotsu 🎆', 'Ichigo Kurosaki 🎆', 'Yamamoto Genryuusai 🎆', 'Yuta Okkotsu ▫️ 🎆', 'Bakugo Katsuki 🎆', 'Isagi Yoichi 🎆', 'Phantom x ? 🎆', 'Ichigo x Legion 🎆', 'SF x ? 🎆', 'Kiper x ? 🎆', 'Aizen x Juggernaut 🎆', 'Zoldyck x Storm 🎆', 'Visage x ? 🎆', 'Tusk x ? 🎆', 'Yamamoto x Ember 🎆', 'Kunkka x ? 🎆', 'Sukuna x BloodSeeker 🎆', 'Zeus x ? 🎆', 'Todoroki Shoto 🎆', 'Sven 🎆', 'Juggernaut 🎆', 'Void 🎆', 'Chaos Knight 🎆', 'Axe 🎆', 'Luffi 🎆', 'Zeus 🎆', 'Sukuna 🎆', 'Phantom Assassin 🎆', 'Visage 🎆', 'Storm Spirit 🎆', 'Kunkka 🎆', 'Shadow Fiend 🎆', 'Magnus 🎆', 'Tusk 🎆', 'Lo 🎆', 'Spectrum 🎆', 'Arc Warden 🎆', 'Marci 🎆', 'Lina 🎆', 'Drow Ranger 🎆', 'Keeper of Light 🎆'],
        'rare': ['Toshiro Hitsugaya 🎇', 'Kaneki Ken 🎇', 'Hyakkimaru 🎇', 'Uruma Shun 🎇', 'Makima 🎇', 'Crystal Maiden 🎇', 'Gojo x Visage 🎇', 'Arima x Druid 🎇', 'Void x ? 🎇', 'Sukuna x Techies 🎇', 'Gin x Ancient 🎇', 'Sukuna x Morphling 🎇', 'Spectre 🎇', 'Benimaru x Razor 🎇', 'Genos x Axe 🎇', 'Takizawa x Knight 🎇', 'Shinobu Kocho 🎇', 'Miwa Kasumi 🎇', 'Muerta 🎇', 'Undying 🎇', 'Prophet 🎇', 'Razor 🎇', 'Wind Ranger 🎇', 'Luna 🎇', 'Tinker 🎇', 'Bat Rider 🎇', 'Lifestealer 🎇', 'Giyu Tomioka 🎇', 'Musashi Miyamoto 🎇', 'TBlade 🎇', 'Faceless Void 🎇', 'Disruptor 🎇', 'Terrorblade 🎇'],
        'common': ['Yuta Okkotsu 🌁', 'Seishiro Nagi 🌁', 'Kaneki Ken 🌁', 'Uchiha Madara 🌁', 'Manjiro Sano 🌁', 'Itoshi Rin 🌁', 'Benimaru Shinmon 🌁', 'Aki Hayakawa ▫️ 🌁', 'Izuku Midoriya 🌁', 'Deku 🌁', 'Sukuna 🌁', 'Eren Yeager 🌁', 'Aki Hayakawa 🌁', 'Juuzou Suzuya 🌁', 'Toji Fushiguro 🌁', 'Gojo Satoru 🌁', 'Makima 🌁', 'Unohana Retsu 🌁', 'Toshiro Hitsugaya 🌁', 'Arima Kishou 🌁', 'Hyakkimaru 🌁', 'Levi Ackerman 🌁', 'Uchiha Sasuke 🌁', 'Naruto Uzumaki 🌁', 'Zenitsu 🌁', 'Shoto Todoroki 🌁', 'Lance Crown 🌁', 'Megumi Fushiguro 🌁', 'Nanami Kento 🌁', 'Todoroki 🌁', 'Miyamoto Musashi 🌁', 'Feitan Portor 🌁', 'Seidou Takizawa 🌁', 'Gaara 🌁', '02 🌁', 'Power 🌁', 'Yoru 🌁', 'Kugisaki Nobara 🌁', 'Hinata Hyuga 🌁', 'Sakura Haruno 🌁', 'Maki Zenin 🌁']
    },
    # 'Allstars(old)': {
    #     'divine': ['Arima Kishou 🌠', 'Uruma Shun 🌠', 'Gojo Satoru 🌠', 'Kaneki Ken 🌠', 'Gojo Satoru ▫️ ▫️ 🌠', 'Koji 🌠', 'Ulquiorra 🌠', 'Kurumi Tokisaki 🌠', 'Gabimaru 🌠', 'Renji 🌠', 'Grimmjow 🌠', 'Megumi Fushiguro 🌠', 'Geto Suguru ▫️ 🌠', 'Rangiku Matsumoto 🌠', 'Shutara Senjumaru 🌠', 'Gojo Satoru ▫️ ▫️ ▫️ 🌠', 'Gorgon 🌠', 'Urahara Kisuke 🌠', 'Rukia Kuchiki 🌠', 'Inoue Orihime 🌠', 'Soifon 🌠', 'Urahara Kisuke ▫️ 🌠', 'Yagami Light ▫️ 🌠', 'Sukuna 🌠', 'Aizen Sosuke 🌠', 'Yuta Okkotsu ▫️ 🌠', 'Yuta Okkotsu 🌠', 'Kakashi Hatake 🌠', 'Seishiro Nagi 🌠', 'Mitsuri Kanroji 🌠', 'Rengoku Kyojuro ▫️ 🌠', 'Temari Nara 🌠', 'Yagami Light 🌠', 'Tengen Uzui ▫️ 🌠', 'Itachi Uchiha 🌠', 'Geto Suguru 🌠', 'Rengoku Kyojuro 🌠', 'Yami Sukehiro 🌠', 'Choso Kamo 🌠', 'Gojo Satoru ▫️ 🌠', 'Uchiha Madara 🌠', 'Shinobu Kocho 🌠', 'Toji Fushiguro 🌠', 'Tengen Uzui 🌠', 'Toji Fushiguro ▫️ 🌠'],  # Самый редкий уровень
    #     'mythical': ['L 🌌', 'Juuzou Suzuya 🌌', 'Shinobu Kocho 🌌', 'Manjiro Sano 🌌', 'Eren Yeager ▫️ 🌌', 'Furina 🌌', 'Kurumi Tokisaki 🌌', 'Zenitsu Agatsuma 🌌', 'Apex girl 🌌', 'Mugetsu 🌌', 'Ichigo Kurosaki 🌌', 'Hokushin Mei 🌌', 'Delta 🌌', 'Scaramouche 🌌', 'Blade 🌌', 'Knave 🌌', 'Kazuha 🌌', 'Kaveh 🌌', 'Zhongli 🌌', 'Rei Ayanami 🌌', 'Ayato Kamisato 🌌', 'Sukuna 🌌', 'Makima ▫️ ▫️ 🌌', 'Yuta Okkotsu 🌌', 'Levi Ackerman ▫️ 🌌', 'Jean Kirstein 🌌', 'Mikasa Ackerman 🌌', 'Yuta Okkotsu ▫️ 🌌', 'Uruma Shun 🌌', 'Tanjiro Kamado ▫️ 🌌', 'Gojo Satoru 🌌', 'Guts 🌌', 'Akashi Seijuro 🌌', 'Yagami Light ▫️ 🌌', 'Garou 🌌', 'Urahara Kisuke 🌌', 'Itachi Uchiha 🌌', 'Yuta Okkotsu ▫️ ▫️ 🌌', 'Yato Noragami 🌌', 'Kaneki Ken ▫️ 🌌', 'Hisoka Morow 🌌', 'Kaneki Ken ▫️ ▫️ 🌌', 'Todoroki Shoto 🌌', 'Yagami Light 🌌', 'Makima ▫️ 🌌', 'Arima Kishou 🌌', 'Uchiha Madara 🌌', 'Kaneki Ken 🌌', 'Genos 🌌', '2B 🌌', 'Kokushibo 🌌', 'Power 🌌', 'Touya Todoroki 🌌', 'Makima 🌌', 'Ken Ryuguji 🌌', 'Kakashi Hatake ▫️ 🌌', 'Kakashi Hatake ▫️ ▫️ 🌌', 'Aki Hayakawa 🌌', 'Tanjiro Kamado 🌌', 'Eren Yeager 🌌', 'Kakashi Hatake 🌌', 'Levi Ackerman 🌌', 'Nobara Kugisaki 🌌'],
    #     'legendary': ['Artoria pendragon 🌅', 'Ichigo Kurosaki 🌅', 'Bell Cranel 🌅', 'Yuta Okkotsu 🌅', 'Roronoa Zoro 🌅', 'Todoroki Shoto 🌅', 'Giyu Tomioka 🌅', 'Zenitsu Agatsuma 🌅', 'Artoria pendragon ▫️ ▫️ ▫️ 🌅', 'Kurama 🌅', 'Monkey D. Luffy ▫️▫️ 🌅', 'Artoria pendragon ▫️ 🌅', 'Artoria pendragon ▫️ ▫️ 🌅', 'Monkey D. Luffy 🌅', 'Sukuna 🌅', 'Itachi Uchiha 🌅', 'Sasuke Uchiha 🌅', 'Naruto Uzumaki 🌅', 'Son Jin Woo 🌅', 'Son Jin Woo ▫️ 🌅', 'Sanji 🌅', 'Mikasa Ackerman 🌅', 'Garou 🌅', 'Shanks 🌅', 'Monkey D. Luffy ▫️ 🌅', 'Zenitsu 🌅', 'Goku 🌅', 'Orachimaru 🌅'],
    #     'epic': ['Yuta Okkotsu 🎆', 'Ichigo Kurosaki 🎆', 'Yamamoto Genryuusai 🎆', 'Yuta Okkotsu ▫️ 🎆', 'Bakugo Katsuki 🎆', 'Isagi Yoichi 🎆', 'Phantom x ? 🎆', 'Ichigo x Legion 🎆', 'SF x ? 🎆', 'Kiper x ? 🎆', 'Aizen x Juggernaut 🎆', 'Zoldyck x Storm 🎆', 'Visage x ? 🎆', 'Tusk x ? 🎆', 'Yamamoto x Ember 🎆', 'Kunkka x ? 🎆', 'Sukuna x BloodSeeker 🎆', 'Zeus x ? 🎆'],
    #     'rare': ['Toshiro Hitsugaya 🎇', 'Kaneki Ken 🎇', 'Hyakkimaru 🎇', 'Uruma Shun 🎇', 'Makima 🎇', 'Crystal Maiden 🎇', 'Gojo x Visage 🎇', 'Arima x Druid 🎇', 'Void x ? 🎇', 'Sukuna x Techies 🎇', 'Gin x Ancient 🎇', 'Sukuna x Morphling 🎇', 'Spectre 🎇', 'Benimaru x Razor 🎇', 'Genos x Axe 🎇', 'Takizawa x Knight 🎇'],
    #     'common': ['Yuta Okkotsu 🌁', 'Seishiro Nagi 🌁', 'Kaneki Ken 🌁', 'Uchiha Madara 🌁', 'Manjiro Sano 🌁', 'Itoshi Rin 🌁', 'Benimaru Shinmon 🌁', 'Aki Hayakawa ▫️ 🌁', 'Izuku Midoriya 🌁', 'Deku 🌁', 'Sukuna 🌁', 'Eren Yeager 🌁', 'Aki Hayakawa 🌁', 'Juuzou Suzuya 🌁', 'Toji Fushiguro 🌁', 'Gojo Satoru 🌁', 'Makima 🌁', 'Unohana Retsu 🌁', 'Toshiro Hitsugaya 🌁', 'Arima Kishou 🌁', 'Hyakkimaru 🌁', 'Levi Ackerman 🌁'],
    # },
}


# def common_gacha():
#     rand_num = random.random()
#     if rand_num < 0.001:  # 0.1% — divine
#         return 'divine'
#     elif rand_num < 0.005:  # 0.4% — mythical
#         return 'mythical'
#     elif rand_num < 0.025:  # 2% — legendary
#         return 'legendary'
#     elif rand_num < 0.085:  # 6% — epic
#         return 'epic'
#     elif rand_num < 0.22:  # 13.5% — rare
#         return 'rare'
#     else:  # 78.0% — common
#         return 'common'
#
#
# def golden_gacha():
#     rand_num = random.random()
#     if rand_num < 0.005:  # 0.5% — divine
#         return 'divine'
#     elif rand_num < 0.015:  # 1.0% — mythical
#         return 'mythical'
#     elif rand_num < 0.13:  # 11.5% — legendary
#         return 'legendary'
#     elif rand_num < 0.37:  # 24% — epic
#         return 'epic'
#     elif rand_num < 0.70:  # 33% — rare
#         return 'rare'
#     else:  # 30% — common (если допустимо, иначе убери common вообще)
#         return 'common'
#
#
# def sacred_gacha():
#     rand_num = random.random()
#     if rand_num < 0.25:  # 25% шанс
#         return 'divine'
#     elif rand_num < 0.35:  # 35% шанс
#         return 'mythical'
#     else:  # 40% шанс
#         return 'legendary'


def roll(weighted):
    """weighted: список [('название', вероятность)] с суммой = 1.0"""
    r, acc = random.random(), 0.0
    for name, p in weighted:
        acc += p
        if r < acc:
            return name
    return weighted[-1][0]  # защита от float

def common_gacha():
    weights = [
        ('divine',    0.001),   # 0.1%
        ('mythical',  0.004),   # 0.4%
        ('legendary', 0.020),   # 2.0%
        ('epic',      0.060),   # 6.0%
        ('rare',      0.135),   # 13.5%
        ('common',    0.780),   # 78.0%
    ]
    return roll(weights)

def golden_gacha():
    weights = [
        ('divine',    0.005),   # 0.5%
        ('mythical',  0.010),   # 1.0%
        ('legendary', 0.115),   # 11.5%
        ('epic',      0.240),   # 24%
        ('rare',      0.330),   # 33%
        ('common',    0.300),   # 30%
    ]
    return roll(weights)

def sacred_gacha():
    weights = [
        ('divine',    0.10),    # 10%
        ('mythical',  0.25),    # 25%
        ('legendary', 0.65),    # 65%
    ]
    return roll(weights)


async def card_gacha(user_id, callback):

    account = await mongodb.get_user(user_id)
    universe = account['universe']
    inline_id = callback.inline_message_id

    # if callback.data == "soccer_item":
    #     if account['inventory']['items']['soccer'] < 100:
    #         await callback.answer(
    #             text="❖ У вас не достаточно ⚽️ Футбольных предметов. Получайте больше во время событие!",
    #             show_alert=True
    #         )
    #         return
    #     character_category = 'soccer'
    #     await mongodb.update_value(user_id, {'inventory.items.halloween': -100})
    #     icon = "⚽️"
    #     emoji = None
    #     button = "soccer_item"
    #
    # elif callback.data == "halloween_item":
    #     if account['inventory']['items']['halloween'] < 100:
    #         await callback.answer(
    #             text="❖ У вас не достаточно 🎃 Хэллоуинских предметов. Получайте больше во время событие!",
    #             show_alert=True
    #         )
    #         return
    #     character_category = 'halloween'
    #     await mongodb.update_value(user_id, {'inventory.items.halloween': -100})
    #     icon = "🎃"
    #     emoji = None
    #     button = "halloween_item"

    if callback.data == "golden_key":
        if account['inventory']['items']['tickets']['keys'] < 1:
            await callback.answer(
                text="❖ У вас нет  <tg-emoji emoji-id='5276009277482349032'>🧧</tg-emoji> священнего билета. Приобретите его в 🏮 рынке!",
                show_alert=True
            )
            return
        character_category = sacred_gacha()  # Используем новую функцию здесь
        await mongodb.update_value(user_id, {'inventory.items.tickets.keys': -1})
        icon = "🧧"
        emoji = "5276009277482349032"
        button = "golden_key"
    elif callback.data == "golden":
        if account['inventory']['items']['tickets']['golden'] < 1:
            await callback.answer(
                text="❖ У вас нет  <tg-emoji emoji-id='5278306114323099155'>🎫</tg-emoji> золотого билета. Приобретите его в 🏮 рынке!",
                show_alert=True
            )
            return
        character_category = golden_gacha()
        await mongodb.update_value(user_id, {'inventory.items.tickets.golden': -1})
        icon = "🎫"
        emoji = "5278306114323099155"
        button = "golden"
    else:
        if account['inventory']['items']['tickets']['common'] < 1:
            await callback.answer(
                text="❖ У вас нет  <tg-emoji emoji-id='5276027638467539484'>🎟</tg-emoji> обычного билета. Приобретите его в 🏮 рынке!",
                show_alert=True
            )
            return
        character_category = common_gacha()
        await mongodb.update_value(user_id, {'inventory.items.tickets.common': -1})
        icon = "🎟"
        emoji = "5276027638467539484"
        button = "common_summon"

    character = random.choice(characters[universe][character_category])  # Выбираем случайного персонажа из списка

    async def is_in_inventory():
        get_account = await mongodb.get_user(user_id)
        ch_characters = get_account['inventory'].get('characters')
        if characters:
            universe_characters = ch_characters.get(universe)
            if universe_characters:
                return character in universe_characters.get(character_category, [])
        return False

    fragments = 2
    avatar = character_photo.get_stats(universe, character, 'avatar')
    avatar_type = character_photo.get_stats(universe, character, 'type')
    ch_universe = character_photo.get_stats(universe, character, 'universe')
    rarity = character_photo.get_stats(universe, character, 'rarity')

    if rarity == 'Обычная':
        power = 142
    elif rarity == 'Редкая':
        power = 160
    elif rarity == 'Эпическая':
        power = 178
    elif rarity == 'Легендарная':
        power = 196
    elif rarity == 'Мифическая':
        power = 214
    else:
        power = 232

    msg = (f"❖<tg-emoji emoji-id='5415624997689381048'>✨</tg-emoji> Редкость: {rarity}"
           f"\n❖<tg-emoji emoji-id='431420156532235514'>⚜️</tg-emoji> Мощь: {power}")
    buttons = [f"{icon}", ' 🔙 ']
    calls = [f"{button}", 'banner']

    if await is_in_inventory():
        fragments = 4
        if callback.data == "halloween_item":
            halloween = 100
            await mongodb.update_value(user_id, {'inventory.items.halloween': halloween})
            msg = (f"❖ Вам попалась повторка:"
                   f"\n🎃 <i>Предметы возвращены в инвентарь</i>")
        else:
            # Если персонаж уже в инвентаре, увеличиваем только силу и деньги
            await mongodb.update_value(user_id, {'account.fragments': fragments})
            msg = (f"❖ Вам попалась повторка:"
                   f"\n<i> Зачислены только удвоенные бонусы"
                   f"\n + 2х <tg-emoji emoji-id='5994373915294567486'>🧩</tg-emoji> Осколков </i>")

    else:
        if account['universe'] not in ['Allstars', 'Allstars(old)']:
            strength = character_photo.get_stats(universe, character, 'arena')['strength']
            agility = character_photo.get_stats(universe, character, 'arena')['agility']
            intelligence = character_photo.get_stats(universe, character, 'arena')['intelligence']
            msg = (f"❖ <tg-emoji emoji-id='5415624997689381048'>✨</tg-emoji> Редкость: {rarity}"
                   f"\n❖ <tg-emoji emoji-id='5341294339454675575'>🗺</tg-emoji> Вселенная: {ch_universe}"
                   f"\n • <tg-emoji emoji-id='5316791950462950306'>✊🏻</tg-emoji> Сила: {strength}"
                   f"\n • <tg-emoji emoji-id='5949588538952518773'>👣</tg-emoji> Ловкость: {agility}"
                   f"\n • <tg-emoji emoji-id='5371053287380361807'>🧠</tg-emoji> Интелект: {intelligence}")

        await mongodb.push(universe, character_category, character, user_id)
        await mongodb.update_value(user_id, {'account.fragments': fragments})
        await mongodb.update_value(user_id, {'campaign.power': power})

    pattern = dict(
        caption=f"\n ── •✧✧• ───────"
                f"\n <tg-emoji emoji-id='5936017305585586269'>🎴</tg-emoji> 〢 <tg-spoiler>{character}</tg-spoiler>"
        # f"\n ── •✧✧• ──────────"
                f"<blockquote>{msg}</blockquote>"
                f"\n──❀*̥˚──◌──◌──❀*̥˚"
                f"\n<i> + {fragments}<tg-emoji emoji-id='5994373915294567486'>🧩</tg-emoji> Осколков </i>",
        reply_markup=inline_builder(buttons, calls,
                                    row_width=[1], icon_custom_emoji_id=[emoji, None]),
        parse_mode=ParseMode.HTML
    )
    if character_category == 'halloween' or character_category == 'soccer':
        media_id = "CgACAgIAAxkDAAEDr_JnE9fQnk00RusWPffEMMTzJwmD6QACMEAAAkPekElgios1nCJOCjYE"
        time = 5
    elif character_category == 'divine':
        media_id = "CgACAgIAAx0CfstymgACBiVlzikq6HGeA2exxOQQbekNg_KImAACDEIAAsuUcUpNy3ouWDG9xTQE"
        time = 7
    elif character_category == 'mythical':
        media_id = "CgACAgIAAx0CfstymgACBiRlzikgAAEbiUWlzuHAYpT3rlL91O4AAgtCAALLlHFKEzbl8cFs3cg0BA"
        time = 6.2
    elif character_category == 'legendary':
        media_id = "CgACAgIAAx0CfstymgACBiNlzikdQ_RssBYRl4A0G--qgie-ewACCkIAAsuUcUo0j4VTQm0baDQE"
        time = 7.2
    elif character_category == 'epic':
        media_id = "CgACAgIAAx0CfstymgACBixlzivkRBW3Iki8XQ11VLPBx7nqXAACH0IAAsuUcUojWO7WBnMQlzQE"
        time = 7.3
    elif character_category == 'rare':
        media_id = "CgACAgIAAx0CfstymgACBitlzivdoGBCYVhnFaEGl6QWqoxXhgACHkIAAsuUcUqp4UhpJLR2LTQE"
        time = 7.2
    else:
        media_id = "CgACAgIAAx0CfstymgACBiplzivQmnDtjQTgUR23iW_IC4XYjwACHUIAAsuUcUoqWzNNWaav6zQE"
        time = 7.2

    media = InputMediaAnimation(media=media_id)

    await callback.message.edit_media(media, inline_id)

    current_date = datetime.today().date()
    current_datetime = datetime.combine(current_date, datetime.time(datetime.now()))
    await mongodb.update_user(user_id, {"tasks.last_summon": current_datetime})

    await asyncio.sleep(time)

    if avatar_type == 'photo':
        new_photo = InputMediaPhoto(media=avatar, has_spoiler=True)
    else:
        new_photo = InputMediaAnimation(media=avatar, has_spoiler=True)

    await callback.message.edit_media(new_photo, inline_id)

    await callback.message.edit_caption(inline_message_id=inline_id, **pattern)


async def first_summon(callback, universe):
    inline_id = callback.inline_message_id
    character_category = common_gacha()

    character = random.choice(characters[universe][character_category])  # Выбираем случайного персонажа из списка
    avatar = character_photo.get_stats(universe, character, 'avatar')
    avatar_type = character_photo.get_stats(universe, character, 'type')
    ch_universe = character_photo.get_stats(universe, character, 'universe')
    rarity = character_photo.get_stats(universe, character, 'rarity')

    if rarity == 'Обычная':
        power = 142
    elif rarity == 'Редкая':
        power = 160
    elif rarity == 'Эпическая':
        power = 178
    elif rarity == 'Легендарная':
        power = 196
    elif rarity == 'Мифическая':
        power = 214
    else:
        power = 232

    msg = (f"❖<tg-emoji emoji-id='5415624997689381048'>✨</tg-emoji> Редкость: {rarity}"
           f"\n❖<tg-emoji emoji-id='431420156532235514'>⚜️</tg-emoji> Мощь: {power}")

    if universe not in ['Allstars', 'Allstars(old)']:
        strength = character_photo.get_stats(universe, character, 'arena')['strength']
        agility = character_photo.get_stats(universe, character, 'arena')['agility']
        intelligence = character_photo.get_stats(universe, character, 'arena')['intelligence']
        power = character_photo.get_stats(universe, character, 'arena')['power']
        msg = (f"❖ <tg-emoji emoji-id='5415624997689381048'>✨</tg-emoji> Редкость: {rarity}"
               f"\n❖ <tg-emoji emoji-id='5341294339454675575'>🗺</tg-emoji> Вселенная: {ch_universe}"
               f"\n • <tg-emoji emoji-id='5316791950462950306'>✊🏻</tg-emoji> Сила: {strength}"
               f"\n • <tg-emoji emoji-id='5949588538952518773'>👣</tg-emoji> Ловкость: {agility}"
               f"\n • <tg-emoji emoji-id='5371053287380361807'>🧠</tg-emoji> Интелект: {intelligence}"
               f"\n • <tg-emoji emoji-id='431420156532235514'>⚜️</tg-emoji> Мощь: {power}")

    pattern = dict(
        caption=f"\n ── •✧✧• ───────"
                f"\n <tg-emoji emoji-id='5936017305585586269'>🎴</tg-emoji> 〢 <tg-spoiler>{character}</tg-spoiler>"
                # f"\n ── •✧✧• ──────────"
                f"<blockquote>{msg}</blockquote>"
                f"\n──❀*̥˚──◌──◌──❀*̥˚",
        reply_markup=success(),
        parse_mode=ParseMode.HTML
    )

    if avatar_type == 'photo':
        new_photo = InputMediaPhoto(media=avatar, has_spoiler=True)
    else:
        new_photo = InputMediaAnimation(media=avatar, has_spoiler=True)

    if character_category == 'divine':
        media_id = "CgACAgIAAx0CfstymgACBiVlzikq6HGeA2exxOQQbekNg_KImAACDEIAAsuUcUpNy3ouWDG9xTQE"
        time = 7
    elif character_category == 'mythical':
        media_id = "CgACAgIAAx0CfstymgACBiRlzikgAAEbiUWlzuHAYpT3rlL91O4AAgtCAALLlHFKEzbl8cFs3cg0BA"
        time = 6.2
    elif character_category == 'legendary':
        media_id = "CgACAgIAAx0CfstymgACBiNlzikdQ_RssBYRl4A0G--qgie-ewACCkIAAsuUcUo0j4VTQm0baDQE"
        time = 7.2
    elif character_category == 'epic':
        media_id = "CgACAgIAAx0CfstymgACBixlzivkRBW3Iki8XQ11VLPBx7nqXAACH0IAAsuUcUojWO7WBnMQlzQE"
        time = 7.3
    elif character_category == 'rare':
        media_id = "CgACAgIAAx0CfstymgACBitlzivdoGBCYVhnFaEGl6QWqoxXhgACHkIAAsuUcUqp4UhpJLR2LTQE"
        time = 7.2
    else:
        media_id = "CgACAgIAAx0CfstymgACBiplzivQmnDtjQTgUR23iW_IC4XYjwACHUIAAsuUcUoqWzNNWaav6zQE"
        time = 7.2

    media = InputMediaAnimation(media=media_id)

    await callback.message.edit_media(media, inline_id)

    await asyncio.sleep(time)

    await callback.message.edit_media(new_photo, inline_id)

    await callback.message.edit_caption(inline_message_id=inline_id, **pattern)
    await callback.message.answer(f"❖ <tg-emoji emoji-id='5818690584449126294'>📌</tg-emoji> Добро пожаловать во вселенную {universe}", reply_markup=menu_button())
    return character, character_category, power


@router.message((F.text == 'Grab') | (F.text == 'grab')
                | (F.text == 'Граб') | (F.text == 'граб') | (F.text == '🎴 Grab'))
async def campaign_rank(message: Message):
    user_id = message.from_user.id
    account = await mongodb.get_user(user_id)

    if account is not None and account['_id'] == user_id:
        bot = message.bot  # Используем объект бота из сообщения
        universe = account['universe']
        if await check_user_subscription(user_id, bot):
            # Если 'last_call_time' не существует, установите его в текущее время
            if 'last_call_time' not in account or datetime.now() - account['last_call_time'] >= timedelta(hours=4):
                now = datetime.now()
                await mongodb.update_get_card(user_id, now)
                # Извлеките обновленные данные после обновления
                character_category = golden_gacha()
                character = random.choice(characters[universe][character_category])
                avatar = character_photo.get_stats(universe, character, 'avatar')
                avatar_type = character_photo.get_stats(universe, character, 'type')
                ch_universe = character_photo.get_stats(universe, character, 'universe')
                rarity = character_photo.get_stats(universe, character, 'rarity')
                if rarity == 'Обычная':
                    power = 142
                elif rarity == 'Редкая':
                    power = 160
                elif rarity == 'Эпическая':
                    power = 178
                elif rarity == 'Легендарная':
                    power = 196
                elif rarity == 'Мифическая':
                    power = 214
                else:
                    power = 232
                msg = (f"❖<tg-emoji emoji-id='5415624997689381048'>✨</tg-emoji> Редкость: {rarity}"
                       f"\n❖<tg-emoji emoji-id='431420156532235514'>⚜️</tg-emoji> Мощь: {power}")
                buttons = []
                calls = []

                async def is_in_inventory():
                    get_account = await mongodb.get_user(user_id)
                    if universe in get_account['inventory']['characters'] and character_category in \
                            get_account['inventory']['characters'][universe]:
                        return character in get_account['inventory']['characters'][universe][character_category]
                    else:
                        return False

                if await is_in_inventory():
                    fragments = 4
                    # Если персонаж уже в инвентаре, увеличиваем только силу и деньги
                    await mongodb.update_value(user_id, {'account.fragments': fragments})
                    msg = (f"❖ Вам попалась повторка:"
                           f"\n<i> Зачислены только бонусы"
                           f"\n + 2х <tg-emoji emoji-id='5994373915294567486'>🧩</tg-emoji> Осколков </i>")
                else:
                    fragments = 2
                    if account['universe'] not in ['Allstars', 'Allstars(old)']:
                        strength = character_photo.get_stats(universe, character, 'arena')['strength']
                        agility = character_photo.get_stats(universe, character, 'arena')['agility']
                        intelligence = character_photo.get_stats(universe, character, 'arena')['intelligence']
                        msg = (f"❖ <tg-emoji emoji-id='5415624997689381048'>✨</tg-emoji> Редкость: {rarity}"
                               f"\n❖ <tg-emoji emoji-id='5341294339454675575'>🗺</tg-emoji> Вселенная: {ch_universe}"
                               f"\n • <tg-emoji emoji-id='5316791950462950306'>✊🏻</tg-emoji> Сила: {strength}"
                               f"\n • <tg-emoji emoji-id='5949588538952518773'>👣</tg-emoji> Ловкость: {agility}"
                               f"\n • <tg-emoji emoji-id='5371053287380361807'>🧠</tg-emoji> Интелект: {intelligence}")
                        buttons = ["<tg-emoji emoji-id='5936017305585586269'>🎴</tg-emoji> Навыки"]
                        calls = [Ability(action="ability", universe=universe,
                                         character=character, back='banner')]

                    await mongodb.push(universe, character_category, character, user_id)
                    await mongodb.update_value(user_id, {'account.fragments': fragments})
                    await mongodb.update_value(user_id, {'campaign.power': power})

                pattern = dict(
                    caption=f"\n ── •✧✧• ───────"
                            f"\n <tg-emoji emoji-id='5936017305585586269'>🎴</tg-emoji> 〢 <tg-spoiler>{character}</tg-spoiler>"
                            # f"\n ── •✧✧• ──────────"
                            f"<blockquote>{msg}</blockquote>"
                            f"\n──❀*̥˚──◌──◌──❀*̥˚"
                            f"\n<i> + {fragments}<tg-emoji emoji-id='5994373915294567486'>🧩</tg-emoji> Осколков </i>",
                    # reply_markup=inline_builder(buttons, calls,
                    #                             row_width=[1]),
                    parse_mode=ParseMode.HTML
                )

                if character_category == 'divine':
                    media_id = "CgACAgIAAx0CfstymgACBiVlzikq6HGeA2exxOQQbekNg_KImAACDEIAAsuUcUpNy3ouWDG9xTQE"
                    time = 7
                elif character_category == 'mythical':
                    media_id = "CgACAgIAAx0CfstymgACBiRlzikgAAEbiUWlzuHAYpT3rlL91O4AAgtCAALLlHFKEzbl8cFs3cg0BA"
                    time = 6.2
                elif character_category == 'legendary':
                    media_id = "CgACAgIAAx0CfstymgACBiNlzikdQ_RssBYRl4A0G--qgie-ewACCkIAAsuUcUo0j4VTQm0baDQE"
                    time = 7.2
                elif character_category == 'epic':
                    media_id = "CgACAgIAAx0CfstymgACBixlzivkRBW3Iki8XQ11VLPBx7nqXAACH0IAAsuUcUojWO7WBnMQlzQE"
                    time = 7.3
                elif character_category == 'rare':
                    media_id = "CgACAgIAAx0CfstymgACBitlzivdoGBCYVhnFaEGl6QWqoxXhgACHkIAAsuUcUqp4UhpJLR2LTQE"
                    time = 7.2
                else:
                    media_id = "CgACAgIAAx0CfstymgACBiplzivQmnDtjQTgUR23iW_IC4XYjwACHUIAAsuUcUoqWzNNWaav6zQE"
                    time = 7.2

                gacha_msg = await message.reply_animation(media_id)

                await asyncio.sleep(time)

                current_date = datetime.today().date()
                current_datetime = datetime.combine(current_date, datetime.time(datetime.now()))
                await mongodb.update_user(user_id, {"tasks.last_free_summon": current_datetime})

                if avatar_type == 'photo':
                    new_photo = InputMediaPhoto(media=avatar, has_spoiler=True)
                else:
                    new_photo = InputMediaAnimation(media=avatar, has_spoiler=True)

                await gacha_msg.edit_media(new_photo)
                await gacha_msg.edit_caption(**pattern)

            else:
                # Вычислите, сколько времени осталось
                remaining_time = timedelta(hours=4) - (datetime.now() - account['last_call_time'])
                remaining_seconds = int(remaining_time.total_seconds())
                remaining_hours = remaining_seconds // 3600
                remaining_minutes = (remaining_seconds % 3600) // 60

                await message.reply_animation(
                    animation="CgACAgIAAx0CfstymgACBzpl0I7O2WanntSMhoK4cXEfBxt33AAC4j8AAvasiUp11UMJwtm8UTQE",
                    caption="\n ── •✧✧• ──────────"
                    f"\n✶ 🔮 Можно совершить бесплатный <tg-emoji emoji-id='5278306114323099155'>🎫</tg-emoji> золотой призыв раз в ⏳ 4 часа"
                    # f"\n ── •✧✧• ──────────"
                    "\n➖➖➖➖➖➖➖➖➖➖➖"
                    f"\n⏳ подожди еще {remaining_hours}ч {remaining_minutes}мин")
        else:
            await message.reply_animation(
                animation="CgACAgIAAx0CfstymgACBzpl0I7O2WanntSMhoK4cXEfBxt33AAC4j8AAvasiUp11UMJwtm8UTQE",
                caption="\n ── •✧✧• ──────────"
                        f"\n✶ 🔮 Можно совершить бесплатный <tg-emoji emoji-id='5278306114323099155'>🎫</tg-emoji> золотой призыв раз в ⏳ 4 часа"
                        # f"\n ── •✧✧• ──────────"
                        "\n➖➖➖➖➖➖➖➖➖➖➖"
                        f"\n🔒 Для разблокировки нужно подписаться на канал бота",
                reply_markup=channel_check())
    else:
        media = "CgACAgIAAx0CfstymgACBbRlzDgYWpgLO50Lgeg0HImQEC9GEAAC7D4AAsywYUo5sbjTkVkCRjQE"
        await message.answer_animation(animation=media, caption="✧ • 📄 Ты не регистрирован"
                                                                f"\n── •✧✧• ──────────"
                                                                f"\n❖ 💮 Присоединяйся в мир битв и "
                                                                f"получи своего первого <tg-emoji emoji-id='5936017305585586269'>🎴</tg-emoji> персонажа <tg-emoji emoji-id='5415624997689381048'>✨</tg-emoji>",
                                                                # f"\n── •✧✧• ──────────",
                                       reply_markup=start_button())
