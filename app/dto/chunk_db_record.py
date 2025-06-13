from pydantic import BaseModel

class ChunkDbRecord(BaseModel):
    chunk_content: str