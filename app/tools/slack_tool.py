import json
from mcp import types
from mcp.server.fastmcp.server import Context
from app.mcp_server import server
from app.webclients.slack.slack_client import SlackClientImpl
from app.utils.user_client_token_util import fetch_user_token, fetch_user_uuid

slack_client = SlackClientImpl()
client_name = "slack"

@server.tool(
    name="list_channel",
    description=(
            "List all Slack channels (both public and private) that the bot has access to for the current user.\n\n"
            "Returns a mapping of Slack bot tokens to their accessible channels."
    )
)
async def list_channels(ctx: Context) -> types.CallToolResult:
    bot_tokens = await fetch_user_token(await fetch_user_uuid(ctx), client_name)
    output = {}
    for bot_token in bot_tokens:
        response = await slack_client.list_conversations(bot_token)
        channels = response.get("channels", [])
        public = []
        private = []
        for c in channels:
            channel_info = f"- #{c['name']} (ID: {c['id']})"
            if c.get("is_private"):
                private.append(channel_info)
            else:
                public.append(channel_info)
        output[bot_token] = (
            f"Public channels:\n{chr(10).join(public) or 'None'}\n\n"
            f"Private channels:\n{chr(10).join(private) or 'None'}"
        )
    text_str = json.dumps(output)
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=text_str)]
    )

@server.tool(
    name="get_channel_info",
    description=(
            "Get details about a specific Slack channel including name and visibility for all workspaces the user is connected to.\n\n"
            "**Parameters:**\n"
            "- `channel_id`: ID of the channel to get information about."
    )
)
async def get_channel_info(ctx: Context, channel_id: str) -> types.CallToolResult:
    bot_tokens = await fetch_user_token(await fetch_user_uuid(ctx), client_name)
    output = {}
    for bot_token in bot_tokens:
        response = await slack_client.get_conversation_info(bot_token, channel_id)
        channel = response.get("channel", {})
        visibility = "private" if channel.get("is_private") else "public"
        output[bot_token] = f"Channel #{channel.get('name', 'N/A')} is {visibility}."
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=json.dumps(output))]
    )

@server.tool(
    name="read_channel_messages",
    description=(
            "Read recent messages from a Slack channel across all connected workspaces for the user.\n\n"
            "**Parameters:**\n"
            "- `channel_id`: ID of the channel.\n"
            "- `limit`: Max number of messages to retrieve (default: 5)."
    )
)
async def read_channel_messages(ctx: Context, channel_id: str, limit: int = 5) -> types.CallToolResult:
    bot_tokens = await fetch_user_token(await fetch_user_uuid(ctx), client_name)
    output = {}
    for bot_token in bot_tokens:
        response = await slack_client.get_conversation_history(bot_token, channel_id, limit)
        messages = response.get("messages", [])
        summary = "\n".join(f"- {m['text']}" for m in messages if m.get("text"))
        output[bot_token] = summary or "No messages found."
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=json.dumps(output))]
    )

@server.tool(
    name="read_thread_replies",
    description=(
            "Retrieve replies to a specific thread in a Slack channel for all user workspaces.\n\n"
            "**Parameters:**\n"
            "- `channel_id`: Channel ID where the thread exists.\n"
            "- `thread_ts`: Timestamp of the root message."
    )
)
async def read_thread_replies(ctx: Context, channel_id: str, thread_ts: str) -> types.CallToolResult:
    bot_tokens = await fetch_user_token(await fetch_user_uuid(ctx), client_name)
    output = {}
    for bot_token in bot_tokens:
        response = await slack_client.get_conversation_replies(bot_token, channel_id, thread_ts)
        replies = response.get("messages", [])[1:]  # skip thread root
        texts = "\n".join(f"- {msg.get('text')}" for msg in replies if msg.get("text"))
        output[bot_token] = texts or "No replies found."
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=json.dumps(output))]
    )

@server.tool(
    name="get_user_info",
    description=(
            "Fetch the name and email of a Slack user using their user ID across all connected workspaces.\n\n"
            "**Parameters:**\n"
            "- `user_id`: Slack user ID."
    )
)
async def get_user_info(ctx: Context, user_id: str) -> types.CallToolResult:
    bot_tokens = await fetch_user_token(await fetch_user_uuid(ctx), client_name)
    output = {}
    for bot_token in bot_tokens:
        response = await slack_client.get_user_info(bot_token, user_id)
        user = response.get("user", {})
        email = user.get("profile", {}).get("email", "N/A")
        output[bot_token] = f"User {user.get('name')} — Email: {email}"
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=json.dumps(output))]
    )

