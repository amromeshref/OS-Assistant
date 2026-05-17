from evaluation.runners.nodes.clarification_evaluation import clarification_evaluation_node
from evaluation.runners.nodes.final_response_evaluation import final_response_evaluation_node
from evaluation.runners.nodes.information_generation_evaluation import information_generation_evaluation_node
from evaluation.runners.nodes.user_validation_evaluation import user_validation_evaluation_node
from os_assistant.core.states.os_assistant_state import OSAssistantState
from os_assistant.utils.logger import get_logger

logger = get_logger(__name__)

class EvaluationGraph:
    def __init__(self, state: OSAssistantState):
        self.state = state
        self.clarification_evaluation_result = None
        self.final_response_evaluation_result = None
        self.information_generation_evaluation_results = None
        self.user_validation_evaluation_result = None

    def execute(self):
        logger.info("Starting Evaluation Graph")

        # Execute Clarification Evaluation Node
        self.clarification_evaluation_result = clarification_evaluation_node(self.state)

        # Execute User Validation Evaluation Node
        self.user_validation_evaluation_result = user_validation_evaluation_node(self.state)

        # Execute Information Generation Evaluation Node
        self.information_generation_evaluation_results = information_generation_evaluation_node(self.state.generated_information_responses)

        # Execute Final Response Evaluation Node
        self.final_response_evaluation_result = final_response_evaluation_node(self.state)

        logger.info("Completed Evaluation Graph")