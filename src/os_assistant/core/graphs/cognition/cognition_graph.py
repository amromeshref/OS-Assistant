from os_assistant.core.states.os_assistant_state import OSAssistantState
from os_assistant.core.graphs.cognition.nodes.query_clarification import query_clarification_node
from os_assistant.core.graphs.cognition.nodes.query_classification import query_classification_node
from os_assistant.core.graphs.cognition.routing.logic import route_query_after_classification, route_query_after_starting
from os_assistant.core.settings import (
    QUERY_CLASSIFICATION_NODE,
    QUERY_CLARIFICATION_NODE,
)

from os_assistant.utils.logger import get_logger
from langgraph.graph import StateGraph, END, START


logger = get_logger(__name__)

class CognitionGraph(StateGraph):
    def __init__(self):
        self.graph = self._build_cognition_graph()
        self.compiled_graph = None

    def _build_cognition_graph(self) -> StateGraph[OSAssistantState]:
        """
        Builds the cognition graph for the OS Assistant, which includes nodes for query classification and clarification. The graph defines the flow of information and decision-making based on the user's query and the results of each node's processing.
        Returns:
            StateGraph[OSAssistantState]: The constructed cognition graph.
        """
        graph = StateGraph(OSAssistantState)

        graph.add_node(QUERY_CLASSIFICATION_NODE, query_classification_node)
        graph.add_node(QUERY_CLARIFICATION_NODE, query_clarification_node)

        graph.add_conditional_edges(
            START,
            route_query_after_starting,
            {
                QUERY_CLARIFICATION_NODE: QUERY_CLARIFICATION_NODE,
                QUERY_CLASSIFICATION_NODE: QUERY_CLASSIFICATION_NODE,
            },
        )

        graph.add_conditional_edges(
            QUERY_CLASSIFICATION_NODE,
            route_query_after_classification,
            {
                QUERY_CLARIFICATION_NODE: QUERY_CLARIFICATION_NODE,
                END: END,
            },
        )
        
        graph.add_edge(QUERY_CLARIFICATION_NODE, END)

        logger.info("Cognition graph built successfully.")

        return graph

    def compile(self) -> None:
        """
        Compiles the cognition graph.
        """
        self.compiled_graph = self.graph.compile()
        logger.info("Cognition graph compiled successfully.")
    
    def execute(self, initial_state: OSAssistantState) -> OSAssistantState:
        """
        Executes the compiled cognition graph starting from the given initial state.
        Args:
            initial_state (OSAssistantState): The initial state to start the graph execution from.
        Returns:
            OSAssistantState: The final state after executing the graph.
        """        
        logger.info("Executing Cognition Graph.")
        final_state = self.compiled_graph.invoke(initial_state)
        final_state = OSAssistantState(**final_state)
        logger.info("Cognition Graph execution completed.")
        return final_state