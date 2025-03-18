from langgraph.types import StreamWriter
from typing import TypedDict, Annotated, TypeVar
import logging
from langchain_core.runnables import RunnableLambda
from app.config import gpt4o, deepseek, deepseek_openrouter
from .prompts import (
     SUMMARY_PROMPT,
     CONTEXT_TIME_PROMPT,
     CONTEXT_SPACE_PROMPT,
     ANALYST_MACRO_PROMPT,
     ANALYST_INDUSTRY_PROMPT,
     ANALYST_COMPANY_PROMPT,
     ANALYST_TRADING_PROMPT,
     WARREN_BUFFETT_PROMPT,
     SOROS_PROMPT,
     LYNCH_PROMPT,
     SON_PROMPT,
     LEIJUN_PROMPT,
     LI_KA_SHING_PROMPT,
     KAI_FU_LEE_PROMPT,
)
from time import time

logger = logging.getLogger("uvicorn")

T = TypeVar('T')

def take_latest(old_value, new_value) -> T:
    return new_value

class State(TypedDict):
    news_input: Annotated[str, take_latest]
    ticker: Annotated[str, take_latest]
    summary: Annotated[str, take_latest]
    context_time_output: Annotated[str, take_latest]
    context_space_output: Annotated[str, take_latest]
    analyst_macro_output: Annotated[str, take_latest]
    analyst_industry_output: Annotated[str, take_latest]
    analyst_company_output: Annotated[str, take_latest]
    analyst_trading_output: Annotated[str, take_latest]
    warren_buffett_output: Annotated[str, take_latest]
    soros_output: Annotated[str, take_latest]
    lynch_output: Annotated[str, take_latest]
    son_output: Annotated[str, take_latest]
    leijun_output: Annotated[str, take_latest]
    li_ka_shing_output: Annotated[str, take_latest]
    kai_fu_lee_output: Annotated[str, take_latest]

    summary_node_time: Annotated[float, take_latest]
    context_time_time: Annotated[float, take_latest]
    context_space_time: Annotated[float, take_latest]
    analyst_macro_time: Annotated[float, take_latest]
    analyst_industry_time: Annotated[float, take_latest]
    analyst_company_time: Annotated[float, take_latest]
    analyst_trading_time: Annotated[float, take_latest]
    warren_buffett_time: Annotated[float, take_latest]
    soros_time: Annotated[float, take_latest]
    lynch_time: Annotated[float, take_latest]
    son_time: Annotated[float, take_latest]
    leijun_time: Annotated[float, take_latest]
    li_ka_shing_time: Annotated[float, take_latest]
    kai_fu_lee_time: Annotated[float, take_latest]

