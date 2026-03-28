from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import joblib
import os
from typing import List
import groq
from dotenv import load_dotenv

# Load from prog.env if it exists
load_dotenv('prog.env')
# ==========================================
# GROQ API CONFIGURATION
# ==========================================
groq_api_key = os.environ.get("GROQ_API_KEY", "PASTE_YOUR_KEY_HERE")
groq_client = None

# ==========================================
# BASE PATH
# ==========================================
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

# ==========================================
# CREATE APP
# ==========================================
app = FastAPI(title="GoCudos API")

# ==========================================
# LOAD MODELS
# ==========================================
performance_model = joblib.load(os.path.join(BASE_PATH, "performance_model.pkl"))
performance_columns = joblib.load(os.path.join(BASE_PATH, "column.pkl"))

risk_model = joblib.load(os.path.join(BASE_PATH, "risk_model.pkl"))
risk_target_encoder = joblib.load(os.path.join(BASE_PATH, "risk_target_encoder.pkl"))

# ==========================================
# INPUT SCHEMA
# ==========================================
class StudentInput(BaseModel):
    StudyHours: float
    Attendance: float
    Resources: float
    Extracurricular: float
    Motivation: float
    Internet: float
    Gender: float
    Age: float
    LearningStyle: float
    OnlineCourses: float
    Discussions: float
    AssignmentCompletion: float
    EduTech: float
    StressLevel: float
    Sem1_Marks: float
    Sem2_Marks: float
    Sem3_Marks: float
    Sem4_Marks: float
    ExamScore: float

class ChatRequest(BaseModel):
    message: str
    
# ==========================================
# HELPER FUNCTIONS
# ==========================================
def generate_recommendations(student):
    rec = []

    if student["Attendance"] < 75:
        rec.append("Improve attendance above 75%")
    if student["StudyHours"] < 10:
        rec.append("Increase study hours regularly")
    if student["AssignmentCompletion"] < 70:
        rec.append("Complete assignments on time")
    if student["StressLevel"] >= 3:
        rec.append("Focus on stress management")
    if student["Discussions"] < 5:
        rec.append("Participate more in discussions")
    if student["OnlineCourses"] < 2:
        rec.append("Take more online courses")

    return rec


def detect_weak_areas(student):
    weak = []

    if student["Attendance"] < 75:
        weak.append("Attendance")
    if student["StudyHours"] < 10:
        weak.append("Study Consistency")
    if student["AssignmentCompletion"] < 70:
        weak.append("Assignment Completion")
    if student["Discussions"] < 5:
        weak.append("Participation")
    if student["StressLevel"] >= 3:
        weak.append("Stress Management")

    return weak


def analyze_student(student):
    analysis = []

    if student["Attendance"] < 75:
        analysis.append("Low attendance is affecting performance.")
    if student["StudyHours"] < 10:
        analysis.append("Study hours are lower than expected.")
    if student["AssignmentCompletion"] < 70:
        analysis.append("Incomplete assignments may reduce academic consistency.")
    if student["Discussions"] < 5:
        analysis.append("Low classroom/discussion participation is observed.")
    if student["StressLevel"] >= 3:
        analysis.append("Higher stress level may be negatively impacting learning.")

    return analysis

# ==========================================
# HOME ROUTE
# ==========================================
@app.get("/")
def home():
    return {"message": "Student Performance Monitoring API is running!"}

# ==========================================
# PERSON 1 — PERFORMANCE PREDICTION
# ==========================================
@app.post("/predict-performance")
def predict_performance(data: StudentInput):
    input_dict = data.dict()
    input_df = pd.DataFrame([input_dict])

    input_df = pd.get_dummies(input_df)

    # Match training columns
    for col in performance_columns:
        if col not in input_df.columns:
            input_df[col] = 0

    input_df = input_df[performance_columns]

    predicted_score = performance_model.predict(input_df)[0]

    return {
        "predicted_performance": round(float(predicted_score), 2)
    }

# ==========================================
# PERSON 2 — RISK PREDICTION
# ==========================================
@app.post("/predict-risk")
def predict_risk(data: StudentInput):
    input_dict = data.dict()
    input_df = pd.DataFrame([input_dict])

    predicted_class = risk_model.predict(input_df)[0]
    risk_label = risk_target_encoder.inverse_transform([predicted_class])[0]

    weak_areas = detect_weak_areas(input_dict)
    recommendations = generate_recommendations(input_dict)
    analysis = analyze_student(input_dict)

    return {
        "risk_level": risk_label,
        "weak_areas": weak_areas,
        "analysis": analysis,
        "recommendations": recommendations
    }

# ==========================================
# FULL REPORT
# ==========================================
@app.post("/student-report")
def student_report(data: StudentInput):
    input_dict = data.dict()
    input_df = pd.DataFrame([input_dict])

    # Person 1
    perf_df = pd.get_dummies(input_df)

    for col in performance_columns:
        if col not in perf_df.columns:
            perf_df[col] = 0

    perf_df = perf_df[performance_columns]
    predicted_score = performance_model.predict(perf_df)[0]

    # Person 2
    predicted_class = risk_model.predict(input_df)[0]
    risk_label = risk_target_encoder.inverse_transform([predicted_class])[0]

    weak_areas = detect_weak_areas(input_dict)
    recommendations = generate_recommendations(input_dict)
    analysis = analyze_student(input_dict)

    return {
        "predicted_performance": round(float(predicted_score), 2),
        "risk_level": risk_label,
        "weak_areas": weak_areas,
        "analysis": analysis,
        "recommendations": recommendations
    }

# ==========================================
# GROQ CHATBOT ROUTE
# ==========================================
@app.post("/chatbot")
def chat_with_ai(data: ChatRequest):
    try:
        if groq_api_key == "PASTE_YOUR_KEY_HERE" or not groq_api_key:
            return {"error": "Groq API key is not configured. Please add it to main.py or prog.env."}
        
        # Create client with a strict timeout to prevent infinite hanging
        client = groq.Groq(
            api_key=groq_api_key,
            timeout=10.0
        )
        
        # Shortened efficient system prompt
        system_msg = {
            "role": "system",
            "content": "You are AgniVeda AI, a fast and intelligent study assistant by GoCudos. Give short, direct, actionable advice on study tips and motivation. Keep replies under 4 sentences."
        }
        
        messages = [system_msg, {"role": "user", "content": data.message}]
        
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama-3.1-8b-instant", 
            temperature=0.7,
            max_tokens=150
        )
        
        return {"reply": chat_completion.choices[0].message.content}
    except Exception as e:
        return {"error": str(e)}
