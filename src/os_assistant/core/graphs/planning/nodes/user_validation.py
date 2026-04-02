from os_assistant.core.states.os_assistant_state import OSAssistantState, UserValidationState
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
    if state.user_validation.is_validation_required:
        human_message = f"""
    Finalized enhanced user query (original request): {state.finalized_enhanced_query}
    Current Turn Query: {state.original_queries[-1]}
    Conversation History: {str(state.multi_turn_conversation_history)}
    The planning node has generated the following execution/information plan based on the user's original query: {state.planning.model_dump_json()}"""
    else:
        human_message = f"""
The user did not see the current plan yet. They did not reject it, approve it, or ask for changes.
User's original query: {state.finalized_enhanced_query}
Generated execution/information plan: {state.planning.model_dump_json()}
    """
        
    while True:
        try:
            response: UserValidationState = llm_model.generate_response(
                system_message=sys_prompt,
                human_message=human_message,
                structured_output=UserValidationState,
            )
            break  # Exit the loop if response is successfully generated
        except Exception as e:
            error_message = str(e)

            # Detect tool call failure
            if "tool" in error_message.lower():
                logger.warning("Tool call failed during user validation. Retrying...")
                human_message += "\nNote: The previous response encountered an error related to tool calls. Please ensure that the response adheres to the expected format and does not include any tool calls."
                continue  # Retry the user validation node

    # TODO: Implement parsing logic

    state.user_validation = response
    state.user_validation_status = "completed"

    logger.info("User validation node completed.")

    return state

