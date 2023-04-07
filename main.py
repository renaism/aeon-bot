import logging
import config
import discord

from src import Bot


if config.BotConfig.ENV == "production":
    logging.basicConfig(level=logging.WARNING)
else:
    logging.basicConfig(level=logging.INFO)

intents = discord.Intents.all()
bot = Bot(intents=intents)

if __name__ == "__main__":
    bot.run(config.DiscordConfig.TOKEN)