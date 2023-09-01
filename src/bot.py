import discord

from typing import cast


class Bot(discord.Bot):
    async def on_ready(self):
        print(f"Logged in as {self.user}")
    

    def get_slash_command(self, command: str) -> discord.SlashCommand:
        slash_command = cast(discord.SlashCommand, self.get_command(command, type=discord.SlashCommand))
        return slash_command