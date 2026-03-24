import subprocess

def check_ollama_installed() -> bool:
    """
    Check if Ollama is installed by trying to run 'ollama --version'.
    Returns True if Ollama is installed, False otherwise.
    """
    try:
        subprocess.run(["ollama", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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