from os_assistant.utils.helper_functions import save_command_executions
from os_assistant.core.states.os_assistant_state import OSAssistantState, CommandExecution
from os_assistant.prompts.code_execution import get_code_execution_sys_prompt
from os_assistant.tools.command_execution import run_command
from os_assistant.utils.logger import get_logger
from os_assistant.core.models.main import LLMModel

logger = get_logger(__name__)

def code_execution_node(state: OSAssistantState) -> OSAssistantState:
    """
    Node responsible for executing code/commands as part of the execution graph.
    """
    logger.info("Starting code execution node.")

    # if(len(state.planning.command_steps) == 0):
    #     logger.info("No code execution steps provided")
    #     logger.info("Completed code execution node.")
    #     return state

    sys_prompt: str = get_code_execution_sys_prompt()
    llm_model = LLMModel()
    
    command = state.execution_orchestrator[-1].next_step.step_details.command

    # Command output after running
    command_output = run_command(command)

    human_message =f"""
User's original query: {state.finalized_enhanced_query}
Current command to execute: {command}
Command Output(After running):
{command_output}
"""
    
    response: CommandExecution = llm_model.generate_response(
        system_message=sys_prompt,
        human_message=human_message,
        structured_output=CommandExecution
    )

    # TODO: Add parsing logic here

    state.command_executions.append(response)
    state.executed_steps.append(response.summary)
    #state.current_step_index += 1
    #state.steps_done_indicies.append(state.execution_orchestrator[-1].next_step_index)

    save_command_executions(state.command_executions)

    state.command_execution_status = "completed"
    logger.info("Completed code execution node.")

    return state