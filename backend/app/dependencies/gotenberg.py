from functools import lru_cache
import json
from typing import Annotated, Any

from fastapi import Depends
import httpx

from app.core import AppException, ErrorCode, get_settings


class Gotenberg:
    """
    This class implements the Gotenberg service via http api.
    Official docs: https://gotenberg.dev/
    """

    def __init__(self, api_endpoint: str):
        self.api_endpoint = api_endpoint

    def convert_from_url(
        self, file_url: str, extra_header: dict[str, Any] = None
    ) -> bytes | None:
        download_from = {"url": file_url}
        if extra_header:
            download_from["extraHttpHeaders"] = json.dumps(extra_header)

        download_from_json = json.dumps([download_from])

        files = {"downloadFrom": (None, download_from_json)}

        try:
            with httpx.Client(timeout=300) as client:
                response = client.post(
                    f"{self.api_endpoint}/forms/libreoffice/convert", files=files
                )
                response.raise_for_status()
                return response.content
        except httpx.HTTPError as e1:
            raise AppException(ErrorCode.FILE_UPLOAD_FAILED, str(e1))
        except Exception as e2:
            raise AppException(ErrorCode.FILE_UPLOAD_FAILED, str(e2))


@lru_cache
def get_gotenberg() -> Gotenberg:
    settings = get_settings()
    return Gotenberg(settings.GOTENBERG_ENDPOINT)


GotenbergDep = Annotated[Gotenberg, Depends(get_gotenberg)]
