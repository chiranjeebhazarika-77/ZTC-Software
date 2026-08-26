import streamlit as st
import pandas as pd
import os
import datetime
import pytz
import base64
import requests
import json
import threading
import urllib.parse

# Page Configuration
st.set_page_config(
    page_title="Soft Tech Computers & ZTC Enterprise Portal",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# IST TimeZone Setup
IST = pytz.timezone('Asia/Kolkata')

# -------------------------------------------------------------
# GOOGLE SHEETS LIVE SYNC URL
# -------------------------------------------------------------
GSHEET_WEBAPP_URL = "https://script.google.com/macros/s/AKfycbyeLkWRqD_gHSIQzFBUEJ2kv1e6DpbaUkBB9_CV5l_95k8kg-tSyBnCC50W1TN0XwES/exec"

STUDENT_MASTER_FILE = "students_db.csv"
FEE_LOG_FILE = "fees_db.csv"
ATTENDANCE_FILE = "attendance_db.csv"
TEACHERS_FILE = "teachers_db.csv"
TEACHER_ATT_FILE = "teacher_attendance.csv"
ENQUIRY_FILE = "enquiries_db.csv"
SFPC_FILE = "sfpc_db.csv"
CREDS_FILE = "creds_db.csv"
FEEDBACK_FILE = "feedback_db.csv"
SYLLABUS_LOG_FILE = "syllabus_logs.csv"
MARKS_FILE = "marks_db.csv"
NOTICES_FILE = "notices_db.csv"
TASKS_FILE = "tasks_db.csv"
PC_ALLOC_FILE = "pc_alloc_db.csv"
WEAK_NOTES_FILE = "weak_notes_db.csv"
EXAM_FORMS_FILE = "exam_forms_db.csv"
COURSES_FILE = "courses_db.csv"
DISPATCH_FILE = "dispatch_db.csv"
PHOTO_DIR = "student_photos"

os.makedirs(PHOTO_DIR, exist_ok=True)

# -------------------------------------------------------------
# HIGH-SPEED MEMORY CACHE & ASYNC CLOUD SYNC ENGINE
# -------------------------------------------------------------
def push_to_cloud_async(payload):
    def _worker():
        try:
            requests.post(GSHEET_WEBAPP_URL, data=json.dumps(payload), headers={"Content-Type": "application/json"}, timeout=5, allow_redirects=True)
        except Exception:
            pass
    t = threading.Thread(target=_worker)
    t.daemon = True
    t.start()

def load_data_from_disk(file_path, columns):
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path, dtype=str)
            for col in columns:
                if col not in df.columns: df[col] = ""
            return df
        except Exception:
            pass
    return pd.DataFrame(columns=columns)

def save_data(df, file_path, sheet_name=None, session_key=None):
    if session_key:
        st.session_state[session_key] = df.copy()
    df.to_csv(file_path, index=False)
    if GSHEET_WEBAPP_URL and sheet_name:
        records = [df.columns.tolist()] + df.fillna("").values.tolist()
        payload = {"action": "overwrite", "sheet_name": sheet_name, "rows": records}
        push_to_cloud_async(payload)

@st.cache_data(show_spinner=False)
def get_image_base64(file_name):
    extensions = ['', '.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG']
    for ext in extensions:
        p = f"{file_name}{ext}"
        if os.path.exists(p):
            try:
                with open(p, "rb") as image_file:
                    encoded = base64.b64encode(image_file.read()).decode()
                    is_png = 'png' in p.lower()
                    mime_type = 'image/png' if is_png else 'image/jpeg'
                    return f"data:{mime_type};base64,{encoded}"
            except Exception:
                pass
    return None

def get_student_photo_base64(photo_path):
    if photo_path and os.path.exists(photo_path):
        try:
            with open(photo_path, "rb") as image_file:
                encoded = base64.b64encode(image_file.read()).decode()
                return f"data:image/png;base64,{encoded}"
        except Exception:
            pass
    return "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

# Columns definitions
student_cols = [
    "Sl. No.", "Student ID", "Name", "Father Name", "Mother Name", "Gender", "DOB", "Caste", "Mobile No", 
    "Vill Town", "PO", "PS", "PIN Code", "District", "Full Address", "Course", "Duration", "Days_Batch", 
    "Session", "Join Date", "Validity Date", "Total Fee", "Discount", "Net Fee", "Shift", "Batch Time", 
    "Photo Path", "Status", "HO_Reg_No", "Stage_HO_Reg", "Stage_AdmitCard", "Stage_Exam", 
    "Stage_Cert_Status", "Cert_Serial_No", "Cert_Arrival_Date", "Cert_Handover_Date", "Handover_Status"
]
fee_cols = ["Receipt No", "Student ID", "Date", "Amount Paid", "Payment Mode", "Collected_By", "Remarks"]
attendance_cols = ["Student ID", "Date", "Time_In", "Status", "Late_Reason", "Sign_Mode", "Location_Verified"]
teacher_cols = ["Teacher ID", "Name", "Phone", "Qualification", "Designation", "Shift Assigned"]
teacher_att_cols = ["Date", "Teacher ID", "Name", "Shift", "Time_In", "Time_Out", "Status", "Late_Mins", "Penalty_Deduction", "Net_Earning_Today", "Remarks"]
enquiry_cols = ["Date", "Name", "Mobile", "Course Interested", "Village/Address", "Status"]
sfpc_cols = ["Date", "Student ID", "Student Name", "PC Machine No", "Topic Practiced", "Teacher Incharge"]
creds_cols = ["Role", "Password"]
feedback_cols = ["Date", "Student ID", "Student Name", "Teacher Name", "Theory Written", "Rating_Stars", "Comments"]
syllabus_cols = ["Date", "Course", "Topics Covered", "Class Type", "Teacher Incharge"]
marks_cols = ["Date", "Student ID", "Student Name", "Course/Subject", "Test Topic", "Marks Obtained", "Total Marks", "Teacher Incharge"]
notices_cols = ["Date", "Notice Title", "Notice Content", "Category", "Posted By"]
tasks_cols = ["Date", "Student ID", "Student Name", "Task Assigned", "Status", "Teacher Incharge"]
pc_alloc_cols = ["Date", "Student ID", "Student Name", "PC Machine No", "Shift", "Teacher Incharge"]
weak_notes_cols = ["Date", "Student ID", "Student Name", "Weak Topic / Area", "Teacher Advice", "Teacher Name"]
exam_forms_cols = ["Date", "Student ID", "Student Name", "Course", "Exam Fee Amount", "Payment Status", "Exam Center Code", "Remarks"]
courses_cols = ["Course Name", "Duration", "Fee (₹)", "Description"]
dispatch_cols = ["Date", "Student ID", "Student Name", "Course", "Certificate No", "Marksheet Status", "Received By", "Contact No", "Handover Confirmed"]

# -------------------------------------------------------------
# INITIALIZE IN-MEMORY SESSION STATE DATA (RUNS ONCE = 0-LAG)
# -------------------------------------------------------------
if "data_initialized" not in st.session_state:
    st.session_state["student_df"] = load_data_from_disk(STUDENT_MASTER_FILE, student_cols)
    st.session_state["fee_df"] = load_data_from_disk(FEE_LOG_FILE, fee_cols)
    st.session_state["att_df"] = load_data_from_disk(ATTENDANCE_FILE, attendance_cols)
    st.session_state["teacher_df"] = load_data_from_disk(TEACHERS_FILE, teacher_cols)
    st.session_state["teacher_att_df"] = load_data_from_disk(TEACHER_ATT_FILE, teacher_att_cols)
    st.session_state["enquiry_df"] = load_data_from_disk(ENQUIRY_FILE, enquiry_cols)
    st.session_state["sfpc_df"] = load_data_from_disk(SFPC_FILE, sfpc_cols)
    st.session_state["creds_df"] = load_data_from_disk(CREDS_FILE, creds_cols)
    st.session_state["feedback_df"] = load_data_from_disk(FEEDBACK_FILE, feedback_cols)
    st.session_state["syllabus_df"] = load_data_from_disk(SYLLABUS_LOG_FILE, syllabus_cols)
    st.session_state["marks_df"] = load_data_from_disk(MARKS_FILE, marks_cols)
    st.session_state["notices_df"] = load_data_from_disk(NOTICES_FILE, notices_cols)
    st.session_state["tasks_df"] = load_data_from_disk(TASKS_FILE, tasks_cols)
    st.session_state["pc_alloc_df"] = load_data_from_disk(PC_ALLOC_FILE, pc_alloc_cols)
    st.session_state["weak_notes_df"] = load_data_from_disk(WEAK_NOTES_FILE, weak_notes_cols)
    st.session_state["exam_forms_df"] = load_data_from_disk(EXAM_FORMS_FILE, exam_forms_cols)
    st.session_state["courses_df"] = load_data_from_disk(COURSES_FILE, courses_cols)
    st.session_state["dispatch_df"] = load_data_from_disk(DISPATCH_FILE, dispatch_cols)
    
    # Defaults
    if st.session_state["courses_df"].empty:
        default_courses = [
            {"Course Name": "PGDCA (Post Graduate Diploma in Computer Application)", "Duration": "12 Months", "Fee (₹)": "8500", "Description": "Fundamentals, Office, Tally Prime, Web Design, Python/C"},
            {"Course Name": "ADCA (Advanced Diploma in Computer Application)", "Duration": "12 Months", "Fee (₹)": "7500", "Description": "Office, DTP, Tally Prime, HTML, Python Basics"},
            {"Course Name": "DCA (Diploma in Computer Application)", "Duration": "6 Months", "Fee (₹)": "4500", "Description": "Fundamentals, Office, Access, Tally, Internet"},
            {"Course Name": "DTP (Desktop Publishing)", "Duration": "3 Months", "Fee (₹)": "3500", "Description": "Photoshop, Pagemaker, CorelDraw, Assamese DTP"},
            {"Course Name": "Tally Prime with GST", "Duration": "3 Months", "Fee (₹)": "4000", "Description": "Accounting, GST Billing, Inventory, Payroll"},
            {"Course Name": "Certificate Course in Computer Basics", "Duration": "3 Months", "Fee (₹)": "2500", "Description": "Paint, Notepad, MS Office Basics, Internet"},
            {"Course Name": "Class 9 English Coaching", "Duration": "12 Months", "Fee (₹)": "600", "Description": "Grammar, Literature, Writing Skills (Monthly)"},
            {"Course Name": "Class 10 English Coaching", "Duration": "12 Months", "Fee (₹)": "700", "Description": "Grammar, Literature, Writing Skills (Monthly)"},
            {"Course Name": "Class 11 English Coaching", "Duration": "12 Months", "Fee (₹)": "800", "Description": "Grammar, Literature, Writing Skills (Monthly)"},
            {"Course Name": "Class 12 English Coaching", "Duration": "12 Months", "Fee (₹)": "900", "Description": "Grammar, Literature, Writing Skills (Monthly)"}
        ]
        st.session_state["courses_df"] = pd.DataFrame(default_courses)
        save_data(st.session_state["courses_df"], COURSES_FILE, "courses_db", "courses_df")

    if st.session_state["teacher_df"].empty:
        default_teachers = [
            {"Teacher ID": "TCH-01", "Name": "Chiranjeeb Hazarika", "Phone": "9101026718", "Qualification": "Director / Master Trainer", "Designation": "Director", "Shift Assigned": "All Shifts"},
            {"Teacher ID": "TCH-02", "Name": "Senior Faculty", "Phone": "9876543210", "Qualification": "MCA / PGDCA", "Designation": "Instructor", "Shift Assigned": "Morning, Afternoon, Evening"}
        ]
        st.session_state["teacher_df"] = pd.DataFrame(default_teachers)
        save_data(st.session_state["teacher_df"], TEACHERS_FILE, "teachers_db", "teacher_df")

    if st.session_state["creds_df"].empty:
        st.session_state["creds_df"] = pd.DataFrame([
            {"Role": "Admin", "Password": "zaan123"},
            {"Role": "Teacher", "Password": "teacher123"}
        ])
        save_data(st.session_state["creds_df"], CREDS_FILE, "creds_db", "creds_df")
        
    st.session_state["data_initialized"] = True

# Pointers to Session Data for Zero-Lag Execution
student_df = st.session_state["student_df"]
fee_df = st.session_state["fee_df"]
att_df = st.session_state["att_df"]
teacher_df = st.session_state["teacher_df"]
teacher_att_df = st.session_state["teacher_att_df"]
enquiry_df = st.session_state["enquiry_df"]
sfpc_df = st.session_state["sfpc_df"]
creds_df = st.session_state["creds_df"]
feedback_df = st.session_state["feedback_df"]
syllabus_df = st.session_state["syllabus_df"]
marks_df = st.session_state["marks_df"]
notices_df = st.session_state["notices_df"]
tasks_df = st.session_state["tasks_df"]
pc_alloc_df = st.session_state["pc_alloc_df"]
weak_notes_df = st.session_state["weak_notes_df"]
exam_forms_df = st.session_state["exam_forms_df"]
courses_df = st.session_state["courses_df"]
dispatch_df = st.session_state["dispatch_df"]

