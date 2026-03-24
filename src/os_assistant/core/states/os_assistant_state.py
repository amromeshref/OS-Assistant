from pydantic import BaseModel

class OsAssistantState(BaseModel):
    """
    Represents the state of the OS Assistant, including any relevant information
    about the current session, user preferences, and system status.
    """
    original_prompt: str
    

