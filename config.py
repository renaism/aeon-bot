import os

from dotenv import load_dotenv

load_dotenv()

class BotConfig(object):
    ENV = os.getenv("ENV")

class DiscordConfig(object):
    TOKEN = os.getenv("TOKEN")