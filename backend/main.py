# main.py
"""
FastAPI Server for Livestock Management AI Chat
Integrates LangChain AI Agent with Supabase
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv

from app.ai_agent import LivestockAgent

load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Livestock Management AI API",
    description="AI-powered chat API for livestock and insemination data",
    version="1.0.0"
)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI Agent (singleton)
agent = None

@app.on_event("startup")
async def startup_event():
    """Initialize AI agent on startup"""
    global agent
    try:
        print("🚀 Starting Livestock AI API...")
        agent = LivestockAgent()
        print("✅ AI Agent initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize AI Agent: {e}")
        raise


# Pydantic models for request/response
class ChatRequest(BaseModel):
    message: str
    language: Optional[str] = "en"  # 'en' or 'pt'

class ChatResponse(BaseModel):
    response: str
    success: bool
    error: Optional[str] = None

class StatsResponse(BaseModel):
    farms: int
    animals: int
    bulls: int
    protocols: int
    inseminations: int


# API Endpoints
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Livestock Management AI API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "agent_initialized": agent is not None,
        "environment": os.getenv("ENVIRONMENT", "unknown")
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint - sends user message to AI agent
    
    Args:
        request: ChatRequest with user message
        
    Returns:
        ChatResponse with AI agent's response
    """
    if not agent:
        raise HTTPException(
            status_code=503, 
            detail="AI Agent not initialized"
        )
    
    try:
        # Get response from AI agent
        response = agent.query(request.message)
        
        return ChatResponse(
            response=response,
            success=True
        )
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return ChatResponse(
            response="Sorry, I encountered an error processing your request.",
            success=False,
            error=str(e)
        )


@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """
    Get database statistics
    
    Returns:
        StatsResponse with counts of all entities
    """
    if not agent:
        raise HTTPException(
            status_code=503,
            detail="AI Agent not initialized"
        )
    
    try:
        stats = agent.get_database_stats()
        
        if "error" in stats:
            raise HTTPException(status_code=500, detail=stats["error"])
        
        return StatsResponse(**stats)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching statistics: {str(e)}"
        )


@app.get("/tables")
async def get_tables():
    """
    Get list of available database tables and their schemas
    """
    return {
        "tables": [
            {
                "name": "farms",
                "columns": ["id", "name", "state", "municipality", "created_at"]
            },
            {
                "name": "animals",
                "columns": ["id", "animal_number", "breed", "category", "farm_id", "created_at"]
            },
            {
                "name": "bulls",
                "columns": ["id", "bull_name", "bull_breed", "bull_company", "created_at"]
            },
            {
                "name": "protocols",
                "columns": ["id", "protocol_name", "protocol_days", "p4_implant", "company", "created_at"]
            },
            {
                "name": "inseminations",
                "columns": ["id", "animal_id", "bull_id", "protocol_id", "inseminator", "insemination_date", "result", "created_at"]
            }
        ]
    }


# Run with: uvicorn main:app --reload --host 0.0.0.0 --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )