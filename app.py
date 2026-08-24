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
# GOOGLE SHEETS LIVE SYNC URL (PASTE YOUR DEPLOYED URL HERE)
# -------------------------------------------------------------
GSHEET_WEBAPP_URL = "https://script.google.com/macros/s/AKfycbzKN3L0VyzgniW8RYlG3qZjp9DZzmCSTQHmXS1l2shwtAQu6mHIQX1w1nbFcnOghkMy/exec"

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

def sync_from_cloud(sheet_name, columns):
    if GSHEET_WEBAPP_URL:
        try:
            res = requests.get(f"{GSHEET_WEBAPP_URL}?sheet_name={sheet_name}", timeout=10, allow_redirects=True)
            if res.status_code == 200:
                data = res.json()
                if data and len(data) > 1:
                    header = data[0]
                    rows = data[1:]
                    df = pd.DataFrame(rows, columns=header, dtype=str)
                    for col in columns:
                        if col not in df.columns: df[col] = ""
                    return df
        except Exception:
            pass
    return None

def load_data(file_path, columns, sheet_name=None):
    if sheet_name:
        cloud_df = sync_from_cloud(sheet_name, columns)
        if cloud_df is not None and not cloud_df.empty:
            cloud_df.to_csv(file_path, index=False)
            return cloud_df

    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path, dtype=str)
            for col in columns:
                if col not in df.columns: df[col] = ""
            return df
        except Exception:
            return pd.DataFrame(columns=columns)
    else:
        return pd.DataFrame(columns=columns)

def save_data(df, file_path, sheet_name=None):
    df.to_csv(file_path, index=False)
    if GSHEET_WEBAPP_URL and sheet_name:
        try:
            records = [df.columns.tolist()] + df.fillna("").values.tolist()
            payload = {"action": "overwrite", "sheet_name": sheet_name, "rows": records}
            requests.post(GSHEET_WEBAPP_URL, json=payload, timeout=10, allow_redirects=True)
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

# Load DataFrames with Cloud Persistence
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

