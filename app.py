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
teacher_att_cols = ["Teacher ID", "Name", "Date", "Time_In", "Time_Out", "Shift", "Status", "Late_Mins", "Penalty_Deduction", "Net_Earning_Today"]
enquiry_cols = ["Date", "Name", "Mobile", "Course Interested", "Is ZTC Student", "Village/Address", "Status"]
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

if creds_df.empty:
    creds_df = pd.DataFrame([
        {"Role": "Admin", "Password": "zaan123"},
        {"Role": "Teacher", "Password": "teacher123"}
    ])
    save_data(creds_df, CREDS_FILE, "creds_db")

ADMIN_PWD = creds_df[creds_df["Role"] == "Admin"]["Password"].values[0] if "Admin" in creds_df["Role"].values else "zaan123"
TEACHER_PWD = creds_df[creds_df["Role"] == "Teacher"]["Password"].values[0] if "Teacher" in creds_df["Role"].values else "teacher123"

COURSE_CONFIG = {
    "PGDCA (Post Graduate Diploma in Computer Application)": {"Months": 12, "FeeNum": 8500, "FeeStr": "₹8,500 Total"},
    "ADCA (Advanced Diploma in Computer Application)": {"Months": 12, "FeeNum": 7500, "FeeStr": "₹7,500 Total"},
    "DCA (Diploma in Computer Application)": {"Months": 6, "FeeNum": 4500, "FeeStr": "₹4,500 Total"},
    "DTP (Desktop Publishing)": {"Months": 3, "FeeNum": 3500, "FeeStr": "₹3,500 Total"},
    "Tally Prime with GST": {"Months": 3, "FeeNum": 4000, "FeeStr": "₹4,000 Total"},
    "Certificate Course in Computer Basics": {"Months": 3, "FeeNum": 2500, "FeeStr": "₹2,500 Total"},
    "Class 9 English Coaching": {"Months": 12, "FeeNum": 600, "FeeStr": "₹600 / Month"},
    "Class 10 English Coaching": {"Months": 12, "FeeNum": 700, "FeeStr": "₹700 / Month"},
    "Class 11 English Coaching": {"Months": 12, "FeeNum": 800, "FeeStr": "₹800 / Month"},
    "Class 12 English Coaching": {"Months": 12, "FeeNum": 900, "FeeStr": "₹900 / Month"}
}

