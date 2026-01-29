import os
from typing import Optional, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Ajuste o import para onde seu orchestrator estiver de fato
from app.orchestrator import AIOrchestrator 

load_dotenv()

# Variável global para o singleton do agente
agent: Optional[AIOrchestrator] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação (Substitui o startup_event)"""
    global agent
    try:
        print("🚀 Inicializando AI Orchestrator...")
        agent = AIOrchestrator()
        print("✅ AI Agent pronto para uso")
        yield
    except Exception as e:
        print(f"❌ Erro crítico na inicialização: {e}")
        raise e
    finally:
        # Aqui você fecharia conexões se necessário
        print("Shutting down...")

app = FastAPI(
    title="Business Intelligence AI API",
    description="API para KPIs e análise de dados usando Agentes LangChain",
    version="1.0.0",
    lifespan=lifespan
)

# --- Middleware CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Schemas ---
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    success: bool
    error: Optional[str] = None

# --- Endpoints ---
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "agent_ready": agent is not None
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if agent is None:
        raise HTTPException(status_code=503, detail="Agente não inicializado")

    try:
        # A mágica acontece aqui: o handle_message agora usa Tools internamente
        response = agent.handle_message(request.message)

        return ChatResponse(
            response=response,
            success=True
        )

    except Exception as e:
        print(f"❌ Erro no processamento da mensagem: {e}")
        return ChatResponse(
            response="Desculpe, tive um problema ao processar sua consulta.",
            success=False,
            error=str(e)
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)