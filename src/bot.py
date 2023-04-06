import discord

class Bot(discord.Bot):
    async def on_ready(self):
        print(f"Logged in as {self.user}")

        self.load_extension("src.cogs.general")
        self.load_extension("src.cogs.activity_monitor")