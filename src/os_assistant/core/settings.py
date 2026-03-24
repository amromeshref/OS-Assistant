import os


VOICE_ENABLED = False
AVAILABLE_PLATFORMS = ["ollama", "groq"]
DEFAULT_PLATFORM = "groq"

# Ollama settings
DEFAULT_OLLAMA_MODEL_NAME = "llama3:8b"


# Groq settings
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
DEFAULT_GROQ_MODEL_NAME = "openai/gpt-oss-120b"