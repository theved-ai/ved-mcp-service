import json
import logging
from typing import List, Optional, Literal
from mcp import types
from mcp.server.fastmcp.server import Context
from app.mcp_server import server
from app.webclients.gmail.gmail_client import GmailClientImpl
from app.utils.user_client_token_util import fetch_user_uuid

gmail_client = GmailClientImpl()
logger = logging.getLogger(__name__)


@server.tool(
    name="search_gmail_messages",
    description=(
            "Search messages in user's Gmail for a given query string.\n\n"
            "**Parameters:**\n"
            "- `query` (str): Gmail search query string (supports standard Gmail search syntax).\n"
            "- `page_size` (int): Max number of results (default 10).\n\n"
            "**Returns:**\n"
            "- List of matching message IDs."
    )
)
async def search_gmail_messages(ctx: Context, query: str, page_size: int = 10) -> types.CallToolResult:
    user_uuid = await fetch_user_uuid(ctx)
    try:
        messages = await gmail_client.search_messages(user_uuid, query, page_size)
        msg_ids = [msg["id"] for msg in messages] if messages else []
        text = f"Found {len(msg_ids)} message(s):\n" + "\n".join(msg_ids) if msg_ids else "No messages found."
        return types.CallToolResult(content=[types.TextContent(type="text", text=text)])
    except Exception as e:
        logger.exception("Error searching Gmail messages")
        return types.CallToolResult(isError=True, content=[types.TextContent(type="text", text=str(e))])

@server.tool(
    name="get_gmail_message_content",
    description=(
            "Get full content of a Gmail message by ID.\n\n"
            "**Parameters:**\n"
            "- `message_id` (str): Gmail message ID.\n\n"
            "**Returns:**\n"
            "- Message subject, sender, body and web URL."
    )
)
async def get_gmail_message_content(ctx: Context, message_id: str) -> types.CallToolResult:
    user_uuid = await fetch_user_uuid(ctx)
    try:
        msg = await gmail_client.get_message_content(user_uuid, message_id)
        text = json.dumps(msg, indent=2)
        return types.CallToolResult(content=[types.TextContent(type="text", text=text)])
    except Exception as e:
        logger.exception("Error getting Gmail message content")
        return types.CallToolResult(isError=True, content=[types.TextContent(type="text", text=str(e))])

@server.tool(
    name="get_gmail_messages_content_batch",
    description=(
            "Get content for multiple Gmail messages by their IDs.\n\n"
            "**Parameters:**\n"
            "- `message_ids` (List[str]): List of Gmail message IDs.\n"
            "- `format` (Literal['full','metadata']): Whether to return full message (with body) or only headers.\n\n"
            "**Returns:**\n"
            "- List of message info dictionaries."
    )
)
async def get_gmail_messages_content_batch(ctx: Context, message_ids: List[str], format: Literal["full", "metadata"] = "full") -> types.CallToolResult:
    user_uuid = await fetch_user_uuid(ctx)
    try:
        msgs = await gmail_client.get_messages_content_batch(user_uuid, message_ids, format)
        text = json.dumps(msgs, indent=2)
        return types.CallToolResult(content=[types.TextContent(type="text", text=text)])
    except Exception as e:
        logger.exception("Error getting Gmail messages content batch")
        return types.CallToolResult(isError=True, content=[types.TextContent(type="text", text=str(e))])

@server.tool(
    name="send_gmail_message",
    description=(
            "Send an email using the user's Gmail account.\n\n"
            "**Parameters:**\n"
            "- `to` (str): Recipient email address.\n"
            "- `subject` (str): Email subject.\n"
            "- `body` (str): Email body (plain text).\n\n"
            "**Returns:**\n"
            "- ID of sent Gmail message."
    )
)
async def send_gmail_message(ctx: Context, to: str, subject: str, body: str) -> types.CallToolResult:
    user_uuid = await fetch_user_uuid(ctx)
    try:
        message_id = await gmail_client.send_message(user_uuid, to, subject, body)
        return types.CallToolResult(content=[types.TextContent(type="text", text=f"Email sent! Message ID: {message_id}")])
    except Exception as e:
        logger.exception("Error sending Gmail message")
        return types.CallToolResult(isError=True, content=[types.TextContent(type="text", text=str(e))])

@server.tool(
    name="draft_gmail_message",
    description=(
            "Create a draft email in user's Gmail account.\n\n"
            "**Parameters:**\n"
            "- `subject` (str): Email subject.\n"
            "- `body` (str): Email body (plain text).\n"
            "- `to` (str, optional): Recipient email address.\n\n"
            "**Returns:**\n"
            "- ID of created Gmail draft."
    )
)
async def draft_gmail_message(ctx: Context, subject: str, body: str, to: Optional[str] = None) -> types.CallToolResult:
    user_uuid = await fetch_user_uuid(ctx)
    try:
        draft_id = await gmail_client.draft_message(user_uuid, subject, body, to)
        return types.CallToolResult(content=[types.TextContent(type="text", text=f"Draft created! Draft ID: {draft_id}")])
    except Exception as e:
        logger.exception("Error creating Gmail draft")
        return types.CallToolResult(isError=True, content=[types.TextContent(type="text", text=str(e))])