ADMIN_PWD = creds_df[creds_df["Role"] == "Admin"]["Password"].values[0] if "Admin" in creds_df["Role"].values else "zaan123"
TEACHER_PWD = creds_df[creds_df["Role"] == "Teacher"]["Password"].values[0] if "Teacher" in creds_df["Role"].values else "teacher123"

ALL_SYLLABUS_TOPICS = [
    "Computer Basics & Hardware", "Windows Operating System", "Paint / Notepad / Wordpad",
    "MS Word (Documentation)", "MS Excel (Formulas & Data)", "MS Powerpoint (Presentations)",
    "MS Access (Database)", "Tally Prime (Company & Accounts)", "Tally Prime (GST & Billing)",
    "Photoshop (Graphic Design)", "Pagemaker (Publications)", "CorelDraw (Vector Art)",
    "Assamese Typesetting (Rodali/Geetanjali)", "HTML / CSS Web Design", "Python Programming",
    "Internet, Email & Cyber Security", "English Grammar & Writing Skills", "Exam & Practical Viva"
]

# -------------------------------------------------------------
# UDISE+ GOVT-STYLE THEME CSS
# -------------------------------------------------------------
st.markdown("""
<style>
.stApp {
    background-color: #F8FAFC;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
.udise-topbar {
    background-color: #1E293B;
    color: white;
    padding: 12px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 3px solid #0284C7;
    margin-top: -60px;
    margin-left: -4rem;
    margin-right: -4rem;
    margin-bottom: 18px;
}
.udise-logo {
    font-size: 20px;
    font-weight: 800;
    letter-spacing: 0.8px;
    color: #38BDF8;
}
.udise-logo span {
    color: #FFFFFF;
    font-weight: 400;
    font-size: 15px;
    margin-left: 10px;
    border-left: 1px solid #64748B;
    padding-left: 10px;
}
.udise-user-badge {
    background: #334155;
    padding: 5px 14px;
    border-radius: 20px;
    font-size: 12px;
    color: #E2E8F0;
    border: 1px solid #475569;
}
.school-info-card {
    background: #FFFFFF;
    border-radius: 8px;
    padding: 14px 20px;
    border: 1px solid #CBD5E1;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    margin-bottom: 20px;
}
.hero-side-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 14px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.03);
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: space-around;
}
.hero-side-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 10px;
    background: #F8FAFC;
    border-radius: 6px;
    border-left: 3px solid #0284C7;
    margin-bottom: 6px;
}
.action-box {
    background: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    padding: 16px;
    display: flex;
    align-items: center;
    gap: 15px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    margin-bottom: 12px;
}
.action-icon {
    background: #0284C7;
    color: white;
    width: 44px;
    height: 44px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 6px;
    font-size: 20px;
}
.support-card {
    background: #0F172A;
    color: white;
    border-radius: 8px;
    padding: 14px 18px;
}
.support-item {
    background: #1E293B;
    padding: 8px 12px;
    border-radius: 6px;
    margin-top: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 13px;
}
.pink-badge {
    background: #FCE7F3;
    color: #BE185D;
    border: 1px solid #F472B6;
    padding: 12px 16px;
    border-radius: 8px;
    font-weight: 600;
    margin-bottom: 12px;
}
.green-badge {
    background: #DCFCE7;
    color: #15803D;
    border: 1.5px solid #22C55E;
    padding: 12px 16px;
    border-radius: 8px;
    font-weight: 600;
    margin-bottom: 12px;
    box-shadow: 0 2px 5px rgba(34, 197, 94, 0.15);
}
.stepper-wrapper {
    display: flex;
    justify-content: space-between;
    margin: 20px 0;
    background: #FFFFFF;
    padding: 16px 20px;
    border-radius: 8px;
    border: 1px solid #E2E8F0;
}
.stepper-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    flex: 1;
}
.step-counter {
    width: 34px;
    height: 34px;
    border-radius: 50%;
    background: #E2E8F0;
    color: #64748B;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    margin-bottom: 6px;
}
.step-counter.active {
    background: #10B981;
    color: white;
}
.step-name {
    font-size: 11px;
    font-weight: 600;
    color: #334155;
}

/* ID CARD CSS */
.id-card-container {
    width: 360px;
    background: #FFFFFF;
    border-radius: 14px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.12);
    overflow: hidden;
    border: 2px solid #0284C7;
    margin: 10px auto;
}
.id-card-header {
    background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
    color: white;
    padding: 14px;
    text-align: center;
    border-bottom: 3px solid #38BDF8;
}
.id-card-body {
    padding: 16px;
    text-align: center;
}
.id-photo {
    width: 95px;
    height: 95px;
    border-radius: 50%;
    object-fit: cover;
    border: 3px solid #0284C7;
    margin-top: -10px;
}
.id-name {
    font-size: 17px;
    font-weight: 800;
    color: #0F172A;
    margin: 8px 0 2px 0;
    text-transform: uppercase;
}
.id-roll-badge {
    background: #E0F2FE;
    color: #0369A1;
    font-weight: 700;
    font-size: 12px;
    padding: 3px 12px;
    border-radius: 12px;
    display: inline-block;
    margin-bottom: 10px;
}
.id-details-table {
    width: 100%;
    font-size: 11.5px;
    text-align: left;
    color: #334155;
    margin-bottom: 12px;
}
.id-details-table td {
    padding: 4px 6px;
}
.id-card-footer {
    background: #F8FAFC;
    padding: 10px 14px;
    border-top: 1px dashed #CBD5E1;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

/* PASSBOOK CSS */
.passbook-card {
    background: #FFFFFF;
    border: 2px solid #334155;
    border-radius: 10px;
    padding: 18px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.06);
    max-width: 750px;
    margin: 10px auto;
}
.passbook-header {
    text-align: center;
    border-bottom: 2px solid #0284C7;
    padding-bottom: 8px;
    margin-bottom: 12px;
}
.passbook-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12.5px;
    margin-top: 12px;
}
.passbook-table th {
    background: #F1F5F9;
    color: #0F172A;
    border: 1px solid #CBD5E1;
    padding: 7px;
    text-align: center;
    font-weight: 700;
}
.passbook-table td {
    border: 1px solid #E2E8F0;
    padding: 7px;
    text-align: center;
    color: #334155;
}

/* Vibrant Green Button Theme */
div.stButton > button {
    background-color: #047857 !important;
    color: white !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    border: none !important;
    transition: all 0.2s ease-in-out !important;
}
div.stButton > button:hover {
    background-color: #059669 !important;
    transform: scale(1.01) !important;
    box-shadow: 0 4px 10px rgba(5, 150, 105, 0.3) !important;
}
div.stButton > button:active {
    background-color: #10B981 !important;
}
</style>
""", unsafe_allow_html=True)

# Top Header Bar
st.markdown("""
<div class="udise-topbar">
<div class="udise-logo">STC-ZTC+ <span>Enterprise Management Portal</span></div>
<div style="display:flex; align-items:center; gap:15px;">
<span style="font-size:12px; color:#94A3B8;">Academic Session: 2026-27</span>
<div class="udise-user-badge">👤 Chiranjeeb Hazarika (DIRECTOR / ADMIN)</div>
</div>
</div>
""", unsafe_allow_html=True)

