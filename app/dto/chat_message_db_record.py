from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

class ChatMessageDbRecord(BaseModel):
    message_id: UUID
    conversation_id: UUID
    content: str
    tools_called: str
    model_metadata_id: int
    created_at: datetime
    updated_at: datetime