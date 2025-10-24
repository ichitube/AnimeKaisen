from dataclasses import dataclass
import os


class ConfigError(RuntimeError):
    """Raised when required configuration values are missing."""


@dataclass(slots=True)
class BotConfig:
    token: str
    mongo_uri: str
    mongo_db: str
    mongo_collection: str


def load_config() -> BotConfig:
    token = os.getenv("VISA_BOT_TOKEN")
    if not token:
        raise ConfigError("Environment variable VISA_BOT_TOKEN is required")

    mongo_uri = os.getenv("VISA_MONGO_URI", "mongodb://localhost:27017")
    mongo_db = os.getenv("VISA_MONGO_DB", "visa_registration")
    mongo_collection = os.getenv("VISA_MONGO_COLLECTION", "applications")

    return BotConfig(
        token=token,
        mongo_uri=mongo_uri,
        mongo_db=mongo_db,
        mongo_collection=mongo_collection,
    )