# Institutional Header Strip
st.markdown("""
<div class="school-info-card">
<div style="display:flex; justify-content:space-between; flex-wrap:wrap; gap:15px;">
<div>
<div style="font-size:12px; color:#64748B;">🏛️ Institution:</div>
<div style="font-size:15px; font-weight:700; color:#0F172A;">SOFT TECH COMPUTERS & ZTC ENTERPRISE</div>
</div>
<div>
<div style="font-size:12px; color:#64748B;">📋 Center Code:</div>
<div style="font-size:15px; font-weight:700; color:#0284C7;">4159 (Kamarchuburi, Sonitpur)</div>
</div>
<div>
<div style="font-size:12px; color:#64748B;">🏷️ Quality Standard:</div>
<div style="font-size:15px; font-weight:700; color:#0F172A;">ISO 9001:2015 Certified Academy</div>
</div>
<div>
<div style="font-size:12px; color:#64748B;">📍 Center Location:</div>
<div style="font-size:15px; font-weight:700; color:#10B981;">Thelamara, Assam - 784149</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# SIDEBAR NAVIGATION
# -------------------------------------------------------------
st.sidebar.title("💻 Portal Navigation")
menu = st.sidebar.radio("Go To Module:", [
    "⚡ Quick Actions & Dashboard",
    "📜 Online Certificate Verification",
    "📝 New Student Admission",
    "🔑 Student Login Portal",
    "🎯 Sunday Free Practice Class (SFPC)",
    "💵 Fee Counter Desk",
    "🔑 Teacher Portal & Attendance",
    "🔐 Admin Control Panel"
])

# -------------------------------------------------------------
# 1. QUICK ACTIONS & PUBLIC DASHBOARD
# -------------------------------------------------------------
if menu == "⚡ Quick Actions & Dashboard":
    dp2_b64 = get_image_base64("dp2")
    col_h_left, col_h_mid, col_h_right = st.columns([1, 1.8, 1])
    
    with col_h_left:
        st.markdown("""
<div class="hero-side-card">
<div style="font-size:13px; font-weight:bold; color:#0F172A; margin-bottom:6px; border-bottom:1px solid #E2E8F0; padding-bottom:4px;">🏆 Institutional Standards</div>
<div class="hero-side-item">
<span style="font-size:18px;">🏛️</span>
<div><b style="font-size:12px; color:#0F172A;">ISO 9001:2015</b><br><span style="font-size:11px; color:#64748B;">Certified IT Academy</span></div>
</div>
<div class="hero-side-item">
<span style="font-size:18px;">🎯</span>
<div><b style="font-size:12px; color:#0F172A;">Digital India Skill</b><br><span style="font-size:11px; color:#64748B;">Quality Technical Training</span></div>
</div>
<div class="hero-side-item">
<span style="font-size:18px;">💻</span>
<div><b style="font-size:12px; color:#0F172A;">100% Practical Lab</b><br><span style="font-size:11px; color:#64748B;">Dedicated Computer PCs</span></div>
</div>
</div>
""", unsafe_allow_html=True)
        
    with col_h_mid:
        if dp2_b64:
            st.markdown(f'<img src="{dp2_b64}" style="width:100%; max-height:220px; object-fit:contain; border-radius:10px; border:1px solid #CBD5E1; box-shadow: 0 4px 10px rgba(0,0,0,0.05);">', unsafe_allow_html=True)
        else:
            st.markdown("""
<div style="background:#0F172A; color:white; padding:30px; border-radius:10px; text-align:center;">
<h3 style="margin:0; color:#38BDF8;">SOFT TECH COMPUTERS & ZTC</h3>
<p style="margin:6px 0 0 0; color:#94A3B8;">Kamarchuburi, Thelamara, Sonitpur, Assam - 784149</p>
</div>
""", unsafe_allow_html=True)
            
    with col_h_right:
        st.markdown("""
<div class="hero-side-card">
<div style="font-size:13px; font-weight:bold; color:#0F172A; margin-bottom:6px; border-bottom:1px solid #E2E8F0; padding-bottom:4px;">📜 Recognition & Certs</div>
<div class="hero-side-item" style="border-left-color:#10B981;">
<span style="font-size:18px;">📋</span>
<div><b style="font-size:12px; color:#0F172A;">Center Code: 4159</b><br><span style="font-size:11px; color:#64748B;">Govt Regd Accreditation</span></div>
</div>
<div class="hero-side-item" style="border-left-color:#10B981;">
<span style="font-size:18px;">📜</span>
<div><b style="font-size:12px; color:#0F172A;">Sarva India Certs</b><br><span style="font-size:11px; color:#64748B;">Valid Across India</span></div>
</div>
<div class="hero-side-item" style="border-left-color:#10B981;">
<span style="font-size:18px;">🌐</span>
<div><b style="font-size:12px; color:#0F172A;">Online Verification</b><br><span style="font-size:11px; color:#64748B;">Instant Roll ID Check</span></div>
</div>
</div>
""", unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1:
        st.metric("Institutional Certification", "ISO 9001:2015")
    with col_s2:
        st.metric("Authorized Center Code", "4159 (Assam)")
    with col_s3:
        st.metric("Alumni Network", "350+ Graduates")
    with col_s4:
        st.metric("Govt Approved Courses", f"{len(courses_df)} Programs")
        
    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_r = st.columns([2, 1])
    
    with col_l:
        st.markdown("""
<div class="action-box">
<div class="action-icon">📝</div>
<div>
<b style="font-size:15px; color:#0F172A;">Online Student Admission & Course Fee Enquiry Desk</b>
<div style="font-size:12px; color:#64748B;">Submit your query to check official course duration and fee structure</div>
</div>
</div>
""", unsafe_allow_html=True)
        
        with st.expander("📝 Click here to Submit Public Admission / Course Fee Enquiry", expanded=True):
            with st.form("public_enquiry_form", clear_on_submit=True):
                e_name = st.text_input("Candidate Full Name*")
                e_mobile = st.text_input("Mobile Number (WhatsApp Enabled)*")
                e_vill = st.text_input("Village / Town / Address*")
                
                course_list = courses_df["Course Name"].tolist() if not courses_df.empty else []
                e_course = st.selectbox("Select Interested Course:*", course_list)
                
                if st.form_submit_button("🟢 Submit Enquiry & Check Course Fee"):
                    if not e_name or not e_mobile:
                        st.error("Please enter Name and Mobile Number!")
                    else:
                        c_match = courses_df[courses_df["Course Name"] == e_course]
                        c_fee = c_match["Fee (₹)"].values[0] if not c_match.empty else "N/A"
                        c_dur = c_match["Duration"].values[0] if not c_match.empty else "N/A"
                        
                        enq_row = {
                            "Date": str(datetime.date.today()),
                            "Name": e_name.upper(),
                            "Mobile": e_mobile,
                            "Course Interested": e_course,
                            "Village/Address": e_vill.upper(),
                            "Status": "New Lead"
                        }
                        st.session_state["enquiry_df"] = pd.concat([st.session_state["enquiry_df"], pd.DataFrame([enq_row])], ignore_index=True)
                        save_data(st.session_state["enquiry_df"], ENQUIRY_FILE, "enquiries_db", "enquiry_df")
                        
                        st.markdown(f"""
<div class="green-badge">
🎉 <b>Enquiry Submitted Successfully!</b><br>
<b>Selected Course:</b> {e_course}<br>
<b>Duration:</b> {c_dur} | <b>Official Total Course Fee:</b> ₹{c_fee}<br>
<i>Our academy office will contact you on {e_mobile} shortly!</i>
</div>
""", unsafe_allow_html=True)

    with col_r:
        st.markdown("""
<div class="support-card">
<div style="font-size:14px; font-weight:700; color:#38BDF8; display:flex; align-items:center; gap:8px;">📞 Center Support & Helplines</div>
<div class="support-item">
<div><b>Director / Head MIS</b><br><span style="color:#94A3B8; font-size:11px;">Chiranjeeb Hazarika</span></div>
<div style="color:#38BDF8; font-weight:bold;">9101026718</div>
</div>
<div class="support-item">
<div><b>Helpdesk / Center Location</b><br><span style="color:#94A3B8; font-size:11px;">Kamarchuburi, Sonitpur</span></div>
<div style="color:#10B981; font-weight:bold;">PIN: 784149</div>
</div>
</div>
""", unsafe_allow_html=True)
        
    st.markdown("---")
    
    st.subheader("🔒 Master Student Directory (Authorized Staff Access Only)")
    with st.expander("🔑 Click to Unlock Master Database (Password Required)", expanded=False):
        view_pwd = st.text_input("Enter Staff / Director Password:", type="password", key="dash_view_pwd")
        if view_pwd in [ADMIN_PWD, TEACHER_PWD]:
            st.success("Access Granted! Showing Master Database:")
            if not student_df.empty:
                st.dataframe(student_df, use_container_width=True)
            else:
                st.info("No records found in database.")
        elif view_pwd:
            st.error("Incorrect Password! Access denied for privacy reasons.")
        else:
            st.info("Personal contact numbers, addresses, and fee accounts are protected. Enter password to view.")

# -------------------------------------------------------------
# 2. ONLINE CERTIFICATE VERIFICATION
# -------------------------------------------------------------
elif menu == "📜 Online Certificate Verification":
    st.header("📜 Online Certificate Verification Desk")
    v_id = st.text_input("Enter Student Roll ID / Registration No (e.g. STC26-001):").strip().upper()
    if v_id:
        v_match = student_df[student_df["Student ID"] == v_id]
        if not v_match.empty:
            v_data = v_match.iloc[0]
            st.balloons()
            st.markdown(f"""
<div class="green-badge">
<h3 style="margin:0; color:#15803D;">✅ OFFICIAL RECORD VERIFIED</h3>
<p style="margin:8px 0 0 0; font-size:15px;"><b>Candidate Name:</b> {v_data['Name']} | <b>Course:</b> {v_data['Course']} | <b>Roll ID:</b> {v_data['Student ID']}</p>
<p style="margin:4px 0 0 0; font-size:13px; color:#15803D;">Center: Soft Tech Computers & ZTC (Code: 4159) | HP Reg No: {v_data['HO_Reg_No'] if v_data['HO_Reg_No'] else 'Registered'} | Status: {v_data['Status']}</p>
</div>
""", unsafe_allow_html=True)
        else:
            st.error("❌ INVALID ROLL ID! No official matching record found in academy database.")

# -------------------------------------------------------------
# 3. NEW STUDENT ADMISSION
# -------------------------------------------------------------
elif menu == "📝 New Student Admission":
    st.header("📝 Candidate Admission Data Capture Format (DCF)")
    auth_pwd = st.text_input("Enter Staff / Admin Password:", type="password", key="adm_pwd")
    if auth_pwd in [ADMIN_PWD, TEACHER_PWD]:
        st.success("Authorized Access Granted!")
        year_code = str(datetime.date.today().year)[2:]
        existing_ids = [sid for sid in student_df["Student ID"] if str(sid).startswith(f"STC{year_code}-")] if not student_df.empty else []
        next_id = f"STC{year_code}-{len(existing_ids)+1:03d}"
        st.info(f"⚡ **Auto-Generated Roll ID:** `{next_id}`")
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            cert_dur = st.selectbox("Course Duration Option*", ["12 Months", "6 Months", "3 Months", "2 Months", "45 Days"])
            join_date = st.date_input("Admission / Joining Date*", value=datetime.date.today())
            months_to_add = 12 if "12" in cert_dur else (6 if "6" in cert_dur else (3 if "3" in cert_dur else (2 if "2" in cert_dur else 1)))
            auto_expiry = join_date + datetime.timedelta(days=months_to_add*30)
            st.success(f"📅 **Course Expiry Date:** {auto_expiry.strftime('%d-%B-%Y')}")

        with st.form("add_student_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Student Full Name*")
                fname = st.text_input("Father's Name*")
                mname = st.text_input("Mother's Name*")
                gender = st.selectbox("Gender", ["Male", "Female", "Other"])
                dob = st.date_input("Date of Birth", min_value=datetime.date(1990, 1, 1))
                mobile = st.text_input("Mobile Number (Unique Key)*")
                photo_file = st.file_uploader("Upload Passport Photo", type=["jpg", "jpeg", "png"])
                
            with col2:
                vill = st.text_input("Village / Town*")
                po = st.text_input("Post Office")
                ps = st.text_input("Police Station", value="THELAMARA")
                dist = st.text_input("District", value="Sonitpur")
                course_list = courses_df["Course Name"].tolist() if not courses_df.empty else []
                course = st.selectbox("Course Selected*", course_list)
                days_batch = st.selectbox("Class Schedule Days*", ["MWF (Monday, Wednesday, Friday)", "TTS (Tuesday, Thursday, Saturday)", "Regular (Daily Classes)"])
                
            col3, col4 = st.columns(2)
            with col3:
                session = st.text_input("Session", value=f"{datetime.date.today().year}-{datetime.date.today().year+1}")
                total_fee = st.number_input("Total Course Fee (₹)", min_value=0.0, value=2550.0, step=100.0)
                discount = st.number_input("Discount Allowed (₹)", min_value=0.0, step=50.0)
                
            with col4:
                shift = st.selectbox("Shift Assigned", ["Morning (06:30-08:00 AM)", "Afternoon (04:00-05:30 PM)", "Evening (05:30-07:00 PM)"])
                batch_time = st.text_input("Batch Timing", value="90 Minutes Session")
                
            if st.form_submit_button("🟢 Submit Admission Now"):
                existing_mobiles = student_df["Mobile No"].tolist() if not student_df.empty else []
                if not name or not mobile:
                    st.error("Please fill in Name and Mobile Number!")
                elif mobile in existing_mobiles:
                    st.error("🚨 THIS MOBILE NUMBER IS ALREADY REGISTERED WITH STC!")
                else:
                    photo_path = ""
                    if photo_file is not None:
                        photo_path = os.path.join(PHOTO_DIR, f"{next_id}.png")
                        with open(photo_path, "wb") as f:
                            f.write(photo_file.getbuffer())
                            
                    net_fee = float(total_fee) - float(discount)
                    full_addr = f"{vill}, {po}, {ps}, {dist}".upper()
                    new_row = {
                        "Sl. No.": str(len(student_df) + 1), "Student ID": next_id, "Name": name.upper(),
                        "Father Name": fname.upper(), "Mother Name": mname.upper(), "Gender": gender,
                        "DOB": str(dob), "Caste": "General", "Mobile No": mobile, "Vill Town": vill.upper(),
                        "PO": po.upper(), "PS": ps.upper(), "PIN Code": "784149", "District": dist.upper(),
                        "Full Address": full_addr, "Course": course,
                        "Duration": cert_dur, "Days_Batch": days_batch, "Session": session,
                        "Join Date": str(join_date), "Validity Date": str(auto_expiry),
                        "Total Fee": str(total_fee), "Discount": str(discount), "Net Fee": str(net_fee),
                        "Shift": shift, "Batch Time": batch_time, "Photo Path": photo_path, "Status": "Active",
                        "HO_Reg_No": "Pending", "Stage_HO_Reg": "Submitted to HP HO", "Stage_AdmitCard": "Pending",
                        "Stage_Exam": "Not Appeared", "Stage_Cert_Status": "In Process", "Cert_Serial_No": "--",
                        "Cert_Arrival_Date": "--", "Cert_Handover_Date": "--", "Handover_Status": "Pending"
                    }
                    st.session_state["student_df"] = pd.concat([st.session_state["student_df"], pd.DataFrame([new_row])], ignore_index=True)
                    save_data(st.session_state["student_df"], STUDENT_MASTER_FILE, "students_db", "student_df")
                    st.balloons()
                    st.markdown(f"""
<div class="green-badge">
🎉 <b>Candidate Registered Successfully!</b> Student ID: <b>{next_id}</b>
</div>
""", unsafe_allow_html=True)
                    st.rerun()

# -------------------------------------------------------------
# 4. STUDENT LOGIN PORTAL (WITH ID CARD & PASSBOOK PRINTER)
# -------------------------------------------------------------
elif menu == "🔑 Student Login Portal":
    st.header("🔑 Student Individual Dashboard & Digital Documents")
    if "student_logged_in" not in st.session_state:
        st.session_state["student_logged_in"] = False
        st.session_state["logged_student_id"] = ""

    if not st.session_state["student_logged_in"]:
        col_l1, col_l2 = st.columns(2)
        with col_l1:
            s_id_in = st.text_input("Enter Student Roll ID:").strip().upper()
        with col_l2:
            s_pwd_in = st.text_input("Enter Password (Registered Mobile No):", type="password").strip()
            
        if st.button("🟢 Login To Dashboard", use_container_width=True):
            st_data = student_df[(student_df["Student ID"] == s_id_in) & (student_df["Mobile No"] == s_pwd_in)]
            if not st_data.empty:
                st.session_state["student_logged_in"] = True
                st.session_state["logged_student_id"] = s_id_in
                st.rerun()
            else:
                st.error("❌ Invalid Roll ID or Mobile Number!")
                
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("❓ Need Login Help / Retrieve Roll ID?", expanded=False):
            st.info("💡 **Note:** Your registered 10-digit mobile number provided during admission is your default password.")
            st.markdown("---")
            st.write("**🔍 Option 1: Find your Roll ID by Mobile Number**")
            find_mob = st.text_input("Enter your 10-digit Registered Mobile Number:", key="find_mob_in").strip()
            if st.button("Search My Roll ID"):
                if find_mob:
                    match_s = student_df[student_df["Mobile No"] == find_mob]
                    if not match_s.empty:
                        for _, row in match_s.iterrows():
                            st.markdown(f"""
<div class="green-badge">
✅ <b>Student Record Found:</b><br>
<b>Name:</b> {row['Name']}<br>
<b>Roll ID:</b> <span style="font-size:18px; color:#047857;"><b>{row['Student ID']}</b></span><br>
<b>Password:</b> <i>Your 10-digit Mobile Number ({find_mob})</i>
</div>
""", unsafe_allow_html=True)
                    else:
                        st.error("No student found with this mobile number. Please contact director support below.")
                        
            st.markdown("---")
            st.write("**💬 Option 2: Direct WhatsApp Support**")
            wa_link = "https://wa.me/919101026718?text=Hello%20Director%20Sir,%20I%20forgot%20my%20Student%20Portal%20Login%20Details%20(STC%20Portal).%20Please%20help."
            st.markdown(f"""
<a href="{wa_link}" target="_blank" style="text-decoration:none;">
<div style="background-color:#25D366; color:white; padding:10px 16px; border-radius:6px; font-weight:bold; text-align:center; display:inline-block;">
📲 Message Director Sir on WhatsApp (+91 9101026718)
</div>
</a>
""", unsafe_allow_html=True)
    else:
        s_id = st.session_state["logged_student_id"]
        s = student_df[student_df["Student ID"] == s_id].iloc[0]
        
        st.markdown(f"""
<div class="green-badge">
Welcome back, <b>{s['Name']}</b> | Roll ID: <b>{s['Student ID']}</b> | Course: <b>{s['Course']}</b>
</div>
""", unsafe_allow_html=True)
        
        ho_reg = s["HO_Reg_No"] if s["HO_Reg_No"] and s["HO_Reg_No"] != "Pending" else "In Process"
        c_status = s["Stage_Cert_Status"] if s["Stage_Cert_Status"] else "In Process"
        
        st.markdown(f"""
<div class="stepper-wrapper">
<div class="stepper-item">
<div class="step-counter active">1</div>
<div class="step-name">Admission<br><span style="color:#10B981;">✓ Confirmed</span></div>
</div>
<div class="stepper-item">
<div class="step-counter {'active' if ho_reg != 'In Process' else ''}">2</div>
<div class="step-name">HP HO Reg<br><span style="color:#0284C7;">{ho_reg}</span></div>
</div>
<div class="stepper-item">
<div class="step-counter {'active' if s['Stage_AdmitCard'] == 'Generated' else ''}">3</div>
<div class="step-name">Admit Card<br><span style="color:#64748B;">{s['Stage_AdmitCard']}</span></div>
</div>
<div class="stepper-item">
<div class="step-counter {'active' if 'Arrived' in c_status or 'Delivered' in c_status else ''}">4</div>
<div class="step-name">Certificate<br><span style="color:#10B981;">{c_status}</span></div>
</div>
<div class="stepper-item">
<div class="step-counter {'active' if s['Handover_Status'] == 'Delivered' else ''}">5</div>
<div class="step-name">Handover<br><span style="color:#64748B;">{s['Handover_Status']}</span></div>
</div>
</div>
""", unsafe_allow_html=True)
        
        # Calculations
        p_logs = fee_df[fee_df["Student ID"] == s_id]
        tot_paid = sum([float(amt) for amt in p_logs["Amount Paid"] if amt])
        net_f = float(s["Net Fee"]) if s["Net Fee"] else 0.0
        due_f = net_f - tot_paid
        
        s_att = att_df[att_df["Student ID"] == s_id]
        tot_classes = len(s_att)
        present_cnt = len(s_att[s_att["Status"].isin(["Present", "Late"])])
        att_percentage = (present_cnt / tot_classes * 100) if tot_classes > 0 else 100.0
        
        s_marks = marks_df[marks_df["Student ID"] == s_id]
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Fee Paid", f"₹{tot_paid:.2f}", f"Net: ₹{net_f:.2f}")
        c2.metric("Due Balance", f"₹{due_f:.2f}", delta="-Due" if due_f > 0 else "Cleared", delta_color="inverse")
        c3.metric("Attendance Score", f"{att_percentage:.1f}%", f"{present_cnt}/{tot_classes} Days")
        c4.metric("HP Registration No", f"{ho_reg}")
        
        st.markdown("---")
        
        s_tab1, s_tab2, s_tab3, s_tab4, s_tab5 = st.tabs([
            "🪪 My Digital ID Card", 
            "💳 Installment Passbook Card", 
            "🎫 Official Admit Card", 
            "📸 Attendance Log", 
            "📝 Exam Marksheet"
        ])
        
        with s_tab1:
            st.subheader("🪪 Official Student Digital Identity Card")
            photo_src = get_student_photo_base64(s["Photo Path"])
            qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=110x110&data={s['Student ID']}"
            barcode_url = f"https://quickchart.io/barcode?type=code128&text={s['Student ID']}&width=180&height=36"
            
            st.markdown(f"""
<div class="id-card-container">
<div class="id-card-header">
<div style="font-size:14px; font-weight:800; color:#38BDF8; letter-spacing:0.5px;">SOFT TECH COMPUTERS & ZTC</div>
<div style="font-size:10px; color:#E2E8F0;">ISO 9001:2015 Certified | Center Code: 4159</div>
<div style="font-size:9.5px; color:#94A3B8;">Kamarchuburi, Thelamara, Sonitpur - 784149</div>
</div>
<div class="id-card-body">
<img src="{photo_src}" class="id-photo"><br>
<div class="id-name">{s['Name']}</div>
<div class="id-roll-badge">ROLL ID: {s['Student ID']}</div>
<table class="id-details-table">
<tr><td><b>Course:</b></td><td>{s['Course']}</td></tr>
<tr><td><b>Father:</b></td><td>{s['Father Name']}</td></tr>
<tr><td><b>Mobile:</b></td><td>{s['Mobile No']}</td></tr>
<tr><td><b>Shift/Batch:</b></td><td>{s['Shift']}</td></tr>
<tr><td><b>Validity:</b></td><td>{s['Validity Date']}</td></tr>
</table>
<div style="display:flex; justify-content:space-around; align-items:center; margin-top:6px;">
<div>
<img src="{qr_url}" style="width:75px; height:75px; border:1px solid #CBD5E1; padding:2px; border-radius:4px;"><br>
<span style="font-size:9px; color:#64748B;">Attendance QR</span>
</div>
<div style="text-align:right;">
<img src="{barcode_url}" style="width:140px; height:30px;"><br>
<div style="border-top:1px solid #0F172A; width:100px; margin-top:8px; margin-left:auto;"></div>
<span style="font-size:9.5px; color:#0F172A; font-weight:bold;">Director Sign</span>
</div>
</div>
</div>
<div class="id-card-footer">
<span style="font-size:9px; color:#64748B;">Affiliated with Sarva India (HP)</span>
<span style="font-size:9px; font-weight:bold; color:#10B981;">● ACTIVE TRAINEE</span>
</div>
</div>
""", unsafe_allow_html=True)
            
        with s_tab2:
            st.subheader("💳 Student Fee Installment Passbook Card")
            rows_html = ""
            current_running_paid = 0.0
            for idx, (_, row) in enumerate(p_logs.iterrows(), 1):
                amt = float(row["Amount Paid"]) if row["Amount Paid"] else 0.0
                current_running_paid += amt
                running_due = max(0.0, net_f - current_running_paid)
                rows_html += f"""
<tr>
<td><b>{idx}</b></td>
<td>{row['Date']}</td>
<td>{row['Receipt No']}</td>
<td style="color:#047857; font-weight:bold;">₹{amt:.2f}</td>
<td style="color:#DC2626; font-weight:bold;">₹{running_due:.2f}</td>
<td>{row['Payment Mode']}</td>
<td>{row['Collected_By']}</td>
</tr>
"""
            if not rows_html:
                rows_html = "<tr><td colspan='7' style='color:#64748B;'>No installment payments deposited yet.</td></tr>"
                
            st.markdown(f"""
<div class="passbook-card">
<div class="passbook-header">
<h3 style="margin:0; color:#0F172A;">SOFT TECH COMPUTERS & ZTC ENTERPRISE</h3>
<p style="margin:2px 0 0 0; font-size:11.5px; color:#64748B;">Accredited Center Code: 4159 | An ISO 9001:2015 Certified Academy</p>
<h4 style="margin:6px 0 0 0; color:#0284C7; text-transform:uppercase;">OFFICIAL STUDENT FEE INSTALLMENT PASSBOOK CARD</h4>
</div>
<div style="display:flex; justify-content:space-between; font-size:13px; margin-bottom:10px; background:#F8FAFC; padding:10px; border-radius:6px; border:1px solid #E2E8F0;">
<div>
<b>Candidate Name:</b> {s['Name']}<br>
<b>Roll ID:</b> {s['Student ID']}<br>
<b>Course:</b> {s['Course']}
</div>
<div style="text-align:right;">
<b>Total Course Fee:</b> ₹{net_f:.2f}<br>
<b>Total Deposited:</b> <span style="color:#047857; font-weight:bold;">₹{tot_paid:.2f}</span><br>
<b>Net Due Balance:</b> <span style="color:#DC2626; font-weight:bold;">₹{due_f:.2f}</span>
</div>
</div>
<table class="passbook-table">
<thead>
<tr>
<th>Inst #</th>
<th>Date</th>
<th>Receipt No</th>
<th>Amount Paid</th>
<th>Balance Due</th>
<th>Pay Mode</th>
<th>Authorized Sign</th>
</tr>
</thead>
<tbody>
{rows_html}
</tbody>
</table>
<div style="display:flex; justify-content:space-between; margin-top:25px; font-size:11px; color:#64748B; border-top:1px dashed #CBD5E1; padding-top:8px;">
<span>Student / Guardian Copy</span>
<span style="font-weight:bold; color:#0F172A;">Authorized Cashier / Director Signature</span>
</div>
</div>
""", unsafe_allow_html=True)
            
        with s_tab3:
            st.subheader("🎫 Official Examination Admit Card")
            st.markdown(f"""
<div style="background:#FFFFFF; border:2px solid #0284C7; border-radius:10px; padding:20px; max-width:700px; margin:auto; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
<div style="text-align:center; border-bottom:2px solid #0284C7; padding-bottom:10px;">
<h3 style="margin:0; color:#0F172A;">SOFT TECH COMPUTERS & ZTC ENTERPRISE</h3>
<p style="margin:2px 0 0 0; font-size:12px; color:#64748B;">Accredited Center Code: 4159 | Affiliated with Sarva India (HP Head Office)</p>
<h4 style="margin:8px 0 0 0; color:#0284C7; text-transform:uppercase;">Official Examination Admit Card</h4>
</div>
<div style="display:flex; justify-content:space-between; margin-top:15px; font-size:14px; line-height:1.8;">
<div>
<b>Candidate Name:</b> {s['Name']}<br>
<b>Roll ID:</b> {s['Student ID']}<br>
<b>HP Reg No:</b> {ho_reg}<br>
<b>Course:</b> {s['Course']}<br>
<b>Batch Time:</b> {s['Shift']}
</div>
<div style="text-align:right;">
<b>Exam Center:</b> STC Lab (Code: 4159)<br>
<b>Center Location:</b> Thelamara, Sonitpur<br>
<b>Academic Year:</b> {s['Session']}<br>
<b>Validity:</b> {s['Validity Date']}
</div>
</div>
<div style="margin-top:20px; border-top:1px dashed #CBD5E1; padding-top:10px; font-size:11px; color:#64748B; display:flex; justify-content:space-between;">
<span>Candidate Signature</span>
<span>Authorized Center Seal & Signature</span>
</div>
</div>
""", unsafe_allow_html=True)
            
        with s_tab4:
            st.subheader("📸 Classroom Attendance Log")
            if not s_att.empty:
                st.dataframe(s_att[["Date", "Time_In", "Status", "Sign_Mode", "Location_Verified"]], use_container_width=True)
            else:
                st.info("No daily attendance recorded yet.")
                
        with s_tab5:
            st.subheader("📝 Official Exam & Class Test Marks Report")
            if not s_marks.empty:
                st.dataframe(s_marks[["Date", "Course/Subject", "Test Topic", "Marks Obtained", "Total Marks", "Teacher Incharge"]], use_container_width=True)
            else:
                st.info("No exam or test marks recorded yet.")
            
        if st.button("🔒 Logout From Portal"):
            st.session_state["student_logged_in"] = False
            st.session_state["logged_student_id"] = ""
            st.rerun()

# -------------------------------------------------------------
# 5. SUNDAY FREE PRACTICE CLASS (SFPC)
# -------------------------------------------------------------
elif menu == "🎯 Sunday Free Practice Class (SFPC)":
    st.header("🎯 Sunday Free Practice Class (SFPC) Desk")
    tab_sf1, tab_sf2 = st.tabs(["🔒 Student Eligibility & Fee Summary", "📝 Staff SFPC Lab Entry Log"])
    
    with tab_sf1:
        st.subheader("🔑 Check SFPC Eligibility & Account Summary")
        col_sf_id, col_sf_pwd = st.columns(2)
        with col_sf_id:
            sf_id = st.text_input("Enter Student Roll ID (e.g. STC26-001):", key="sf_user_id").strip().upper()
        with col_sf_pwd:
            sf_pwd = st.text_input("Enter Password (Registered Mobile No):", type="password", key="sf_user_pwd").strip()
            
        if st.button("🟢 Check My SFPC Eligibility Now", use_container_width=True):
            if not sf_id or not sf_pwd:
                st.error("Please enter both Roll ID and Password!")
            else:
                st_res = student_df[(student_df["Student ID"] == sf_id) & (student_df["Mobile No"] == sf_pwd)]
                if not st_res.empty:
                    s = st_res.iloc[0]
                    p_logs = fee_df[fee_df["Student ID"] == sf_id]
                    tot_paid = sum([float(a) for a in p_logs["Amount Paid"] if a])
                    net_f = float(s["Net Fee"]) if s["Net Fee"] else 2550.0
                    due_f = net_f - tot_paid
                    
                    s_att = att_df[att_df["Student ID"] == sf_id]
                    tot_classes = len(s_att)
                    present_classes = len(s_att[s_att["Status"].isin(["Present", "Late"])])
                    att_pct = (present_classes / tot_classes * 100) if tot_classes > 0 else 100.0
                    
                    cond1 = tot_paid >= 999.0
                    fee_pct = (tot_paid / net_f * 100) if net_f > 0 else 100.0
                    cond2 = fee_pct >= 50.0
                    cond3 = att_pct >= 75.0
                    
                    is_eligible = cond1 and cond2 and cond3
                    
                    st.markdown("---")
                    st.subheader(f"📊 Student Account & SFPC Summary: {s['Name']}")
                    col_c1, col_c2, col_c3 = st.columns(3)
                    col_c1.metric("Total Fee Paid", f"₹{tot_paid:.2f}", f"Due: ₹{due_f:.2f}")
                    col_c2.metric("Fee Clearance", f"{fee_pct:.1f}%", "Min 50% required")
                    col_c3.metric("Attendance Score", f"{att_pct:.1f}%", "Min 75% required")
                    
                    st.markdown("---")
                    st.write("**Mandatory Eligibility Checklist:**")
                    st.write(f"- {'✅' if cond1 else '❌'} **Admission Fee (Min ₹999 Paid):** Paid ₹{tot_paid:.2f}")
                    st.write(f"- {'✅' if cond2 else '❌'} **50% Total Course Fee Clearance:** Current {fee_pct:.1f}%")
                    st.write(f"- {'✅' if cond3 else '❌'} **Minimum 75% Class Attendance:** Current {att_pct:.1f}%")
                    
                    if is_eligible:
                        st.markdown("""
<div class="green-badge" style="font-size:16px;">
🎉 <b>APPROVED: Candidate is 100% ELIGIBLE for Sunday Free Practice Class (SFPC)!</b>
</div>
""", unsafe_allow_html=True)
                    else:
                        st.markdown("""
<div class="pink-badge" style="font-size:16px;">
❌ <b>NOT ELIGIBLE:</b> Student does not satisfy all 3 mandatory SFPC criteria. Please clear pending dues/attendance.
</div>
""", unsafe_allow_html=True)
                else:
                    st.error("❌ Authentication Failed: Invalid Roll ID or Password!")
                
    with tab_sf2:
        sf_auth = st.text_input("Enter Staff Password for SFPC Lab Entry:", type="password", key="sfpc_auth")
        if sf_auth in [ADMIN_PWD, TEACHER_PWD]:
            with st.form("sfpc_entry_form", clear_on_submit=True):
                sf_sid = st.selectbox("Select Student:", student_df["Student ID"] + " - " + student_df["Name"]) if not student_df.empty else None
                pc_no = st.selectbox("Machine / PC Allocated:", [f"PC-{i:02d}" for i in range(1, 21)])
                sf_topic = st.selectbox("Practice Topic:", ALL_SYLLABUS_TOPICS)
                sf_teacher = st.selectbox("Teacher Incharge:", teacher_df["Name"].tolist() if not teacher_df.empty else ["Director Chiranjeeb Hazarika"])
                
                if st.form_submit_button("🟢 Record Sunday Practice Entry"):
                    if sf_sid:
                        sid_val = sf_sid.split(" - ")[0]
                        sname_val = sf_sid.split(" - ")[1]
                        new_sf = {
                            "Date": str(datetime.date.today()), "Student ID": sid_val,
                            "Student Name": sname_val, "PC Machine No": pc_no,
                            "Topic Practiced": sf_topic, "Teacher Incharge": sf_teacher
                        }
                        st.session_state["sfpc_df"] = pd.concat([st.session_state["sfpc_df"], pd.DataFrame([new_sf])], ignore_index=True)
                        save_data(st.session_state["sfpc_df"], SFPC_FILE, "sfpc_db", "sfpc_df")
                        st.markdown('<div class="green-badge">✅ SFPC Practice Session Saved Successfully!</div>', unsafe_allow_html=True)
                        st.rerun()
            if not sfpc_df.empty:
                st.dataframe(sfpc_df, use_container_width=True)

# -------------------------------------------------------------
# 6. FEE COUNTER DESK
# -------------------------------------------------------------
elif menu == "💵 Fee Counter Desk":
    st.header("💵 Student Fee Collection Counter Desk")
    f_pwd = st.text_input("Enter Password:", type="password", key="fee_desk_pwd")
    if f_pwd in [ADMIN_PWD, TEACHER_PWD]:
        sel_sid = st.selectbox("Select Student ID:", student_df["Student ID"] + " - " + student_df["Name"]) if not student_df.empty else None
        if sel_sid:
            sid = sel_sid.split(" - ")[0]
            s_rec = student_df[student_df["Student ID"] == sid].iloc[0]
            paid_logs = fee_df[fee_df["Student ID"] == sid]
            total_paid = sum([float(amt) for amt in paid_logs["Amount Paid"] if amt])
            net = float(s_rec["Net Fee"]) if s_rec["Net Fee"] else 0.0
            due = net - total_paid
            
            st.markdown(f"""
<div style="background:#FFFFFF; border-left:4px solid #0284C7; padding:12px 16px; border-radius:6px; margin:10px 0; border:1px solid #E2E8F0;">
<b>Student:</b> {s_rec['Name']} | <b>Course Fee:</b> ₹{net:.2f} | <b>Paid:</b> ₹{total_paid:.2f} | <b>Due Balance:</b> <span style="color:#EF4444; font-weight:bold;">₹{due:.2f}</span>
</div>
""", unsafe_allow_html=True)
            
            with st.form("fee_collect_form", clear_on_submit=True):
                pay_amt = st.number_input("Amount Paid (₹)", min_value=100.0, step=100.0)
                pay_mode = st.selectbox("Payment Mode", ["Cash", "UPI / GPay", "Bank Transfer"])
                collector_nm = st.selectbox("Collected By:", teacher_df["Name"].tolist() if not teacher_df.empty else ["Director Chiranjeeb Hazarika"])
                remarks = st.text_input("Remarks", value="Monthly / Installment Fee")
                
                if st.form_submit_button("🟢 Issue Receipt & Save Deposit"):
                    rc_num = f"REC-{datetime.date.today().strftime('%Y%m%d')}-{len(fee_df)+1:03d}"
                    f_row = {"Receipt No": rc_num, "Student ID": sid, "Date": str(datetime.date.today()), "Amount Paid": str(pay_amt), "Payment Mode": pay_mode, "Collected_By": collector_nm, "Remarks": remarks}
                    st.session_state["fee_df"] = pd.concat([st.session_state["fee_df"], pd.DataFrame([f_row])], ignore_index=True)
                    save_data(st.session_state["fee_df"], FEE_LOG_FILE, "fees_db", "fee_df")
                    st.markdown(f"""
<div class="green-badge">
🧾 <b>Money Receipt Issued!</b> Receipt No: <b>{rc_num}</b> | Amount: <b>₹{pay_amt}</b>
</div>
""", unsafe_allow_html=True)
                    st.rerun()

# -------------------------------------------------------------
# 7. TEACHER PORTAL & ATTENDANCE + EXAM MARKS ENTRY MENU
# -------------------------------------------------------------
elif menu == "🔑 Teacher Portal & Attendance":
    st.header("🔑 Faculty / Teacher Desk, Attendance & Exam Management")
    t_pwd = st.text_input("Enter Teacher Portal Password:", type="password", key="t_desk_pwd")
    if t_pwd in [ADMIN_PWD, TEACHER_PWD]:
        st.success("Authorized Faculty Access Granted!")
        t_tab1, t_tab2, t_tab3, t_tab4, t_tab5, t_tab6 = st.tabs([
            "⏰ Teacher Self Attendance & Salary Punch",
            "📸 Student Attendance (IST)",
            "📝 Student Exam & Test Marks Entry",
            "📚 Syllabus Coverage (Multi-Topic)",
            "💻 PC Lab Allocation",
            "📋 Daily Student Tasks"
        ])
        
        with t_tab1:
            st.subheader("⏰ Teacher Shift Attendance (Late Penalty & Daily Earning)")
            now_ist = datetime.datetime.now(IST)
            st.info(f"🕒 **Current IST Real-Time:** `{now_ist.strftime('%I:%M:%S %p (%d-%B-%Y)')}`")
            
            st.markdown("""
<div style="background:#F1F5F9; border:1px solid #CBD5E1; padding:10px 14px; border-radius:6px; font-size:13px; margin-bottom:12px;">
💡 <b>Salary Rule:</b> 3 Batches (90+90+90 = 270 Mins) = <b>₹230 / Day</b> (₹76.67 per 90-min batch | ₹0.852/Min). Late arrival automatically calculates penalty deduction.
</div>
""", unsafe_allow_html=True)
            
            t_name_sel = st.selectbox("Select Teacher Name:", teacher_df["Name"].tolist() if not teacher_df.empty else ["Director Chiranjeeb Hazarika"])
            t_shift_sel = st.selectbox("Assigned Shift:", [
                "Morning (06:30 - 08:00 AM)",
                "Afternoon (04:00 - 05:30 PM)",
                "Evening (05:30 - 07:00 PM)"
            ])
            
            shift_start_mins = 6 * 60 + 30 if "Morning" in t_shift_sel else (16 * 60 if "Afternoon" in t_shift_sel else 17 * 60 + 30)
            current_mins = now_ist.hour * 60 + now_ist.minute
            late_by = max(0, current_mins - shift_start_mins)
            is_late = late_by > 5
            
            base_batch_pay = 230.0 / 3.0
            per_min_rate = 230.0 / 270.0
            penalty_amt = round(min(late_by * per_min_rate, base_batch_pay), 2) if is_late else 0.0
            net_batch_earning = round(max(0.0, base_batch_pay - penalty_amt), 2)
            
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                if st.button("🟢 Teacher Punch IN Now", use_container_width=True):
                    today_str = str(datetime.date.today())
                    time_in_str = now_ist.strftime("%I:%M %p")
                    stat_val = "Late" if is_late else "On-Time"
                    late_val = f"{late_by} Mins" if is_late else "0"
                    
                    new_t_att = {
                        "Date": today_str,
                        "Teacher ID": t_name_sel,
                        "Name": t_name_sel,
                        "Shift": t_shift_sel,
                        "Time_In": time_in_str,
                        "Time_Out": "--",
                        "Status": stat_val,
                        "Late_Mins": late_val,
                        "Penalty_Deduction": f"₹{penalty_amt:.2f}",
                        "Net_Earning_Today": f"₹{net_batch_earning:.2f}",
                        "Remarks": "Punched In"
                    }
                    st.session_state["teacher_att_df"] = pd.concat([st.session_state["teacher_att_df"], pd.DataFrame([new_t_att])], ignore_index=True)
                    save_data(st.session_state["teacher_att_df"], TEACHER_ATT_FILE, "teacher_attendance", "teacher_att_df")
                    
                    if is_late:
                        st.markdown(f"""
<div class="pink-badge">
🚨 <b>RED ALERT (LATE PUNCH):</b> Punched In at <b>{time_in_str}</b> (Late by <b>{late_by} mins</b>)!<br>
<b>Penalty Deducted:</b> ₹{penalty_amt:.2f} | <b>Net Shift Earning:</b> ₹{net_batch_earning:.2f} / ₹{base_batch_pay:.2f}
</div>
""", unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
<div class="green-badge">
✅ <b>Punched IN On-Time at {time_in_str}!</b> Net Shift Earning: <b>₹{base_batch_pay:.2f}</b>
</div>
""", unsafe_allow_html=True)
                    st.rerun()
                    
            with col_p2:
                if st.button("🔴 Teacher Punch OUT Now", use_container_width=True):
                    today_str = str(datetime.date.today())
                    time_out_str = now_ist.strftime("%I:%M %p")
                    idx = st.session_state["teacher_att_df"][(st.session_state["teacher_att_df"]["Date"] == today_str) & (st.session_state["teacher_att_df"]["Name"] == t_name_sel)].index
                    if len(idx) > 0:
                        st.session_state["teacher_att_df"].loc[idx[-1], "Time_Out"] = time_out_str
                        st.session_state["teacher_att_df"].loc[idx[-1], "Remarks"] = "Completed"
                        save_data(st.session_state["teacher_att_df"], TEACHER_ATT_FILE, "teacher_attendance", "teacher_att_df")
                        st.markdown(f'<div class="green-badge">✅ Punched OUT at {time_out_str}!</div>', unsafe_allow_html=True)
                    else:
                        st.warning("No Punch IN record found for today to punch out.")
                    st.rerun()
                    
            if not teacher_att_df.empty:
                st.write("**Recent Teacher Punch & Earning Records:**")
                st.dataframe(teacher_att_df.tail(10), use_container_width=True)

        with t_tab2:
            st.subheader("Student Daily Attendance (IST Recorded)")
            with st.form("student_att_form", clear_on_submit=True):
                att_sid = st.selectbox("Select Student:", student_df["Student ID"] + " - " + student_df["Name"]) if not student_df.empty else None
                att_status = st.selectbox("Attendance Status:", ["Present", "Absent", "Late", "Excused"])
                if st.form_submit_button("🟢 Mark Student Attendance"):
                    if att_sid:
                        s_id_val = att_sid.split(" - ")[0]
                        now_time_ist = datetime.datetime.now(IST).strftime("%I:%M %p")
                        att_row = {
                            "Student ID": s_id_val, "Date": str(datetime.date.today()),
                            "Time_In": now_time_ist, "Status": att_status,
                            "Late_Reason": "", "Sign_Mode": "Manual/QR", "Location_Verified": "Classroom"
                        }
                        st.session_state["att_df"] = pd.concat([st.session_state["att_df"], pd.DataFrame([att_row])], ignore_index=True)
                        save_data(st.session_state["att_df"], ATTENDANCE_FILE, "attendance_db", "att_df")
                        st.markdown(f'<div class="green-badge">✅ Attendance marked {att_status} for {att_sid} at {now_time_ist}!</div>', unsafe_allow_html=True)
                        st.rerun()
            if not att_df.empty:
                st.dataframe(att_df.tail(15), use_container_width=True)

        with t_tab3:
            st.subheader("📝 Record Class Test & Exam Marks")
            with st.form("exam_marks_form", clear_on_submit=True):
                exam_sid = st.selectbox("Select Candidate:", student_df["Student ID"] + " - " + student_df["Name"]) if not student_df.empty else None
                exam_course = st.selectbox("Course / Subject:", courses_df["Course Name"].tolist() if not courses_df.empty else ["Computer Application"])
                exam_topic = st.text_input("Test / Exam Name (e.g., MS Word Test, Tally GST Practical, Unit-1 Exam)*")
                
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    marks_obt = st.number_input("Marks Obtained*", min_value=0.0, max_value=100.0, value=40.0, step=1.0)
                with col_m2:
                    total_mks = st.number_input("Total Full Marks*", min_value=1.0, max_value=100.0, value=50.0, step=1.0)
                    
                exam_teacher = st.selectbox("Evaluated By (Teacher):", teacher_df["Name"].tolist() if not teacher_df.empty else ["Director Chiranjeeb Hazarika"])
                
                if st.form_submit_button("🟢 Save Exam Marks"):
                    if exam_sid and exam_topic:
                        sid_val = exam_sid.split(" - ")[0]
                        sname_val = exam_sid.split(" - ")[1]
                        m_row = {
                            "Date": str(datetime.date.today()),
                            "Student ID": sid_val,
                            "Student Name": sname_val,
                            "Course/Subject": exam_course,
                            "Test Topic": exam_topic,
                            "Marks Obtained": str(marks_obt),
                            "Total Marks": str(total_mks),
                            "Teacher Incharge": exam_teacher
                        }
                        st.session_state["marks_df"] = pd.concat([st.session_state["marks_df"], pd.DataFrame([m_row])], ignore_index=True)
                        save_data(st.session_state["marks_df"], MARKS_FILE, "marks_db", "marks_df")
                        st.markdown(f"""
<div class="green-badge">
🎉 <b>Exam Result Saved Successfully!</b><br>
Candidate: <b>{sname_val} ({sid_val})</b> | Test: <b>{exam_topic}</b> | Score: <b>{marks_obt} / {total_mks}</b>
</div>
""", unsafe_allow_html=True)
                        st.rerun()
                    else:
                        st.error("Please enter Exam/Test Topic details!")
                        
            if not marks_df.empty:
                st.write("**Recent Exam / Test Records:**")
                st.dataframe(marks_df.tail(15), use_container_width=True)

        with t_tab4:
            st.subheader("Record Daily Syllabus Coverage (Multi-Select Allowed)")
            with st.form("syl_multi_form", clear_on_submit=True):
                syl_course = st.selectbox("Course:", courses_df["Course Name"].tolist() if not courses_df.empty else [])
                syl_topics = st.multiselect("Topics Covered in Today's Class:*", ALL_SYLLABUS_TOPICS, default=[ALL_SYLLABUS_TOPICS[0]])
                syl_type = st.selectbox("Session Type:", ["Theory Lecture", "Practical Lab Training", "Weekly Revision", "Class Test / Viva"])
                syl_teacher = st.selectbox("Teacher Incharge:", teacher_df["Name"].tolist() if not teacher_df.empty else ["Director Chiranjeeb Hazarika"])
                
                if st.form_submit_button("🟢 Save Daily Syllabus Coverage"):
                    if syl_topics:
                        topics_str = ", ".join(syl_topics)
                        s_row = {"Date": str(datetime.date.today()), "Course": syl_course, "Topics Covered": topics_str, "Class Type": syl_type, "Teacher Incharge": syl_teacher}
                        st.session_state["syllabus_df"] = pd.concat([st.session_state["syllabus_df"], pd.DataFrame([s_row])], ignore_index=True)
                        save_data(st.session_state["syllabus_df"], SYLLABUS_LOG_FILE, "syllabus_logs", "syllabus_df")
                        st.markdown(f'<div class="green-badge">✅ Syllabus entry saved: <b>{topics_str}</b></div>', unsafe_allow_html=True)
                        st.rerun()
                    else:
                        st.error("Please select at least one topic!")
            if not syllabus_df.empty:
                st.dataframe(syllabus_df.tail(10), use_container_width=True)

        with t_tab5:
            st.subheader("Daily Computer Machine Allocation")
            with st.form("pc_alloc_form", clear_on_submit=True):
                pc_sid = st.selectbox("Student:", student_df["Student ID"] + " - " + student_df["Name"], key="pc_s_sel") if not student_df.empty else None
                m_no = st.selectbox("Machine / PC No:", [f"PC-{i:02d}" for i in range(1, 21)])
                pc_shift = st.selectbox("Shift Assigned:", ["Morning", "Afternoon", "Evening"])
                if st.form_submit_button("🟢 Assign Machine"):
                    if pc_sid:
                        pc_row = {"Date": str(datetime.date.today()), "Student ID": pc_sid.split(" - ")[0], "Student Name": pc_sid.split(" - ")[1], "PC Machine No": m_no, "Shift": pc_shift, "Teacher Incharge": "Faculty"}
                        st.session_state["pc_alloc_df"] = pd.concat([st.session_state["pc_alloc_df"], pd.DataFrame([pc_row])], ignore_index=True)
                        save_data(st.session_state["pc_alloc_df"], PC_ALLOC_FILE, "pc_alloc_db", "pc_alloc_df")
                        st.markdown(f'<div class="green-badge">✅ Machine {m_no} allocated to {pc_sid}!</div>', unsafe_allow_html=True)
                        st.rerun()

        with t_tab6:
            st.subheader("Assign Student Daily Tasks / Homework")
            with st.form("task_assign_form", clear_on_submit=True):
                t_sid = st.selectbox("Student:", student_df["Student ID"] + " - " + student_df["Name"], key="t_s_sel") if not student_df.empty else None
                task_txt = st.text_area("Practical Task / Assignment Details:")
                if st.form_submit_button("🟢 Assign Task"):
                    if t_sid and task_txt:
                        tsk_row = {"Date": str(datetime.date.today()), "Student ID": t_sid.split(" - ")[0], "Student Name": t_sid.split(" - ")[1], "Task Assigned": task_txt, "Status": "Assigned", "Teacher Incharge": "Faculty"}
                        st.session_state["tasks_df"] = pd.concat([st.session_state["tasks_df"], pd.DataFrame([tsk_row])], ignore_index=True)
                        save_data(st.session_state["tasks_df"], TASKS_FILE, "tasks_db", "tasks_df")
                        st.markdown('<div class="green-badge">✅ Practical Task Assigned Successfully!</div>', unsafe_allow_html=True)
                        st.rerun()

