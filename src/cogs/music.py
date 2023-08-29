import discord
import logging
import wavelink

from src.helper import get_member_voice_channel

from config import BotConfig, WavelinkConfig
from discord.ext import commands
from typing import cast


_log = logging.getLogger(__name__)


class Music(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
    

    @commands.Cog.listener()
    async def on_ready(self):
        node = wavelink.Node(uri=WavelinkConfig.URI, password=WavelinkConfig.PASSWORD)
        await wavelink.NodePool.connect(client=self.bot, nodes=[node])


    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        _log.info(f"Wavelink node {node.id} is ready")


    @discord.slash_command(
        description="Play a track with a given search keyword"
    )
    @discord.guild_only()
    async def play(self, ctx: discord.ApplicationContext, search: str):      
        check_user_in_vc, member_vc = await self.__check_user_in_vc(ctx)

        if not check_user_in_vc:
            return
        
        if not ctx.voice_client:
            # Connect to the user voice channel if not connected yet
            vc = await member_vc.connect(cls=wavelink.Player) # type: ignore
        else:
            # Check if the user is in the same voice channel as the bot
            check_user_same_vc = await self.__check_user_same_vc(ctx)
            
            if not check_user_same_vc:
                return
        
            # Get current voice channel the bot connected to
            vc = cast(wavelink.Player, ctx.voice_client)
        
        # Search track from YouTube with the given search keyword
        tracks = await wavelink.YouTubeTrack.search(search)
        
        # Check if no track is found from the given search keyword
        if not tracks:
            await ctx.respond(
                "No track found."
            )

        # Play the track
        track = tracks[0]
        await vc.play(track)
        await ctx.respond(f"Now playing: {track.title}\n{track.uri}")
    

    @discord.slash_command(
        description="Pause track playback"
    )
    @discord.guild_only()
    async def pause(self, ctx: discord.ApplicationContext):
        check_user_same_vc = await self.__check_user_same_vc(ctx)

        if not check_user_same_vc:
            return
        
        # Get current voice channel the bot connected to
        vc = cast(wavelink.Player, ctx.voice_client)

        if not vc.is_playing():
            await ctx.respond(
                "Nothing is playing right now!",
                ephemeral=True,
                delete_after=BotConfig.EPHEMERAL_MSG_DURATION
            )
            return
        
        await vc.pause()
        await ctx.respond("Track playback is paused.")


    @discord.slash_command(
        description="Resume track playback"
    )
    @discord.guild_only()
    async def resume(self, ctx: discord.ApplicationContext):
        check_user_same_vc = await self.__check_user_same_vc(ctx)

        if not check_user_same_vc:
            return
        
        # Get current voice channel the bot connected to
        vc = cast(wavelink.Player, ctx.voice_client)

        if not vc.is_paused():
            await ctx.respond(
                "Playback is not paused!",
                ephemeral=True,
                delete_after=BotConfig.EPHEMERAL_MSG_DURATION
            )
            return
        
        await vc.resume()
        await ctx.respond("Track playback is resumed.")


    @discord.slash_command(
        description="Stop track playback"
    )
    @discord.guild_only()
    async def stop(self, ctx: discord.ApplicationContext):
        check_user_same_vc = await self.__check_user_same_vc(ctx)

        if not check_user_same_vc:
            return
        
        # Get current voice channel the bot connected to
        vc = cast(wavelink.Player, ctx.voice_client)

        if not vc.is_playing() and not vc.is_paused():
            await ctx.respond(
                "Nothing is playing right now!",
                ephemeral=True,
                delete_after=BotConfig.EPHEMERAL_MSG_DURATION
            )
            return
        
        await vc.stop()
        await ctx.respond("Track playback is stopped.")


    @discord.slash_command(
        description="Disconnect from voice channel"
    )
    @discord.guild_only()
    async def disconnect(self, ctx: discord.ApplicationContext):
        check_user_same_vc = await self.__check_user_same_vc(ctx)

        if not check_user_same_vc:
            return
        
        # Get current voice channel the bot connected to
        vc = cast(wavelink.Player, ctx.voice_client)
        
        await vc.disconnect()
        await ctx.respond("Disconnected from voice channel.")


    async def __check_user_in_vc(self, ctx: discord.ApplicationContext) -> tuple[bool, discord.VoiceChannel | None]:
        # Get the user voice channel
        member = cast(discord.Member, ctx.user)
        member_vc = get_member_voice_channel(member)

        # Check if the user is not in a voice channel
        if member_vc is None:
            await ctx.respond(
                "You are not in a voice channel!",
                ephemeral=True,
                delete_after=BotConfig.EPHEMERAL_MSG_DURATION
            )

            return False, None
        
        return True, member_vc
    

    async def __check_user_same_vc(self, ctx: discord.ApplicationContext) -> bool:
        # Get the user voice channel
        member = cast(discord.Member, ctx.user)
        member_vc = get_member_voice_channel(member)

        # Check if the bot is not in a voice channel
        if ctx.voice_client is None:
            await ctx.respond(
                "I'm not in a voice channel!",
                ephemeral=True,
                delete_after=BotConfig.EPHEMERAL_MSG_DURATION
            )

            return False
        
        # Check if the user is not in a voice channel
        if member_vc is None:
            await ctx.respond(
                "You are not in a voice channel!",
                ephemeral=True,
                delete_after=BotConfig.EPHEMERAL_MSG_DURATION
            )

            return False
        
        # Check if the bot is in the same voice channel as the user
        if  ctx.voice_client.channel != member_vc:
            await ctx.respond(
                "I'm not in the same voice channel as you!",
                ephemeral=True,
                delete_after=BotConfig.EPHEMERAL_MSG_DURATION
            )

            return False

        return True


def setup(bot: discord.Bot):
    bot.add_cog(Music(bot))