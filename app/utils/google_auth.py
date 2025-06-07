import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from app.webclients.gmail.google_scopes import SCOPES

async def refresh_google_access_token(token_data: dict) -> dict:
    """
    Refreshes an expired access token using the refresh token.

    Args:
        token_data (dict): Contains access_token, refresh_token, scopes, etc.

    Returns:
        dict: Updated token data including access_token and expiry.
    """
    creds = Credentials(
        token=token_data["access_token"],
        refresh_token=token_data["refresh_token"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        scopes=SCOPES,
        account=''
    )

    creds.refresh(Request())

    return {
        "access_token": creds.token,
        "refresh_token": creds.refresh_token,
        "expiry": creds.expiry
    }
