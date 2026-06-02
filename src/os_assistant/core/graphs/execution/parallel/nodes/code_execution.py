from os_assistant.core.states.os_assistant_state import OSAssistantState, CommandExecution, Step, StepResolverState, CommandErrorHandlerState
from os_assistant.prompts.code_execution import get_code_execution_sys_prompt, get_human_message
from os_assistant.core.graphs.execution.parallel.nodes.step_resolver import step_resolver_node
from os_assistant.tools.command_execution import run_command
from os_assistant.utils.logger import get_logger
from os_assistant.core.models.main import LLMModel
from os_assistant.config.config import COMMAND_ERROR_HANDLING_MAX_ATTEMPTS
from os_assistant.core.graphs.execution.parallel.state_manager import update_state
from os_assistant.core.graphs.execution.parallel.code_execution_manager import CommandBatchCoordinator
from os_assistant.core.graphs.execution.parallel.nodes.code_error_handling import code_error_handling_node
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed

logger = get_logger(__name__)

def analyze_code_execution(state: OSAssistantState, command: str, success: bool, command_output: str, error: str, step_index: int):
    sys_prompt: str = get_code_execution_sys_prompt()
    llm_model = LLMModel()

    summary = f"Executed command: {command} with success: {success}, output: {command_output}, error: {error}"
    command_execution = CommandExecution(
        command=command,
        success=success,
        output=command_output,
        error=error,
        summary=summary
    )

    command_execution.step_index = step_index

    # TODO: Send the generated command by error handler to user
    # TODO: Generated commands by error handlers should be executed sequantially in order of step index

    executed_step_summary = None
    if command_execution.success:
        executed_step_summary = command_execution.summary

    update_state(state=state, response=command_execution, executed_step_summary=executed_step_summary, step_index=step_index)

    # Error handler bart
    if not command_execution.success:
        if state.planning.plan_steps[step_index].num_error_executions >= COMMAND_ERROR_HANDLING_MAX_ATTEMPTS:
            executed_step_summary = f"Could not resolve the error in step index {step_index} and description {state.planning.plan_steps[step_index].step_details.description} after {state.planning.plan_steps[step_index].num_error_executions} recovery attempts."
            update_state(state=state, executed_step_summary=executed_step_summary, step_index=step_index)
            return

        response: CommandErrorHandlerState = code_error_handling_node(state, step_index)

        if not response.can_recover:
            return

        command = response.suggested_command
        execution_mode = response.execution_mode

        success, output, error = run_command(command, execution_mode)

        analyze_code_execution(state, command, success, output, error, step_index)

    return


def code_execution_node(state: OSAssistantState, step: Step, coordinator: CommandBatchCoordinator):
    """
    Node responsible for executing code/commands as part of the execution graph.
    """
    logger.info("Starting code execution node.")

    step_index = step.step_index
    
    if step.dependencies_required:
        #call step resolver
        step_resolver_response: StepResolverState = step_resolver_node(state, step)
        if step_resolver_response.is_resolution_successful:
            resolved_steps = step_resolver_response.resolved_steps
        else:
            commands = ["ignore"]
            execution_modes = ["ignore"]
            coordinator.submit(
                step_index,
                commands,
                execution_modes,
            )
            return {
    "step_index": step_index,
    "success": False,
    "reasoning": "step resolover failed"
}


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

    coordinator_output = coordinator.submit(
        step_index,
        commands,
        execution_modes,
    )

    if len(commands) > 1:
        # Call analyze code in parallel
        futures = []

        with ThreadPoolExecutor(max_workers=len(commands)) as executor:

            for i in range(len(commands)):
                command = commands[i]
                success, output, error = coordinator_output[i]
    
                future = executor.submit(
                    analyze_code_execution,
                    state,
                    command,
                    success,
                    output,
                    error,
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
        analyze_code_execution(state, commands[0], coordinator_output[0][0], coordinator_output[0][1], coordinator_output[0][2], step_index)


    logger.info("Completed code execution node.")

    return {
    "step_index": step_index,
    "success": True,
}