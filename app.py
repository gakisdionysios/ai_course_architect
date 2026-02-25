import streamlit as st
import time
import json


st.set_page_config(page_title="AI Course Architect", layout="wide", page_icon="🎓")

def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Load the external CSS file
load_css("assets/style.css")

# ==========================================
# 1. MOCK BACKEND
# ==========================================
def generate_dummy_course(topic):
    """
    This function simulates the entire LangGraph process.
    """
    time.sleep(1.5) # Simulate AI "thinking"
    
    return {
        "course_title": f"Mastering {topic}: From Zero to Hero",
        "description": "A comprehensive AI-generated curriculum designed to take you from beginner to expert.",
        "modules": [
            {
                "title": "Module 1: Foundations",
                "lessons": [
                    {
                        "title": "1.1 The Core Concepts",
                        "content": {
                            "text": f"### Introduction to {topic}\n\n**{topic}** is a fundamental concept in modern systems. In this lesson, we explore the history and basic definitions.\n\n#### Key Takeaways\n* Understanding the 'Why' before the 'How'\n* Historical context and evolution\n* Core terminology definition\n\n> \"Complexity is the enemy of execution.\" - Tony Robbins",
                            "video_script": f"**[Scene: Modern studio background, Host looks at camera]**\n\nHOST: Welcome back! Today we are talking about {topic}. It might sound scary, but it's actually quite simple...\n\n(Cut to B-Roll of diagrams)\n\nHOST: Let's break it down."
                        }
                    },
                    {
                        "title": "1.2 Setting Up Your Environment",
                        "content": {
                            "text": "### Getting Started\n\nTo work with this technology, you need to install the following tools:\n\n1. **VS Code**: Your code editor.\n2. **Docker**: For containerization.\n3. **Python 3.10+**: The runtime.\n\n```bash\npip install dependency-x --upgrade\n```",
                            "video_script": "**[Scene: Screen recording of terminal]**\n\nHOST: Open your terminal and type the command you see on screen."
                        }
                    }
                ]
            },
            {
                "title": "Module 2: Advanced Techniques",
                "lessons": [
                    {
                        "title": "2.1 Scaling Up",
                        "content": {
                            "text": "### How to Scale\n\nWhen your application grows, you need to consider **horizontal** vs **vertical** scaling.\n\n* **Horizontal**: Adding more machines.\n* **Vertical**: Adding more power to one machine.",
                            "video_script": "**[Scene: Animation of servers multiplying]**\n\nHOST: Think of horizontal scaling like hiring more workers, while vertical scaling is like training one worker to be stronger."
                        }
                    }
                ]
            }
        ]
    }

# ==========================================
# 2. SESSION STATE
# ==========================================
if 'course_data' not in st.session_state:
    st.session_state['course_data'] = None
if 'selected_module_idx' not in st.session_state:
    st.session_state['selected_module_idx'] = 0
if 'selected_lesson_idx' not in st.session_state:
    st.session_state['selected_lesson_idx'] = 0

# ==========================================
# 3. SIDEBAR
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712009.png", width=50) # Placeholder Icon
    st.markdown("## **AI Course Architect**")
    st.caption("v1.0 Hackathon Build")
    st.markdown("---")
    
    topic_input = st.text_input("Enter a Topic:", placeholder="e.g. Quantum Physics...")
    
    if st.button("🚀 Generate Course", type="primary"):
        if topic_input:
            with st.spinner(f"Agents are researching '{topic_input}'..."):
                st.session_state['course_data'] = generate_dummy_course(topic_input)
                # Reset selection
                st.session_state['selected_module_idx'] = 0
                st.session_state['selected_lesson_idx'] = 0
                st.rerun()
        else:
            st.warning("Please enter a topic first.")

    st.markdown("---")
    with st.expander("🛠 System Status"):
        st.success("Neo4j: Connected")
        st.success("Ollama (Llama3): Active")
        st.info("LangGraph: Ready")

# ==========================================
# 4. MAIN DISPLAY LOGIC
# ==========================================
if st.session_state['course_data'] is None:
    # Welcome Screen with Modern Layout
    st.markdown('<p class="gradient-text">The AI Course Architect</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div style="height: 150px;"></div>', unsafe_allow_html=True)
        st.info("👈 **Start Here:** Enter a topic in the sidebar to launch the agents.")
    with col2:
        st.markdown("""
        ### 🤖 Transforming Knowledge into Curriculum
        Welcome to the future of education. This tool uses a swarm of autonomous AI agents to research, structure, and generate complete courses on **any topic** in seconds.
        
        **Powered by:**
        * 🕸️ **Neo4j** Graph Database
        * 🦜 **LangChain** & **LangGraph**
        * 🦙 **Ollama** Local LLMs
        """)


else:
    # Data is loaded - Show the Course Interface
    course = st.session_state['course_data']
    
    # Header
    st.markdown(f'<h1 style="color: #FAFAFA;">{course["course_title"]}</h1>', unsafe_allow_html=True)
    st.markdown(f"*{course['description']}*")
    st.markdown("---")
    
    # Layout: 1 Column Nav (Cards), 3 Column Content
    col_nav, col_content = st.columns([1, 2.5])

    with col_nav:
        st.subheader("📚 Curriculum")
        
        # NAVIGATION LOGIC
        for m_idx, module in enumerate(course['modules']):
            # We use Expanders to look like "Modules"
            with st.expander(f"📦 {module['title']}", expanded=(m_idx == st.session_state['selected_module_idx'])):
                for l_idx, lesson in enumerate(module['lessons']):
                    # Stylized selection
                    is_selected = (m_idx == st.session_state['selected_module_idx'] and l_idx == st.session_state['selected_lesson_idx'])
                    btn_label = f"📍 {lesson['title']}" if is_selected else lesson['title']
                    
                    if st.button(btn_label, key=f"btn_{m_idx}_{l_idx}", use_container_width=True):
                        st.session_state['selected_module_idx'] = m_idx
                        st.session_state['selected_lesson_idx'] = l_idx
                        st.rerun()

    with col_content:
        # Get the currently selected lesson
        m_idx = st.session_state['selected_module_idx']
        l_idx = st.session_state['selected_lesson_idx']
        
        current_module = course['modules'][m_idx]
        current_lesson = current_module['lessons'][l_idx]

        # Content Card
        with st.container():
            st.markdown(f"### 📖 {current_lesson['title']}")
            
            # Tabs for different content formats
            tab1, tab2, tab3 = st.tabs(["📝 Reading Material", "🎬 Video Script", "🧠 Interactive Quiz"])

            with tab1:
                st.markdown(current_lesson['content']['text'])
            
            with tab2:
                st.info("💡 **Pro Tip:** Use this script to record a 5-minute micro-learning video.")
                st.code(current_lesson['content']['video_script'], language="markdown")
                
            with tab3:
                st.warning("Construction in progress by Agent 'Professor'...")
                st.progress(0.4)