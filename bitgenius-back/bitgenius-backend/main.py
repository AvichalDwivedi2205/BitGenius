import os
from dotenv import load_dotenv

load_dotenv()

if not os.environ.get("MAESTRO_API_KEY"):
    os.environ["MAESTRO_API_KEY"] = "test_9uXypd7GsdjAYXXskswIhMUf"  
    os.environ["MAESTRO_URL"] = "https://xbt-testnet.gomaestro-api.org/v0"
    os.environ["CONTRACT_ADDRESS"] = "ST1PQHQKV0RJXZFY1DGX8MNSNYVE3VGZJSRTPGZGM"

import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from routers import dashboard, agents, logs, ai
from services.firebase import initialize_firebase

app = FastAPI(
    title="BitGenius API",
    description="Backend API for BitGenius Bitcoin Agent Platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    initialize_firebase()

app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(agents.router, prefix="/agents", tags=["Agents"])
app.include_router(logs.router, prefix="/logs", tags=["Logs"])
app.include_router(ai.router, prefix="/ai", tags=["AI"])

@app.get("/", tags=["Root"])
async def root():
    return {"message": "Welcome to BitGenius API", "status": "online"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    debug = os.getenv("DEBUG", "False").lower() == "true"
    uvicorn.run("main:app", host=host, port=port, reload=debug)
