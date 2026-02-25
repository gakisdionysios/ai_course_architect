import os
import sys
from dotenv import load_dotenv
from neo4j import GraphDatabase
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.llm import LlmFactory  # Now it can find agents module



load_dotenv()

#temp 0 for strict execution of prompts 
llm = LlmFactory(mode="azure",temperature=0).get_llm()



# Connect to Local Neo4j
uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
user = os.getenv("NEO4J_USERNAME", "neo4j")
password = os.getenv("NEO4J_PASSWORD", "password") # Change this!

driver = GraphDatabase.driver(uri, auth=(user, password))



def run_cypher(query: str, parameters=None): 
    """Executes the raw Cypher query against the NEO4J database."""
    with driver.session() as session:
        try:
            # Pass the parameters to the session.run() method
            result = session.run(query, parameters or {}) 
            return [record.data() for record in result]
        except Exception as e:
            print(f"❌ Cypher Execution Error: {e}")
            return None


def generate_course_cypher(topic: str) -> str:
    """
    Asks the LLM to design a course on `topic` and write the 
    Cypher query to insert it into Neo4j.
    """
    
    prompt = f"""
    You are an expert Neo4j Database Architect for an educational platform.
    
    ### TASK
    Design a professional, logical curriculum for the topic: "{topic}".
    The course should have 3 Modules, and each Module should contain 3 Lessons.

    ### GRAPH SCHEMA REQUIREMENTS
    - **Nodes**:
      - `(:Course {{title: "..."}})`
      - `(:Module {{title: "...", order_index: int}})`
      - `(:Lesson {{title: "...", order_index: int}})`
    
    - **Relationships**:
      - `(:Course)-[:HAS_MODULE]->(:Module)`
      - `(:Module)-[:HAS_LESSON]->(:Lesson)`
      - `(:Module)-[:NEXT_MODULE]->(:Module)` : Links modules in chronological order.
      - `(:Lesson)-[:NEXT_LESSON]->(:Lesson)` : Links lessons within the SAME module.
      - `(:Module)-[:REQUIRES]->(:Module)` : Optional: link a module to a previous one if it's a prerequisite.

    ### LOGICAL RULES
    1. Use **MERGE** for the Course node.
    2. Use **MERGE** for all Modules and Lessons.
    3. Every node MUST have an `order_index` starting from 1 within its parent scope.
    4. Ensure the `NEXT_MODULE` and `NEXT_LESSON` chains are perfectly linear.

    ### OUTPUT INSTRUCTIONS
    - Return **ONLY** the raw Cypher query. 
    - **DO NOT** use markdown code blocks (no ```cypher). 
    - **DO NOT** include any conversational text or explanations.
    
    ### EXAMPLE SYNTAX
    MERGE (c:Course {{title: "{topic}"}})
    MERGE (m1:Module {{title: "Basics", order_index: 1}})
    MERGE (m2:Module {{title: "Advanced", order_index: 2}})
    MERGE (c)-[:HAS_MODULE]->(m1)
    MERGE (c)-[:HAS_MODULE]->(m2)
    MERGE (m1)-[:NEXT_MODULE]->(m2)
    MERGE (l1:Lesson {{title: "L1", order_index: 1"}})
    MERGE (m1)-[:HAS_LESSON]->(l1)
    """

    # Invoke LLM
    print(f"🤔 AI is designing the course for: {topic}...")
    response = llm.invoke(prompt)
    
    # Clean Output (Strip Markdown if the LLM disobeyed)
    cleaned_cypher = response.content.replace("```cypher", "").replace("```", "").strip()
    
    return cleaned_cypher


def create_course_in_db(topic: str):
    # Step 1: Generate the Query
    cypher_query = generate_course_cypher(topic)
    print(f"\n📝 Generated Cypher:\n{'-'*20}\n{cypher_query}\n{'-'*20}")
    
    # Step 2: Execute it
    print("🚀 Executing in Neo4j...")
    run_cypher(cypher_query)
    print(f"✅ Course '{topic}' created successfully!")


# create_course_in_db("Physics")



