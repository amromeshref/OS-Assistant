from os_assistant.core.states.os_assistant_state import (
    OSAssistantState,
    InformationResponse,
)
from os_assistant.prompts.information_generation import (
    get_information_generation_sys_prompt,
)
from os_assistant.utils.logger import get_logger
from os_assistant.core.models import LLMModel

logger = get_logger(__name__)


def information_generation_node(state: OSAssistantState) -> OSAssistantState:
    """ """
    logger.info("Starting information generation node.")

    if len(state.planning.information_steps) == 0:
        logger.info("No information query provided")
        logger.info("Completed information generation node.")
        return state

    llm_model = LLMModel()
    sys_prompt = get_information_generation_sys_prompt()

    for information_step in state.planning.information_steps:
        information_response = InformationResponse()
        information_response.query = information_step.description
        human_message = f"""
User's Original Query: {state.finalized_enhanced_query}
Information Query: {information_step.description}
"""
        if len(state.command_executions) != 0:
            command_executions_str = ""
            for command_execution in state.command_executions:
                command_executions_str += command_execution.model_dump_json() + "\n"

            human_message += f"""
Command Execution Details:
{command_executions_str}
"""
        response: str = llm_model.generate_response(
            human_message=human_message,
            system_message=sys_prompt,
            structured_output=None,
        )

        # TODO: Add parsing logic here

        information_response.answer = response
        state.generated_information_responses.append(information_response)

    state.generated_information_responses_status = "completed"
    logger.info("Completed information generation node.")
    
    return state
