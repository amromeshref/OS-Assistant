import os

# Voice input settings
VOICE_INPUT_ENABLED = True
AVAILABLE_VOICE_PLATFORMS = ["whisper", "google"]
DEFAULT_VOICE_PLATFORM = "google"

# LLM Platforms
AVAILABLE_LLM_PLATFORMS = ["ollama", "groq"]
DEFAULT_LLM_PLATFORM = "groq"

# Node Names
QUERY_CLASSIFICATION_NODE = "query_classification_node"
QUERY_CLARIFICATION_NODE = "query_clarification_node"
PLANNING_NODE = "planning_node"
USER_VALIDATION_NODE = "user_validation_node"
EXECUTION_ORCHESTRATOR_NODE = "execution_orchestrator_node"
CODE_EXECUTION_NODE = "code_execution_node"
INFORMATION_NODE = "information_generation_node"
FINAL_RESPONSE_NODE = "final_response_node"
STEP_RESOLVER_NODE = "step_resolver_node"
CODE_ERROR_HANDLING_NODE = "code_error_handling_node"
SUMMARIZER_NODE = "summarizer_node"

# Configuration for the clarification node
# shourd be added to config dir
CLARIFICATION_NODE_MAX_ATTEMPTS = 10

# Configuration for the command error handling node
# should be added to config dir
COMMAND_ERROR_HANDLING_MAX_ATTEMPTS = 5


# Ollama settings
DEFAULT_OLLAMA_MODEL_NAME = "qwen2.5:14b-instruct-q5_K_M"


# Groq settings
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
DEFAULT_GROQ_MODEL_NAME = "openai/gpt-oss-120b"


SESSION_ID = 0