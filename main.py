import logging
import sys
import asyncio
import json
from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.responses import StreamingResponse, FileResponse
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
    version="1.2.1", # Version updated for streaming fix
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

async def stream_agent_events(message: str, conversation_id: str):
    """
    A generator function that streams agent events for a given request.
    """
    inputs = {"messages": [HumanMessage(content=message)]}
    config = {"configurable": {"thread_id": conversation_id}}
    
    logging.info(f"Starting stream for conversation {conversation_id} with message: {message}")

    # astream_events returns an async generator that we can iterate over
    async for event in langgraph_app.astream_events(inputs, config, version="v1"):
        kind = event["event"]
        
        # We are looking for events where the LLM is streaming back tokens
        if kind == "on_chat_model_stream":
            content = event["data"]["chunk"].content
            if content:
                # SSE format: data: <json_string>\n\n
                logging.debug(f"Streaming content: {content}")
                yield f"data: {json.dumps({'type': 'chunk', 'content': content})}\n\n"
        elif kind == "on_tool_end":
            # Also stream back the output of the tool
            tool_output = event["data"].get("output")
            if tool_output:
                logging.info(f"Streaming tool output: {tool_output}")
                yield f"data: {json.dumps({'type': 'tool_end', 'content': tool_output})}\n\n"

    # Signal the end of the stream
    logging.info(f"Stream finished for conversation {conversation_id}")
    yield f"data: {json.dumps({'type': 'stream_end'})}\n\n"


@app.get("/stream")
async def stream(message: str, conversation_id: str):
    """
    Endpoint to stream the agent's response using Server-Sent Events.
    Accepts GET requests with query parameters.
    """
    return StreamingResponse(stream_agent_events(message, conversation_id), media_type="text/event-stream")


@app.get("/")
async def read_root():
    return FileResponse('templates/index.html')
