import logging
from mcp import types
from mcp.server.fastmcp.server import Context
from app.webclients.gsuite.gcalendar.gcal_client import GoogleCalendarClientImpl
from app.utils.tool_util import fetch_user_uuid
from app.mcp_server import server

logger = logging.getLogger(__name__)
calendar_client = GoogleCalendarClientImpl()

@server.tool(
    name="list_google_calendars",
    description=(
            "List all Google Calendars accessible to the user.\n\n"
            "**Returns:**\n"
            "- List of calendar names, IDs, and primary status."
    )
)
async def list_google_calendars(ctx: Context) -> types.CallToolResult:
    user_uuid = await fetch_user_uuid(ctx)
    try:
        calendars = await calendar_client.list_calendars(user_uuid)
        if not calendars:
            return types.CallToolResult(content=[types.TextContent(type="text", text="No calendars found.")])
        lines = []
        for cal in calendars:
            summary = cal.get('summary', 'No Summary')
            cal_id = cal.get('id', 'Unknown')
            is_primary = " (Primary)" if cal.get('primary') else ""
            lines.append(f"- {summary}{is_primary} (ID: {cal_id})")
        return types.CallToolResult(content=[types.TextContent(type="text", text="\n".join(lines))])
    except Exception as e:
        logger.exception("Error listing Google Calendars")
        return types.CallToolResult(isError=True, content=[types.TextContent(type="text", text=str(e))])


@server.tool(
    name="get_google_calendar_events",
    description=(
            "Get upcoming events from a specified Google Calendar.\n\n"
            "**Parameters:**\n"
            "- `calendar_id` (str): Calendar ID (default: 'primary').\n"
            "- `time_min` (str, optional): RFC3339 start datetime. If omitted, defaults to now.\n"
            "- `time_max` (str, optional): RFC3339 end datetime. If omitted, gets upcoming events only.\n"
            "- `max_results` (int): Max number of results (default 25).\n\n"
            "**Returns:**\n"
            "- List of event summaries, times, and links."
    )
)
async def get_google_calendar_events(
        ctx: Context,
        calendar_id: str = "primary",
        time_min: str = None,
        time_max: str = None,
        max_results: int = 25
) -> types.CallToolResult:
    user_uuid = await fetch_user_uuid(ctx)
    try:
        events = await calendar_client.get_events(user_uuid, calendar_id, time_min, time_max, max_results)
        if not events:
            return types.CallToolResult(content=[types.TextContent(type="text", text="No events found.")])
        lines = []
        for e in events:
            summary = e.get('summary', 'No Title')
            start = e['start'].get('dateTime', e['start'].get('date', ''))
            link = e.get('htmlLink', '')
            lines.append(f'- "{summary}" (Starts: {start}) | Link: {link}')
        return types.CallToolResult(content=[types.TextContent(type="text", text="\n".join(lines))])
    except Exception as e:
        logger.exception("Error getting Google Calendar events")
        return types.CallToolResult(isError=True, content=[types.TextContent(type="text", text=str(e))])


@server.tool(
    name="create_google_calendar_event",
    description=(
            "Create a new event in the user's Google Calendar.\n\n"
            "**Parameters:**\n"
            "- `summary` (str): Event title.\n"
            "- `start_time` (str): RFC3339 start datetime.\n"
            "- `end_time` (str): RFC3339 end datetime.\n"
            "- `calendar_id` (str): Calendar ID (default: 'primary').\n"
            "- `description` (str, optional): Description.\n"
            "- `location` (str, optional): Location.\n"
            "- `attendees` (list[str], optional): Email addresses.\n"
            "- `timezone` (str, optional): Timezone, e.g., 'America/New_York'.\n\n"
            "**Returns:**\n"
            "- Confirmation message with event link."
    )
)
async def create_google_calendar_event(
        ctx: Context,
        summary: str,
        start_time: str,
        end_time: str,
        calendar_id: str = "primary",
        description: str = None,
        location: str = None,
        attendees: list = None,
        timezone: str = None,
) -> types.CallToolResult:
    user_uuid = await fetch_user_uuid(ctx)
    try:
        event = await calendar_client.create_event(
            user_uuid, summary, start_time, end_time, calendar_id, description, location, attendees, timezone
        )
        link = event.get("htmlLink", "No link available")
        confirmation = f"Event '{event.get('summary', summary)}' created. Link: {link}"
        return types.CallToolResult(content=[types.TextContent(type="text", text=confirmation)])
    except Exception as e:
        logger.exception("Error creating Google Calendar event")
        return types.CallToolResult(isError=True, content=[types.TextContent(type="text", text=str(e))])


@server.tool(
    name="modify_google_calendar_event",
    description=(
            "Modify an existing event in the user's Google Calendar.\n\n"
            "**Parameters:**\n"
            "- `event_id` (str): The ID of the event.\n"
            "- `calendar_id` (str): Calendar ID (default: 'primary').\n"
            "- `summary`, `start_time`, `end_time`, `description`, `location`, `attendees`, `timezone`: Any to update.\n\n"
            "**Returns:**\n"
            "- Confirmation message with updated event link."
    )
)
async def modify_google_calendar_event(
        ctx: Context,
        event_id: str,
        calendar_id: str = "primary",
        summary: str = None,
        start_time: str = None,
        end_time: str = None,
        description: str = None,
        location: str = None,
        attendees: list = None,
        timezone: str = None,
) -> types.CallToolResult:
    user_uuid = await fetch_user_uuid(ctx)
    try:
        event = await calendar_client.modify_event(
            user_uuid, event_id, calendar_id, summary, start_time, end_time, description, location, attendees, timezone
        )
        link = event.get("htmlLink", "No link available")
        confirmation = f"Event updated. Link: {link}"
        return types.CallToolResult(content=[types.TextContent(type="text", text=confirmation)])
    except Exception as e:
        logger.exception("Error modifying Google Calendar event")
        return types.CallToolResult(isError=True, content=[types.TextContent(type="text", text=str(e))])


@server.tool(
    name="delete_google_calendar_event",
    description=(
            "Delete an event from the user's Google Calendar.\n\n"
            "**Parameters:**\n"
            "- `event_id` (str): The ID of the event.\n"
            "- `calendar_id` (str): Calendar ID (default: 'primary').\n\n"
            "**Returns:**\n"
            "- Confirmation message."
    )
)
async def delete_google_calendar_event(
        ctx: Context,
        event_id: str,
        calendar_id: str = "primary",
) -> types.CallToolResult:
    user_uuid = await fetch_user_uuid(ctx)
    try:
        result = await calendar_client.delete_event(user_uuid, event_id, calendar_id)
        confirmation = f"Event (ID: {event_id}) deleted." if result.get("deleted") else "Delete failed."
        return types.CallToolResult(content=[types.TextContent(type="text", text=confirmation)])
    except Exception as e:
        logger.exception("Error deleting Google Calendar event")
        return types.CallToolResult(isError=True, content=[types.TextContent(type="text", text=str(e))])
