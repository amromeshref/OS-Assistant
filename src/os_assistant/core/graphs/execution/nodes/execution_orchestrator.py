from os_assistant.core.states.os_assistant_state import (
    OSAssistantState,
    ExecutionOrchestratorState,
)
from os_assistant.prompts.execution_orchestrator import get_execution_orchestrator_sys_prompt
from os_assistant.utils.helper_functions import command_executions_to_str, planning_state_to_str, variable_execution_contexts_to_str, information_responses_to_str
from os_assistant.utils.logger import get_logger
from os_assistant.core.models import LLMModel

logger = get_logger(__name__)

def execution_orchestrator_node(state: OSAssistantState) -> OSAssistantState:
    """
    This node is responsible for orchestrating the execution of commands based on the generated plan and user validation feedback. It manages the flow of execution, handles any necessary adjustments, and ensures that the assistant's actions align with the user's intentions and the overall plan.
    Args:
        state (OSAssistantState): The current state of the OS Assistant, including the generated plan, user validation feedback, and any relevant context.
    Returns:
        OSAssistantState: The updated state after orchestrating the execution, which may include the results of executed commands and any adjustments made to the plan based on execution outcomes.
    """
    logger.info("Starting execution orchestrator node.")

    llm_model = LLMModel()
    sys_prompt = get_execution_orchestrator_sys_prompt()

    if state.current_step_index == 0:
        human_message = f"""
This is the first turn of the execution orchestrator node. No steps have been executed yet.
Original user query: {state.finalized_enhanced_query}
Output Of Planning Node: {planning_state_to_str(state.planning)}
"""
    else:
        human_message = f"""
This is a subsequent turn of the execution orchestrator node. Some steps(information or command) have already been executed.
Original user query: {state.finalized_enhanced_query}
Output Of Planning Node: {planning_state_to_str(state.planning)}
Indices of steps done so far: {str(state.steps_done_indicies)}
Details of Executed command steps so far: {command_executions_to_str(state.command_executions)}
Details of Executed information steps so far: {information_responses_to_str(state.generated_information_responses)}
"""
        
    response: ExecutionOrchestratorState = llm_model.generate_response(
        system_message=sys_prompt,
        human_message=human_message,
        structured_output=ExecutionOrchestratorState,
    )

    # TODO: Implement parsing logic here

    # Update the variable execution contexts
    # if len(response.variable_execution_contexts) > 0:
    #     for var_context in response.variable_execution_contexts:
    #         state.variable_execution_contexts.append(var_context)

    state.execution_orchestrator.append(response)
    logger.info("Completed execution orchestrator node.")

    return state