import streamlit as st
import pandas as pd
import os
import datetime
import pytz
import base64
import requests
import json
import threading

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
PHOTO_DIR = "student_photos"

os.makedirs(PHOTO_DIR, exist_ok=True)

# -------------------------------------------------------------
# BACKGROUND THREADING FOR CLOUD SYNC (0-LAG PERFORMANCE)
# -------------------------------------------------------------
def push_to_cloud_async(payload):
    def _worker():
        try:
            requests.post(GSHEET_WEBAPP_URL, data=json.dumps(payload), headers={"Content-Type": "application/json"}, timeout=8, allow_redirects=True)
        except Exception:
            pass
    t = threading.Thread(target=_worker)
    t.daemon = True
    t.start()

def load_data(file_path, columns, sheet_name=None):
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path, dtype=str)
            for col in columns:
                if col not in df.columns: df[col] = ""
            return df
        except Exception:
            pass
    return pd.DataFrame(columns=columns)

def save_data(df, file_path, sheet_name=None):
    df.to_csv(file_path, index=False)
    if GSHEET_WEBAPP_URL and sheet_name:
        records = [df.columns.tolist()] + df.fillna("").values.tolist()
        payload = {"action": "overwrite", "sheet_name": sheet_name, "rows": records}
        push_to_cloud_async(payload)

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

# Columns definitions
student_cols = ["Sl. No.", "Student ID", "Name", "Father Name", "Mother Name", "Gender", "DOB", "Caste", "Mobile No", "Vill Town", "PO", "PS", "PIN Code", "District", "Full Address", "Course", "Duration", "Days_Batch", "Session", "Join Date", "Validity Date", "Total Fee", "Discount", "Net Fee", "Shift", "Batch Time", "Photo Path", "Status", "Stage_Admission", "Stage_IDCard", "Stage_Registration", "Stage_ExamForm", "Stage_AdmitCard", "Stage_Certificate"]
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

# Load Data
student_df = load_data(STUDENT_MASTER_FILE, student_cols, "students_db")
fee_df = load_data(FEE_LOG_FILE, fee_cols, "fees_db")
att_df = load_data(ATTENDANCE_FILE, attendance_cols, "attendance_db")
teacher_df = load_data(TEACHERS_FILE, teacher_cols, "teachers_db")
teacher_att_df = load_data(TEACHER_ATT_FILE, teacher_att_cols, "teacher_attendance")
enquiry_df = load_data(ENQUIRY_FILE, enquiry_cols, "enquiries_db")
sfpc_df = load_data(SFPC_FILE, sfpc_cols, "sfpc_db")
creds_df = load_data(CREDS_FILE, creds_cols, "creds_db")
feedback_df = load_data(FEEDBACK_FILE, feedback_cols, "feedback_db")
syllabus_df = load_data(SYLLABUS_LOG_FILE, syllabus_cols, "syllabus_logs")
marks_df = load_data(MARKS_FILE, marks_cols, "marks_db")
notices_df = load_data(NOTICES_FILE, notices_cols, "notices_db")
tasks_df = load_data(TASKS_FILE, tasks_cols, "tasks_db")
pc_alloc_df = load_data(PC_ALLOC_FILE, pc_alloc_cols, "pc_alloc_db")
weak_notes_df = load_data(WEAK_NOTES_FILE, weak_notes_cols, "weak_notes_db")
exam_forms_df = load_data(EXAM_FORMS_FILE, exam_forms_cols, "exam_forms_db")
courses_df = load_data(COURSES_FILE, courses_cols, "courses_db")

# Initialize Default Courses if empty
if courses_df.empty:
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
    courses_df = pd.DataFrame(default_courses)
    save_data(courses_df, COURSES_FILE, "courses_db")

