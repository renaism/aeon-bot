import discord
import re
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


def timestamp_to_seconds(timestamp: str) -> int | None:
    mm_ss = r"^([0-9]+):([0-9]+)$"
    hh_mm_ss =  r"^([0-9]+):([0-9]+):([0-9]+)$"

    # Match MM:SS format
    re_match = re.match(mm_ss, timestamp)

    if re_match:
        minutes = int(re_match.group(1))
        seconds = int(re_match.group(2))
        
        return minutes * 60 + seconds
    
    # Match HH:MM:SS format
    re_match = re.match(hh_mm_ss, timestamp)

    if re_match:
        hours = int(re_match.group(1))
        minutes = int(re_match.group(2))
        seconds = int(re_match.group(3))
    
        return hours * 3600 + minutes * 60 + seconds
    
    return None


async def get_youtube_search_suggestion(ctx: discord.AutocompleteContext) -> list[str]:
    # Minimum 3 characters to get suggestion
    if not ctx.value or len(ctx.value) < 3:
        return []
    
    tracks = await wavelink.YouTubeTrack.search(ctx.value)

    # Return the first five result from the search
    return [ f"{track.title}" for track in tracks[:5] ]
