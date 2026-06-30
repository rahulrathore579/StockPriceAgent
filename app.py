from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os
import sys

# Ensure agent can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent import build_agent

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(title="Stock Price Agent API")

# Mount static directory for frontend
static_path = os.path.join(BASE_DIR, "static")
os.makedirs(static_path, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_path), name="static")

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

# Try to initialize the agent globally if API key is present
agent_executor = None
try:
    agent_executor = build_agent()
except ValueError:
    print("Warning: Agent could not be built initially. Ensure API key is set.")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    index_path = os.path.join(BASE_DIR, "static", "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    global agent_executor
    
    # Try initializing again if it failed before (e.g. key added later)
    if agent_executor is None:
        try:
            agent_executor = build_agent()
        except ValueError as e:
            raise HTTPException(status_code=500, detail=str(e))
            
    try:
        result = agent_executor.invoke({"input": request.message})
        return ChatResponse(response=result["output"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    # Make sure we don't block locally if testing
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
