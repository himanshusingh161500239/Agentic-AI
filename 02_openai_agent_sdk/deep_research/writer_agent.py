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

INSTRUCTIONS = (
    "You are a senior researcher tasked with writing a cohesive report for a research query. "
    "You will be provided with the original query, and some initial research done by a research assistant.\n"
    "You should first come up with an outline for the report that describes the structure and "
    "flow of the report. Then, generate the report and return that as your final output.\n"
    "The final output should be in markdown format, and it should be lengthy and detailed. Aim "
    "for 5-10 pages of content, at least 1000 words." 
    "At the bottom of report provide some useful reference links to explore."\
)


class ReportData(BaseModel):
    short_summary: str 
    "A short 2-3 sentence summary of the findings."

    markdown_report: str 
    "The final report"

    follow_up_questions: list[str] 
    "Suggested topics to research further"


writer_agent = Agent(
    name="WriterAgent",
    instructions=INSTRUCTIONS,
    model=model,
    output_type=ReportData,
)