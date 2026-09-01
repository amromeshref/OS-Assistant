from oshope.core.graphs.cognition.cognition_graph import CognitionGraph
from oshope.core.graphs.planning.planning_graph import PlanningGraph
from oshope.core.graphs.execution.sequential.execution_graph import (
    SequentialExecutionGraph,
)
from oshope.core.graphs.execution.parallel.execution_graph import ParallelExecutionGraph
from oshope.core.graphs.memory.memory_graph import MemoryGraph
from oshope.core.states.oshope_state import OSHopeState
from oshope.utils.helper_functions import save_debug_state
from oshope.utils.logger import get_logger
from oshope.tools.rag.main import RAGTool
from oshope_evaluation.config import (
    PARALLEL_EXECUTION_ENABLED,
    RAG_ENABLED,
    DEBUG_MODE,
    DATASET_VERSION,
)
from oshope_evaluation.runners.evaluation_graph import EvaluationGraph
from oshope_evaluation.runners.pydantic_schemas import (
    DataPointEvaluation,
    StepResolverEvaluation,
    CommandExecutionEvaluation,
    CommandErrorHandlingEvaluation,
)
from rich.console import Console
from rich.markdown import Markdown
from pathlib import Path
import time
import json
import argparse

PARENT_DIR = Path(__file__).parent.parent.parent.parent
OS_ASISTANT_OUTPUT_DIR = (
    PARENT_DIR / "src/oshope_evaluation/outputs/os-assistant-output"
)
EVALUATION_OUTPUT_DIR = PARENT_DIR / "src/oshope_evaluation/outputs/evaluation-output"
DATASET_DIR = PARENT_DIR / f"src/oshope_evaluation/datasets/{DATASET_VERSION}"

logger = get_logger(__name__)


