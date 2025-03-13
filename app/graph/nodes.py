from typing import TypedDict, Annotated, TypeVar
import operator
from langchain_core.runnables import RunnableLambda
from app.config import gpt4o, deepseek
'''
from .prompts import (
    ANALYSIS_PROMPT,
    SENTIMENT_PROMPT,
    SUMMARY_PROMPT,
    FINAL_PROMPT
)
'''
from typing import Dict, Any
from langchain_core.runnables import RunnableConfig
from app.graph.prompts import CONTEXT_PROMPT, ANALYST_PROMPT, WB_PROMPT

async def context_analysis(data: Dict[str, Any], config: RunnableConfig) -> Dict[str, Any]:
    """上下文分析节点"""
    response = await CONTEXT_PROMPT.ainvoke({"input_text": data["input_text"]}, config)
    return {"context_analysis": response.content}

async def analyst_analysis(data: Dict[str, Any], config: RunnableConfig) -> Dict[str, Any]:
    """分析师深度分析节点"""
    response = await ANALYST_PROMPT.ainvoke({
        "input_text": data["input_text"],
        "context_analysis": data["context_analysis"]
    }, config)
    return {"analyst_analysis": response.content}

async def wb_generation(data: Dict[str, Any], config: RunnableConfig) -> Dict[str, Any]:
    """研报生成节点"""
    response = await WB_PROMPT.ainvoke({
        "input_text": data["input_text"],
        "context_analysis": data["context_analysis"],
        "analyst_analysis": data["analyst_analysis"]
    }, config)
    return {"wb_report": response.content}

T = TypeVar('T')

def take_latest(old_value, new_value) -> T:
    return new_value

class State(TypedDict):
    input_text: Annotated[str, take_latest]
    analysis: Annotated[str, take_latest]
    sentiment: Annotated[str, take_latest]
    summary: Annotated[str, take_latest]
    final_report: Annotated[str, take_latest]

def create_node_functions():
    # Create processing chains
    analysis_chain = ANALYSIS_PROMPT | gpt4o
    sentiment_chain = SENTIMENT_PROMPT | gpt4o
    summary_chain = SUMMARY_PROMPT | gpt4o
    final_chain = FINAL_PROMPT | gpt4o

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
        # Get the latest values from the lists
        state["final_report"] = final_chain.invoke({
            "analysis": state["analysis"],
            "sentiment": state["sentiment"],
            "summary": state["summary"]
        }).content
        return state

    return {
        "analyze": RunnableLambda(analyze),
        "analyze_sentiment": RunnableLambda(analyze_sentiment),
        "summarize": RunnableLambda(summarize),
        "compile": RunnableLambda(compile_report)
    }