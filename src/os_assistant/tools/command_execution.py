from os_assistant.utils.logger import get_logger
import subprocess

logger = get_logger(__name__)


def run_command(command: str, execution_mode: str) -> tuple[bool, str, str]:
    """
    Executes a system command and returns structured execution results.
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
                stdout, stderr = process.communicate(timeout=1)

                if process.returncode is not None:
                    if process.returncode != 0:
                        error = stderr.strip() or "Unknown error"
                        logger.error(f"Command failed with error: {error}")
                        
                        success = False
                        output = stdout.strip() or "no output"
                        return success, output, error

                    logger.info("Command executed successfully in the background.")

                    success = True
                    output = stdout.strip() or "no output"
                    error = "no errors"
                    return success, output, error

            except subprocess.TimeoutExpired:
                logger.info("Command is running in the background.")

                success = True
                output = "no output"
                error = "no errors"
                return success, output, error

        # Foreground execution
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            logger.info("Command executed successfully.")

            success = True
            output = result.stdout.strip() or "no output"
            error = "no errors"

            return success, output, error

        error = result.stderr.strip() or "Unknown error"
        logger.error(f"Command failed with error: {error}")

        success = False
        output = result.stdout.strip() or "no output"
            
        return success, output, error

    except Exception as e:
        logger.error(f"Unexpected error occurred: {str(e)}")

        success = False
        output = "no output"
        error = str(e)

        return success, output, error