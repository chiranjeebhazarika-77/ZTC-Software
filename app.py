import streamlit as st
import pandas as pd
import os
import datetime
import pytz
import base64
import requests
import json

# Page Configuration
st.set_page_config(page_title="Soft Tech Computers & ZTC Enterprise Portal", page_icon="💻", layout="wide")

# IST TimeZone Setup
IST = pytz.timezone('Asia/Kolkata')

# -------------------------------------------------------------
# GOOGLE SHEETS LIVE SYNC URL (PASTE YOUR NEW WEB APP URL HERE)
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

# -------------------------------------------------------------
# HIGH-SPEED OPTIMIZED DATA LOADING & BACKGROUND SYNC
# -------------------------------------------------------------
@st.cache_data(ttl=60)
def sync_from_cloud(sheet_name):
    if GSHEET_WEBAPP_URL:
        try:
            res = requests.get(f"{GSHEET_WEBAPP_URL}?sheet_name={sheet_name}", timeout=3, allow_redirects=True)
            if res.status_code == 200:
                data = res.json()
                if data and len(data) > 1:
                    return data
        except Exception:
            pass
    return None

def load_data(file_path, columns, sheet_name=None):
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path, dtype=str)
            for col in columns:
                if col not in df.columns: df[col] = ""
            return df
        except Exception:
            pass

    if sheet_name:
        cloud_raw = sync_from_cloud(sheet_name)
        if cloud_raw and len(cloud_raw) > 1:
            header = cloud_raw[0]
            rows = cloud_raw[1:]
            df = pd.DataFrame(rows, columns=header, dtype=str)
            for col in columns:
                if col not in df.columns: df[col] = ""
            df.to_csv(file_path, index=False)
            return df

    return pd.DataFrame(columns=columns)

def save_data(df, file_path, sheet_name=None):
    df.to_csv(file_path, index=False)
    if GSHEET_WEBAPP_URL and sheet_name:
        try:
            records = [df.columns.tolist()] + df.fillna("").values.tolist()
            payload = {"action": "overwrite", "sheet_name": sheet_name, "rows": records}
            requests.post(GSHEET_WEBAPP_URL, data=json.dumps(payload), headers={"Content-Type": "application/json"}, timeout=4, allow_redirects=True)
        except Exception:
            pass    df.to_csv(file_path, index=False)
    if GSHEET_WEBAPP_URL and sheet_name:
        try:
            records = [df.columns.tolist()] + df.fillna("").values.tolist()
            payload = {"action": "overwrite", "sheet_name": sheet_name, "rows": records}
            # Google Script Redirects handle
            requests.post(GSHEET_WEBAPP_URL, data=json.dumps(payload), headers={"Content-Type": "application/json"}, timeout=12, allow_redirects=True)
        except Exception:
            pass

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