# Initialize Default Teachers if empty
if teacher_df.empty:
    default_teachers = [
        {"Teacher ID": "TCH-01", "Name": "Chiranjeeb Hazarika", "Phone": "9101026718", "Qualification": "Director / Master Trainer", "Designation": "Director", "Shift Assigned": "All Shifts"},
        {"Teacher ID": "TCH-02", "Name": "Senior Faculty", "Phone": "9876543210", "Qualification": "MCA / PGDCA", "Designation": "Instructor", "Shift Assigned": "Morning, Afternoon, Evening"}
    ]
    teacher_df = pd.DataFrame(default_teachers)
    save_data(teacher_df, TEACHERS_FILE, "teachers_db")

if creds_df.empty:
    creds_df = pd.DataFrame([
        {"Role": "Admin", "Password": "zaan123"},
        {"Role": "Teacher", "Password": "teacher123"}
    ])
    save_data(creds_df, CREDS_FILE, "creds_db")

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
        color: #DB2777;
        border: 1px solid #F472B6;
        padding: 10px 15px;
        border-radius: 8px;
        font-weight: 600;
        margin-bottom: 12px;
    }
    .green-badge {
        background: #DCFCE7;
        color: #15803D;
        border: 1px solid #4ADE80;
        padding: 10px 15px;
        border-radius: 8px;
        font-weight: 600;
        margin-bottom: 12px;
    }

    div.stButton > button {
        background-color: #0284C7 !important;
        color: white !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        border: none !important;
    }
    div.stButton > button:hover {
        background-color: #0369A1 !important;
    }
