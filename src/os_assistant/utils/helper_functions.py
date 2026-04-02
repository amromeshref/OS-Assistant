from os_assistant.core.states.os_assistant_state import CommandExecution, PlanningState, InformationResponse
import json
from pathlib import Path
from datetime import datetime
from typing import Union, List
import subprocess

DEBUG_STATE_PATH = "logs/debug_state.json"

def check_ollama_installed() -> bool:
    """
    Check if Ollama is installed by trying to run 'ollama --version'.
    Returns True if Ollama is installed, False otherwise.
    """
    try:
        subprocess.run(
            ["ollama", "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check_installed_ollama_model(model_name: str) -> bool:
    """
    Check if a specific Ollama model is installed by running 'ollama list'.
    Returns True if the model is found in the list, False otherwise.
    """
    result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
    if model_name in result.stdout:
        return True
    return False


def save_debug_state(state, title: str, path: Union[str, Path] = DEBUG_STATE_PATH) -> None:
    """
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Create new entry
    entry = {
        "title": title,
        "timestamp": datetime.now().strftime("%Y-%m-%d %I:%M:%S %p"),
        "state": state.model_dump(),
    }

    # Load existing data if file exists
    if path.exists():
        try:
            with open(path, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = []
    else:
        data = []

    # Append new state
    data.append(entry)

    # Save back
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

def planning_state_to_str(state: PlanningState) -> str:
    """
    Convert a PlanningState object into a human-readable string format for debugging or prompting purposes.
    Args:
        state (PlanningState): The PlanningState object to convert.
    Returns:
        str: A human-readable string representation of the PlanningState.    
    """
    lines = []

    # Fulfillment summary
    if state.fulfillment_summary:
        lines.append(f"Fulfillment Summary:\n{state.fulfillment_summary}\n")

    # Information steps
    if state.information_steps:
        lines.append("Information Steps:")
        for i, step in enumerate(state.information_steps, start=1):
            lines.append(f"  {i}. {step.description}")
        lines.append("")  # empty line

    # Command steps
    if state.command_steps:
        lines.append("Command Steps:")
        for i, step in enumerate(state.command_steps, start=1):
            lines.append(f"  {i}. Command: {step.command}")
            lines.append(f"     Description: {step.description}")
            lines.append(f"     Expected Output: {step.expected_output}")
            lines.append(f"     Safety Risk: {step.safety_risk}")
        lines.append("")

    # Follow-up reasoning
    if state.requires_follow_up:
        lines.append("Requires Follow-Up: Yes")
        if state.follow_up_reasoning:
            lines.append(f"Follow-Up Reasoning: {state.follow_up_reasoning}")
    else:
        lines.append("Requires Follow-Up: No")

    return "\n".join(lines)

def command_executions_to_str(executions: List[CommandExecution]) -> str:
    """
    Convert a list of CommandExecution objects into a human-readable string format for debugging or prompting purposes.
    Args:        
        executions (List[CommandExecution]): The list of CommandExecution objects to convert.
    Returns:        
        str: A human-readable string representation of the command executions.    
    """
    if not executions:
        return "No command executions."

    lines = []
    for i, exec in enumerate(executions, start=1):
        lines.append(f"Command {i}: {exec.command_line}")
        lines.append(f"  Success: {'Yes' if exec.success else 'No'}")
        lines.append(f"  Output: {exec.output or 'no output'}")
        lines.append(f"  Error: {exec.error or 'no errors'}")
        lines.append("")  # empty line for separation

    return "\n".join(lines)

def information_responses_to_str(responses: List[InformationResponse]) -> str:
    """
    Convert a list of InformationResponse objects into a human-readable string format for debugging or prompting purposes.
    Args:        
        responses (List[InformationResponse]): The list of InformationResponse objects to convert.
    Returns:        
        str: A human-readable string representation of the information responses.       
    """
    if not responses:
        return "No information responses."

    lines = []
    for i, response in enumerate(responses, start=1):
        lines.append(f"Response {i}:")
        lines.append(f"  Query: {response.query or 'N/A'}")
        lines.append(f"  Answer: {response.answer or 'N/A'}")
        lines.append("")  # empty line for readability

    return "\n".join(lines)