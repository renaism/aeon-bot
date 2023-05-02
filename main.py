import logging
import config
import discord

from src import Bot


# Setup logging
if config.BotConfig.ENV == "production":
    logging.basicConfig(level=logging.WARNING)
else:
    logging.basicConfig(level=logging.INFO)

# Bot configurations
intents = discord.Intents.all()
bot = Bot(intents=intents)

# Load cogs
bot.load_extension('src.cogs.general')
bot.load_extension('src.cogs.utility')
bot.load_extension('src.cogs.activity_monitor')
bot.load_extension('src.cogs.music')


if __name__ == "__main__":
    bot.run(config.DiscordConfig.TOKEN)