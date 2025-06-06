import logging
import logging
import sys

from app.mcp_server import server
from app.utils.tool_loader import load_all_tools_from_package

LOG_FORMAT = (
    "\n[%(asctime)s] %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
)

logging.basicConfig(
    level=logging.DEBUG,
    format=LOG_FORMAT,
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

def main():
    """
    Main entry point for the MCP server.
    Uses FastMCP's native streamable-http transport.
    """
    try:
        logger.info("Loading all tool modules...")
        load_all_tools_from_package("app.tools")

        logger.info("MCP server starting...")
        # The server is already configured with port and server_url in core/server.py
        server.run(transport="streamable-http")
    except KeyboardInterrupt:
        logger.info("Server shutdown requested via keyboard interrupt")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error running server: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()