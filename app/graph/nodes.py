from typing import TypedDict, Annotated, TypeVar
import operator
from langchain_core.runnables import RunnableLambda
from app.config import gpt4o, deepseek
from .prompts import (
     CONTEXT_TIME_PROMPT,
     CONTEXT_SPACE_PROMPT,
     ANALYST_MACRO_PROMPT,
     ANALYST_INDUSTRY_PROMPT,
     ANALYST_COMPANY_PROMPT,
     ANALYST_TRADING_PROMPT,
     WARREN_BUFFETT_PROMPT,
)

T = TypeVar('T')

def take_latest(old_value, new_value) -> T:
    return new_value

class State(TypedDict):
    news_input: Annotated[str, take_latest]
    ticker: Annotated[str, take_latest]
    context_time_output: Annotated[str, take_latest]
    context_space_output: Annotated[str, take_latest]
    analyst_macro_output: Annotated[str, take_latest]
    analyst_industry_output: Annotated[str, take_latest]
    analyst_company_output: Annotated[str, take_latest]
    analyst_trading_output: Annotated[str, take_latest]
    warren_buffett_output: Annotated[str, take_latest]

def create_node_functions():
    # Create processing chains
    context_time_chain = CONTEXT_TIME_PROMPT | deepseek
    context_space_chain = CONTEXT_SPACE_PROMPT | deepseek
    analyst_macro_chain = ANALYST_MACRO_PROMPT | deepseek
    analyst_industry_chain = ANALYST_INDUSTRY_PROMPT | deepseek
    analyst_company_chain = ANALYST_COMPANY_PROMPT | deepseek
    analyst_trading_chain = ANALYST_TRADING_PROMPT | deepseek
    warren_buffett_chain = WARREN_BUFFETT_PROMPT | deepseek
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
    def start(state: State) -> State:
        return state

    def context_time(state: State) -> State:
        state["context_time_output"] = context_time_chain.invoke({"news_input": state["news_input"]}).content
        return state
    def context_space(state: State) -> State:
        state["context_space_output"] = context_space_chain.invoke({"news_input": state["news_input"]}).content
        return state
    def analyst_macro(state: State) -> State:
        state["analyst_macro_output"] = analyst_macro_chain.invoke({
            "context_time_output": state["context_time_output"],
            "context_space_output": state["context_space_output"],
            "ticker": state["ticker"]
            }).content
        return state
    def analyst_industry(state: State) -> State:
        state["analyst_industry_output"] = analyst_industry_chain.invoke({
            "context_time_output": state["context_time_output"],
            "context_space_output": state["context_space_output"],
            "ticker": state["ticker"]
            }).content
        return state
    def analyst_company(state: State) -> State:
        state["analyst_company_output"] = analyst_company_chain.invoke({
            "context_time_output": state["context_time_output"],
            "context_space_output": state["context_space_output"],
            "ticker": state["ticker"]
            }).content
        return state
    def analyst_trading(state: State) -> State:
        state["analyst_trading_output"] = analyst_trading_chain.invoke({
            "context_time_output": state["context_time_output"],
            "context_space_output": state["context_space_output"],
            "ticker": state["ticker"]
            }).content
        return state
    def warren_buffett(state: State) -> State:
        state["warren_buffett_output"] = warren_buffett_chain.invoke({
            "context_time_output": state["context_time_output"],
            "context_space_output": state["context_space_output"],
            "analyst_macro_output": state["analyst_macro_output"],
            "analyst_industry_output": state["analyst_industry_output"],
            "analyst_company_output": state["analyst_company_output"],
            "analyst_trading_output": state["analyst_trading_output"],
            "ticker": state["ticker"]
            }).content
        return state

    return {
        "start": RunnableLambda(start),
        "context_time": RunnableLambda(context_time),
        "context_space": RunnableLambda(context_space),
        "analyst_macro": RunnableLambda(analyst_macro),
        "analyst_industry": RunnableLambda(analyst_industry),
        "analyst_company": RunnableLambda(analyst_company),
        "analyst_trading": RunnableLambda(analyst_trading),
        "warren_buffett": RunnableLambda(warren_buffett)
    }
    """
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
    """