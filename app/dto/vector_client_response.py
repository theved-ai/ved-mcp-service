from datetime import datetime
from typing import Optional, Dict, Any

from pydantic import BaseModel

class VectorClientResponse(BaseModel):
    chunk_id: str
    chunk_data_source: str
    chunk_ingested_at: datetime
    content_timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None
    conversation_id: str
    message_id: str