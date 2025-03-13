from langgraph.graph import StateGraph, END
from .nodes import State, create_node_functions

def create_workflow():
    workflow = StateGraph(State)
    nodes = create_node_functions()
    
    # Add nodes
    for name, node in nodes.items():
        workflow.add_node(name, node)

    # Define parallel execution paths
    """
    workflow.set_entry_point("analyze")
    workflow.add_edge("analyze", "analyze_sentiment")
    workflow.add_edge("analyze", "summarize")
    """

    # Define a chained execution path
    workflow.set_entry_point("context")
    workflow.add_edge("context", "analyst")
    workflow.add_edge("analyst", "warren_buffett")
    """
    # Join parallel paths at compile
    workflow.add_edge(["summarize", "analyze_sentiment"], "compile")
    
    # End the graph after compilation
    workflow.add_edge("compile", END)
    """
    workflow.add_edge("warren_buffett", END)

    return workflow.compile() 