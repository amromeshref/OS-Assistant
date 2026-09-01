from oshope.core.states.planning_states import Step
from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, List


class StepResolverState(BaseModel):
    """
    Represents the state of the Step Resolver, which is responsible for resolving a step in the plan by replacing any placeholders with actual values from dependencies.
    """

    is_resolution_successful: bool = Field(
        default=False,
        description=(
            "Indicates whether the step was successfully resolved with all placeholders replaced by actual values from dependencies. "
            "This should be set to True if the step can be executed after resolution, and False if the step cannot be executed due to missing variables, invalid/empty inputs, or logical impossibility."
        ),
    )

    resolved_steps: List[Step] = Field(
        ...,
        description="The steps after resolving all placeholders with actual values from dependencies.",
    )

    resolution_reasoning: str = Field(
        default="",
        description=(
            "The reasoning behind how the step was resolved, including how placeholders were identified and replaced with values from dependencies."
        ),
    )


class CommandExecution(BaseModel):
    command: str = Field(
        ..., description="The exact command-line instruction that was executed."
    )

    success: bool = Field(
        ...,
        description=(
            "Indicates whether the command executed successfully. "
            "This should be set to true if the command executed without any errors and produced the expected output. "
            "This should be set to false if the command execution resulted in any errors, produced unexpected output, or failed to execute."
        ),
    )

    output: str = Field(
        ...,
        description="The standard output produced by the command, if any. If no output, set it as 'no output'.",
    )

    error: str = Field(
        default="",
        description="The error output produced by the command, if any. If no errors, set it as 'no errors'.",
    )

    summary: str = Field(
        default="",
        description="A short summary of the details of this command execution step",
    )

    model_config = ConfigDict(extra="allow")


class CommandErrorHandlerState(BaseModel):
    """
    Handles failed command executions by attempting to recover
    and generate a corrected command that fulfills the original step.
    """

    can_recover: bool = Field(
        default=False,
        description=(
            "Indicates whether the failed command execution can be recovered by generating a corrected command. "
            "This should be set to True if it is possible to generate a corrected command that fulfills "
            "the original step's intent. This should be set to False if recovery is not possible due to reasons such as syntax issues, missing files, invalid inputs, or logical impossibility."
        ),
    )

    recovery_reasoning: str = Field(
        default="",
        description=(
            "The reasoning behind whether recovery is possible or not."
            "If recovery is possible, this should explain how a corrected command can be generated to fulfill the original step's intent."
            "If recovery is not possible, this should explain why recovery cannot be achieved."
        ),
    )

    suggested_command: str = Field(
        default="",
        description=(
            "If can_recover = True, this should be the corrected command that is suggested to be executed to fulfill the original step's intent."
        ),
    )

    safety_risk: Literal["low", "medium", "high"] = Field(
        default="low",
        description=(
            "The safety risk level of executing the suggested command, if recovery is possible. "
            "This should be set to 'low' if the suggested command is safe to execute with minimal risk of causing harm or unintended consequences. "
            "This should be set to 'medium' if the suggested command carries some risk and should be executed with caution, potentially after reviewing the command and its implications. "
            "This should be set to 'high' if the suggested command carries a significant risk of causing harm or unintended consequences, and should only be executed after careful consideration and review."
        ),
    )

    execution_mode: Literal["blocking", "background"] = Field(
        ...,
        description=(
            "The execution mode of the command, either 'blocking' or 'background'."
            "'blocking' should be used when the command must complete and its output is needed for subsequent steps. "
            "'background' should be used when the command starts a long-running or GUI process and does not need to block execution of subsequent steps."
        ),
    )

    # messages: Optional[List[str]] = Field(default_factory=list),
    # remaining_steps: Optional[List[str]] = Field(default_factory=list)


class InformationResponse(BaseModel):
    query: str = Field(default="", description="The query or topic that was answered")

    answer: str = Field(default="", description="Clear and user-friendly explanation")

    model_config = ConfigDict(extra="allow")


class FinalResponse(BaseModel):
    """
    Final response sent to the user.
    """

    response: str = Field(
        ..., description="User-friendly final response combining all results"
    )

    summary: str = Field(default="", description="Short summary of what was done")


class SummarizerState(BaseModel):
    """
    Represents the state of the Summarizer, which is responsible for extracting durable and reusable information from the conversation history, execution plan, and executed steps to be stored in long-term memory for retrieval augmentation in future sessions.
    """

    summary_for_rag: List[str] = Field(
        default_factory=list,
        description=(
            "A list of key information extracted from the conversation history, execution plan, and executed steps"
        ),
    )

    session_summary: str = Field(
        default="",
        description=(
            "A concise summary of the entire session, including the user's queries, the execution plan, and the results of executed steps. This summary should provide a clear overview of what was accomplished during the session and any important context that may be relevant for future queries."
        ),
    )
