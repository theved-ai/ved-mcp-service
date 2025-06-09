from app.utils.tool_util import fetch_user_uuid
from app.mcp_server import server
import logging
from mcp import types
from mcp.server.fastmcp.server import Context
from app.webclients.gsuite.gtasks.gtasks_client import GoogleTasksClientImpl

tasks_client = GoogleTasksClientImpl()
logger = logging.getLogger(__name__)

@server.tool(
    name="list_google_tasklists",
    description=(
            "List all Google Tasklists accessible to the user.\n\n"
            "**Returns:**\n"
            "- List of tasklist titles and IDs."
    )
)
async def list_google_tasklists(ctx: Context) -> types.CallToolResult:
    user_uuid = await fetch_user_uuid(ctx)
    try:
        tasklists = await tasks_client.list_tasklists(user_uuid)
        if not tasklists:
            return types.CallToolResult(content=[types.TextContent(type="text", text="No tasklists found.")])
        lines = []
        for tl in tasklists:
            title = tl.get('title', 'No Title')
            tl_id = tl.get('id', 'Unknown')
            lines.append(f"- {title} (ID: {tl_id})")
        return types.CallToolResult(content=[types.TextContent(type="text", text="\n".join(lines))])
    except Exception as e:
        logger.exception("Error listing Google Tasklists")
        return types.CallToolResult(isError=True, content=[types.TextContent(type="text", text=str(e))])


@server.tool(
    name="get_google_tasklist",
    description=(
            "Get a Google Tasklist by its ID.\n\n"
            "**Returns:**\n"
            "- Tasklist title and details."
    )
)
async def get_google_tasklist(ctx: Context, tasklist_id: str) -> types.CallToolResult:
    user_uuid = await fetch_user_uuid(ctx)
    try:
        tasklist = await tasks_client.get_tasklist(user_uuid, tasklist_id)
        if not tasklist:
            return types.CallToolResult(content=[types.TextContent(type="text", text="Tasklist not found.")])
        title = tasklist.get('title', 'No Title')
        tl_id = tasklist.get('id', 'Unknown')
        updated = tasklist.get('updated', 'Unknown')
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=f"Tasklist: {title}\nID: {tl_id}\nUpdated: {updated}")]
        )
    except Exception as e:
        logger.exception("Error getting Google Tasklist")
        return types.CallToolResult(isError=True, content=[types.TextContent(type="text", text=str(e))])


@server.tool(
    name="list_google_tasks",
    description=(
            "List all tasks in a specified Google Tasklist.\n\n"
            "**Arguments:**\n"
            "- tasklist_id: The ID of the tasklist.\n"
            "- show_completed (optional): Include completed tasks (True/False).\n"
            "- show_hidden (optional): Include hidden tasks (True/False).\n"
            "- show_deleted (optional): Include deleted tasks (True/False).\n"
            "- max_results (optional): Maximum number of results to return.\n"
            "- due_min (optional): Earliest due date (RFC3339 timestamp).\n"
            "- due_max (optional): Latest due date (RFC3339 timestamp).\n"
            "- page_token (optional): Page token for pagination.\n\n"
            "**Returns:**\n"
            "- List of task titles, due dates, and statuses."
    )
)
async def list_google_tasks(
        ctx: Context,
        tasklist_id: str,
        show_completed: bool = None,
        show_hidden: bool = None,
        show_deleted: bool = None,
        max_results: int = None,
        due_min: str = None,
        due_max: str = None,
        page_token: str = None,
) -> types.CallToolResult:
    user_uuid = await fetch_user_uuid(ctx)
    try:
        tasks = await tasks_client.list_tasks(
            user_uuid, tasklist_id, show_completed, show_hidden, show_deleted,
            max_results, due_min, due_max, page_token
        )
        if not tasks:
            return types.CallToolResult(content=[types.TextContent(type="text", text="No tasks found in this tasklist.")])
        lines = []
        for task in tasks:
            title = task.get('title', 'No Title')
            due = task.get('due', 'No Due Date')
            status = task.get('status', 'No Status')
            task_id = task.get('id', 'Unknown')
            lines.append(f"- {title} (ID: {task_id}, Due: {due}, Status: {status})")
        return types.CallToolResult(content=[types.TextContent(type="text", text="\n".join(lines))])
    except Exception as e:
        logger.exception("Error listing Google Tasks")
        return types.CallToolResult(isError=True, content=[types.TextContent(type="text", text=str(e))])



