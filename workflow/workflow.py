import os
 
from typing import TypedDict, List
 
from langgraph.graph import StateGraph, END
 
# Import Nodes
 
from agents.deconstructor import create_course_in_db
 
from agents.librarian import librarian_node
 
from agents.professor import professor_node
 
from agents.llm import LlmFactory
 
 
 
class AgentState(TypedDict):
 
    topic: str
 
    course_title: str
 
    lessons_processed: List[str]
 
    current_status: str
 
# Initialize LLM
 
llm = LlmFactory(mode='local', temperature=0.5).get_llm()
 
 
 
def deconstructor_node(state):
 
    topic = state["topic"]
 
    print(f"🏗️ Deconstructor: Designing course skeleton for '{topic}'...")
 
    create_course_in_db(topic)
 
    state["course_title"] = topic
 
    return state
 
 
 
workflow = StateGraph(AgentState)
 
# Add Nodes with LLM injection
 
workflow.add_node("deconstructor", deconstructor_node)
 
workflow.add_node("librarian", lambda state: librarian_node(state, llm))
 
workflow.add_node("professor", lambda state: professor_node(state, llm))
 
# Define the Path
 
workflow.set_entry_point("deconstructor")
 
workflow.add_edge("deconstructor", "librarian")
 
workflow.add_edge("librarian", "professor")
 
workflow.add_edge("professor", END)
 
# Compile
 
langgraph_app = workflow.compile()