import os
from dotenv import load_dotenv
from pydantic import BaseModel
from agents import Agent, OpenAIChatCompletionsModel
from openai import AsyncOpenAI

load_dotenv(override=True)

client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_ACCESS_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=client
)

HOW_MANY_SEARCHES = 20

INSTRUCTIONS = f"You are a helpful research assistant. Given a query, come up with a set of web searches \
to perform to best answer the query. Output {HOW_MANY_SEARCHES} terms to query for."


class WebSearchItem(BaseModel):
    reason: str
    "Your reasoning for why this search is important to the query."

    query: str
    "The search term to use for the web search."


class WebSearchPlan(BaseModel):
    searches: list[WebSearchItem]
    "A list of web searches to perform to best answer the query."


planner_agent = Agent(
    name="PlannerAgent",
    instructions=INSTRUCTIONS,
    model=model,
    output_type=WebSearchPlan,
)