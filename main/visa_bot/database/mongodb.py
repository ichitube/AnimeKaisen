import os
from datetime import datetime
from typing import Any, Dict

from motor.motor_asyncio import AsyncIOMotorClient


MONGO_URI = os.getenv("VISA_MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("VISA_MONGO_DB", "visa_bot")
COLLECTION_NAME = os.getenv("VISA_MONGO_COLLECTION", "applications")

_client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(MONGO_URI)
    return _client


def get_collection():
    client = get_client()
    return client[DATABASE_NAME][COLLECTION_NAME]


async def save_application(data: Dict[str, Any]) -> None:
    collection = get_collection()
    data = {
        **data,
        "submitted_at": datetime.utcnow(),
    }
    await collection.insert_one(data)
