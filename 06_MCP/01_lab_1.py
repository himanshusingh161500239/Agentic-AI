from dotenv import load_dotenv
from agents import Agent, Runner, trace, OpenAIChatCompletionsModel
from openai import AsyncOpenAI
from agents.mcp import MCPServerStdio
import os
import asyncio
load_dotenv(override=True)

# default timeout is 5 seconds
fetch_tools=None
fetch_params={"command":"uvx","args":["mcp-server-fetch"]}
async def noraml_fetch_tool():
    async with MCPServerStdio(params=fetch_params, client_session_timeout_seconds=30) as server:
        fetch_tools= await server.list_tools()
        return fetch_tools

fetch_tools= asyncio.run(noraml_fetch_tool()) 
print("Fetch Tools::",fetch_tools)
print("\n\n")

## The above command will run and spwan a new python process in our system
## It will create a MCP client running within Openai SDk.
## That client will connect with server and ask which tools you can offer.
## it's a python based MCP server


## let's create a javascript based MCP server using Node.js

playwright_params={"command":"npx","args":["@playwright/mcp@latest"]}
async def playwright_fetch_tool():
    async with MCPServerStdio(params=playwright_params, client_session_timeout_seconds=30) as server:
        playwright_tools = await server.list_tools()
        return playwright_tools

playwright_tools= asyncio.run(playwright_fetch_tool()) 
print("Playwright Tools:::",playwright_tools)
print("\n\n")



sandbox_path = os.path.abspath(os.path.join(os.getcwd(),"sandbox"))
files_params ={"command":"npx","args":["-y","@modelcontextprotocol/server-filesystem",sandbox_path]}
async def playwright_sandbox_fetch_tool():
    async with MCPServerStdio(params=files_params,client_session_timeout_seconds=30) as server:
        file_tools=await server.list_tools()
        return file_tools

file_tools= asyncio.run(playwright_sandbox_fetch_tool()) 
print("File Handling Tools::",file_tools)
print("\n\n")


instructions = """
You browse the internet to accomplish your instructions.
You are highly capable at browsing the internet independently to accomplish your task, 
including accepting all cookies and clicking 'not now' as
appropriate to get to the content you need. If one website isn't fruitful, try another. 
Be persistent until you have solved your assignment,
trying different options and sites as needed.
"""

client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_ACCESS_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=client
)

async def mcp_Agent():
    async with MCPServerStdio(params=files_params, client_session_timeout_seconds=60) as mcp_server_files:
        async with MCPServerStdio(params=playwright_params, client_session_timeout_seconds=60) as mcp_server_browser:
            agent = Agent(
                name="investigator", 
                instructions=instructions, 
                model=model,
                mcp_servers=[mcp_server_files, mcp_server_browser]
                )
            with trace("investigate"):
                result = await Runner.run(agent, "Find a great recipe for Banoffee Pie, then summarize it in markdown to banoffee.md")
                print("Final Response:::",result.final_output)

asyncio.run(mcp_Agent()) 