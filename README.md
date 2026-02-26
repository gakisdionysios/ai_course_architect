# 🎓 AI-demy: Your Personal Knowledge Engine

<div align="center">
  <img src="https://cdn-icons-png.flaticon.com/512/4712/4712009.png" alt="AI-demy Logo" width="150" />
</div>

**AI-demy** is an intelligent, multi-agent AI framework that dynamically researches, curates, and generates comprehensive educational courses on any topic. Powered by cutting-edge LLMs and agent orchestration tools, AI-demy operates as your personal knowledge researcher and course architect.

## ✨ Features

- **Dynamic Course Generation**: Simply input a topic (e.g., *Quantum Computing*, *Machine Learning Basics*), and AI-demy will independently structure and build an entire curriculum.
- **📚 Multi-Agent Architecture**: 
  - **🏗️ Deconstructor (Course Creator)**: Formulates a structured curriculum roadmap based on the core topic.
  - **🔍 Librarian**: Scours reliable sources like Wikipedia, ArXiv, and the Web to gather accurate, context-rich facts.
  - **🎓 Professor**: Transforms raw data into rich lessons, writes presentation scripts, and constructs interactive self-assessment quizzes.
- **🎬 Micro-Learning Video Scripts**: Every lesson comes paired with a ready-made script for a 5-minute micro-learning video—perfect for educators and creators!
- **🧠 Interactive Quizzes**: Test your knowledge with dynamically generated quizzes that are seamlessly integrated into the UI.
- **📂 Persistent Library**: Complete with **Neo4j** graph database integration, your courses are saved automatically. Return anytime to seamlessly resume your learning.
- **📈 Progress Tracking**: Enjoy visual progress bars and strictly structured modules. Lessons lock and unlock interactively based on your course advancement.

## 🛠️ Technology Stack

- **Frontend Application**: [Streamlit](https://streamlit.io/)
- **Agent Orchestration**: [LangChain](https://python.langchain.com/) & [LangGraph](https://langchain-ai.github.io/langgraph/)
- **Database**: [Neo4j](https://neo4j.com/) (Graph DB)
- **Local Model Serving**: [Ollama](https://ollama.com/) & [LiteLLM](https://github.com/BerriAI/litellm) (orchestrated via Docker)
- **Cloud LLMs Supported**: [Groq](https://groq.com/), [OpenAI](https://openai.com/)
- **Data Tools**: `wikipedia`, `arxiv`, `DuckDuckGo Search`
- **Dependency Management**: Modern Python (`>= 3.13`) optimized with [uv](https://github.com/astral-sh/uv).

## 🚀 Getting Started

### 1. Prerequisites

- **Python**: 3.13+
- **Docker**: For running local services like ChromaDB, Ollama, and LiteLLM (Optional but highly recommended).
- **Neo4j**: A local or remote Neo4j instance to persist your courses (Configure via `.env`).

### 2. Installation

Clone the repository and install dependencies. We recommend using `uv` for blistering fast dependency resolution:

```bash
# Clone the repository
git clone https://github.com/your-username/ai-course-architect.git
cd ai-course-architect

# Sync dependencies using uv (or use standard pip install -r pyproject.toml)
uv sync
```

### 3. Environment Configuration

Create a `.env` file in the root directory (based on `.env.example` if applicable) and insert your API credentials for your preferred model providers and tools:

```env
# Fast LLM Inference (e.g., Groq)
GROQ_API_KEY="your-groq-api-key"
GROQ_MODEL="llama-3.3-70b-versatile"

# Optional: LangSmith metrics and tracing
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT="https://eu.api.smith.langchain.com"
LANGSMITH_API_KEY="your-langsmith-key"
LANGSMITH_PROJECT="AI-demy"

# Neo4j Graph DB Settings
NEO4J_URI="neo4j://localhost:7687"
NEO4J_USERNAME="neo4j"
NEO4J_PASSWORD="your-secure-password"
```

### 4. Setup Local Infrastructure (Optional)

If you plan to use local models, local proxy deployments, or need a local Vector/Graph database, spin up the included Docker setup:

```bash
cd docker
docker-compose up -d
cd ..
```

*Note: To run Neo4j locally, simply uncomment the `neo4j-db` service block inside `docker/docker-compose.yml` prior to starting it up.*

### 5. Launch Application

Fire up the Streamlit UI!

```bash
streamlit run app.py
```

## 🧠 Behind the Scenes

When you enter a topic and click **"Generate Course"**, a state-machine LangGraph workflow activates:
1. The **Deconstructor** plans out nodes for the topic, organizing a cohesive curriculum.
2. The **Librarian** dives into reliable datasets, grabbing scientific papers and fact-checked info.
3. The **Professor** molds those findings into polished copy. 
4. Post-generation, your course is meticulously indexed into a **Neo4j Graph Database**, saving your course securely.
5. The Streamlit component retrieves this course and renders a gorgeous, interactive classroom interface.

---
*Built by Marios Vlachoulis, Dionysis Gakis and Panagiotis Georgitseas for the Final Hackathon Project of the "Get Trained Get Hired" AI Engineer program curated by Accenture in Athens, February 2026*