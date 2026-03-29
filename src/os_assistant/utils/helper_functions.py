import json
from pathlib import Path
from datetime import datetime
from typing import Union
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
