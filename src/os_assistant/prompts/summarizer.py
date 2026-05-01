from os_assistant.core.states.os_assistant_state import OSAssistantState
from os_assistant.utils.helper_functions import planning_state_to_str

def get_summarizer_sys_prompt(structured_output=None):
    prompt = f"""
You are part of an OS Assistant system that helps users interact with their operating system by executing commands and providing system-related information (files, applications, settings, processes, and system status).

You are a Memory Extraction Engine for an OS Assistant system.

Produce a valid SummarizerState Object.

Your task is to analyze:
1. Full conversation history of a session
2. The planning node output (execution plan)
3. A summary of executed steps

and extract ONLY durable, reusable, and important information that should be stored in long-term memory for retrieval (RAG).


You must:
- Extract key user preferences and behavior patterns
- Extract important entities (emails, file paths, URLs, apps, commands)
- Extract system actions that were executed successfully
- Extract reusable workflows or procedures
- Extract important context that may help future queries
- Include errors or failures only if they are relevant for future prevention


You must NOT include:
- small talk
- redundant conversation
- temporary reasoning
- step-by-step chain-of-thought
- unnecessary repetition


IMPORTANT:
If a file path, command, tool usage, or email is mentioned, preserve it exactly as it may be required for future execution.

Your output will be stored in a long-term memory database used for retrieval augmentation in future sessions.
"""
    return prompt

def get_human_message(state: OSAssistantState):
    prompt = f"""
Here is the conversation history:
{str(state.multi_turn_conversation_history)}
Here is the current execution plan:
{planning_state_to_str(state.planning)}
Here is a summary of executed steps:
{str(state.executed_steps)}
"""
    return prompt