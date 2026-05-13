from os_assistant.core.states.os_assistant_state import OSAssistantState, PlanningState
from os_assistant.core.models.main import LLMModel
from os_assistant.prompts.planning import get_planning_sys_prompt, get_first_human_message, get_second_human_message
from os_assistant.utils.logger import get_logger
from os_assistant.config.config import parallel_execution_enabled

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
        human_message = get_second_human_message(state)

    # Mode 1: Initial Planning Mode (before user validation)
    else:
        human_message = get_first_human_message(state)

    response: PlanningState = llm_model.generate_response(
        system_message=sys_prompt,
        human_message=human_message,
        structured_output=PlanningState,
    )

    if parallel_execution_enabled:
        for i in range(len(response.plan_steps)):
            response.plan_steps[i].status = "pending"
            response.plan_steps[i].step_index = i
            response.plan_steps[i].command_executions = []
            response.plan_steps[i].command_error_handlers = []
            response.plan_steps[i].num_error_executions = 0
            response.plan_steps[i].steps_resolver = []

    # TODO: Implement the actual parsing logic based on the expected response format from the LLM

    # Update the state with the generated execution plan
    state.planning = response
    state.planning_status = "completed"
    #state.total_steps = len(state.planning.plan_steps)

    logger.info("Completed planning node.")

    return state

