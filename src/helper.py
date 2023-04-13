import discord

from typing import cast

def get_member_voice_channel(member: discord.Member) -> discord.VoiceChannel | None:
    voice_state = member.voice

    if voice_state is None:
        return None
    
    voice_channel = voice_state.channel

    if voice_channel is None:
        return None
    
    return cast(discord.VoiceChannel, voice_channel)
