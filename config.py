import os

from dotenv import load_dotenv

load_dotenv()


class BotConfig(object):
    ENV = os.getenv("ENV", default="production")
    EPHEMERAL_MSG_DURATION = int(os.getenv("EPHEMERAL_MSG_DURATION", default=10))


class DiscordConfig(object):
    TOKEN = os.getenv("TOKEN")


class ActivityMonitorConfig(object):
    # UPDATE_INTERVAL adjusted based on Discord rate limit on channel rename (5 min.)
    UPDATE_INTERVAL = float(os.getenv("UPDATE_INTERVAL", default=360))