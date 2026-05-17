from evaluation.runners.pydantic_schemas import InformationGenerationEvaluation
from evaluation.config import DEFAULT_LLM_PLATFORM, DEFAULT_GROQ_MODEL_NAME, DEFAULT_OLLAMA_MODEL_NAME
from evaluation.runners.prompts.information_generation_evaluation import (
    get_information_generation_evaluation_system_prompt,
    get_human_message_for_information_generation_evaluation
)
from os_assistant.core.states.os_assistant_state import InformationResponse
from os_assistant.core.models.main import LLMModel
from os_assistant.utils.logger import get_logger
from typing import List

logger = get_logger(__name__)

def information_generation_evaluation_node(information_responses: List[InformationResponse]) -> List[InformationGenerationEvaluation]:
    logger.info("Starting Information Generation Evaluation Node")
    
    # Get the system prompt for evaluation
    system_prompt = get_information_generation_evaluation_system_prompt()
    
    if DEFAULT_LLM_PLATFORM == "groq":
        llm_model = LLMModel(
            platform=DEFAULT_LLM_PLATFORM,
            model_name=DEFAULT_GROQ_MODEL_NAME
        )
    elif DEFAULT_LLM_PLATFORM == "ollama":
        llm_model = LLMModel(
            platform=DEFAULT_LLM_PLATFORM,
            model_name=DEFAULT_OLLAMA_MODEL_NAME
        )
    else:
        logger.error(f"Unsupported LLM platform: {DEFAULT_LLM_PLATFORM}")
        raise ValueError(f"Unsupported LLM platform: {DEFAULT_LLM_PLATFORM}")
    
    responses = []

    for info_response in information_responses:
        logger.info(f"Evaluating Information Response: {info_response.query}")

        human_message = get_human_message_for_information_generation_evaluation(info_response)

        # Generate the evaluation result using the LLM
        response: InformationGenerationEvaluation = llm_model.generate_response(
            system_message=system_prompt,
            human_message=human_message,
            structured_output=InformationGenerationEvaluation
        )

        responses.append(response)

    logger.info("Completed Information Generation Evaluation Node")
    
    return responses