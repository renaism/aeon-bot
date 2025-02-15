import discord
import wavelink

from dataclasses import dataclass
from datetime import datetime
from discord.ext import commands
from enum import Enum
from typing import Any, cast

from config import BotConfig, WavelinkConfig
from src.bot import Bot
from src.helper import get_member_voice_channel, get_youtube_search_suggestion
from src.responses import embed_response, EmbedMessageType


class LoopType(Enum):
    OFF = "off"
    ONE = "one"
    ALL = "all"


class PlayAction(Enum):
    QUEUE = "queue"
    NEXT = "next"
    NOW = "now"


class Player(wavelink.Player):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.autoplay = True
        self.loop = LoopType.OFF
        self.shuffle = False


@dataclass
class PlayerSession:
    channel: discord.VoiceChannel
    player: Player
    ctx: discord.ApplicationContext
    created_at: datetime = datetime.now()


    async def end(self):
        await self.player.disconnect()
        await self.ctx.interaction.edit_original_response(
            embed=discord.Embed(description="Session has ended"),
            view=None,
            delete_after=BotConfig.EPHEMERAL_MSG_DURATION
        )


class PlayerInfoEmbed(discord.Embed):
    def __init__(self, session: PlayerSession):
        player = session.player
        track = player.current

        super().__init__(
            colour=discord.Colour.blue(),
            title = f"Music Player {session.channel.mention}"
        )

        content = ""

        if track:
            pass
        
        content += "Use `/music add` to add a song!"

        self.description = content
        self.set_footer(text=f"Volume: {player.volume}%")


class PlayerActionView(discord.ui.View):
    def __init__(self, session: PlayerSession):
        self.session = session
        super().__init__()
    

    @discord.ui.button(emoji="⏮️", style=discord.ButtonStyle.secondary)
    async def prev_button_callback(self, button: discord.Button, interaction: discord.Interaction):
        pass


    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.secondary)
    async def play_button_callback(self, button: discord.Button, interaction: discord.Interaction):
        pass


    @discord.ui.button(emoji="⏸️", style=discord.ButtonStyle.secondary)
    async def pause_button_callback(self, button: discord.Button, interaction: discord.Interaction):
        pass


    @discord.ui.button(emoji="⏹️", style=discord.ButtonStyle.secondary)
    async def stop_button_callback(self, button: discord.Button, interaction: discord.Interaction):
        pass


    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.secondary)
    async def next_button_callback(self, button: discord.Button, interaction: discord.Interaction):
        pass


    @discord.ui.button(emoji="🔀", style=discord.ButtonStyle.secondary)
    async def shuffle_button_callback(self, button: discord.Button, interaction: discord.Interaction):
        player = self.session.player

        # Toggle shuffle state
        player.shuffle = not player.shuffle

        # Update button colour based on the shuffle state
        if player.shuffle:
            button.style = discord.ButtonStyle.primary
        else:
            button.style = discord.ButtonStyle.secondary
        
        # Update view
        await interaction.response.edit_message(view=self)


    @discord.ui.button(emoji="🔁", style=discord.ButtonStyle.secondary)
    async def repeat_button_callback(self, button: discord.Button, interaction: discord.Interaction):
        player = self.session.player
        
        # Cycle repeat state
        if player.loop == LoopType.OFF:
            player.loop = LoopType.ALL
            button.emoji = discord.PartialEmoji.from_str("🔁")
            button.style = discord.ButtonStyle.primary
        elif player.loop == LoopType.ALL:
            player.loop = LoopType.ONE
            button.emoji = discord.PartialEmoji.from_str("🔂")
            button.style = discord.ButtonStyle.primary
        else:
            player.loop = LoopType.OFF
            button.emoji = discord.PartialEmoji.from_str("🔁")
            button.style = discord.ButtonStyle.secondary
        
        # Update view
        await interaction.response.edit_message(view=self)


    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.secondary)
    async def queue_prev_button_callback(self, button: discord.Button, interaction: discord.Interaction):
        pass


    @discord.ui.button(label="➡️", style=discord.ButtonStyle.secondary)
    async def queue_next_button_callback(self, button: discord.Button, interaction: discord.Interaction):
        pass


    @discord.ui.button(label="End", style=discord.ButtonStyle.danger)
    async def end_button_callback(self, button: discord.Button, interaction: discord.Interaction):
        pass


class MusicV2(commands.Cog):
    music = discord.SlashCommandGroup(
        name="music",
        description="Music player commands"
    )

    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.sessions: dict[int, PlayerSession] = {}
    

    @music.command(
        description="Start the music player session"
    )
    @discord.guild_only()
    async def start(self, ctx: discord.ApplicationContext):
        if ctx.guild_id is None:
            return
        
        # Check for existing session on the guild
        session = self.sessions.get(ctx.guild_id)

        if session and session.ctx.channel:
            channel = cast(discord.TextChannel, session.ctx.channel)
            await embed_response(
                ctx,
                msg=f"There is already an existing player in {channel.mention}!",
                msg_type=EmbedMessageType.WARNING,
                ephemeral=True
            )
            return
        
        # Check if the user is connected to a voice channel
        member = cast(discord.Member, ctx.user)
        member_vc = get_member_voice_channel(member)

        if not member_vc:
            await embed_response(
                ctx,
                msg="You must be in a voice channel before starting a session!",
                msg_type=EmbedMessageType.WARNING,
                ephemeral=True
            )
            return
        
        # Connect to voice channel
        player: Player = await member_vc.connect(cls=Player()) # type: ignore
        await player.set_volume(WavelinkConfig.DEFAULT_VOLUME)

        # Register session
        session = PlayerSession(
            channel=member_vc,
            ctx=ctx,
            player=player
        )

        self.sessions[ctx.guild_id] = session

        await ctx.respond(
            embed=PlayerInfoEmbed(session),
            view=PlayerActionView(session)
        )
    

    @music.command(
        description="Stop the music player session"
    )
    @discord.guild_only()
    async def stop(self, ctx: discord.ApplicationContext):
        if ctx.guild_id is None:
            return
        
        # Check for existing session on the guild
        session = self.sessions.get(ctx.guild_id)

        if not session:
            await embed_response(
                ctx,
                msg="There is no player running on this server!",
                msg_type=EmbedMessageType.WARNING,
                ephemeral=True
            )
            return
        
        del self.sessions[ctx.guild_id]
        await session.end()

        await embed_response(
            ctx,
            msg=f"Ended player session in {session.channel.mention}.",
            msg_type=EmbedMessageType.WARNING,
        )


    @music.command(
        description="Add song to the player queue"
    )
    @discord.guild_only()
    @discord.option(
        name="search",
        type=str,
        autocomplete=get_youtube_search_suggestion
    )
    async def add(self, ctx: discord.ApplicationContext, search: str, action: PlayAction = PlayAction.QUEUE):
        pass


def setup(bot: Bot):
    bot.add_cog(MusicV2(bot))