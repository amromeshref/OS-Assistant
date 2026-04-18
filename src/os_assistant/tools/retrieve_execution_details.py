from os_assistant.core.states.os_assistant_state import OSAssistantState
from os_assistant.utils.helper_functions import command_executions_to_str
from langchain.tools import tool
from os_assistant.utils.logger import get_logger
from langchain.tools import Tool

logger = get_logger(__name__)



def retrieve_execution_details(state: OSAssistantState, step_index: int) -> str:
    """
    Retrieve the execution details of a specific command.
    Args:
        state: OSAssistantState
        step_index: The index of the step for which to retrieve execution details
    Returns:
        str: The execution details of the command.
    """
    logger.info("Starting retrieval of command execution details tool")

    try:
        command_executions = []
        for command_exe in state.command_executions:
            if command_exe.step_index == step_index:
                command_executions.append(command_exe)
    

        command_executions_str = command_executions_to_str(command_executions)

        logger.info("Completed retrieval of command execution details tool")
        return command_executions_str
    except:
        return "No command executions found. Check the step index or try the 'retrieve_information_details'"


retrieve_execution_details_tool =  Tool(
    name="RetrieveExecutionDetails",
    func=retrieve_execution_details,
    description="Retrieve the execution details of a specific command based on a query."
    )