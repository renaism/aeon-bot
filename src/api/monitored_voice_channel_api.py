from requests import Response

from src.api import BaseAPI


class MonitoredVoiceChannelAPI(BaseAPI):
    endpoint: str = "/api/v1/monitored-voice-channel"


    @classmethod
    def List(
        cls, 
        guild_id: int | None = None
    ) -> Response:
        params = {
            "guild_id": guild_id
        }

        return super().List(params=params)
    

    @classmethod
    def Create(
        cls,
        guild_id: int,
        channel_id: int,
        default_name: str,
        icon: str | None
    ) -> Response:
        payload = {
            "guild_id": guild_id,
            "channel_id": channel_id,
            "default_name": default_name,
            "icon": icon,
        }

        return super().Create(payload=payload)
    

    @classmethod
    def Detail(
        cls,
        guild_id: int,
        channel_id: int
    ) -> Response:
        params = {
            "guild_id": guild_id,
            "channel_id": channel_id,
        }

        return super().Detail(params=params)
    

    @classmethod
    def Edit(
        cls,
        guild_id: int,
        channel_id: int,
        default_name: str | None,
        icon: str | None
    ) -> Response:
        params = {
            "guild_id": guild_id,
            "channel_id": channel_id,
        }

        payload = {
            "default_name": default_name,
            "icon": icon,
        }

        return super().Edit(params=params, payload=payload)
    

    @classmethod
    def Delete(
        cls,
        guild_id: int,
        channel_id: int
    ) -> Response:
        params = {
            "guild_id": guild_id,
            "channel_id": channel_id,
        }

        return super().Delete(params=params)
