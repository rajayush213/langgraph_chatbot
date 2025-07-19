
"""
No Memory
With tools

On each iteration graph is reinitiated
"""

from typing import TypedDict, Annotated
from langgraph.graph import add_messages, StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage, HumanMessage
from langchain_community.tools.tavily_search import TavilySearchResults
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(model="llama-3.1-8b-instant")

class BasicChatState(TypedDict):
    messages: Annotated[list, add_messages]

search_tool = TavilySearchResults(max_results=2)
tools = [search_tool]

llm_with_tools = llm.bind_tools(tools=tools)

def chatbot(state: BasicChatState):
    return {
        "messages": [llm_with_tools.invoke(state["messages"])]
    }

def tools_router(state: BasicChatState):
    last_message = state["messages"][-1]
    if (hasattr(last_message, "tool_calls") and len(last_message.tool_calls)>0):
        return "tool_node"
    else:
        return END

tool_node = ToolNode(tools=tools) 

graph = StateGraph(BasicChatState)
graph.add_node("chatbot", chatbot)
graph.add_node("tool_node", tool_node)
graph.set_entry_point("chatbot")
graph.add_conditional_edges(
    "chatbot",
    tools_router
)
graph.add_edge("tool_node", "chatbot")

app = graph.compile()

while True:
    user_input = input("User: ")
    if user_input in ["exit", "end"]:
        break
    else:
        result = app.invoke({
            "messages": [HumanMessage(content=user_input)]
        })
        print(result)