</style>
""", unsafe_allow_html=True)

# Top Header Bar
st.markdown("""
<div class="udise-topbar">
    <div class="udise-logo">
        STC-ZTC+ <span>Enterprise Management Portal</span>
    </div>
    <div style="display:flex; align-items:center; gap:15px;">
        <span style="font-size:12px; color:#94A3B8;">Academic Year: 2026-27</span>
        <div class="udise-user-badge">
            👤 Chiranjeeb Hazarika (DIRECTOR / ADMIN)
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Institutional Header Strip (No student counts on public strip)
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
    if dp2_b64:
        st.markdown(f'<img src="{dp2_b64}" style="width:100%; max-height:240px; object-fit:contain; border-radius:10px; margin-bottom:15px; border:1px solid #CBD5E1;">', unsafe_allow_html=True)
        
    st.markdown('<h4 style="color:#0F172A; margin:0 0 15px 0;">⚡ Institutional Overview & Services</h4>', unsafe_allow_html=True)
    
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1:
        st.metric("Institutional Certification", "ISO 9001:2015")
    with col_s2:
        st.metric("Center Code", "4159 (Assam)")
    with col_s3:
        st.metric("Alumni Network", "350+ Students")
    with col_s4:
        st.metric("Govt Approved Courses", f"{len(courses_df)} Available")
        
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
        
        # PUBLIC ADMISSION & FEE ENQUIRY DESK
        with st.expander("📝 Click here to Submit Public Admission / Course Fee Enquiry", expanded=True):
            with st.form("public_enquiry_form", clear_on_submit=True):
                e_name = st.text_input("Candidate Full Name*")
                e_mobile = st.text_input("Mobile Number (WhatsApp Enabled)*")
                e_vill = st.text_input("Village / Town / Address*")
                
                course_list = courses_df["Course Name"].tolist() if not courses_df.empty else []
                e_course = st.selectbox("Select Interested Course:*", course_list)
                
                if st.form_submit_button("Submit Enquiry & Check Course Fee"):
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
                        enquiry_df = pd.concat([enquiry_df, pd.DataFrame([enq_row])], ignore_index=True)
                        save_data(enquiry_df, ENQUIRY_FILE, "enquiries_db")
                        
                        st.markdown(f"""
                        <div class="pink-badge">
                            🎉 <b>Enquiry Submitted Successfully!</b><br>
                            <b>Selected Course:</b> {e_course}<br>
                            <b>Duration:</b> {c_dur} | <b>Official Total Course Fee:</b> ₹{c_fee}<br>
                            <i>Our academy office will contact you on {e_mobile} shortly!</i>
                        </div>
                        """, unsafe_allow_html=True)

    with col_r:
        st.markdown("""
        <div class="support-card">
            <div style="font-size:14px; font-weight:700; color:#38BDF8; display:flex; align-items:center; gap:8px;">
                📞 Center Support & Helplines
            </div>
            <div class="support-item">
                <div>
                    <b>Director / Head MIS</b><br>
                    <span style="color:#94A3B8; font-size:11px;">Chiranjeeb Hazarika</span>
                </div>
                <div style="color:#38BDF8; font-weight:bold;">9101026718</div>
            </div>
            <div class="support-item">
                <div>
                    <b>Helpdesk / Center Location</b><br>
                    <span style="color:#94A3B8; font-size:11px;">Kamarchuburi, Sonitpur</span>
                </div>
                <div style="color:#10B981; font-weight:bold;">PIN: 784149</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    
    # PRIVACY PROTECTED MASTER DIRECTORY
    st.subheader("🔒 Master Student Directory (Authorized Access Only)")
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
                <p style="margin:4px 0 0 0; font-size:13px; color:#15803D;">Center: Soft Tech Computers & ZTC (Code: 4159) | Status: {v_data['Status']}</p>
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
                        "Stage_Admission": "Completed", "Stage_IDCard": "Generated", "Stage_Registration": "Pending",
                        "Stage_ExamForm": "Pending", "Stage_AdmitCard": "Pending", "Stage_Certificate": "Pending"
                    }
                    student_df = pd.concat([student_df, pd.DataFrame([new_row])], ignore_index=True)
                    save_data(student_df, STUDENT_MASTER_FILE, "students_db")
                    st.balloons()
                    st.markdown(f"""
                    <div class="green-badge">
                        🎉 <b>Candidate Registered Successfully!</b> Student ID: <b>{next_id}</b>
                    </div>
                    """, unsafe_allow_html=True)
                    st.rerun()

# -------------------------------------------------------------
# 4. STUDENT LOGIN PORTAL
# -------------------------------------------------------------
elif menu == "🔑 Student Login Portal":
    st.header("🔑 Student Individual Dashboard")
    if "student_logged_in" not in st.session_state:
        st.session_state["student_logged_in"] = False
        st.session_state["logged_student_id"] = ""

    if not st.session_state["student_logged_in"]:
        col_l1, col_l2 = st.columns(2)
        with col_l1:
            s_id_in = st.text_input("Enter Student Roll ID:").strip().upper()
        with col_l2:
            s_pwd_in = st.text_input("Enter Password (Mobile No):", type="password").strip()
            
        if st.button("Login To Dashboard"):
            st_data = student_df[(student_df["Student ID"] == s_id_in) & (student_df["Mobile No"] == s_pwd_in)]
            if not st_data.empty:
                st.session_state["student_logged_in"] = True
                st.session_state["logged_student_id"] = s_id_in
                st.rerun()
            else:
                st.error("Invalid Roll ID or Mobile Number!")
    else:
        s_id = st.session_state["logged_student_id"]
        s = student_df[student_df["Student ID"] == s_id].iloc[0]
        st.markdown(f"""
        <div class="green-badge">
            Welcome back, <b>{s['Name']}</b> (Roll ID: {s['Student ID']})
        </div>
        """, unsafe_allow_html=True)
        
        p_logs = fee_df[fee_df["Student ID"] == s_id]
        tot_paid = sum([float(amt) for amt in p_logs["Amount Paid"] if amt])
        net_f = float(s["Net Fee"]) if s["Net Fee"] else 0.0
        due_f = net_f - tot_paid
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Course Enrolled", s["Course"])
        c2.metric("Total Fee Paid", f"₹{tot_paid:.2f}")
        c3.metric("Balance Due", f"₹{due_f:.2f}")
        
        if not p_logs.empty:
            st.subheader("🧾 Fee Receipts & Payment Logs")
            st.dataframe(p_logs[["Receipt No", "Date", "Amount Paid", "Payment Mode", "Collected_By"]], use_container_width=True)
            
        if st.button("🔒 Logout"):
            st.session_state["student_logged_in"] = False
            st.session_state["logged_student_id"] = ""
            st.rerun()

# -------------------------------------------------------------
# 5. SUNDAY FREE PRACTICE CLASS (SFPC) - PROTECTED WITH ID & PASSWORD
# -------------------------------------------------------------
elif menu == "🎯 Sunday Free Practice Class (SFPC)":
    st.header("🎯 Sunday Free Practice Class (SFPC) Desk")
    tab_sf1, tab_sf2 = st.tabs(["🔒 Student Eligibility & Fee Summary", "📝 Staff SFPC Lab Entry Log"])
    
    with tab_sf1:
        st.subheader("🔑 Check SFPC Eligibility & Account Summary")
        st.info("ℹ️ Enter your official **Roll ID** and **Password (Registered Mobile No)** to verify access.")
        
        col_sf_id, col_sf_pwd = st.columns(2)
        with col_sf_id:
            sf_id = st.text_input("Enter Student Roll ID (e.g. STC26-001):", key="sf_user_id").strip().upper()
        with col_sf_pwd:
            sf_pwd = st.text_input("Enter Password (Registered Mobile No):", type="password", key="sf_user_pwd").strip()
            
        if st.button("🔓 Check My SFPC Eligibility Now", use_container_width=True):
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
                    
                    # Attendance calculation
                    s_att = att_df[att_df["Student ID"] == sf_id]
                    tot_classes = len(s_att)
                    present_classes = len(s_att[s_att["Status"].isin(["Present", "Late"])])
                    att_pct = (present_classes / tot_classes * 100) if tot_classes > 0 else 100.0
                    
                    # SFPC Eligibility Rules:
                    # 1. Admission Fee min ₹999 paid
                    cond1 = tot_paid >= 999.0
                    # 2. At least 50% of total course fee paid
                    fee_pct = (tot_paid / net_f * 100) if net_f > 0 else 100.0
                    cond2 = fee_pct >= 50.0
                    # 3. Attendance >= 75%
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
                
                if st.form_submit_button("Record Sunday Practice Entry"):
                    if sf_sid:
                        sid_val = sf_sid.split(" - ")[0]
                        sname_val = sf_sid.split(" - ")[1]
                        new_sf = {
                            "Date": str(datetime.date.today()), "Student ID": sid_val,
                            "Student Name": sname_val, "PC Machine No": pc_no,
                            "Topic Practiced": sf_topic, "Teacher Incharge": sf_teacher
                        }
                        sfpc_df = pd.concat([sfpc_df, pd.DataFrame([new_sf])], ignore_index=True)
                        save_data(sfpc_df, SFPC_FILE, "sfpc_db")
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
                
                if st.form_submit_button("Issue Receipt & Save Deposit"):
                    rc_num = f"REC-{datetime.date.today().strftime('%Y%m%d')}-{len(fee_df)+1:03d}"
                    f_row = {"Receipt No": rc_num, "Student ID": sid, "Date": str(datetime.date.today()), "Amount Paid": str(pay_amt), "Payment Mode": pay_mode, "Collected_By": collector_nm, "Remarks": remarks}
                    fee_df = pd.concat([fee_df, pd.DataFrame([f_row])], ignore_index=True)
                    save_data(fee_df, FEE_LOG_FILE, "fees_db")
                    st.markdown(f"""
                    <div class="green-badge">
                        🧾 <b>Money Receipt Issued!</b> Receipt No: <b>{rc_num}</b> | Amount: <b>₹{pay_amt}</b>
                    </div>
                    """, unsafe_allow_html=True)
                    st.rerun()

# -------------------------------------------------------------
# 7. TEACHER PORTAL & ATTENDANCE WITH LATE PENALTY & SALARY FORMULA
# -------------------------------------------------------------
elif menu == "🔑 Teacher Portal & Attendance":
    st.header("🔑 Faculty / Teacher Desk & Shift Punching")
    t_pwd = st.text_input("Enter Teacher Portal Password:", type="password", key="t_desk_pwd")
    if t_pwd in [ADMIN_PWD, TEACHER_PWD]:
        st.success("Authorized Faculty Access Granted!")
        t_tab1, t_tab2, t_tab3, t_tab4, t_tab5 = st.tabs([
            "⏰ Teacher Self Attendance & Salary Punch",
            "📸 Student Attendance (IST)",
            "📚 Syllabus Coverage (Multi-Topic)",
            "💻 PC Lab Allocation",
            "📝 Daily Student Tasks"
        ])
        
        # 1. TEACHER SELF PUNCH WITH LATE DEDUCTION & EARNING
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
            
            # Late Check Calculation based on 90 mins shift
            shift_start_mins = 6 * 60 + 30 if "Morning" in t_shift_sel else (16 * 60 if "Afternoon" in t_shift_sel else 17 * 60 + 30)
            current_mins = now_ist.hour * 60 + now_ist.minute
            late_by = max(0, current_mins - shift_start_mins)
            is_late = late_by > 5  # 5 min grace period
            
            # Base per batch: 230 / 3 = 76.67. Per min rate: 230 / 270 = 0.85185
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
                    teacher_att_df = pd.concat([teacher_att_df, pd.DataFrame([new_t_att])], ignore_index=True)
                    save_data(teacher_att_df, TEACHER_ATT_FILE, "teacher_attendance")
                    
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
                    idx = teacher_att_df[(teacher_att_df["Date"] == today_str) & (teacher_att_df["Name"] == t_name_sel)].index
                    if len(idx) > 0:
                        teacher_att_df.loc[idx[-1], "Time_Out"] = time_out_str
                        teacher_att_df.loc[idx[-1], "Remarks"] = "Completed"
                        save_data(teacher_att_df, TEACHER_ATT_FILE, "teacher_attendance")
                        st.markdown(f'<div class="green-badge">✅ Punched OUT at {time_out_str}!</div>', unsafe_allow_html=True)
                    else:
                        st.warning("No Punch IN record found for today to punch out.")
                    st.rerun()
                    
            if not teacher_att_df.empty:
                st.write("**Recent Teacher Punch & Earning Records:**")
                st.dataframe(teacher_att_df.tail(10), use_container_width=True)

        # 2. STUDENT ATTENDANCE
        with t_tab2:
            st.subheader("Student Daily Attendance (IST Recorded)")
            with st.form("student_att_form", clear_on_submit=True):
                att_sid = st.selectbox("Select Student:", student_df["Student ID"] + " - " + student_df["Name"]) if not student_df.empty else None
                att_status = st.selectbox("Attendance Status:", ["Present", "Absent", "Late", "Excused"])
                if st.form_submit_button("Mark Student Attendance"):
                    if att_sid:
                        s_id_val = att_sid.split(" - ")[0]
                        now_time_ist = datetime.datetime.now(IST).strftime("%I:%M %p")
                        att_row = {
                            "Student ID": s_id_val, "Date": str(datetime.date.today()),
                            "Time_In": now_time_ist, "Status": att_status,
                            "Late_Reason": "", "Sign_Mode": "Manual/QR", "Location_Verified": "Classroom"
                        }
                        att_df = pd.concat([att_df, pd.DataFrame([att_row])], ignore_index=True)
                        save_data(att_df, ATTENDANCE_FILE, "attendance_db")
                        st.markdown(f'<div class="green-badge">✅ Attendance marked {att_status} for {att_sid} at {now_time_ist}!</div>', unsafe_allow_html=True)
                        st.rerun()
            if not att_df.empty:
                st.dataframe(att_df.tail(15), use_container_width=True)

        # 3. MULTI-TOPIC SYLLABUS COVERAGE
        with t_tab3:
            st.subheader("Record Daily Syllabus Coverage (Multi-Select Allowed)")
            with st.form("syl_multi_form", clear_on_submit=True):
                syl_course = st.selectbox("Course:", courses_df["Course Name"].tolist() if not courses_df.empty else [])
                syl_topics = st.multiselect("Topics Covered in Today's Class:*", ALL_SYLLABUS_TOPICS, default=[ALL_SYLLABUS_TOPICS[0]])
                syl_type = st.selectbox("Session Type:", ["Theory Lecture", "Practical Lab Training", "Weekly Revision", "Class Test / Viva"])
                syl_teacher = st.selectbox("Teacher Incharge:", teacher_df["Name"].tolist() if not teacher_df.empty else ["Director Chiranjeeb Hazarika"])
                
                if st.form_submit_button("Save Daily Syllabus Coverage"):
                    if syl_topics:
                        topics_str = ", ".join(syl_topics)
                        s_row = {"Date": str(datetime.date.today()), "Course": syl_course, "Topics Covered": topics_str, "Class Type": syl_type, "Teacher Incharge": syl_teacher}
                        syllabus_df = pd.concat([syllabus_df, pd.DataFrame([s_row])], ignore_index=True)
                        save_data(syllabus_df, SYLLABUS_LOG_FILE, "syllabus_logs")
                        st.markdown(f'<div class="green-badge">✅ Syllabus entry saved: <b>{topics_str}</b></div>', unsafe_allow_html=True)
                        st.rerun()
                    else:
                        st.error("Please select at least one topic!")
            if not syllabus_df.empty:
                st.dataframe(syllabus_df.tail(10), use_container_width=True)

        # 4. PC ALLOCATION
        with t_tab4:
            st.subheader("Daily Computer Machine Allocation")
            with st.form("pc_alloc_form", clear_on_submit=True):
                pc_sid = st.selectbox("Student:", student_df["Student ID"] + " - " + student_df["Name"], key="pc_s_sel") if not student_df.empty else None
                m_no = st.selectbox("Machine / PC No:", [f"PC-{i:02d}" for i in range(1, 21)])
                pc_shift = st.selectbox("Shift Assigned:", ["Morning", "Afternoon", "Evening"])
                if st.form_submit_button("Assign Machine"):
                    if pc_sid:
                        pc_row = {"Date": str(datetime.date.today()), "Student ID": pc_sid.split(" - ")[0], "Student Name": pc_sid.split(" - ")[1], "PC Machine No": m_no, "Shift": pc_shift, "Teacher Incharge": "Faculty"}
                        pc_alloc_df = pd.concat([pc_alloc_df, pd.DataFrame([pc_row])], ignore_index=True)
                        save_data(pc_alloc_df, PC_ALLOC_FILE, "pc_alloc_db")
                        st.markdown(f'<div class="green-badge">✅ Machine {m_no} allocated to {pc_sid}!</div>', unsafe_allow_html=True)
                        st.rerun()

        # 5. TASKS
        with t_tab5:
            st.subheader("Assign Student Daily Tasks / Homework")
            with st.form("task_assign_form", clear_on_submit=True):
                t_sid = st.selectbox("Student:", student_df["Student ID"] + " - " + student_df["Name"], key="t_s_sel") if not student_df.empty else None
                task_txt = st.text_area("Practical Task / Assignment Details:")
                if st.form_submit_button("Assign Task"):
                    if t_sid and task_txt:
                        tsk_row = {"Date": str(datetime.date.today()), "Student ID": t_sid.split(" - ")[0], "Student Name": t_sid.split(" - ")[1], "Task Assigned": task_txt, "Status": "Assigned", "Teacher Incharge": "Faculty"}
                        tasks_df = pd.concat([tasks_df, pd.DataFrame([tsk_row])], ignore_index=True)
                        save_data(tasks_df, TASKS_FILE, "tasks_db")
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
        adm_tab1, adm_tab2, adm_tab3, adm_tab4, adm_tab5, adm_tab6, adm_tab7 = st.tabs([
            "📋 Student Edit / Delete",
            "👨‍🏫 Teacher Management",
            "💰 Dues & Balance Ledger",
            "📖 Class Logs & Activity Review",
            "📚 Course & Fee Settings",
            "🔑 Change Passwords",
            "🗑️ Danger Zone"
        ])
        
        # 1. STUDENT EDIT & DELETE
        with adm_tab1:
            st.subheader("📋 Student Master Management (Edit / Delete)")
            if not student_df.empty:
                st.dataframe(student_df[["Student ID", "Name", "Mobile No", "Course", "Net Fee", "Join Date", "Status"]], use_container_width=True)
                
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
                            
                        if st.form_submit_button("Update Student Record"):
                            student_df.loc[student_df["Student ID"] == e_sid, "Name"] = new_name.upper()
                            student_df.loc[student_df["Student ID"] == e_sid, "Mobile No"] = new_mobile
                            student_df.loc[student_df["Student ID"] == e_sid, "Net Fee"] = new_fee
                            student_df.loc[student_df["Student ID"] == e_sid, "Course"] = new_course
                            student_df.loc[student_df["Student ID"] == e_sid, "Status"] = new_status
                            save_data(student_df, STUDENT_MASTER_FILE, "students_db")
                            st.markdown('<div class="green-badge">✅ Student Record Updated Successfully!</div>', unsafe_allow_html=True)
                            st.rerun()
                            
                    if st.button("🔴 Delete This Student Completely", key="del_s_btn"):
                        student_df = student_df[student_df["Student ID"] != e_sid]
                        save_data(student_df, STUDENT_MASTER_FILE, "students_db")
                        st.markdown(f'<div class="pink-badge">🗑️ Student {e_sid} Deleted Completely!</div>', unsafe_allow_html=True)
                        st.rerun()
            else:
                st.info("No student records found.")

        # 2. TEACHER MANAGEMENT
        with adm_tab2:
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
                    
                    if st.form_submit_button("Add Teacher"):
                        if t_nname:
                            new_t_row = {"Teacher ID": t_nid, "Name": t_nname, "Phone": t_nphone, "Qualification": t_nqual, "Designation": t_ndesig, "Shift Assigned": t_nshift}
                            teacher_df = pd.concat([teacher_df, pd.DataFrame([new_t_row])], ignore_index=True)
                            save_data(teacher_df, TEACHERS_FILE, "teachers_db")
                            st.markdown(f'<div class="green-badge">✅ Faculty {t_nname} Added Successfully!</div>', unsafe_allow_html=True)
                            st.rerun()
                            
            with col_t2:
                st.write("**🗑️ Remove Faculty:**")
                if not teacher_df.empty:
                    del_t_name = st.selectbox("Select Teacher to Remove:", teacher_df["Name"].tolist())
                    if st.button("Delete Selected Teacher", key="del_t_btn"):
                        teacher_df = teacher_df[teacher_df["Name"] != del_t_name]
                        save_data(teacher_df, TEACHERS_FILE, "teachers_db")
                        st.markdown(f'<div class="pink-badge">🗑️ Teacher {del_t_name} Removed!</div>', unsafe_allow_html=True)
                        st.rerun()

        # 3. DUES & BALANCE LEDGER
        with adm_tab3:
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

        # 4. CLASS LOGS & TEACHER EARNINGS REVIEW
        with adm_tab4:
            st.subheader("📖 Daily Teacher Activities, Attendance & Earnings")
            c_sub1, c_sub2, c_sub3, c_sub4 = st.tabs(["⏰ Teacher Attendance & Earnings", "📚 Syllabus Covered", "💻 PC Allocations", "📝 Tasks Assigned"])
            
            with c_sub1:
                if not teacher_att_df.empty:
                    st.dataframe(teacher_att_df, use_container_width=True)
                else:
                    st.info("No teacher attendance punched yet.")
            with c_sub2:
                if not syllabus_df.empty:
                    st.dataframe(syllabus_df, use_container_width=True)
                else:
                    st.info("No syllabus logs recorded yet.")
            with c_sub3:
                if not pc_alloc_df.empty:
                    st.dataframe(pc_alloc_df, use_container_width=True)
                else:
                    st.info("No PC allocations recorded.")
            with c_sub4:
                if not tasks_df.empty:
                    st.dataframe(tasks_df, use_container_width=True)
                else:
                    st.info("No tasks recorded.")

        # 5. COURSE & FEE SETTINGS
        with adm_tab5:
            st.subheader("📚 Course & Fee Master Settings (Add / Edit / Remove)")
            st.dataframe(courses_df, use_container_width=True)
            
            col_cadd, col_cdel = st.columns(2)
            with col_cadd:
                st.write("**➕ Add / Update Course:**")
                with st.form("course_add_form", clear_on_submit=True):
                    c_nname = st.text_input("Course Name / Title*")
                    c_ndur = st.selectbox("Duration", ["12 Months", "6 Months", "3 Months", "2 Months", "45 Days"])
                    c_nfee = st.number_input("Course Fee (₹)*", min_value=100.0, value=2500.0, step=100.0)
                    c_ndesc = st.text_input("Topics / Description")
                    
                    if st.form_submit_button("Save Course"):
                        if c_nname:
                            if c_nname in courses_df["Course Name"].values:
                                courses_df.loc[courses_df["Course Name"] == c_nname, "Duration"] = c_ndur
                                courses_df.loc[courses_df["Course Name"] == c_nname, "Fee (₹)"] = str(c_nfee)
                                courses_df.loc[courses_df["Course Name"] == c_nname, "Description"] = c_ndesc
                            else:
                                new_c_row = {"Course Name": c_nname, "Duration": c_ndur, "Fee (₹)": str(c_nfee), "Description": c_ndesc}
                                courses_df = pd.concat([courses_df, pd.DataFrame([new_c_row])], ignore_index=True)
                            save_data(courses_df, COURSES_FILE, "courses_db")
                            st.markdown('<div class="green-badge">✅ Course Master Settings Saved!</div>', unsafe_allow_html=True)
                            st.rerun()
                            
            with col_cdel:
                st.write("**🗑️ Delete Course:**")
                del_c_sel = st.selectbox("Select Course to Remove:", courses_df["Course Name"].tolist() if not courses_df.empty else [])
                if st.button("Delete Selected Course", key="del_c_btn"):
                    courses_df = courses_df[courses_df["Course Name"] != del_c_sel]
                    save_data(courses_df, COURSES_FILE, "courses_db")
                    st.markdown(f'<div class="pink-badge">🗑️ Course {del_c_sel} Removed!</div>', unsafe_allow_html=True)
                    st.rerun()

        # 6. CHANGE PASSWORDS
        with adm_tab6:
            st.subheader("🔑 Change Portal Passwords")
            with st.form("pwd_change_form"):
                new_adm_pwd = st.text_input("New Director Admin Password:", value=ADMIN_PWD)
                new_tch_pwd = st.text_input("New Teacher Portal Password:", value=TEACHER_PWD)
                
                if st.form_submit_button("Update Passwords"):
                    creds_df = pd.DataFrame([
                        {"Role": "Admin", "Password": new_adm_pwd},
                        {"Role": "Teacher", "Password": new_tch_pwd}
                    ])
                    save_data(creds_df, CREDS_FILE, "creds_db")
                    st.markdown('<div class="green-badge">✅ Passwords Updated Successfully!</div>', unsafe_allow_html=True)
                    st.rerun()

        # 7. DANGER ZONE
        with adm_tab7:
            st.warning("⚠️ Danger Zone: Clear entire local and cloud database.")
            if st.checkbox("Confirm Reset"):
                if st.button("🔴 RESET ALL MASTER DATA"):
                    student_df = pd.DataFrame(columns=student_cols)
                    fee_df = pd.DataFrame(columns=fee_cols)
                    att_df = pd.DataFrame(columns=attendance_cols)
                    save_data(student_df, STUDENT_MASTER_FILE, "students_db")
                    save_data(fee_df, FEE_LOG_FILE, "fees_db")
                    save_data(att_df, ATTENDANCE_FILE, "attendance_db")
                    st.success("Database Reset Completed!")
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
