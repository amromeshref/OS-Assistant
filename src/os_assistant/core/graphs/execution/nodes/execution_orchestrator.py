from os_assistant.core.states.os_assistant_state import (
    OSAssistantState,
    ExecutionOrchestratorState,
)
from os_assistant.prompts.execution_orchestrator import (
    get_execution_orchestrator_sys_prompt,
    get_first_human_message,
    get_second_human_message,
    get_human_message_after_action_input,
)
from os_assistant.utils.helper_functions import planning_state_to_str
from os_assistant.tools.retrieve_execution_details import retrieve_execution_details
from os_assistant.tools.retrieve_information_details import retrieve_information_details
from os_assistant.utils.logger import get_logger
from os_assistant.core.models.main import LLMModel

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

    if len(state.executed_steps) == 0:
        human_message = get_first_human_message(state)
    else:
        human_message = get_second_human_message(state)
    
    response = None

    while True:
        response: ExecutionOrchestratorState = llm_model.generate_response(
            system_message=sys_prompt,
            human_message=human_message,
            structured_output=ExecutionOrchestratorState
        )

        print(response.model_dump_json())

        # TODO: Implement parsing logic here

        state.execution_orchestrator.append(response)

        if response.is_blocked:
            state.executed_steps.append(response.blocked_reasoning)
            break

        if not response.action_required:
            break
        
        if response.action_type == "retrieve_execution_details":
            action_output = retrieve_execution_details(state)
        elif response.action_type == "retrieve_information_details":
            action_output = retrieve_information_details(state)
        
        print(action_output)
        
        human_message = get_human_message_after_action_input(state, action_output)
    

    # Update the variable execution contexts
    # if len(response.variable_execution_contexts) > 0:
    #     for var_context in response.variable_execution_contexts:
    #         state.variable_execution_contexts.append(var_context)

    if response.is_blocked:
        state.executed_steps.append(response.blocked_reasoning)
        
    logger.info("Completed execution orchestrator node.")

    return state
