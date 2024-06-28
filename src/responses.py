import discord

from enum import Enum
from requests import Response

from config import BotConfig


class EmbedMessageType(Enum):
    INFO = 0
    SUCCESS = 1
    WARNING = 2
    ERROR = 3


async def api_error_response(ctx: discord.ApplicationContext, response: Response | None):
    msg = "An error occured."
    
    if response is not None:
        data = response.json()

        if "detail" in data:
            msg = data["detail"]
    
    await ctx.respond(
        msg,
        ephemeral=True,
        delete_after=BotConfig.EPHEMERAL_MSG_DURATION
    )


async def embed_response(
    ctx: discord.ApplicationContext,
    msg: str,
    msg_type: EmbedMessageType = EmbedMessageType.INFO,
    title: str | None = None,
    ephemeral: bool = False
):
    # Determine embed colour based on the message type
    if msg_type == EmbedMessageType.SUCCESS:
        colour = discord.Colour.green()
    elif msg_type == EmbedMessageType.WARNING:
        colour = discord.Colour.yellow()
    elif msg_type == EmbedMessageType.ERROR:
        colour = discord.Colour.red()
    else:
        colour = discord.Colour.blurple()
    
    embed = discord.Embed(
        title=title,
        description=msg,
        colour=colour
    )

    await ctx.respond(
        embed=embed,
        ephemeral=ephemeral,
        delete_after=BotConfig.EPHEMERAL_MSG_DURATION if ephemeral else None
    )