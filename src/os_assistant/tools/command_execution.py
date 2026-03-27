from os_assistant.utils.logger import get_logger
import subprocess

logger = get_logger(__name__)


def run_command(command: str) -> str:
    """
    Executes a system command and returns its output.
    """
    logger.info(f"Running the command: {command}")
    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )

        if result.returncode == 0:
            output = result.stdout.strip()
            logger.info(f"Command runned successfully!")
            return output if output else "Command executed successfully with no output."
        else:
            logger.error(
                f"Command failed with return code {result.returncode}: {result.stderr}"
            )
            return (
                f"Command failed with return code {result.returncode}: {result.stderr}"
            )

    except subprocess.CalledProcessError as e:
        logger.error(f"An error occurred while executing the command: {e.stderr}")
        return f"An error occurred while executing the command: {e.stderr}"
