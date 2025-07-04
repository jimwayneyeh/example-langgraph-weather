import os
from typing import TypedDict, Annotated
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from tools import get_weather
from dotenv import load_dotenv

load_dotenv()

# Set up the Gemini model
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=os.getenv("GEMINI_API_KEY"))

# Bind the weather tool to the model
tools = [get_weather]
llm_with_tools = llm.bind_tools(tools)

# Define the state for our graph
class AgentState(TypedDict):
    messages: Annotated[list, lambda x, y: x + y]

# Define the nodes for our graph
from langchain_core.messages import BaseMessage, SystemMessage

def agent_node(state):
    # Add a system message to give the agent clear instructions
    messages_with_system_prompt = [
        SystemMessage(content="You are a helpful assistant that has access to a tool for getting the weather. Use it when the user asks about the weather.")
    ] + state["messages"]
    
    response = llm_with_tools.invoke(messages_with_system_prompt)
    return {"messages": [response]}

tool_node = ToolNode(tools)

# Define the conditional logic for agetn
def should_continue(state):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END

# Build the graph
workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)
workflow.set_entry_point("agent")
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        END: END
    }
)
workflow.add_edge("tools", "agent")

# Compile the graph
app = workflow.compile()
