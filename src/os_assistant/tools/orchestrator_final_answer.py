from langchain.tools import Tool

orchestrator_final_answer_tool = Tool(
    name="ReturnFinalStep",
    func=lambda next_step: next_step,  # Identity function
    description="Use this tool to return the final step at the end."
)