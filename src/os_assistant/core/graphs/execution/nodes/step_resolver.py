from os_assistant.core.states.os_assistant_state import (
    OSAssistantState,
    StepResolverState,
)
from os_assistant.prompts.step_resolver import (
    get_step_resolver_sys_prompt,
    get_human_message
)
from os_assistant.utils.logger import get_logger
from os_assistant.core.models.main import LLMModel
from os_assistant.utils.helper_functions import retrieve_dependency_outputs

logger = get_logger(__name__)

    
def step_resolver_node(state: OSAssistantState) -> OSAssistantState:
    """
    Resolve the current step by replacing placeholders with actual values from dependencies.
    """
    logger.info("Starting step resolver node.")

    llm_model = LLMModel()
    sys_prompt = get_step_resolver_sys_prompt()
    current_step_index = state.current_step_index
    print("="*90)
    print(f"Current step index in step resolver: {current_step_index}")
    print("="*90)
    current_step = state.planning.plan_steps[current_step_index]
    dependency_outputs_str = retrieve_dependency_outputs(state)
    
    human_message = get_human_message(current_step, dependency_outputs_str)

    response: StepResolverState = llm_model.generate_response(
        system_message=sys_prompt,
        human_message=human_message,
        structured_output=StepResolverState,
    )

    # TODO: Add parsing logic

    state.steps_resolver_active = True
    state.steps_resolver.append(response)
    logger.info("Completed step resolver node.")

    if not response.is_resolution_successful:
        state.executed_steps.append(f"Could not execute the step whose index is {current_step_index} and description is {current_step.description} due to the following reason: {response.resolution_reasoning}")
        logger.info("Step resolution failed. Moving to the next step.")
        state.current_step_index += 1
        state.steps_resolver_active = False
    
    return state

    