def create_node_functions():
    # Create processing chains
    summary_chain = SUMMARY_PROMPT | deepseek_openrouter
    context_time_chain = CONTEXT_TIME_PROMPT | deepseek_openrouter
    context_space_chain = CONTEXT_SPACE_PROMPT | deepseek_openrouter
    analyst_macro_chain = ANALYST_MACRO_PROMPT | deepseek_openrouter
    analyst_industry_chain = ANALYST_INDUSTRY_PROMPT | deepseek_openrouter
    analyst_company_chain = ANALYST_COMPANY_PROMPT | deepseek_openrouter
    analyst_trading_chain = ANALYST_TRADING_PROMPT | deepseek_openrouter
    warren_buffett_chain = WARREN_BUFFETT_PROMPT | deepseek_openrouter
    soros_chain = SOROS_PROMPT | deepseek_openrouter
    lynch_chain = LYNCH_PROMPT | deepseek_openrouter
    son_chain = SON_PROMPT | deepseek_openrouter
    leijun_chain = LEIJUN_PROMPT | deepseek_openrouter
    li_ka_shing_chain = LI_KA_SHING_PROMPT | deepseek_openrouter
    kai_fu_lee_chain = KAI_FU_LEE_PROMPT | deepseek_openrouter


    def start(state: State, writer: StreamWriter):
        writer({"node_start": "新闻透视流程启动"})
        return state
 
    def summary_node(state: State, writer: StreamWriter, ):
        writer({"node": "summary_node", "type": "start", "message": "开始提取新闻核心内容"})
        start_time = time()
        output = summary_chain.invoke({"news_input": state["news_input"]}).content
        end_time = time()
        elapsed_time = end_time - start_time
        writer({"node": "summary_node", "type": "end", "message": "核心内容提取完毕"})
    #    writer({"node": "summary_node", "type": "output", "message": output})
        return {
            "summary": output,
            "summary_node_time": elapsed_time
        }

    def context_time(state: State, writer: StreamWriter):
        writer({"node": "context_time", "type": "start", "message": "进行空间维度信息补充"})
        start_time = time()
        output = context_time_chain.invoke({"news_input": state["news_input"]}).content
        end_time = time()
        elapsed_time = end_time - start_time
        writer({"node": "context_time", "type": "end", "message": "空间维度信息补充完毕"})
    #    writer({"node": "context_time", "type": "output", "message": output})
        return {
            "context_time_output": output,
            "context_time_time": elapsed_time
        }

    def context_space(state: State, writer: StreamWriter):
        writer({"node": "context_space", "type": "start", "message": "进行时间维度信息补充"})
        start_time = time()
        output = context_space_chain.invoke({"news_input": state["news_input"]}).content
        end_time = time()
        elapsed_time = end_time - start_time
        writer({"node": "context_space", "type": "end", "message": "时间维度信息补充完毕"})
    #    writer({"node": "context_space", "type": "output", "message": output})
        return {
            "context_space_output": output,
            "context_space_time": elapsed_time
        }

    def analyst_macro(state: State, writer: StreamWriter):
        writer({"node": "analyst_macro", "type": "start", "message": "经济学家开始分析"})
        start_time = time()
        output = analyst_macro_chain.invoke({
            "summary": state["summary"],
            "context_time_output": state["context_time_output"],
            "context_space_output": state["context_space_output"],
            "ticker": state["ticker"]
            }).content
        end_time = time()
        elapsed_time = end_time - start_time
        writer({"node": "analyst_macro", "type": "end", "message": "经济学家分析完毕"})
    #    writer({"node": "analyst_macro", "type": "output", "message": output})
        return {
            "analyst_macro_output": output,
            "analyst_macro_time": elapsed_time
        }

    def analyst_industry(state: State, writer: StreamWriter):
        writer({"node": "analyst_industry", "type": "start", "message": "行业研究员正在钻研"})
        start_time = time()
        output = analyst_industry_chain.invoke({
            "summary": state["summary"],
            "context_time_output": state["context_time_output"],
            "context_space_output": state["context_space_output"],
            "ticker": state["ticker"]
            }).content
        end_time = time()
        elapsed_time = end_time - start_time
        writer({"node": "analyst_industry", "type": "end", "message": "钻研完毕"})
    #    writer({"node": "analyst_industry", "type": "output", "message": output})
        return {
            "analyst_industry_output": output,
            "analyst_industry_time": elapsed_time
        }

    def analyst_company(state: State, writer: StreamWriter):
        writer({"node": "analyst_company", "type": "start", "message": "个股分析师正在进行公司研判"})
        start_time = time()
        output = analyst_company_chain.invoke({
            "summary": state["summary"],
            "context_time_output": state["context_time_output"],
            "context_space_output": state["context_space_output"],
            "ticker": state["ticker"]
            }).content
        end_time = time()
        elapsed_time = end_time - start_time
        writer({"node": "analyst_company", "type": "end", "message": "研判完毕"})
    #    writer({"node": "analyst_company", "type": "output", "message": output})
        return {
            "analyst_company_output": output,
            "analyst_company_time": elapsed_time
        }

    def analyst_trading(state: State, writer: StreamWriter):
        writer({"node": "analyst_trading", "type": "start", "message": "交易员开始分析"})
        start_time = time()
        output = analyst_trading_chain.invoke({
            "summary": state["summary"],
            "context_time_output": state["context_time_output"],
            "context_space_output": state["context_space_output"],
            "ticker": state["ticker"]
            }).content
        end_time = time()
        elapsed_time = end_time - start_time
        writer({"node": "analyst_trading", "type": "end", "message": "交易员分析完毕"})
    #    writer({"node": "analyst_trading", "type": "output", "message": output})
        return {
            "analyst_trading_output": output,
            "analyst_trading_time": elapsed_time
        }

    def warren_buffett(state: State, writer: StreamWriter):
        writer({"node": "warren_buffett", "type": "start", "message": "巴菲特正在思考"})
        start_time = time()
        output = warren_buffett_chain.invoke({
            "summary": state["summary"],
            "analyst_macro_output": state["analyst_macro_output"],
            "analyst_industry_output": state["analyst_industry_output"],
            "analyst_company_output": state["analyst_company_output"],
            "analyst_trading_output": state["analyst_trading_output"],
            "ticker": state["ticker"]
            }).content
        end_time = time()
        elapsed_time = end_time - start_time
        writer({"node": "warren_buffett", "type": "end", "message": "巴菲特心意已决"})
        writer({"node": "warren_buffett", "type": "output", "message": output})
        return {
            "warren_buffett_output": output,
            "warren_buffett_time": elapsed_time
        }

    def soros(state: State, writer: StreamWriter):
        writer({"node": "soros", "type": "start", "message": "索罗斯思索中"})
        start_time = time()
        output = soros_chain.invoke({
            "summary": state["summary"],
            "analyst_macro_output": state["analyst_macro_output"],
            "analyst_industry_output": state["analyst_industry_output"],
            "analyst_company_output": state["analyst_company_output"],
            "analyst_trading_output": state["analyst_trading_output"],
            "ticker": state["ticker"]
            }).content
        end_time = time()
        elapsed_time = end_time - start_time
        writer({"node": "soros", "type": "end", "message": "索罗斯有了答案"})
        writer({"node": "soros", "type": "output", "message": output})
        return {
            "soros_output": output,
            "soros_time": elapsed_time
        }

    def lynch(state: State, writer: StreamWriter):
        writer({"node": "lynch", "type": "start", "message": "彼得林奇接过了分析师们的初步成果"})
        start_time = time()
        output = lynch_chain.invoke({
            "summary": state["summary"],
            "analyst_macro_output": state["analyst_macro_output"],
            "analyst_industry_output": state["analyst_industry_output"],
            "analyst_company_output": state["analyst_company_output"],
            "analyst_trading_output": state["analyst_trading_output"],
            "ticker": state["ticker"]
            }).content
        end_time = time()
        elapsed_time = end_time - start_time
        writer({"node": "lynch", "type": "end", "message": "彼得林奇做出了决定"})
        writer({"node": "lynch", "type": "output", "message": output})
        return {
            "lynch_output": output,
            "lynch_time": elapsed_time
        }

    def son(state: State, writer: StreamWriter):
        writer({"node": "son", "type": "start", "message": "孙正义开始翻看材料"})
        start_time = time()
        output = son_chain.invoke({
            "summary": state["summary"],
            "analyst_macro_output": state["analyst_macro_output"],
            "analyst_industry_output": state["analyst_industry_output"],
            "analyst_company_output": state["analyst_company_output"],
            "analyst_trading_output": state["analyst_trading_output"],
            "ticker": state["ticker"]
            }).content
        end_time = time()
        elapsed_time = end_time - start_time
        writer({"node": "son", "type": "end", "message": "孙正义放下材料得出了结论"})
        writer({"node": "son", "type": "output", "message": output})
        return {
            "son_output": output,
            "son_time": elapsed_time
        }

    def leijun(state: State, writer: StreamWriter):
        writer({"node": "leijun", "type": "start", "message": "雷军正在研究 OK 不 OK"})
        start_time = time()
        output = leijun_chain.invoke({
            "summary": state["summary"],
            "analyst_macro_output": state["analyst_macro_output"],
            "analyst_industry_output": state["analyst_industry_output"],
            "analyst_company_output": state["analyst_company_output"],
            "analyst_trading_output": state["analyst_trading_output"],
            "ticker": state["ticker"]
            }).content
        end_time = time()
        elapsed_time = end_time - start_time
        writer({"node": "leijun", "type": "end", "message": "雷军OK 了"})
        writer({"node": "leijun", "type": "output", "message": output})
        return {
            "leijun_output": output,
            "leijun_time": elapsed_time
        }

    def li_ka_shing(state: State, writer: StreamWriter):
        writer({"node": "li_ka_shing", "type": "start", "message": "李嘉诚开始校准手表"})
        start_time = time()
        output = li_ka_shing_chain.invoke({
            "summary": state["summary"],
            "analyst_macro_output": state["analyst_macro_output"],
            "analyst_industry_output": state["analyst_industry_output"],
            "analyst_company_output": state["analyst_company_output"],
            "analyst_trading_output": state["analyst_trading_output"],
            "ticker": state["ticker"]
            }).content
        end_time = time()
        elapsed_time = end_time - start_time
        writer({"node": "li_ka_shing", "type": "end", "message": "校准完毕"})
        writer({"node": "li_ka_shing", "type": "output", "message": output})
        return {
            "li_ka_shing_output": output,
            "li_ka_shing_time": elapsed_time
        }

    def kai_fu_lee(state: State, writer: StreamWriter):
        writer({"node": "kai_fu_lee", "type": "start", "message": "李开复开始推演"})
        start_time = time()
        output = kai_fu_lee_chain.invoke({
            "summary": state["summary"],
            "analyst_macro_output": state["analyst_macro_output"],
            "analyst_industry_output": state["analyst_industry_output"],
            "analyst_company_output": state["analyst_company_output"],
            "analyst_trading_output": state["analyst_trading_output"],
            "ticker": state["ticker"]
            }).content
        end_time = time()
        elapsed_time = end_time - start_time
        writer({"node": "kai_fu_lee", "type": "end", "message": "李开复推演完毕"})
        writer({"node": "kai_fu_lee", "type": "output", "message": output})

        return {
            "kai_fu_lee_output": output,
            "kai_fu_lee_time": elapsed_time
        }

    return {
        "start": start,
        "summary_node": summary_node,
        "context_time": context_time,
        "context_space": context_space,
        "analyst_macro": analyst_macro,
        "analyst_industry": analyst_industry,
        "analyst_company": analyst_company,
        "analyst_trading": analyst_trading,
        "warren_buffett": warren_buffett,
        "soros": soros,
        "lynch": lynch,
        "son": son,
        "leijun": leijun,
        "li_ka_shing": li_ka_shing,
        "kai_fu_lee": kai_fu_lee
    }