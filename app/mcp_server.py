from mcp.server.fastmcp import FastMCP

settings = {
    "log_level": "DEBUG",
    "debug": True
}

server = FastMCP(
    name="mcp_server",
    server_url="http://localhost:8080/mcp",
    port="8080",
    **settings
)