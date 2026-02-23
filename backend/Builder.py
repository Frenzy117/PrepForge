import os
from langgraph.graph.message import MessagesState
from langchain_mistralai import ChatMistralAI
from langgraph.graph import MessagesState
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from IPython.display import Image, display
from .PromptRepository import systemInstructionTemplate
from backend.ResumeExtractor import extract_resume_text
from backend.JobReader import get_job_summary
from langsmith import traceable

tools = [extract_resume_text, get_job_summary]

@traceable(name="PrepForge")
def assistant(state: MessagesState):
    llm = ChatMistralAI(model="mistral-medium-2508", api_key=os.getenv("MISTRAL_API_KEY"))
    
    tool_node = ToolNode(tools)
    llm_with_tools = llm.bind_tools(tools)
    return {
        "messages": [llm_with_tools.invoke([systemInstructionTemplate] + state["messages"])]
    }

def create_builder():
    builder = StateGraph[MessagesState, None, MessagesState, MessagesState](MessagesState)
    builder.add_node("assistant", assistant)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "assistant")
    builder.add_conditional_edges("assistant", tools_condition)
    builder.add_edge("tools", "assistant")
    react_graph = builder.compile()
    # display(Image(react_graph.get_graph(xray=True).draw_mermaid_png()))
    return react_graph