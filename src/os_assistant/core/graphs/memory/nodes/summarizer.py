from os_assistant.core.states.os_assistant_state import OSAssistantState, SummarizerState
from os_assistant.core.settings import SESSION_ID
from os_assistant.prompts.summarizer import get_summarizer_sys_prompt, get_human_message
from os_assistant.utils.logger import get_logger
from os_assistant.core.models.main import LLMModel
from datetime import datetime
from typing import List
import json

logger = get_logger(__name__)


def save_session_memory(
    session_id: int,
    summaries: List[str],
    file_path: str = "memory/memory.jsonl",
) -> None:
    """
    Saves summarizer output into a JSONL memory file for RAG.
    Each line = one memory entry.
    """

    with open(file_path, "a", encoding="utf-8") as f:
        for text in summaries:
            record = {
                "session_id": session_id,
                "text": text,
                "timestamp": datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
            }

            f.write(json.dumps(record, ensure_ascii=False) + "\n")

def summarizer_node(state: OSAssistantState) -> OSAssistantState:
    """
    Node responsible for summarizing the current state of the assistant's memory and reasoning.
    """
    logger.info("Starting summarizer node.")

    sys_prompt: str = get_summarizer_sys_prompt()
    human_message: str = get_human_message(state)
    llm_model = LLMModel()

    response: SummarizerState = llm_model.generate_response(
        system_message=sys_prompt,
        human_message=human_message,
    )

    state.memory_extraction = response

    # Save the extracted memory into a JSONL file for RAG
    save_session_memory(
        session_id=SESSION_ID,
        summaries=response.summary,
    )

    logger.info("Completed summarizer node.")
    return state