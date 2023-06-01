import dataclasses
import datetime
import hmac
import logging
import requests
import secrets

from base64 import b64encode
from hashlib import sha1, sha256
from typing import Optional
from urllib.parse import urlencode


@dataclasses.dataclass
class FitbitClient:
    logger: logging.Logger
    client_id: str
    client_secret: str
    collections: list[str] = dataclasses.field(
        default_factory=lambda: ["activity", "heartrate", "profile", "social"]
    )

    def create_code_verifier() -> str:
        return secrets.token_hex()

    @property
    def signing_key(self) -> str:
        return self.client_secret + "&"

    def verify_signature(self, header_signature: str, json_body: bytes) -> bool:
        digest = hmac.digest(self.signing_key.encode("utf-8"), json_body, sha1)
        b64_encoded = b64encode(digest)
        return header_signature.encode("utf-8") == b64_encoded

    @property
    def authorization_token(self) -> str:
        return b64encode(
            f"{self.client_id}:{self.client_secret}".encode("utf-8")
        ).decode("utf-8")

    def get_token_data(
        self, authorization_code: str, code_verifier: str
    ) -> Optional[dict]:
        url_parameters = urlencode(
            {
                "client_id": self.client_id,
                "code": authorization_code,
                "code_verifier": code_verifier,
                "grant_type": "authorization_code",
            }
        )

        auth_request = requests.post(
            url="https://api.fitbit.com/oauth2/token?" + url_parameters,
            headers={
                "Authorization": f"Basic {self.authorization_token}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data=url_parameters,
        )

        if auth_request.status_code != 200:
            self.logger.warn(
                f"Could not fetch token data. url={auth_request.url}, headers={auth_request.headers}, body={auth_request.text}"
            )
            return None

        return auth_request.json()

    @staticmethod
    def code_challenge_from_verifier(code_verifier: str) -> str:
        return (
            b64encode(sha256(code_verifier.encode("utf-8")).digest())
            .decode("utf-8")
            .rstrip("=")
            .replace("+", "-")
            .replace("/", "_")
        )

    def authorization_url(self, code_verifier: str) -> str:
        url_parameters = {
            "client_id": self.client_id,
            "response_type": "code",
            "code_challenge": self.code_challenge_from_verifier(code_verifier),
            "code_challenge_method": "S256",
            "scope": " ".join(self.collections),
        }
        return "https:///www.fitbit.com/oauth2/authorize?" + urlencode(url_parameters)

    def get_user_daily_activity_summary(
        self, user_id: str, access_token: str, date: datetime.datetime
    ) -> dict:
        formatted_date: str = date.date().strftime("%Y-%m-%d")
        return requests.get(
            f"https://api.fitbit.com/1/user/{user_id}/activities/date/{formatted_date}.json",
            headers={"Authorization": f"Bearer {access_token}"},
        ).json()

    @staticmethod
    def request_indicates_expired_token(response: dict) -> bool:
        return "errors" in response and any(
            e["errorType"] == "expired_token" for e in response["errors"]
        )

    def refresh_user_tokens(self, refresh_token: str) -> dict:
        url_parameters = urlencode(
            {
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            }
        )

        response = requests.post(
            "https://api.fitbit.com/oauth2/token",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Basic {self.authorization_token}",
            },
            data=url_parameters,
        )

        if response.status_code not in (200, 201):
            raise ValueError(f"Error when refreshing user tokens: {response.json()}")

        return response.json()
