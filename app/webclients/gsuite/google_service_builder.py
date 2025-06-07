import datetime
from googleapiclient.discovery import build
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from app.utils.constants import google_client_id_key, google_client_secret_key
from app.webclients.gsuite.google_scopes import SCOPES
from app.service.external_token_service import fetch_external_token_records, update_external_token


async def generate_authenticated_client(user_uuid: str, service_name: str, version: str):
    tokens_data = await fetch_external_token_records(user_uuid, service_name)
    authenticated_google_client = []
    for token_data in tokens_data:
        client = await build_google_service(user_uuid, service_name, version, token_data)
        authenticated_google_client.append(client)

    return authenticated_google_client


async def build_google_service(user_uuid: str, service_name: str, version: str, token_data: dict):
    if token_data["expires_at"] and token_data["expires_at"] < datetime.datetime.utcnow():
        token_data = await refresh_google_access_token(token_data)
        await update_external_token(token_data, service_name, user_uuid)
        return token_data

    creds = generate_google_creds(token_data)
    return build(service_name, version, credentials=creds)


def generate_google_creds(token_data: dict):
    token_metadata = json.loads(token_data["metadata"])
    return Credentials(
        token=token_data["access_token"],
        refresh_token=token_data["refresh_token"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=token_metadata[google_client_id_key],
        client_secret=token_metadata[google_client_secret_key],
        scopes=SCOPES
    )


async def refresh_google_access_token(token_data: dict) -> dict:
    token_metadata = json.loads(token_data["metadata"])
    creds = Credentials(
        token=token_data["access_token"],
        refresh_token=token_data["refresh_token"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=token_metadata[google_client_id_key],
        client_secret=token_metadata[google_client_secret_key],
        scopes=SCOPES
    )
    creds.refresh(Request())
    return {
        "access_token": creds.token,
        "refresh_token": creds.refresh_token,
        "expires_at": creds.expiry
    }