from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.agents import create_react_agent, AgentExecutor
from os_assistant.utils.helper_functions import (
    check_ollama_installed,
    check_installed_ollama_model,
)
from os_assistant.utils.logger import get_logger
from langchain import hub
from os_assistant.core.settings import DEFAULT_OLLAMA_MODEL_NAME


logger = get_logger(__name__)


class OllamaModel:
    def __init__(self, model_name):
        self.model_name = self._resolve_ollama_model(model_name)

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
            raise EnvironmentError(
                "Ollama is not installed. Please install Ollama to use this model."
            )

        if model_name is None:
            # Check if the default model name is installed
            if not check_installed_ollama_model(DEFAULT_OLLAMA_MODEL_NAME):
                logger.error(
                    f"Default Ollama model '{DEFAULT_OLLAMA_MODEL_NAME}' is not installed. Please install it to use this model or specify a different model name."
                )
                raise EnvironmentError(
                    f"Ollama model '{DEFAULT_OLLAMA_MODEL_NAME}' is not installed. Please install it to use this model or specify a different model name."
                )
            else:
                logger.info(
                    f"Using default Ollama model name: {DEFAULT_OLLAMA_MODEL_NAME}"
                )
                return DEFAULT_OLLAMA_MODEL_NAME

        else:
            # Check if the specified model name is installed
            if not check_installed_ollama_model(model_name):
                logger.error(
                    f"Ollama model '{model_name}' is not installed. Switching to default model name '{DEFAULT_OLLAMA_MODEL_NAME}' if available."
                )
                # Check if the default model name is installed
                if check_installed_ollama_model(DEFAULT_OLLAMA_MODEL_NAME):
                    logger.info(
                        f"Using default Ollama model name: {DEFAULT_OLLAMA_MODEL_NAME}"
                    )
                    return DEFAULT_OLLAMA_MODEL_NAME
                else:
                    logger.error(
                        f"Default Ollama model '{DEFAULT_OLLAMA_MODEL_NAME}' is also not installed. Please install it to use this model or specify a different model name."
                    )
                    raise EnvironmentError(
                        f"Ollama model '{model_name}' is not installed. Default model '{DEFAULT_OLLAMA_MODEL_NAME}' is also not installed. Please install one of these models to use this feature."
                    )
            else:
                logger.info(f"Using specified Ollama model name: {model_name}")
                return model_name


    def generate_response(
        self, human_message: str, system_message: str = None, structured_output=None
    ):
        """ """
        messages = [
            SystemMessage(content=system_message),
            HumanMessage(content=human_message),
        ]

        llm_model = ChatOllama(model=self.model_name, temperature=0)

        if not structured_output:
            logger.info("Generating response using Ollama without structured output.")

            response = llm_model.invoke(messages)
            return response.content
        else:
            logger.info("Generating response using Ollama with structured output.")
            response = llm_model.with_structured_output(structured_output).invoke(
                messages
            )
            return response


    def generate_response_react_agent(
        self,
        human_message: str,
        system_message: str = None,
        tools: list = None,
    ):
        """ """
        agent_prompt = hub.pull("hwchase17/react")
        agent_prompt.template = system_message

        llm = ChatOllama(model=self.model_name, temperature=0)

        if tools is None:
            agent = create_react_agent(llm=llm, prompt=agent_prompt)
        else:
            agent = create_react_agent(llm=llm, prompt=agent_prompt, tools=tools)

        logger.info("Generating response using Ollama, ReactAgent")

        agent_executor = AgentExecutor(
            agent=agent, tools=tools, verbose=True, handle_parsing_errors=True
        )
        agent_response = agent_executor.invoke({"input": human_message})["output"]

        return agent_response
