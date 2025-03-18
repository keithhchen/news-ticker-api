from langgraph.graph import Graph, END
from typing import Dict
from .prompts import SINGLE_SETH_PROMPT, SIMPLE_PROMPT_OUTPUT_SCHEMA
from app.config import gpt4o, deepseek, deepseek_openrouter_low
import json
import logging

logger = logging.getLogger("uvicorn")

def create_simple_workflow():
    # Create processing chain
    seth_chain = SINGLE_SETH_PROMPT | deepseek_openrouter_low

    def simple_analysis(state: Dict):
        output = seth_chain.invoke({
            "news_input": state["news_input"],
            "ticker": state["ticker"],
            "json_schema": json.dumps(SIMPLE_PROMPT_OUTPUT_SCHEMA, ensure_ascii=False, indent=2)
        }).content
        try:
            output = json.loads(output)
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON: {e}")
        return output

    # Create workflow graph
    workflow = Graph()

    # Add node
    workflow.add_node("simple_analysis", simple_analysis)

    # Add edge from input to analysis
    workflow.set_entry_point("simple_analysis")
    workflow.add_edge("simple_analysis", END)

    return workflow.compile()