ALL_SYLLABUS_TOPICS = [
    "Computer Basics / Fundamentals", "Paint / Notepad / Wordpad", "MS Word", "MS Excel", 
    "MS Powerpoint", "MS Access", "Tally Prime with GST", "Photoshop", "Pagemaker", 
    "CorelDraw", "HTML / Web Design", "Python Programming", "Internet & Cyber Security", 
    "Assamese Typesetting", "English Grammar", "English Literature Prose/Poetry", "Exam Taken"
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
        transition: all 0.2s ease;
    }
    .action-box:hover {
        border-color: #0284C7;
        box-shadow: 0 4px 10px rgba(2, 132, 199, 0.15);
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
    .action-title {
        font-size: 15px;
        font-weight: 700;
        color: #0F172A;
        margin: 0;
    }
    .action-sub {
        font-size: 12px;
        color: #64748B;
        margin: 2px 0 0 0;
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

# Top UDISE+ Govt Header Bar
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

# School Info Strip
total_students_count = len(student_df)
st.markdown(f"""
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
            <div style="font-size:12px; color:#64748B;">👥 Enrolled Trainees:</div>
            <div style="font-size:15px; font-weight:700; color:#10B981;">{total_students_count} Active Candidates</div>
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
    "🔑 Teacher Portal & QR Scanner",
    "🔐 Admin Control Panel"
])

# -------------------------------------------------------------
# 1. QUICK ACTIONS & PRIVACY DASHBOARD
# -------------------------------------------------------------
if menu == "⚡ Quick Actions & Dashboard":
    dp2_b64 = get_image_base64("dp2")
    if dp2_b64:
        st.markdown(f'<img src="{dp2_b64}" style="width:100%; max-height:240px; object-fit:contain; border-radius:10px; margin-bottom:15px; border:1px solid #CBD5E1;">', unsafe_allow_html=True)
        
    st.markdown('<h4 style="color:#0F172A; margin:0 0 15px 0;">⚡ Institutional Overview & Analytics</h4>', unsafe_allow_html=True)
    
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1:
        st.metric("Total Enrolled Candidates", f"{len(student_df)} Students")
    with col_s2:
        active_count = len(student_df[student_df["Status"] == "Active"]) if "Status" in student_df.columns else len(student_df)
        st.metric("Active Ongoing Batches", f"{active_count} Trainees")
    with col_s3:
        st.metric("Alumni Network", "350+ Students")
    with col_s4:
        st.metric("Certified Graduates", "200+ Certified")
        
    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_r = st.columns([2, 1])
    
    with col_l:
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("""
            <div class="action-box">
                <div class="action-icon">📊</div>
                <div>
                    <div class="action-title">Candidate Directory</div>
                    <div class="action-sub">Protected master student database</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="action-box">
                <div class="action-icon">💳</div>
                <div>
                    <div class="action-title">Fee Ledger Desk</div>
                    <div class="action-sub">Confidential money receipts & dues</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_b:
            st.markdown("""
            <div class="action-box">
                <div class="action-icon">📝</div>
                <div>
                    <div class="action-title">Candidate Admission DCF</div>
                    <div class="action-sub">Register new applicant form</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="action-box">
                <div class="action-icon">📜</div>
                <div>
                    <div class="action-title">Certificate Verification</div>
                    <div class="action-sub">Verify authentic Sarva India records</div>
                </div>
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
    st.subheader("🔒 Master Student Records (Authorized Staff Access Only)")
    with st.expander("🔑 Click to Unlock Full Student Database (Password Required)", expanded=False):
        view_pwd = st.text_input("Enter Staff / Director Password:", type="password", key="dash_view_pwd")
        if view_pwd in [ADMIN_PWD, TEACHER_PWD]:
            st.success("Access Granted! Live Master Records:")
            if not student_df.empty:
                st.dataframe(student_df, use_container_width=True)
            else:
                st.info("No records found in database.")
        elif view_pwd:
            st.error("Incorrect Password! Access denied for privacy reasons.")
        else:
            st.info("Personal contact numbers, addresses, and fees are protected. Enter password to view.")

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
            <div style="background:#ECFDF5; border:1.5px solid #10B981; border-radius:8px; padding:18px; color:#065F46;">
                <h3 style="margin:0; color:#047857;">✅ OFFICIAL RECORD VERIFIED</h3>
                <p style="margin:8px 0 0 0; font-size:15px;"><b>Candidate Name:</b> {v_data['Name']} | <b>Course:</b> {v_data['Course']} | <b>Reg ID:</b> {v_data['Student ID']}</p>
                <p style="margin:4px 0 0 0; font-size:13px; color:#047857;">Center: Soft Tech Computers & ZTC (Code: 4159) | Status: {v_data['Status']}</p>
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
                course = st.selectbox("Course Selected*", list(COURSE_CONFIG.keys()))
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
                    st.success(f"🎉 Registered Successfully! Student ID: {next_id}")
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
        st.success(f"Welcome, **{s['Name']}** ({s['Student ID']})")
        
        p_logs = fee_df[fee_df["Student ID"] == s_id]
        tot_paid = sum([float(amt) for amt in p_logs["Amount Paid"] if amt])
        net_f = float(s["Net Fee"]) if s["Net Fee"] else 0.0
        due_f = net_f - tot_paid
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Course", s["Course"])
        c2.metric("Total Fee Paid", f"₹{tot_paid:.2f}")
        c3.metric("Due Balance", f"₹{due_f:.2f}")
        
        if not p_logs.empty:
            st.subheader("🧾 Payment History")
            st.dataframe(p_logs[["Receipt No", "Date", "Amount Paid", "Payment Mode", "Collected_By"]], use_container_width=True)
            
        if st.button("🔒 Logout"):
            st.session_state["student_logged_in"] = False
            st.session_state["logged_student_id"] = ""
            st.rerun()

# -------------------------------------------------------------
# 5. SUNDAY FREE PRACTICE CLASS (SFPC)
# -------------------------------------------------------------
elif menu == "🎯 Sunday Free Practice Class (SFPC)":
    st.header("🎯 Sunday Free Practice Class (SFPC) Desk")
    
    tab_sf1, tab_sf2 = st.tabs(["🔍 Check Eligibility", "📝 SFPC Lab Entry Log"])
    
    with tab_sf1:
        sf_id = st.text_input("Enter Student ID to check Sunday Lab Eligibility:").strip().upper()
        if sf_id:
            st_res = student_df[student_df["Student ID"] == sf_id]
            if not st_res.empty:
                s = st_res.iloc[0]
                p_logs = fee_df[fee_df["Student ID"] == sf_id]
                tot_paid = sum([float(a) for a in p_logs["Amount Paid"] if a])
                net_f = float(s["Net Fee"]) if s["Net Fee"] else 2550.0
                cleared_pct = (tot_paid / net_f * 100) if net_f > 0 else 100
                is_ok = cleared_pct >= 50.0
                
                if is_ok:
                    st.success(f"✅ **ELIGIBLE FOR SUNDAY LAB!** Fee Paid: {cleared_pct:.1f}% (₹{tot_paid} / ₹{net_f})")
                else:
                    st.error(f"❌ **NOT ELIGIBLE!** Minimum 50% fee payment required. (Current: {cleared_pct:.1f}%)")
            else:
                st.error("Student ID not found.")
                
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
                        st.success("✅ SFPC Practice Session Saved!")
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
                
                if st.form_submit_button("Issue Receipt & Save Deposit"):
                    rc_num = f"REC-{datetime.date.today().strftime('%Y%m%d')}-{len(fee_df)+1:03d}"
                    f_row = {"Receipt No": rc_num, "Student ID": sid, "Date": str(datetime.date.today()), "Amount Paid": str(pay_amt), "Payment Mode": pay_mode, "Collected_By": collector_nm, "Remarks": "Fee Deposit"}
                    fee_df = pd.concat([fee_df, pd.DataFrame([f_row])], ignore_index=True)
                    save_data(fee_df, FEE_LOG_FILE, "fees_db")
                    st.success(f"✅ Receipt Issued: {rc_num}")
                    st.rerun()

# -------------------------------------------------------------
# 7. TEACHER PORTAL & QR SCANNER
# -------------------------------------------------------------
elif menu == "🔑 Teacher Portal & QR Scanner":
    st.header("🔑 Faculty / Teacher Desk & QR Attendance")
    t_pwd = st.text_input("Enter Teacher Portal Password:", type="password", key="t_desk_pwd")
    if t_pwd in [ADMIN_PWD, TEACHER_PWD]:
        st.success("Authorized Faculty Access!")
        t_tab1, t_tab2, t_tab3, t_tab4 = st.tabs(["📸 QR / Manual Attendance", "📚 Syllabus Coverage", "💻 PC Lab Allocation", "📝 Daily Student Task"])
        
        # 1. Attendance
        with t_tab1:
            st.subheader("Student Daily Attendance")
            with st.form("att_form", clear_on_submit=True):
                att_sid = st.selectbox("Select Student:", student_df["Student ID"] + " - " + student_df["Name"]) if not student_df.empty else None
                att_status = st.selectbox("Status:", ["Present", "Absent", "Late", "Excused"])
                if st.form_submit_button("Mark Attendance"):
                    if att_sid:
                        s_id_val = att_sid.split(" - ")[0]
                        now_time = datetime.datetime.now(IST).strftime("%I:%M %p")
                        att_row = {
                            "Student ID": s_id_val, "Date": str(datetime.date.today()),
                            "Time_In": now_time, "Status": att_status,
                            "Late_Reason": "", "Sign_Mode": "Manual/QR", "Location_Verified": "Classroom"
                        }
                        att_df = pd.concat([att_df, pd.DataFrame([att_row])], ignore_index=True)
                        save_data(att_df, ATTENDANCE_FILE, "attendance_db")
                        st.success(f"✅ Attendance recorded for {att_sid}!")
                        st.rerun()
            if not att_df.empty:
                st.dataframe(att_df.tail(15), use_container_width=True)

        # 2. Syllabus
        with t_tab2:
            st.subheader("Record Daily Syllabus Covered")
            with st.form("syl_form", clear_on_submit=True):
                syl_course = st.selectbox("Course:", list(COURSE_CONFIG.keys()))
                syl_topic = st.selectbox("Topic Covered:", ALL_SYLLABUS_TOPICS)
                syl_type = st.selectbox("Class Type:", ["Theory Class", "Practical Lab Session", "Class Test / Viva"])
                syl_teacher = st.selectbox("Teacher:", teacher_df["Name"].tolist() if not teacher_df.empty else ["Director Sir"])
                if st.form_submit_button("Save Syllabus Log"):
                    s_row = {"Date": str(datetime.date.today()), "Course": syl_course, "Topics Covered": syl_topic, "Class Type": syl_type, "Teacher Incharge": syl_teacher}
                    syllabus_df = pd.concat([syllabus_df, pd.DataFrame([s_row])], ignore_index=True)
                    save_data(syllabus_df, SYLLABUS_LOG_FILE, "syllabus_logs")
                    st.success("✅ Syllabus entry saved!")
                    st.rerun()

        # 3. PC Allocation
        with t_tab3:
            st.subheader("Daily PC Lab Allocation")
            with st.form("pc_alloc_form", clear_on_submit=True):
                pc_sid = st.selectbox("Student:", student_df["Student ID"] + " - " + student_df["Name"], key="pc_s_sel") if not student_df.empty else None
                m_no = st.selectbox("Machine No:", [f"PC-{i:02d}" for i in range(1, 21)])
                pc_shift = st.selectbox("Shift:", ["Morning", "Afternoon", "Evening"])
                if st.form_submit_button("Allocate PC Machine"):
                    if pc_sid:
                        pc_row = {"Date": str(datetime.date.today()), "Student ID": pc_sid.split(" - ")[0], "Student Name": pc_sid.split(" - ")[1], "PC Machine No": m_no, "Shift": pc_shift, "Teacher Incharge": "Faculty"}
                        pc_alloc_df = pd.concat([pc_alloc_df, pd.DataFrame([pc_row])], ignore_index=True)
                        save_data(pc_alloc_df, PC_ALLOC_FILE, "pc_alloc_db")
                        st.success(f"✅ Machine {m_no} allocated!")
                        st.rerun()

        # 4. Tasks
        with t_tab4:
            st.subheader("Assign Student Daily Tasks")
            with st.form("task_assign_form", clear_on_submit=True):
                t_sid = st.selectbox("Student:", student_df["Student ID"] + " - " + student_df["Name"], key="t_s_sel") if not student_df.empty else None
                task_txt = st.text_area("Practical Task / Assignment Details:")
                if st.form_submit_button("Assign Task"):
                    if t_sid and task_txt:
                        tsk_row = {"Date": str(datetime.date.today()), "Student ID": t_sid.split(" - ")[0], "Student Name": t_sid.split(" - ")[1], "Task Assigned": task_txt, "Status": "Assigned", "Teacher Incharge": "Faculty"}
                        tasks_df = pd.concat([tasks_df, pd.DataFrame([tsk_row])], ignore_index=True)
                        save_data(tasks_df, TASKS_FILE, "tasks_db")
                        st.success("✅ Task Assigned Successfully!")
                        st.rerun()

# -------------------------------------------------------------
# 8. ADMIN CONTROL PANEL
# -------------------------------------------------------------
elif menu == "🔐 Admin Control Panel":
    st.header("🔐 Director Admin Control Panel")
    pwd = st.text_input("Enter Director Admin Password", type="password", key="admin_pwd_main")
    if pwd == ADMIN_PWD:
        st.success("Welcome Director Chiranjeeb Hazarika Sir!")
        adm_tab1, adm_tab2 = st.tabs(["📋 All Students Master Directory", "🗑️ Reset Database"])
        
        with adm_tab1:
            if not student_df.empty:
                st.dataframe(student_df, use_container_width=True)
            else:
                st.info("Student directory is empty.")
                
        with adm_tab2:
            st.warning("⚠️ Danger Zone: Clear entire local and cloud database.")
            if st.checkbox("Confirm Database Reset"):
                if st.button("🔴 RESET ALL MASTER DATA"):
                    student_df = pd.DataFrame(columns=student_cols)
                    fee_df = pd.DataFrame(columns=fee_cols)
                    att_df = pd.DataFrame(columns=attendance_cols)
                    save_data(student_df, STUDENT_MASTER_FILE, "students_db")
                    save_data(fee_df, FEE_LOG_FILE, "fees_db")
                    save_data(att_df, ATTENDANCE_FILE, "attendance_db")
                    st.success("Database Reset Successfully!")
                    st.rerun()

# -------------------------------------------------------------
# FOOTER
# -------------------------------------------------------------
st.markdown("""
<div style="text-align:center; padding:20px; font-size:12px; color:#64748B; border-top:1px solid #CBD5E1; margin-top:40px;">
    Design & Architecture Inspired by National Institutional Portals | Developed for Soft Tech Computers & ZTC Enterprise © 2026<br>
    Center Code: 4159 | Kamarchuburi, Near Thelamara, Sonitpur, Assam - 784149
</div>
""", unsafe_allow_html=True)
