from dotenv import load_dotenv
from agents import Agent, Runner, OpenAIChatCompletionsModel
from agents.mcp import MCPServerStdio
import os
from datetime import datetime

from openai import AsyncOpenAI

import asyncio
load_dotenv(override=True)


# # First type of MCP Server: runs locally, everything local
# # Here's a really interesting one: a knowledge-graph based memory.

# # It's a persistent memory store of entities, observations about them, and relationships between them.

# # https://github.com/modelcontextprotocol/servers/tree/main/src/memory


# params = {"command": "npx","args": ["-y", "mcp-memory-libsql"],"env": {"LIBSQL_URL": "file:./memory/himanshu.db"}}
# async def mcp_node_server_tools():
#     async with MCPServerStdio(params=params, client_session_timeout_seconds=90) as server:
#         mcp_tools = await server.list_tools()
#         return mcp_tools

# mcp_tools=asyncio.run(mcp_node_server_tools()) 
# # print("MCP Tools::",mcp_tools)


# instructions="Use your entity tools as a persistent memory to store and recall information about your conversations."
# request="My name is Himanshu. I am a Software Enginner and learning about AI Agents, including the incredibles MCP protocol.\
#     I have learned that MCP is a protocol for connecting with agents with tools, resources and prompt templates, and makes it easy to integrate Ai agents with capabilities."

client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_ACCESS_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=client
)

# # Create a MCP server
# async def mcp_server(request):
#     async with MCPServerStdio(params=params, client_session_timeout_seconds=30) as mcp_server:
#         agent = Agent(name="agent", instructions=instructions, model=model, mcp_servers=[mcp_server])
#         result = await Runner.run(agent, request)
#         return result.final_output
    
# result = asyncio.run(mcp_server(request)) 
# print("Response::",result)


# request="My name is Himanshu, What do you know about me?"
# follow_up_response=asyncio.run(mcp_server(request)) 
# print("Follow up Response::",follow_up_response)





# Second type of MCP Server: runs locally, calls a web service

# env = {"BRAVE_API_KEY": os.getenv("BRAVE_API_KEY")}
# async def brave_mcp_server():
#     params = {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-brave-search"], "env": env}

#     async with MCPServerStdio(params=params, client_session_timeout_seconds=30) as server:
#         mcp_tools = await server.list_tools()
#         return mcp_tools

# mcp_tools=asyncio.run(brave_mcp_server()) 


# Instead of Brave , let's use Tavily
# params = {
#     "command": "npx",
#     "args": ["-y", "@mcptools/mcp-tavily"],
#     "env": {"TAVILY_API_KEY": os.getenv('TAVILY_SEARCH_API_KEY')}
# }
# async def tavily_mcp_server():
#     async with MCPServerStdio(params=params, client_session_timeout_seconds=30) as server:
#         tools = await server.list_tools()
#         # print("Available tools:", tools)
#         return tools
#         # Example search call
#         # result = await server.call_tool("search", {"query": "current trends in AI", "options": {"maxResults": 5}})
#         # print("Search Result:", result)

# tavily_search_tool=asyncio.run(tavily_mcp_server())

# instructions = "You are able to search the web for information and briefly summarize the takeaways."
# request = f"Please research the latest news on ITC stock price and briefly summarize its outlook. \
# For context, the current date is {datetime.now().strftime('%Y-%m-%d')}"

# model = model


# # # Create a MCP server
# async def tavily_server():
#     async with MCPServerStdio(params=params, client_session_timeout_seconds=30) as mcp_server:
#         agent = Agent(name="agent", instructions=instructions, model=model, mcp_servers=[mcp_server])
#         result = await Runner.run(agent, request)
#         return result.final_output

# tavily_search_result=asyncio.run(tavily_server())

# print("Tavily search result::",tavily_search_result)




# Let's integrate Yahoo Finance as MCP Server
import yfinance as yf
# ticker = yf.Ticker("ITC.NS")

# Get last 5 days of data
# hist = ticker.history(period="5d")
# print(hist[["Open", "High", "Low", "Close", "Volume"]])


params={"command":"uv","args":["run","market_server.py"]}

# Fetch the tools
async def yahoo_finance_server():
    async with MCPServerStdio(params=params) as server:
        mcp_tools=await server.list_tools()
        return mcp_tools
    
yahoo_mcp_tools=asyncio.run(yahoo_finance_server())
print("Yahoo tools::",yahoo_mcp_tools)


# Call the MCP server with query
instructions ="You answer questions aboout the stock market."
request="What's the share price of ITC?"

async def check_stock_price():
    # async with MCPServerStdio(params=params) as mcp_server:
    #     agent=Agent(name="agent",instructions=instructions,model=model,mcp_servers=[mcp_server])
    #     result=await Runner.run(agent,request)
    #     return result.final_output
    async with MCPServerStdio(params=params, client_session_timeout_seconds=60) as mcp_server:
        agent = Agent(name="agent", instructions=instructions, model=model, mcp_servers=[mcp_server])
        result = await Runner.run(agent, request)
        return result.final_output
    
share_info=asyncio.run(check_stock_price())
print("Analysis response::",share_info)