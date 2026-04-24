from os_assistant.utils.logger import get_logger
import subprocess

logger = get_logger(__name__)


def run_command(command: str, execution_mode: str) -> str:
    """
    Executes a system command and returns its output.
    Supports background execution with partial output capture.
    """
    logger.info(f"Running the command: {command}")

    try:
        if execution_mode == "background":
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            try:
                # Wait briefly to catch immediate errors (e.g., command not found)
                stdout, stderr = process.communicate(timeout=1)

                if process.returncode is not None:
                    # Process exited quickly → likely error
                    if process.returncode != 0:
                        logger.error(f"Command failed with error: {stderr.strip()}")
                        return f"Command failed: {stderr.strip() or 'Unknown error'}"
                    
                    logger.info("Command executed successfully in the background.")
                    return stdout.strip() or "Command executed successfully."

            except subprocess.TimeoutExpired:
                # Process is still running → expected for background apps
                logger.info("Command is running in the background.")
                return "Command started successfully in background."

        # Foreground execution
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            logger.info("Command executed successfully.")
            return result.stdout.strip() or "Command executed successfully with no output."
        else:
            logger.error(f"Command failed with error: {result.stderr.strip()}")
            return f"Command failed: {result.stderr.strip()}"

    except Exception as e:
        logger.error(f"Unexpected error occurred: {str(e)}")
        return f"Error: {str(e)}"