@server.tool(
    name="get_google_task",
    description=(
            "Get a specific Google Task by its ID and the parent tasklist ID.\n\n"
            "**Arguments:**\n"
            "- tasklist_id: The ID of the tasklist.\n"
            "- task_id: The ID of the task.\n\n"
            "**Returns:**\n"
            "- Task title, notes, due date, and status."
    )
)
async def get_google_task(ctx: Context, tasklist_id: str, task_id: str) -> types.CallToolResult:
    user_uuid = await fetch_user_uuid(ctx)
    try:
        task = await tasks_client.get_task(user_uuid, tasklist_id, task_id)
        if not task:
            return types.CallToolResult(content=[types.TextContent(type="text", text="Task not found.")])
        title = task.get('title', 'No Title')
        notes = task.get('notes', 'No Notes')
        due = task.get('due', 'No Due Date')
        status = task.get('status', 'No Status')
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=f"Task: {title}\nStatus: {status}\nDue: {due}\nNotes: {notes}")]
        )
    except Exception as e:
        logger.exception("Error getting Google Task")
        return types.CallToolResult(isError=True, content=[types.TextContent(type="text", text=str(e))])


@server.tool(
    name="create_google_task",
    description=(
            "Create a new Google Task in a specified tasklist.\n\n"
            "**Arguments:**\n"
            "- tasklist_id: The ID of the tasklist.\n"
            "- title: The title of the task.\n"
            "- notes (optional): Notes or description for the task.\n"
            "- due (optional): Due date (RFC3339 timestamp).\n"
            "- status (optional): Task status (e.g., needsAction, completed).\n"
            "- parent (optional): Parent task ID.\n"
            "- previous (optional): Previous sibling task ID."
    )
)
async def create_google_task(
        ctx: Context,
        tasklist_id: str,
        title: str,
        notes: str = None,
        due: str = None,
        status: str = None,
        parent: str = None,
        previous: str = None,
) -> types.CallToolResult:
    user_uuid = await fetch_user_uuid(ctx)
    try:
        task = await tasks_client.create_task(
            user_uuid, tasklist_id, title, notes, due, status, parent, previous
        )
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=f"Task '{title}' created with ID: {task.get('id', 'Unknown')}")]
        )
    except Exception as e:
        logger.exception("Error creating Google Task")
        return types.CallToolResult(isError=True, content=[types.TextContent(type="text", text=str(e))])


@server.tool(
    name="modify_google_task",
    description=(
            "Modify an existing Google Task in a specified tasklist.\n\n"
            "**Arguments:**\n"
            "- tasklist_id: The ID of the tasklist.\n"
            "- task_id: The ID of the task.\n"
            "- title (optional): New title for the task.\n"
            "- notes (optional): Notes or description for the task.\n"
            "- due (optional): Due date (RFC3339 timestamp).\n"
            "- status (optional): Task status (e.g., needsAction, completed).\n"
            "- parent (optional): Parent task ID.\n"
            "- previous (optional): Previous sibling task ID.\n"
            "- completed (optional): Completed timestamp (RFC3339).\n"
            "- deleted (optional): Mark task as deleted (True/False).\n"
            "- hidden (optional): Mark task as hidden (True/False).\n"
            "- position (optional): Task's position."
    )
)
async def modify_google_task(
        ctx: Context,
        tasklist_id: str,
        task_id: str,
        title: str = None,
        notes: str = None,
        due: str = None,
        status: str = None,
        parent: str = None,
        previous: str = None,
        completed: str = None,
        deleted: bool = None,
        hidden: bool = None,
        position: str = None,
) -> types.CallToolResult:
    user_uuid = await fetch_user_uuid(ctx)
    try:
        task = await tasks_client.modify_task(
            user_uuid, tasklist_id, task_id,
            title, notes, due, status, parent, previous,
            completed, deleted, hidden, position
        )
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=f"Task '{task.get('title', 'Unknown')}' updated successfully.")]
        )
    except Exception as e:
        logger.exception("Error modifying Google Task")
        return types.CallToolResult(isError=True, content=[types.TextContent(type="text", text=str(e))])



@server.tool(
    name="delete_google_task",
    description=(
            "Delete a Google Task by its ID from a specified tasklist.\n\n"
            "**Arguments:**\n"
            "- tasklist_id: The ID of the tasklist.\n"
            "- task_id: The ID of the task."
    )
)
async def delete_google_task(ctx: Context, tasklist_id: str, task_id: str) -> types.CallToolResult:
    user_uuid = await fetch_user_uuid(ctx)
    try:
        await tasks_client.delete_task(user_uuid, tasklist_id, task_id)
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=f"Task {task_id} deleted successfully.")]
        )
    except Exception as e:
        logger.exception("Error deleting Google Task")
        return types.CallToolResult(isError=True, content=[types.TextContent(type="text", text=str(e))])
