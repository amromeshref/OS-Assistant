from os_assistant.core.states.os_assistant_state import (
    OSAssistantState,
)
from os_assistant.prompts.final_response import get_final_response_sys_prompt

from os_assistant.utils.logger import get_logger
from os_assistant.core.models.main import LLMModel
from os_assistant.utils.helper_functions import command_executions_to_str, information_responses_to_str, planning_state_to_str

logger = get_logger(__name__)

def final_response_node(state: OSAssistantState) -> OSAssistantState:
    """
    Node responsible for generating the final response to the user after all planning, code execution, and information generation steps are completed.
    This node takes into account the entire execution process, including any user feedback during validation, to generate a comprehensive final response.
    """
    logger.info("Starting final response node.")

    llm_model = LLMModel()
    sys_prompt = get_final_response_sys_prompt()

    if state.user_validation.user_feedback_type == "rejected":
        human_message = f"""
User rejected the plan during validation.
User's Original Query: {state.finalized_enhanced_query}
Planning State: {planning_state_to_str(state.planning)}
Conversatin history till now: {str(state.multi_turn_conversation_history)}
"""       
    else:
        human_message = f"""
User's Original Query: {state.finalized_enhanced_query}
Short summary of how the user's query should be handeled: {state.planning.fulfillment_summary}
Command Executions:
{command_executions_to_str(state.command_executions)}
Information Responses:
{information_responses_to_str(state.generated_information_responses)}
Short summary of the steps(information or command) that have already been executed: {str(state.executed_steps)}
"""
    
    response: str = llm_model.generate_response(
        human_message=human_message,
        system_message=sys_prompt,
        structured_output=None,
    )

    # TODO: Add parse logic here

    state.final_response_status = "completed"
    logger.info("Completed final response node.")

    state.generated_final_response = response

    return state