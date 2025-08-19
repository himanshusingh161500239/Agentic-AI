from openai import OpenAI
from PyPDF2 import PdfReader
from pydantic import BaseModel
import gradio as gr
import os
import boto3
import json
from dotenv import load_dotenv
load_dotenv(override=True)

os.environ["AWS_ACCESS_KEY_ID"] = os.getenv('AWS_ACCESS_KEY')
os.environ["AWS_SECRET_ACCESS_KEY"] = os.getenv('AWS_SECRET_ACCESS_KEY')
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')


openai=OpenAI(api_key=os.getenv('GEMINI_ACCESS_KEY'),base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
model_name = "gemini-1.5-flash"

reader=PdfReader('data/me.pdf')

data=""
for page in reader.pages:
    text = page.extract_text()
    if text:
        data+=text
# print("Data::",data)

with open('data/summary.txt') as f:
    summary=f.read()

# print("Summary::",summary)
name="Himanshu"

system_prompt=f"You are acting as {name}.You are answering questions on {name}'s profile, particularly questions related to {name}'s career,\
    background, skills and experience.\
    Your responsibility is to represent {name} for interactions on the profile as faithfully as possible.\
    You are given a summary of {name}'s background and profile/resume which you can use to answer questions.\
    Be profeccional and engaging, as if talking to a potential client or future employer who can some across the profile.\
    If you don't know the answer, say so."

system_prompt+=f"\n\n##Summary:\n{summary}\n\n## {name}'s Profile:\n{data}\n\n"
system_prompt+=f"With this context, please chat with the user, always statying in character as {name}"



# def chat(message,history):
#     messages=[{"role":"system","content":system_prompt}] + history + [{"role":"user","content":message}]
#     response=openai.chat.completions.create(model=model_name,messages=messages)
#     return response.choices[0].message.content

# gr.ChatInterface(chat,type="messages").launch()

class Evaluation(BaseModel):
    is_acceptable:bool
    feedback:str

evaluator_system_prompt = f"You are an evaluator that decides whether a response to a question is acceptable. \
You are provided with a conversation between a User and an Agent. Your task is to decide whether the Agent's latest response is acceptable quality. \
The Agent is playing the role of {name} and is representing {name} on their website. \
The Agent has been instructed to be professional and engaging, as if talking to a potential client or future employer who came across the website. \
The Agent has been provided with context on {name} in the form of their summary and LinkedIn details. Here's the information:"

evaluator_system_prompt += f"\n\n## Summary:\n{summary}\n\n## Profile:\n{data}\n\n"
evaluator_system_prompt += f"With this context, please evaluate the latest response, replying with whether the response is acceptable and your feedback."


def evaluator_user_prompt(reply, message, history):
    user_prompt = f"Here's the conversation between the User and the Agent: \n\n{history}\n\n"
    user_prompt += f"Here's the latest message from the User: \n\n{message}\n\n"
    user_prompt += f"Here's the latest response from the Agent: \n\n{reply}\n\n"
    user_prompt += "Please evaluate the response, replying with whether it is acceptable and your feedback."
    return user_prompt


def evaluate(reply,message,history) ->Evaluation:
    messages = [{"role": "system", "content": evaluator_system_prompt}] + [{"role": "user", "content": evaluator_user_prompt(reply, message, history)}]
    response = openai.beta.chat.completions.parse(model=model_name,messages=messages,response_format=Evaluation)
    return response.choices[0].message.parsed


# messages=[{"role":"system","content":system_prompt}]+ [{"role":"user","content":"do you hold a patent?"}]
# response=openai.chat.completions.create(model=model_name,messages=messages)
# reply=response.choices[0].message.content
# print("Reply:::",reply)

# evaluation_response=evaluate(reply,"do you hold a patent?",messages[:1])

# print("Evaluation Response::",evaluation_response)


def rerun(reply, message, history, feedback):
    updated_system_prompt = system_prompt + "\n\n## Previous answer rejected\nYou just tried to reply, but the quality control rejected your reply\n"
    updated_system_prompt += f"## Your attempted answer:\n{reply}\n\n"
    updated_system_prompt += f"## Reason for rejection:\n{feedback}\n\n"
    messages = [{"role": "system", "content": updated_system_prompt}] + history + [{"role": "user", "content": message}]
    response = openai.chat.completions.create(model=model_name, messages=messages)
    return response.choices[0].message.content

def chat(message, history):
    if "patent" in message:
        system = system_prompt +"\n\nEverything in your reply needs to be in pig latin - \
              it is mandatory that you respond only and entirely in pig latin"
    else:
        system=system_prompt
    messages=[{"role":"system","content":system}]+ history + [{"role":"user","content":message}]
    response = openai.chat.completions.create(model=model_name,messages=messages)
    reply=response.choices[0].message.content

    evaluation = evaluate(reply,message,history)
    if evaluation.is_acceptable:
        print("Passed evaluation -returning reply")
    else:
        print("Failed evaluation - retrying")
        print(evaluation.feedback)
        reply = rerun(reply,message,history,evaluation.feedback)
    return reply


gr.ChatInterface(chat,type="messages").launch()
