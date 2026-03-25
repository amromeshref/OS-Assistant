from os_assistant.core.states.os_assistant_state import OSAssistantState
from os_assistant.core.graph.nodes.query_clarification import query_clarification_node
from os_assistant.core.graph.nodes.query_classification import query_classification_node
from os_assistant.core.graph.nodes.planner import planner_node
from os_assistant.core.graph.routing.logic import route_query_after_classification
from os_assistant.core.settings import (
    QUERY_CLASSIFICATION_NODE,
    QUERY_CLARIFICATION_NODE,
    PLANNER_NODE,
)

from os_assistant.utils.logger import get_logger
from langgraph.graph import StateGraph, END, START


logger = get_logger(__name__)

class OSAssistantGraph:
    def __init__(self):
        self.graph = self._build_os_assistant_graph()
        self.compiled_graph = None

    def _build_os_assistant_graph(self) -> StateGraph[OSAssistantState]:
        """
        Builds the state graph for the OS Assistant, defining the flow of states and transitions.
        Returns:
            StateGraph[OSAssistantState]: The constructed state graph for the OS Assistant.
        """
        logger.info("Building OS Assistant graph.")
        graph = StateGraph(OSAssistantState)

        graph.add_node(QUERY_CLASSIFICATION_NODE, query_classification_node)
        graph.add_node(QUERY_CLARIFICATION_NODE, query_clarification_node)
        graph.add_node(PLANNER_NODE, planner_node)

        graph.add_edge(START, QUERY_CLASSIFICATION_NODE)
        graph.add_conditional_edges(
            QUERY_CLASSIFICATION_NODE,
            route_query_after_classification,
            {
                QUERY_CLARIFICATION_NODE: QUERY_CLARIFICATION_NODE,
                PLANNER_NODE: PLANNER_NODE,
            },
        )
        graph.add_edge(QUERY_CLARIFICATION_NODE, QUERY_CLASSIFICATION_NODE)
        graph.add_edge(PLANNER_NODE, END)

        logger.info("OS Assistant graph built successfully.")

        return graph

    def compile(self) -> None:
        """
        Compiles the OS Assistant graph for execution.
        """
        logger.info("Compiling OS Assistant graph.")
        self.compiled_graph = self.graph.compile()
        logger.info("OS Assistant graph compiled successfully.")
    
    def execute(self, initial_state: OSAssistantState) -> OSAssistantState:
        """
        Executes the OS Assistant graph starting from the given initial state.
        Args:
            initial_state (OSAssistantState): The initial state to start the graph execution from.
        Returns:
            OSAssistantState: The final state after executing the graph.
        """        
        logger.info("Executing OS Assistant graph.")
        final_state = self.compiled_graph.invoke(initial_state)
        logger.info("OS Assistant graph execution completed.")
        return final_state