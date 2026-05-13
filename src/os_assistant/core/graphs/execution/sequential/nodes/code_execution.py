from os_assistant.core.states.os_assistant_state import OSAssistantState, CommandExecution
from os_assistant.prompts.code_execution import get_code_execution_sys_prompt, get_human_message
from os_assistant.tools.command_execution import run_command
from os_assistant.utils.logger import get_logger
from os_assistant.core.models.main import LLMModel
from os_assistant.config.config import COMMAND_ERROR_HANDLING_MAX_ATTEMPTS

logger = get_logger(__name__)

def code_execution_node(state: OSAssistantState) -> OSAssistantState:
    """
    Node responsible for executing code/commands as part of the execution graph.
    """
    logger.info("Starting code execution node.")

    sys_prompt: str = get_code_execution_sys_prompt()
    llm_model = LLMModel()
    
    step_index = state.current_step_index

    if state.command_error_handler_active:
        if not state.command_error_handlers[-1].can_recover:
            logger.info("Cannot recover from the error, moving to the next step.")
            state.command_error_handler_active = False
            state.num_error_executions = 0
            
            if state.steps_resolver_active:
                state.current_resolving_step_index += 1
                total_resolved_steps = len(state.steps_resolver[-1].resolved_steps)
                if state.current_resolving_step_index >= total_resolved_steps:
                    logger.info("All resolved steps have been executed.")
                    state.steps_resolver_active = False
                    state.current_resolving_step_index = 0
                    state.current_step_index += 1
                    return state
            else:
                state.current_step_index += 1
                return state
        
        else:
            logger.info("Currently in command error handling mode, executing the recovery command.")
            command = state.command_error_handlers[-1].suggested_command
            execution_mode = state.command_error_handlers[-1].execution_mode

    elif state.steps_resolver_active:
        current_resolving_step_index = state.current_resolving_step_index
        current_resolving_step = state.steps_resolver[-1].resolved_steps[current_resolving_step_index]
        command = current_resolving_step.step_details.command
        execution_mode = current_resolving_step.step_details.execution_mode
        state.current_resolving_step_index += 1

    else:
        command = state.planning.plan_steps[step_index].step_details.command
        execution_mode = state.planning.plan_steps[step_index].step_details.execution_mode

    # Command output after running
    command_output = run_command(command, execution_mode)

    human_message = get_human_message(state.finalized_enhanced_query, command, command_output)
    
    response: CommandExecution = llm_model.generate_response(
        system_message=sys_prompt,
        human_message=human_message,
        structured_output=CommandExecution
    )

    response.step_index = step_index

    # TODO: Add parsing logic here

    state.command_executions.append(response)
    if response.success:
        state.executed_steps.append(response.summary)    
    
    #state.current_step_index += 1
    #state.steps_done_indicies.append(state.execution_orchestrator[-1].next_step_index)

    #save_command_executions(state.command_executions)

    if not response.success:
        if state.num_error_executions < COMMAND_ERROR_HANDLING_MAX_ATTEMPTS:
            logger.info("Command execution failed, routing to code error handling node.")
            state.command_error_handler_active = True
            return state
        else:
            logger.info("Could not resolve the error after maximum attempts, moving to the next step.")
            state.executed_steps.append(
                f"Could not resolve the error in step index {state.current_step_index} and description {state.planning.plan_steps[state.current_step_index].step_details.description} after {state.num_error_executions} recovery attempts."
            )
            state.command_error_handler_active = False
            state.num_error_executions = 0
    else:
        state.command_error_handler_active = False
        state.num_error_executions = 0

    if state.steps_resolver_active:
        print("="*90)
        print("debug me", state.current_resolving_step_index)
        print("="*90)
        current_resolving_step_index = state.current_resolving_step_index
        total_resolved_steps = len(state.steps_resolver[-1].resolved_steps)

        if current_resolving_step_index >= total_resolved_steps:
            logger.info("All resolved steps have been executed.")
            state.steps_resolver_active = False
            state.current_resolving_step_index = 0
            state.current_step_index += 1
    else:
        state.current_step_index += 1

    state.command_execution_status = "completed"
    logger.info("Completed code execution node.")

    return state