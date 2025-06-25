
class GoogleAuthReauthRequired(Exception):
    """Custom exception to trigger OAuth flow when refresh token is expired/revoked."""
    pass