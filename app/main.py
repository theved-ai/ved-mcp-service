import asyncio
import os
import sys

from app.config.logging_config import logger
from app.db.postgres.psql_conn_pool import close_pg_pool, init_pg_pool
from app.mcp_server import server
from app.utils.application_constants import db_url_key
from app.utils.env_loader import load_environment
from app.utils.global_exception_handler import global_exception_handler
from app.utils.tool_util import load_package


async def main():
    """
    Main entry point for the MCP server.
    Uses FastMCP's native streamable-http transport.
    """
    try:
        logger.info("Loading all tool modules...")
        load_package("app.tools")
        load_package("app.webclients.pensieve.text_extraction")

        db_url = os.getenv(db_url_key)
        await init_pg_pool(db_url)
        logger.info("PG pool initialised")

        logger.info("MCP server starting...")
        await server.run_streamable_http_async()
        server.streamable_http_app().add_exception_handler(Exception, global_exception_handler)
    except Exception as e:
        logger.error(f"Unexpected error running server: {e}", exc_info=True)
        await close_pg_pool()
        sys.exit(1)

if __name__ == "__main__":
    load_environment()
    asyncio.run(main())