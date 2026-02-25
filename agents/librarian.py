from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools.search import SEARCH_TOOLS  # Import the list of tools with @tool docstrings
from agents.deconstructor import run_cypher
from agents.llm import LlmFactory

def execute_agent_research(llm, course_topic, lesson_title):
    """
    Uses tool binding to let the LLM choose and execute the best tool.
    """
    # Bind the tools to the LLM
    llm_with_tools = llm.bind_tools(SEARCH_TOOLS)
    query = f"Research the following lesson: '{lesson_title}' for a course titled '{course_topic}'."
    # 1. LLM decides which tool to use
    response = llm_with_tools.invoke(query)
    # 2. Check if the LLM actually called a tool
    if response.tool_calls:
        tool_call = response.tool_calls[0]
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        print(f"   🔎 Librarian chose [{tool_name}] for: '{lesson_title}'")
        # Mapping names to the actual functions
        tool_map = {tool.name: tool for tool in SEARCH_TOOLS}
        selected_tool = tool_map.get(tool_name)
        if selected_tool:
            # Execute the tool
            raw_result = selected_tool.invoke(tool_args)
            return raw_result, tool_name
    # Fallback if no tool was called or something went wrong
    print(f"   ⚠️ No tool selected. Falling back to general search...")
    return SEARCH_TOOLS.invoke({"query": f"{lesson_title} {course_topic}"}), "search_tool"
 

def librarian_node(state, llm):
    topic_from_state = state.get("topic", "General Course")
    pending_query = """
    MATCH (c:Course)-[:HAS_MODULE]->(m)-[:HAS_LESSON]->(l:Lesson)
    WHERE c.title CONTAINS $course_title 
      AND (l.research_notes IS NULL OR l.research_notes = "")
    RETURN l.title as title, c.title as course_name
    """ 
    lessons_to_research = run_cypher(pending_query, {"course_title": topic_from_state})
    if not lessons_to_research:
        print("🎉 Librarian: No pending lessons found.")
        return state
 
    results_log = []
 
    for item in lessons_to_research:
        lesson_title = item['title']
        actual_course_title = item['course_name'] 
        # A. Intelligent Research (Binding Logic)
        raw_data, source_used = execute_agent_research(llm, actual_course_title, lesson_title)
        # B. Summarize for the Professor
        summary_prompt = ChatPromptTemplate.from_template("""
        Summarize the following raw research data into a concise set of notes for a professor.
        Focus on facts, dates, and definitions. Keep it under 200 words.
        RAW DATA: {data}
        """)
        chain = summary_prompt | llm | StrOutputParser()
        clean_notes = chain.invoke({"data": raw_data})
        # C. Save to Neo4j
        update_query = """
        MATCH (l:Lesson {title: $title})
        SET l.research_notes = $notes, l.source = $source
        """
        run_cypher(update_query, {
            "title": lesson_title, 
            "notes": clean_notes,
            "source": source_used
        })
        results_log.append(f"Researched '{lesson_title}' using {source_used}")
 
    state["research_log"] = results_log
    return state

