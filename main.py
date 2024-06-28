import config
import discord
import logging
import os

from src import Bot


# Setup logging
if config.BotConfig.ENV == "production":
    logging.basicConfig(level=logging.WARNING)
else:
    logging.basicConfig(level=logging.INFO)

# Bot configurations
intents = discord.Intents.all()
bot = Bot(intents=intents)

# Load internal cogs
cogs = [
    'src.cogs.general',
    'src.cogs.utility',
    'src.cogs.activity_monitor',
    #'src.cogs.music',
]


def load_external_cogs():
    if not os.path.exists('ext'):
        return
    
    # Get all direct subdirectories in ext folder
    dirs = [ f.path for f in os.scandir('ext') if f.is_dir() ]

    # Load cog in each ext folder
    for dir in dirs:
        # Skip ext marked inactive
        if os.path.exists(f"{dir}/.inactive"):
            continue
        
        # Get cog list from the folder
        ext_cogs = [ 
            f.path[:-3].replace('/', '.') 
            for f in os.scandir(dir) if f.name.endswith('.py') 
        ]

        bot.load_extensions(*ext_cogs)


if __name__ == "__main__":
    bot.load_extensions(*cogs)
    load_external_cogs()
    bot.run(config.DiscordConfig.TOKEN)
