"""
Axiom PWA - FastAPI Backend Main Application
Clean, coherent AI collaboration platform
"""

import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv

# Load environment variables FIRST (auto-resolves .env up the directory tree)
load_dotenv()

from api.messages import router as messages_router
from api.sessions import router as sessions_router
from core.session_manager import SessionManager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Global session manager
session_manager = SessionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    print("🚀 Axiom PWA Backend starting...")
    yield
    # Shutdown
    print("🛑 Axiom PWA Backend shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Axiom PWA Backend",
    description="Coherent AI collaboration platform",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware for PWA
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(sessions_router, prefix="/api")
app.include_router(messages_router, prefix="/api")


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time communication"""
    await websocket.accept()

    # Register WebSocket connection with session
    session_manager.add_websocket(session_id, websocket)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()

            # Handle different message types
            if data["type"] == "message":
                await session_manager.handle_websocket_message(
                    session_id, data["content"], websocket
                )
            elif data["type"] == "interrupt_task":
                await session_manager.interrupt_task(
                    session_id, data["task_id"], websocket
                )

    except WebSocketDisconnect:
        session_manager.remove_websocket(session_id, websocket)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "Axiom PWA Backend running", "version": "0.1.0"}


# Mount static files for PWA frontend
if os.path.exists("../frontend"):
    app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
