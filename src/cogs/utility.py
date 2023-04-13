import config
import discord

from ..helper import get_member_voice_channel

from discord.ext import commands
from typing import cast


class Utility(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
    

    @discord.slash_command(
        description="Move all user on a voice channel to another voice channel."
    )
    @discord.guild_only()
    @discord.default_permissions(move_members=True)
    async def migratevc(self, ctx: discord.ApplicationContext,
                        channel_to: discord.VoiceChannel,
                        channel_from: discord.VoiceChannel | None = None):
        member = cast(discord.Member, ctx.user)

        # If no origin voice channel is specified,
        # check if user is in a voice channel
        if channel_from is None:
            member_vc = get_member_voice_channel(member)

            if member_vc is None:
                await ctx.respond(
                    "You are not in a voice channel! Please specify the origin voice channel.",
                    ephemeral=True,
                    delete_after=config.BotConfig.EPHEMERAL_MSG_DURATION
                )

                return
            
            channel_from = member_vc
        
        # Check if the origin voice channel has any user connected 
        if len(channel_from.members) == 0:
            await ctx.respond(
                "Origin voice channel has no connected user.",
                ephemeral=True,
                delete_after=config.BotConfig.EPHEMERAL_MSG_DURATION
            )

            return
        
        # Move all user from origin voice channel to other voice channel
        for vc_mem in channel_from.members:
            await vc_mem.move_to(channel_to)
        
        await ctx.respond(
            f"Migrated all user from {channel_from.name} to {channel_to.name}.",
            ephemeral=True
        )
    

    @discord.slash_command(
        description="Mention every user in the same voice channel as you."
    )
    @discord.guild_only()
    async def vcmention(self, ctx: discord.ApplicationContext):
        member = cast(discord.Member, ctx.user)

        # Check if the user is in a voice channel
        voice_channel = get_member_voice_channel(member)
        if voice_channel is None:
            return await ctx.respond(
                "You are not in a voice channel!",
                ephemeral=True,
                delete_after=config.BotConfig.EPHEMERAL_MSG_DURATION
            )

        # Check if there is any other user in the voice channel
        if len(voice_channel.members) <= 1:
            return await ctx.respond(
                "You are alone in the voice channel! :(",
                ephemeral=True,
                delete_after=config.BotConfig.EPHEMERAL_MSG_DURATION
            )
        
        # Create mentions for every member in the voice channel,
        # except the user who called the command
        mentions = " ".join(f"{vc_mem.mention}" for vc_mem in voice_channel.members 
                            if vc_mem != member)

        return await ctx.respond(f"**{member.display_name}**: {mentions}")


def setup(bot: discord.Bot):
    bot.add_cog(Utility(bot))