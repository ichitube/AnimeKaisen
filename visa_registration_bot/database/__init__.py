"""MongoDB helpers for the visa registration bot."""

from .mongodb import get_client, get_collection, save_application

__all__ = ["get_client", "get_collection", "save_application"]
