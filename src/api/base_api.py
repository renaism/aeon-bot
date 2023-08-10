import logging
import requests

from abc import ABC
from requests import Response
from requests.exceptions import RequestException

from config import APIConfig


_log = logging.getLogger(__name__)


class BaseAPI(ABC):
    endpoint: str = ""
    headers: dict = {
        "Access-Token": APIConfig.KEY,
    }


    @staticmethod
    def Request(
        method: str,
        url: str,
        headers: dict,
        params: dict | None = None,
        payload: dict | None = None
    ) -> Response:
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=payload,
            )

            response.raise_for_status()
        except RequestException as err:
            res_data = err.response.json() if err.response is not None else None

            _log.exception(
                "Unsuccessful API Request"
                + f"\n\tParams: {params}"
                + f"\n\tPayload: {payload}"
                + f"\n\tResponse: {res_data}"
            )

            return err.response
        
        return response


    @classmethod
    def List(
        cls, 
        params: dict | None = None
    ) -> Response:
        url = f"{APIConfig.URL}{cls.endpoint}/list"

        return cls.Request(
            method="GET",
            url=url,
            headers=cls.headers,
            params=params,
        )


    @classmethod
    def Create(
        cls,
        params: dict | None = None,
        payload: dict | None = None
    ) -> Response:
        url = f"{APIConfig.URL}{cls.endpoint}/create"

        return cls.Request(
            method="POST",
            url=url,
            headers=cls.headers,
            params=params,
            payload=payload,
        )


    @classmethod
    def Detail(
        cls,
        params: dict | None = None
    ) -> Response:
        url = f"{APIConfig.URL}{cls.endpoint}/detail"

        return cls.Request(
            method="GET",
            url=url,
            headers=cls.headers,
            params=params,
        )


    @classmethod
    def Edit(
        cls,
        params: dict | None = None,
        payload: dict | None = None
    ) -> Response:
        url = f"{APIConfig.URL}{cls.endpoint}/edit"
        
        return cls.Request(
            method="PUT",
            url=url,
            headers=cls.headers,
            params=params,
            payload=payload,
        )


    @classmethod
    def Delete(
        cls,
        params: dict | None = None
    ) -> Response:
        url = f"{APIConfig.URL}{cls.endpoint}/delete"

        return cls.Request(
            method="DELETE",
            url=url,
            headers=cls.headers,
            params=params,
        )