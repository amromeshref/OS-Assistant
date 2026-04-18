from os_assistant.utils.helper_functions import save_information_responses
from os_assistant.core.states.os_assistant_state import (
    OSAssistantState,
    InformationResponse,
)
from os_assistant.prompts.information_generation import (
    get_information_generation_sys_prompt,
)
from os_assistant.utils.logger import get_logger
from os_assistant.core.models.main import LLMModel
from os_assistant.utils.helper_functions import command_executions_to_str, information_responses_to_str

logger = get_logger(__name__)


def information_generation_node(state: OSAssistantState) -> OSAssistantState:
    """ """
    logger.info("Starting information generation node.")

    # if len(state.planning.information_steps) == 0:
    #     logger.info("No information query provided")
    #     logger.info("Completed information generation node.")
    #     return state

    llm_model = LLMModel()
    sys_prompt = get_information_generation_sys_prompt()

    step_index = state.current_step_index


    information_response = InformationResponse()

    if state.steps_resolver_active:
        current_resolving_step_index = state.current_resolving_step_index
        current_resolving_step = state.steps_resolver[-1].resolved_steps[current_resolving_step_index]
        information_response.query = current_resolving_step.step_details.description
        state.current_resolving_step_index += 1
    else:
        information_response.query = state.planning.plan_steps[step_index].step_details.description

    human_message = f"""
User's Original Query: {state.finalized_enhanced_query}
Information Query: {information_response.query}
"""
    
    response: str = llm_model.generate_response(
        human_message=human_message,
        system_message=sys_prompt,
        structured_output=None,
    )

    # TODO: Add parsing logic here

    information_response.answer = response
    information_response.step_index = step_index
    state.generated_information_responses.append(information_response)
    state.executed_steps.append(
        f"The information step involving the query '{information_response.query}' is done."
    )
    #state.current_step_index += 1
    
    # state.steps_done_indicies.append(state.execution_orchestrator[-1].next_step_index)

    #save_information_responses(state.generated_information_responses)

    if state.steps_resolver_active:
        current_resolving_step_index = state.current_resolving_step_index
        total_resolved_steps = len(state.steps_resolver[-1].resolved_steps)

        if current_resolving_step_index >= total_resolved_steps:
            logger.info("All resolved steps have been executed.")
            state.steps_resolver_active = False
            state.current_resolving_step_index = 0
            state.current_step_index += 1
    else:
        state.current_step_index += 1

    state.generated_information_responses_status = "completed"
    logger.info("Completed information generation node.")
    
    return state
