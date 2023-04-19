import os

from dotenv import load_dotenv

load_dotenv()

class BotConfig(object):
    ENV = os.getenv("ENV")
    EPHEMERAL_MSG_DURATION = 10

class DiscordConfig(object):
    TOKEN = os.getenv("TOKEN")

class ActivityMonitorConfig(object):
    # UPDATE_INTERVAL adjusted based on Discord rate limit on channel rename (5 min.)
    UPDATE_INTERVAL = 360