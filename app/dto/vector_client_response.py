from datetime import datetime
from typing import Optional

from pydantic import BaseModel

class VectorClientResponse(BaseModel):
    chunk_id: str
    chunk_data_source: str
    chunk_ingested_at: datetime
    content_timestamp: datetime
    metadata: Optional[dict] = None