# Load DataFrames
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
    "PGDCA (Post Graduate Diploma in Computer Application)": {
        "Months": 12, "FeeNum": 8500, "FeeStr": "₹8,500 Total",
        "Topics": ["Computer Fundamentals", "Operating System", "MS-Office", "Tally Prime with GST", "DBMS & SQL", "HTML/CSS Web Design", "Python / C Programming", "Internet & Cyber Security"]
    },
    "ADCA (Advanced Diploma in Computer Application)": {
        "Months": 12, "FeeNum": 7500, "FeeStr": "₹7,500 Total",
        "Topics": ["Paint", "Notepad", "Wordpad", "MS-Word", "MS-Excel", "MS-Powerpoint", "MS-Access", "HTML", "DHTML", "Tally Prime", "Photoshop", "Pagemaker", "Internet", "Python"]
    },
    "DCA (Diploma in Computer Application)": {
        "Months": 6, "FeeNum": 4500, "FeeStr": "₹4,500 Total",
        "Topics": ["Paint", "Notepad", "Wordpad", "MS-Word", "MS-Excel", "MS-Powerpoint", "MS-Access", "HTML", "Tally", "Internet"]
    },
    "DTP (Desktop Publishing)": {
        "Months": 3, "FeeNum": 3500, "FeeStr": "₹3,500 Total",
        "Topics": ["MS-Word", "Photoshop", "Pagemaker", "CorelDraw", "Assamese Typesetting", "Internet"]
    },
    "Tally Prime with GST": {
        "Months": 3, "FeeNum": 4000, "FeeStr": "₹4,000 Total",
        "Topics": ["Accounting Basics", "Tally Prime Basics", "Inventory Management", "GST & TDS Calculation", "Payroll & Billing"]
    },
    "Certificate Course in Computer Basics": {
        "Months": 3, "FeeNum": 2500, "FeeStr": "₹2,500 Total",
        "Topics": ["Paint", "Notepad", "Wordpad", "MS-Word", "Internet"]
    },
    "Class 9 English Coaching": {"Months": 12, "FeeNum": 600, "FeeStr": "₹600 / Month", "Topics": ["Grammar", "Literature prose", "Poetry", "Writing Skills"]},
    "Class 10 English Coaching": {"Months": 12, "FeeNum": 700, "FeeStr": "₹700 / Month", "Topics": ["Grammar", "Literature prose", "Poetry", "Writing Skills"]},
    "Class 11 English Coaching": {"Months": 12, "FeeNum": 800, "FeeStr": "₹800 / Month", "Topics": ["Grammar", "Literature prose", "Poetry", "Writing Skills"]},
    "Class 12 English Coaching": {"Months": 12, "FeeNum": 900, "FeeStr": "₹900 / Month", "Topics": ["Grammar", "Literature prose", "Poetry", "Writing Skills"]}
}

ALL_SYLLABUS_TOPICS = [
    "Computer Basics / Fundamentals", "Paint / Notepad / Wordpad", "MS Word", "MS Excel", 
    "MS Powerpoint", "MS Access", "Tally Prime with GST", "Photoshop", "Pagemaker", 
    "CorelDraw", "HTML / Web Design", "Python Programming", "Internet & Cyber Security", 
    "Assamese Typesetting", "English Grammar", "English Literature Prose/Poetry", "Exam Taken"
]

st.sidebar.title("💻 STC & ZTC Portal")
menu = st.sidebar.radio("Navigation Menu:", [
    "🏠 Home & Public Dashboard",
    "📜 Online Certificate Verification",
    "📝 New Student Admission",
    "🔑 Student Login Portal",
    "🎯 Sunday Free Practice Class (SFPC)",
    "📝 Exam Form Fill-Up & Reg Desk",
    "💵 Fee Counter Desk",
    "🔑 Teacher Portal & QR Scanner",
    "🔐 Admin Control Panel"
])

# 1. PUBLIC DASHBOARD
if menu == "🏠 Home & Public Dashboard":
    dp2_b64 = get_image_base64("dp2")
    if dp2_b64:
        st.markdown(f'<img src="{dp2_b64}" style="width:100%; max-height:280px; object-fit:contain; border-radius:15px; border:2px solid #00F0FF; box-shadow: 0 0 20px rgba(0, 240, 255, 0.3); margin-bottom:12px;">', unsafe_allow_html=True)
    
    st.markdown("""
        <div style="background: linear-gradient(135deg, #020B19 0%, #0F172A 50%, #1E3A8A 100%); padding: 12px 20px; border-radius: 12px; text-align: center; color: white; border: 1.5px solid #00F0FF; box-shadow: 0 0 15px rgba(0, 240, 255, 0.2); margin-bottom: 15px;">
            <h4 style="margin:0; color:#FBBF24; font-size:15px; font-weight:bold;">MAKE YOURSELF DIGITAL | AN ISO 9001:2015 CERTIFIED INSTITUTION</h4>
            <p style="margin:4px 0 0 0; font-size:13px; color:#CBD5E1;">Kamarchuburi, Near Thelamara, Sonitpur, Assam - 784149 | Center Code: 4159 | Contact: +91 9101026718</p>
        </div>
    """, unsafe_allow_html=True)
    
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Est. Year", "Since 2020")
    col_m2.metric("Total Enrolled", f"{max(500, len(student_df))}+ Students")
    col_m3.metric("Alumni Network", "350+ Students")
    col_m4.metric("Certified Graduates", "200+ Certified")

