from langchain_mistralai import ChatMistralAI
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langsmith import traceable

from backend.agents.prompts.templates import systemInstructionTemplate
from backend.agents.tools.job_reader import get_job_summary
from backend.agents.tools.resume_extractor import extract_resume_text
from backend.config import get_settings

tools = [extract_resume_text, get_job_summary]


@traceable(name="PrepForge")
def assistant(state: MessagesState):
    settings = get_settings()
    llm = ChatMistralAI(
        model="mistral-medium-2508",
        api_key=settings.mistral_api_key,
    )
    llm_with_tools = llm.bind_tools(tools)
    return {
        "messages": [
            llm_with_tools.invoke([systemInstructionTemplate] + state["messages"])
        ]
    }


def create_builder():
    builder = StateGraph(MessagesState)
    builder.add_node("assistant", assistant)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "assistant")
    builder.add_conditional_edges("assistant", tools_condition)
    builder.add_edge("tools", "assistant")
    return builder.compile()
