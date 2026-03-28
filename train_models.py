# ==========================================
# 📌 FINAL COMBINED ML PIPELINE
# Person 1 + Person 2
# ==========================================

# ==========================================
# 📌 1. IMPORT LIBRARIES
# ==========================================
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix,
    mean_absolute_error, mean_squared_error, r2_score
)

# ==========================================
# 📌 2. LOAD DATASET
# ==========================================
df = pd.read_excel("student_performance_enhanced.xlsx")

print("✅ Dataset Loaded Successfully!")
print("Shape:", df.shape)
print(df.head())

# ==========================================
# 📌 3. CLEAN DATA
# ==========================================
df = df.dropna()

# ==========================================
# ==========================================
# 👤 PERSON 1 — PERFORMANCE PREDICTION MODEL
# ==========================================
# ==========================================

print("\n" + "="*50)
print("🚀 TRAINING PERSON 1 MODEL (Performance Prediction)")
print("="*50)

# ==========================================
# 📌 4. REMOVE LEAKAGE COLUMNS
# ==========================================
columns_to_drop = [
    "RollNo", "Average", "Grade", "Pass_Fail",
    "Sem1_Marks", "Sem2_Marks", "Sem3_Marks", "Sem4_Marks",
    "Total_Marks", "FinalGrade", "ExamScore"
]

columns_to_drop = [col for col in columns_to_drop if col in df.columns]

X1 = df.drop(columns=columns_to_drop)
y1 = df["Average"]

# Convert categorical → numeric
X1 = pd.get_dummies(X1)

print("\n✅ PERSON 1 FEATURES AFTER ENCODING:")
print(X1.head())

# ==========================================
# 📌 5. SAVE COLUMN ORDER
# ==========================================
# IMPORTANT: This fixes your column.pkl issue
joblib.dump(X1.columns.tolist(), "column.pkl")

# ==========================================
# 📌 6. SPLIT DATA
# ==========================================
X1_train, X1_test, y1_train, y1_test = train_test_split(
    X1, y1, test_size=0.2, random_state=42
)

# ==========================================
# 📌 7. TRAIN MODEL
# ==========================================
performance_model = RandomForestRegressor(
    n_estimators=200,
    max_depth=10,
    random_state=42
)

performance_model.fit(X1_train, y1_train)

# ==========================================
# 📌 8. PREDICT
# ==========================================
y1_pred = performance_model.predict(X1_test)

# ==========================================
# 📌 9. EVALUATE MODEL
# ==========================================
mae = mean_absolute_error(y1_test, y1_pred)
rmse = np.sqrt(mean_squared_error(y1_test, y1_pred))
r2 = r2_score(y1_test, y1_pred)

print("\n📊 PERSON 1 MODEL PERFORMANCE")
print("="*40)
print(f"MAE (Average Error): {mae:.2f}")
print(f"RMSE (Root Error): {rmse:.2f}")
print(f"R2 Score: {r2:.3f}")
print("="*40)

# ==========================================
# 📌 10. SAVE PERSON 1 MODEL
# ==========================================
joblib.dump(performance_model, "performance_model.pkl")
print("✅ performance_model.pkl saved!")
print("✅ column.pkl saved!")

# ==========================================
# 📌 11. GRAPH — PERSON 1 FEATURE IMPORTANCE
# ==========================================
importances1 = performance_model.feature_importances_
features1 = X1.columns

indices1 = np.argsort(importances1)

plt.figure(figsize=(10,6))
plt.barh(features1[indices1], importances1[indices1], color="skyblue")
plt.title("Feature Importance - Performance Prediction")
plt.xlabel("Importance")
plt.tight_layout()
plt.show()

# ==========================================
# ==========================================
# 👤 PERSON 2 — RISK PREDICTION MODEL
# ==========================================
# ==========================================

print("\n" + "="*50)
print("🚀 TRAINING PERSON 2 MODEL (Risk Prediction)")
print("="*50)

# ==========================================
# 📌 12. CREATE RISK LEVEL
# ==========================================
def risk_level(avg):
    if avg >= 75:
        return "Low Risk"
    elif avg >= 50:
        return "Medium Risk"
    else:
        return "High Risk"

df["Risk_Level"] = df["Average"].apply(risk_level)

# ==========================================
# 📌 13. FILTER DATA FOR PERSON 2
# ==========================================
person2_df = df[[
    "RollNo",
    "StudyHours",
    "Attendance",
    "Resources",
    "Extracurricular",
    "Motivation",
    "Internet",
    "Gender",
    "Age",
    "LearningStyle",
    "OnlineCourses",
    "Discussions",
    "AssignmentCompletion",
    "EduTech",
    "StressLevel",
    "Sem1_Marks",
    "Sem2_Marks",
    "Sem3_Marks",
    "Sem4_Marks",
    "ExamScore",
    "Average",
    "Risk_Level"
]].copy()

print("\n✅ Filtered Dataset Ready for Person 2!")
print(person2_df.head())

# ==========================================
# 📌 14. SELECT FEATURES & TARGET
# ==========================================
X2 = person2_df.drop(columns=["RollNo", "Average", "Risk_Level"])
y2 = person2_df["Risk_Level"]

# ==========================================
# 📌 15. ENCODE CATEGORICAL DATA
# ==========================================
label_encoders = {}

for col in X2.columns:
    if X2[col].dtype == "object":
        le = LabelEncoder()
        X2[col] = le.fit_transform(X2[col].astype(str))
        label_encoders[col] = le

# Encode target
target_encoder = LabelEncoder()
y2 = target_encoder.fit_transform(y2)

print("\n✅ Person 2 Encoding Done!")

