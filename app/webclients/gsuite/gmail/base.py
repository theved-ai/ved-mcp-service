from abc import ABC, abstractmethod
from typing import List, Optional, Literal, Any


class GmailClientBase(ABC):
    @abstractmethod
    async def search_messages(self, user_uuid: str, query: str, page_size: int = 10) -> Any:
        pass

    @abstractmethod
    async def get_message_content(self, user_uuid: str, message_id: str) -> Any:
        pass

    @abstractmethod
    async def get_messages_content_batch(self, user_uuid: str, message_ids: List[str], format: Literal["full", "metadata"] = "full") -> Any:
        pass

    @abstractmethod
    async def send_message(self, user_uuid: str, to: str, subject: str, body: str) -> Any:
        pass

    @abstractmethod
    async def draft_message(self, user_uuid: str, subject: str, body: str, to: Optional[str] = None) -> Any:
        pass

    @abstractmethod
    async def get_thread_content(self, user_uuid: str, thread_id: str) -> Any:
        pass

    @abstractmethod
    async def list_labels(self, user_uuid: str) -> Any:
        pass

    @abstractmethod
    async def manage_label(self, user_uuid: str, action: Literal["create", "update", "delete"], name: Optional[str] = None,
                           label_id: Optional[str] = None, label_list_visibility: Literal["labelShow", "labelHide"] = "labelShow",
                           message_list_visibility: Literal["show", "hide"] = "show") -> Any:
        pass

    @abstractmethod
    async def modify_message_labels(self, user_uuid: str, message_id: str, add_label_ids: Optional[List[str]] = None,
                                    remove_label_ids: Optional[List[str]] = None) -> Any:
        pass
