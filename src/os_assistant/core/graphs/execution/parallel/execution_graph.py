from os_assistant.core.states.os_assistant_state import OSAssistantState, Step
from os_assistant.core.graphs.execution.parallel.nodes.code_execution import code_execution_node
from os_assistant.core.graphs.execution.parallel.nodes.information_generation import information_generation_node
from os_assistant.core.graphs.execution.parallel.nodes.final_response import final_response_node
from os_assistant.core.graphs.execution.parallel.code_execution_manager import CommandBatchCoordinator
from os_assistant.core.graphs.execution.parallel.state_manager import update_state
from os_assistant.config.config import MAX_WORKERS
from os_assistant.utils.logger import get_logger
from os_assistant.core.graphs.memory.memory_graph import MemoryGraph
from os_assistant.utils.helper_functions import save_debug_state
from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed,
)
from typing import List
import threading

logger = get_logger(__name__)


class ParallelExecutionGraph:
    def __init__(self):
        self.memory_graph = MemoryGraph()
        self.memory_graph.compile()

    def _dependencies_satisfied(self, step: Step, steps: List[Step]) -> bool:
        for dep_idx in step.dependency_step_indices:
            if steps[dep_idx].status != "completed":
                return False
        return True
    
    def _get_next_execution_batch(self, steps: List[Step]) -> List[int]:
        """
        Returns:
        - list of step indices that can run in parallel
        - OR single next sequential step if no parallel batch exists
        """

        runnable = []

        # 1. collect all runnable steps
        for i, step in enumerate(steps):

            if step.status != "pending":
                continue

            if step.dependencies_required:
                if not self._dependencies_satisfied(step, steps):
                    continue

            runnable.append(i)

        # 2. if we found parallel candidates → return them
        if runnable:
            return runnable

        # 3. fallback: return next sequential pending step
        for i, step in enumerate(steps):
            if step.status == "pending":
                return [i]

        # 4. nothing left
        return []

    def _execute_step(self, state: OSAssistantState, step: Step, coordinator: CommandBatchCoordinator):
        logger.info(f"Executing step {step.step_index}")

        try:

            update_state(state=state, step_index=step.step_index, step_status="running")

            if step.step_type == "command":
                code_execution_node(state, step, coordinator)

            elif step.step_type == "information":
                information_generation_node(state, step)
            else:
                raise ValueError(
                    f"Unknown step type: "
                    f"{step.step_type}"
                )

            update_state(state=state, step_index=step.step_index, step_status="completed")

            logger.info(
                f"Completed step "
                f"{step.step_index}"
            )

            return {
                "step_index": step.step_index,
                "success": True,
            }

        except Exception as e:

            logger.exception(
                f"Failed step "
                f"{step.step_index}"
            )

            update_state(state=state, step_index=step.step_index, step_status="failed")

            return {
                "step_index": step.step_index,
                "success": False,
                "error": str(e),
            }
        

    def _execute_planned_steps(self, state: OSAssistantState, max_workers: int = MAX_WORKERS):

        logger.info("Starting parallel execution engine.")

        if state.user_validation.user_feedback_type == "rejected":

            logger.info("User rejected the plan during validation, routing to final response node.")

            with ThreadPoolExecutor(max_workers=2) as executor:

                memory_future = executor.submit(
                    self.memory_graph.execute,
                    state,
                )

                response_future = executor.submit(
                    final_response_node,
                    state,
                )

                memory_result = memory_future.result()

                save_debug_state(memory_result, "memory")

            return state

        steps = state.planning.plan_steps

        while True:

            # --------------------------------------
            # Find next runnable batch
            # --------------------------------------

            batch_indices = self._get_next_execution_batch(steps)

            if len(batch_indices) == 0:
                logger.info("No runnable steps remaining.")
                break

            batch_steps = [
                steps[i]
                for i in batch_indices
            ]

            logger.info(
                f"Executing batch: "
                f"{batch_indices}"
            )

            command_steps_size = 0
            for step in batch_steps:
                if step.step_type == "command":
                    command_steps_size += 1


            coordinator = CommandBatchCoordinator(expected_size=command_steps_size)

            executor_thread = threading.Thread(
                target=coordinator.execute_all,
                daemon=True
            )

            executor_thread.start()

            # --------------------------------------
            # Execute batch in parallel
            # --------------------------------------

            futures = {}
            

            with ThreadPoolExecutor(max_workers=max_workers) as executor:

                for step in batch_steps:

                    future = executor.submit(
                        self._execute_step,
                        state,
                        step,
                        coordinator,
                    )

                    futures[future] = step

                # ----------------------------------
                # Wait for completion
                # ----------------------------------

                for future in as_completed(futures):

                    result = future.result()

                    logger.info(
                        f"Finished step "
                        f"{result['step_index']}"
                    )

                    if not result["success"]:

                        logger.error(
                            f"Step failed: "
                            f"{result}"
                        )

            logger.info("Batch execution finished.")

        with ThreadPoolExecutor(max_workers=2) as executor:

            memory_future = executor.submit(
                self.memory_graph.execute,
                state,
            )

            response_future = executor.submit(
                final_response_node,
                state,
            )

            memory_result = memory_future.result()
                        
            save_debug_state(memory_result, "memory")

        logger.info("Execution engine completed.")

        state.memory_extraction = memory_result.memory_extraction
        state.past_session_summaries.append(memory_result.memory_extraction.session_summary)

        return state

    def compile(self) -> None:
        """
        Compile the execution graph to prepare it for execution.
        """
        logger.info("Execution graph compiled successfully.")

    def execute(self, initial_state: OSAssistantState) -> OSAssistantState:
        """
        Execute the compiled graph starting from the initial state and return the final state after execution.
        """
        logger.info("Executing the Parallel Execution graph.")
        final_state = self._execute_planned_steps(initial_state)
        logger.info("The Parallel Execution Graph execution completed.")
        return final_state