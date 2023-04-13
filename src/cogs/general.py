import discord

from discord.ext import commands

class General(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
    
    @discord.slash_command(
        description="Check if the bot is online and get its latency."
    )
    async def ping(self, ctx: discord.ApplicationContext):
        latency_ms = int(self.bot.latency * 1000)
        await ctx.respond(f"Pong! Latency is {latency_ms} ms")

def setup(bot: discord.Bot):
    bot.add_cog(General(bot))