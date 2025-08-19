import os
from dotenv import load_dotenv
from pydantic import BaseModel
from agents import Agent, OpenAIChatCompletionsModel,function_tool
from agents.model_settings import ModelSettings
from openai import AsyncOpenAI
from ddgs import DDGS


load_dotenv(override=True)

client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_ACCESS_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=client
)


class SearchInput(BaseModel):
    query: str


# @function_tool
# def duckduckgo_web_search(input: SearchInput) -> str:
#     """Search the web using DuckDuckGo and return text snippets."""
#     with DDGS() as ddgs:
#         results = ddgs.text(input.query, max_results=20)
#         filtered = [r["body"] for r in results if "agent" in r["body"].lower()]
#         return "\n".join(filtered) or "No relevant results found."

@function_tool
def duckduckgo_web_search(input: SearchInput) -> str:
    """Search the web using DuckDuckGo and return text snippets."""
    with DDGS() as ddgs:
        results = ddgs.text(input.query, max_results=20)
        filtered = [r["body"] for r in results if "agent" in r["body"].lower()]
        return "\n".join(filtered) or "No relevant results found."


INSTRUCTIONS = "You are a research assistant. Given a search term, you search the web for that term and \
produce a concise summary of the results. The summary must 2-3 paragraphs and less than 300 \
words. Capture the main points. Write succintly, no need to have complete sentences or good \
grammar. This will be consumed by someone synthesizing a report, so it's vital you capture the \
essence and ignore any fluff. Do not include any additional commentary other than the summary itself.\
If the search results are vague, combine them with prior knowledge and reasonable inference to provide the best possible answer." \
""

search_agent = Agent(
    name="Search agent",
    instructions=INSTRUCTIONS,
    tools=[duckduckgo_web_search],
    model=model,
    model_settings=ModelSettings(tool_choice="required"),
)