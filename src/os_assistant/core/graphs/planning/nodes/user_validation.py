from os_assistant.core.states.os_assistant_state import OSAssistantState
from os_assistant.core.models import LLMModel
from os_assistant.prompts.user_validation import get_user_validation_sys_prompt
from os_assistant.utils.logger import get_logger

logger = get_logger(__name__)

def user_validation_node(state: OSAssistantState) -> OSAssistantState:
    """
    Validates the generated execution/information plan with the user to ensure it aligns with their original query and intentions.
    Args:
        state (OSAssistantState): The current state of the OS Assistant, including the generated execution/information plan.
    Returns:
        OSAssistantState: The updated state after user validation, which may include any adjustments to the plan based on user feedback.
    """
    logger.info("Starting user validation node.")

    llm_model = LLMModel()
    sys_prompt = get_user_validation_sys_prompt()
    
    human_message = f"""
User's original query: {state.original_query_enhanced}
Generated execution/information plan: {state.planning.model_dump_json()}
    """

    response: str = llm_model.generate_response(
        system_message=sys_prompt,
        human_message=human_message,
        structured_output=None,
    )

    # TODO: Implement parsing logic

    state.generated_response_for_user_validation = response
    state.user_validation_status = "pending"

    logger.info("User validation node completed.")

    return state

