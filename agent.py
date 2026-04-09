from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from pathlib import Path
from dotenv import load_dotenv

# --- Load Environment Variables from current directory ---
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

from tools import (
    check_red_flag,
    map_symptoms,
    find_clinics,
    get_doctors,
    get_slots,
    book_appointment,
)

SYSTEM_PROMPT = (Path(__file__).parent / "system_prompt.txt").read_text(encoding="utf-8")

# --- State ---
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

# --- Tools list ---
TOOLS = [
    check_red_flag,
    map_symptoms,
    find_clinics,
    get_doctors,
    get_slots,
    book_appointment,
]

# --- LLM ---
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_with_tools = llm.bind_tools(TOOLS)

# --- Agent node ---
def agent_node(state: AgentState) -> AgentState:
    messages = state["messages"]

    # Inject system prompt nếu chưa có
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages

    response = llm_with_tools.invoke(messages)

    # Logging tool calls
    if response.tool_calls:
        for tc in response.tool_calls:
            print(f"[Tool] {tc['name']}({tc['args']})")
    else:
        print("[Agent] Trả lời trực tiếp")

    return {"messages": [response]}

# --- Build graph ---
builder = StateGraph(AgentState)
builder.add_node("agent", agent_node)
builder.add_node("tools", ToolNode(TOOLS))

builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition)
builder.add_edge("tools", "agent")

graph = builder.compile()