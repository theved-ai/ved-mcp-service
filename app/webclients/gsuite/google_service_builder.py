import datetime
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.exceptions import RefreshError

from app.exceptions.GoogleAuthReauthRequired import GoogleAuthReauthRequired
from app.service.external_token_service import fetch_external_token_records, update_external_token
from app.utils.constants import google_client_id_key, google_client_secret_key, google_external_client
from app.utils.google_oauth_utils import run_local_oauth_flow
from app.webclients.gsuite.google_scopes import SCOPES
from app.config.logging_config import logger


async def generate_authenticated_client(user_uuid: str, service_name: str, version: str):
    tokens_data = await fetch_external_token_records(user_uuid, google_external_client)
    authenticated_google_client = []
    for token_data in tokens_data:
        client = await build_google_service(user_uuid, service_name, version, token_data)
        authenticated_google_client.append(client)

    return authenticated_google_client


async def build_google_service(user_uuid: str, service_name: str, version: str, token_data: dict):
    if token_data["expires_at"] and token_data["expires_at"] < datetime.datetime.utcnow():
        token_data = await refresh_google_access_token(token_data, user_uuid)
        await update_external_token(token_data, google_external_client, user_uuid)
        return token_data

    creds = generate_google_creds(token_data)
    return build(service_name, version, credentials=creds)


def generate_google_creds(token_data: dict):
    return Credentials(
        token=token_data["access_token"],
        refresh_token=token_data["refresh_token"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv(google_client_id_key),
        client_secret=os.getenv(google_client_secret_key),
        scopes=SCOPES
    )


async def refresh_google_access_token(token_data: dict, user_uuid: str) -> dict:
    creds = generate_google_creds(token_data)
    try:
        creds.refresh(Request())
        return {
            "access_token": creds.token,
            "refresh_token": creds.refresh_token,
            "expires_at": creds.expiry
        }
    except RefreshError as e:
        if "invalid_grant" in str(e):
            logger.warning(f"Refresh token expired or revoked for user {user_uuid}")
            if os.environ.get("APP_ENV") in ("local", "test"):
                new_tokens = run_local_oauth_flow(SCOPES)
                await update_external_token(new_tokens, google_external_client, user_uuid)
                return new_tokens
            raise GoogleAuthReauthRequired("Google refresh token expired or revoked; user must re-authorize.") from e
        raise