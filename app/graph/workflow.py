
from langchain_core.graphs import StateGraph
from app.graph.nodes import (
    context_analysis,
    analyst_analysis,
    wb_generation
)

def create_financial_analysis_graph() -> StateGraph:
    """创建金融分析工作流"""
    workflow = StateGraph()

    # 添加节点
    workflow.add_node("context_analysis", context_analysis)
    workflow.add_node("analyst_analysis", analyst_analysis)
    workflow.add_node("wb_generation", wb_generation)

    # 设置节点间的连接
    workflow.add_edge("context_analysis", "analyst_analysis")
    workflow.add_edge("analyst_analysis", "wb_generation")

    # 设置入口和出口
    workflow.set_entry_point("context_analysis")
    workflow.set_finish_point("wb_generation")

    return workflow.compile()