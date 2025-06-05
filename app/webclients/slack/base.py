from abc import ABC, abstractmethod
from typing import Any
from slack_sdk.web.async_client import AsyncSlackResponse


class SlackClient(ABC):

    @abstractmethod
    async def list_conversations(self, token: str) -> AsyncSlackResponse:
        pass

    @abstractmethod
    async def get_conversation_info(self, token: str, channel_id: str) -> AsyncSlackResponse:
        pass

    @abstractmethod
    async def get_conversation_history(self, token: str, channel_id: str, limit: int) -> AsyncSlackResponse:
        pass

    @abstractmethod
    async def get_conversation_replies(self, token: str, channel_id: str, ts: str) -> AsyncSlackResponse:
        pass

    @abstractmethod
    async def get_user_info(self, token: str, user_id: str) -> AsyncSlackResponse:
        pass

    @abstractmethod
    async def list_users(self, token: str) -> AsyncSlackResponse:
        pass

    @abstractmethod
    async def search_messages_in_conversation(self, request: dict) -> Any:
        pass

    @abstractmethod
    async def get_messages_mentioning_user(self, request: dict) -> Any:
        pass

    @abstractmethod
    async def is_bot_member_of_conversation(self, request: dict) -> Any:
        pass

    @abstractmethod
    async def get_conversation_members(self, request: dict) -> Any:
        pass
