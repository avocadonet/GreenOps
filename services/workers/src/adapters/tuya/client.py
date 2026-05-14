"""
Tuya Cloud OpenAPI HTTP client.

Authentication
--------------
Tuya uses a two-step scheme:
  1. Exchange (client_id, client_secret) for a short-lived access_token.
  2. Sign every subsequent request with HMAC-SHA256.

Signature algorithm (sign_method = HMAC-SHA256):
  string_to_sign = client_id + access_token + timestamp + nonce
                   + "\n" + method + "\n" + sha256(body) + "\n"
                   + sha256(query_string) + "\n" + path
  sign = HMAC-SHA256(string_to_sign, client_secret).upper()

Regions
-------
  EU : https://openapi.tuyaeu.com
  US : https://openapi.tuyaus.com
  CN : https://openapi.tuyacn.com
  IN : https://openapi.tuyain.com

References
----------
  https://developer.tuya.com/en/docs/iot/new-singnature?id=Kbw0q34cs2e5g
  https://developer.tuya.com/en/docs/iot/device-status?id=Kb0aaj42iitss
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import time
import uuid
from typing import Any

logger = logging.getLogger(__name__)

_TOKEN_PATH = "/v1.0/token?grant_type=1"
_DEVICE_STATUS_PATH = "/v1.0/devices/{device_id}/status"
_DEVICE_FUNCTIONS_PATH = "/v1.0/devices/{device_id}/functions"


class TuyaAPIError(Exception):
    pass


class TuyaClient:
    """
    Async client for the Tuya OpenAPI (cloud-to-cloud).

    Parameters
    ----------
    client_id     Tuya IoT project Access ID
    client_secret Tuya IoT project Access Secret
    base_url      Regional API endpoint (default: EU)
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        base_url: str = "https://openapi.tuyaeu.com",
    ) -> None:
        self._client_id = client_id
        self._client_secret = client_secret
        self._base_url = base_url.rstrip("/")
        self._access_token: str = ""
        self._token_expire_at: float = 0.0
        self._session: object | None = None

    # ── lifecycle ─────────────────────────────────────────────────────────────

    async def open(self) -> None:
        try:
            import aiohttp as _aiohttp
        except ImportError as exc:
            raise RuntimeError(
                "aiohttp is required for the Tuya adapter: pip install aiohttp"
            ) from exc
        self._session = _aiohttp.ClientSession()
        await self._refresh_token()

    async def close(self) -> None:
        if self._session:
            await self._session.close()
            self._session = None

    # ── public API ────────────────────────────────────────────────────────────

    async def get_device_status(self, device_id: str) -> list[dict]:
        """
        Return the current status of a device as a list of data-point dicts.

        Example response item:
            {"code": "cur_power",   "value": 4500}  # 0.1 W — divide by 10 for W
            {"code": "cur_current", "value": 2050}  # mA   — divide by 1000 for A
            {"code": "cur_voltage", "value": 2200}  # 0.1 V — divide by 10 for V
            {"code": "add_ele",     "value": 12.34} # kWh (accumulated energy)
        """
        path = _DEVICE_STATUS_PATH.format(device_id=device_id)
        data = await self._get(path)
        return data.get("result", [])

    # ── signing helpers ───────────────────────────────────────────────────────

    def _sign(
        self,
        method: str,
        path: str,
        body: str = "",
        access_token: str = "",
    ) -> tuple[str, str, str]:
        """Returns (sign, timestamp, nonce)."""
        timestamp = str(int(time.time() * 1000))
        nonce = uuid.uuid4().hex

        body_hash = hashlib.sha256(body.encode()).hexdigest()
        query = path.split("?", 1)[1] if "?" in path else ""
        path_clean = path.split("?", 1)[0]
        query_hash = hashlib.sha256(query.encode()).hexdigest()

        string_to_sign = (
            f"{self._client_id}{access_token}{timestamp}{nonce}"
            f"\n{method.upper()}\n{body_hash}\n{query_hash}\n{path_clean}"
        )
        sign = (
            hmac.new(
                self._client_secret.encode(),
                string_to_sign.encode(),
                hashlib.sha256,
            )
            .hexdigest()
            .upper()
        )

        return sign, timestamp, nonce

    def _headers(
        self,
        method: str,
        path: str,
        body: str = "",
        with_token: bool = True,
    ) -> dict:
        token = self._access_token if with_token else ""
        sign, ts, nonce = self._sign(method, path, body, token)
        return {
            "client_id": self._client_id,
            "access_token": token,
            "sign": sign,
            "t": ts,
            "nonce": nonce,
            "sign_method": "HMAC-SHA256",
            "Content-Type": "application/json",
        }

    # ── HTTP helpers ──────────────────────────────────────────────────────────

    async def _get(self, path: str) -> dict[str, Any]:
        await self._ensure_token()
        url = self._base_url + path
        headers = self._headers("GET", path)
        assert self._session is not None
        async with self._session.get(url, headers=headers) as resp:
            payload = await resp.json()
        if not payload.get("success"):
            raise TuyaAPIError(
                f"GET {path} failed: code={payload.get('code')} msg={payload.get('msg')}"
            )
        return payload

    async def _refresh_token(self) -> None:
        url = self._base_url + _TOKEN_PATH
        headers = self._headers("GET", _TOKEN_PATH, with_token=False)
        assert self._session is not None
        async with self._session.get(url, headers=headers) as resp:
            payload = await resp.json()
        if not payload.get("success"):
            raise TuyaAPIError(f"Token request failed: {payload}")
        result = payload["result"]
        self._access_token = result["access_token"]
        self._token_expire_at = time.time() + result.get("expire_time", 7200) - 60
        logger.debug(
            "[tuya] token refreshed, expires in %ss", result.get("expire_time")
        )

    async def _ensure_token(self) -> None:
        if time.time() >= self._token_expire_at:
            await self._refresh_token()
