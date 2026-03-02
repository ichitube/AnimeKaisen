import os
import importlib

def test_smoke_import():
    os.environ.setdefault("MONGO_URI", "mongodb://localhost:27017")
    os.environ.setdefault("BOT_TOKEN", "123:ABC")
    os.environ.setdefault("OPENAI_API_KEY", "test-key")
    importlib.import_module("app.__main__")

