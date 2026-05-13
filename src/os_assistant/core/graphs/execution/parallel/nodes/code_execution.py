from os_assistant.core.states.os_assistant_state import OSAssistantState, CommandExecution, Step, StepResolverState, CommandErrorHandlerState
from os_assistant.prompts.code_execution import get_code_execution_sys_prompt, get_human_message
from os_assistant.core.graphs.execution.parallel.nodes.step_resolver import step_resolver_node
from os_assistant.tools.command_execution import run_command
from os_assistant.utils.logger import get_logger
from os_assistant.core.models.main import LLMModel
from os_assistant.config.config import COMMAND_ERROR_HANDLING_MAX_ATTEMPTS
from os_assistant.core.graphs.execution.parallel.update_state import update_state
from os_assistant.core.graphs.execution.parallel.occ import detect_resources, ResourceDetails
from os_assistant.core.graphs.execution.parallel.code_execution_manager import CommandBatchCoordinator
from os_assistant.core.graphs.execution.parallel.nodes.code_error_handling import code_error_handling_node
from pathlib import Path
from typing import List
import hashlib
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed

logger = get_logger(__name__)


def compute_file_hash(path: str):

    try:

        p = Path(path)

        if not p.exists():
            return None

        if p.is_dir():
            return str(p.stat().st_mtime)

        with open(p, "rb") as f:
            return hashlib.sha256(
                f.read()
            ).hexdigest()

    except Exception:
        return None

def compute_resource_snapshot(resources: List[ResourceDetails]):
    snapshot = {}

    for resource in resources:

        if resource.type != "file":
            continue

        snapshot[resource.identifier] = compute_file_hash(resource.identifier)

    return snapshot

def validate_resource_snapshot(snapshot: dict):
    for path, old_hash in snapshot.items():
        current_hash = compute_file_hash(path)
        if current_hash != old_hash:
            return False
    return True

def analyze_code_execution(state: OSAssistantState, command: str, command_output: str, step_index: int):
    sys_prompt: str = get_code_execution_sys_prompt()
    llm_model = LLMModel()

    human_message = get_human_message(state.finalized_enhanced_query, command, command_output)

    response: CommandExecution = llm_model.generate_response(
        system_message=sys_prompt,
        human_message=human_message,
        structured_output=CommandExecution
    )

    response.step_index = step_index

    # TODO: Send the generated command by error handler to user
    # TODO: Generated commands by error handlers should be executed sequantially in order of step index

    executed_step_summary = None
    if response.success:
        executed_step_summary = response.summary

    update_state(state=state, response=response, executed_step_summary=executed_step_summary, step_index=step_index)

    # Error handler bart
    if not response.success:
        if state.planning.plan_steps[step_index].num_error_executions >= COMMAND_ERROR_HANDLING_MAX_ATTEMPTS:
            executed_step_summary = f"Could not resolve the error in step index {step_index} and description {state.planning.plan_steps[step_index].step_details.description} after {state.planning.plan_steps[step_index].num_error_executions} recovery attempts."
            update_state(state=state, response=None, executed_step_summary=executed_step_summary, step_index=step_index)
            return

        response: CommandErrorHandlerState = code_error_handling_node(state, step_index)

        if not response.can_recover:
            return

        command = response.suggested_command
        execution_mode = response.execution_mode

        command_output = run_command(command, execution_mode)

        analyze_code_execution(state, command, command_output,step_index)

    return


def code_execution_node(state: OSAssistantState, step: Step, coordinator: CommandBatchCoordinator) -> CommandExecution:
    """
    Node responsible for executing code/commands as part of the execution graph.
    """
    logger.info("Starting code execution node.")

    step_index = step.step_index
    
    if step.dependencies_required:
        #call step resolver
        step_resolver_response: StepResolverState= step_resolver_node(state, step)
        if step_resolver_response.is_resolution_successful:
            resolved_steps = step_resolver_response.resolved_steps
        else:
            return {
    "step_index": step_index,
    "success": False,
    "reasoning": "step resolover failed"
}
        

    # command = step.step_details.command
    # execution_mode = step.step_details.execution_mode

    # # TODO: Optimistic Concurrency Control (OCC)

    # resources = detect_resources(command)

    # command_output = ""

    # while True:
    #     pre_execution_snapshot = compute_resource_snapshot(resources)

    #     # Command output after running
    #     command_output = run_command(command, execution_mode)

    #     if validate_resource_snapshot(pre_execution_snapshot):
    #         break

    commands = []
    execution_modes = []

    if step.dependencies_required:
        for step in resolved_steps:
            if step.step_type == "command":
                commands.append(step.step_details.command)
                execution_modes.append(step.step_details.execution_mode)
    else:
        commands.append(step.step_details.command)
        execution_modes.append(step.step_details.execution_mode)

    commands_output = coordinator.submit(
        step.step_index,
        commands,
        execution_modes,
    )

    if len(commands) > 1:
        # Call analyze code in parallel
        futures = []

        with ThreadPoolExecutor(max_workers=len(commands)) as executor:

            for command, output in zip(
                commands,
                commands_output,
            ):

                future = executor.submit(
                    analyze_code_execution,
                    state,
                    command,
                    output,
                    step_index,
                )

                futures.append(future)

            for future in as_completed(futures):

                try:
                    future.result()

                except Exception as e:
                    logger.exception(
                        f"Analyze code execution failed: {e}"
                    )
    else:
        analyze_code_execution(state, commands[0], commands_output[0], step_index)


    logger.info("Completed code execution node.")

    return {
    "step_index": step_index,
    "success": True,
}