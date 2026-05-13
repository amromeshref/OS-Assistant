from os_assistant.core.states.os_assistant_state import OSAssistantState, CommandExecution, Step, StepResolverState
from os_assistant.prompts.code_execution import get_code_execution_sys_prompt, get_human_message
from os_assistant.core.graphs.execution.parallel.nodes.step_resolver import step_resolver_node
from os_assistant.tools.command_execution import run_command
from os_assistant.utils.logger import get_logger
from os_assistant.core.models.main import LLMModel
from os_assistant.config.config import COMMAND_ERROR_HANDLING_MAX_ATTEMPTS
from os_assistant.core.graphs.execution.parallel.update_state import update_state
from os_assistant.core.graphs.execution.parallel.occ import detect_resources, ResourceDetails
from pathlib import Path
from typing import List
import hashlib

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

def code_execution_node(state: OSAssistantState, step: Step, command_output: str) -> CommandExecution:
    """
    Node responsible for executing code/commands as part of the execution graph.
    """
    logger.info("Starting code execution node.")

    step_index = step.step_index

    sys_prompt: str = get_code_execution_sys_prompt()
    llm_model = LLMModel()
    
    if step.dependencies_required:
        #call step resolver
        step_resolver_response: StepResolverState= step_resolver_node(state, step)
        if step_resolver_response.is_resolution_successful:
            # execute steps in parallel
            pass
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

    human_message = get_human_message(state.finalized_enhanced_query, command, command_output)
    
    response: CommandExecution = llm_model.generate_response(
        system_message=sys_prompt,
        human_message=human_message,
        structured_output=CommandExecution
    )

    response.step_index = step_index

    if response.error:
        # call error handling node
        pass
    
    executed_step_summary = f"Could not resolve the error in step index {step_index} and description {step.step_details.description} after {state.num_error_executions} recovery attempts."

    logger.info("Completed code execution node.")

    update_state(state=state, response=response, executed_step_summary=executed_step_summary, step_index=step_index)

    return {
    "step_index": step_index,
    "success": True,
}