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
        '<p style="text-align: center; font-weight: bold; margin-top: -20px; margin-bottom: -10px; margin-left: -20px;">AI Course Architect</p>', 
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
    
    
    
    with st.sidebar:
        # A modern, slim section header
        st.markdown("""
            <div style="
                background: linear-gradient(90deg, rgba(0, 255, 255, 0.2) 0%, rgba(0, 255, 255, 0) 100%);
                border-left: 3px solid #00FFFF;
                padding: 5px 15px;
                margin: -10px 20px 5px -10px;
                color: #00FFFF;
                font-weight: bold;
                letter-spacing: 1px;
                text-transform: uppercase;
                font-size: 1.5rem;
            ">
                📚 My Space
            </div>
        """, unsafe_allow_html=True)

    topic_input = st.text_input("Enter a Topic:", placeholder="e.g. Quantum Physics...")
        
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
    # --- MAIN INPUT SECTION ---
if st.session_state['course_data'] is None:
    # First Row: Input + Step 1
    row1_col1, row1_col2 = st.columns([2, 1])
    with row1_col1:
        topic_input = st.text_input("Enter a Topic:", placeholder="e.g. Quantum Physics...", label_visibility="collapsed")
    with row1_col2:
        st.info("👈 **Step 1:** Enter your topic.")

    # Second Row: Step 2 + Button
    row2_col1, row2_col2 = st.columns([2, 1])
    with row2_col1:
        # Check if already generating to disable button
        is_gen = st.session_state.get('is_generating', False)
        if st.button("🚀 Generate Course", type="primary", use_container_width=True, disabled=is_gen):
            if topic_input:
                # Launch your thread logic here
                st.session_state['is_generating'] = True
                st.session_state['generation_logs'] = ["🛸 Deploying AI Agents..."]
                st.rerun()
    with row2_col2:
        st.warning("🚀 **Step 2:** Click the button to launch agents.")

    
    # 2. Main Hero Layout
    col_left, col_right = st.columns([5, 0.1])

    with col_left:
        # Create 3 equal columns for the cards
        card_col1, card_col2, card_col3 = st.columns(3)

        with card_col1:
            st.markdown("""
            <div style="background: rgba(255, 255, 255, 0.05); padding: 30px; border-radius: 15px; border-left: 5px solid #00C9FF; margin-bottom: 20px; min-height: 180px;">
    <h4 style="margin:0; color: #00C9FF;">📝 Rich, Easy-to-Read Lessons</h4>
    <p style="font-size: 1.1rem; color: #D0D0D0; line-height: 1.6;">
        Our AI acts as your personal researcher, gathering information from trusted sources across the web. 
        It then organizes everything into clear, structured chapters that make learning even the most complex topics feel simple and natural.
    </p>
</div>
            """, unsafe_allow_html=True)

        with card_col2:
            st.markdown("""
            <div style="background: rgba(255, 255, 255, 0.05); padding: 30px; border-radius: 15px; border-left: 5px solid #92FE9D; margin-bottom: 20px; min-height: 180px;">
    <h4 style="margin:0; color: #92FE9D;">🎬 Scripts for Your Own Videos</h4>
    <p style="font-size: 1.1rem; color: #D0D0D0; line-height: 1.6;">
        Want to teach others? Every lesson comes with a ready-made script. 
        Whether you want to record yourself or use an AI video creator, we provide the perfect words and visual cues to help you share your knowledge with the world.
    </p>
</div>
            """, unsafe_allow_html=True)

        with card_col3:
            st.markdown("""
            <div style="background: rgba(255, 255, 255, 0.05); padding: 30px; border-radius: 15px; border-left: 5px solid #6a11cb; margin-bottom: 20px; min-height: 180px;">
    <h4 style="margin:0; color: #6a11cb;">🧠 Fun Quizzes to Test Yourself</h4>
    <p style="font-size: 1.1rem; color: #D0D0D0; line-height: 1.6;">
        Learning is better when you know you're making progress. 
        At the end of each lesson, you'll find an interactive quiz designed to check your understanding and help you master the material before moving on to the next exciting topic.
    </p>
</div>
            """, unsafe_allow_html=True)




