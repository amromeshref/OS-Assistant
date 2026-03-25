from os_assistant.core.states.os_assistant_state import OSAssistantState
from os_assistant.prompts.query_clarification import get_query_clarification_sys_prompt
from os_assistant.utils.logger import get_logger
from os_assistant.core.models import LLMModel

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

    human_message = f"""
The user's original query is: "{state.query_classification.original_query_enhanced}"
Follow up reasoning: "{state.query_classification.follow_up_reasoning}"
"""

    # Generate the classification response from the LLM
    response = llm_model.generate_response(
        system_message=sys_prompt, human_message=human_message, structured_output=None
    )

    state.generated_response_for_clarification = response
    logger.info("Completed query clarification node.")

    return state

    # Parse the classification response and update the state
    # (This is a placeholder for actual parsing logic, which would depend on the format of the LLM's response)
    # For example, you might expect a JSON response that can be directly converted to ClassificationState
