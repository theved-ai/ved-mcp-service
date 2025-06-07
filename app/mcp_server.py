from mcp.server.fastmcp import FastMCP

settings = {
    "log_level": "INFO",
    "debug": False
}

server = FastMCP(
    name="mcp_server",
    server_url="http://localhost:8080/mcp",
    port="8080",
    **settings
)