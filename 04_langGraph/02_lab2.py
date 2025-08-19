# from typing import Annotated, TypedDict
# from langgraph.graph import StateGraph, START, END
# from langgraph.graph.message import add_messages
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langsmith import traceable
# from dotenv import load_dotenv
# import os

# # Load env
# load_dotenv(override=True)

# # --- Step 1: Define State ---
# class State(TypedDict):
#     messages: Annotated[list, add_messages]

# # --- Step 2: Create Graph Builder ---
# graph_builder = StateGraph(State)

# # LLM with Gemini
# llm = ChatGoogleGenerativeAI(
#     model="gemini-2.0-flash-001",
#     google_api_key=os.getenv("GEMINI_ACCESS_KEY")
# )

# # --- Step 3: Create Nodes ---
# @traceable(name="chatbot_node")   # traces this node separately in LangSmith
# def chatbot(state: State):
#     response = llm.invoke(state["messages"])
#     return {"messages": [response]}

# graph_builder.add_node("chatbot", chatbot)

# # --- Step 4: Add Edges ---
# graph_builder.add_edge(START, "chatbot")
# graph_builder.add_edge("chatbot", END)

# # --- Step 5: Compile ---
# graph = graph_builder.compile()

# # --- Step 6: Run ---
# result = graph.invoke({"messages": [{"role": "user", "content": "Hey I need some help"}]})
# print("Final response:", result["messages"][-1].content)





from typing import Annotated,TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from IPython.display import Image, display
import gradio as gr
from langgraph.prebuilt import ToolNode, tools_condition
import requests
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langsmith import traceable
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain.agents import Tool

load_dotenv(override=True)

serper=GoogleSerperAPIWrapper()
serper.run("What is the capital of India?")


pushover_token=os.getenv("PUSHOVER_TOKEN")
pushover_user=os.getenv("PUSHOVER_USER")
pushover_url=os.getenv("PUSHOVER_URL")

def push(text: str):
    """ Send a push notification to the user """
    requests.post(pushover_url,data={"token":pushover_token,"user":pushover_user,"message":text})


tool_search=Tool(
    name="search",
    func=serper.run,
    description="Useful when we need more information from an online search"
)

tool_push=Tool(
    name="send_push_notification",
    func=push,
    description="useful for when we want to send a push notification"
)

tools=[tool_search,tool_push]


# Step 1: Define the State object
class State(TypedDict):
    messages:Annotated[list,add_messages]

# Step 2: Start the Graph Bbuilder with this State class
graph_builder=StateGraph(State)

llm=ChatGoogleGenerativeAI(model="gemini-2.0-flash-001",google_api_key=os.getenv('GEMINI_ACCESS_KEY'))
llm_with_toolss=llm.bind_tools(tools)


# Step 3: Create a Node
@traceable(name="chatbot_node")   # traces this node separately in LangSmith
def chatbot(state:State):
    return {"messages":[llm_with_toolss.invoke(state["messages"])]}

graph_builder.add_node("chatbot",chatbot)
graph_builder.add_node("tools",ToolNode(tools=tools))


# Step 4: Create Edges

graph_builder.add_conditional_edges("chatbot",tools_condition,"tools")

graph_builder.add_edge("tools","chatbot")
graph_builder.add_edge(START,"chatbot")
graph_builder.add_edge("chatbot", END)


# Step 5: Compile the Graph
graph=graph_builder.compile()


@traceable(name="chat")
def chat(user_input: str, history):
    result = graph.invoke({"messages":[{"role":"user","content":user_input}]})
    return result["messages"][-1].content

gr.ChatInterface(chat,type="messages").launch()