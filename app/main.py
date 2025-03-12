from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.controllers.text_controller import router as text_router
from app.api.controllers.graph_controller import router as graph_router

app = FastAPI(
    title="FastAPI Service",
    description="Combined API and LangGraph services",
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

# Include traditional API routes
app.include_router(text_router)
app.include_router(graph_router)

# Root endpoint
@app.get("/")
async def hello():
    return "hello world"