# ==========================================
# 📌 16. TRAIN TEST SPLIT
# ==========================================
X2_train, X2_test, y2_train, y2_test = train_test_split(
    X2, y2, test_size=0.2, random_state=42, stratify=y2
)

print("\n✅ Person 2 Train-Test Split Done!")
print("Train Shape:", X2_train.shape)
print("Test Shape:", X2_test.shape)

# ==========================================
# 📌 17. TRAIN RISK MODEL
# ==========================================
risk_model = RandomForestClassifier(
    n_estimators=300,
    max_depth=12,
    min_samples_split=5,
    min_samples_leaf=2,
    class_weight="balanced",
    random_state=42
)

risk_model.fit(X2_train, y2_train)

print("\n✅ Risk Model Trained Successfully!")

# ==========================================
# 📌 18. EVALUATE MODEL
# ==========================================
y2_pred = risk_model.predict(X2_test)

print("\n🎯 PERSON 2 MODEL PERFORMANCE")
print("Accuracy:", accuracy_score(y2_test, y2_pred))
print("\nClassification Report:\n", classification_report(y2_test, y2_pred))
print("\nConfusion Matrix:\n", confusion_matrix(y2_test, y2_pred))

# ==========================================
# 📌 19. SAVE PERSON 2 MODEL & ENCODERS
# ==========================================
joblib.dump(risk_model, "risk_model.pkl")
joblib.dump(label_encoders, "risk_label_encoders.pkl")
joblib.dump(target_encoder, "risk_target_encoder.pkl")

print("\n✅ risk_model.pkl saved!")
print("✅ risk_label_encoders.pkl saved!")
print("✅ risk_target_encoder.pkl saved!")

# ==========================================
# 📌 20. GRAPH — RISK LEVEL DISTRIBUTION
# ==========================================
plt.figure(figsize=(6,4))
sns.countplot(x=person2_df["Risk_Level"], palette="Set2")
plt.title("Risk Level Distribution")
plt.xlabel("Risk Level")
plt.ylabel("Number of Students")
plt.tight_layout()
plt.show()

# ==========================================
# 📌 21. GRAPH — CONFUSION MATRIX
# ==========================================
cm = confusion_matrix(y2_test, y2_pred)

plt.figure(figsize=(6,4))
sns.heatmap(
    cm, annot=True, fmt='d', cmap="Blues",
    xticklabels=target_encoder.classes_,
    yticklabels=target_encoder.classes_
)
plt.title("Confusion Matrix")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.tight_layout()
plt.show()

# ==========================================
# 📌 22. GRAPH — FEATURE IMPORTANCE
# ==========================================
importances2 = pd.Series(risk_model.feature_importances_, index=X2.columns)
importances2 = importances2.sort_values(ascending=False)

plt.figure(figsize=(10,6))
sns.barplot(x=importances2.values, y=importances2.index, palette="viridis")
plt.title("Feature Importance for Risk Prediction")
plt.xlabel("Importance Score")
plt.ylabel("Features")
plt.tight_layout()
plt.show()

# ==========================================
# 📌 23. RECOMMENDATION ENGINE
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

# ==========================================
# 📌 24. WEAK AREA DETECTION
# ==========================================
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

# ==========================================
# 📌 25. ANALYSIS FUNCTION
# ==========================================
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
# 📌 26. TEST WITH SAMPLE STUDENT
# ==========================================
sample_index = 0
sample_student = X2.iloc[sample_index].to_dict()

sample_array = np.array([list(sample_student.values())])
predicted_class = risk_model.predict(sample_array)[0]
risk_label_pred = target_encoder.inverse_transform([predicted_class])[0]

recommendations = generate_recommendations(sample_student)
weak_areas = detect_weak_areas(sample_student)
analysis = analyze_student(sample_student)

print("\n🎯 SAMPLE STUDENT OUTPUT")
print("Student RollNo:", person2_df.iloc[sample_index]["RollNo"])
print("Risk Level:", risk_label_pred)
print("Weak Areas:", weak_areas)
print("Analysis:", analysis)
print("Recommendations:", recommendations)

# ==========================================
# 📌 27. GRAPH — STUDENT SEMESTER TREND
# ==========================================
semester_scores = [
    person2_df.iloc[sample_index]["Sem1_Marks"],
    person2_df.iloc[sample_index]["Sem2_Marks"],
    person2_df.iloc[sample_index]["Sem3_Marks"],
    person2_df.iloc[sample_index]["Sem4_Marks"]
]

semesters = ["Sem1", "Sem2", "Sem3", "Sem4"]

plt.figure(figsize=(8,4))
plt.plot(semesters, semester_scores, marker='o', linestyle='-', color='purple')
plt.title(f"Semester Performance Trend for Student {person2_df.iloc[sample_index]['RollNo']}")
plt.xlabel("Semester")
plt.ylabel("Marks")
plt.ylim(0, 100)
plt.grid(True)
plt.tight_layout()
plt.show()

# ==========================================
# 📌 28. GRAPH — STUDENT FACTOR ANALYSIS
# ==========================================
weak_scores = {
    "Attendance": sample_student["Attendance"],
    "StudyHours": sample_student["StudyHours"],
    "Assignments": sample_student["AssignmentCompletion"],
    "Discussions": sample_student["Discussions"],
    "OnlineCourses": sample_student["OnlineCourses"]
}

plt.figure(figsize=(8,4))
sns.barplot(x=list(weak_scores.keys()), y=list(weak_scores.values()), palette="coolwarm")
plt.title("Student Performance Factors")
plt.ylabel("Score / Value")
plt.ylim(0, 100)
plt.tight_layout()
plt.show()

# ==========================================
# 📌 29. FINAL SUCCESS MESSAGE
# ==========================================
print("\n🎉 ALL MODELS TRAINED & SAVED SUCCESSFULLY!")