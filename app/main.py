from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import TypedDict, Annotated
from operator import itemgetter
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langgraph.graph import StateGraph, END
from .models import GraphInput
from .prompts import (
    ANALYSIS_PROMPT,
    SENTIMENT_PROMPT,
    SUMMARY_PROMPT,
    FINAL_PROMPT
)
from .config import gpt4o, deepseek

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

# Define state structure
class State(TypedDict):
    input_text: str
    analysis: str | None
    sentiment: str | None
    summary: str | None
    final_report: str | None

def create_graph():
    # Create processing nodes using different LLMs
    analysis_chain = ANALYSIS_PROMPT | gpt4o
    sentiment_chain = SENTIMENT_PROMPT | deepseek
    summary_chain = SUMMARY_PROMPT | gpt4o
    final_chain = FINAL_PROMPT | deepseek

    # Define node functions
    def analyze(state: State) -> State:
        state["analysis"] = analysis_chain.invoke({"input_text": state["input_text"]}).content
        return state

    def analyze_sentiment(state: State) -> State:
        state["sentiment"] = sentiment_chain.invoke({"input_text": state["input_text"]}).content
        return state

    def summarize(state: State) -> State:
        state["summary"] = summary_chain.invoke({"input_text": state["input_text"]}).content
        return state

    def compile_report(state: State) -> State:
        state["final_report"] = final_chain.invoke({
            "analysis": state["analysis"],
            "sentiment": state["sentiment"],
            "summary": state["summary"]
        }).content
        return state

    # Create workflow
    workflow = StateGraph(State)
    
    # Add nodes
    workflow.add_node("analyze", RunnableLambda(analyze))
    workflow.add_node("sentiment", RunnableLambda(analyze_sentiment))
    workflow.add_node("summarize", RunnableLambda(summarize))
    workflow.add_node("compile", RunnableLambda(compile_report))

    # Define parallel execution paths
    workflow.set_entry_point("analyze")
    workflow.add_edge("analyze", "sentiment")
    workflow.add_edge("analyze", "summarize")
    
    # Join parallel paths at compile
    workflow.add_edge("sentiment", "compile")
    workflow.add_edge("summarize", "compile")
    
    # End the graph after compilation
    workflow.add_edge("compile", END)

    return workflow.compile()

@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI LangGraph Server"}

@app.post("/process")
async def process_text(input_data: GraphInput):
    graph = create_graph()
    result = graph.invoke({
        "input_text": input_data.input_text,
        "analysis": None,
        "sentiment": None,
        "summary": None,
        "final_report": None
    })
    return {"result": result} 