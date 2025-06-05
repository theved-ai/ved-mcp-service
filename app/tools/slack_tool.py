from mcp import types
from app.mcp_server import server
from app.webclients.slack.slack_client import SlackClientImpl

slack_client = SlackClientImpl()


@server.tool(
    name="list_channel",
    description=(
            "List all Slack channels (both public and private) that the bot has access to.\n\n"
            "**Parameters:**\n"
            "- `bot_token`: Slack bot token with required permissions (e.g., `channels:read`, `groups:read`).\n\n"
            "**Returns:**\n"
            "- Channel name, ID, and visibility."
    )
)
async def list_channels(bot_token: str) -> types.CallToolResult:
    response = await slack_client.list_conversations(bot_token)
    channels = response.get("channels", [])
    if not channels:
        return types.CallToolResult(
            content=[types.TextContent(type="text", text="No channels found.")]
        )

    public = []
    private = []

    for c in channels:
        channel_info = f"- #{c['name']} (ID: {c['id']})"
        if c.get("is_private"):
            private.append(channel_info)
        else:
            public.append(channel_info)

    text = (
        f"Public channels:\n{chr(10).join(public) or 'None'}\n\n"
        f"Private channels:\n{chr(10).join(private) or 'None'}"
    )

    return types.CallToolResult(
        content=[types.TextContent(type="text", text=text)]
    )


@server.tool(
    name="get_channel_info",
    description=(
            "Get details about a specific Slack channel including name and visibility.\n\n"
            "**Parameters:**\n"
            "- `bot_token`: Slack bot token.\n"
            "- `channel_id`: ID of the channel to get information about.\n\n"
            "**Returns:**\n"
            "- Channel name and whether it is public or private."
    )
)
async def get_channel_info(bot_token: str, channel_id: str) -> types.CallToolResult:
    response = await slack_client.get_conversation_info(bot_token, channel_id)
    channel = response.get("channel", {})
    visibility = "private" if channel.get("is_private") else "public"
    return types.CallToolResult(content=[
        types.TextContent(type="text", text=f"Channel #{channel['name']} is {visibility}.")
    ])


@server.tool(
    name="read_channel_messages",
    description=(
            "Read recent messages from a Slack channel.\n\n"
            "**Parameters:**\n"
            "- `bot_token`: Slack bot token.\n"
            "- `channel_id`: ID of the channel.\n"
            "- `limit`: Max number of messages to retrieve (default: 5).\n\n"
            "**Returns:**\n"
            "- Latest messages from the specified channel."
    )
)
async def read_channel_messages(bot_token: str, channel_id: str, limit: int = 5) -> types.CallToolResult:
    response = await slack_client.get_conversation_history(bot_token, channel_id, limit)
    messages = response.get("messages", [])
    if not messages:
        return types.CallToolResult(content=[types.TextContent(type="text", text="No messages found.")])
    summary = "\n".join(f"- {m['text']}" for m in messages if m.get("text"))
    return types.CallToolResult(content=[types.TextContent(type="text", text=summary)])


@server.tool(
    name="read_thread_replies",
    description=(
            "Retrieve replies to a specific thread in a Slack channel.\n\n"
            "**Parameters:**\n"
            "- `bot_token`: Slack bot token.\n"
            "- `channel_id`: ID of the channel where the thread exists.\n"
            "- `thread_ts`: Timestamp of the root message of the thread.\n\n"
            "**Returns:**\n"
            "- All reply messages in the thread."
    )
)
async def read_thread_replies(bot_token: str, channel_id: str, thread_ts: str) -> types.CallToolResult:
    response = await slack_client.get_conversation_replies(bot_token, channel_id, thread_ts)
    replies = response.get("messages", [])[1:]  # skip thread root
    if not replies:
        return types.CallToolResult(content=[types.TextContent(type="text", text="No replies found.")])
    texts = "\n".join(f"- {msg.get('text')}" for msg in replies if msg.get("text"))
    return types.CallToolResult(content=[types.TextContent(type="text", text=texts)])

@server.tool(
    name="get_user_info",
    description=(
            "Fetch the name and email of a Slack user using their user ID.\n\n"
            "**Parameters:**\n"
            "- `bot_token`: Slack bot token.\n"
            "- `user_id`: Slack user ID.\n\n"
            "**Returns:**\n"
            "- User's display name and email address."
    )
)
async def get_user_info(bot_token: str, user_id: str) -> types.CallToolResult:
    response = await slack_client.get_user_info(bot_token, user_id)
    user = response.get("user", {})
    email = user.get("profile", {}).get("email", "N/A")
    return types.CallToolResult(content=[
        types.TextContent(type="text", text=f"User {user.get('name')} — Email: {email}")
    ])

