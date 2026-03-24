from langchain_groq.chat_models import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from groq import Groq
import ollama
from os_assistant.core.settings import DEFAULT_OLLAMA_MODEL_NAME, AVAILABLE_PLATFORMS, GROQ_API_KEY, DEFAULT_GROQ_MODEL_NAME, DEFAULT_PLATFORM
from os_assistant.utils.helper_functions import check_ollama_installed, check_installed_ollama_model
from os_assistant.utils.logger import get_logger

logger = get_logger(__name__)

class LLMModel:
    def __init__(self, platform: str=None, model_name:str=None):
        if platform is None:
            platform = DEFAULT_PLATFORM
        self.platform = platform

        logger.info(f"Initializing LLMModel with platform: {self.platform }")

        if self.platform == "ollama":
            self.model_name = self._resolve_ollama_model(model_name)
        elif self.platform  == "groq":
            self.model_name = self._resolve_groq_model(model_name)
        else:
            logger.error(f"Unsupported platform: {self.platform}. Available platforms are: {AVAILABLE_PLATFORMS}")
            raise ValueError(f"Unsupported platform: {self.platform}. Available platforms are: {AVAILABLE_PLATFORMS}")
        
    def _resolve_ollama_model(self, model_name: str) -> str:
        """
        Check if Ollama is installed and validate the requested model version.
        If no version is specified, use the default version.
        Args:
            model_name: The requested Ollama model name.
        Returns:
            str: The valid Ollama model name.  
        Raises:
            EnvironmentError: If Ollama or the specified model is not installed.
        """
        if not check_ollama_installed():
            logger.error("Ollama is not installed.")
            raise EnvironmentError("Ollama is not installed. Please install Ollama to use this model.")
    
        if model_name is None:
            # Check if the default model name is installed
            if not check_installed_ollama_model(DEFAULT_OLLAMA_MODEL_NAME):
                logger.error(f"Default Ollama model '{DEFAULT_OLLAMA_MODEL_NAME}' is not installed. Please install it to use this model or specify a different model name.")
                raise EnvironmentError(f"Ollama model '{DEFAULT_OLLAMA_MODEL_NAME}' is not installed. Please install it to use this model or specify a different model name.")
            else:
                logger.info(f"Using default Ollama model name: {DEFAULT_OLLAMA_MODEL_NAME}")
                return DEFAULT_OLLAMA_MODEL_NAME
            
        else:
            # Check if the specified model name is installed
            if not check_installed_ollama_model(model_name):
                logger.error(f"Ollama model '{model_name}' is not installed. Switching to default model name '{DEFAULT_OLLAMA_MODEL_NAME}' if available.")
                # Check if the default model name is installed
                if check_installed_ollama_model(DEFAULT_OLLAMA_MODEL_NAME):
                    logger.info(f"Using default Ollama model name: {DEFAULT_OLLAMA_MODEL_NAME}")
                    return DEFAULT_OLLAMA_MODEL_NAME
                else:
                    logger.error(f"Default Ollama model '{DEFAULT_OLLAMA_MODEL_NAME}' is also not installed. Please install it to use this model or specify a different model name.")
                    raise EnvironmentError(f"Ollama model '{model_name}' is not installed. Default model '{DEFAULT_OLLAMA_MODEL_NAME}' is also not installed. Please install one of these models to use this feature.")
            else:
                logger.info(f"Using specified Ollama model name: {model_name}")
                return model_name
    
    def _resolve_groq_model(self, model_name: str) -> str:
        """
        Resolve the Groq model name. If no model name is provided, return the default model name.
        Args:
            model_name: The requested Groq model name.
        Returns:
            str: The valid Groq model name.
        """
        if model_name is None:
            logger.info(f"No Groq model name specified. Using default model name: {DEFAULT_GROQ_MODEL_NAME}")
            return DEFAULT_GROQ_MODEL_NAME
        
        client = Groq()
        models = client.models.list()
        available_models = [m.id for m in models.data]
        if model_name not in available_models:
            logger.error(f"Groq model '{model_name}' is not available. Available models are: {available_models}")
            raise ValueError(f"Groq model '{model_name}' is not available. Available models are: {available_models}")
        
        logger.info(f"Using specified Groq model name: {model_name}")
        return model_name


    def generate_response(self, human_message: str, system_message: str=None, structured_output=None):
        """"
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

        if self.platform == "ollama":
            try:
                if not structured_output:
                    logger.info("Generating response using Ollama without structured output.")
                    response = ollama.chat(
                        model=self.model_name,
                        messages=[
                            {"role": "system", "content": system_message},
                            {"role": "user", "content": human_message}
                        ]
                    )
                    return response['message']['content']
                else:
                    # TODO: Implement structured output handling for Ollama.
                    pass
            except Exception as e:
                logger.error(f"Error generating response with Ollama: {e}")
                raise RuntimeError(f"Error generating response with Ollama: {e}")
            
        elif self.platform == "groq":
            try:
                llm = ChatGroq(model=self.model_name, api_key=GROQ_API_KEY)
                messages = [
                    SystemMessage(content=system_message),
                    HumanMessage(content=human_message)
                ]
                if not structured_output:
                    logger.info("Generating response using Groq without structured output.")
                    response = llm.invoke(messages)
                    return response.content
                else:
                    logger.info("Generating response using Groq with structured output.")   
                    response = llm.with_structured_output(structured_output).invoke(messages)
                    return response
            except Exception as e:
                logger.error(f"Error generating response with Groq: {e}")
                raise RuntimeError(f"Error generating response with Groq: {e}")