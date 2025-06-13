from datetime import datetime

from pydantic import BaseModel

class PensieveResponse(BaseModel):
    chunk_content: str
    chunk_data_source: str
    user_ingested_chunk_at: datetime
    chunk_creation_timestamp: datetime
    chunk_metadata: dict
