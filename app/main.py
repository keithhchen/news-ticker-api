from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.runnables import RunnablePassthrough
from langgraph.graph import StateGraph
from pydantic import BaseModel

app = FastAPI(
    title="FastAPI LangGraph Server",
    description="A FastAPI server with LangGraph integration",
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

@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI LangGraph Server"}

# Example of a simple graph
def create_graph():
    workflow = StateGraph(nodes=[])
    
    # Add your graph nodes and edges here
    # This is just a placeholder
    workflow.add_node("start", RunnablePassthrough())
    
    workflow.set_entry_point("start")
    return workflow.compile()

@app.get("/graph")
async def run_graph():
    graph = create_graph()
    result = graph.invoke({"input": "test"})
    return {"result": result} 