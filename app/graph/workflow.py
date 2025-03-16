from langgraph.graph import StateGraph, END
from .nodes import State, create_node_functions

def create_workflow():
    workflow = StateGraph(State)
    nodes = create_node_functions()
    
    # Add nodes
    for name, node in nodes.items():
        workflow.add_node(name, node)
    
    # Define a chained execution path
    workflow.set_entry_point("start")

    
    workflow.add_edge("start", "summary_node")
    workflow.add_edge("start", "context_time")
    workflow.add_edge("start", "context_space")

    workflow.add_edge(["summary_node","context_time","context_space"], "analyst_macro")

    workflow.add_edge(["summary_node","context_time","context_space"], "analyst_industry")

    workflow.add_edge(["summary_node","context_time","context_space"], "analyst_company")

    workflow.add_edge(["summary_node","context_time","context_space"], "analyst_trading")

    workflow.add_edge(["analyst_macro","analyst_industry","analyst_company","analyst_trading"], "warren_buffett")
    

    workflow.add_edge("warren_buffett", END)

    return workflow.compile()