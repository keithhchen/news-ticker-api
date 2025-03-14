from typing import TypedDict, Annotated, TypeVar
import operator
import logging
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

logger = logging.getLogger("uvicorn")

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

    def start(state: State) -> State:
        return state

    def context_time(state: State):
        output = context_time_chain.invoke({"news_input": state["news_input"]}).content
        return {
            "context_time_output": output
        }
    def context_space(state: State):
        output = context_space_chain.invoke({"news_input": state["news_input"]}).content
        return {
            "context_space_output": output
        }
    def analyst_macro(state: State):
        logger.info("starting analyst_macro")
        output = analyst_macro_chain.invoke({
            "context_time_output": state["context_time_output"],
            "context_space_output": state["context_space_output"],
            "ticker": state["ticker"]
            }).content
        return {
            "analyst_macro_output": output
        }
    def analyst_industry(state: State):
        output = analyst_industry_chain.invoke({
            "context_time_output": state["context_time_output"],
            "context_space_output": state["context_space_output"],
            "ticker": state["ticker"]
            }).content
        return {
            "analyst_industry_output": output
        }
    def analyst_company(state: State):
        output = analyst_company_chain.invoke({
            "context_time_output": state["context_time_output"],
            "context_space_output": state["context_space_output"],
            "ticker": state["ticker"]
            }).content
        return {
            "analyst_company_output": output
        }
    def analyst_trading(state: State):
        output = analyst_trading_chain.invoke({
            "context_time_output": state["context_time_output"],
            "context_space_output": state["context_space_output"],
            "ticker": state["ticker"]
            }).content
        return {
            "analyst_trading_output": output
        }
    def warren_buffett(state: State):
        output = warren_buffett_chain.invoke({
            "context_time_output": state["context_time_output"],
            "context_space_output": state["context_space_output"],
            "analyst_macro_output": state["analyst_macro_output"],
            "analyst_industry_output": state["analyst_industry_output"],
            "analyst_company_output": state["analyst_company_output"],
            "analyst_trading_output": state["analyst_trading_output"],
            "ticker": state["ticker"]
            }).content
        return {
            "warren_buffett_output": output
        }

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

    # def analyst(state: State) -> State:
    #     state["analysts_output"] = analyst_chain.invoke({"context_output": state["context_output"], "ticker": state["ticker"]}).content
    #     return state
    # def warren_buffett(state: State) -> State:
    #     state["warren_buffett_output"] = warren_buffett_chain.invoke({
    #         "context_output": state["context_output"], 
    #         "analysts_output": state["analysts_output"], 
    #         "ticker": state["ticker"]
    #         }).content
    #     return state
    
    # return {
    #     "context": RunnableLambda(context),
    #     "analyst": RunnableLambda(analyst),
    #     "warren_buffett": RunnableLambda(warren_buffett)
    # }