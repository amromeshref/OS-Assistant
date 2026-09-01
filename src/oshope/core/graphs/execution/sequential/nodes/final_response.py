from oshope.core.states.oshope_state import (
    OSHopeState,
)
from oshope.prompts.final_response import (
    get_final_response_sys_prompt,
    get_human_message_after_plan_rejection,
    get_normal_human_message,
)

from oshope.utils.logger import get_logger
from oshope.core.models.main import LLMModel

logger = get_logger(__name__)


def final_response_node(state: OSHopeState) -> OSHopeState:
    """
    Node responsible for generating the final response to the user after all planning, code execution, and information generation steps are completed.
    This node takes into account the entire execution process, including any user feedback during validation, to generate a comprehensive final response.
    """
    logger.info("Starting final response node.")

    llm_model = LLMModel()
    sys_prompt = get_final_response_sys_prompt()

    if state.user_validation.user_feedback_type == "rejected":
        human_message = get_human_message_after_plan_rejection(state)
    else:
        human_message = get_normal_human_message(state)

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
