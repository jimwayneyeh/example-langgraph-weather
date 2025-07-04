import logging
import sys
from fastapi import FastAPI
from pydantic import BaseModel
from langgraph.graph import END
from graph import app as langgraph_app
from langchain_core.messages import HumanMessage

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
    description="An API for interacting with a LangGraph agent that can use a weather tool.",
    version="1.0.0",
)

class AgentRequest(BaseModel):
    message: str

@app.post("/agent-invoke")
def invoke_agent(request: AgentRequest):
    """
    Invokes the LangGraph agent with a user message and returns the final response.
    """
    logging.info(f"Received request: {request.message}")
    inputs = [HumanMessage(content=request.message)]
    
    # The config will now use the logging setup
    response = langgraph_app.invoke({"messages": inputs})
    
    logging.info(f"LangGraph final response: {response}")

    # The final response is the last message from the agent
    final_message = response["messages"][-1]
    
    return {"response": final_message.content}

@app.get("/")
def read_root():
    return {"status": "LangGraph Weather Agent is running"}
