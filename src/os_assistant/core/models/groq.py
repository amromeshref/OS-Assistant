from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.agents import create_react_agent, AgentExecutor
from os_assistant.utils.logger import get_logger
from langchain import hub
from os_assistant.core.settings import (
    GROQ_API_KEY,
    DEFAULT_GROQ_MODEL_NAME,
)
from groq import Groq


logger = get_logger(__name__)


class GroqModel:
    def __init__(self, model_name):
        self.model_name = self._resolve_groq_model(model_name)

    def _resolve_groq_model(self, model_name: str) -> str:
        """
        Resolve the Groq model name. If no model name is provided, return the default model name.
        Args:
            model_name: The requested Groq model name.
        Returns:
            str: The valid Groq model name.
        """
        if model_name is None:
            logger.info(
                f"No Groq model name specified. Using default model name: {DEFAULT_GROQ_MODEL_NAME}"
            )
            return DEFAULT_GROQ_MODEL_NAME

        client = Groq()
        models = client.models.list()
        available_models = [m.id for m in models.data]
        if model_name not in available_models:
            logger.error(
                f"Groq model '{model_name}' is not available. Available models are: {available_models}"
            )
            raise ValueError(
                f"Groq model '{model_name}' is not available. Available models are: {available_models}"
            )

        logger.info(f"Using specified Groq model name: {model_name}")
        return model_name


    def generate_response(
        self, human_message: str, system_message: str = None, structured_output=None
    ):
        """ """
        messages = [
            SystemMessage(content=system_message),
            HumanMessage(content=human_message),
        ]

        if not structured_output:
            llm = ChatGroq(
                model=self.model_name,
                api_key=GROQ_API_KEY,
            )

            logger.info("Generating response using Groq without structured output.")

            response = llm.invoke(messages)

            return response.content
        else:
            logger.info("Generating response using Groq with structured output.")

            llm = ChatGroq(
                model=self.model_name,
                api_key=GROQ_API_KEY,
                model_kwargs={
                    "tools": [{"name": "json"}],
                },
            )

            response = llm.with_structured_output(structured_output).invoke(messages)

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

        llm = ChatGroq(
            model=self.model_name,
            api_key=GROQ_API_KEY,
        )

        if tools is None:
            agent = create_react_agent(llm=llm, prompt=agent_prompt)
        else:
            agent = create_react_agent(llm=llm, prompt=agent_prompt, tools=tools)

        logger.info("Generating response using Groq, ReactAgent")

        agent_executor = AgentExecutor(
            agent=agent, tools=tools, verbose=True, handle_parsing_errors=True
        )
        agent_response = agent_executor.invoke({"input": human_message})["output"]

        return agent_response
