from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

from ..config import BotConfig

_client: Optional[AsyncIOMotorClient] = None


def get_client(uri: str) -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(uri)
    return _client


def get_collection(config: BotConfig) -> AsyncIOMotorCollection:
    client = get_client(config.mongo_uri)
    return client[config.mongo_db][config.mongo_collection]


async def save_application(config: BotConfig, data: Dict[str, Any]) -> None:
    collection = get_collection(config)
    document = {
        **data,
        "created_at": datetime.utcnow(),
    }
    await collection.insert_one(document)
