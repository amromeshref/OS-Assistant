from os_assistant.core.states.os_assistant_state import OSAssistantState, QueryClarificationState
from os_assistant.prompts.query_clarification import (
    get_query_clarification_sys_prompt, 
    get_fitst_human_message, 
    get_second_human_message
)
from os_assistant.utils.logger import get_logger
from os_assistant.core.models.main import LLMModel

logger = get_logger(__name__)


def query_clarification_node(state: OSAssistantState) -> OSAssistantState:
    """
    Generates a clarification response using an LLM based on the original query and its classification.
    Args:
        state (OSAssistantState): The current state of the OS Assistant, including the original query and its classification.
    Returns:
        OSAssistantState: The updated state with the generated response for clarification.
    """
    logger.info("Starting query clarification node.")
    state.clarification_attempts += 1

    llm_model = LLMModel()
    sys_prompt = get_query_clarification_sys_prompt()

    if state.planning.requires_follow_up:
        human_message = get_second_human_message(state)
    else:
        human_message = get_fitst_human_message(state)

    # Generate the classification response from the LLM
    response: QueryClarificationState = llm_model.generate_response(
        system_message=sys_prompt,
        human_message=human_message,
        structured_output=QueryClarificationState
    )

    # TODO: Implement parsing logic

    state.query_clarification = response
    logger.info("Completed query clarification node.")

    if not state.query_clarification.is_clarification_needed:
        state.finalized_enhanced_query = state.query_clarification.finalized_enhanced_query

    return state

    # Parse the classification response and update the state
    # (This is a placeholder for actual parsing logic, which would depend on the format of the LLM's response)
    # For example, you might expect a JSON response that can be directly converted to ClassificationState
