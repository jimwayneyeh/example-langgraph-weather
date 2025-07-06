import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from tools import get_weather
from dotenv import load_dotenv
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import chat_agent_executor

load_dotenv()

# Set up the Gemini model
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=os.getenv("GOOGLE_API_KEY"))

# Bind the weather tool to the model
tools = [get_weather]
llm_with_tools = llm.bind_tools(tools)

# This is our checkpointer, responsible for saving and loading conversation state
checkpointer = MemorySaver()

# Define the agent state
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

# Define the nodes
def agent(state: AgentState):
    """Invokes the agent LLM."""
    # Prepend a system message to guide the agent.
    # Note: In a more complex app, you might add this only once.
    system_prompt = SystemMessage(content="You are a helpful assistant with access to a weather tool. Use it when asked about the weather.")
    messages_with_prompt = [system_prompt] + state["messages"]
    response = llm_with_tools.invoke(messages_with_prompt)
    return {"messages": [response]}

tool_node = ToolNode(tools)

# Define the graph
graph_builder = StateGraph(AgentState)
graph_builder.add_node("agent", agent)
graph_builder.add_node("tools", tool_node)

# Define the edges
def should_continue(state: AgentState):
    """
    Checks the last message from the agent.
    If it contains tool calls, route to the tool node.
    Otherwise, end the conversation.
    """
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END

graph_builder.add_conditional_edges("agent", should_continue)
graph_builder.add_edge("tools", "agent")
graph_builder.set_entry_point("agent")

# Compile the graph
app = graph_builder.compile(checkpointer=checkpointer)
