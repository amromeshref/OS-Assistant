from os_assistant.core.states.os_assistant_state import OSAssistantState
from os_assistant.utils.helper_functions import command_executions_to_str
from langchain.tools import tool
from os_assistant.utils.logger import get_logger
from langchain.tools import Tool

logger = get_logger(__name__)



def retrieve_execution_details(state: OSAssistantState) -> str:
    """
    Retrieve the execution details of a specific command.
    Args:
        state: OSAssistantState
    Returns:
        str: The execution details of the command.
    """
    logger.info("Starting retrieval of command execution details tool")

    try:
        step_index = state.execution_orchestrator[-1].action_input

        command_execution = None
        for command_exe in state.command_executions:
            if command_exe.step_index == step_index:
                command_execution = command_exe
                break

        command_execution_str = command_executions_to_str([command_execution])

        logger.info("Completed retrieval of command execution details tool")
        return command_execution_str
    except:
        return "No command executions found. Check the step index or try the 'retrieve_information_details'"


retrieve_execution_details_tool =  Tool(
    name="RetrieveExecutionDetails",
    func=retrieve_execution_details,
    description="Retrieve the execution details of a specific command based on a query."
    )