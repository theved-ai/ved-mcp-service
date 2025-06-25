import os

from google_auth_oauthlib.flow import InstalledAppFlow


def run_local_oauth_flow(scopes):
    """
    Runs the OAuth consent flow for local development/testing using client ID and secret from environment variables.
    """
    client_id = os.getenv("GOOGLE_CLIENT_ID")  # or your google_client_id_key variable
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")  # or your google_client_secret_key variable
    if not client_id or not client_secret:
        raise Exception("Google client ID or secret not set in environment variables.")

    # Build the client_config dict as expected by from_client_config
    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [
                "urn:ietf:wg:oauth:2.0:oob",
                "http://localhost"
            ]
        }
    }

    flow = InstalledAppFlow.from_client_config(
        client_config,
        scopes=scopes
    )
    creds = flow.run_local_server(port=0)
    return {
        "access_token": creds.token,
        "refresh_token": creds.refresh_token,
        "expires_at": creds.expiry
    }
