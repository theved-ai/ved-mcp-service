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
            "Use this tool to search the user's own ingested data for relevant information, facts, or content. "
            "Pensieve stores and indexes the user's knowledge from various sources—including emails, meeting transcripts, Slack messages, YouTube video transcripts, web pages, uploaded PDF files, and more. "
            "Whenever a user's request could be answered from their personal data, use this tool to find matching text chunks.\n\n"
            "**Parameters:**\n"
            "- `user_prompt` (str): The user's question, query, or search phrase describing what they want to find in their data.\n"
            "- `metadata` (optional, dict): Optional filters or context to narrow the search. Example keys include:\n"
            "    - `data_input_source` (str): Data source type (e.g., 'user_typed', 'meet_transcript', 'yt_transcript', 'web_page', 'pdf', 'slack').\n"
            "    - `content_timestamp` (str): Filter by content creation date/time (ISO8601) in IST timezone.\n"
            "**Returns:**\n"
            "- List of matching content chunks, with data sources, timestamps, and any available metadata."
    )
)
async def search_pensieve_chunks(
        ctx: Context,
        user_prompt: str,
        metadata: dict = None,
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
