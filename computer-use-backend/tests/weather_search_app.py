from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv
import asyncio

load_dotenv()

app = FastAPI(title="Computer Use Agent - Weather Search Demo")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for demo
sessions = {}
messages = {}

@app.get("/")
async def root():
    return {"message": "Computer Use Agent - Weather Search Demo", "status": "running"}

@app.get("/api/health")
async def health():
    api_key_set = bool(os.getenv('ANTHROPIC_API_KEY'))
    return {
        "status": "healthy",
        "api_key_configured": api_key_set,
        "service": "Weather Search Demo"
    }

@app.post("/api/sessions")
async def create_session(session_data: Dict[str, str]):
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "id": session_id,
        "name": session_data["name"],
        "status": "active",
        "created_at": datetime.now().isoformat(),
        "message_count": 0
    }
    messages[session_id] = []
    return sessions[session_id]

@app.get("/api/sessions")
async def list_sessions():
    return list(sessions.values())

@app.post("/api/sessions/{session_id}/messages")
async def send_message(session_id: str, message_data: Dict[str, str]):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    message_id = str(uuid.uuid4())
    message = {
        "id": message_id,
        "session_id": session_id,
        "role": "user",
        "content": message_data["content"],
        "timestamp": datetime.now().isoformat()
    }
    
    messages[session_id].append(message)
    sessions[session_id]["message_count"] += 1
    
    # Simulate weather search processing
    await asyncio.sleep(1)
    
    # Create agent response
    agent_message = {
        "id": str(uuid.uuid4()),
        "session_id": session_id,
        "role": "assistant", 
        "content": f"🌤️ Processing weather search: '{message_data['content']}'\n\nI'll search for weather information and provide you with current conditions and forecasts.",
        "timestamp": datetime.now().isoformat()
    }
    
    messages[session_id].append(agent_message)
    sessions[session_id]["message_count"] += 1
    
    return {
        "id": message_id,
        "session_id": session_id,
        "role": "user",
        "content": message_data["content"],
        "timestamp": message["timestamp"],
        "metadata": {"status": "processed"},
        "tool_executions": []
    }

@app.get("/api/sessions/{session_id}/messages")
async def get_messages(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return messages.get(session_id, [])

if __name__ == "__main__":
    import uvicorn
    
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("⚠️  ANTHROPIC_API_KEY not set - using demo mode")
    
    print("🚀 Starting Weather Search Demo Server...")
    print("🌐 Access: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("🏥 Health: http://localhost:8000/api/health")
    
    uvicorn.run("weather_search_app:app", host="0.0.0.0", port=8000, reload=True)
