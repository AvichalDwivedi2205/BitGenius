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
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Firebase on startup
@app.on_event("startup")
async def startup_event():
    initialize_firebase()

# Include routers
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(agents.router, prefix="/agents", tags=["Agents"])
app.include_router(logs.router, prefix="/logs", tags=["Logs"])
app.include_router(ai.router, prefix="/ai", tags=["AI"])

@app.get("/", tags=["Root"])
async def root():
    return {"message": "Welcome to BitGenius API", "status": "online"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
