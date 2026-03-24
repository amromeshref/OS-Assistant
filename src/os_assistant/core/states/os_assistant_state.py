from pydantic import BaseModel, Field
from typing import Literal, Optional

class ClassificationState(BaseModel):
    """
    Represents the classification of a user's query, including the enhanced query,
    type, confidence score, reasoning, and follow-up requirements.
    """
    enhanced_query: str = Field(..., description="The enhanced version of the user's original query, rewritten for better clarity and understanding.")
    query_type: Literal["command", "information", "both"] = Field(..., description="The type of query.")
    confidence_score: float = Field(..., ge=0, le=1, description="The confidence score of the classification.")
    classification_reasoning: str = Field(..., description="The reasoning behind the classification decision.")
    requires_follow_up: bool = Field(..., description="Indicates if a follow-up question is needed for clarification.")
    follow_up_reasoning: Optional[str] = Field(default=None, description="The reasoning for why a follow-up question is needed, if applicable.")


class OSAssistantState(BaseModel):
    """
    Represents the state of the OS Assistant, including any relevant information
    about the current session, user preferences, and system status.
    """
    original_query: str
    query_classification: ClassificationState = Field(default=None, description="The classification of the user's query.")
    query_classification_status: Optional[str] = Field(default=None, description="The status of the query classification process (e.g., 'pending', 'completed', 'error').")
    

