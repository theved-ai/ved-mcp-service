import asyncio
from typing import List, Optional, Any

from app.config.logging_config import logger
from app.decorators.retry_decorator import async_retryable
from app.utils.application_constants import gcalendar_service_name, gcalendar_service_version
from app.webclients.gsuite.gcalendar.base import GoogleCalendarClientBase
from app.webclients.gsuite.google_service_builder import generate_authenticated_client


class GoogleCalendarClientImpl(GoogleCalendarClientBase):

    @async_retryable()
    async def list_calendars(self, user_uuid: str) -> Any:
        services = await generate_authenticated_client(user_uuid, gcalendar_service_name, gcalendar_service_version)
        for service in services:
            try:
                response = await asyncio.to_thread(
                    service.calendarList().list().execute
                )
                return response.get("items", [])
            except Exception as e:
                logger.error(f"Calendar API error listing calendars: {e}", exc_info=True)
                raise


    @async_retryable()
    async def get_events(self, user_uuid: str, calendar_id: str, time_min: Optional[str], time_max: Optional[str], max_results: int) -> Any:
        services = await generate_authenticated_client(user_uuid, gcalendar_service_name, gcalendar_service_version)
        for service in services:
            try:
                response = await asyncio.to_thread(
                    service.events().list(
                        calendarId=calendar_id,
                        timeMin=time_min,
                        timeMax=time_max,
                        maxResults=max_results,
                        singleEvents=True,
                        orderBy="startTime",
                    ).execute
                )
                return response.get("items", [])
            except Exception as e:
                logger.error(f"Calendar API error getting events: {e}", exc_info=True)
                raise

    @async_retryable()
    async def create_event(self, user_uuid: str, summary: str, start_time: str, end_time: str, calendar_id: str = "primary",
                           description: Optional[str] = None, location: Optional[str] = None, attendees: Optional[List[str]] = None, timezone: Optional[str] = None) -> Any:
        services = await generate_authenticated_client(user_uuid, gcalendar_service_name, gcalendar_service_version)
        for service in services:
            try:
                event_body = {
                    "summary": summary,
                    "start": {"dateTime": start_time} if "T" in start_time else {"date": start_time},
                    "end": {"dateTime": end_time} if "T" in end_time else {"date": end_time},
                }
                if location:
                    event_body["location"] = location
                if description:
                    event_body["description"] = description
                if timezone:
                    if "dateTime" in event_body["start"]:
                        event_body["start"]["timeZone"] = timezone
                    if "dateTime" in event_body["end"]:
                        event_body["end"]["timeZone"] = timezone
                if attendees:
                    event_body["attendees"] = [{"email": email} for email in attendees]
                created_event = await asyncio.to_thread(
                    service.events().insert(calendarId=calendar_id, body=event_body).execute
                )
                return created_event
            except Exception as e:
                logger.error(f"Calendar API error creating event: {e}", exc_info=True)
                raise

    @async_retryable()
    async def modify_event(self, user_uuid: str, event_id: str, calendar_id: str = "primary", summary: Optional[str] = None,
                           start_time: Optional[str] = None, end_time: Optional[str] = None, description: Optional[str] = None,
                           location: Optional[str] = None, attendees: Optional[List[str]] = None, timezone: Optional[str] = None) -> Any:
        services = await generate_authenticated_client(user_uuid, gcalendar_service_name, gcalendar_service_version)
        for service in services:
            try:
                event_body = {}
                if summary is not None:
                    event_body["summary"] = summary
                if start_time is not None:
                    event_body["start"] = {"dateTime": start_time} if "T" in start_time else {"date": start_time}
                    if timezone and "dateTime" in event_body["start"]:
                        event_body["start"]["timeZone"] = timezone
                if end_time is not None:
                    event_body["end"] = {"dateTime": end_time} if "T" in end_time else {"date": end_time}
                    if timezone and "dateTime" in event_body["end"]:
                        event_body["end"]["timeZone"] = timezone
                if description is not None:
                    event_body["description"] = description
                if location is not None:
                    event_body["location"] = location
                if attendees is not None:
                    event_body["attendees"] = [{"email": email} for email in attendees]
                updated_event = await asyncio.to_thread(
                    service.events().update(calendarId=calendar_id, eventId=event_id, body=event_body).execute
                )
                return updated_event
            except Exception as e:
                logger.error(f"Calendar API error modifying event: {e}", exc_info=True)
                raise

    @async_retryable()
    async def delete_event(self, user_uuid: str, event_id: str, calendar_id: str = "primary") -> Any:
        services = await generate_authenticated_client(user_uuid, gcalendar_service_name, gcalendar_service_version)
        for service in services:
            try:
                await asyncio.to_thread(
                    service.events().delete(calendarId=calendar_id, eventId=event_id).execute
                )
                return {"deleted": True, "event_id": event_id}
            except Exception as e:
                logger.error(f"Calendar API error deleting event: {e}", exc_info=True)
                raise
