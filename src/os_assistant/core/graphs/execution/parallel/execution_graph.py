from os_assistant.core.states.os_assistant_state import OSAssistantState, Step
from os_assistant.core.graphs.execution.parallel.nodes.code_execution import code_execution_node
from os_assistant.core.graphs.execution.parallel.nodes.information_generation import information_generation_node
from os_assistant.core.graphs.execution.parallel.nodes.final_response import final_response_node
from os_assistant.core.graphs.execution.parallel.nodes.code_error_handling import code_error_handling_node
from os_assistant.core.graphs.execution.parallel.nodes.step_resolver import step_resolver_node
from os_assistant.tools.command_execution import run_command
from os_assistant.core.graphs.execution.routing.logic import (
    route_after_starting,
    route_after_code_execution,
    router,
)
from os_assistant.config.config import (
    CODE_EXECUTION_NODE,
    INFORMATION_NODE,
    FINAL_RESPONSE_NODE,
    STEP_RESOLVER_NODE,
    CODE_ERROR_HANDLING_NODE
)

from os_assistant.utils.logger import get_logger
from langgraph.graph import StateGraph, END, START
from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed,
)
from typing import List
import threading
from dataclasses import dataclass, field

logger = get_logger(__name__)

@dataclass
class CommandRequest:

    step_index: int
    commands: List[str]
    execution_modes: List[str]

    result: List[str] = field(default_factory=list)
    error: Exception = None

    event: threading.Event = field(
        default_factory=threading.Event
    )

class CommandBatchCoordinator:

    def __init__(self, expected_size: int):

        self.expected_size = expected_size

        self.lock = threading.Lock()

        self.requests = {}

        self.all_submitted = threading.Event()

        self.results = {}

    def submit(self, step_index: int, commands: List[str], execution_modes: List[str]):

        request = CommandRequest(
            step_index=step_index,
            commands=commands,
            execution_modes=execution_modes,
        )

        with self.lock:
            self.requests[step_index] = request

            if len(self.requests) == self.expected_size:
                self.all_submitted.set()

        # wait for execution result
        request.event.wait()

        if request.error:
            raise request.error

        return request.result
    
    def execute_all(self):

        # wait until all commands submitted
        self.all_submitted.wait()

        # execute in strict order
        for step_index in sorted(self.requests.keys()):

            request: CommandRequest = self.requests[step_index]

            try:
                results = []
                for i in range(len(request.commands)):
                    output = run_command(
                        request.commands[i],
                        request.execution_modes[i],
                    )
                    results.append(output)
                
                request.result = results

            except Exception as e:
                request.error = e

            finally:
                request.event.set()


class ExecutionGraph:
    def __init__(self):
        pass

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

    def _execute_step(self, state: OSAssistantState, step: Step, command_outputs: dict):
        logger.info(f"Executing step {step.step_index}")

        try:

            step.status = "running"

            if step.step_type == "command":
                command_output = command_outputs[step.step_index]
                code_execution_node(state, step, command_output)

            elif step.step_type == "information":
                information_generation_node(state, step)
            else:
                raise ValueError(
                    f"Unknown step type: "
                    f"{step.step_type}"
                )

            step.status = "completed"

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

            step.status = "failed"

            return {
                "step_index": step.step_index,
                "success": False,
                "error": str(e),
            }
        
    def _execute_batch_commands(self, batch_steps: List[Step]):
        command_outputs = {}

        command_steps = [
            step
            for step in batch_steps
            if step.step_type == "command"
        ]

        # sort by step index
        command_steps.sort(key=lambda s: s.step_index)

        for step in command_steps:

            logger.info(
                f"Executing command for "
                f"step {step.step_index}"
            )

            command = step.step_details.command

            execution_mode = step.step_details.execution_mode

            output = run_command(command, execution_mode)

            command_outputs[step.step_index] = output

        return command_outputs

    def _execute_planned_steps(self, state: OSAssistantState, max_workers: int = 4):

        logger.info("Starting parallel execution engine.")

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

            # --------------------------------------
            # Execute batch in parallel
            # --------------------------------------

            futures = {}

            command_outputs = self._execute_batch_commands(batch_steps)
            

            with ThreadPoolExecutor(max_workers=max_workers) as executor:

                for step in batch_steps:

                    future = executor.submit(
                        self._execute_step,
                        state,
                        step,
                        command_outputs,
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

        logger.info("Execution engine completed.")

        return state
    
    def execute(self, initial_state: OSAssistantState) -> OSAssistantState:
        """
        Execute the compiled graph starting from the initial state and return the final state after execution.
        """
        logger.info("Executing the Parallel Execution graph.")
        final_state = self._execute_planned_steps(initial_state)
        logger.info("The Parallel Execution Graph execution completed.")
        return final_state