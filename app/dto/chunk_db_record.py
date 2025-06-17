from pydantic import BaseModel

class ChunkDbRecord(BaseModel):
    chunk_content: str
    chunk_id: str