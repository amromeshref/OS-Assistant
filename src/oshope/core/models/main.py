from oshope.core.models.groq import GroqModel
from oshope.core.models.ollama import OllamaModel
from oshope.config.config import (
    AVAILABLE_LLM_PLATFORMS,
    DEFAULT_LLM_PLATFORM,
)
from oshope.utils.logger import get_logger


logger = get_logger(__name__)


class LLMModel:
    def __init__(self, platform: str = None, model_name: str = None):
        if platform is None:
            platform = DEFAULT_LLM_PLATFORM
        self.platform = platform

        logger.info(f"Initializing LLMModel with platform: {self.platform }")

        if self.platform == "ollama":
            self.llm_model = OllamaModel(model_name)
        elif self.platform == "groq":
            self.llm_model = GroqModel(model_name)
        else:
            logger.error(
                f"Unsupported platform: {self.platform}. Available platforms are: {AVAILABLE_LLM_PLATFORMS}"
            )
            raise ValueError(
                f"Unsupported platform: {self.platform}. Available platforms are: {AVAILABLE_LLM_PLATFORMS}"
            )

    def generate_response(
        self,
        human_message: str,
        system_message: str = None,
        structured_output=None,
    ):
        """
        Generate a response from the LLM based on the provided system and human messages.
        If structured_output is provided, the response will be formatted according to the specified structure.
        Args:
            system_message: The system message to provide context to the LLM.
            human_message: The human message containing the user's input or query.
            structured_output: Optional parameter specifying the desired structure of the output. If None, a standard response will be generated.
        Returns:
            str or structured response: The generated response from the LLM, either as a plain string or in the specified structured format.
        """
        if system_message is None:
            system_message = "You are a helpful assistant for managing and interacting with the operating system. Provide accurate and concise responses to the user's queries and commands related to OS tasks, file management, system information, and troubleshooting."

        try:
            response = self.llm_model.generate_response(
                human_message=human_message,
                system_message=system_message,
                structured_output=structured_output,
            )
            return response
        except Exception as e:
            logger.error(f"Error generating response with {self.platform}: {e}")
            raise RuntimeError(f"Error generating response with {self.platform}: {e}")

    def generate_response_react_agent(
        self,
        human_message: str,
        system_message: str = None,
        tools: list = None,
    ):
        """ """
        if system_message is None:
            system_message = "You are a helpful assistant for managing and interacting with the operating system. Provide accurate and concise responses to the user's queries and commands related to OS tasks, file management, system information, and troubleshooting."

        try:
            agent_response = self.llm_model.generate_response_react_agent(
                human_message=human_message,
                system_message=system_message,
                tools=tools,
            )

            return agent_response
        except Exception as e:
            logger.error(f"Error generating response with {self.platform}: {e}")
            raise RuntimeError(f"Error generating response with {self.platform}: {e}")
