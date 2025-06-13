from typing import Any, Optional

from pydantic import BaseModel

class PensieveRequest(BaseModel):
    user_prompt: str
    user_id: str
    metadata: Optional[dict[str, Any]] = None