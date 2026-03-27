from os_assistant.core.states.os_assistant_state import OSAssistantState
from os_assistant.utils.logger import get_logger
from os_assistant.core.settings import (
    CODE_EXECUTION_NODE,
    INFORMATION_NODE,
    FINAL_RESPONSE_NODE,
)

logger = get_logger(__name__)


def route_after_starting(state: OSAssistantState) -> str:
    """
    """
    #add logging
    if state.query_classification.query_type == "information":
        return INFORMATION_NODE
    return CODE_EXECUTION_NODE

def route_after_code_execution(state: OSAssistantState) -> str:
    """
    """
    #add logging
    if state.query_classification.query_type == "command":
        return FINAL_RESPONSE_NODE
    return INFORMATION_NODE
