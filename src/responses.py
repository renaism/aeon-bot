import discord

from requests import Response

from config import BotConfig

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