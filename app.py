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
    initial_sidebar_state="collapsed"
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

# -------------------------------------------------------------
# UDISE+ GOVT-STYLE THEME CSS
# -------------------------------------------------------------
st.markdown("""
<style>
    /* Global Styling */
    .stApp {
        background-color: #F0F4F8;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Top Government Header */
    .udise-topbar {
        background-color: #1E293B;
        color: white;
        padding: 10px 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 3px solid #0284C7;
        margin-top: -60px;
        margin-left: -4rem;
        margin-right: -4rem;
        margin-bottom: 15px;
    }
    .udise-logo {
        font-size: 22px;
        font-weight: 800;
        letter-spacing: 1px;
        color: #38BDF8;
    }
    .udise-logo span {
        color: #FFFFFF;
        font-weight: 400;
        font-size: 16px;
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

    /* School / Center Info Strip Card */
    .school-info-card {
        background: #FFFFFF;
        border-radius: 8px;
        padding: 14px 20px;
        border: 1px solid #CBD5E1;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    
    /* Action Cards */
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
    
    /* Support Box */
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

    /* Primary Buttons */
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

# -------------------------------------------------------------
# TOP GOVERNMENT / NIC STYLE NAVBAR
# -------------------------------------------------------------
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

# -------------------------------------------------------------
# SCHOOL / CENTER INFO BANNER MATRIX
# -------------------------------------------------------------
total_students_count = len(student_df)
st.markdown(f"""
<div class="school-info-card">
    <div style="display:flex; justify-content:space-between; flex-wrap:wrap; gap:15px;">
        <div>
            <div style="font-size:12px; color:#64748B;">🏛️ Center / Institution:</div>
            <div style="font-size:15px; font-weight:700; color:#0F172A;">SOFT TECH COMPUTERS & ZTC ENTERPRISE</div>
        </div>
        <div>
            <div style="font-size:12px; color:#64748B;">📋 Center Code:</div>
            <div style="font-size:15px; font-weight:700; color:#0284C7;">4159 (Kamarchuburi, Thelamara)</div>
        </div>
        <div>
            <div style="font-size:12px; color:#64748B;">🏷️ Category & Recognition:</div>
            <div style="font-size:15px; font-weight:700; color:#0F172A;">ISO 9001:2015 Certified IT Academy</div>
        </div>
        <div>
            <div style="font-size:12px; color:#64748B;">👥 Enrolled Database:</div>
            <div style="font-size:15px; font-weight:700; color:#10B981;">{total_students_count} Active Candidates</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# NAVIGATION MODULE TABS
# -------------------------------------------------------------
main_mod = st.radio("Navigation View:", [
    "⚡ Quick Actions & Dashboard",
    "📝 New Student Admission",
    "💵 Fee Counter Desk",
    "📜 Certificate Verification",
    "🎯 Sunday Free Practice Class (SFPC)",
    "🔐 Director Admin Control"
], horizontal=True)

st.markdown("---")

# -------------------------------------------------------------
# 1. QUICK ACTIONS (UDISE+ HOMEPAGE GRID)
# -------------------------------------------------------------
# -------------------------------------------------------------
# 1. QUICK ACTIONS & PRIVACY-PROTECTED DASHBOARD
# -------------------------------------------------------------
if main_mod == "⚡ Quick Actions & Dashboard":
    st.markdown('<h4 style="color:#0F172A; margin:0 0 15px 0;">⚡ Institutional Overview & Quick Actions</h4>', unsafe_allow_html=True)
    
    # Overview Summary Cards (No Personal Data Leaked)
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1:
        st.metric("Total Enrolled Candidates", f"{len(student_df)} Students")
    with col_s2:
        active_count = len(student_df[student_df["Status"] == "Active"]) if "Status" in student_df.columns else len(student_df)
        st.metric("Active Ongoing Batches", f"{active_count} Trainees")
    with col_s3:
        st.metric("Institutional ISO Certified", "ISO 9001:2015")
    with col_s4:
        st.metric("Authorized Center Code", "4159 (Assam)")
        
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
                    <div class="action-title">Public Certificate Verification</div>
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
                    <b>Helpdesk / Technical</b><br>
                    <span style="color:#94A3B8; font-size:11px;">Kamarchuburi, Sonitpur</span>
                </div>
                <div style="color:#10B981; font-weight:bold;">PIN: 784149</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    
    # PRIVACY PROTECTED STUDENT DIRECTORY SECTION
    st.subheader("🔒 Master Student Records (Authorized Staff Access Only)")
    with st.expander("🔑 Click here to unlock student database (Password Required)", expanded=False):
        view_pwd = st.text_input("Enter Staff / Director Password to View Records:", type="password", key="view_dash_pwd")
        if view_pwd in [ADMIN_PWD, TEACHER_PWD]:
            st.success("Access Granted! Showing Master Database:")
            if not student_df.empty:
                st.dataframe(student_df, use_container_width=True)
            else:
                st.info("No candidates registered in database yet.")
        elif view_pwd:
            st.error("Incorrect Password! Access denied for privacy reasons.")
            else:
    st.info("Student phone numbers, addresses, and fee details are hidden for privacy. Enter password to view.")elif main_mod == "📝 New Student Admission":
    st.header("📝 Candidate Admission Data Capture Format (DCF)")
    
    year_code = str(datetime.date.today().year)[2:]
    existing_ids = [sid for sid in student_df["Student ID"] if str(sid).startswith(f"STC{year_code}-")] if not student_df.empty else []
    next_id = f"STC{year_code}-{len(existing_ids)+1:03d}"
    st.info(f"⚡ **Auto Generated Roll ID / Reg No:** `{next_id}`")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        cert_dur = st.selectbox("Course Duration Option*", ["12 Months", "6 Months", "3 Months", "2 Months", "45 Days"])
        join_date = st.date_input("Admission / Joining Date*", value=datetime.date.today())
        months_to_add = 12 if "12" in cert_dur else (6 if "6" in cert_dur else (3 if "3" in cert_dur else (2 if "2" in cert_dur else 1)))
        auto_expiry = join_date + datetime.timedelta(days=months_to_add*30)
        st.success(f"📅 **Course Validity / Expiry:** {auto_expiry.strftime('%d-%B-%Y')}")

    with st.form("add_student_dcf_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Candidate Full Name*")
            fname = st.text_input("Father's Name*")
            mname = st.text_input("Mother's Name*")
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            dob = st.date_input("Date of Birth", min_value=datetime.date(1990, 1, 1))
            mobile = st.text_input("Contact Mobile Number*")
            
        with col2:
            vill = st.text_input("Village / Town*")
            po = st.text_input("Post Office")
            ps = st.text_input("Police Station", value="THELAMARA")
            dist = st.text_input("District", value="Sonitpur")
            course = st.selectbox("Course Enrolled*", list(COURSE_CONFIG.keys()))
            days_batch = st.selectbox("Batch Schedule*", ["MWF (Monday, Wednesday, Friday)", "TTS (Tuesday, Thursday, Saturday)", "Regular (Daily)"])
            
        col3, col4 = st.columns(2)
        with col3:
            session = st.text_input("Academic Session", value=f"{datetime.date.today().year}-{datetime.date.today().year+1}")
            total_fee = st.number_input("Total Fee (₹)", min_value=0.0, value=2550.0, step=100.0)
            discount = st.number_input("Discount Allowed (₹)", min_value=0.0, step=50.0)
            
        with col4:
            shift = st.selectbox("Shift Assigned", ["Morning (06:30-08:00 AM)", "Afternoon (04:00-05:30 PM)", "Evening (05:30-07:00 PM)"])
            batch_time = st.text_input("Session Timing", value="90 Mins Practical")
            
        if st.form_submit_button("💾 Submit & Save Candidate DCF"):
            existing_mobiles = student_df["Mobile No"].tolist() if not student_df.empty else []
            if not name or not mobile:
                st.error("Please enter Student Name and Mobile Number!")
            elif mobile in existing_mobiles:
                st.error("🚨 THIS MOBILE NUMBER IS ALREADY REGISTERED!")
            else:
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
                    "Shift": shift, "Batch Time": batch_time, "Photo Path": "", "Status": "Active",
                    "Stage_Admission": "Completed", "Stage_IDCard": "Generated", "Stage_Registration": "Pending",
                    "Stage_ExamForm": "Pending", "Stage_AdmitCard": "Pending", "Stage_Certificate": "Pending"
                }
                student_df = pd.concat([student_df, pd.DataFrame([new_row])], ignore_index=True)
                save_data(student_df, STUDENT_MASTER_FILE, "students_db")
                st.balloons()
                st.success(f"🎉 Candidate Registered Successfully with ID: {next_id}")
                st.rerun()

