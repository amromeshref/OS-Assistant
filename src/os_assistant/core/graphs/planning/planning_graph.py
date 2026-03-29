from os_assistant.core.states.os_assistant_state import OSAssistantState
from os_assistant.core.graphs.planning.nodes.planning import planning_node
from os_assistant.core.graphs.planning.nodes.user_validation import user_validation_node
from os_assistant.core.settings import (
    PLANNER_NODE,
    USER_VALIDATION_NODE,
)

from os_assistant.utils.logger import get_logger
from langgraph.graph import StateGraph, END, START

logger = get_logger(__name__)

class PlanningGraph(StateGraph):
    """
    The PlanningGraph is responsible for generating an execution plan based on the user's query and the information obtained from previous nodes (e.g., query classification and clarification). It also handles user validation of the generated plan before execution.
    """

    def __init__(self):
        self.graph = self._build_planning_graph()
        self.compiled_graph = None
    
    def _build_planning_graph(self) -> StateGraph[OSAssistantState]:
        """
        Builds the planning graph for the OS Assistant, which includes nodes for planning and user validation. The graph defines the flow of information and decision-making based on the user's query and the results of each node's processing.
        Returns:
            StateGraph[OSAssistantState]: The constructed planning graph.
        """
        graph = StateGraph(OSAssistantState)

        graph.add_node(PLANNER_NODE, planning_node)
        graph.add_node(USER_VALIDATION_NODE, user_validation_node)

        graph.add_edge(START, PLANNER_NODE)
        graph.add_edge(PLANNER_NODE, USER_VALIDATION_NODE)
        graph.add_edge(USER_VALIDATION_NODE, END)

        logger.info("Planning Graph built successfully.")

        return graph
    
    def compile(self) -> None:
        """
        Compiles the planning graph.
        """
        self.compiled_graph = self.graph.compile()
        logger.info("Planning Graph compiled successfully.")
    
    def execute(self, initial_state: OSAssistantState) -> OSAssistantState:
        """
        Executes the compiled planning graph starting from the given initial state.
        Args:
            initial_state (OSAssistantState): The initial state to start the graph execution from.
        Returns:
            OSAssistantState: The final state after executing the graph.
        """        
        logger.info("Executing Planning Graph.")
        final_state = self.compiled_graph.invoke(initial_state)
        final_state = OSAssistantState(**final_state)
        logger.info("Planning Graph execution completed.")
        return final_state