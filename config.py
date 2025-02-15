import os

from dotenv import load_dotenv

load_dotenv(override=True)


class BotConfig(object):
    ENV = os.getenv("ENV", default="production")
    EPHEMERAL_MSG_DURATION = int(os.getenv("EPHEMERAL_MSG_DURATION", default=10))
    DEBUG_GUILD_ID = int(os.getenv("DEBUG_GUILD_ID"))


class DiscordConfig(object):
    TOKEN = os.getenv("TOKEN")


class APIConfig(object):
    KEY = os.getenv("API_KEY")
    URL = os.getenv("API_URL")


class ActivityMonitorConfig(object):
    # UPDATE_INTERVAL adjusted based on Discord rate limit on channel rename (5 min.)
    UPDATE_INTERVAL = float(os.getenv("UPDATE_INTERVAL", default=360))


class WavelinkConfig(object):
    URL = os.getenv("LAVALINK_URL", default="http://localhost:2333")
    PASSWORD = os.getenv("LAVALINK_PASSWORD", default="youshallnotpass")
    DEFAULT_VOLUME = int(os.getenv("DEFAULT_VOLUME", default=10))