@server.tool(
    name="list_users",
    description=(
            "List all active users in the Slack workspace with their display names and user IDs for all workspaces the user is connected to."
    )
)
async def list_users(ctx: Context) -> types.CallToolResult:
    bot_tokens = await fetch_user_token(await fetch_user_uuid(ctx), client_name)
    output = {}
    for bot_token in bot_tokens:
        response = await slack_client.list_users(bot_token)
        members = response.get("members", [])
        user_list = [
            f"user_name: {user['name']} (ID: {user['id']})"
            for user in members if not user.get("deleted")
        ]
        output[bot_token] = "\n".join(user_list) or "No users found."
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=json.dumps(output))]
    )

@server.tool(
    name="search_messages_in_channel",
    description=(
            "Search recent messages in a specific Slack channel for a given keyword across all user-connected workspaces.\n\n"
            "**Parameters:**\n"
            "- `channel_id`: Channel ID to search in.\n"
            "- `keyword`: Word or phrase to look for.\n"
            "- `limit`: Number of recent messages to scan (default: 10).\n\n"
            "Returns a JSON with each bot token mapped to matched messages and their timestamps."
    )
)
async def search_messages(ctx: Context, channel_id: str, keyword: str, limit: int = 10) -> types.CallToolResult:
    bot_tokens = await fetch_user_token(await fetch_user_uuid(ctx), client_name)
    output = {}
    for bot_token in bot_tokens:
        response = await slack_client.search_messages_in_conversation({
            "bot_token": bot_token,
            "channel_id": channel_id,
            "limit": limit
        })
        matches = []
        for m in response.get("messages", []):
            if m.get("subtype"):
                continue
            text = m.get("text", "")
            if keyword.lower() in text.lower():
                ts = m.get("ts")
                matches.append(f"- [{ts}] {text}")
        output[bot_token] = "\n".join(matches[:limit]) or f"No messages containing '{keyword}' found."
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=json.dumps(output))]
    )

@server.tool(
    name="search_mentions",
    description=(
            "Search for messages in a Slack channel where a specific user was mentioned, for all user-connected workspaces.\n\n"
            "**Parameters:**\n"
            "- `user_id`: Slack user ID to search mentions of.\n"
            "- `channel_id`: Channel in which to perform the search.\n"
            "- `limit`: Number of recent messages to scan (default: 10)."
    )
)
async def search_mentions(ctx: Context, user_id: str, channel_id: str, limit: int = 10) -> types.CallToolResult:
    bot_tokens = await fetch_user_token(await fetch_user_uuid(ctx), client_name)
    output = {}
    for bot_token in bot_tokens:
        response = await slack_client.get_messages_mentioning_user({
            "bot_token": bot_token,
            "user_id": user_id,
            "channel_id": channel_id,
            "limit": limit
        })
        messages = [m["text"] for m in response.get("messages", [])]
        output[bot_token] = "\n".join(messages[:limit]) or "No mentions found."
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=json.dumps(output))]
    )

@server.tool(
    name="is_bot_in_channel",
    description=(
            "Check whether the bot is a member of a specific Slack channel for all connected workspaces.\n\n"
            "**Parameters:**\n"
            "- `channel_id`: Channel ID.\n\n"
            "Returns a JSON of bot token to 'Yes' or 'No'."
    )
)
async def is_bot_in_channel(ctx: Context, channel_id: str) -> types.CallToolResult:
    bot_tokens = await fetch_user_token(await fetch_user_uuid(ctx), client_name)
    output = {}
    for bot_token in bot_tokens:
        is_member = await slack_client.is_bot_member_of_conversation({
            "bot_token": bot_token,
            "channel_id": channel_id
        })
        output[bot_token] = "Yes" if is_member else "No"
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=json.dumps(output))]
    )

@server.tool(
    name="get_channel_members",
    description=(
            "Retrieve a list of members in a specific Slack channel for all user-connected workspaces.\n\n"
            "**Parameters:**\n"
            "- `channel_id`: Channel ID."
    )
)
async def get_channel_members(ctx: Context, channel_id: str) -> types.CallToolResult:
    bot_tokens = await fetch_user_token(await fetch_user_uuid(ctx), client_name)
    output = {}
    for bot_token in bot_tokens:
        response = await slack_client.get_conversation_members({
            "bot_token": bot_token,
            "channel_id": channel_id
        })
        members = response.get("members", [])
        summary = ", ".join(f"{m['name']}" for m in members)
        output[bot_token] = summary or "No members found."
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=json.dumps(output))]
    )
