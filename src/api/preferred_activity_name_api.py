from requests import Response

from src.api import BaseAPI


class PreferredActivityNameApi(BaseAPI):
    endpoint: str = "/api/v1/preferred-activity-name"


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
        original_name: str,
        preferred_name: str
    ) -> Response:
        payload = {
            "guild_id": guild_id,
            "original_name": original_name,
            "preferred_name": preferred_name,
        }

        return super().Create(payload=payload)
    

    @classmethod
    def Detail(
        cls,
        guild_id: int,
        original_name: str
    ) -> Response:
        params = {
            "guild_id": guild_id,
            "original_name": original_name,
        }

        return super().Detail(params=params)
    

    @classmethod
    def Edit(
        cls,
        guild_id: int,
        original_name: str,
        preferred_name: str
    ) -> Response:
        params = {
            "guild_id": guild_id,
            "original_name": original_name,
        }

        payload = {
            "preferred_name": preferred_name,
        }

        return super().Edit(params=params, payload=payload)
    

    @classmethod
    def Delete(
        cls,
        guild_id: int,
        original_name: str
    ) -> Response:
        params = {
            "guild_id": guild_id,
            "original_name": original_name,
        }

        return super().Delete(params=params)