# Custom CSS
st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: #065F46;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 8px 16px;
    }
    div.stButton > button:first-child:hover {
        background-color: #047857;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 1. PUBLIC DASHBOARD
# ---------------------------------------------------------
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

    dp3_b64 = get_image_base64("dp3")
    col_img1, col_img2 = st.columns(2)
    with col_img1:
        if dp3_b64:
            st.markdown('<h4 style="color:#1E3A8A; margin:0 0 8px 0;">🛠️ Key Technologies Taught</h4>', unsafe_allow_html=True)
            st.markdown(f'<img src="{dp3_b64}" style="width:100%; border-radius:12px; border:2px solid #2563EB; box-shadow:0 0 10px rgba(37,99,235,0.2);">', unsafe_allow_html=True)
    
    with col_img2:
        st.markdown('<h4 style="color:#1E3A8A; margin:0 0 8px 0;">📝 Course Enquiry Desk</h4>', unsafe_allow_html=True)
        with st.form("pub_enq_form", clear_on_submit=False):
            e_name = st.text_input("Your Full Name*")
            e_mobile = st.text_input("Contact Mobile Number*")
            e_course = st.selectbox("Select Interested Course*", list(COURSE_CONFIG.keys()))
            is_ztc = st.checkbox("I am currently a ZTC Tuition Student (Get 50% Discount)")
            e_addr = st.text_input("Village / Address")
            
            if st.form_submit_button("Submit & Reveal Course Fee Structure"):
                if not e_name or not e_mobile:
                    st.error("Please enter Name and Mobile Number!")
                else:
                    e_row = {"Date": str(datetime.date.today()), "Name": e_name.upper(), "Mobile": e_mobile, "Course Interested": e_course, "Is ZTC Student": "Yes" if is_ztc else "No", "Village/Address": e_addr.upper(), "Status": "Enquired"}
                    enquiry_df = pd.concat([enquiry_df, pd.DataFrame([e_row])], ignore_index=True)
                    save_data(enquiry_df, ENQUIRY_FILE, "enquiries_db")
                    raw_fee = COURSE_CONFIG[e_course]["FeeStr"]
                    st.balloons()
                    st.success(f"🎉 Thank you {e_name}! Course Fee Structure for {e_course}: {raw_fee}")

    st.markdown("---")
    top_student_name, top_student_id = "N/A", "N/A"
    if not att_df.empty and not student_df.empty:
        pres_counts = att_df[att_df["Status"] == "Present"]["Student ID"].value_counts()
        if not pres_counts.empty:
            top_id = pres_counts.index[0]
            st_match = student_df[student_df["Student ID"] == top_id]
            if not st_match.empty:
                top_student_name = st_match.iloc[0]["Name"]
                top_student_id = st_match.iloc[0]["Student ID"]

    st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1E1B4B, #312E81); border: 1.5px solid #F59E0B; border-radius: 12px; padding: 10px 18px; text-align: center; color: white; margin-bottom: 20px;">
            <span style="color:#FBBF24; font-weight:bold; font-size:12px;">🏆 AI STUDENT OF THE MONTH:</span>
            <span style="color:#FFFFFF; font-weight:bold; font-size:15px; margin-left:8px;">{top_student_name}</span>
            <span style="color:#CBD5E1; font-size:12px;"> ({top_student_id})</span>
        </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 1.5 ONLINE CERTIFICATE VERIFICATION
# ---------------------------------------------------------
elif menu == "📜 Online Certificate Verification":
    st.header("📜 Online Certificate Verification Desk")
    verify_id = st.text_input("Enter Student Roll ID (e.g. STC26-001):").strip().upper()
    if verify_id:
        v_match = student_df[student_df["Student ID"] == verify_id]
        if not v_match.empty:
            v_data = v_match.iloc[0]
            st.balloons()
            st.success(f"✅ **VERIFIED RECORD FOUND:** Name: {v_data['Name']} | Course: {v_data['Course']} | Roll ID: {v_data['Student ID']}")
        else:
            st.error("❌ INVALID ROLL ID! No official record found.")

# ---------------------------------------------------------
# 2. NEW STUDENT ADMISSION
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# 3. STUDENT LOGIN PORTAL
# ---------------------------------------------------------
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
                st.error("Invalid Roll ID or Password!")
    else:
        s_id = st.session_state["logged_student_id"]
        s = student_df[student_df["Student ID"] == s_id].iloc[0]
        
        col_head, col_out = st.columns([4, 1])
        with col_head:
            st.success(f"Welcome, **{s['Name']}** ({s['Student ID']})")
        with col_out:
            if st.button("🔒 Logout"):
                st.session_state["student_logged_in"] = False
                st.session_state["logged_student_id"] = ""
                st.rerun()

        st_tab1, st_tab2, st_tab3 = st.tabs(["💳 Digital ID Card & QR", "💵 Passbook Ledger", "🔄 6-Stage Journey Tracker"])
        with st_tab1:
            st_photo_b64 = get_image_base64(s["Photo Path"]) if s["Photo Path"] else None
            id_card_html = f"""
            <div id="print_id_card" style="background:#020B19; border:2px solid #00F0FF; border-radius:16px; padding:20px; color:white; max-width:680px; margin:auto; box-shadow:0 0 20px rgba(0,240,255,0.3); font-family:Arial, sans-serif;">
                <div style="display:flex; align-items:center; justify-content:space-between; border-bottom:1px solid rgba(255,255,255,0.2); padding-bottom:10px;">
                    <div>
                        <h2 style="margin:0; color:#00F0FF; font-size:20px; font-weight:bold;">SOFT TECH COMPUTERS & ZTC</h2>
                        <p style="margin:2px 0 0 0; font-size:10px; color:#CBD5E1;">KAMARCHUBURI, THELAMARA, SONITPUR | CENTER CODE: 4159</p>
                    </div>
                </div>
                <div style="display:flex; align-items:center; justify-content:space-between; margin:15px 0;">
                    <div style="text-align:center; flex:1;">
                        <img src="{st_photo_b64 if st_photo_b64 else 'https://cdn-icons-png.flaticon.com/512/3135/3135715.png'}" style="width:100px; height:100px; border-radius:50%; border:2px solid #00F0FF; object-fit:cover;">
                        <div style="margin-top:5px; color:#00F0FF; font-weight:bold; font-size:12px;">ID: {s['Student ID']}</div>
                    </div>
                    <div style="flex:2; padding-left:20px;">
                        <h3 style="margin:0; color:#FFFFFF; font-size:18px;">{s['Name']}</h3>
                        <p style="margin:3px 0; font-size:12px; color:#00F0FF;"><b>Course:</b> <span style="color:white;">{s['Course']}</span></p>
                        <p style="margin:3px 0; font-size:12px; color:#00F0FF;"><b>Validity:</b> <span style="color:white;">{s['Join Date']} to {s['Validity Date']}</span></p>
                    </div>
                    <div>
                        <img src="https://api.qrserver.com/v1/create-qr-code/?size=80x80&data={s['Student ID']}" style="width:75px; height:75px; border-radius:4px; background:white; padding:2px;">
                    </div>
                </div>
            </div>
            """
            st.markdown(id_card_html, unsafe_allow_html=True)
            if st.button("🖨️ Print / Download ID Card"):
                st.components.v1.html("<script>window.print();</script>", height=0)

        with st_tab2:
            net_f = float(s["Net Fee"]) if s["Net Fee"] else 0.0
            st_paid_logs = fee_df[fee_df["Student ID"] == s_id]
            tot_p = sum([float(amt) for amt in st_paid_logs["Amount Paid"] if amt])
            bal_due = net_f - tot_p
            col_m1, col_m2, col_m3 = st.columns(3)
            col_m1.metric("Net Course Fee", f"₹{net_f:.2f}")
            col_m2.metric("Total Paid", f"₹{tot_p:.2f}")
            col_m3.metric("Balance Due", f"₹{bal_due:.2f}", delta="-Pending" if bal_due > 0 else "Cleared")

        with st_tab3:
            st.markdown(f"""
                <div style="background:#0F172A; border:1.5px solid #00F0FF; padding:18px; border-radius:12px; color:white;">
                    <ol>
                        <li><b>(a) Admission Taken:</b> <span style="color:#10B981; font-weight:bold;">{s.get('Stage_Admission', 'Completed')}</span></li>
                        <li><b>(b) Digital ID Card Generated:</b> <span style="color:#10B981; font-weight:bold;">{s.get('Stage_IDCard', 'Generated')}</span></li>
                        <li><b>(c) SARVA Head Office Registration:</b> <span style="color:#F59E0B; font-weight:bold;">{s.get('Stage_Registration', 'In Progress')}</span></li>
                        <li><b>(d) Examination Form Fillup:</b> <span style="color:#EF4444; font-weight:bold;">{s.get('Stage_ExamForm', 'Pending')}</span></li>
                        <li><b>(e) Admit Card Issued:</b> <span style="color:#EF4444; font-weight:bold;">{s.get('Stage_AdmitCard', 'Pending')}</span></li>
                        <li><b>(f) Certificate & Marksheet:</b> <span style="color:#EF4444; font-weight:bold;">{s.get('Stage_Certificate', 'Pending')}</span></li>
                    </ol>
                </div>
            """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. SUNDAY FREE PRACTICE CLASS (SFPC)
# ---------------------------------------------------------
elif menu == "🎯 Sunday Free Practice Class (SFPC)":
    st.header("🎯 Sunday Free Practice Class (SFPC) Eligibility Portal")
    st.markdown("""
        <div style="background:#0F172A; border:1.5px solid #F59E0B; padding:12px 18px; border-radius:10px; color:#FBBF24; margin-bottom:15px; font-size:13px;">
            📌 <b>SFPC RUNNING FEE POLICY:</b> Admission Fee: ₹999 | Monthly Class: ₹550/Month.<br>
            Student must have cleared <b>≥50% of Current Running Bill</b> AND maintain <b>≥75% Attendance Record</b>.
        </div>
    """, unsafe_allow_html=True)
    
    check_id = st.text_input("Enter Student Roll ID (e.g. STC26-001):").strip().upper()
    if check_id:
        st_res = student_df[student_df["Student ID"] == check_id]
        if not st_res.empty:
            s = st_res.iloc[0]
            
            today_date = datetime.date.today()
            try:
                j_date = datetime.datetime.strptime(str(s["Join Date"]), "%Y-%m-%d").date()
            except Exception:
                j_date = today_date
                
            days_enrolled = max(1, (today_date - j_date).days)
            months_active = max(1, (today_date.year - j_date.year) * 12 + today_date.month - j_date.month + 1)
            
            adm_fee = 999.0
            monthly_rate = 550.0
            total_running_bill = adm_fee + (months_active * monthly_rate)
            
            p_logs = fee_df[fee_df["Student ID"] == check_id]
            tot_paid = sum([float(a) for a in p_logs["Amount Paid"] if a])
            min_fee_required = total_running_bill * 0.50
            fee_paid_perc = (tot_paid / total_running_bill * 100) if total_running_bill > 0 else 100.0
            
            s_att = att_df[att_df["Student ID"] == check_id]
            present_days = len(s_att[s_att["Status"] == "Present"])
            total_conducted_classes = max(1, len(s_att))
            attendance_perc = (present_days / total_conducted_classes * 100)
            
            fee_cleared = tot_paid >= min_fee_required
            att_cleared = attendance_perc >= 75.0
            is_eligible = fee_cleared and att_cleared
            
            st.markdown(f"""
                <div style="background:#020B19; border:2px solid {'#10B981' if is_eligible else '#EF4444'}; border-radius:14px; padding:20px; color:white; margin:15px 0;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <h3 style="margin:0; color:#00F0FF;">👤 {s['Name']} ({s['Student ID']})</h3>
                        <span style="background:{'#10B981' if is_eligible else '#EF4444'}; color:white; padding:5px 14px; border-radius:8px; font-weight:bold; font-size:13px;">
                            {'✅ ELIGIBLE FOR SFPC' if is_eligible else '❌ NOT ELIGIBLE'}
                        </span>
                    </div>
                    <p style="margin:6px 0; color:#CBD5E1; font-size:13px;"><b>Course:</b> {s['Course']} | <b>Active:</b> {months_active} Months ({days_enrolled} Days Enrolled)</p>
                </div>
            """, unsafe_allow_html=True)
            
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            col_m1.metric("Current Running Bill", f"₹{total_running_bill:.2f}")
            col_m2.metric("Total Fee Paid", f"₹{tot_paid:.2f}", delta=f"{fee_paid_perc:.1f}% Cleared")
            col_m3.metric("Attendance Score", f"{attendance_perc:.1f}%", delta=f"{present_days}/{total_conducted_classes} Days Present")
            col_m4.metric("Minimum 50% Req.", f"₹{min_fee_required:.2f}", delta="Required to Qualify")
            
            st.markdown("---")
            st.subheader("🔍 SFPC Running Bill Breakdown")
            
            audit_data = [
                {"Criteria": "Admission Fee Bill", "Value": "₹999.00", "Details": "One-time Admission Charge"},
                {"Criteria": f"Active Monthly Tuition ({months_active} Months × ₹550)", "Value": f"₹{months_active * monthly_rate:.2f}", "Details": f"{months_active} Months Running"},
                {"Criteria": "Total Running Bill Generated", "Value": f"₹{total_running_bill:.2f}", "Details": "Admission + Monthly Total"},
                {"Criteria": "Amount Deposited by Student", "Value": f"₹{tot_paid:.2f}", "Details": f"{fee_paid_perc:.1f}% Cleared"},
                {"Criteria": "Fee Rule Status (≥50% Required)", "Value": f"₹{tot_paid:.2f} / ₹{min_fee_required:.2f}", "Details": "Passed ✅" if fee_cleared else "Failed ❌ (Deposit Needed)"},
                {"Criteria": "Attendance Status (≥75% Required)", "Value": f"{attendance_perc:.1f}%", "Details": "Passed ✅" if att_cleared else "Failed ❌ (Low Attendance)"}
            ]
            st.table(pd.DataFrame(audit_data))
            
            if is_eligible:
                st.balloons()
                st.success(f"🎉 Congratulations {s['Name']}! You are ELIGIBLE for Sunday Free Practice Lab Access!")
            else:
                reasons = []
                if not fee_cleared:
                    shortage = min_fee_required - tot_paid
                    reasons.append(f"Fee clearance is {fee_paid_perc:.1f}% (Minimum 50% required. Please deposit ₹{shortage:.2f} to qualify).")
                if not att_cleared:
                    reasons.append(f"Attendance is {attendance_perc:.1f}% (Minimum 75% required).")
                st.error("❌ Access Denied! Reasons:\n- " + "\n- ".join(reasons))
        else:
            st.error("❌ INVALID ROLL ID! No student record found.")

# ---------------------------------------------------------
# 4.5 EXAM FORM FILL-UP & FINAL REGISTRATION DESK
# ---------------------------------------------------------
elif menu == "📝 Exam Form Fill-Up & Reg Desk":
    st.header("📝 Final Examination & Registration Form Fill-Up Desk")
    st.markdown("""
        <div style="background:#0F172A; border:1.5px solid #2563EB; padding:12px 18px; border-radius:10px; color:#93C5FD; margin-bottom:15px; font-size:13px;">
            🎓 <b>EXAMINATION POLICY:</b> Registration cum Examination Form Fill-Up Fee: <b>₹999/-</b>.<br>
            Calculated and applied automatically during the final course duration period before SARVA Board Exam conduction.
        </div>
    """, unsafe_allow_html=True)
    
    ex_sid = st.text_input("Enter Student Roll ID for Examination Form:").strip().upper()
    if ex_sid:
        st_res = student_df[student_df["Student ID"] == ex_sid]
        if not st_res.empty:
            s = st_res.iloc[0]
            st.markdown(f"""
                <div style="background:#020B19; border:2px solid #2563EB; border-radius:14px; padding:18px; color:white; margin:15px 0;">
                    <h3 style="margin:0; color:#60A5FA;">👤 {s['Name']} ({s['Student ID']})</h3>
                    <p style="margin:4px 0; color:#CBD5E1;"><b>Course:</b> {s['Course']} | <b>Duration:</b> {s['Duration']} | <b>Validity:</b> {s['Join Date']} to {s['Validity Date']}</p>
                    <h4 style="margin:6px 0; color:#FBBF24;">🧾 Registration & Examination Bill: ₹999.00</h4>
                </div>
            """, unsafe_allow_html=True)
            
            with st.form("exam_fill_form", clear_on_submit=True):
                st.write("📋 **SARVA Head Office Exam Center Details:**")
                st.text_input("Center Code", value="4159", disabled=True)
                st.text_input("Institution Name", value="SOFT TECH COMPUTERS & ZTC", disabled=True)
                ex_pay_mode = st.selectbox("Exam Fee Payment Mode (₹999)", ["Paid via Cash at Counter", "Paid via UPI / Online", "Due to Pay"])
                ex_remarks = st.text_input("Remarks", value="Final Term Board Exam Form Fill-Up")
                
                if st.form_submit_button("Submit Exam Form & Register Candidate"):
                    ex_row = {
                        "Date": str(datetime.date.today()), "Student ID": ex_sid, "Student Name": s["Name"],
                        "Course": s["Course"], "Exam Fee Amount": "999", "Payment Status": ex_pay_mode,
                        "Exam Center Code": "4159", "Remarks": ex_remarks
                    }
                    exam_forms_df = pd.concat([exam_forms_df, pd.DataFrame([ex_row])], ignore_index=True)
                    save_data(exam_forms_df, EXAM_FORMS_FILE, "exam_forms_db")
                    
                    student_df.loc[student_df["Student ID"] == ex_sid, "Stage_ExamForm"] = "Completed"
                    student_df.loc[student_df["Student ID"] == ex_sid, "Stage_Registration"] = "Verified"
                    save_data(student_df, STUDENT_MASTER_FILE, "students_db")
                    
                    st.balloons()
                    st.success(f"🎉 Examination Form Filled Successfully for {s['Name']}! Registration Stage Updated to Verified.")
        else:
            st.error("❌ INVALID ROLL ID! No student record found.")

# ---------------------------------------------------------
# 5. FEE COUNTER DESK
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# 6. TEACHER PORTAL
# ---------------------------------------------------------
elif menu == "🔑 Teacher Portal & QR Scanner":
    st.header("🔑 Faculty Portal & Class Management Desk")
    t_pwd = st.text_input("Enter Faculty Password:", type="password")
    if t_pwd == TEACHER_PWD:
        now_ist = datetime.datetime.now(IST)
        cur_time_str = now_ist.strftime("%I:%M:%S %p")
        cur_date_str = now_ist.strftime("%Y-%m-%d")
        
        t_tab1, t_tab2, t_tab3, t_tab4, t_tab5 = st.tabs([
            "📸 Camera Student Attendance", 
            "⏱️ Shift Punch In & Out", 
            "🖥️ Lab PC Allocator",
            "📌 Weak Student Note for Director",
            "📖 Log Syllabus & Marks"
        ])
        
        with t_tab1:
            cam_pic = st.camera_input("Scan Student ID Card via Camera")
            if not student_df.empty:
                sel_student_att = st.selectbox("Select Student to Mark Present:", student_df["Student ID"] + " - " + student_df["Name"])
                if st.button("Mark Student Present Now"):
                    st_id_scan = sel_student_att.split(" - ")[0]
                    st_name_scan = sel_student_att.split(" - ")[1]
                    att_row = {"Student ID": st_id_scan, "Date": cur_date_str, "Time_In": cur_time_str, "Status": "Present", "Late_Reason": "Camera Verified", "Sign_Mode": "Camera QR Portal", "Location_Verified": "Campus"}
                    att_df = pd.concat([att_df, pd.DataFrame([att_row])], ignore_index=True)
                    save_data(att_df, ATTENDANCE_FILE, "attendance_db")
                    st.success(f"✅ Marked Present for {st_name_scan} ({st_id_scan}) at {cur_time_str} IST!")
                    st.rerun()

        with t_tab2:
            t_name_sel = st.selectbox("Select Teacher Name:", teacher_df["Name"].tolist() if not teacher_df.empty else ["Faculty"])
            t_shift = st.selectbox("Select Shift Session:", ["Morning Shift (06:30 AM)", "Afternoon Shift (04:00 PM)", "Evening Shift (05:30 PM)"])
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                if st.button("🟢 Punch-In Shift Start"):
                    t_row = {"Teacher ID": "TCH-01", "Name": t_name_sel, "Date": cur_date_str, "Time_In": cur_time_str, "Time_Out": "Ongoing", "Shift": t_shift, "Status": "Present", "Late_Mins": "0", "Penalty_Deduction": "₹0.00", "Net_Earning_Today": "₹76.66"}
                    teacher_att_df = pd.concat([teacher_att_df, pd.DataFrame([t_row])], ignore_index=True)
                    save_data(teacher_att_df, TEACHER_ATT_FILE, "teacher_attendance")
                    st.success(f"✅ Punched at {cur_time_str} IST!")
                    st.rerun()
            with col_p2:
                if st.button("🔴 Punch-Out Shift Wrap-Up"):
                    st.success(f"✅ Shift Completed at {cur_time_str} IST!")

        with t_tab3:
            with st.form("pc_alloc_form", clear_on_submit=True):
                pc_st = st.selectbox("Select Student:", student_df["Student ID"] + " - " + student_df["Name"]) if not student_df.empty else None
                pc_no = st.selectbox("Assign PC Machine Number:", [f"PC-{i:02d}" for i in range(1, 21)])
                if st.form_submit_button("Assign PC Seat"):
                    if pc_st:
                        p_id = pc_st.split(" - ")[0]
                        p_name = pc_st.split(" - ")[1]
                        pc_row = {"Date": cur_date_str, "Student ID": p_id, "Student Name": p_name, "PC Machine No": pc_no, "Shift": "Current Shift", "Teacher Incharge": t_name_sel if 't_name_sel' in locals() else "Faculty"}
                        pc_alloc_df = pd.concat([pc_alloc_df, pd.DataFrame([pc_row])], ignore_index=True)
                        save_data(pc_alloc_df, PC_ALLOC_FILE, "pc_alloc_db")
                        st.success(f"✅ Assigned {pc_no} to {p_name}!")
                        st.rerun()

        with t_tab4:
            with st.form("weak_note_form", clear_on_submit=True):
                w_st = st.selectbox("Select Student:", student_df["Student ID"] + " - " + student_df["Name"]) if not student_df.empty else None
                w_topic = st.text_input("Weak Area / Topic (e.g. Slow Typing / Excel Formulas)")
                w_adv = st.text_area("Teacher Observation & Recommendation")
                if st.form_submit_button("Submit Private Note to Director"):
                    if w_st:
                        w_id = w_st.split(" - ")[0]
                        w_name = w_st.split(" - ")[1]
                        w_row = {"Date": cur_date_str, "Student ID": w_id, "Student Name": w_name, "Weak Topic / Area": w_topic, "Teacher Advice": w_adv, "Teacher Name": t_name_sel if 't_name_sel' in locals() else "Faculty"}
                        weak_notes_df = pd.concat([weak_notes_df, pd.DataFrame([w_row])], ignore_index=True)
                        save_data(weak_notes_df, WEAK_NOTES_FILE, "weak_notes_db")
                        st.success("✅ Private Note forwarded to Director Admin Panel!")
                        st.rerun()

        with t_tab5:
            with st.form("syllabus_form", clear_on_submit=True):
                sys_course = st.selectbox("Select Course Taught:", list(COURSE_CONFIG.keys()))
                sys_topics = st.multiselect("Select Topics Covered Today:", ALL_SYLLABUS_TOPICS, default=["Computer Basics / Fundamentals"])
                sys_class_type = st.radio("Class Type:", ["Practical Session", "Theory Session", "Both Practical & Theory", "Exam Taken"])
                if st.form_submit_button("Save Syllabus Record"):
                    topic_str = ", ".join(sys_topics) if sys_topics else "General Topics"
                    s_row = {"Date": cur_date_str, "Course": sys_course, "Topics Covered": topic_str, "Class Type": sys_class_type, "Teacher Incharge": t_name_sel if 't_name_sel' in locals() else "Faculty"}
                    syllabus_df = pd.concat([syllabus_df, pd.DataFrame([s_row])], ignore_index=True)
                    save_data(syllabus_df, SYLLABUS_LOG_FILE, "syllabus_logs")
                    st.success(f"✅ Saved: {topic_str}")
                    st.rerun()

# ---------------------------------------------------------
# 7. ADMIN CONTROL PANEL
# ---------------------------------------------------------
elif menu == "🔐 Admin Control Panel":
    st.header("🔐 Director Admin Control Panel")
    pwd = st.text_input("Enter Director Admin Password", type="password")
    if pwd == ADMIN_PWD:
        st.success("Welcome Director Chiranjeeb Hazarika Sir!")
        
        adm_tab1, adm_tab2, adm_tab3, adm_tab4, adm_tab5, adm_tab6 = st.tabs([
            "📋 All Students Directory",
            "✏️ Edit Student Profile & Address",
            "💵 Fee & Receipt Ledger",
            "🔴 Red Alert Defaulters (WhatsApp)", 
            "📌 Faculty Notes & Lab Activities",
            "🗑️ Reset Database"
        ])
        
        with adm_tab1:
            st.subheader("📋 All Registered Students Full Directory")
            if not student_df.empty:
                st.dataframe(student_df[["Student ID", "Name", "Father Name", "Mother Name", "Mobile No", "Full Address", "Course", "Join Date", "Net Fee", "Shift", "Status"]], use_container_width=True)
            else:
                st.info("No students registered yet.")

        with adm_tab2:
            st.subheader("✏️ Edit Student Profile, Parents & Full Address Information")
            if not student_df.empty:
                sel_edit_st = st.selectbox("Select Student to Edit:", student_df["Student ID"] + " - " + student_df["Name"])
                if sel_edit_st:
                    edit_id = sel_edit_st.split(" - ")[0]
                    curr_st = student_df[student_df["Student ID"] == edit_id].iloc[0]
                    
                    with st.form("edit_student_full_form"):
                        col_e1, col_e2 = st.columns(2)
                        with col_e1:
                            new_name = st.text_input("Student Name*", value=curr_st.get("Name", ""))
                            new_fname = st.text_input("Father's Name*", value=curr_st.get("Father Name", ""))
                            new_mname = st.text_input("Mother's Name*", value=curr_st.get("Mother Name", ""))
                            new_mob = st.text_input("Mobile Number*", value=curr_st.get("Mobile No", ""))
                            new_course = st.selectbox("Course", list(COURSE_CONFIG.keys()), index=list(COURSE_CONFIG.keys()).index(curr_st["Course"]) if curr_st.get("Course") in COURSE_CONFIG else 0)
                        
                        with col_e2:
                            new_vill = st.text_input("Village / Town*", value=curr_st.get("Vill Town", ""))
                            new_po = st.text_input("Post Office", value=curr_st.get("PO", ""))
                            new_ps = st.text_input("Police Station", value=curr_st.get("PS", "THELAMARA"))
                            new_dist = st.text_input("District", value=curr_st.get("District", "Sonitpur"))
                            new_shift = st.selectbox("Shift Assigned", ["Morning (06:30-08:00 AM)", "Afternoon (04:00-05:30 PM)", "Evening (05:30-07:00 PM)"], index=0)
                            
                        col_e3, col_e4 = st.columns(2)
                        with col_e3:
                            new_tot_fee = st.number_input("Total Fee (₹)", min_value=0.0, value=float(curr_st["Total Fee"]) if curr_st.get("Total Fee") else 2550.0)
                            new_disc = st.number_input("Discount Allowed (₹)", min_value=0.0, value=float(curr_st["Discount"]) if curr_st.get("Discount") else 0.0)
                        with col_e4:
                            new_status = st.selectbox("Student Status", ["Active", "Completed", "Dropped"], index=0 if curr_st.get("Status") == "Active" else 1)

                        if st.form_submit_button("💾 Save & Update Full Student Information"):
                            full_addr_up = f"{new_vill}, {new_po}, {new_ps}, {new_dist}".upper()
                            student_df.loc[student_df["Student ID"] == edit_id, "Name"] = new_name.upper()
                            student_df.loc[student_df["Student ID"] == edit_id, "Father Name"] = new_fname.upper()
                            student_df.loc[student_df["Student ID"] == edit_id, "Mother Name"] = new_mname.upper()
                            student_df.loc[student_df["Student ID"] == edit_id, "Mobile No"] = new_mob
                            student_df.loc[student_df["Student ID"] == edit_id, "Course"] = new_course
                            student_df.loc[student_df["Student ID"] == edit_id, "Vill Town"] = new_vill.upper()
                            student_df.loc[student_df["Student ID"] == edit_id, "PO"] = new_po.upper()
                            student_df.loc[student_df["Student ID"] == edit_id, "PS"] = new_ps.upper()
                            student_df.loc[student_df["Student ID"] == edit_id, "District"] = new_dist.upper()
                            student_df.loc[student_df["Student ID"] == edit_id, "Full Address"] = full_addr_up
                            student_df.loc[student_df["Student ID"] == edit_id, "Shift"] = new_shift
                            student_df.loc[student_df["Student ID"] == edit_id, "Total Fee"] = str(new_tot_fee)
                            student_df.loc[student_df["Student ID"] == edit_id, "Discount"] = str(new_disc)
                            student_df.loc[student_df["Student ID"] == edit_id, "Net Fee"] = str(new_tot_fee - new_disc)
                            student_df.loc[student_df["Student ID"] == edit_id, "Status"] = new_status
                            
                            save_data(student_df, STUDENT_MASTER_FILE, "students_db")
                            st.success(f"✅ Successfully Updated Profile & Address for Roll ID: {edit_id}!")
                            st.rerun()
            else:
                st.info("No registered students available to edit.")

        with adm_tab3:
            st.subheader("💵 Comprehensive Fee Collection & Receipt Ledger")
            if not fee_df.empty:
                st.dataframe(fee_df, use_container_width=True)

        with adm_tab4:
            st.subheader("🔴 Red Alert Fee Defaulters")
            if not student_df.empty:
                for idx, row in student_df.iterrows():
                    sid = row["Student ID"]
                    net_f = float(row["Net Fee"]) if row["Net Fee"] else 0.0
                    paid = sum([float(amt) for amt in fee_df[fee_df["Student ID"] == sid]["Amount Paid"] if amt])
                    due = net_f - paid
                    if due > 0:
                        wa_msg = f"Hello {row['Name']}, your fee balance of Rs.{due:.0f} is pending at Soft Tech Computers & ZTC. Please clear it soon."
                        encoded_msg = wa_msg.replace(" ", "%20")
                        wa_url = f"https://wa.me/91{row['Mobile No']}?text={encoded_msg}"
                        col_a, col_b = st.columns([3, 1])
                        col_a.markdown(f"🔴 **{row['Name']} ({sid})** - Pending: **₹{due:.2f}**")
                        col_b.markdown(f'<a href="{wa_url}" target="_blank" style="background:#25D366; color:white; padding:6px 12px; border-radius:6px; text-decoration:none; font-weight:bold; font-size:12px;">📲 Send WhatsApp</a>', unsafe_allow_html=True)

        with adm_tab5:
            st.subheader("📌 Faculty Confidential Notes on Weak Students")
            if not weak_notes_df.empty:
                st.dataframe(weak_notes_df, use_container_width=True)

        with adm_tab6:
            st.subheader("🗑️ Reset Database")
            if st.checkbox("মই সঁচাকৈয়ে সকলো পুৰণি ছাত্ৰ ডেটা Clear কৰি নতুনকৈ এণ্ট্ৰি কৰিব বিচাৰোঁ।"):
                if st.button("🔴 CLEAR ALL DATA NOW"):
                    student_df = pd.DataFrame(columns=student_cols)
                    fee_df = pd.DataFrame(columns=fee_cols)
                    att_df = pd.DataFrame(columns=attendance_cols)
                    save_data(student_df, STUDENT_MASTER_FILE, "students_db")
                    save_data(fee_df, FEE_LOG_FILE, "fees_db")
                    save_data(att_df, ATTENDANCE_FILE, "attendance_db")
                    st.success("🎉 ডেটাবেছ Clear কৰা হ'ল!")
                    st.rerun()
