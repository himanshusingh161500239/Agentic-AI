from agents import Agent,function_tool,OpenAIChatCompletionsModel
from openai import AsyncOpenAI
from dotenv import load_dotenv
import os
from typing import Dict
from email.message import EmailMessage
import ssl
import smtplib
from email.message import EmailMessage
import ssl
import smtplib

load_dotenv(override=True)

client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_ACCESS_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=client
)

@function_tool
def send_email(subject:str, html_body:str) ->Dict[str,str]:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = "himanshusinghvns343@gmail.com"
    msg["To"] = "himanshusinghvns343@gmail.com"
    msg.add_alternative(html_body, subtype="html")

    context = ssl.create_default_context()
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls(context=context)
        server.login(os.getenv('GMAIL_USER_ID'), os.getenv('GMAIL_API_KEY'))
        server.send_message(msg)

    return {"status": "success"}

INSTRUCTIONS = """You are able to send a nicely formatted HTML email based on a detailed report.
You will be provided with a detailed report. You should use your tool to send one email, providing the 
report converted into clean, well presented HTML with an appropriate subject line."""

email_agent = Agent(
    name="Email agent",
    instructions=INSTRUCTIONS,
    tools=[send_email],
    model=model,
)