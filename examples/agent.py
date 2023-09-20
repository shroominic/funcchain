from funcchain import chain, settings
from langchain.pydantic_v1 import BaseModel, Field
from codeboxapi import CodeBox


settings.OPENAI_API_KEY = "sk-*******"

codebox = CodeBox()
codebox.start()


tools = {
    "python": {
        "tutorial": "Insert a string of python code that gets executed.",
        "when_to_use": "If the user wants you to do something like plottings a graph, data analysis, or something else that requires python.",
        "run": codebox.run,
    },
    "bash": {
        "tutorial": "Insert a string of bash code that gets executed.",
        "when_to_use": "If the user wants you to do something like install a package, run a script, or something else that requires bash.",
        "run": lambda x: codebox.run("import os; os.system(f'{x}')"),
    },
    "final_answer": {
        "tutorial": "Insert a string of text that gets returned to the user.",
        "when_to_use": "If the user wants you to do something like answer a question, or something else that requires text.",
        "run": lambda x: x,
    },
}


class AgentAction(BaseModel):
    tool: str = Field(..., description="Name of the tool.")
    action_plan: str = Field(..., description="Plan of what to do with the tool.")
    action_input: str = Field(..., description="Input for the action.")


def agent_selector(user_query: str, tools: str) -> str:
    """
    Given a user query select the best strategy for it.
    You can choose from the following tools:
    {tools}
    """
    return chain()
