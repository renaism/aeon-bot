import discord

from discord.ext import commands


class General(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot


    @discord.slash_command(
        description="List all available commands."
    )
    async def help(self, ctx: discord.ApplicationContext):
        cog_contents = []

        for cog_name, cog in self.bot.cogs.items():
            command_contents = []

            for command in cog.walk_commands():
                if isinstance(command, discord.SlashCommand):
                    command_contents.append(f"{command.mention} {command.description}")
            
            if len(command_contents) > 0:
                cog_content = f"**{cog_name}**\n"
                cog_content += "\n".join(command_contents)
                cog_contents.append(cog_content)
        
        embed_content = "\n\n".join(cog_contents)
            
        embed = discord.Embed(
            title="Command List",
            description=embed_content
        )

        await ctx.respond(embed=embed)


    @discord.slash_command(
        description="Check if the bot is online and get its latency."
    )
    async def ping(self, ctx: discord.ApplicationContext):
        latency_ms = int(self.bot.latency * 1000)
        await ctx.respond(f"Pong! Latency is {latency_ms} ms")


def setup(bot: discord.Bot):
    bot.add_cog(General(bot))