import discord
import logging
import wavelink

from datetime import timedelta
from discord.ext import commands
from enum import Enum
from typing import Any, cast

from config import BotConfig, WavelinkConfig
from src.helper import get_member_voice_channel


_log = logging.getLogger(__name__)


class PlayAction(Enum):
    QUEUE = "queue"
    NEXT = "next"
    NOW = "now"


class Player(wavelink.Player):
    def __init__(self, command_channel: discord.TextChannel, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.autoplay = True
        self.command_channel = command_channel


class Music(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
    

    @commands.Cog.listener()
    async def on_ready(self):
        node = wavelink.Node(uri=WavelinkConfig.URL, password=WavelinkConfig.PASSWORD)
        await wavelink.NodePool.connect(client=self.bot, nodes=[node])


    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        _log.info(f"Wavelink node {node.id} is ready")


    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload: wavelink.TrackEventPayload):
        vc = cast(Player, payload.player)
        track = payload.track

        # Send message about the track being played
        embed = discord.Embed(
            title="Now playing",
            description=f"[{track.title}]({track.uri})"
        )

        embed.set_footer(text=f"Length: {self.__format_track_length(track.length)}")

        await vc.command_channel.send(
            embed=embed
        )


    @discord.slash_command(
        description="Play a track with a given search keyword"
    )
    @discord.guild_only()
    async def play(self, ctx: discord.ApplicationContext, search: str, action: PlayAction = PlayAction.QUEUE): 
        check_user_in_vc, member_vc = await self.__check_user_in_vc(ctx)

        if not check_user_in_vc:
            return
        
        if not ctx.voice_client:
            # Connect to the user voice channel if not connected yet
            player = Player(command_channel=cast(discord.TextChannel, ctx.channel))
            vc = await member_vc.connect(cls=player) # type: ignore
            await vc.set_volume(WavelinkConfig.DEFAULT_VOLUME)
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

        track = tracks[0]
        queue_command = cast(discord.SlashCommand, self.bot.get_command('queue', type=discord.SlashCommand))
        
        if action == PlayAction.NEXT:
            # Put the track at the start of the queue
            vc.queue.put_at_front(track)

            embed = discord.Embed(
                title=f"Next in {queue_command.mention}",
                description=f"[{track.title}]({track.uri})"
            )

            embed.set_footer(text=f"Length: {self.__format_track_length(track.length)}")

            await ctx.respond(embed=embed)
        elif action == PlayAction.NOW:
            if vc.current:
                # Set aside currently playing to the queue
                vc.queue.put_at_front(vc.current)
            
            await ctx.respond(":white_check_mark:")
            await vc.play(track, populate=True)
        else:
            # Put the track at the end of the queue
            vc.queue.put(track)

            embed = discord.Embed(
                title=f"Added to {queue_command.mention}",
                description=f"[{track.title}]({track.uri})"
            )

            embed.set_footer(text=f"Length: {self.__format_track_length(track.length)}")

            await ctx.respond(embed=embed)

        if not vc.current:
            await vc.play(vc.queue.pop(), populate=True)
    

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
        await ctx.respond(":pause_button:")


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

        if vc.is_playing():
            await ctx.respond(
                "Playback is not stopped!",
                ephemeral=True,
                delete_after=BotConfig.EPHEMERAL_MSG_DURATION
            )

            return
        
        if vc.is_paused():
            await vc.resume()
            await ctx.respond(":arrow_forward:")

            return
        
        if vc.queue.is_empty and vc.auto_queue.is_empty:
            await ctx.respond(
                "Queue is empty!",
                ephemeral=True,
                delete_after=BotConfig.EPHEMERAL_MSG_DURATION
            )

            return
        
        if not vc.queue.is_empty:
            await vc.play(vc.queue.pop())
        elif not vc.auto_queue.is_empty:
            await vc.play(vc.auto_queue.pop())
        
        await ctx.respond(":arrow_forward:")


    @discord.slash_command(
        description="Skip the current track"
    )
    @discord.guild_only()
    async def next(self, ctx: discord.ApplicationContext):
        check_user_same_vc = await self.__check_user_same_vc(ctx)

        if not check_user_same_vc:
            return
        
        # Get current voice channel the bot connected to
        vc = cast(wavelink.Player, ctx.voice_client)
        
        await vc.stop()
        await ctx.respond(":track_next:")
    

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
        
        if vc.current:
            await vc.pause()
            await vc.seek(0)

        await ctx.respond(":stop_button:")
    

    @discord.slash_command(
        description="Set playback volume (0-100)"
    )
    @discord.guild_only()
    async def setvolume(self, ctx: discord.ApplicationContext, volume: int):
        check_user_same_vc = await self.__check_user_same_vc(ctx)

        if not check_user_same_vc:
            return
        
        # Get current voice channel the bot connected to
        vc = cast(wavelink.Player, ctx.voice_client)

        # Bound volume value to 0-100
        volume = min(max(volume, 0), 100)

        # Set the player volume
        await vc.set_volume(volume)
        await ctx.respond(f"Playback volume set at {volume}%")


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
        await ctx.respond(":white_check_mark:")
    

    @discord.slash_command(
        description="Show track playback queue"
    )
    @discord.guild_only()
    async def queue(self, ctx: discord.ApplicationContext):
        check_user_same_vc = await self.__check_user_same_vc(ctx)

        if not check_user_same_vc:
            return
        
        # Get current Player
        vc = cast(wavelink.Player, ctx.voice_client)

        embed_content = ""

        # Currently playing
        embed_content += "**Now playing**:\n"

        if vc.current:
            track = vc.current
            position = self.__format_track_length(int(vc.position))
            duration = self.__format_track_length(track.length)
            embed_content += f"[{track.title}]({track.uri}) ({position}/{duration})\n"
        else:
            embed_content += "*None*\n"
        
        # Next in queue
        embed_content += "\n**Next in queue**:\n"

        if not vc.queue.is_empty:
            track_contents = [
                f"{i+1}. [{track.title}]({track.uri}) ({self.__format_track_length(track.length)})" 
                for i, track in enumerate(vc.queue)
            ]
            embed_content += "\n".join(track_contents)
        else:
            embed_content += "*None*\n"
        
        # Next in auto-queue
        if vc.queue.is_empty and not vc.auto_queue.is_empty:
            embed_content += "\n**Next in auto-queue**:\n"
            track_contents = [
                f"{i+1}. [{track.title}]({track.uri}) ({self.__format_track_length(track.length)})"
                for i, track in enumerate(list(vc.auto_queue)[:5])
            ]
            embed_content += "\n".join(track_contents)
        
        # Response embed
        embed = discord.Embed(
            title="Queue",
            description=embed_content
        )

        embed.set_footer(text=f"Volume: {vc.volume}%")

        await ctx.respond(embed=embed)


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
    

    def __format_track_length(self, length: int) -> str:
        td = timedelta(milliseconds=length)
        seconds = int(td.total_seconds())

        hours = seconds // 3600
        seconds %= 3600

        minutes = seconds // 60
        seconds %= 60

        duration_str = f"{minutes:02}:{seconds:02}"
        
        if hours > 0:
            # Show hour if length is more than one hour
            duration_str = f"{hours:02}:{duration_str}"

        return duration_str


def setup(bot: discord.Bot):
    bot.add_cog(Music(bot))