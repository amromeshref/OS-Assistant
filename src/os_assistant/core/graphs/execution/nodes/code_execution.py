from os_assistant.core.states.os_assistant_state import OSAssistantState, CommandExecution
from os_assistant.prompts.code_execution import get_code_execution_sys_prompt
from os_assistant.tools.command_execution import run_command
from os_assistant.utils.logger import get_logger
from os_assistant.core.models import LLMModel

logger = get_logger(__name__)

def code_execution_node(state: OSAssistantState) -> OSAssistantState:
    """
    """
    logger.info("Starting code execution node.")

    if(len(state.planning.command_steps) == 0):
        logger.info("No code execution steps provided")
        logger.info("Completed code execution node.")
        return state

    sys_prompt: str = get_code_execution_sys_prompt()
    llm_model = LLMModel()


    
    for command_step in state.planning.command_steps:
        # Command output after running
        command_output = run_command(command_step.command)

        human_message =f"""
User's original query: {state.original_query_enhanced}
Command Execution Details(Before running the command):
{command_step.model_dump_json()}

Command Output(After running):
{command_output}
"""
        response: CommandExecution = llm_model.generate_response(
            system_message=sys_prompt,
            human_message=human_message,
            structured_output=CommandExecution
        )

        # TODO: Add parsing logic here

        state.command_executions.append(response)

    state.command_execution_status = "completed"
    logger.info("Completed code execution node.")

    return state