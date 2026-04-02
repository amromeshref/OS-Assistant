from os_assistant.core.states.os_assistant_state import OSAssistantState
from langgraph.graph import END
from os_assistant.utils.logger import get_logger
from os_assistant.core.settings import (
    USER_VALIDATION_NODE,
    PLANNING_NODE,
)
from langgraph.graph import END

logger = get_logger(__name__)

def route_after_starting(state: OSAssistantState) -> str:
    """
    Routes the flow after the START node based on whether user validation is required.
    If user validation is required, it routes to the USER_VALIDATION_NODE. Otherwise, it routes to the PLANNING_NODE to generate the execution/information plan.
    Args:        
        state (OSAssistantState): The current state of the OS Assistant, which includes information about the user's query and any preliminary processing results that may indicate whether user validation is needed.
    Returns:        
        str: The next node to route to, either USER_VALIDATION_NODE or PLANNING_NODE.
    """
    if state.user_validation.is_validation_required:
        return USER_VALIDATION_NODE
    return PLANNING_NODE

def route_after_planning(state: OSAssistantState) -> str:
    """
    Routes the flow after the planning node based on the query classification and whether follow-up is required.
    If the query is classified as "information" or if follow-up is required, it routes to the END node.
    Otherwise, it routes to the USER_VALIDATION_NODE for user validation of the generated plan.
    Args:        
        state (OSAssistantState): The current state of the OS Assistant, which includes information about the user's query, the results of query classification, and the planning results.
    Returns:        
        str: The next node to route to, either END or USER_VALIDATION_NODE.
    """
    if state.query_classification.query_type == "information" or state.planning.requires_follow_up:
        return END
    return USER_VALIDATION_NODE