@server.tool(
    name="get_gmail_thread_content",
    description=(
            "Get the complete content of a Gmail conversation thread, including all messages.\n\n"
            "**Parameters:**\n"
            "- `thread_id` (str): Gmail thread ID.\n\n"
            "**Returns:**\n"
            "- List of messages in the thread."
    )
)
async def get_gmail_thread_content(ctx: Context, thread_id: str) -> types.CallToolResult:
    user_uuid = await fetch_user_uuid(ctx)
    try:
        thread_content = await gmail_client.get_thread_content(user_uuid, thread_id)
        text = json.dumps(thread_content, indent=2)
        return types.CallToolResult(content=[types.TextContent(type="text", text=text)])
    except Exception as e:
        logger.exception("Error getting Gmail thread content")
        return types.CallToolResult(isError=True, content=[types.TextContent(type="text", text=str(e))])

@server.tool(
    name="list_gmail_labels",
    description=(
            "List all labels in the user's Gmail account.\n\n"
            "**Returns:**\n"
            "- List of label dictionaries (ID, name, type, etc)."
    )
)
async def list_gmail_labels(ctx: Context) -> types.CallToolResult:
    user_uuid, resolved_email = await fetch_user_uuid(ctx)
    try:
        labels = await gmail_client.list_labels(user_uuid)
        text = json.dumps(labels, indent=2)
        return types.CallToolResult(content=[types.TextContent(type="text", text=text)])
    except Exception as e:
        logger.exception("Error listing Gmail labels")
        return types.CallToolResult(isError=True, content=[types.TextContent(type="text", text=str(e))])

@server.tool(
    name="manage_gmail_label",
    description=(
            "Manage Gmail labels: create, update, or delete a label.\n\n"
            "**Parameters:**\n"
            "- `action` (str): 'create', 'update', or 'delete'.\n"
            "- `name` (str, optional): Label name (required for create, optional for update).\n"
            "- `label_id` (str, optional): Label ID (required for update/delete).\n"
            "- `label_list_visibility` (str): 'labelShow' or 'labelHide' (default 'labelShow').\n"
            "- `message_list_visibility` (str): 'show' or 'hide' (default 'show').\n\n"
            "**Returns:**\n"
            "- Label info or confirmation message."
    )
)
async def manage_gmail_label(
        ctx: Context,
        action: Literal["create", "update", "delete"],
        name: Optional[str] = None,
        label_id: Optional[str] = None,
        label_list_visibility: Literal["labelShow", "labelHide"] = "labelShow",
        message_list_visibility: Literal["show", "hide"] = "show"
) -> types.CallToolResult:
    user_uuid, resolved_email = await fetch_user_uuid(ctx)
    try:
        result = await gmail_client.manage_label(
            user_uuid, action, name, label_id, label_list_visibility, message_list_visibility
        )
        text = json.dumps(result, indent=2)
        return types.CallToolResult(content=[types.TextContent(type="text", text=text)])
    except Exception as e:
        logger.exception("Error managing Gmail label")
        return types.CallToolResult(isError=True, content=[types.TextContent(type="text", text=str(e))])

@server.tool(
    name="modify_gmail_message_labels",
    description=(
            "Add or remove labels from a Gmail message.\n\n"
            "**Parameters:**\n"
            "- `message_id` (str): Gmail message ID.\n"
            "- `add_label_ids` (List[str], optional): IDs to add.\n"
            "- `remove_label_ids` (List[str], optional): IDs to remove.\n\n"
            "**Returns:**\n"
            "- Confirmation of label changes."
    )
)
async def modify_gmail_message_labels(
        ctx: Context,
        message_id: str,
        add_label_ids: Optional[List[str]] = None,
        remove_label_ids: Optional[List[str]] = None
) -> types.CallToolResult:
    user_uuid, resolved_email = await fetch_user_uuid(ctx)
    try:
        result = await gmail_client.modify_message_labels(
            user_uuid, message_id, add_label_ids, remove_label_ids
        )
        text = json.dumps(result, indent=2)
        return types.CallToolResult(content=[types.TextContent(type="text", text=text)])
    except Exception as e:
        logger.exception("Error modifying Gmail message labels")
        return types.CallToolResult(isError=True, content=[types.TextContent(type="text", text=str(e))])
