from os_assistant.core.states.os_assistant_state import OSAssistantState
from os_assistant.utils.helper_functions import information_responses_to_str
from langchain.tools import tool
from os_assistant.utils.logger import get_logger
from langchain.tools import Tool

logger = get_logger(__name__)


def retrieve_information_details(state: OSAssistantState, step_index: int) -> str:
    """
    Retrieve previously generated information response.
    Args:
        state: OSAssistantState
        step_index: The index of the step for which to retrieve information
    Returns:
        str: The information responses details
    """
    logger.info("Starting retrieval of information details tool")

    try:
        information_response = None
        for info_resp in state.generated_information_responses:
            if info_resp.step_index == step_index:
                information_response = info_resp
                break

        information_response_str = information_responses_to_str([information_response])

        logger.info("Completed retrieval of information details tool")

        return information_response_str
    except:
        return "No information responses found. Check the step index or try the 'retrieve_execution_details'"
    
retrieve_information_details_tool =  Tool(
    name="RetrieveInformationDetails",
    func=retrieve_information_details,
    description="Retrieve previously generated information response details based on a query."
    )