from typing import Any, Optional

from mcp import types
from mcp.server.fastmcp.server import Context

from app.decorators.try_catch_decorator import try_catch_wrapper_no_raised_exception
from app.dto.pensieve_request import PensieveRequest
from app.dto.search_chat_req import SearchChatRequest
from app.mcp_server import server
from app.utils.app_utils import failed_tool_response
from app.utils.application_constants import pensieve_search_failed, pensieve_search_chat_failed
from app.utils.tool_util import fetch_user_uuid
from app.webclients.pensieve.pensieve_service import PensieveService

pensieve_service = PensieveService()

@try_catch_wrapper_no_raised_exception(logger_fn= lambda e: failed_tool_response(e, pensieve_search_failed))
@server.tool(
    name="search_matching_chunks",
    description=("""
    Description:
      Semantic search across the user's personal knowledge base (Pensieve).  
      Works on personal notes and past chats with Ved. 
      Always pass the user’s question in `user_prompt`.  
      Optionally add a `metadata` filter to target a specific data source
      and/or time range.
    
    Parameters:
      user_prompt (str, required)
          The natural-language query.
      metadata (dict, optional)
          Additional filters. Common keys:
            - data_input_source : str   # available values => "user_typed", "chat"
            - conversation_id   : str   # mandatory when data_input_source == "chat"
            - content_timestamp : dict  # {"gte": ISO-8601, "lte": ISO-8601}
    
    Returns:
      List of matching chunks with payload:
        chunk_content, chunk_data_source, chunk_creation_timestamp,
        user_ingested_chunk_at, chunk_metadata
    """
    )
)
async def search_matching_chunks(
        ctx: Context,
        user_prompt: str,
        metadata: Optional[dict[str, Any]] = None,
) -> types.CallToolResult:
    user_id = await fetch_user_uuid(ctx)
    req = PensieveRequest(user_prompt=user_prompt, user_id=user_id, metadata=metadata)
    results = await pensieve_service.fetch_matching_chunks(req)
    return await generate_tool_response(results)


@try_catch_wrapper_no_raised_exception(logger_fn= lambda e: failed_tool_response(e, pensieve_search_chat_failed))
@server.tool(
    name="fetch_recent_chat_messages",
    description=(
        "Retrieve the latest messages from the **current Ved-user conversation**.\n\n"
        "Typical triggers: “message above”, “reply to that”, “continue the conversation”, "
        "“what did we just talk about?”, or any prompt that clearly references the live chat.\n\n"
        "**Parameters**\n"
        "• `conversation_id` (str, **required**) – UUID of the chat thread to scan.\n"
        "• `max_messages` (int, **required**) – Number of most-recent messages to return "
        "(1 ⇒ newest only).\n\n"
        "**Returns**\n"
        "A list of message objects sorted newest ➜ oldest."
    )
)
async def search_chats(
        ctx: Context,
        conversation_id: str,
        max_messages: int
) -> types.CallToolResult:
    user_id = await fetch_user_uuid(ctx)
    req = SearchChatRequest(user_id=user_id, conversation_id=conversation_id, max_messages=max_messages)
    results = await pensieve_service.search_chat(req)
    return await generate_tool_response(results)


async def generate_tool_response(results):
    if not results:
        return types.CallToolResult(
            content=[types.TextContent(type="text", text="No matching content found in Pensieve.")])
    output_lines = []
    for res in results:
        meta_str = f"\nMetadata: {res.chunk_metadata}" if res.chunk_metadata else ""
        output_lines.append(
            f"- Content: {res.chunk_content}\n"
            f"  Source: {res.chunk_data_source}\n"
            f"  Ingested At: {res.user_ingested_chunk_at}\n"
            f"  Created: {res.chunk_creation_timestamp}{meta_str}"
        )
    return types.CallToolResult(content=[types.TextContent(type="text", text="\n\n".join(output_lines))])