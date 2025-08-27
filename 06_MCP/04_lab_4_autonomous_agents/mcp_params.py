import os
from dotenv import load_dotenv

load_dotenv(override=True)

# Market MCP server (Yahoo Finance via your own market_server.py)
market_mcp = {"command": "uv", "args": ["run", "market_server.py"]}

# Trader MCP servers: Accounts, Push Notification, Market
trader_mcp_server_params = [
    {"command": "uv", "args": ["run", "accounts_server.py"]},
    {"command": "uv", "args": ["run", "push_server.py"]},
    market_mcp,
]

# Researcher MCP servers: Fetch, Tavily Search, (optional) Memory
def researcher_mcp_server_params(name: str):
    return [
        {"command": "uvx", "args": ["mcp-server-fetch"]},
        {
            "command": "npx",
            "args": ["-y", "@mcptools/mcp-tavily"],
            "env": {"TAVILY_API_KEY": os.getenv("TAVILY_SEARCH_API_KEY")},
        },
        # Optional: memory server for agent memory
        # {
        #     "command": "npx",
        #     "args": ["-y", "mcp-memory-libsql"],
        #     "env": {"LIBSQL_URL": f"file:./memory/{name}.db"},
        # },
    ]