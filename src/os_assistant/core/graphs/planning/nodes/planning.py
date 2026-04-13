from os_assistant.core.states.os_assistant_state import OSAssistantState, PlanningState
from os_assistant.core.models.main import LLMModel
from os_assistant.prompts.planning import get_planning_sys_prompt
from os_assistant.utils.logger import get_logger
from os_assistant.utils.helper_functions import planning_state_to_str

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

    # Mode 2: Feedback Mode (after user validation if user asked for plan update)
    if state.user_validation.user_feedback_type == "update_plan":
        human_message = f"""User's Original Query: {state.finalized_enhanced_query}
This is Mode 2: Feedback Mode 
Existing Plan:
{planning_state_to_str(state.planning)}
User Feedback on the Plan: {str(state.user_validation.user_feedback)}
"""
    # Mode 1: Initial Planning Mode (before user validation)
    else:
        human_message = f"""
This is Mode 1: Planning Mode 
User's original query: {state.finalized_enhanced_query}
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
    #state.total_steps = len(state.planning.plan_steps)

    logger.info("Completed planning node.")

    return state

