import streamlit as st
import requests
import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd
import time
import sqlite3

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="GoCudos - Student Performance Monitoring",
    page_icon="🎓",
    layout="wide"
)

import os
from dotenv import load_dotenv
load_dotenv('prog.env')

API_URL = os.environ.get("API_URL", "http://127.0.0.1:8001")

# Auto-initialize database if it doesn't exist
if not os.path.exists("users.db"):
    import subprocess
    subprocess.run(["python", "init_db.py"], cwd=os.path.dirname(os.path.abspath(__file__)))

# ==========================================
# DYNAMIC HIGH-RES BACKGROUND DOWNLOADER
# ==========================================
import os
import base64

@st.cache_data
def get_base64_bg():
    bg_path = "neon_glass_highlight_bg_v2.jpg"
    if not os.path.exists(bg_path):
        import requests
        # Ultra HD 4K Dark Glass with sharp Neon Light Highlights / Abstract 3D Glass Render
        url = "https://images.unsplash.com/photo-1620641788421-7a1c342ea42e?q=100&w=2560&auto=format&fit=crop"
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            r = requests.get(url, headers=headers)
            with open(bg_path, "wb") as f:
                f.write(r.content)
        except:
            pass

    if os.path.exists(bg_path):
        with open(bg_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

img_b64 = get_base64_bg()

if img_b64:
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpeg;base64,{img_b64}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        [data-testid="stAppViewContainer"] {{
            background-image: url("data:image/jpeg;base64,{img_b64}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
    """, unsafe_allow_html=True)

# ==========================================
# CUSTOM CSS
# ==========================================
st.markdown("""
    <style>
    /* Add the AI Background Image */
    .stApp > header {
        background-color: transparent;
    }
    


    [data-testid="stHeader"] {
        background: rgba(0,0,0,0);
    }

    /* Glassmorphism effect over the background */
    .main {
        background-color: rgba(10, 12, 16, 0.45) !important;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
    }

    .title {
        font-size: 38px;
        font-weight: 800;
        color: #00f2fe;
        text-align: center;
        margin-bottom: 10px;
        text-shadow: 0px 2px 10px rgba(0, 242, 254, 0.4);
    }

    .subtitle {
        font-size: 18px;
        color: #d1d5db;
        text-align: center;
        margin-bottom: 30px;
    }

    .card {
        background: rgba(20, 25, 30, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
        color: white;
        margin-bottom: 20px;
    }

    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        padding: 20px;
        border-radius: 16px;
        color: #ffffff;
        text-align: center;
        font-size: 22px;
        font-weight: bold;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.4);
    }

    .risk-low {
        color: #10b981;
        font-weight: bold;
        font-size: 22px;
    }

    .risk-medium {
        color: #f59e0b;
        font-weight: bold;
        font-size: 22px;
    }

    .risk-high {
        color: #ef4444;
        font-weight: bold;
        font-size: 22px;
    }

    .small-title {
        font-size: 22px;
        font-weight: 700;
        color: #00f2fe;
        margin-top: 20px;
        margin-bottom: 10px;
    }
    
    [data-testid="stForm"] {
        background: rgba(10, 12, 16, 0.5);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        padding: 40px;
        border-radius: 16px;
        box-shadow: 0px 8px 32px rgba(0,0,0,0.8);
        text-align: center;
        max-width: 450px;
        margin: auto;
        margin-top: 50px;
        color: #ffffff;
    }
    
    [data-testid="stForm"] h2 {
        color: #00f2fe !important;
        text-shadow: 0px 0px 10px rgba(0, 242, 254, 0.3);
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = None
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! I am AgniVeda AI 🔥 How can I help you today?"}]
if "groq_messages" not in st.session_state:
    st.session_state.groq_messages = [{"role": "assistant", "content": "Hello! I am AgniVeda AI 🔥 I can help you with study tips, motivation, and performance improvement. How can I assist you today?"}]
if "roll_no" not in st.session_state:
    st.session_state.roll_no = None
if "username" not in st.session_state:
    st.session_state.username = None
if "name" not in st.session_state:
    st.session_state.name = "Student"

# ==========================================
# LOGIN PAGE
# ==========================================
if not st.session_state.logged_in:
    st.markdown('<div class="title">🚀 GoCudos</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Please log in to access your dashboard</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form"):
            st.markdown('<h2 style="color: #00f2fe; margin-bottom: 20px; text-align: center; text-shadow: 0px 0px 10px rgba(0, 242, 254, 0.3);">🔐 System Login</h2>', unsafe_allow_html=True)
            
            role = st.selectbox("👤 Select Role", ["Student", "Educator"])
            username = st.text_input("📝 Username")
            password = st.text_input("🔑 Password", type="password")
            
            submitted = st.form_submit_button("🚀 Login", use_container_width=True)
            if submitted:
                try:
                    conn = sqlite3.connect('users.db')
                    cursor = conn.cursor()
                    cursor.execute("SELECT role, roll_no, name FROM users WHERE username=? AND password=? AND role=?", (username, password, role))
                    user = cursor.fetchone()
                    conn.close()
                    
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.role = user[0]
                        st.session_state.roll_no = user[1]
                        st.session_state.name = user[2]
                        st.session_state.username = username
                        st.success(f"Welcome back, {user[2]}! Redirecting...")
                        st.rerun()
                    else:
                        st.error("Invalid Username, Password, or Role!")
                except Exception as e:
                    st.error(f"Database error: {e}")
            
            st.info("Demo Credentials:\n\n**Student**: stu1 / stu1 (RollNo: STU1000)\n\n**Educator**: edu1 / edu1")
        
# ==========================================
# MAIN APP
# ==========================================
else:
    # ==========================================
    # HEADER
    # ==========================================
    st.markdown('<div class="title">🚀 GoCudos</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">AI-powered student performance, risk prediction, and academic insights — by GoCudos</div>', unsafe_allow_html=True)

    # ==========================================
    # SIDEBAR
    # ==========================================
    st.sidebar.markdown(f"### 👤 Logged in as: **{st.session_state.role}**")
    
    # UPDATED MENU TABS FOR NEW LAYOUT
    if st.session_state.role == "Student":
        options = ["🏠 Dashboard", "📅 Attendance", "📊 Marks", "📚 Learning", "💡 Suggestions", "📚 Explore & Learn", "🔥 AgniVeda AI"]
    else:
        options = ["🏠 Home", "👩‍🏫 Educator Dashboard", "🔍 Student Intervention", "🧠 Predict New Student", "📚 Explore & Learn", "🔥 AgniVeda AI"]

    menu = st.sidebar.radio("📌 Navigation", options)

    
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.session_state.messages = [{"role": "assistant", "content": "Hello! I am AgniVeda AI 🔥 How can I help you today?"}]
        st.session_state.groq_messages = [{"role": "assistant", "content": "Hello! I am AgniVeda AI 🔥 I can help you with study tips, motivation, and performance improvement. How can I assist you today?"}]
        st.rerun()

    # ==========================================
    # HOME PAGE
    # ==========================================
    if menu == "🏠 Home":
        st.markdown("## 🚀 Project Overview")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown('<div class="metric-card">📈 Performance Prediction</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="metric-card">🚨 Risk Detection</div>', unsafe_allow_html=True)

        with col3:
            st.markdown('<div class="metric-card">💡 Smart Recommendations</div>', unsafe_allow_html=True)

        st.markdown("---")

        st.markdown("""
        ### 🔍 What this system does:
        - Predicts **student academic performance**
        - Detects **low / medium / high risk students**
        - Identifies **weak areas**
        - Generates **recommendations**
        - Visualizes **semester-wise progress**
        - Helps **educators monitor class performance**
        """)

        st.info("Use the sidebar to explore your dashboard and tools.")

    # ==========================================
    # STUDENT DASHBOARD (NEW LAYOUT)
    # ==========================================
    elif menu == "🏠 Dashboard":
        # Top Section Container
        st.markdown('<div class="small-title" style="margin-top:0;">Student Overview</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            try:
                df = pd.read_excel("student_performance_enhanced.xlsx")
                student_df = df[df["RollNo"] == st.session_state.roll_no]
                if not student_df.empty:
                    current_attendance = student_df.iloc[0]["Attendance"]
                    cgpa = round(student_df.iloc[0].get("Average", 87.5) / 10, 2)
                else:
                    current_attendance = 64
                    cgpa = 8.75
            except:
                current_attendance = 64
                cgpa = 8.75
                
            st.markdown(f"""
            <div class="card" style="display: flex; align-items: center; gap: 20px;">
                <img src="https://api.dicebear.com/7.x/avataaars/svg?seed={st.session_state.username}&backgroundColor=b6e3f4" width="80" style="border-radius: 50%; box-shadow: 0 0 10px #00f2fe;">
                <div>
                    <h3 style="margin:0; color:#00f2fe;">{st.session_state.name}</h3>
                    <p style="margin:0; color:#d1d5db;">Roll No: {st.session_state.roll_no}</p>
                    <p style="margin:0; color:#d1d5db;">Dept: Computer Science</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
            <div class="card" style="display: flex; justify-content: space-around; align-items: center; height: 125px;">
                <div style="text-align:center;">
                    <h2 style="margin:0; color:#10b981; font-size:32px;">{cgpa}</h2>
                    <p style="margin:0; color:#d1d5db; font-size:14px;">CGPA</p>
                </div>
                <div style="text-align:center;">
                    <h2 style="margin:0; color:#10b981; font-size:32px;">0</h2>
                    <p style="margin:0; color:#d1d5db; font-size:14px;">Backlogs</p>
                </div>
                <div style="text-align:center;">
                    <h1 style="margin:0; font-size:36px;">🥇</h1>
                    <p style="margin:0; color:#d1d5db; font-size:14px;">Rank: 4th</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown('<div class="small-title">Performance Analytics</div>', unsafe_allow_html=True)
        
        col_mid1, col_mid2 = st.columns([1, 2])
        
        att_color = "#10b981" if current_attendance >= 75 else "#ef4444"
        
        with col_mid1:
            st.markdown(f"""
            <div class="card" style="height: 380px;">
                <h4 style="color:#00f2fe; margin-top:0;">🏆 Achievements</h4>
                <hr style="border-color: rgba(255,255,255,0.1); margin: 10px 0;">
                <div style="margin-top: 20px;">
                    <p style="font-size: 16px; margin-bottom: 15px;"><b>📅 Attendance:</b> <span style="color:{att_color};">{current_attendance}%</span></p>
                    <p style="font-size: 16px; margin-bottom: 15px;"><b>📝 Quizzes:</b> <span style="color:#10b981;">14/15</span></p>
                    <p style="font-size: 16px; margin-bottom: 15px;"><b>🧠 Performance:</b> Excellent</p>
                    <p style="font-size: 16px;"><b>⭐ Extra-curricular:</b> Active</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_mid2:
            perf_data = pd.DataFrame({
                "Subject": ["Math", "Physics", "Chemistry", "CS", "English"],
                "Marks": [88, 76, 82, 95, 89]
            })
            fig = px.bar(perf_data, x="Subject", y="Marks", color="Marks", color_continuous_scale="blues", title="Recent Marks Trend")
            # Styled internal Plotly background to match the glass cards natively
            fig.update_layout(paper_bgcolor="rgba(255, 255, 255, 0.05)", plot_bgcolor="rgba(0,0,0,0)", font_color="white", margin=dict(l=20, r=20, t=40, b=20), height=380)
            st.plotly_chart(fig, use_container_width=True)
            
        st.markdown('<div class="small-title">Anonymous Ranking</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="card">
            <h4 style="color:#00f2fe; margin-top:0;">📊 Peer Comparison</h4>
            <p style="color:#d1d5db;">Your current position among your classmates based on aggregate performance.</p>
            <div style="width:100%; height:8px; background:rgba(255,255,255,0.1); border-radius:4px; margin: 25px 0 15px 0; position:relative;">
                <div style="position:absolute; left: 8%; top:-18px; font-size: 24px;">📍</div>
                <div style="width: 15%; height:100%; background:#00f2fe; border-radius:4px;"></div>
            </div>
            <p style="margin-bottom:0;">You are in the <b>Top 8%</b> of your class.</p>
        </div>
        """, unsafe_allow_html=True)

    # ==========================================
    # ATTENDANCE MODULE
    # ==========================================
    elif menu == "📅 Attendance":
        st.markdown("## 📅 Attendance Overview")
        st.write("Extracting your logged attendance directly from the academic dataset...")
        try:
            df = pd.read_excel("student_performance_enhanced.xlsx")
            student_df = df[df["RollNo"] == st.session_state.roll_no]
            if not student_df.empty:
                attendance_percent = student_df.iloc[0]["Attendance"]
            else:
                attendance_percent = 64
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown(f"""
                <div class="card" style="text-align: center; padding: 50px;">
                    <h1 style="font-size: 80px; margin:0; color: #00f2fe; text-shadow: 0px 0px 20px rgba(0,242,254,0.5);">{attendance_percent}%</h1>
                    <h3 style="color: #d1d5db; margin:0; margin-top:10px;">Overall Attendance</h3>
                </div>
                """, unsafe_allow_html=True)
                
                st.write("")
                if attendance_percent < 75:
                     st.error("⚠️ Warning: Your attendance has fallen below the 75% threshold mandated by the university! You are at risk of detention.")
                elif attendance_percent >= 90:
                     st.success("🌟 Excellent! You have maintained a highly commendable attendance record.")
                else:
                     st.info("✅ Good standing. Ensure you continue attending regularly to stay safe.")
        except Exception as e:
            st.error(f"Error loading student_performance_enhanced.xlsx dataset: {e}")

    # ==========================================
    # MARKS MODULE
    # ==========================================
    elif menu == "📊 Marks":
        st.markdown("## 📊 Academic Marks Entry")
        st.write("Enter your 3 recent Test marks. These will be analyzed by the AI engine to generate improvement strategies.")
        
        # Initialize in session_state if not exists
        if "test1" not in st.session_state: st.session_state.test1 = 0
        if "test2" not in st.session_state: st.session_state.test2 = 0
        if "test3" not in st.session_state: st.session_state.test3 = 0

        col1, col2, col3 = st.columns(3)
        with col1:
             st.session_state.test1 = st.number_input("Test 1 Marks (out of 100)", 0, 100, st.session_state.test1)
        with col2:
             st.session_state.test2 = st.number_input("Test 2 Marks (out of 100)", 0, 100, st.session_state.test2)
        with col3:
             st.session_state.test3 = st.number_input("Test 3 Marks (out of 100)", 0, 100, st.session_state.test3)

        if sum([st.session_state.test1, st.session_state.test2, st.session_state.test3]) > 0:
            st.markdown('<div class="small-title">Trend Visualization</div>', unsafe_allow_html=True)
            marks_df = pd.DataFrame({
                "Test": ["Test 1", "Test 2", "Test 3"],
                "Score": [st.session_state.test1, st.session_state.test2, st.session_state.test3]
            })
            fig = px.line(marks_df, x="Test", y="Score", markers=True, title="Recent Test Progression")
            fig.update_layout(paper_bgcolor="rgba(255, 255, 255, 0.05)", plot_bgcolor="rgba(0,0,0,0)", font_color="white", yaxis=dict(range=[0, 100]))
            st.plotly_chart(fig, use_container_width=True)
            
        st.success("Marks auto-saved in your dashboard session! Head to 'Suggestions' to see your AI Analysis.")

    # ==========================================
    # LEARNING MODULE
    # ==========================================
    elif menu == "📚 Learning":
        st.markdown("## 📚 Learning Progress Tracker")
        st.write("Manually track your self-study progress so our AI can focus on generating perfect recommendations.")
        
        if "self_study" not in st.session_state: st.session_state.self_study = 4
        if "focus_topic" not in st.session_state: st.session_state.focus_topic = "Algorithms"
        if "confidence" not in st.session_state: st.session_state.confidence = "Medium"
        if "assignments" not in st.session_state: st.session_state.assignments = 80
        
        with st.form("learning_form"):
            col1, col2 = st.columns(2)
            with col1:
                st.session_state.self_study = st.slider("Daily Self-Study Hours", 0, 15, st.session_state.self_study)
                st.session_state.assignments = st.slider("Assignment Completion (%)", 0, 100, st.session_state.assignments)
            with col2:
                idx = ["Low", "Medium", "High"].index(st.session_state.confidence)
                st.session_state.confidence = st.selectbox("Current Confidence Level", ["Low", "Medium", "High"], index=idx)
                st.session_state.focus_topic = st.text_input("Current Topic of Focus", st.session_state.focus_topic)
                
            submitted = st.form_submit_button("💾 Save Learning Data", use_container_width=True)
            if submitted:
                 st.success("Learning progress saved successfully! Our AI will use this to build your custom recommendations.")

    # ==========================================
    # SUGGESTIONS MODULE
    # ==========================================
    elif menu == "💡 Suggestions":
        st.markdown("## 💡 AI Smart Suggestions")
        st.write("Using your **Learning Progress** and **Test Marks** to synthesize personalized areas for improvement.")
        
        t1 = st.session_state.get("test1", 0)
        t2 = st.session_state.get("test2", 0)
        t3 = st.session_state.get("test3", 0)
        study_hours = st.session_state.get("self_study", 0)
        topic = st.session_state.get("focus_topic", "your current subjects")
        
        if t1 == 0 and t2 == 0 and t3 == 0:
            st.warning("⚠️ No Test Marks detected. Please go to the **📊 Marks** tab and enter your scores so the AI can analyze your trajectory.")
        else:
            avg_marks = (t1 + t2 + t3) / 3
            
            st.markdown(f"### Current Analytics Snapshot")
            col1, col2, col3 = st.columns(3)
            col1.metric("Average Test Score", f"{avg_marks:.1f}%")
            col2.metric("Reported Study Hours", f"{study_hours} hrs/day")
            col3.metric("Key Focus", topic)
            
            st.markdown("---")
            st.markdown("### 🤖 Area of Improvement Analysis")
            
            st.markdown("🧠 **AI-Generated Weakness Identification:**")
            if t3 < t2 and t2 < t1:
                st.error(f"📉 **Declining Trend Detected:** Your test scores are falling from {t1}% to {t3}%. You need to immediately review your foundational concepts, especially in your focus area: **{topic}**.")
            elif avg_marks < 50:
                st.warning(f"🔴 **Critical Performance Alert:** Your average is {avg_marks:.1f}%. You are putting in {study_hours} daily hours, which suggests inefficient learning. Consider shifting to active recall rather than passive reading to improve.")
            elif avg_marks >= 85:
                st.success(f"🌟 **Exceptional Trajectory:** Elite average maintained ({avg_marks:.1f}%). Your strategy is working perfectly. Next step: start teaching peers or taking advanced mock tests in **{topic}** to achieve perfect mastery.")
            else:
                st.info(f"📊 **Stable Growth:** You are in a safe zone. To push your {avg_marks:.1f}% average higher, allocate 30% of your {study_hours} daily study hours strictly toward solving previous exam papers for **{topic}**.")
                
            st.success("💡 **Actionable Suggestion:** To dig deeper into these suggestions, open your **💬 Chat (AI)** tab!")

    # ==========================================
    # EDUCATOR DASHBOARD
    # ==========================================
    elif menu == "👩‍🏫 Educator Dashboard":
        st.markdown("## 👩‍🏫 Educator Dashboard")

        st.markdown("""
        This section can be used to present:
        - High-risk student monitoring
        - Attendance analysis
        - Semester performance comparisons
        - Class-level insights
        """)

        # Demo visuals
        risk_df = pd.DataFrame({
            "Risk Level": ["Low Risk", "Medium Risk", "High Risk"],
            "Students": [45, 25, 10]
        })

        fig1 = px.pie(risk_df, names="Risk Level", values="Students", title="Class Risk Distribution")
        st.plotly_chart(fig1, use_container_width=True)

        perf_df = pd.DataFrame({
            "Semester": ["Sem1", "Sem2", "Sem3", "Sem4"],
            "Average Marks": [62, 67, 71, 75]
        })

        fig2 = px.bar(perf_df, x="Semester", y="Average Marks", color="Average Marks", title="Average Class Semester Performance")
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("### 📋 Sample High Risk Students")
        sample_students = pd.DataFrame({
            "RollNo": [101, 102, 103],
            "Attendance": [52, 61, 48],
            "Predicted Performance": [42, 51, 38],
            "Risk Level": ["High Risk", "Medium Risk", "High Risk"]
        })

        st.dataframe(sample_students, use_container_width=True)

    # ==========================================
    # STUDENT INTERVENTION (EDUCATOR TOOL)
    # ==========================================
    elif menu == "🔍 Student Intervention":
        st.markdown("## 🔍 1-on-1 Student Intervention")
        st.write("Lookup an individual student's real-time academic profile to schedule personalized tutoring sessions.")
        
        search_usn = st.text_input("Enter Student USN / Roll No.", "STU1000")
        
        if st.button("Fetch Student Profile", use_container_width=True):
            try:
                df = pd.read_excel("student_performance_enhanced.xlsx")
                student_match = df[df["RollNo"] == search_usn]
                
                if not student_match.empty:
                    student_data = student_match.iloc[0]
                    st.success(f"✅ Target Located: **{search_usn}**")
                    
                    st.markdown("---")
                    col1, col2 = st.columns(2)
                    col1.metric("Overall Attendance", f"{student_data['Attendance']}%")
                    col2.metric("Total Score Average", f"{student_data.get('Average', student_data.get('Total_Marks', 0)/4):.1f}%")
                    
                    st.markdown("### ⚠️ Discovered Weaknesses")
                    issues = 0
                    if student_data['Attendance'] < 75:
                        st.error("- Critically low attendance. Mandatory counseling required.")
                        issues += 1
                    if student_data['AssignmentCompletion'] < 60:
                        st.warning("- High rate of missing assignments. Intervention on time-management needed.")
                        issues += 1
                    if student_data.get('Average', 100) < 50:
                        st.error("- Academic average below threshold. Intensive subject tutoring required.")
                        issues += 1
                        
                    if issues == 0:
                        st.success("Student is in generally good standing. No critical interventions required.")
                        
                    st.markdown("---")
                    st.markdown("### 📅 Schedule Tutoring Intervention")
                    with st.form("tutoring_form"):
                        col_date, col_time = st.columns(2)
                        with col_date:
                            tutoring_date = st.date_input("Tutoring Date")
                        with col_time:
                            tutoring_time = st.time_input("Tutoring Time")
                            
                        tutoring_focus = st.selectbox("Focus Area", ["Mathematics", "Programming", "Assignments", "Counseling"])
                        tutoring_notes = st.text_area("Educator Notes")
                        
                        if st.form_submit_button("Confirm & Send Tutoring Invite", use_container_width=True):
                            st.info(f"✅ Invitation successfully dispatched to {search_usn}'s student dashboard!")
                else:
                    st.error("❌ Student not found in academic database. Please verify the USN.")
            except Exception as e:
                st.error(f"Database connection error: {e}")

    # ==========================================
    # PREDICT NEW STUDENT
    # ==========================================
    elif menu == "🧠 Predict New Student":
        st.markdown("## 🧠 Predict New Student")

        st.write("Quick prediction tool for trying out a new student profile.")

        col1, col2 = st.columns(2)

        with col1:
            study = st.slider("📚 Study Hours", 0, 20, 5, key="p1")
            attend = st.slider("🏫 Attendance", 0, 100, 70, key="p2")
            resources = st.slider("📖 Resources", 0, 10, 5, key="p3")
            extra = st.slider("🎭 Extracurricular", 0, 10, 2, key="p4")
            motivation = st.slider("🔥 Motivation", 0, 10, 5, key="p5")
            internet = st.slider("🌐 Internet Access", 0, 1, 1, key="p6")
            gender = st.slider("🧑 Gender (0/1)", 0, 1, 0, key="p7")
            age = st.slider("🎂 Age", 15, 30, 20, key="p8")
            learning = st.slider("🧠 Learning Style", 0, 3, 1, key="p9")
            online = st.slider("💻 Online Courses", 0, 10, 2, key="p10")

        with col2:
            discussions = st.slider("🗣 Discussions", 0, 10, 3, key="p11")
            assignment = st.slider("📝 Assignment Completion", 0, 100, 60, key="p12")
            edutech = st.slider("📱 EduTech Usage", 0, 10, 5, key="p13")
            stress = st.slider("😵 Stress Level", 1, 5, 3, key="p14")
            sem1 = st.slider("📊 Sem1 Marks", 0, 100, 60, key="p15")
            sem2 = st.slider("📊 Sem2 Marks", 0, 100, 65, key="p16")
            sem3 = st.slider("📊 Sem3 Marks", 0, 100, 70, key="p17")
            sem4 = st.slider("📊 Sem4 Marks", 0, 100, 75, key="p18")
            exam = st.slider("🧾 Exam Score", 0, 100, 68, key="p19")

        payload = {
            "StudyHours": study,
            "Attendance": attend,
            "Resources": resources,
            "Extracurricular": extra,
            "Motivation": motivation,
            "Internet": internet,
            "Gender": gender,
            "Age": age,
            "LearningStyle": learning,
            "OnlineCourses": online,
            "Discussions": discussions,
            "AssignmentCompletion": assignment,
            "EduTech": edutech,
            "StressLevel": stress,
            "Sem1_Marks": sem1,
            "Sem2_Marks": sem2,
            "Sem3_Marks": sem3,
            "Sem4_Marks": sem4,
            "ExamScore": exam
        }

        if st.button("🚀 Predict Now", use_container_width=True):
            try:
                perf = requests.post(f"{API_URL}/predict-performance", json=payload).json()
                risk = requests.post(f"{API_URL}/predict-risk", json=payload).json()

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("📈 Predicted Performance", perf.get("predicted_performance", "N/A"))
                with col2:
                    st.metric("🚨 Risk Level", risk.get("risk_level", "N/A"))

                st.markdown("### ⚠ Weak Areas")
                for item in risk.get("weak_areas", []):
                    st.warning(item)

                st.markdown("### 🧠 Analysis")
                for item in risk.get("analysis", []):
                    st.info(item)

                st.markdown("### ✅ Recommendations")
                for item in risk.get("recommendations", []):
                    st.success(item)

            except Exception as e:
                st.error(f"❌ Error connecting to backend: {e}")



    # ==========================================
    # AGNIVEDA AI (GROQ-POWERED CHATBOT)
    # ==========================================
    elif menu == "🔥 AgniVeda AI":
        st.markdown("## 🔥 AgniVeda AI")
        st.write("I am **AgniVeda AI** powered by **Groq** — your real-time academic companion! Ask me anything related to **study tips, motivation, performance improvement**, or **academic support**.")
        
        # Display chat messages from history on app rerun
        for message in st.session_state.groq_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Accept user input
        if prompt := st.chat_input("Ask for study tips, motivation, or academic support..."):
            st.session_state.groq_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("🤖 Thinking..."):
                    try:
                        payload = {"message": prompt}
                        response = requests.post(f"{API_URL}/chatbot", json=payload, timeout=15.0)
                        
                        if response.status_code == 200:
                            data = response.json()
                            if "error" in data:
                                reply = f"❌ API Error: {data['error']}"
                            else:
                                reply = data.get("reply", "No response generated.")
                        else:
                            reply = f"❌ Server Error {response.status_code}: {response.text}"
                    except Exception as e:
                        reply = f"❌ Connection Error: {str(e)}\n\nIs the FastAPI backend definitely running?"
                        
                st.markdown(reply)
                st.session_state.groq_messages.append({"role": "assistant", "content": reply})

    # ==========================================
    # EXPLORE & LEARN
    # ==========================================
    elif menu == "📚 Explore & Learn":
        st.markdown("## 📚 Explore & Learn")
        st.markdown('<div class="subtitle">Discover curated educational resources and smart recommendations</div>', unsafe_allow_html=True)

        # --------------------------------------------------
        # Section 1: Platforms
        # --------------------------------------------------
        st.markdown('<div class="small-title">🌐 Top Learning Platforms</div>', unsafe_allow_html=True)
        
        plat1, plat2, plat3 = st.columns(3)
        with plat1:
            st.markdown('''
            <div class="card" style="text-align: center;">
                <h3 style="color:#00f2fe; margin-bottom: 5px;">📘 Coursera</h3>
                <p style="color:#d1d5db; font-size: 14px; height: 60px;">University-level courses, certificates, and degrees.</p>
                <a href="https://www.coursera.org/" target="_blank">
                    <button style="background-color: #00f2fe; color: black; border: none; padding: 10px 20px; border-radius: 8px; font-weight: bold; cursor: pointer; width: 100%;">Open Coursera</button>
                </a>
            </div>
            ''', unsafe_allow_html=True)
            
        with plat2:
            st.markdown('''
            <div class="card" style="text-align: center;">
                <h3 style="color:#10b981; margin-bottom: 5px;">🎓 MIT OCW</h3>
                <p style="color:#d1d5db; font-size: 14px; height: 60px;">Free lecture notes, exams, and videos from MIT.</p>
                <a href="https://ocw.mit.edu/" target="_blank">
                    <button style="background-color: #10b981; color: black; border: none; padding: 10px 20px; border-radius: 8px; font-weight: bold; cursor: pointer; width: 100%;">Open MIT OCW</button>
                </a>
            </div>
            ''', unsafe_allow_html=True)
            
        with plat3:
            st.markdown('''
            <div class="card" style="text-align: center;">
                <h3 style="color:#f59e0b; margin-bottom: 5px;">💻 edX</h3>
                <p style="color:#d1d5db; font-size: 14px; height: 60px;">Top courses from Harvard, MIT, and more.</p>
                <a href="https://www.edx.org/" target="_blank">
                    <button style="background-color: #f59e0b; color: black; border: none; padding: 10px 20px; border-radius: 8px; font-weight: bold; cursor: pointer; width: 100%;">Open edX</button>
                </a>
            </div>
            ''', unsafe_allow_html=True)
            
        # --------------------------------------------------
        # Section 3: Smart Recommendations (IMPORTANT)
        # --------------------------------------------------
        st.markdown("---")
        st.markdown('<div class="small-title">🧠 Smart AI Recommendations</div>', unsafe_allow_html=True)
        st.write("Based on your latest performance analytics and weak areas.")
        
        # Try to pull actual user state if student, else simulate
        att = 100
        stress = 1
        study = 10
        if st.session_state.role == "Student":
            try:
                df = pd.read_excel("student_performance_enhanced.xlsx")
                student_df = df[df["RollNo"] == st.session_state.roll_no]
                if not student_df.empty:
                    att = student_df.iloc[0]["Attendance"]
                    study = st.session_state.get("self_study", student_df.iloc[0]["StudyHours"])
                else:
                    att = 64
                    study = 4
                stress = 3 
            except:
                att = 64
                study = 4
                stress = 4
                
        if att < 75:
            st.warning("⚠️ **Weak Area Detected: Low Attendance**")
            st.markdown("""
            **Recommended Course:** *Time Management for Professionals*
            - **Platform:** Coursera
            - **Goal:** Learn how to balance academic schedules effectively.
            - [Visit Course](https://www.coursera.org/learn/work-smarter-not-harder)
            """)
            
        if study < 10:
            st.error("📉 **Weak Area Detected: Low Study Consistency**")
            st.markdown("""
            **Recommended Course:** *Learning How to Learn*
            - **Platform:** Coursera
            - **Goal:** Master powerful mental tools to help you master tough subjects.
            - [Visit Course](https://www.coursera.org/learn/learning-how-to-learn)
            """)
            
        if stress >= 3:
            st.info("😵 **Weak Area Detected: High Stress Signals**")
            st.markdown("""
            **Recommended Course:** *The Science of Well-Being*
            - **Platform:** Yale / Coursera
            - **Goal:** Engage in challenges to increase happiness and build productive habits.
            - [Visit Course](https://www.coursera.org/learn/the-science-of-well-being)
            """)
            
        if att >= 75 and study >= 10 and stress < 3:
            st.success("🌟 **Strong Profile Detected!** Keep up the great work.")
            st.markdown("""
            **Recommended Course:** *Advanced Python Programming*
            - **Platform:** edX
            - **Goal:** Push your boundaries by learning advanced concepts.
            - [Visit Course](https://www.edx.org)
            """)

        # --------------------------------------------------
        # Section 2: Recommended Courses
        # --------------------------------------------------
        st.markdown("---")
        st.markdown('<div class="small-title">🔥 Trending Courses</div>', unsafe_allow_html=True)
        
        rc1, rc2 = st.columns(2)
        with rc1:
            st.markdown("""
            <div class="card" style="padding: 15px;">
                <h4 style="margin: 0; color: #00f2fe;">Data Science Basics</h4>
                <p style="color: #d1d5db; font-size: 14px; margin-top: 5px;">Platform: IBM / Coursera</p>
                <a href="https://www.coursera.org/" target="_blank" style="color: #10b981; font-weight: bold; text-decoration: none;">▶ Visit Course</a>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("""
            <div class="card" style="padding: 15px;">
                <h4 style="margin: 0; color: #00f2fe;">Machine Learning Foundations</h4>
                <p style="color: #d1d5db; font-size: 14px; margin-top: 5px;">Platform: Stanford / Coursera</p>
                <a href="https://www.coursera.org/" target="_blank" style="color: #10b981; font-weight: bold; text-decoration: none;">▶ Visit Course</a>
            </div>
            """, unsafe_allow_html=True)
            
        with rc2:
            st.markdown("""
            <div class="card" style="padding: 15px;">
                <h4 style="margin: 0; color: #00f2fe;">Python for Everybody</h4>
                <p style="color: #d1d5db; font-size: 14px; margin-top: 5px;">Platform: Univ. of Michigan / Coursera</p>
                <a href="https://www.coursera.org/" target="_blank" style="color: #10b981; font-weight: bold; text-decoration: none;">▶ Visit Course</a>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("""
            <div class="card" style="padding: 15px;">
                <h4 style="margin: 0; color: #00f2fe;">CS50: Intro to Computer Science</h4>
                <p style="color: #d1d5db; font-size: 14px; margin-top: 5px;">Platform: HarvardX / edX</p>
                <a href="https://www.edx.org/cs50" target="_blank" style="color: #10b981; font-weight: bold; text-decoration: none;">▶ Visit Course</a>
            </div>
            """, unsafe_allow_html=True)

        # --------------------------------------------------
        # Section 4: Embedded Learning (YouTube)
        # --------------------------------------------------
        st.markdown("---")
        st.markdown('<div class="small-title">▶ Embedded Micro-Learning</div>', unsafe_allow_html=True)
        st.write("Watch quick study tips right here on your dashboard!")
        
        vid1, vid2 = st.columns(2)
        with vid1:
            st.video("https://www.youtube.com/watch?v=p60rN9JEapg") 
            st.caption("Study Less Study Smart - Effective Techniques")
        with vid2:
            st.video("https://www.youtube.com/watch?v=vd2dtkMINIw") 
            st.caption("How to study for exams - Evidence-based tricks")