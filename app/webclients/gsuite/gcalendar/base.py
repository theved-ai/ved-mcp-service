from abc import ABC, abstractmethod
from typing import List, Optional, Any

class GoogleCalendarClientBase(ABC):
    @abstractmethod
    async def list_calendars(self, user_uuid: str) -> Any:
        pass

    @abstractmethod
    async def get_events(self, user_uuid: str, calendar_id: str, time_min: Optional[str], time_max: Optional[str], max_results: int) -> Any:
        pass

    @abstractmethod
    async def create_event(self, user_uuid: str, summary: str, start_time: str, end_time: str, calendar_id: str, description: Optional[str], location: Optional[str], attendees: Optional[List[str]], timezone: Optional[str]) -> Any:
        pass

    @abstractmethod
    async def modify_event(self, user_uuid: str, event_id: str, calendar_id: str, summary: Optional[str], start_time: Optional[str], end_time: Optional[str], description: Optional[str], location: Optional[str], attendees: Optional[List[str]], timezone: Optional[str]) -> Any:
        pass

    @abstractmethod
    async def delete_event(self, user_uuid: str, event_id: str, calendar_id: str) -> Any:
        pass
