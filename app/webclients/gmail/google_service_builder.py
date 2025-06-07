import datetime
import os

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from app.utils.google_auth import refresh_google_access_token
from app.db.db_reader import update_token_by_user
from app.utils.user_client_token_util import fetch_user_token_records
from app.webclients.gmail.google_scopes import SCOPES
from app.utils.token_encryption import encrypt_token


async def generate_authenticated_client(user_uuid: str, service_name: str, version: str):
    tokens_data = await fetch_user_token_records(user_uuid, service_name)

    authenticated_google_client = []
    for token_data in tokens_data:
        client = await build_google_service(user_uuid, service_name, version, token_data)
        authenticated_google_client.append(client)

    return authenticated_google_client

async def build_google_service(user_uuid: str, service_name: str, version: str, token_data: dict):
    """
    Builds and returns an authenticated Google service client.
    Refreshes token if expired and updates DB.

    Args:
        user_uuid (str): ID of the user
        service_name (str): Google API service, e.g., 'gmail'
        version (str): API version
        token_data (dict): Fetched from DB

    Returns:
        googleapiclient.discovery.Resource
    """
    # Check if expired
    if token_data["expires_at"] and token_data["expires_at"] < datetime.datetime.utcnow():
        token_data = await refresh_google_access_token(token_data)
        token_data_encrypted = {
            "access_token": encrypt_token(token_data["access_token"]) if token_data["access_token"] else None,
            "refresh_token": encrypt_token(token_data["refresh_token"]) if token_data["refresh_token"] else None,
            "expiry": token_data["expiry"]
        }
        await update_token_by_user(user_uuid, token_data_encrypted, service_name)

    creds = Credentials(
        token=token_data["access_token"],
        refresh_token=token_data["refresh_token"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        scopes=SCOPES
    )

    return build(service_name, version, credentials=creds)
