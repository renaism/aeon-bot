import discord
import wavelink

from ..helper import get_member_voice_channel

from config import BotConfig, WavelinkConfig
from discord.ext import commands
from typing import cast


class Music(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
    

    @commands.Cog.listener()
    async def on_ready(self):
        node = wavelink.Node(uri=WavelinkConfig.URI, password=WavelinkConfig.PASSWORD)
        await wavelink.NodePool.connect(client=self.bot, nodes=[node])


    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        print(f"Wavelink node {node.id} is ready")
    

    @discord.slash_command(
        description="Play a track with a given search keyword"
    )
    @discord.guild_only()
    async def play(self, ctx: discord.ApplicationContext, search: str):      
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

            return
        
        # Connect to the voice channel
        vc = await member_vc.connect(cls=wavelink.Player) # type: ignore
        
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


def setup(bot: discord.Bot):
    bot.add_cog(Music(bot))