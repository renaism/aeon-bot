import logging
import os

from dotenv import load_dotenv
from src import Bot

load_dotenv()

if os.getenv("env") == "production":
    logging.basicConfig(level=logging.WARNING)
else:
    logging.basicConfig(level=logging.INFO)

bot = Bot()
bot.load_extension('src.cogs.general')

if __name__ == "__main__":
    bot.run(os.getenv("token"))