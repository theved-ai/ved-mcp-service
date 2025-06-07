from mcp.server.fastmcp import Context
import importlib
import pkgutil
import logging

logger = logging.getLogger(__name__)

async def fetch_user_uuid(ctx: Context):
    header_dict = {k.decode().lower(): v.decode() for k, v in ctx.request_context.request.headers.raw}
    return header_dict.get("user_uuid")

def load_all_tools_from_package(package_name: str):
    """
    Dynamically imports all modules in a given package to trigger decorator registration.
    """
    package = importlib.import_module(package_name)
    for loader, name, is_pkg in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
        if not is_pkg:
            logger.debug(f"Importing tool module: {name}")
            importlib.import_module(name)