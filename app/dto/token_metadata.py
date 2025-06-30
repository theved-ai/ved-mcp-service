from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel

class TokenMetadata(BaseModel):
    access_token: str
    refresh_token: str
    expires_at: datetime
    metadata: Optional[dict[str, Any]] = {}