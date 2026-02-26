import streamlit as st
import time
import json
from workflow.workflow import langgraph_app
from agents.deconstructor import get_full_course_data, get_all_courses, mark_lesson_completed


st.set_page_config(page_title="AI Course Architect", layout="wide", page_icon="🎓", initial_sidebar_state="expanded")

def load_css(file_name):
    # Added encoding="utf-8" to handle special characters and icons
    with open(file_name, encoding="utf-8") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Load the external CSS file
load_css("assets/style.css")


if 'course_data' not in st.session_state:
    st.session_state['course_data'] = None
if 'selected_module_idx' not in st.session_state:
    st.session_state['selected_module_idx'] = 0
if 'selected_lesson_idx' not in st.session_state:
    st.session_state['selected_lesson_idx'] = 0


# SIDEBAR
with st.sidebar:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(
            "https://cdn-icons-png.flaticon.com/512/4712/4712009.png", 
            width=100
        )
    st.markdown(
        '<p style="text-align: center; font-weight: bold; margin-top: -10px; margin-left: -20px;">AI Course Architect</p>', 
        unsafe_allow_html=True
    )
    
    # Load saved courses from the Database
    existing_courses = get_all_courses()
    if existing_courses:
        st.subheader("📂 Your Library")
        selected_old_course = st.selectbox(
            "Load a previous course:",
            options=["-- Select --"] + existing_courses
        )
        
        if selected_old_course != "-- Select --":
            if st.button("Load Course"):
                with st.spinner("Retrieving from Database..."):
                    st.session_state['course_data'] = get_full_course_data(selected_old_course)
                    st.session_state['selected_module_idx'] = 0
                    st.session_state['selected_lesson_idx'] = 0
                    st.rerun()
    
    
    
    
    
    topic_input = st.text_input("Enter a Topic:", placeholder="e.g. Quantum Physics...")
    
    if st.session_state['course_data'] is None:
        st.info("☝️ **Step 1:** Enter any topic you want to learn about above.")
        st.warning("🚀 **Step 2:** Click the button below to create your course.")
        
    if st.button("🚀 Generate Course", type="primary"):
        if topic_input:
            with st.status("🛸 Deploying AI Agents...", expanded=True) as status_box:            
            # Prepare inputs for LangGraph
                inputs = {"topic": topic_input}
                
                # Run the graph and stream the node updates
                # 'langgraph_app' is the compiled workflow from workflow.py
                for output in langgraph_app.stream(inputs):
                    for node_name, metadata in output.items():
                        if node_name == "deconstructor":
                            st.write("🏗️ **Course Creator:**Creating Curriculum Content.")
                            status_box.update(label="📚 Researching Knowledge...", state="running")
                            
                        elif node_name == "librarian":
                            st.write("🔍 **Librarian:** Scouring Wikipedia & ArXiv & the Web for facts.")
                            status_box.update(label="✍️ Drafting Content...", state="running")
                            
                        elif node_name == "professor":
                            st.write("🎓 **Professor:** Generating lessons, scripts, and quizzes.")
                            status_box.update(label="✨ Finalizing Course...", state="running")

                # Final update when loop ends
                status_box.update(label="✅ Course Architected Successfully!", state="complete", expanded=False)
               
        # Pull the newly created course data from Neo4j to display in the UI
        with st.spinner("Loading your personalized classroom..."):
            course_data = get_full_course_data(topic_input)
            
            if course_data:
                st.session_state['course_data'] = course_data
                st.session_state['selected_module_idx'] = 0
                st.session_state['selected_lesson_idx'] = 0
                # Re-render the page with the new course data
                st.rerun()
            else:
                st.error("Agents failed to save data to Neo4j. Check console logs.")


