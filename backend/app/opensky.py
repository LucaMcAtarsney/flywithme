from dotenv import load_dotenv
import httpx
import os
import time

TOKEN_URL = "https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token"
ROOT_URL = "https://opensky-network.org/api"

class TokenManager:
    def __init__(self, client_id: str, client_secret: str, margin: int = 60):
        self.client_id = client_id
        self.client_secret = client_secret
        self.margin = margin
        self._token = None
        self._expires_at = 0.0

    def _fetch(self) -> None:
        print("fetching...")
        r = httpx.post(TOKEN_URL, data={
                        "grant_type": "client_credentials",
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                    },
                    timeout=10.0
                )

        # raises exception if error
        r.raise_for_status()

        data = r.json()
        self._token = data["access_token"]
        self._expires_at = time.monotonic() + data["expires_in"]

    def get(self) -> str:
        if self._token is None or time.monotonic() > self._expires_at - self.margin:
            self._fetch()

        return self._token


def get_states(token: str) -> list[list]:
    GET_STATES = ROOT_URL + "/states/all"
    r = httpx.get(
        GET_STATES,
        headers={"Authorization": f"Bearer {token}"},
        timeout=10.0)

    r.raise_for_status()
    return r.json()["states"] or []