class EvaluationRunner:
    def __init__(self, parallel_execution: bool = PARALLEL_EXECUTION_ENABLED):
        self.equal_num = 50
        self.parallel_execution = parallel_execution
        self._init_os_assistant()
        self.execution_time = 0.0
        self.timer_start = None
        self.first_generated_clarification_response = "no output"
        self.first_generated_validation_response = "no output"

    def resume_timer(self):
        self.timer_start = time.perf_counter()

    def pause_timer(self):
        if self.timer_start is not None:
            self.execution_time += time.perf_counter() - self.timer_start

            self.timer_start = None

    def reset_timer(self):
        self.execution_time = 0.0
        self.timer_start = None

    def _init_os_assistant(self):
        # Graphs
        self.cognition_graph = CognitionGraph()
        self.planning_graph = PlanningGraph()

        if self.parallel_execution:
            self.execution_graph = ParallelExecutionGraph()
        else:
            self.execution_graph = SequentialExecutionGraph()

        self.cognition_graph.compile()
        self.planning_graph.compile()
        self.execution_graph.compile()

        if not self.parallel_execution:
            self.memory_graph = MemoryGraph()
            self.memory_graph.compile()

        if RAG_ENABLED:
            self.rag_tool = RAGTool()

    def load_dataset_point(self, data_point_id: int):
        data_point_path = DATASET_DIR / f"{data_point_id}.json"
        with open(data_point_path, "r") as file:
            data = json.load(file)
        return data

    def get_input(self):
        self.pause_timer()

        print("=" * self.equal_num)
        inp = input("YOU: ")

        if inp == "exit":
            print("Exiting...")
            exit(0)

        self.resume_timer()

        return inp

    # ================= PRINT AI MESSAGE =================
    def print_ai(self, text):
        self.pause_timer()

        print("=" * self.equal_num)
        print("AI:")
        self.render(text)
        print("=" * self.equal_num)

        self.resume_timer()

    def render(self, text):
        console = Console()
        console.print(Markdown(text))

    def append_hist(self, state: OSHopeState):
        state.multi_turn_conversation_history.append(
            {
                "turn_num": state.turn_num,
                "user_query": state.original_queries[-1],
                "assistant_response": state.multi_turn_generated_responses[-1],
            }
        )
        state.turn_num += 1

    def new_state_from(self, state: OSHopeState):
        """Clean state reset (you repeated this MANY times)"""
        new_state = OSHopeState()

        new_state.finalized_enhanced_query = state.finalized_enhanced_query
        new_state.original_queries = state.original_queries
        new_state.turn_num = state.turn_num
        new_state.multi_turn_conversation_history = (
            state.multi_turn_conversation_history
        )
        new_state.original_queries_enhanced = state.original_queries_enhanced
        new_state.multi_turn_generated_responses = state.multi_turn_generated_responses
        new_state.clarification_attempts = state.clarification_attempts

        new_state.query_clarification = state.query_clarification
        new_state.query_classification = state.query_classification

        return new_state

    # ================= CLARIFICATION LOOP =================
    def clarification_loop(self, state: OSHopeState):
        while True:
            state = self.cognition_graph.execute(state)

            if DEBUG_MODE:
                save_debug_state(state, "clarification")

            if not state.query_clarification.is_clarification_needed:
                return state

            self.print_ai(state.query_clarification.generated_response)
            state.multi_turn_generated_responses.append(
                state.query_clarification.generated_response
            )
            self.append_hist(state)

            follow_up = self.get_input()
            state.original_queries.append(follow_up)

    # ================= COGNITION =================
    def handle_cognition(self, state):
        while True:
            state = self.cognition_graph.execute(state)

            if DEBUG_MODE:
                save_debug_state(state, "cognition")

            if not state.query_classification.requires_follow_up:
                return state

            self.print_ai(state.query_clarification.generated_response)
            state.multi_turn_generated_responses.append(
                state.query_clarification.generated_response
            )
            self.append_hist(state)

            if self.first_generated_clarification_response == "no output":
                self.first_generated_clarification_response = (
                    state.query_clarification.generated_response
                )

            follow_up = self.get_input()
            state.original_queries.append(follow_up)

            # deeper clarification
            state = self.clarification_loop(state)

            # reset cleanly
            state = self.new_state_from(state)

    # ================= VALIDATION =================
    def validation_loop(self, state: OSHopeState):
        while state.user_validation.is_validation_required:
            self.print_ai(state.user_validation.generated_response)
            state.multi_turn_generated_responses.append(
                state.user_validation.generated_response
            )
            self.append_hist(state)

            if self.first_generated_validation_response == "no output":
                self.first_generated_validation_response = (
                    state.user_validation.generated_response
                )

            follow_up = self.get_input()
            state.original_queries.append(follow_up)

            state = self.planning_graph.execute(state)

            if DEBUG_MODE:
                save_debug_state(state, "validation")

        return state

    # ================= PLANNING =================
    def handle_planning(self, state):
        while True:
            state = self.planning_graph.execute(state)

            if DEBUG_MODE:
                save_debug_state(state, "planning")

            # clarification needed
            if state.planning.requires_follow_up:
                state.query_clarification.is_clarification_needed = True
                state = self.clarification_loop(state)
                state = self.new_state_from(state)
                continue

            # skip validation for info queries
            if state.query_classification.query_type == "information":
                return state

            # validation loop
            state = self.validation_loop(state)

            if state.user_validation.user_feedback_type == "update_plan":
                continue

            return state

    # ================= EXECUTION =================
    def handle_execution(self, state: OSHopeState):
        state = self.execution_graph.execute(state)

        self.print_ai(state.generated_final_response)
        state.multi_turn_generated_responses.append(state.generated_final_response)
        self.append_hist(state)

        if DEBUG_MODE:
            save_debug_state(state, "execution")

        return state

    def handle_memory(self, state: OSHopeState):
        state = self.memory_graph.execute(state)

        if DEBUG_MODE:
            save_debug_state(state, "memory")

        return state

    def handle_rag(self, state: OSHopeState):
        self.rag_tool.add_memories(
            session_id=state.turn_num, summaries=state.memory_extraction.summary
        )
        return state

    def run_os_assistant(self, query: str, data_point_id: int):

        self.resume_timer()

        state = OSHopeState()
        state.original_queries.append(query)

        state = self.handle_cognition(state)
        state = self.handle_planning(state)
        state = self.handle_execution(state)

        if not self.parallel_execution:
            state = self.handle_memory(state)

        if RAG_ENABLED:
            state = self.handle_rag(state)

        self.pause_timer()

        state.execution_time = self.execution_time

        self.reset_timer()

        state.first_generated_clarification_response = (
            self.first_generated_clarification_response
        )
        state.first_generated_validation_response = (
            self.first_generated_validation_response
        )

        self.save_os_assistant_output(
            state, data_point_id, parallel_execution=self.parallel_execution
        )

        return state

    def save_os_assistant_output(
        self, state: OSHopeState, data_point_id: int, parallel_execution: bool = False
    ):
        if parallel_execution:
            output_path = (
                OS_ASISTANT_OUTPUT_DIR
                / "parallel"
                / f"data-point-{data_point_id }-osass-output-parallel.json"
            )
        else:
            output_path = (
                OS_ASISTANT_OUTPUT_DIR
                / "sequential"
                / f"data-point-{data_point_id}-osass-output-sequential.json"
            )

        with open(output_path, "w") as f:
            json.dump(state.model_dump(), f, indent=4)

    def save_evaluation_output(
        self, data_point_evaluation: DataPointEvaluation, data_point_id: int
    ):
        output_path = (
            EVALUATION_OUTPUT_DIR / f"data-point-{data_point_id}-evaluation.json"
        )

        with open(output_path, "w") as f:
            json.dump(data_point_evaluation.model_dump(), f, indent=4)

    def run_evaluation(self, state: OSHopeState, data_point_id: int):
        evaluation_graph = EvaluationGraph(state)
        evaluation_graph.execute()

        data_point_evaluation = DataPointEvaluation(
            clarification_evaluation=evaluation_graph.clarification_evaluation_result,
            final_response_evaluation=evaluation_graph.final_response_evaluation_result,
        )

        data_point_evaluation.user_validation_evaluation = (
            evaluation_graph.user_validation_evaluation_result
        )

        for info_eval in evaluation_graph.information_generation_evaluation_results:
            data_point_evaluation.information_generation_evaluation.append(info_eval)

        if len(state.command_executions) == 0:
            data_point_evaluation.command_execution_analysis_evaluation.append(
                CommandExecutionEvaluation(evaluation_needed=False)
            )
        else:
            for _ in state.command_executions:
                data_point_evaluation.command_execution_analysis_evaluation.append(
                    CommandExecutionEvaluation()
                )

        if len(state.steps_resolver) == 0:
            data_point_evaluation.step_resolver_evaluation.append(
                StepResolverEvaluation(evaluation_needed=False)
            )
        else:
            for _ in state.steps_resolver:
                data_point_evaluation.step_resolver_evaluation.append(
                    StepResolverEvaluation()
                )

        if len(state.command_error_handlers) == 0:
            data_point_evaluation.command_error_handling_evaluation.append(
                CommandErrorHandlingEvaluation(evaluation_needed=False)
            )
        else:
            for _ in state.command_error_handlers:
                data_point_evaluation.command_error_handling_evaluation.append(
                    CommandErrorHandlingEvaluation()
                )

        self.save_evaluation_output(data_point_evaluation, data_point_id)

        return state


def main():
    parser = argparse.ArgumentParser(description="Run OS Assistant Evaluation")

    parser.add_argument(
        "--data_point_id", type=int, required=True, help="The ID for the data point"
    )

    parser.add_argument("--parallel_execution", type=bool, default=False)

    args = parser.parse_args()

    parallel = False

    if not parallel:
        runner = EvaluationRunner(parallel_execution=args.parallel_execution)
        data_point_details = runner.load_dataset_point(args.data_point_id)

        logger.info(f"Loaded data point details for ID: {args.data_point_id}")

        logger.info("Running OS Assistant...")
        state = runner.run_os_assistant(
            data_point_details["user_query"], args.data_point_id
        )
        logger.info("OS Assistant completed.")

        logger.info("Running Evaluation...")
        runner.run_evaluation(state, args.data_point_id)
        logger.info("Evaluation completed.")
    else:
        runner = EvaluationRunner(parallel_execution=True)
        data_point_details = runner.load_dataset_point(args.data_point_id)

        logger.info("Running OS Assistant with parallel execution...")
        state = runner.run_os_assistant(
            data_point_details["user_query"], args.data_point_id
        )
        logger.info("OS Assistant with parallel execution completed.")


if __name__ == "__main__":
    main()