# -------------------------------------------------------------
# 8. ADMIN CONTROL PANEL
# -------------------------------------------------------------
elif menu == "🔐 Admin Control Panel":
    st.header("🔐 Director Admin Control Panel")
    pwd = st.text_input("Enter Director Admin Password", type="password", key="admin_pwd_main")
    if pwd == ADMIN_PWD:
        st.success("Welcome Director Chiranjeeb Hazarika Sir!")
        adm_tab1, adm_tab2, adm_tab3, adm_tab4, adm_tab5, adm_tab6, adm_tab7, adm_tab8, adm_tab9 = st.tabs([
            "🪪 ID Card & Passbook Printer",
            "🏢 HP HO Registration & Export",
            "📢 WhatsApp Notice & Dispatch Register",
            "📋 Student Edit / Delete",
            "👨‍🏫 Teacher Management",
            "💰 Dues & Balance Ledger",
            "📖 Activity & Logs Review",
            "📚 Course Master",
            "🔑 Change Passwords"
        ])
        
        # 1. ID CARD & PASSBOOK PRINTER DESK
        with adm_tab1:
            st.subheader("🪪 Official ID Card & Fee Installment Passbook Print Desk")
            if not student_df.empty:
                sel_p_sid = st.selectbox("Select Candidate to Generate Documents:", student_df["Student ID"] + " - " + student_df["Name"], key="sel_print_sid")
                if sel_p_sid:
                    p_sid = sel_p_sid.split(" - ")[0]
                    p_stu = student_df[student_df["Student ID"] == p_sid].iloc[0]
                    
                    doc_type = st.radio("Select Document to Print / Preview:", ["🪪 Digital Student ID Card", "💳 Fee Installment Passbook Card"], horizontal=True)
                    
                    if doc_type == "🪪 Digital Student ID Card":
                        photo_src_adm = get_student_photo_base64(p_stu["Photo Path"])
                        qr_url_adm = f"https://api.qrserver.com/v1/create-qr-code/?size=110x110&data={p_stu['Student ID']}"
                        barcode_url_adm = f"https://quickchart.io/barcode?type=code128&text={p_stu['Student ID']}&width=180&height=36"
                        
                        st.markdown(f"""
<div class="id-card-container">
<div class="id-card-header">
<div style="font-size:14px; font-weight:800; color:#38BDF8; letter-spacing:0.5px;">SOFT TECH COMPUTERS & ZTC</div>
<div style="font-size:10px; color:#E2E8F0;">ISO 9001:2015 Certified | Center Code: 4159</div>
<div style="font-size:9.5px; color:#94A3B8;">Kamarchuburi, Thelamara, Sonitpur - 784149</div>
</div>
<div class="id-card-body">
<img src="{photo_src_adm}" class="id-photo"><br>
<div class="id-name">{p_stu['Name']}</div>
<div class="id-roll-badge">ROLL ID: {p_stu['Student ID']}</div>
<table class="id-details-table">
<tr><td><b>Course:</b></td><td>{p_stu['Course']}</td></tr>
<tr><td><b>Father:</b></td><td>{p_stu['Father Name']}</td></tr>
<tr><td><b>Mobile:</b></td><td>{p_stu['Mobile No']}</td></tr>
<tr><td><b>Shift/Batch:</b></td><td>{p_stu['Shift']}</td></tr>
<tr><td><b>Validity:</b></td><td>{p_stu['Validity Date']}</td></tr>
</table>
<div style="display:flex; justify-content:space-around; align-items:center; margin-top:6px;">
<div>
<img src="{qr_url_adm}" style="width:75px; height:75px; border:1px solid #CBD5E1; padding:2px; border-radius:4px;"><br>
<span style="font-size:9px; color:#64748B;">Attendance QR</span>
</div>
<div style="text-align:right;">
<img src="{barcode_url_adm}" style="width:140px; height:30px;"><br>
<div style="border-top:1px solid #0F172A; width:100px; margin-top:8px; margin-left:auto;"></div>
<span style="font-size:9.5px; color:#0F172A; font-weight:bold;">Director Sign</span>
</div>
</div>
</div>
<div class="id-card-footer">
<span style="font-size:9px; color:#64748B;">Affiliated with Sarva India (HP)</span>
<span style="font-size:9px; font-weight:bold; color:#10B981;">● AUTHORIZED ID</span>
</div>
</div>
""", unsafe_allow_html=True)
                        
                    else:
                        stu_p_logs = fee_df[fee_df["Student ID"] == p_sid]
                        adm_tot_paid = sum([float(amt) for amt in stu_p_logs["Amount Paid"] if amt])
                        adm_net_f = float(p_stu["Net Fee"]) if p_stu["Net Fee"] else 0.0
                        adm_due_f = adm_net_f - adm_tot_paid
                        
                        rows_html_adm = ""
                        curr_run_paid = 0.0
                        for idx, (_, row) in enumerate(stu_p_logs.iterrows(), 1):
                            amt = float(row["Amount Paid"]) if row["Amount Paid"] else 0.0
                            curr_run_paid += amt
                            run_due = max(0.0, adm_net_f - curr_run_paid)
                            rows_html_adm += f"""
<tr>
<td><b>{idx}</b></td>
<td>{row['Date']}</td>
<td>{row['Receipt No']}</td>
<td style="color:#047857; font-weight:bold;">₹{amt:.2f}</td>
<td style="color:#DC2626; font-weight:bold;">₹{run_due:.2f}</td>
<td>{row['Payment Mode']}</td>
<td>{row['Collected_By']}</td>
</tr>
"""
                        if not rows_html_adm:
                            rows_html_adm = "<tr><td colspan='7' style='color:#64748B;'>No installment payments deposited yet.</td></tr>"
                            
                        st.markdown(f"""
<div class="passbook-card">
<div class="passbook-header">
<h3 style="margin:0; color:#0F172A;">SOFT TECH COMPUTERS & ZTC ENTERPRISE</h3>
<p style="margin:2px 0 0 0; font-size:11.5px; color:#64748B;">Accredited Center Code: 4159 | An ISO 9001:2015 Certified Academy</p>
<h4 style="margin:6px 0 0 0; color:#0284C7; text-transform:uppercase;">OFFICIAL STUDENT FEE INSTALLMENT PASSBOOK CARD</h4>
</div>
<div style="display:flex; justify-content:space-between; font-size:13px; margin-bottom:10px; background:#F8FAFC; padding:10px; border-radius:6px; border:1px solid #E2E8F0;">
<div>
<b>Candidate Name:</b> {p_stu['Name']}<br>
<b>Roll ID:</b> {p_stu['Student ID']}<br>
<b>Course:</b> {p_stu['Course']}
</div>
<div style="text-align:right;">
<b>Total Course Fee:</b> ₹{adm_net_f:.2f}<br>
<b>Total Deposited:</b> <span style="color:#047857; font-weight:bold;">₹{adm_tot_paid:.2f}</span><br>
<b>Net Due Balance:</b> <span style="color:#DC2626; font-weight:bold;">₹{adm_due_f:.2f}</span>
</div>
</div>
<table class="passbook-table">
<thead>
<tr>
<th>Inst #</th>
<th>Date</th>
<th>Receipt No</th>
<th>Amount Paid</th>
<th>Balance Due</th>
<th>Pay Mode</th>
<th>Authorized Sign</th>
</tr>
</thead>
<tbody>
{rows_html_adm}
</tbody>
</table>
<div style="display:flex; justify-content:space-between; margin-top:25px; font-size:11px; color:#64748B; border-top:1px dashed #CBD5E1; padding-top:8px;">
<span>Student / Guardian Copy</span>
<span style="font-weight:bold; color:#0F172A;">Authorized Cashier / Director Signature</span>
</div>
</div>
""", unsafe_allow_html=True)
            else:
                st.info("No student records available to print.")

        # 2. HP HO REGISTRATION & EXPORT
        with adm_tab2:
            st.subheader("🏢 Head Office (Himachal Pradesh) Candidate Lifecycle Management")
            col_ex1, col_ex2 = st.columns([2, 1])
            with col_ex1:
                st.write("**📥 Export Registered Candidates for Himachal HO:**")
            with col_ex2:
                if not student_df.empty:
                    csv_export = student_df[["Student ID", "Name", "Father Name", "Mother Name", "DOB", "Gender", "Course", "Duration", "Join Date", "Full Address", "Mobile No"]].to_csv(index=False)
                    st.download_button(
                        label="📥 Download HO Candidate Data (CSV)",
                        data=csv_export,
                        file_name=f"STC_HO_Candidates_{datetime.date.today()}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                    
            st.write("---")
            st.markdown("#### ✏️ Update Candidate HP HO Registration & Status")
            if not student_df.empty:
                sel_ho_sid = st.selectbox("Select Candidate to Update HO Record:", student_df["Student ID"] + " - " + student_df["Name"], key="sel_ho_s")
                if sel_ho_sid:
                    ho_sid_val = sel_ho_sid.split(" - ")[0]
                    ho_s_rec = student_df[student_df["Student ID"] == ho_sid_val].iloc[0]
                    
                    with st.form("ho_update_form"):
                        col_u1, col_u2 = st.columns(2)
                        with col_u1:
                            new_ho_reg = st.text_input("Himachal HO Registration No / Roll:", value=ho_s_rec["HO_Reg_No"])
                            new_admit_stat = st.selectbox("Admit Card Status:", ["Pending", "Generated", "Dispatched to Student"], index=0 if ho_s_rec["Stage_AdmitCard"]=="Pending" else 1)
                        with col_u2:
                            new_cert_stat = st.selectbox("Certificate / Marksheet Status from HO:", ["In Process at HP HO", "Dispatched from HP", "Arrived at Center (Ready)", "Handed Over to Student"])
                            new_cert_no = st.text_input("Certificate Serial No (if received):", value=ho_s_rec["Cert_Serial_No"])
                            
                        if st.form_submit_button("🟢 Save HO Registration & Status"):
                            idx_s = st.session_state["student_df"][st.session_state["student_df"]["Student ID"] == ho_sid_val].index
                            if len(idx_s) > 0:
                                st.session_state["student_df"].loc[idx_s[0], "HO_Reg_No"] = new_ho_reg
                                st.session_state["student_df"].loc[idx_s[0], "Stage_AdmitCard"] = new_admit_stat
                                st.session_state["student_df"].loc[idx_s[0], "Stage_Cert_Status"] = new_cert_stat
                                st.session_state["student_df"].loc[idx_s[0], "Cert_Serial_No"] = new_cert_no
                                save_data(st.session_state["student_df"], STUDENT_MASTER_FILE, "students_db", "student_df")
                                st.markdown(f'<div class="green-badge">✅ HO Record for {ho_sid_val} Updated Successfully!</div>', unsafe_allow_html=True)
                                st.rerun()

        # 3. WHATSAPP NOTICE & DISPATCH REGISTER
        with adm_tab3:
            st.subheader("📢 Certificate Arrival Announcement & Handover Record Book")
            st.markdown("#### 💬 1-Click WhatsApp Group Notice Generator")
            arrived_students = student_df[student_df["Stage_Cert_Status"].str.contains("Arrived", na=False)]
            
            if not arrived_students.empty:
                st.write(f"Found **{len(arrived_students)} Candidates** whose certificates have arrived at the center:")
                st.dataframe(arrived_students[["Student ID", "Name", "Course", "Cert_Serial_No", "Stage_Cert_Status"]], use_container_width=True)
                
                names_list = "\n".join([f"• {row['Name']} ({row['Student ID']}) - {row['Course']}" for _, row in arrived_students.iterrows()])
                raw_wa_msg = f"""📢 *OFFICIAL NOTICE: CERTIFICATES & MARKSHEETS ARRIVED!*
Soft Tech Computers & ZTC Enterprise (Center Code: 4159)

Dear Students, your official Sarva India Certificates & Marksheets have safely arrived at our center from Himachal Pradesh Head Office.

*List of Candidates:*
{names_list}

📍 *Please visit our center to sign the official dispatch register and collect your original certificates.*
Time: 09:00 AM - 05:00 PM
Director Contact: 9101026718"""
                
                wa_encoded = urllib.parse.quote(raw_wa_msg)
                wa_broadcast_link = f"https://wa.me/?text={wa_encoded}"
                
                st.markdown(f"""
<a href="{wa_broadcast_link}" target="_blank" style="text-decoration:none;">
<div style="background-color:#25D366; color:white; padding:12px 20px; border-radius:8px; font-weight:bold; text-align:center; display:inline-block; margin:10px 0;">
📲 Share Certificate Arrival List to WhatsApp Group Now
</div>
</a>
""", unsafe_allow_html=True)
            else:
                st.info("No candidates marked as 'Arrived at Center' yet. Update certificate arrival in HP HO tab.")
                
            st.write("---")
            st.markdown("#### 📜 Digital Certificate Handover Log (Student Record Book)")
            with st.form("dispatch_handover_form", clear_on_submit=True):
                disp_sid = st.selectbox("Select Student Collecting Certificate:", student_df["Student ID"] + " - " + student_df["Name"]) if not student_df.empty else None
                c_serial = st.text_input("Certificate Serial No*")
                m_stat = st.selectbox("Marksheet Attached:", ["Certificate + Marksheet", "Certificate Only", "Marksheet Only"])
                rec_by = st.text_input("Collected By (Self / Father / Guardian)*", value="Self")
                rec_contact = st.text_input("Receiver Contact Phone No*")
                
                if st.form_submit_button("🟢 Confirm Handover & Save to Dispatch Book"):
                    if disp_sid and c_serial:
                        d_sid = disp_sid.split(" - ")[0]
                        d_name = disp_sid.split(" - ")[1]
                        d_course = student_df[student_df["Student ID"] == d_sid]["Course"].values[0] if not student_df.empty else "N/A"
                        
                        disp_row = {
                            "Date": str(datetime.date.today()),
                            "Student ID": d_sid,
                            "Student Name": d_name,
                            "Course": d_course,
                            "Certificate No": c_serial,
                            "Marksheet Status": m_stat,
                            "Received By": rec_by,
                            "Contact No": rec_contact,
                            "Handover Confirmed": "YES (Signed)"
                        }
                        st.session_state["dispatch_df"] = pd.concat([st.session_state["dispatch_df"], pd.DataFrame([disp_row])], ignore_index=True)
                        save_data(st.session_state["dispatch_df"], DISPATCH_FILE, "dispatch_db", "dispatch_df")
                        
                        idx_m = st.session_state["student_df"][st.session_state["student_df"]["Student ID"] == d_sid].index
                        if len(idx_m) > 0:
                            st.session_state["student_df"].loc[idx_m[0], "Stage_Cert_Status"] = "Handed Over"
                            st.session_state["student_df"].loc[idx_m[0], "Cert_Handover_Date"] = str(datetime.date.today())
                            st.session_state["student_df"].loc[idx_m[0], "Handover_Status"] = "Delivered"
                            save_data(st.session_state["student_df"], STUDENT_MASTER_FILE, "students_db", "student_df")
                            
                        st.markdown(f'<div class="green-badge">✅ Certificate Handover Recorded in Digital Register for {d_name}!</div>', unsafe_allow_html=True)
                        st.rerun()
                    else:
                        st.error("Please enter Certificate Serial No!")
                        
            if not dispatch_df.empty:
                st.write("**Official Certificate Dispatch & Handover Register:**")
                st.dataframe(dispatch_df, use_container_width=True)

        # 4. STUDENT EDIT & DELETE
        with adm_tab4:
            st.subheader("📋 Student Master Management (Edit / Delete)")
            if not student_df.empty:
                st.dataframe(student_df[["Student ID", "Name", "Mobile No", "Course", "Net Fee", "Join Date", "HO_Reg_No", "Status"]], use_container_width=True)
                
                sel_edit_sid = st.selectbox("Select Student to Edit / Delete:", student_df["Student ID"] + " - " + student_df["Name"])
                if sel_edit_sid:
                    e_sid = sel_edit_sid.split(" - ")[0]
                    s_curr = student_df[student_df["Student ID"] == e_sid].iloc[0]
                    
                    with st.form("edit_student_form"):
                        st.write(f"Editing Record for: **{s_curr['Name']}** ({e_sid})")
                        col_e1, col_e2 = st.columns(2)
                        with col_e1:
                            new_name = st.text_input("Student Name", value=s_curr["Name"])
                            new_mobile = st.text_input("Mobile No", value=s_curr["Mobile No"])
                            new_fee = st.text_input("Net Course Fee (₹)", value=s_curr["Net Fee"])
                        with col_e2:
                            new_course = st.selectbox("Course", courses_df["Course Name"].tolist(), index=0)
                            new_status = st.selectbox("Status", ["Active", "Completed", "Dropout"], index=0 if s_curr["Status"]=="Active" else 1)
                            
                        if st.form_submit_button("🟢 Update Student Record"):
                            st.session_state["student_df"].loc[st.session_state["student_df"]["Student ID"] == e_sid, "Name"] = new_name.upper()
                            st.session_state["student_df"].loc[st.session_state["student_df"]["Student ID"] == e_sid, "Mobile No"] = new_mobile
                            st.session_state["student_df"].loc[st.session_state["student_df"]["Student ID"] == e_sid, "Net Fee"] = new_fee
                            st.session_state["student_df"].loc[st.session_state["student_df"]["Student ID"] == e_sid, "Course"] = new_course
                            st.session_state["student_df"].loc[st.session_state["student_df"]["Student ID"] == e_sid, "Status"] = new_status
                            save_data(st.session_state["student_df"], STUDENT_MASTER_FILE, "students_db", "student_df")
                            st.markdown('<div class="green-badge">✅ Student Record Updated Successfully!</div>', unsafe_allow_html=True)
                            st.rerun()
                            
                    if st.button("🔴 Delete This Student Completely", key="del_s_btn"):
                        st.session_state["student_df"] = st.session_state["student_df"][st.session_state["student_df"]["Student ID"] != e_sid]
                        save_data(st.session_state["student_df"], STUDENT_MASTER_FILE, "students_db", "student_df")
                        st.markdown(f'<div class="pink-badge">🗑️ Student {e_sid} Deleted Completely!</div>', unsafe_allow_html=True)
                        st.rerun()
            else:
                st.info("No student records found.")

        # 5. TEACHER MANAGEMENT
        with adm_tab5:
            st.subheader("👨‍🏫 Teacher Management (Add / Remove)")
            if not teacher_df.empty:
                st.dataframe(teacher_df, use_container_width=True)
                
            st.write("---")
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                st.write("**➕ Add New Faculty / Staff:**")
                with st.form("add_teacher_form", clear_on_submit=True):
                    t_nid = f"TCH-{len(teacher_df)+1:02d}"
                    t_nname = st.text_input("Teacher Name*")
                    t_nphone = st.text_input("Phone Number*")
                    t_nqual = st.text_input("Qualification", value="MCA / PGDCA / Graduate")
                    t_ndesig = st.selectbox("Designation", ["Instructor", "Lab Assistant", "Guest Faculty", "Center Head"])
                    t_nshift = st.selectbox("Shift", ["All Shifts", "Morning", "Afternoon", "Evening"])
                    
                    if st.form_submit_button("🟢 Add Teacher"):
                        if t_nname:
                            new_t_row = {"Teacher ID": t_nid, "Name": t_nname, "Phone": t_nphone, "Qualification": t_nqual, "Designation": t_ndesig, "Shift Assigned": t_nshift}
                            st.session_state["teacher_df"] = pd.concat([st.session_state["teacher_df"], pd.DataFrame([new_t_row])], ignore_index=True)
                            save_data(st.session_state["teacher_df"], TEACHERS_FILE, "teachers_db", "teacher_df")
                            st.markdown(f'<div class="green-badge">✅ Faculty {t_nname} Added Successfully!</div>', unsafe_allow_html=True)
                            st.rerun()
                            
            with col_t2:
                st.write("**🗑️ Remove Faculty:**")
                if not teacher_df.empty:
                    del_t_name = st.selectbox("Select Teacher to Remove:", teacher_df["Name"].tolist())
                    if st.button("🔴 Delete Selected Teacher", key="del_t_btn"):
                        st.session_state["teacher_df"] = st.session_state["teacher_df"][st.session_state["teacher_df"]["Name"] != del_t_name]
                        save_data(st.session_state["teacher_df"], TEACHERS_FILE, "teachers_db", "teacher_df")
                        st.markdown(f'<div class="pink-badge">🗑️ Teacher {del_t_name} Removed!</div>', unsafe_allow_html=True)
                        st.rerun()

        # 6. DUES & BALANCE LEDGER
        with adm_tab6:
            st.subheader("💰 Live Student Fee & Dues Balance Ledger")
            if not student_df.empty:
                ledger_data = []
                total_pending_all = 0.0
                total_collected_all = 0.0
                
                for _, s in student_df.iterrows():
                    sid = s["Student ID"]
                    s_paid_logs = fee_df[fee_df["Student ID"] == sid]
                    tot_p = sum([float(a) for a in s_paid_logs["Amount Paid"] if a])
                    net_f = float(s["Net Fee"]) if s["Net Fee"] else 0.0
                    due_b = net_f - tot_p
                    
                    total_collected_all += tot_p
                    total_pending_all += max(0.0, due_b)
                    
                    ledger_data.append({
                        "Roll ID": sid,
                        "Student Name": s["Name"],
                        "Mobile": s["Mobile No"],
                        "Course": s["Course"],
                        "Net Fee (₹)": f"{net_f:.2f}",
                        "Total Paid (₹)": f"{tot_p:.2f}",
                        "Due Balance (₹)": f"{due_b:.2f}",
                        "Payment Status": "Cleared" if due_b <= 0 else "Pending Due"
                    })
                    
                ld_df = pd.DataFrame(ledger_data)
                
                c_m1, c_m2 = st.columns(2)
                c_m1.metric("Total Fee Collected", f"₹{total_collected_all:,.2f}")
                c_m2.metric("Total Pending Dues from Students", f"₹{total_pending_all:,.2f}", delta="-Pending", delta_color="inverse")
                
                only_dues = st.checkbox("Show Only Students with Pending Dues", value=True)
                if only_dues:
                    show_df = ld_df[ld_df["Payment Status"] == "Pending Due"]
                else:
                    show_df = ld_df
                    
                st.dataframe(show_df, use_container_width=True)

        # 7. CLASS LOGS & ACTIVITIES REVIEW
        with adm_tab7:
            st.subheader("📖 Daily Activities, Attendance & Exam Marks")
            c_sub1, c_sub2, c_sub3, c_sub4, c_sub5 = st.tabs(["📝 Exam Marks", "⏰ Teacher Attendance", "📚 Syllabus Covered", "💻 PC Allocations", "📋 Tasks Assigned"])
            
            with c_sub1:
                if not marks_df.empty:
                    st.dataframe(marks_df, use_container_width=True)
                else:
                    st.info("No exam marks recorded yet.")
            with c_sub2:
                if not teacher_att_df.empty:
                    st.dataframe(teacher_att_df, use_container_width=True)
                else:
                    st.info("No teacher attendance punched yet.")
            with c_sub3:
                if not syllabus_df.empty:
                    st.dataframe(syllabus_df, use_container_width=True)
                else:
                    st.info("No syllabus logs recorded yet.")
            with c_sub4:
                if not pc_alloc_df.empty:
                    st.dataframe(pc_alloc_df, use_container_width=True)
                else:
                    st.info("No PC allocations recorded.")
            with c_sub5:
                if not tasks_df.empty:
                    st.dataframe(tasks_df, use_container_width=True)
                else:
                    st.info("No tasks recorded.")

        # 8. COURSE MASTER SETTINGS
        with adm_tab8:
            st.subheader("📚 Course Master Management (Add / Edit / Delete)")
            if not courses_df.empty:
                st.dataframe(courses_df, use_container_width=True)
            else:
                st.info("No courses registered in catalog.")
                
            st.write("---")
            col_cadd, col_cedit = st.columns(2)
            
            with col_cadd:
                st.markdown("#### ➕ Add New Course")
                with st.form("course_add_form", clear_on_submit=True):
                    c_nname = st.text_input("Course Name / Title*")
                    c_ndur = st.selectbox("Duration", ["12 Months", "6 Months", "3 Months", "2 Months", "45 Days"], key="c_add_dur")
                    c_nfee = st.number_input("Course Fee (₹)*", min_value=100.0, value=3500.0, step=100.0, key="c_add_fee")
                    c_ndesc = st.text_input("Topics / Description", key="c_add_desc")
                    
                    if st.form_submit_button("🟢 Add Course Now"):
                        if c_nname:
                            if c_nname in courses_df["Course Name"].values:
                                st.error("A course with this name already exists! Use the Edit section to modify it.")
                            else:
                                new_c_row = {"Course Name": c_nname, "Duration": c_ndur, "Fee (₹)": str(c_nfee), "Description": c_ndesc}
                                st.session_state["courses_df"] = pd.concat([st.session_state["courses_df"], pd.DataFrame([new_c_row])], ignore_index=True)
                                save_data(st.session_state["courses_df"], COURSES_FILE, "courses_db", "courses_df")
                                st.markdown(f'<div class="green-badge">✅ Course "{c_nname}" Added Successfully!</div>', unsafe_allow_html=True)
                                st.rerun()
                        else:
                            st.error("Please enter Course Name!")
            
            with col_cedit:
                st.markdown("#### ✏️ Edit Existing Course")
                if not courses_df.empty:
                    sel_edit_c = st.selectbox("Select Course to Modify:", courses_df["Course Name"].tolist(), key="sel_edit_c_box")
                    if sel_edit_c:
                        c_data = courses_df[courses_df["Course Name"] == sel_edit_c].iloc[0]
                        with st.form("course_edit_form"):
                            edit_cname = st.text_input("Course Name / Title*", value=c_data["Course Name"])
                            dur_opts = ["12 Months", "6 Months", "3 Months", "2 Months", "45 Days"]
                            dur_idx = dur_opts.index(c_data["Duration"]) if c_data["Duration"] in dur_opts else 0
                            edit_cdur = st.selectbox("Duration", dur_opts, index=dur_idx, key="c_edit_dur")
                            
                            try:
                                curr_fval = float(c_data["Fee (₹)"])
                            except Exception:
                                curr_fval = 3500.0
                                
                            edit_cfee = st.number_input("Course Fee (₹)*", min_value=100.0, value=curr_fval, step=100.0, key="c_edit_fee")
                            edit_cdesc = st.text_input("Topics / Description", value=c_data["Description"] if "Description" in c_data else "", key="c_edit_desc")
                            
                            if st.form_submit_button("🟢 Save Updated Course Details"):
                                match_idx = st.session_state["courses_df"][st.session_state["courses_df"]["Course Name"] == sel_edit_c].index
                                if len(match_idx) > 0:
                                    st.session_state["courses_df"].loc[match_idx[0], "Course Name"] = edit_cname
                                    st.session_state["courses_df"].loc[match_idx[0], "Duration"] = edit_cdur
                                    st.session_state["courses_df"].loc[match_idx[0], "Fee (₹)"] = str(edit_cfee)
                                    st.session_state["courses_df"].loc[match_idx[0], "Description"] = edit_cdesc
                                    save_data(st.session_state["courses_df"], COURSES_FILE, "courses_db", "courses_df")
                                    st.markdown(f'<div class="green-badge">✅ Course "{edit_cname}" Updated Successfully!</div>', unsafe_allow_html=True)
                                    st.rerun()
                else:
                    st.info("No courses available to edit.")
                    
            st.write("---")
            st.markdown("#### 🗑️ Delete Course")
            if not courses_df.empty:
                col_d1, col_d2 = st.columns([3, 1])
                with col_d1:
                    del_c_sel = st.selectbox("Select Course to Delete:", courses_df["Course Name"].tolist(), key="del_c_box")
                with col_d2:
                    st.write("<br>", unsafe_allow_html=True)
                    if st.button("🔴 Delete Selected Course", key="del_c_btn_main"):
                        st.session_state["courses_df"] = st.session_state["courses_df"][st.session_state["courses_df"]["Course Name"] != del_c_sel]
                        save_data(st.session_state["courses_df"], COURSES_FILE, "courses_db", "courses_df")
                        st.markdown(f'<div class="pink-badge">🗑️ Course "{del_c_sel}" Deleted Successfully!</div>', unsafe_allow_html=True)
                        st.rerun()

        # 9. CHANGE PASSWORDS
        with adm_tab9:
            st.subheader("🔑 Change Portal Passwords")
            with st.form("pwd_change_form"):
                new_adm_pwd = st.text_input("New Director Admin Password:", value=ADMIN_PWD)
                new_tch_pwd = st.text_input("New Teacher Portal Password:", value=TEACHER_PWD)
                
                if st.form_submit_button("🟢 Update Passwords"):
                    st.session_state["creds_df"] = pd.DataFrame([
                        {"Role": "Admin", "Password": new_adm_pwd},
                        {"Role": "Teacher", "Password": new_tch_pwd}
                    ])
                    save_data(st.session_state["creds_df"], CREDS_FILE, "creds_db", "creds_df")
                    st.markdown('<div class="green-badge">✅ Passwords Updated Successfully!</div>', unsafe_allow_html=True)
                    st.rerun()

# -------------------------------------------------------------
# FOOTER
# -------------------------------------------------------------
st.markdown("""
<div style="text-align:center; padding:20px; font-size:12px; color:#64748B; border-top:1px solid #CBD5E1; margin-top:40px;">
Official Enterprise Management System | Soft Tech Computers & ZTC Enterprise © 2026<br>
An ISO 9001:2015 Certified Institution | Center Code: 4159 | Kamarchuburi, Near Thelamara, Sonitpur, Assam - 784149
</div>
""", unsafe_allow_html=True)
