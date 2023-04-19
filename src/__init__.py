from .bot import Bot
from .db import JSONDatabase

db = JSONDatabase()

__all__ = ["Bot", "db"]