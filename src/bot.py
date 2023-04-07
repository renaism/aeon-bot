import discord

class Bot(discord.Bot):
    async def on_ready(self):
        print(f"Logged in as {self.user}")

        self.__load_cogs()    
    
    def __load_cogs(self):
        self.load_extension('src.cogs.general')