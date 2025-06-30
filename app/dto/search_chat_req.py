from pydantic import BaseModel

class SearchChatRequest(BaseModel):
    conversation_id: str
    user_id: str
    max_messages: int = 1