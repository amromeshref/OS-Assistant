from evaluation.runners.pydantic_schemas import UserValidationEvaluation
from evaluation.config import DEFAULT_LLM_PLATFORM, DEFAULT_GROQ_MODEL_NAME, DEFAULT_OLLAMA_MODEL_NAME
from evaluation.runners.prompts.user_validation_evaluation import (
    get_user_validation_evaluation_system_prompt,
    get_human_message_for_user_validation_evaluation
)
from os_assistant.core.states.os_assistant_state import OSAssistantState
from os_assistant.core.models.main import LLMModel
from os_assistant.utils.logger import get_logger    

logger = get_logger(__name__)

def user_validation_evaluation_node(state: OSAssistantState) -> UserValidationEvaluation:
    logger.info("Starting User Validation Evaluation Node")
    
    # Get the system prompt for evaluation
    system_prompt = get_user_validation_evaluation_system_prompt()
    
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
    
    human_message = get_human_message_for_user_validation_evaluation(state)

    # Generate the evaluation result using the LLM
    response: UserValidationEvaluation = llm_model.generate_response(
        system_message=system_prompt,
        human_message=human_message,
        structured_output=UserValidationEvaluation
    )

    logger.info("Completed User Validation Evaluation Node")
    
    return response