from os_assistant.core.states.os_assistant_state import OSAssistantState, PlanningState
from os_assistant.core.models import LLMModel
from os_assistant.prompts.planning import get_planning_sys_prompt
from os_assistant.utils.logger import get_logger

logger = get_logger(__name__)

def planning_node(state: OSAssistantState) -> OSAssistantState:
    """
    Generates an execution/information plan for the user's query based on the query classification results and updates the state with the plan.
    Args:
        state (OSAssistantState): The current state of the OS Assistant.
    Returns:
        OSAssistantState: The updated state with the generated execution/information plan.
    """
    logger.info("Starting planning node.")

    llm_model = LLMModel()
    sys_prompt = get_planning_sys_prompt()
    
    human_message = f"""
User's original query: {state.original_query_enhanced}
Query Type (command, information, or both): {state.query_classification.query_type}
Classification Reasoning: {state.query_classification.classification_reasoning}
    """

    response: PlanningState = llm_model.generate_response(
        system_message=sys_prompt,
        human_message=human_message,
        structured_output=PlanningState,
    )

    # TODO: Implement the actual parsing logic based on the expected response format from the LLM

    # Update the state with the generated execution plan
    state.planning = response
    state.planning_status = "completed"

    logger.info("Completed planning node.")

    return state

