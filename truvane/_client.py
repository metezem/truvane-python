from __future__ import annotations

import os
from pathlib import Path
from typing import BinaryIO

import httpx

from ._exceptions import (
    TruvaneAPIError,
    TruvaneAuthError,
    TruvaneRateLimitError,
    TruvaneValidationError,
)
from ._models import VerifyResult

DEFAULT_BASE_URL = "https://xmqhzmzs57.execute-api.us-east-1.amazonaws.com/prod"


def _resolve_api_key(api_key: str | None) -> str:
    api_key = api_key or os.environ.get("TRUVANE_API_KEY")
    if not api_key:
        raise ValueError("api_key is required (pass explicitly or set TRUVANE_API_KEY)")
    return api_key


def _read_image(image: bytes | BinaryIO | str | Path) -> bytes:
    if isinstance(image, bytes):
        return image
    if isinstance(image, (str, Path)):
        return Path(image).read_bytes()
    # A stream left at the end of its data (e.g. immediately after writing
    # to it) reads as empty rather than raising — rewind defensively.
    if image.seekable():
        image.seek(0)
    return image.read()


def _check_args(image: object, image_url: object) -> None:
    if (image is None) == (image_url is None):
        raise ValueError("provide exactly one of image or image_url")


def _raise_for_status(response: httpx.Response) -> None:
    if response.status_code < 400:
        return
    try:
        detail = response.json().get("detail", response.text)
    except Exception:
        detail = response.text
    if response.status_code in (401, 403):
        # 401: our app rejected the key. 403: API Gateway rejected it before
        # the request ever reached the app (missing, unrecognized, or
        # disabled key). Both mean the same thing to an SDK consumer.
        raise TruvaneAuthError(detail)
    if response.status_code == 429:
        raise TruvaneRateLimitError(detail)
    if response.status_code in (413, 422):
        raise TruvaneValidationError(detail)
    raise TruvaneAPIError(detail, status_code=response.status_code)


class TruvaneClient:
    """Synchronous client for the Truvane image forensics API."""

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
    ):
        self._api_key = _resolve_api_key(api_key)
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    def verify(
        self,
        image: bytes | BinaryIO | str | Path | None = None,
        *,
        image_url: str | None = None,
        filename: str = "image.jpg",
    ) -> VerifyResult:
        """Submit a photo for authenticity verification.

        Provide exactly one of `image` (bytes, a file-like object, or a
        path to a file on disk) or `image_url` (a public HTTPS URL).
        """
        _check_args(image, image_url)
        headers = {"X-API-Key": self._api_key}

        with httpx.Client(timeout=self._timeout) as client:
            if image_url is not None:
                response = client.post(
                    f"{self._base_url}/api/v1/verify", headers=headers, data={"image_url": image_url}
                )
            else:
                response = client.post(
                    f"{self._base_url}/api/v1/verify",
                    headers=headers,
                    files={"image": (filename, _read_image(image), "application/octet-stream")},
                )

        _raise_for_status(response)
        return VerifyResult._from_json(response.json())


class AsyncTruvaneClient:
    """Asynchronous client for the Truvane image forensics API."""

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
    ):
        self._api_key = _resolve_api_key(api_key)
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    async def verify(
        self,
        image: bytes | BinaryIO | str | Path | None = None,
        *,
        image_url: str | None = None,
        filename: str = "image.jpg",
    ) -> VerifyResult:
        """Submit a photo for authenticity verification.

        Provide exactly one of `image` (bytes, a file-like object, or a
        path to a file on disk) or `image_url` (a public HTTPS URL).
        """
        _check_args(image, image_url)
        headers = {"X-API-Key": self._api_key}

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            if image_url is not None:
                response = await client.post(
                    f"{self._base_url}/api/v1/verify", headers=headers, data={"image_url": image_url}
                )
            else:
                response = await client.post(
                    f"{self._base_url}/api/v1/verify",
                    headers=headers,
                    files={"image": (filename, _read_image(image), "application/octet-stream")},
                )

        _raise_for_status(response)
        return VerifyResult._from_json(response.json())
