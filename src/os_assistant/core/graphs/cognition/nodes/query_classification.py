from os_assistant.core.states.os_assistant_state import (
    OSAssistantState,
    QueryClassificationState,
)
from os_assistant.prompts.query_classification import (
    get_query_classification_sys_prompt,
    get_first_human_message,
    get_second_human_message,
)
from os_assistant.utils.logger import get_logger
from os_assistant.core.models.main import LLMModel

logger = get_logger(__name__)


def query_classification_node(state: OSAssistantState) -> OSAssistantState:
    """
    Classifies the user's query using an LLM and updates the state with the classification results.

    Args:
        state (OSAssistantState): The current state of the OS Assistant, including the original query.

    Returns:
        OSAssistantState: The updated state with the query classification results.
    """
    logger.info("Starting query classification node.")

    llm_model = LLMModel()
    sys_prompt = get_query_classification_sys_prompt()

    if state.clarification_attempts == 0:    
        human_message, retrieved_memories = get_first_human_message(state)
        state.retrieved_memories = retrieved_memories
    else:
        human_message = get_second_human_message(state)

    # Generate the classification response from the LLM
    response: QueryClassificationState = llm_model.generate_response(
        system_message=sys_prompt,
        human_message=human_message, 
        structured_output=QueryClassificationState,
    )

    # Parse the classification response and update the state
    # (This is a placeholder for actual parsing logic, which would depend on the format of the LLM's response)
    # For example, you might expect a JSON response that can be directly converted to ClassificationState

    # TODO: (in core.models)Implement the actual parsing logic based on the expected response format from the LLM
    # classification_result = parse_classification_response(response)
    # the generated response must be in the format of ClassificationState, so we can directly assign it to the state
    # state.query_classification_status = "completed"

    state.query_classification = response
    state.query_classification_status = "completed"
    state.original_queries_enhanced.append(response.original_query_enhanced)
    state.finalized_enhanced_query = response.original_query_enhanced

    logger.info("Completed query classification node.")

    return state
