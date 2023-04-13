import config
import discord

from discord.ext import commands
from typing import cast

class Utility(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
    
    @discord.slash_command(
        description="Mention every user in the same voice channel as you."
    )
    @discord.guild_only()
    async def vcmention(self, ctx: discord.ApplicationContext):
        member = cast(discord.Member, ctx.user)

        # Check if the user is in a voice channel
        if (not isinstance(member.voice, discord.VoiceState) or
            not isinstance(member.voice.channel, discord.VoiceChannel)):
            return await ctx.respond("You are not in a voice channel!",
                              ephemeral=True,
                              delete_after=config.BotConfig.EPHEMERAL_MSG_DURATION)
        
        voice_state = cast(discord.VoiceState, member.voice)
        voice_channel = cast(discord.VoiceChannel, voice_state.channel)

        if len(voice_channel.members) <= 1:
            return await ctx.respond("You are alone in the voice channel! :(",
                              ephemeral=True,
                              delete_after=config.BotConfig.EPHEMERAL_MSG_DURATION)
        
        # Create mentions for every member in the voice channel,
        # except the user who called the command
        mentions = " ".join(f"{vc_mem.mention}" for vc_mem in voice_channel.members 
                            if vc_mem != member)

        return await ctx.respond(f"**{member.display_name}**: {mentions}")

def setup(bot: discord.Bot):
    bot.add_cog(Utility(bot))