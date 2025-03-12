from fastapi import APIRouter
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Dict
import operator
import os
from tempfile import NamedTemporaryFile
from langchain_core.runnables.graph import MermaidDrawMethod

from app.graph.workflow import create_workflow

router = APIRouter(
    prefix="/graph",
    tags=["graph"]
)

class GraphInput(BaseModel):
    input_text: str
    parameters: Optional[Dict] = None

async def cleanup_file(path: str):
    """Background task to clean up the temporary file after sending"""
    try:
        os.unlink(path)
    except Exception as e:
        print(f"Error cleaning up file {path}: {e}")

@router.get("/draw")
async def draw_graph():
    """Generate and return a visualization of the workflow graph"""
    # Create a temporary file
    temp = NamedTemporaryFile(delete=False, suffix='.png')
    filename = temp.name
    temp.close()

    # Create graph and draw it
    graph = create_workflow()
    graph.get_graph().draw_mermaid_png(
        draw_method=MermaidDrawMethod.API,
        output_file_path=filename
    )

    # Return the file and clean up afterwards
    return FileResponse(
        filename,
        media_type="image/png",
        filename="workflow_graph.png",
        background=cleanup_file(filename)
    )

@router.post("/process")
async def process_with_graph(input_data: GraphInput):
    # Create a fresh state dictionary for each request
    initial_state = {
        "input_text": input_data.input_text,
        "analysis": [],
        "sentiment": [],
        "summary": [],
        "final_report": []
    }
    
    # Create a new workflow instance for each request
    graph = create_workflow()
    result = graph.invoke(initial_state)
    return {"result": result} 