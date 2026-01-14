from typing import Callable, Awaitable, Dict, Any
from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message
from cachetools import TTLCache


class AntiFloodMiddleware(BaseMiddleware):
    def __init__(self, time_limit: int = 3) -> None:
        # Кэшируем как чат, так и пользователя для предотвращения флуда
        self.limit = TTLCache(maxsize=10_000, ttl=time_limit)

    async def __call__(
            self,
            handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery,
            data: Dict[str, Any],
    ) -> Any:
        # Создаем уникальный ключ для чата и пользователя
        user_chat_id = (event.message.chat.id, event.from_user.id)

        if user_chat_id in self.limit:
            # Заблокировать флуд для групповых чатов
            await event.answer("❖ Слишком частое нажатие кнопок!", show_alert=True)
            return
        else:
            self.limit[user_chat_id] = None  # Добавляем сочетание чат + пользователь в кэш
        return await handler(event, data)


class AntiFloodMiddlewareM(BaseMiddleware):
    def __init__(self, time_limit: int = 3) -> None:
        self.limit = TTLCache(maxsize=10_000, ttl=time_limit)

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any],
    ) -> Any:
        user_chat_id = (event.chat.id, event.from_user.id)

        if user_chat_id in self.limit:
            # Заблокировать флуд для сообщений в группах
            await event.answer("❖ Слишком частое сообщение!")
            return
        else:
            self.limit[user_chat_id] = None  # Добавляем сочетание чат + пользователь в кэш
        return await handler(event, data)
