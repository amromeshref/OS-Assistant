from os_assistant.core.states.os_assistant_state import (
    OSAssistantState,
    ExecutionOrchestratorState,
)
from os_assistant.prompts.execution_orchestrator import (
    get_execution_orchestrator_sys_prompt,
)
from os_assistant.utils.helper_functions import planning_state_to_str
from os_assistant.tools.retrieve_execution_details import retrieve_execution_details_tool
from os_assistant.tools.retrieve_information_details import retrieve_information_details_tool
from os_assistant.tools.orchestrator_final_answer import orchestrator_final_answer_tool
from os_assistant.utils.logger import get_logger
from os_assistant.core.models import LLMModel

logger = get_logger(__name__)


def execution_orchestrator_node(state: OSAssistantState) -> OSAssistantState:
    """
    This node is responsible for orchestrating the execution of commands based on the generated plan and user validation feedback. It manages the flow of execution, handles any necessary adjustments, and ensures that the assistant's actions align with the user's intentions and the overall plan.
    Args:
        state (OSAssistantState): The current state of the OS Assistant, including the generated plan, user validation feedback, and any relevant context.
    Returns:
        OSAssistantState: The updated state after orchestrating the execution, which may include the results of executed commands and any adjustments made to the plan based on execution outcomes.
    """
    logger.info("Starting execution orchestrator node.")

    llm_model = LLMModel()
    sys_prompt = get_execution_orchestrator_sys_prompt()

    if len(state.executed_steps) == 0:
        human_message = f"""
This is the first turn of the execution orchestrator node. No steps have been executed yet.
I will give you the planning steps and your task is to Determine the NEXT valid step to execute.

Original user query: {state.finalized_enhanced_query}
Output Of Planning Node: {planning_state_to_str(state.planning)}

You MUST follow these rules:

1. STEP ORDER
- Always follow the plan order strictly
- Identify the step that has NOT been executed yet
- That is the ONLY candidate for the next step

2. DO NOT:
- Skip steps
- Reorder steps
- Repeat completed steps

3. DEPENDENCY CHECK (MANDATORY)
Before selecting the next step, verify:

- All required variables are available
- Any dependent previous steps have completed successfully
- No required step has failed

4. IF DEPENDENCY IS MISSING OR INVALID:
- DO NOT proceed
- STOP execution
- Clearly explain:
  - Which step cannot be executed
  - What dependency is missing or failed

5. VARIABLE RESOLUTION
- Replace ALL placeholders (e.g., {{var}}, $var)
- Use ONLY values from executed steps
- NEVER invent values

6. TOOL USAGE
- Use tools ONLY if:
  - You need more details about previous steps
  - You are unsure about a variable or result

What is the NEXT step?
"""
    else:
        human_message = f"""
This is a subsequent turn of the execution orchestrator node.
I will give you the planning steps and your task is to Determine the NEXT valid step to execute.
Original user query: {state.finalized_enhanced_query}
Output Of Planning Node: {planning_state_to_str(state.planning)}
Short summary of the steps(information or command) that have already been executed: {str(state.executed_steps)}

You MUST follow these rules:

1. STEP ORDER
- Always follow the plan order strictly
- Identify the step that has NOT been executed yet
- That is the ONLY candidate for the next step

2. DO NOT:
- Skip steps
- Reorder steps
- Repeat completed steps

3. DEPENDENCY CHECK (MANDATORY)
Before selecting the next step, verify:

- All required variables are available
- Any dependent previous steps have completed successfully
- No required step has failed

4. IF DEPENDENCY IS MISSING OR INVALID:
- DO NOT proceed
- STOP execution
- Clearly explain:
  - Which step cannot be executed
  - What dependency is missing or failed

5. VARIABLE RESOLUTION
- Replace ALL placeholders (e.g., {{var}}, $var)
- Use ONLY values from executed steps
- NEVER invent values

6. COMPLETION CHECK
- If ALL steps are already executed:
  → Return that execution is COMPLETE

7. TOOL USAGE
- Use tools ONLY if:
  - You need more details about previous steps
  - You are unsure about a variable or result
- When using a tool, always provide a precise and detailed query. Include the step’s description and any relevant context so the tool can accurately identify the correct step.

EXPECTED OUTCOME:

You must decide ONE of the following:
1) The next valid step (fully resolved)
2) STOP execution with a clear reason
3) Execution is COMPLETE

What is the NEXT step?
"""
    
    tools = [retrieve_execution_details_tool, retrieve_information_details_tool]

    react_agent_response: str = llm_model.generate_response_react_agent(
        system_message=sys_prompt,
        human_message=human_message,
        structured_output=None,
        tools=tools,
    )

    human_message = f"""
This is the output from the planning node: {planning_state_to_str(state.planning)}
ReactAgent Response(It may be the step index in the planning steps or the description of the step. Make sure to map the right one): {react_agent_response}
What is the next step?
Produce a valid ExecutionOrchestratorState object.
If all steps have been executed, set `is_execution_completed` to True and set `should_proceed` to False, and keep `next_step` as the default value(None).
"""
    response: ExecutionOrchestratorState = llm_model.generate_response(
        human_message=human_message,
        structured_output=ExecutionOrchestratorState
    )

    print(response.model_dump_json())

    # TODO: Implement parsing logic here

    # Update the variable execution contexts
    # if len(response.variable_execution_contexts) > 0:
    #     for var_context in response.variable_execution_contexts:
    #         state.variable_execution_contexts.append(var_context)

    state.execution_orchestrator.append(response)
    if not response.should_proceed:
        state.executed_steps.append(response.should_proceed_reasoning)
        
    logger.info("Completed execution orchestrator node.")

    return state
