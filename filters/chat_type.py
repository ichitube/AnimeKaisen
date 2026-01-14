from typing import Union

from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery


class ChatTypeFilter(BaseFilter):  # [1]
    def __init__(self, chat_type: Union[str, list]):  # [2]
        self.chat_type = chat_type

    async def __call__(self, message: Message) -> bool:  # [3]
        if isinstance(self.chat_type, str):
            return message.chat.type == self.chat_type
        else:
            return message.chat.type in self.chat_type


class CallbackChatTypeFilter(BaseFilter):  # [1]
    def __init__(self, chat_type: Union[str, list]):  # [2]
        self.chat_type = chat_type

    async def __call__(self, callback: CallbackQuery) -> bool:  # [3]
        if isinstance(self.chat_type, str):
            return callback.message.chat.type == self.chat_type
        else:
            return callback.message.chat.type in self.chat_type
