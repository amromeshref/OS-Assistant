import os

VOICE_INPUT_ENABLED = True
AVAILABLE_PLATFORMS = ["ollama", "groq"]
DEFAULT_PLATFORM = "groq"

# Node Names
QUERY_CLASSIFICATION_NODE = "query_classification_node"
QUERY_CLARIFICATION_NODE = "query_clarification_node"
PLANNER_NODE = "planner_node"

# Configuration for the clarification node
CLARIFICATION_NODE_MAX_ATTEMPTS = 3


# Ollama settings
DEFAULT_OLLAMA_MODEL_NAME = "llama3:8b"


# Groq settings
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
DEFAULT_GROQ_MODEL_NAME = "openai/gpt-oss-120b"