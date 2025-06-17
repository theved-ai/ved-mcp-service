from typing import Any, Optional

from app.dto.pensieve_request import PensieveRequest
from app.utils.tool_util import fetch_user_uuid
from app.mcp_server import server
from mcp import types
from mcp.server.fastmcp.server import Context
import logging

from app.webclients.pensieve.pensieve_service import PensieveService

logger = logging.getLogger(__name__)
pensieve_service = PensieveService()

@server.tool(
    name="search_pensieve_chunks",
    description=(
            "Use this tool to search the user's ingested data (emails, meetings, Slack, YouTube transcripts, web pages, PDFs, etc.) for relevant information, facts, or content.\n\n"
            "**How to use:**\n"
            "- Always pass the user's query in `user_prompt`.\n"
            "- When the user's request indicates a specific data source or type (e.g., 'meeting', 'Slack', 'YouTube', 'web page', 'PDF'), **populate the `metadata` field with the correct filter(s)**:\n"
            "    - For meetings, set `metadata` to `{ \"data_input_source\": \"meet_transcript\" }`.\n"
            "    - For Slack messages, set `metadata` to `{ \"data_input_source\": \"slack\" }`.\n"
            "    - For YouTube transcripts, set `metadata` to `{ \"data_input_source\": \"yt_transcript\" }`.\n"
            "    - For web pages, set `metadata` to `{ \"data_input_source\": \"web_page\" }`.\n"
            "    - For PDFs, set `metadata` to `{ \"data_input_source\": \"pdf\" }`.\n"
            "- If the prompt mentions a time or date, include it as `content_timestamp` (in ISO8601, IST timezone) in `metadata`.\n\n"
            "**Parameters:**\n"
            "- `user_prompt` (str): The user's question or search phrase.\n"
            "- `metadata` (optional, dict): Context or filters such as data source or timestamp.\n\n"
            "**Returns:**\n"
            "- List of matching content chunks, with data sources, timestamps, and any available metadata."
    )
)
async def search_pensieve_chunks(
        ctx: Context,
        user_prompt: str,
        metadata: Optional[dict[str, Any]] = None,
) -> types.CallToolResult:
    user_id = await fetch_user_uuid(ctx)
    req = PensieveRequest(user_prompt=user_prompt, user_id=user_id, metadata=metadata)
    try:
        results = await pensieve_service.fetch_matching_chunks(req)
        if not results:
            return types.CallToolResult(content=[types.TextContent(type="text", text="No matching content found in Pensieve.")])

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
    except Exception as e:
        logger.exception("Error searching Pensieve chunks")
        return types.CallToolResult(isError=True, content=[types.TextContent(type="text", text=str(e))])