# -------------------------------------------------------------
# 3. FEE COUNTER DESK
# -------------------------------------------------------------
elif main_mod == "💵 Fee Counter Desk":
    st.header("💵 Fee Counter & Receipt Generation")
    sel_sid = st.selectbox("Select Candidate ID:", student_df["Student ID"] + " - " + student_df["Name"]) if not student_df.empty else None
    if sel_sid:
        sid = sel_sid.split(" - ")[0]
        s_rec = student_df[student_df["Student ID"] == sid].iloc[0]
        paid_logs = fee_df[fee_df["Student ID"] == sid]
        total_paid = sum([float(amt) for amt in paid_logs["Amount Paid"] if amt])
        net = float(s_rec["Net Fee"]) if s_rec["Net Fee"] else 0.0
        due = net - total_paid
        
        st.markdown(f"""
        <div style="background:#FFFFFF; border-left:4px solid #0284C7; padding:12px 16px; border-radius:6px; margin:10px 0; border:1px solid #E2E8F0;">
            <b>Candidate:</b> {s_rec['Name']} | <b>Net Course Fee:</b> ₹{net:.2f} | <b>Total Paid:</b> ₹{total_paid:.2f} | <b>Balance Due:</b> <span style="color:#EF4444; font-weight:bold;">₹{due:.2f}</span>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("fee_form", clear_on_submit=True):
            pay_amt = st.number_input("Amount Deposited (₹)", min_value=100.0, step=100.0)
            pay_mode = st.selectbox("Payment Mode", ["Cash", "UPI / GPay", "Bank Transfer"])
            collector_nm = st.selectbox("Collected By:", ["Director Chiranjeeb Hazarika", "Faculty / Staff"])
            
            if st.form_submit_button("🧾 Issue Money Receipt"):
                rc_num = f"REC-{datetime.date.today().strftime('%Y%m%d')}-{len(fee_df)+1:03d}"
                f_row = {"Receipt No": rc_num, "Student ID": sid, "Date": str(datetime.date.today()), "Amount Paid": str(pay_amt), "Payment Mode": pay_mode, "Collected_By": collector_nm, "Remarks": "Fee Deposit"}
                fee_df = pd.concat([fee_df, pd.DataFrame([f_row])], ignore_index=True)
                save_data(fee_df, FEE_LOG_FILE, "fees_db")
                st.success(f"✅ Receipt Issued Successfully! Receipt No: {rc_num}")
                st.rerun()

# -------------------------------------------------------------
# 4. CERTIFICATE VERIFICATION
# -------------------------------------------------------------
elif main_mod == "📜 Certificate Verification":
    st.header("📜 Online Certificate & Registration Verification")
    v_id = st.text_input("Enter Student Roll ID / Registration Number:").strip().upper()
    if v_id:
        v_match = student_df[student_df["Student ID"] == v_id]
        if not v_match.empty:
            v_data = v_match.iloc[0]
            st.balloons()
            st.markdown(f"""
            <div style="background:#ECFDF5; border:1.5px solid #10B981; border-radius:8px; padding:16px; color:#065F46;">
                <h4 style="margin:0; color:#047857;">✅ OFFICIAL RECORD VERIFIED</h4>
                <p style="margin:6px 0 0 0;"><b>Candidate Name:</b> {v_data['Name']} | <b>Course:</b> {v_data['Course']} | <b>Reg ID:</b> {v_data['Student ID']}</p>
                <p style="margin:4px 0 0 0; font-size:12px; color:#047857;">Center: Soft Tech Computers & ZTC (Code: 4159) | Status: {v_data['Status']}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error("❌ INVALID REGISTRATION NUMBER! No official matching record found in the academy database.")

# -------------------------------------------------------------
# 5. SFPC CLASS ELIGIBILITY
# -------------------------------------------------------------
elif main_mod == "🎯 Sunday Free Practice Class (SFPC)":
    st.header("🎯 Sunday Free Practice Class (SFPC) Eligibility Module")
    sf_id = st.text_input("Enter Student Roll ID for Eligibility Check:").strip().upper()
    if sf_id:
        st_res = student_df[student_df["Student ID"] == sf_id]
        if not st_res.empty:
            s = st_res.iloc[0]
            p_logs = fee_df[fee_df["Student ID"] == sf_id]
            tot_paid = sum([float(a) for a in p_logs["Amount Paid"] if a])
            net_f = float(s["Net Fee"]) if s["Net Fee"] else 2550.0
            cleared_pct = (tot_paid / net_f * 100) if net_f > 0 else 100
            
            is_ok = cleared_pct >= 50.0
            st.markdown(f"""
            <div style="background:#FFFFFF; border:1px solid {'#10B981' if is_ok else '#EF4444'}; border-radius:8px; padding:16px;">
                <h3 style="margin:0; color:{'#10B981' if is_ok else '#EF4444'};">{'✅ ELIGIBLE FOR LAB ACCESS' if is_ok else '❌ NOT ELIGIBLE'}</h3>
                <p style="margin:6px 0 0 0;"><b>Candidate:</b> {s['Name']} ({s['Student ID']}) | <b>Fee Deposited:</b> {cleared_pct:.1f}% (₹{tot_paid:.2f} / ₹{net_f:.2f})</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error("❌ Candidate Roll ID not found.")

# -------------------------------------------------------------
# 6. ADMIN CONTROL
# -------------------------------------------------------------
elif main_mod == "🔐 Director Admin Control":
    st.header("🔐 Director Administration Desk")
    ad_pwd = st.text_input("Enter Admin Password:", type="password")
    if ad_pwd == ADMIN_PWD:
        st.success("Authorized Session Active - Welcome Director Sir!")
        if not student_df.empty:
            st.dataframe(student_df, use_container_width=True)
        if st.checkbox("Danger Zone: Reset Database"):
            if st.button("🔴 Reset All Master DB"):
                save_data(pd.DataFrame(columns=student_cols), STUDENT_MASTER_FILE, "students_db")
                save_data(pd.DataFrame(columns=fee_cols), FEE_LOG_FILE, "fees_db")
                st.success("Database Reset Completed!")
                st.rerun()

# -------------------------------------------------------------
# GOVERNMENT STYLE FOOTER
# -------------------------------------------------------------
st.markdown("""
<div style="text-align:center; padding:20px; font-size:12px; color:#64748B; border-top:1px solid #CBD5E1; margin-top:40px;">
    Design & Architecture Inspired by National Institutional Portals | Developed for Soft Tech Computers & ZTC Enterprise © 2026<br>
    Center Code: 4159 | Kamarchuburi, Near Thelamara, Sonitpur, Assam - 784149
</div>
""", unsafe_allow_html=True)
