import logging
import os

from discord import Intents
from dotenv import load_dotenv
from src import Bot

load_dotenv()

if os.getenv("env") == "production":
    logging.basicConfig(level=logging.WARNING)
else:
    logging.basicConfig(level=logging.INFO)

intents = Intents.all()
bot = Bot(intents=intents)

if __name__ == "__main__":
    bot.run(os.getenv("token"))