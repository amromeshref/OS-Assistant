from os_assistant.core.states.os_assistant_state import InformationResponse, OSAssistantState
from os_assistant.utils.logger import get_logger
from langchain.tools import Tool
from typing import List

logger = get_logger(__name__)

def information_responses_to_str(responses: List[InformationResponse]) -> str:
    """
    Convert a list of InformationResponse objects into a human-readable string format for debugging or prompting purposes.
    Args:
        responses (List[InformationResponse]): The list of InformationResponse objects to convert.
    Returns:
        str: A human-readable string representation of the information responses.
    """
    if not responses:
        return "No information responses."

    lines = []
    for i, response in enumerate(responses, start=1):
        lines.append(f"Step Index: {response.step_index}")
        lines.append(f"  Query: {response.query or 'N/A'}")
        lines.append(f"  Answer: {response.answer or 'N/A'}")
        lines.append("")  # empty line for readability

    return "\n".join(lines)


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
        information_responses = []
        for info_resp in state.generated_information_responses:
            if info_resp.step_index == step_index:
                information_responses.append(info_resp)
       

        information_responses_str = information_responses_to_str(information_responses)

        logger.info("Completed retrieval of information details tool")

        return information_responses_str
    except:
        return "No information responses found. Check the step index or try the 'retrieve_execution_details'"
    
retrieve_information_details_tool =  Tool(
    name="RetrieveInformationDetails",
    func=retrieve_information_details,
    description="Retrieve previously generated information response details based on a query."
    )