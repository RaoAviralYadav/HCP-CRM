"""
LangGraph ReAct Agent for HCP CRM
Uses Groq's gemma2-9b-it model with 5 tools to manage HCP interactions.
"""

import os
import json
from typing import Annotated, TypedDict, Sequence
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition
from tools import log_interaction, edit_interaction, get_hcp_details, suggest_followup, summarize_interaction

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

TOOLS = [log_interaction, edit_interaction, get_hcp_details, suggest_followup, summarize_interaction]

SYSTEM_PROMPT = """You are an intelligent AI assistant for a Life Sciences CRM system that helps field sales representatives log and manage their interactions with Healthcare Professionals (HCPs).

You have access to 5 tools:
1. **log_interaction** - Log a new HCP interaction by extracting details from natural language. Always extract: HCP name, interaction type, date/time, topics, sentiment, materials, samples, and outcomes.
2. **edit_interaction** - Edit specific fields of an existing interaction. Requires interaction_id. Only update the fields the user mentions changing.
3. **get_hcp_details** - Look up HCP information from the database by name.
4. **suggest_followup** - Generate AI-powered follow-up recommendations after logging an interaction. Call this automatically after log_interaction when appropriate.
5. **summarize_interaction** - Generate a concise professional summary of interaction notes.

IMPORTANT RULES:
- When a user describes meeting an HCP, ALWAYS call log_interaction to populate the form.
- When a user says to correct/update/change something, ALWAYS call edit_interaction with only the changed fields.
- Today's date is available via the system. Use it when user says "today" or "just now".
- Extract sentiment from context: positive words → Positive, negative/frustrated → Negative, else → Neutral.
- After log_interaction succeeds, proactively call suggest_followup to provide smart recommendations.
- Always confirm actions taken and what fields were updated.
- Be concise and professional in your responses.
- If the user asks about an HCP, call get_hcp_details first.
- Current date: {current_date}
"""


def create_agent():
    """Create and return the compiled LangGraph agent."""
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model="llama-3.3-70b-versatile",
        temperature=0,
    )

    llm_with_tools = llm.bind_tools(TOOLS)

    class AgentState(TypedDict):
        messages: Annotated[Sequence[BaseMessage], lambda x, y: x + y]

    def call_model(state: AgentState):
        from datetime import datetime
        current_date = datetime.now().strftime("%Y-%m-%d")
        system = SystemMessage(content=SYSTEM_PROMPT.format(current_date=current_date))
        messages = [system] + list(state["messages"])
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    tool_node = ToolNode(TOOLS)

    workflow = StateGraph(AgentState)
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)
    workflow.set_entry_point("agent")
    workflow.add_conditional_edges("agent", tools_condition)
    workflow.add_edge("tools", "agent")

    return workflow.compile()


agent = create_agent()


def run_agent(conversation_history: list[dict], user_message: str) -> dict:
    """
    Run the agent with the full conversation history + new user message.
    Returns the final AI response and any form_data updates from tools.
    """
    from datetime import datetime

    # Convert history to LangChain messages
    messages = []
    for msg in conversation_history:
        role = msg.get("role")
        content = msg.get("content", "")
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))

    messages.append(HumanMessage(content=user_message))

    result = agent.invoke({"messages": messages})

    # Extract final AI text response
    final_message = result["messages"][-1]
    ai_response = final_message.content if hasattr(final_message, "content") else str(final_message)

    # Collect form_data from all tool results
    form_data = None
    tool_messages = [m for m in result["messages"] if isinstance(m, ToolMessage)]

    for tm in tool_messages:
        try:
            tool_result = json.loads(tm.content) if isinstance(tm.content, str) else tm.content
            if isinstance(tool_result, dict) and tool_result.get("success"):
                if "form_data" in tool_result:
                    form_data = tool_result["form_data"]
                # Handle suggest_followup partial updates
                if "form_data_update" in tool_result and form_data:
                    form_data.update(tool_result["form_data_update"])
                elif "form_data_update" in tool_result:
                    form_data = tool_result["form_data_update"]
        except Exception:
            pass

    return {
        "response": ai_response,
        "form_data": form_data,
    }