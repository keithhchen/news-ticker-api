from typing import TypedDict, Annotated, TypeVar
import operator
from langchain_core.runnables import RunnableLambda
from app.config import gpt4o, deepseek
from .prompts import (
     CONTEXT_PROMPT,
     ANALYST_PROMPT,
     WARREN_BUFFETT_PROMPT,
)

T = TypeVar('T')

def take_latest(old_value, new_value) -> T:
    return new_value

class State(TypedDict):
    news_input: Annotated[str, take_latest]
    context_output: Annotated[str, take_latest]
    ticker: Annotated[str, take_latest]
    analysts_output: Annotated[str, take_latest]
    warren_buffett_output: Annotated[str, take_latest]

def create_node_functions():
    # Create processing chains
    context_chain = CONTEXT_PROMPT | gpt4o
    analyst_chain = ANALYST_PROMPT | gpt4o
    warren_buffett_chain = WARREN_BUFFETT_PROMPT | gpt4o
    # final_chain = FINAL_PROMPT | gpt4o

    # Define node functions
    """
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
    """ 

    def context(state: State) -> State:
        state["context_output"] = context_chain.invoke({"news_input": state["news_input"]}).content
        return state
    def analyst(state: State) -> State:
        state["analysts_output"] = analyst_chain.invoke({"context_output": state["context_output"], "ticker": state["ticker"]}).content
        return state
    def warren_buffett(state: State) -> State:
        state["warren_buffett_output"] = warren_buffett_chain.invoke({
            "context_output": state["context_output"], 
            "analysts_output": state["analysts_output"], 
            "ticker": state["ticker"]
            }).content
        return state
    
    return {
        "context": RunnableLambda(context),
        "analyst": RunnableLambda(analyst),
        "warren_buffett": RunnableLambda(warren_buffett)
    }