# MAIN DISPLAY LOGIC
if st.session_state['course_data'] is None:
    # 1. Centered Header with refined spacing
    st.markdown("""
        <div style="text-align: center; margin-top: -30px; padding-bottom: 20px;">
            <h1 class="gradient-text" style="font-size: 3.5rem; margin-bottom: 0px;">
                The AI Course Architect
            </h1>
            <div style="display: flex; justify-content: center; align-items: center; gap: 10px;">
                <hr style="flex-grow: 1; border: none; border-top: 1px solid rgba(0, 255, 255, 0.2);">
                <h4 style="color: #00FFFF; font-weight: 300; margin: 0; white-space: nowrap;">
                    🎓 Your Personal Knowledge Engine
                </h4>
                <hr style="flex-grow: 1; border: none; border-top: 1px solid rgba(0, 255, 255, 0.2);">
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # 2. Main Hero Layout
    col_left, col_right = st.columns([5, 1])

    with col_left:
        st.markdown("### 🤖 Your Autonomous Learning Path")
        st.write("Unlock a fully automated educational experience. Enter a topic, and our multi-agent system orchestrates the entire production pipeline:")
        
        # Feature Blocks using Containerized Markdown for a "Card" feel
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 15px; border-left: 5px solid #00C9FF; margin-bottom: 15px;">
            <h4 style="margin:0;">📝 Depth-First Reading Material</h4>
            <p style="font-size: 0.9rem; color: #D0D0D0;">The <b>Architect</b> maps the curriculum while the <b>Librarian</b> sources facts from ArXiv and Wikipedia to generate comprehensive, structured lessons.</p>
        </div>
        
        <div style="background: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 15px; border-left: 5px solid #92FE9D; margin-bottom: 15px;">
            <h4 style="margin:0;">🎬 Production-Ready Video Scripts</h4>
            <p style="font-size: 0.9rem; color: #D0D0D0;">The <b>Professor</b> drafts scripts with visual cues. <i>How to use:</i> Paste these into an AI video generator or read them for a micro-learning series.</p>
        </div>
        
        <div style="background: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 15px; border-left: 5px solid #6a11cb; margin-bottom: 15px;">
            <h4 style="margin:0;">🧠 Interactive Knowledge Checks</h4>
            <p style="font-size: 0.9rem; color: #D0D0D0;">Every lesson includes a logic-verified quiz. Use these to track your progress and ensure mastery before the next module unlocks.</p>
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        # High-end Robot with Books icon
        st.image("assets/robot_icon.jpg", use_container_width=True)

    st.markdown("---")


else:
    # Data is loaded - Show the Course Interface
    course = st.session_state['course_data']
    
    st.markdown(f'<h1 style="color: #00FFFF;"> Course Topic: {course["course_title"]}</h1>', unsafe_allow_html=True)
    st.markdown(f"*{course.get('description', 'AI-Generated Professional Curriculum')}*")
    
    
    col_nav, col_content = st.columns([0.8, 2.5])

    with col_nav:
        st.subheader("📚 Curriculum")        
        # Calculate overall progress and visualize progress bar
        all_lessons = [l for m in course['modules'] for l in m['lessons']]
        completed_lessons = [l for l in all_lessons if l.get('completed')]
        progress = len(completed_lessons) / len(all_lessons) if all_lessons else 0
        
        st.markdown(f"##### 📈 Course Progress: {int(progress * 100)}%")
        st.progress(progress)
        
        prev_lesson_completed = True # The first lesson is always unlocked
        
        # Display Modules and Lessons
        for m_idx, module in enumerate(course['modules']):
            with st.expander(f"📦 {module['title']}"):
                for l_idx, lesson in enumerate(module['lessons']):
                    
                    is_unlocked = prev_lesson_completed
                    
                    if is_unlocked:
                        if st.button(lesson['title'], key=f"btn_{m_idx}_{l_idx}"):
                            st.session_state['selected_module_idx'] = m_idx
                            st.session_state['selected_lesson_idx'] = l_idx
                            st.rerun()
                    else:
                        st.button(f"🔒 {lesson['title']}", key=f"btn_{m_idx}_{l_idx}", disabled=True)
                        
                    # Update prev_lesson_completed for the next iteration
                    prev_lesson_completed = lesson.get('completed', False)
                    


        with col_content:
            m_idx = st.session_state['selected_module_idx']
            l_idx = st.session_state['selected_lesson_idx']
            
            current_module = course['modules'][m_idx]
            current_lesson = current_module['lessons'][l_idx]

            # Wrap entire content in a styled container
            st.markdown(f"#### Module: {current_module['title']}")
            st.markdown(f"### 📖 {current_lesson['title']}")
            
            
            tab1, tab2, tab3 = st.tabs(["📝 Reading Material", "🎬 Video Script", "🧠 Interactive Quiz"])

            with tab1:
                st.markdown(current_lesson['content']['text'])
            
            with tab2:
                st.info("💡 **Pro Tip:** Use this script to record a 5-minute micro-learning video.")
                st.code(current_lesson['content']['video_script'], language="markdown")
                
            with tab3:
                st.subheader("Knowledge Check")
                quiz_data_raw = current_lesson['content'].get('quiz_json')
                
                if quiz_data_raw:
                    try:
                        if isinstance(quiz_data_raw, str):
                            quiz_list = json.loads(quiz_data_raw)
                        else:
                            quiz_list = quiz_data_raw
                            
                        for i, q in enumerate(quiz_list):
                            st.markdown(f"**Q{i+1}: {q['question']}**")
                            user_choice = st.radio(
                                f"Select answer for Q{i+1}:", 
                                q['options'], 
                                key=f"quiz_{m_idx}_{l_idx}_{i}"
                            )
                            
                            if st.button(f"Check Answer {i+1}", key=f"check_{m_idx}_{l_idx}_{i}"):
                                if user_choice == q['answer']:
                                    st.success("Correct! 🎉")
                                else:
                                    st.error(f"Incorrect. The right answer was: {q['answer']}")
                            
                    except Exception as e:
                        st.warning("Quiz format error. The Professor is still learning!")
                        st.caption(f"Error details: {e}")
                else:
                    st.info("No quiz generated for this lesson yet. The Professor Agent might still be writing it.")            
            
            # Completion Button
            if not current_lesson.get('completed'):
                if st.button("✅ Mark Lesson as Completed", type="primary", use_container_width=True):
                    mark_lesson_completed(current_lesson['title'])
                    updated_data = get_full_course_data(course["course_title"])
                    st.session_state['course_data'] = updated_data
                    
                    # NEW: Check if this was the last lesson for celebration
                    new_all = [l for m in updated_data['modules'] for l in m['lessons']]
                    if all(l.get('completed') for l in new_all):
                        st.balloons()
                        st.toast("🏆 Congratulations! You've mastered the entire course!", icon="🎓")
                    else:
                        st.toast("Lesson Completed! Next one unlocked.", icon="🔓")
                        
                    time.sleep(2)
                    st.rerun()