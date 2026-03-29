from os_assistant.core.states.os_assistant_state import OSAssistantState
from langgraph.graph import END
from os_assistant.utils.logger import get_logger
from os_assistant.core.settings import (
    QUERY_CLARIFICATION_NODE,
    QUERY_CLASSIFICATION_NODE,
    CLARIFICATION_NODE_MAX_ATTEMPTS,
)

logger = get_logger(__name__)

def route_query_after_starting(state: OSAssistantState) -> str:
    """
    Determines the next node to route the query to after the initial start node.

    Args:
        state (OSAssistantState): The current state of the OS Assistant.

    Returns:
        str: The name of the node to route the query to.
    """
    if state.query_clarification.is_clarification_needed:
        return QUERY_CLARIFICATION_NODE
    return QUERY_CLASSIFICATION_NODE

def route_query_after_classification(state: OSAssistantState) -> str:
    """
    Determines the next node to route the query to based on the current state of the OS Assistant.

    Args:
        state (OSAssistantState): The current state of the OS Assistant, including the query classification results.

    Returns:
        str: The name of the node to route the query to.
    """
    if (
        state.query_classification.requires_follow_up
        and state.clarification_attempts < CLARIFICATION_NODE_MAX_ATTEMPTS
    ):
        logger.info("Routing to query clarification node due to follow-up requirement.")
        return QUERY_CLARIFICATION_NODE

    return END
