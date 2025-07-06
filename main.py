import logging
import sys

from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel, Field
from langgraph.graph import END
from graph import app as langgraph_app, checkpointer
from langchain_core.messages import HumanMessage
from uuid import uuid4

# --- Advanced Logging Setup ---
# Overwrite the log file on each run
LOG_FILE_PATH = "app.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE_PATH, mode='w', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

app = FastAPI(
    title="LangGraph Weather Agent API",
    description="An API for interacting with a LangGraph agent that can use a weather tool and has conversation memory.",
    version="1.1.0",
)

@app.on_event("startup")
async def startup_event():
    """Startup event for the FastAPI application."""
    pass

class AgentRequest(BaseModel):
    message: str
    conversation_id: str = Field(default_factory=lambda: str(uuid4()))

@app.post("/agent-invoke")
def invoke_agent(request: AgentRequest, background_tasks: BackgroundTasks):
    """
    Invokes the LangGraph agent with a user message and returns the final response.
    Manages conversation state using a conversation_id.
    """
    logging.info(f"Received request for conversation {request.conversation_id}: {request.message}")

    inputs = [HumanMessage(content=request.message)]
    
    # The config now includes the conversation_id to maintain state
    config = {"configurable": {"thread_id": request.conversation_id}}
    
    response = langgraph_app.invoke({"messages": inputs}, config=config)
    
    logging.info(f"LangGraph final response for {request.conversation_id}: {response}")

    # The final response is the last message from the agent
    final_message = response["messages"][-1]
    
    return {
        "response": final_message.content,
        "conversation_id": request.conversation_id
    }

@app.get("/")
def read_root():
    return {"status": "LangGraph Weather Agent is running"}
