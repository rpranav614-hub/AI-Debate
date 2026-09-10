import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from src.config.settings import settings
from src.api.routes import router
from src.services.chat_history import ChatHistory  # NEW IMPORT
import uvicorn

app = FastAPI(
    title="AI Debate and Decision-Making System",
    description="Multi-Agent AI system for structured decision analysis",
    version="1.0.0",
    debug=settings.debug
)

# Initialize Chat History
chat_history = ChatHistory()  # NEW

# Include routes
app.include_router(router)


# ============ CHAT HISTORY ENDPOINTS (API) ============

@app.get("/history")
async def get_history(limit: int = 50):
    """Get recent chat history"""
    history = chat_history.get_history(limit)
    return {"history": history}


@app.get("/history/search")
async def search_history(q: str):
    """Search chat history by question"""
    history = chat_history.get_history_by_question(q)
    return {"history": history}


@app.delete("/history/{chat_id}")
async def delete_history(chat_id: int):
    """Delete a specific chat"""
    chat_history.delete_history(chat_id)
    return {"status": "deleted"}


@app.delete("/history/clear")
async def clear_history():
    """Clear all history"""
    chat_history.clear_all()
    return {"status": "cleared"}


@app.get("/")
async def root():
    return {
        "message": "AI Debate System is running!",
        "status": "active",
        "version": "1.0.0",
        "endpoints": {
            "debate": "/debate (POST)",
            "health": "/health (GET)",
            "agents": "/agents (GET)",
            "history": "/history (GET)",
            "history_search": "/history/search?q= (GET)",
            "history_delete": "/history/{id} (DELETE)",
            "history_clear": "/history/clear (DELETE)"
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="127.0.0.1",
        port=8000,
        reload=False
    )