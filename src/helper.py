import discord
import wavelink

from typing import cast

def get_member_voice_channel(member: discord.Member) -> discord.VoiceChannel | None:
    voice_state = member.voice

    if voice_state is None:
        return None
    
    voice_channel = voice_state.channel

    if voice_channel is None:
        return None
    
    return cast(discord.VoiceChannel, voice_channel)


async def get_youtube_search_suggestion(ctx: discord.AutocompleteContext) -> list[str]:
    # Minimum 3 characters to get suggestion
    if not ctx.value or len(ctx.value) < 3:
        return []
    
    tracks = await wavelink.YouTubeTrack.search(ctx.value)

    # Return the first five result from the search
    return [ f"{track.title}" for track in tracks[:5] ]
