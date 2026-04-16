from flask import logging

from os_assistant.core.states.os_assistant_state import OSAssistantState
from os_assistant.utils.logger import get_logger
from os_assistant.core.settings import (
    INFORMATION_NODE,
    CODE_EXECUTION_NODE,
    FINAL_RESPONSE_NODE,
    EXECUTION_ORCHESTRATOR_NODE,
)

logger = get_logger(__name__)


def route_after_starting(state: OSAssistantState) -> str:
    """
    Route after starting the graph based on user validation and query classification.
    """
    if state.user_validation.user_feedback_type == "rejected":
        logger.info("User rejected the plan during validation, routing to final response node.")
        return FINAL_RESPONSE_NODE
    
    return EXECUTION_ORCHESTRATOR_NODE

def route_after_orchestrator(state: OSAssistantState) -> str:
    """
    Route after execution orchestrator node based on the next step determined by the orchestrator.
    """
    if state.execution_orchestrator[-1].is_blocked:
        return EXECUTION_ORCHESTRATOR_NODE

    next_step_type = state.execution_orchestrator[-1].next_step.step_type

    if next_step_type == "command":
        return CODE_EXECUTION_NODE
    elif next_step_type == "information":
        return INFORMATION_NODE

# def route_to_final_response(state: OSAssistantState) -> str:
#     """
#     Route to final response node after code execution or information generation based on the completion of all steps.
#     """
#     if state.current_step_index < state.total_steps:
#         return EXECUTION_ORCHESTRATOR_NODE
    
#     return FINAL_RESPONSE_NODE


def route_after_step_execution(state: OSAssistantState) -> str:
    """
    Route after executing a step(command/info).
    """
    #add logging
    if state.execution_orchestrator[-1].is_final_step:
        return FINAL_RESPONSE_NODE
    return EXECUTION_ORCHESTRATOR_NODE