from pydantic import BaseModel, Field
from typing import Literal, Optional, List


class QueryClassificationState(BaseModel):
    """
    Represents the classification of a user's query, including the enhanced query,
    type, confidence score, reasoning, and follow-up requirements.
    """

    original_query_enhanced: str = Field(
        ...,
        description="The enhanced version of the user's original query, rewritten for better clarity and understanding.",
    )

    query_type: Literal["command", "information", "both"] = Field(
        ..., description="The type of query."
    )

    confidence_score: float = Field(
        ..., ge=0, le=1, description="The confidence score of the classification."
    )

    classification_reasoning: str = Field(
        ..., description="The reasoning behind the classification decision."
    )

    requires_follow_up: bool = Field(
        default=False,
        description="Indicates if a follow-up question is needed for clarification.",
    )

    follow_up_reasoning: Optional[str] = Field(
        default="",
        description="The reasoning for why a follow-up question is needed, if applicable.",
    )


class InformationStep(BaseModel):
    description: str = Field(
        ..., description="A human-readable description of the information to provide."
    )


class CommandStep(BaseModel):
    command: str = Field(..., description="The command to execute.")

    description: str = Field(
        ...,
        description="A short, human-readable explanation of what this command does.",
    )

    expected_output: Optional[str] = Field(
        default=None, description="What the command is expected to produce."
    )

    safety_risk: Literal["low", "medium", "high"] = Field(
        ..., description="The safety risk level of executing this command."
    )


class PlanningState(BaseModel):
    """
    Represents the execution plan generated for a user query.
    """

    fulfillment_summary: str = Field(
        ...,
        description=(
            "A high-level explanation of how the user's request will be fulfilled. "
            "This may describe reasoning steps, conceptual answers, or execution logic."
        ),
    )

    information_steps: List[InformationStep] = Field(
        default_factory=list,  # Empty list as default value
        description="A list of information steps that outline the information to be provided to the user.",
    )

    command_steps: List[CommandStep] = Field(
        default_factory=list,
        description="A list of command steps that outline the commands to be executed, along with their descriptions and expected outputs.",
    )


class CommandExecution(BaseModel):
    command_line: str = Field(
        ..., description="The exact command-line instruction that was executed."
    )

    success: bool = Field(
        ..., description="Indicates whether the command executed successfully."
    )

    output: str = Field(
        ..., description="The standard output produced by the command, if any."
    )

    error: Optional[str] = Field(
        default=None, description="The error output produced by the command, if any."
    )
    # messages: Optional[List[str]] = Field(default_factory=list),
    # remaining_steps: Optional[List[str]] = Field(default_factory=list)

class InformationResponse(BaseModel):
    query: str = Field(
        default=None,
        description="The query or topic that was answered"
    )
    
    answer: str = Field(
        default=None,
        description="Clear and user-friendly explanation"
    )

class FinalResponse(BaseModel):
    """
    Final response sent to the user.
    """

    response: str = Field(
        ..., description="User-friendly final response combining all results"
    )

    summary: Optional[str] = Field(
        default=None,
        description="Short summary of what was done"
    )

class OSAssistantState(BaseModel):
    """
    Represents the state of the OS Assistant, including any relevant information
    about the current session, user preferences, and system status.
    """

    # ========== User query & Classification ==========

    # This may inclue follow-up queries in addition to the original query
    original_query: str = Field(
        ..., description="The original query input by the user."
    )

    original_query_enhanced: str = Field(
        default=None,
        description="The enhanced version of the user's original query, rewritten for better clarity and understanding.",
    )

    query_classification: QueryClassificationState = Field(
        default=None, description="The classification of the user's query."
    )
    # This field should be updated by the parsing logic in the query classification node after receiving the response from the LLM
    # The generated response from the LLM must be in the format of QueryClassificationState, so we can directly assign it to this field
    # If an error occurs, retry and generate another response until we get a valid QueryClassificationState response or reach a maximum number of retries to avoid infinite loops
    query_classification_status: str = Field(
        default=None,
        description="The status of the query classification process (e.g., 'pending', 'completed', 'error').",
    )

    # ============ Follow-up query & Clarification ============

    # In case the original query requires a follow-up question for clarification
    clarification_attempts: int = Field(
        default=0,
        description="The number of attempts made to clarify the original query.",
    )

    generated_response_for_clarification: str = Field(
        default=None,
        description="The response generated by the LLM for clarification purposes, if applicable. It should be sent to the user to ask for clarification.",
    )

    # =========== Planning & User Validation ===========

    planning: PlanningState = Field(
        default=None,
        description="The execution plan generated for the user's query, including information steps and command steps.",
    )

    planning_status: str = Field(
        default=None,
        description="The status of the planning process (e.g., 'pending', 'completed', 'error').",
    )

    generated_response_for_user_validation: str = Field(
        default=None,
        description="The response generated by the LLM for user validation purposes. It should be sent to the user to validate the generated execution/information plan.",
    )

    user_validation_status: str = Field(
        default=None,
        description="The status of the user validation process (e.g., 'pending', 'completed', 'error').",
    )


    # =========== Execution ===========

    command_executions: List[CommandExecution] = Field(
        default_factory=list,
        description=(
            "A list of command execution results, detailing the outcome of each command "
            "that was run as part of fulfilling the user's request."
        ),
    )

    command_execution_status: str = Field(
        default=None,
        description="The status of the command execution process (e.g., 'pending', 'completed', 'error')."
    )

    # =========== Information Response ===========

    generated_information_responses: List[InformationResponse] = Field(
        default_factory=list,
        description="A list of generated responses to answer the information the user requested"
    )

    generated_information_responses_status: str = Field(
        default=None,
        description="The status of the information generation process (e.g., 'pending', 'completed', 'error')."
    )

    # =========== Final Response ===========
    final_response: FinalResponse = Field(
        default = None,
        description="Final response sent to the user"
    )

    final_response_status: str = Field(
        default=None,
        description="The status of the final response process (e.g., 'pending', 'completed', 'error')."
    )