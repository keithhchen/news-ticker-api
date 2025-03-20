import os
from dotenv import load_dotenv
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

# Initialize Sentry
sentry_sdk.init(
    dsn="https://2ded3c4c2b59666a9a497bca55a29c27@o4509010374754304.ingest.de.sentry.io/4509010400837712",
    integrations=[
        FastApiIntegration()
    ],
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)

from app.api.controllers.text_controller import router as text_router
from app.api.controllers.graph_controller import router as graph_router
from app.api.controllers.stock_controller import router as stock_router
from app.api.controllers.news_controller import router as news_router
from app.supabase import get_authenticated_user

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
app.include_router(stock_router)
app.include_router(news_router)

# Root endpoint
@app.get("/")
async def hello():
    return { "detail": "hello world" }

@app.get("/profile")
async def profile(user=Depends(get_authenticated_user)):
    return user