from os_assistant.prompts.retrieve_execution_details_tool import get_retrieve_execution_details_sys_prompt
from os_assistant.utils.helper_functions import load_command_executions, command_executions_to_str
from langchain.tools import tool
from os_assistant.utils.logger import get_logger
from os_assistant.core.models import LLMModel
from langchain.tools import Tool

logger = get_logger(__name__)


@tool
def retrieve_execution_details(query: str) -> str:
    """
    Retrieve the execution details of a specific command based on a the given query.
    Args:
        query (str): A natural language query describing which command execution
                     details to retrieve.
    Returns:
        str: The execution details of the command.
    """
    logger.info("Starting retrieval of command execution details tool")

    # Load the system prompt
    sys_prompt = get_retrieve_execution_details_sys_prompt()

    # Initialize the LLM model
    llm = LLMModel()

    # Load all existing command execution records
    command_executions = load_command_executions()

    human_message = f"""
Query: {query}
Existing Command Execution Details: {command_executions_to_str(command_executions)}
"""

    response: str = llm.generate_response(
        system_message=sys_prompt,
        human_message=human_message,
        structured_output=None
    )

    # TODO: Implement parsing logic

    logger.info("Completed retrieval of command execution details tool")

    return response

retrieve_execution_details_tool =  Tool(
    name="RetrieveExecutionDetails",
    func=retrieve_execution_details,
    description="Retrieve the execution details of a specific command based on a query."
    )