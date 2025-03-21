from fastapi import APIRouter, Request, HTTPException, Depends, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Dict
import os
from tempfile import NamedTemporaryFile
from langchain_core.runnables.graph import MermaidDrawMethod
import logging 

from app.graph.workflow import create_workflow
from app.graph.simple_workflow import create_simple_workflow
from app.supabase import get_authenticated_user

logger = logging.getLogger("uvicorn")

router = APIRouter(
    prefix="/graph",
    tags=["graph"]
)

class GraphInput(BaseModel):
    input_text: str
    ticker: str

def cleanup_file(path: str):
    """Background task to clean up the temporary file"""
    try:
        os.unlink(path)
    except Exception as e:
        print(f"Error cleaning up file {path}: {e}")

@router.get("/draw")
async def draw_graph(background_tasks: BackgroundTasks):
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

    # Add cleanup to background tasks
    background_tasks.add_task(cleanup_file, filename)

    # Return the file
    return FileResponse(
        filename,
        media_type="image/png",
        filename="workflow_graph.png"
    )

@router.post("/simple-process")
async def process_with_simple_graph(input_data: GraphInput):
    # Create a new workflow instance for each request
    graph = create_simple_workflow()
    
    result = graph.invoke({
        "news_input": input_data.input_text,
        "ticker": input_data.ticker
    })
    return {"result": result}

@router.post("/process")
async def process_with_graph(input_data: GraphInput, streaming: bool = False):

    # Create a fresh state dictionary for each request
    initial_state = {
        "news_input": input_data.input_text,
        "ticker": input_data.ticker,
        "context_time_output": "",
        "context_space_output": "",
        "analyst_macro_output": "",
        "analyst_industry_output": "",
        "analyst_company_output": "",
        "analyst_trading_output": "",
        "warren_buffett_output": "",
        "summary_node_time": "",
        "context_time_time": "",
        "context_space_time": "",
        "analyst_macro_time": "",
        "analyst_industry_time": "",
        "analyst_company_time": "",
        "analyst_trading_time": "",
        "warren_buffett_time": "",
        "soros_output": "",
        "soros_time": "",
        "lynch_output": "",
        "lynch_time": "",
        "son_output": "",
        "son_time": "",
        "leijun_output": "",
        "leijun_time": "",
        "li_ka_shing_output": "",
        "li_ka_shing_time": "",
        "kai_fu_lee_output": "",
        "kai_fu_lee_time": "",
    }
    
    # Create a new workflow instance for each request
    graph = create_workflow()
    
    if streaming:
        from fastapi.responses import StreamingResponse
        import json
        
        async def generate_stream():
            # Use LangGraph's native streaming support
            async for event in graph.astream({
                "news_input": input_data.input_text,
                "ticker": input_data.ticker
            }, stream_mode=["custom"]):
                # Format as Server-Sent Event
                yield f"data: {json.dumps(event)}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive"
            }
        )
    else:
        result = graph.invoke(initial_state)
        return {"result": result}