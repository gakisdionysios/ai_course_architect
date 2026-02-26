import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from agents.deconstructor import run_cypher
 

def professor_node(state, llm):
    """
    Reads 'research_notes' from Neo4j and generates the final lesson content,
    video scripts.
    """
    course_title = state.get("course_title", state.get("topic"))
    print(f"🎓 Professor: Drafting content for course '{course_title}'...")
    
    # 1. Find lessons that have Research but NO Content
    query = """
    MATCH (c:Course)-[:HAS_MODULE]->(m)-[:HAS_LESSON]->(l:Lesson)
    WHERE c.title CONTAINS $course_title 
      AND l.research_notes IS NOT NULL 
      AND (l.content_text IS NULL OR l.content_text = "")
    RETURN l.title as title, l.research_notes as notes
    """
    
    lessons_to_write = run_cypher(query, {"course_title": course_title})
    if not lessons_to_write:
        print("🎉 Professor: All researched lessons are already written!")
        return state
 
    for lesson in lessons_to_write:
        title = lesson['title']
        notes = lesson['notes']
        print(f"   ✍️ Writing lesson: '{title}'...")
 
        # Create the Full Content Chain
        # We use one prompt to encourage context consistency
        prompt = ChatPromptTemplate.from_template("""
        You are an EXPERT EDUCATOR. Based on the research notes provided, generate:
        1. A clear, engaging Markdown lesson (under 1500 words).
        2. A 1-minute video script with visual cues.
        3. A 3-question multiple-choice quiz, based on Markdown lesson you created.
 
        Research Notes: {notes}
        Lesson Title: {title}
 
        ### OUTPUT FORMAT ###
        Your response must be a valid JSON object with keys: "text", "script", and "quiz".
        The "quiz" key should be a list of objects: 
        [ {{"question": "..", "options": ["A", "B", "C", "D"], "answer": "correct option text"}}, ... ]
        Return ONLY the JSON.
        """)
        
        # Chain the prompt with the LLM and output parser
        chain = prompt | llm | StrOutputParser()
        raw_response = chain.invoke({"title": title, "notes": notes})
        try:
            # Clean and Parse
            clean_json = raw_response.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_json)
            # Save to Neo4j
            update_query = """
            MATCH (l:Lesson {title: $title})
            SET l.content_text = $text, 
                l.video_script = $script, 
                l.quiz_json = $quiz,
                l.status = 'complete'
            """
            run_cypher(update_query, {
                "title": title,
                "text": data.get('text', ''),
                "script": data.get('script', ''),
                "quiz": json.dumps(data.get('quiz', []))
            })
        except Exception as e:
            print(f"   ❌ Error processing JSON for {title}: {e}")
 
    print(state)