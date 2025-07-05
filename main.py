import logging
import sys
import time
import asyncio
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

# --- Conversation State Management ---
# This dictionary will store the last access time for each conversation
conversation_last_access = {}
CONVERSATION_TIMEOUT_SECONDS = 1800  # 30 minutes

async def cleanup_expired_conversations():
    """Periodically checks for and removes expired conversations."""
    while True:
        await asyncio.sleep(600)  # Check every 10 minutes
        now = time.time()
        expired_ids = [
            conv_id for conv_id, last_access_time in conversation_last_access.items()
            if now - last_access_time > CONVERSATION_TIMEOUT_SECONDS
        ]
        
        for conv_id in expired_ids:
            logging.info(f"Removing expired conversation: {conv_id}")
            # The actual removal from MemorySaver is a bit complex as it's not directly exposed.
            # For this example, we'll just remove it from our tracking dict.
            # In a production scenario with RedisSaver, you'd use Redis's TTL feature.
            if conv_id in conversation_last_access:
                del conversation_last_access[conv_id]
                # Note: The state remains in MemorySaver but is now untracked by our cleanup.
                # A more robust solution would involve a custom Checkpointer or a DB with TTL.

app = FastAPI(
    title="LangGraph Weather Agent API",
    description="An API for interacting with a LangGraph agent that can use a weather tool and has conversation memory.",
    version="1.1.0",
)

@app.on_event("startup")
async def startup_event():
    """Starts the background cleanup task when the server starts."""
    asyncio.create_task(cleanup_expired_conversations())

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
    
    # Update the last access time for this conversation
    conversation_last_access[request.conversation_id] = time.time()

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
