from os_assistant.core.states.os_assistant_state import (
    OSAssistantState,
    FinalResponse
)
from os_assistant.prompts.final_response import get_final_response_sys_prompt

from os_assistant.utils.logger import get_logger
from os_assistant.core.models import LLMModel

logger = get_logger(__name__)

def final_response_node(state: OSAssistantState) -> OSAssistantState:
    """
    """
    logger.info("Starting final response node.")

    llm_model = LLMModel()
    sys_prompt = get_final_response_sys_prompt()

    human_message = f"""
User's Original Query: {state.finalized_enhanced_query}
Short summary of how the user's query should be handeled: {state.planning.fulfillment_summary}
"""
    if len(state.command_executions) != 0:
        command_executions_str = ""
        for command_execution in state.command_executions:
            command_executions_str += command_execution.model_dump_json() + "\n"

        human_message += f"""
Command Execution Details:
{command_executions_str}
"""

    if len(state.generated_information_responses) != 0:
        information_responses_str = ""
        for information_response in state.generated_information_responses:
            information_responses_str += information_response.model_dump_json() + "\n"

        human_message += f"""
Information Responses Details:
{information_responses_str}
"""
    
    response: FinalResponse = llm_model.generate_response(
        human_message=human_message,
        system_message=sys_prompt,
        structured_output=FinalResponse,
    )

    # TODO: Add parse logic here

    state.final_response_status = "completed"
    logger.info("Completed final response node.")

    state.final_response = response

    return state