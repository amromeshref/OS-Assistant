from os_assistant.prompts.retrieve_information_details_tool import get_retrieve_information_details_sys_prompt
from os_assistant.utils.helper_functions import load_information_responses, information_responses_to_str
from langchain.tools import tool
from os_assistant.utils.logger import get_logger
from os_assistant.core.models import LLMModel
from langchain.tools import Tool

logger = get_logger(__name__)


@tool
def retrieve_information_details(query: str) -> str:
    """
    Retrieve previously generated information response details based on a query.
    Args:
        query (str): A natural language query describing which information
                     response to retrieve.
    Returns:
        str: The information responses details
    """
    logger.info("Starting retrieval of information details tool")

    # Load the system prompt
    sys_prompt = get_retrieve_information_details_sys_prompt()

    # Initialize the LLM model
    llm = LLMModel()

    # Load all existing information responses records
    information_responses = load_information_responses()

    human_message = f"""
Query: {query}
Existing Information Responses Details: {information_responses_to_str(information_responses)}
"""

    response: str = llm.generate_response(
        system_message=sys_prompt,
        human_message=human_message,
        structured_output=None
    )

    # TODO: Implement parsing logic

    logger.info("Completed retrieval of information details tool")

    return response

retrieve_information_details_tool =  Tool(
    name="RetrieveInformationDetails",
    func=retrieve_information_details,
    description="Retrieve previously generated information response details based on a query."
    )