@server.tool(
    name="list_users",
    description=(
            "List all active users in the Slack workspace with their display names and user IDs.\n\n"
            "**Parameters:**\n"
            "- `bot_token`: Slack bot token with `users:read` scope.\n\n"
            "**Returns:**\n"
            "- Basic info (name, ID) of non-deleted users."
    )
)
async def list_users(bot_token: str) -> types.CallToolResult:
    response = await slack_client.list_users(bot_token)
    members = response.get("members", [])
    if not members:
        return types.CallToolResult(content=[types.TextContent(type="text", text="No users found.")])

    user_list = []
    for user in members:
        if not user.get("deleted"):
            user_info = f"user_name: {user['name']} (ID: {user['id']})"
            user_list.append(user_info)

    text = (
        f"User info:\n{chr(10).join(user_list) or 'None'}"
    )

    return types.CallToolResult(content=[types.TextContent(type="text", text=f"Users: {text}")])

@server.tool(
    name="search_messages_in_channel",
    description=(
            "Search recent messages in a specific Slack channel for a given keyword.\n\n"
            "**Parameters:**\n"
            "- `bot_token`: Slack bot token.\n"
            "- `channel_id`: ID of the Slack channel to search in.\n"
            "- `keyword`: Word or phrase to look for in messages.\n"
            "- `limit`: Number of recent messages to scan (default: 10).\n\n"
            "**Returns:**\n"
            "- A summary of matched messages with their timestamps (`ts`) and content.\n"
            "- Useful for follow-up actions like retrieving thread replies using the timestamp."
    )
)
async def search_messages(bot_token: str, channel_id: str, keyword: str, limit: int = 10) -> types.CallToolResult:
    response = await slack_client.search_messages_in_conversation({
        "bot_token": bot_token,
        "channel_id": channel_id,
        "limit": limit
    })

    matches = []
    for m in response.get("messages", []):
        if m.get("subtype"):  # skip system messages like channel_join
            continue
        text = m.get("text", "")
        if keyword.lower() in text.lower():
            ts = m.get("ts")
            matches.append(f"- [{ts}] {text}")

    text_output = "\n".join(matches[:limit]) or f"No messages containing '{keyword}' found."
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=text_output)]
    )


@server.tool(
    name="search_mentions",
    description=(
            "Search for messages in a Slack channel where a specific user was mentioned.\n\n"
            "**Parameters:**\n"
            "- `bot_token`: Slack bot token.\n"
            "- `user_id`: Slack user ID to search mentions of.\n"
            "- `channel_id`: Channel in which to perform the search.\n"
            "- `limit`: Number of recent messages to scan (default: 10).\n\n"
            "**Returns:**\n"
            "- Messages mentioning the given user."
    )
)
async def search_mentions(bot_token: str, user_id: str, channel_id: str, limit: int = 10) -> types.CallToolResult:
    response = await slack_client.get_messages_mentioning_user({
        "bot_token": bot_token,
        "user_id": user_id,
        "channel_id": channel_id,
        "limit": limit
    })
    messages = [m["text"] for m in response.get("messages", [])]
    text = "\n".join(messages[:limit]) or "No mentions found."
    return types.CallToolResult(content=[types.TextContent(type="text", text=text)])


@server.tool(
    name="is_bot_in_channel",
    description=(
            "Check whether the bot is a member of a specific Slack channel.\n\n"
            "**Parameters:**\n"
            "- `bot_token`: Slack bot token.\n"
            "- `channel_id`: ID of the Slack channel.\n\n"
            "**Returns:**\n"
            "- 'Yes' if the bot is a member; otherwise 'No'."
    )
)
async def is_bot_in_channel(bot_token: str, channel_id: str) -> types.CallToolResult:
    is_member = await slack_client.is_bot_member_of_conversation({
        "bot_token": bot_token,
        "channel_id": channel_id
    })
    return types.CallToolResult(content=[types.TextContent(type="text", text="Yes" if is_member else "No")])


@server.tool(
    name="get_channel_members",
    description=(
            "Retrieve a list of members in a specific Slack channel.\n\n"
            "**Parameters:**\n"
            "- `bot_token`: Slack bot token.\n"
            "- `channel_id`: ID of the Slack channel.\n\n"
            "**Returns:**\n"
            "- Member user IDs or display names in the channel."
    )
)
async def get_channel_members(bot_token: str, channel_id: str) -> types.CallToolResult:
    response = await slack_client.get_conversation_members({
        "bot_token": bot_token,
        "channel_id": channel_id
    })
    members = response.get("members", [])
    if not members:
        return types.CallToolResult(content=[types.TextContent(type="text", text="No members found.")])
    summary = ", ".join(f"{m['name']}" for m in members)
    return types.CallToolResult(content=[types.TextContent(type="text", text=summary)])