# 2. NEW STUDENT ADMISSION
elif menu == "📝 New Student Admission":
    st.header("📝 New Student Registration Form")
    auth_pwd = st.text_input("Enter Staff / Admin Password:", type="password")
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
            st.success(f"📅 **Calculated Course Completion Date:** {auto_expiry.strftime('%d-%B-%Y')}")

        with st.form("add_student_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Student Full Name*")
                fname = st.text_input("Father's Name*")
                mname = st.text_input("Mother's Name*")
                gender = st.selectbox("Gender", ["Male", "Female", "Other"])
                dob = st.date_input("Date of Birth", min_value=datetime.date(1990, 1, 1))
                mobile = st.text_input("Mobile Number (Unique Key)*")
                photo_file = st.file_uploader("Upload Passport Size Photo", type=["jpg", "jpeg", "png"])
                
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

# 5. FEE COUNTER DESK
elif menu == "💵 Fee Counter Desk":
    st.header("💵 Student Fee Collection Counter Desk")
    f_pwd = st.text_input("Enter Password:", type="password")
    if f_pwd in [ADMIN_PWD, TEACHER_PWD]:
        sel_sid = st.selectbox("Select Student ID:", student_df["Student ID"] + " - " + student_df["Name"]) if not student_df.empty else None
        if sel_sid:
            sid = sel_sid.split(" - ")[0]
            s_rec = student_df[student_df["Student ID"] == sid].iloc[0]
            paid_logs = fee_df[fee_df["Student ID"] == sid]
            total_paid = sum([float(amt) for amt in paid_logs["Amount Paid"] if amt])
            net = float(s_rec["Net Fee"]) if s_rec["Net Fee"] else 0.0
            due = net - total_paid
            
            st.write(f"**Student:** {s_rec['Name']} | **Due Balance:** :red[₹{due:.2f}]")
            with st.form("fee_collect_form", clear_on_submit=True):
                pay_amt = st.number_input("Amount Paid (₹)", min_value=100.0, step=100.0)
                pay_mode = st.selectbox("Payment Mode", ["Cash", "UPI / GPay", "Bank Transfer"])
                collector_nm = st.selectbox("Collected By:", teacher_df["Name"].tolist() if not teacher_df.empty else ["Director Sir"])
                
                if st.form_submit_button("Issue Receipt & Save Deposit"):
                    rc_num = f"REC-{datetime.date.today().strftime('%Y%m%d')}-{len(fee_df)+1:03d}"
                    f_row = {"Receipt No": rc_num, "Student ID": sid, "Date": str(datetime.date.today()), "Amount Paid": str(pay_amt), "Payment Mode": pay_mode, "Collected_By": collector_nm, "Remarks": "Fee Deposit"}
                    fee_df = pd.concat([fee_df, pd.DataFrame([f_row])], ignore_index=True)
                    save_data(fee_df, FEE_LOG_FILE, "fees_db")
                    st.success(f"✅ Receipt Issued: {rc_num}")
                    st.rerun()

# 7. ADMIN CONTROL PANEL
elif menu == "🔐 Admin Control Panel":
    st.header("🔐 Director Admin Control Panel")
    pwd = st.text_input("Enter Director Admin Password", type="password")
    if pwd == ADMIN_PWD:
        st.success("Welcome Director Chiranjeeb Hazarika Sir!")
        adm_tab1, adm_tab2 = st.tabs(["📋 All Students Directory", "🗑️ Reset Database"])
        
        with adm_tab1:
            if not student_df.empty:
                st.dataframe(student_df, use_container_width=True)
        with adm_tab2:
            if st.checkbox("Clear All Data"):
                if st.button("🔴 CLEAR NOW"):
                    student_df = pd.DataFrame(columns=student_cols)
                    fee_df = pd.DataFrame(columns=fee_cols)
                    att_df = pd.DataFrame(columns=attendance_cols)
                    save_data(student_df, STUDENT_MASTER_FILE, "students_db")
                    save_data(fee_df, FEE_LOG_FILE, "fees_db")
                    save_data(att_df, ATTENDANCE_FILE, "attendance_db")
                    st.success("Database Reset!")
                    st.rerun()
