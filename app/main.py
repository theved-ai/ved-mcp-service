import logging
import sys

from app.mcp_server import server
from app.utils.tool_util import load_package


logger = logging.getLogger(__name__)

def main():
    """
    Main entry point for the MCP server.
    Uses FastMCP's native streamable-http transport.
    """
    try:
        logger.info("Loading all tool modules...")
        load_package("app.tools")
        load_package("app.webclients.pensieve.text_extraction")
        logger.info("MCP server starting...")
        server.run(transport="streamable-http")
    except Exception as e:
        logger.error(f"Unexpected error running server: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()