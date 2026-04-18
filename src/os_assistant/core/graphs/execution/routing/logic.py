from flask import logging

from os_assistant.core.states.os_assistant_state import OSAssistantState
from os_assistant.utils.logger import get_logger
from os_assistant.core.settings import (
    INFORMATION_NODE,
    CODE_EXECUTION_NODE,
    FINAL_RESPONSE_NODE,
    EXECUTION_ORCHESTRATOR_NODE,
    STEP_RESOLVER_NODE,
)

from os_assistant.utils.helper_functions import save_debug_state

logger = get_logger(__name__)


def route_after_starting(state: OSAssistantState) -> str:
    """
    Route after starting the graph based on user validation and query classification.
    """
    if state.user_validation.user_feedback_type == "rejected":
        logger.info("User rejected the plan during validation, routing to final response node.")
        return FINAL_RESPONSE_NODE
    
    logger.info("Executing first step of the plan.")

    if state.planning.plan_steps[0].step_type == "command":
        return CODE_EXECUTION_NODE
    elif state.planning.plan_steps[0].step_type == "information":
        return INFORMATION_NODE

def router(state: OSAssistantState):
    """
    Main router function to determine the next node based on the current state of the OS Assistant.
    """
    save_debug_state(state, "Current state before routing.")

    if state.steps_resolver_active:
        current_resolving_step_index = state.current_resolving_step_index

        logger.info(f"Routing to next resolved step with the index ({current_resolving_step_index}).")
        next_resolved_step = state.steps_resolver[-1].resolved_steps[current_resolving_step_index]
        if next_resolved_step.step_type == "command":
            return CODE_EXECUTION_NODE
        elif next_resolved_step.step_type == "information":
            return INFORMATION_NODE
            
    total_steps = len(state.planning.plan_steps)

    if state.current_step_index >= total_steps:
        return FINAL_RESPONSE_NODE
    
    next_step = state.planning.plan_steps[state.current_step_index]
    if next_step.dependencies_required:
        logger.info(f"Next step ({state.current_step_index}) has dependencies, routing to step resolver.")
        #save_debug_state(state, "Routing to step resolver due to dependencies.")
        return STEP_RESOLVER_NODE
    
    logger.info(f"Routing to next step ({state.current_step_index}) without dependencies.")

    if next_step.step_type == "command":
        return CODE_EXECUTION_NODE
    elif next_step.step_type == "information":
        return INFORMATION_NODE

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