else:
    # Data is loaded - Show the Course Interface
    course = st.session_state['course_data']
    
    st.markdown(f'<h1 style="color: #00FFFF;"> Course Topic: {course["course_title"]}</h1>', unsafe_allow_html=True)    
    
    col_nav, col_content = st.columns([0.8, 2.5])

    with col_nav:     
        # Calculate overall progress and visualize progress bar
        all_lessons = [l for m in course['modules'] for l in m['lessons']]
        completed_lessons = [l for l in all_lessons if l.get('completed')]
        progress = len(completed_lessons) / len(all_lessons) if all_lessons else 0
        st.progress(progress)
        st.markdown(f'<h6 style="color: #ADD8E6 ;margin-top: -10px; margin-bottom: -10px;"> 📈 Course Progress: {int(progress * 100)}%</h6>', unsafe_allow_html=True)    
        
        st.markdown(f"### 📚 Curriculum")   
        
        prev_lesson_completed = True # The first lesson is always unlocked
        
        # Display Modules and Lessons
        # Display Modules and Lessons with Numbering
        for m_idx, module in enumerate(course['modules']):
            # numbering the Module (e.g., 1. Introduction)
            module_label = f"**Module {m_idx + 1}:** {module['title']}"
            
            with st.expander(f" {module_label}"):
                for l_idx, lesson in enumerate(module['lessons']):
                    
                    # numbering the Lesson (e.g., 1.1. Core Concepts)
                    lesson_label = f"{m_idx + 1}.{l_idx + 1}. {lesson['title']}"
                    
                    is_unlocked = prev_lesson_completed
                    
                    if is_unlocked:
                        # Inside your lesson loop
                        raw_title = lesson['title']

                        # Manual Wrap: Insert a newline every 25 characters so the button expands
                        if len(raw_title) > 25:
                            display_title = raw_title[:25] + "..." # Truncate for the button
                        else:
                            display_title = raw_title

                        lesson_label = f"{m_idx + 1}.{l_idx + 1}. {display_title}"

                        if st.button(lesson_label, key=f"btn_{m_idx}_{l_idx}", use_container_width=True):
    # logic
                            st.session_state['selected_module_idx'] = m_idx
                            st.session_state['selected_lesson_idx'] = l_idx
                            st.rerun()
                    else:
                        st.button(f"🔒 {lesson_label}", key=f"btn_{m_idx}_{l_idx}", disabled=True)
                    
                    prev_lesson_completed = lesson.get('completed', False)
                    


        with col_content:
            m_idx = st.session_state['selected_module_idx']
            l_idx = st.session_state['selected_lesson_idx']
            
            current_module = course['modules'][m_idx]
            current_lesson = current_module['lessons'][l_idx]

            # Wrap entire content in a styled container
            st.markdown(f"""
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px; opacity: 0.9;">
                    <span style="color: #ADD8E6; font-weight: 1000; font-size: 1.2rem;">📦 Module {m_idx + 1}</span>
                    <span style="color: #444;">/</span>
                    <span style="color: #00FFFF; font-weight: 1000; font-size: 1.2rem;">📖 Lesson {m_idx + 1}.{l_idx + 1}</span>
                </div>
                <div style="margin-bottom: -5px;">
                    <p style="color: #ADD8E6; font-style: italic; font-size: 1.2rem;">{current_module['title']}</p>
                    <h4 style="color: #00FFFF;">{current_lesson["title"]}</h4>
                </div>
            """, unsafe_allow_html=True)
            
            
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
                if st.button("✅ Mark Lesson as Completed", type="primary", width='stretch'):
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
                        
                    time.sleep(1)
                    st.rerun()