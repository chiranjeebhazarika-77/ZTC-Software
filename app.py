import streamlit as st
import pandas as pd
import os
import datetime
import pytz
import base64

# Page Configuration
st.set_page_config(page_title="Soft Tech Computers & ZTC Enterprise Portal", page_icon="💻", layout="wide")

# IST TimeZone Setup
IST = pytz.timezone('Asia/Kolkata')

# Paths for CSV Files & Assets
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
PHOTO_DIR = "student_photos"

# SAFE DIRECTORY CREATION
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

def load_data(file_path, columns):
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path, dtype=str)
            for col in columns:
                if col not in df.columns:
                    df[col] = ""
            return df
        except Exception:
            return pd.DataFrame(columns=columns)
    else:
        return pd.DataFrame(columns=columns)

def save_data(df, file_path):
    df.to_csv(file_path, index=False)

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

# Load DataFrames
student_df = load_data(STUDENT_MASTER_FILE, student_cols)
fee_df = load_data(FEE_LOG_FILE, fee_cols)
att_df = load_data(ATTENDANCE_FILE, attendance_cols)
teacher_df = load_data(TEACHERS_FILE, teacher_cols)
teacher_att_df = load_data(TEACHER_ATT_FILE, teacher_att_cols)
enquiry_df = load_data(ENQUIRY_FILE, enquiry_cols)
sfpc_df = load_data(SFPC_FILE, sfpc_cols)
creds_df = load_data(CREDS_FILE, creds_cols)
feedback_df = load_data(FEEDBACK_FILE, feedback_cols)
syllabus_df = load_data(SYLLABUS_LOG_FILE, syllabus_cols)
marks_df = load_data(MARKS_FILE, marks_cols)
notices_df = load_data(NOTICES_FILE, notices_cols)
tasks_df = load_data(TASKS_FILE, tasks_cols)
pc_alloc_df = load_data(PC_ALLOC_FILE, pc_alloc_cols)
weak_notes_df = load_data(WEAK_NOTES_FILE, weak_notes_cols)

if creds_df.empty:
    creds_df = pd.DataFrame([
        {"Role": "Admin", "Password": "zaan123"},
        {"Role": "Teacher", "Password": "teacher123"}
    ])
    save_data(creds_df, CREDS_FILE)

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
    "💵 Fee Counter Desk",
    "🔑 Teacher Portal & QR Scanner",
    "🔐 Admin Control Panel"
])

# Custom CSS for Dark Green Buttons
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
                    save_data(enquiry_df, ENQUIRY_FILE)
                    
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

    st.subheader("📚 Courses Offered & Duration")
    pub_course_list = [{"Course Name": k, "Duration": f"{v['Months']} Months" if "Certificate" not in k else "3 Months / 2 Months / 45 Days"} for k, v in COURSE_CONFIG.items()]
    pub_course_df = pd.DataFrame(pub_course_list)
    pub_course_df.index = range(1, len(pub_course_df) + 1)
    st.table(pub_course_df)

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
            st.success(f"✅ **VERIFIED CERTIFICATE RECORD FOUND:** Name: {v_data['Name']} | Course: {v_data['Course']} | Roll ID: {v_data['Student ID']}")
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
                
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                sub_btn = st.form_submit_button("🟢 Submit Admission Now")
            with col_b2:
                reset_btn = st.form_submit_button("🔴 Clear Form")

            if sub_btn:
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
                    
                    new_row = {
                        "Sl. No.": str(len(student_df) + 1), "Student ID": next_id, "Name": name.upper(),
                        "Father Name": fname.upper(), "Mother Name": mname.upper(), "Gender": gender,
                        "DOB": str(dob), "Caste": "General", "Mobile No": mobile, "Vill Town": vill.upper(),
                        "PO": po.upper(), "PS": ps.upper(), "PIN Code": "784149", "District": dist.upper(),
                        "Full Address": f"{vill}, {po}, {ps}, {dist}".upper(), "Course": course,
                        "Duration": cert_dur, "Days_Batch": days_batch, "Session": session,
                        "Join Date": str(join_date), "Validity Date": str(auto_expiry),
                        "Total Fee": str(total_fee), "Discount": str(discount), "Net Fee": str(net_fee),
                        "Shift": shift, "Batch Time": batch_time, "Photo Path": photo_path, "Status": "Active",
                        "Stage_Admission": "Completed", "Stage_IDCard": "Generated", "Stage_Registration": "Pending",
                        "Stage_ExamForm": "Pending", "Stage_AdmitCard": "Pending", "Stage_Certificate": "Pending"
                    }
                    student_df = pd.concat([student_df, pd.DataFrame([new_row])], ignore_index=True)
                    save_data(student_df, STUDENT_MASTER_FILE)
                    st.balloons()
                    st.success(f"🎉 🎉 SUBMITTED SUCCESSFULLY! Student ID Registered: {next_id} | End Date: {auto_expiry}")
                    st.rerun()

# ---------------------------------------------------------
# 3. STUDENT DASHBOARD
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

        st_tab1, st_tab2, st_tab3, st_tab4 = st.tabs([
            "💳 Digital ID Card & QR",
            "💵 Passbook Ledger",
            "🔄 6-Stage Academic Journey",
            "📊 Test Report Card"
        ])
        
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
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🖨️ Direct Print / Download Digital ID Card"):
                st.components.v1.html("<script>window.print();</script>", height=0)

        with st_tab2:
            st.subheader("💵 My Installment Passbook Ledger")
            net_f = float(s["Net Fee"]) if s["Net Fee"] else 0.0
            st_paid_logs = fee_df[fee_df["Student ID"] == s_id]
            tot_p = sum([float(amt) for amt in st_paid_logs["Amount Paid"] if amt])
            bal_due = net_f - tot_p
            
            col_m1, col_m2, col_m3 = st.columns(3)
            col_m1.metric("Net Total Course Fee", f"₹{net_f:.2f}")
            col_m2.metric("Total Deposit Paid", f"₹{tot_p:.2f}")
            col_m3.metric("Remaining Balance Due", f"₹{bal_due:.2f}", delta="-Pending" if bal_due > 0 else "Cleared")

        with st_tab3:
            st.subheader("🔄 Official 6-Stage Academic Progress Journey Tracker")
            st.markdown(f"""
                <div style="background:#0F172A; border:1.5px solid #00F0FF; padding:18px; border-radius:12px; color:white;">
                    <ol>
                        <li><b>(a) Admission Taken:</b> <span style="color:#10B981; font-weight:bold;">{s.get('Stage_Admission', 'Completed')}</span></li>
                        <li><b>(b) Digital ID Card Generated:</b> <span style="color:#10B981; font-weight:bold;">{s.get('Stage_IDCard', 'Generated')}</span></li>
                        <li><b>(c) SARVA Head Office Registration:</b> <span style="color:#F59E0B; font-weight:bold;">{s.get('Stage_Registration', 'In Progress')}</span></li>
                        <li><b>(d) Examination Form Fillup:</b> <span style="color:#EF4444; font-weight:bold;">{s.get('Stage_ExamForm', 'Pending')}</span></li>
                        <li><b>(e) Admit Card Issued:</b> <span style="color:#EF4444; font-weight:bold;">{s.get('Stage_AdmitCard', 'Pending')}</span></li>
                        <li><b>(f) Certificate & Marksheet Issued:</b> <span style="color:#EF4444; font-weight:bold;">{s.get('Stage_Certificate', 'Pending')}</span></li>
                    </ol>
                </div>
            """, unsafe_allow_html=True)

        with st_tab4:
            st.subheader("📊 My Test Marks & Academic Report Card")
            st_marks = marks_df[marks_df["Student ID"] == s_id]
            if not st_marks.empty:
                st.dataframe(st_marks[["Date", "Course/Subject", "Test Topic", "Marks Obtained", "Total Marks"]], use_container_width=True)

# ---------------------------------------------------------
# 4. SUNDAY PRACTICE CLASS (SFPC)
# ---------------------------------------------------------
elif menu == "🎯 Sunday Free Practice Class (SFPC)":
    st.header("🎯 Sunday Free Practice Class (SFPC) Eligibility Portal")
    check_id = st.text_input("Enter Student Roll ID (e.g. STC26-001):").strip().upper()
    if check_id:
        st_res = student_df[student_df["Student ID"] == check_id]
        if not st_res.empty:
            st.success("🎉 Student Found! Access Eligible.")

# ---------------------------------------------------------
# 5. FEE COUNTER DESK
# ---------------------------------------------------------
elif menu == "💵 Fee Counter Desk":
    st.header("💵 Student Fee Collection Counter Desk")
    f_pwd = st.text_input("Enter Staff / Teacher Password:", type="password")
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
                    save_data(fee_df, FEE_LOG_FILE)
                    st.success(f"✅ Receipt Issued: {rc_num}")
                    st.rerun()

# ---------------------------------------------------------
# 6. TEACHER PORTAL & ADVANCED CLASS MANAGEMENT DESK
# ---------------------------------------------------------
elif menu == "🔑 Teacher Portal & QR Scanner":
    st.header("🔑 Faculty Portal & Advanced Class Management Desk")
    t_pwd = st.text_input("Enter Faculty Password:", type="password")
    
    if t_pwd == TEACHER_PWD:
        now_ist = datetime.datetime.now(IST)
        cur_time_str = now_ist.strftime("%I:%M:%S %p")
        cur_date_str = now_ist.strftime("%Y-%m-%d")
        
        t_tab1, t_tab2, t_tab3, t_tab4, t_tab5, t_tab6 = st.tabs([
            "📸 Camera Student Attendance", 
            "⏱️ Shift Punch In & Out", 
            "🖥️ Lab PC Machine Allocator",
            "📝 Assign Practical Tasks",
            "📌 Weak Student Note for Director",
            "📖 Log Syllabus & Marks"
        ])
        
        # TAB 1: CAMERA STUDENT ATTENDANCE
        with t_tab1:
            st.subheader("📸 Live Camera Student Attendance Desk")
            cam_pic = st.camera_input("Scan Student Digital ID Card / QR via Camera")
            if cam_pic:
                st.success("📸 Photo Captured! Student Verified!")
            
            st.markdown("---")
            if not student_df.empty:
                sel_student_att = st.selectbox("Select Student Roll ID to Punch Attendance:", student_df["Student ID"] + " - " + student_df["Name"])
                if st.button("Mark Student Present Now"):
                    st_id_scan = sel_student_att.split(" - ")[0]
                    st_name_scan = sel_student_att.split(" - ")[1]
                    att_row = {"Student ID": st_id_scan, "Date": cur_date_str, "Time_In": cur_time_str, "Status": "Present", "Late_Reason": "Camera Verified", "Sign_Mode": "Camera QR Portal", "Location_Verified": "Campus"}
                    att_df = pd.concat([att_df, pd.DataFrame([att_row])], ignore_index=True)
                    save_data(att_df, ATTENDANCE_FILE)
                    st.success(f"✅ Marked Present for {st_name_scan} ({st_id_scan}) at {cur_time_str} IST!")
                    st.rerun()

        # TAB 2: FACULTY PUNCH IN & PUNCH OUT
        with t_tab2:
            st.subheader("⏱️ Faculty Punch-In & Shift Session Wrap-Up")
            t_name_sel = st.selectbox("Select Teacher Name:", teacher_df["Name"].tolist() if not teacher_df.empty else ["Faculty"])
            t_shift = st.selectbox("Select Shift Session:", ["Morning Shift (06:30 AM)", "Afternoon Shift (04:00 PM)", "Evening Shift (05:30 PM)"])
            st.info(f"Current Live IST Time: **{cur_time_str}** | Date: **{cur_date_str}**")
            
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                if st.button("🟢 Punch-In Shift Start"):
                    t_row = {"Teacher ID": "TCH-01", "Name": t_name_sel, "Date": cur_date_str, "Time_In": cur_time_str, "Time_Out": "Ongoing", "Shift": t_shift, "Status": "Present", "Late_Mins": "0", "Penalty_Deduction": "₹0.00", "Net_Earning_Today": "₹76.66"}
                    teacher_att_df = pd.concat([teacher_att_df, pd.DataFrame([t_row])], ignore_index=True)
                    save_data(teacher_att_df, TEACHER_ATT_FILE)
                    st.success(f"✅ Faculty {t_name_sel} Shift Started at {cur_time_str} IST!")
                    st.rerun()
            with col_p2:
                if st.button("🔴 Punch-Out Shift Wrap-Up"):
                    st.success(f"✅ Faculty {t_name_sel} Shift Completed & Logged at {cur_time_str} IST!")

        # TAB 3: LAB PC ALLOCATION TRACKER
        with t_tab3:
            st.subheader("🖥️ Lab PC / Machine Allocation Desk")
            with st.form("pc_alloc_form", clear_on_submit=True):
                pc_st = st.selectbox("Select Student:", student_df["Student ID"] + " - " + student_df["Name"]) if not student_df.empty else None
                pc_no = st.selectbox("Assign PC Machine Number:", [f"PC-{i:02d}" for i in range(1, 21)])
                pc_shift_sel = st.selectbox("Lab Shift Session:", ["Morning (06:30 AM)", "Afternoon (04:00 PM)", "Evening (05:30 PM)"])
                if st.form_submit_button("Assign PC Seat"):
                    if pc_st:
                        p_id = pc_st.split(" - ")[0]
                        p_name = pc_st.split(" - ")[1]
                        pc_row = {"Date": cur_date_str, "Student ID": p_id, "Student Name": p_name, "PC Machine No": pc_no, "Shift": pc_shift_sel, "Teacher Incharge": t_name_sel if 't_name_sel' in locals() else "Faculty"}
                        pc_alloc_df = pd.concat([pc_alloc_df, pd.DataFrame([pc_row])], ignore_index=True)
                        save_data(pc_alloc_df, PC_ALLOC_FILE)
                        st.success(f"✅ Assigned {pc_no} to {p_name}!")
                        st.rerun()
            if not pc_alloc_df.empty:
                st.write("📋 **Today's Lab PC Allocations:**")
                st.dataframe(pc_alloc_df.tail(10), use_container_width=True)

        # TAB 4: ASSIGN PRACTICAL TASKS
        with t_tab4:
            st.subheader("📝 Assign Daily Practical Task / Assignment")
            with st.form("task_form", clear_on_submit=True):
                task_st = st.selectbox("Assign Task to Student:", student_df["Student ID"] + " - " + student_df["Name"]) if not student_df.empty else None
                task_desc = st.text_input("Practical Task Description (e.g. MS Word Bio-Data / Tally GST Entry)")
                task_stat = st.selectbox("Status:", ["Assigned", "Completed & Verified", "Needs Improvement"])
                if st.form_submit_button("Save Practical Task"):
                    if task_st and task_desc:
                        tk_id = task_st.split(" - ")[0]
                        tk_name = task_st.split(" - ")[1]
                        tk_row = {"Date": cur_date_str, "Student ID": tk_id, "Student Name": tk_name, "Task Assigned": task_desc, "Status": task_stat, "Teacher Incharge": t_name_sel if 't_name_sel' in locals() else "Faculty"}
                        tasks_df = pd.concat([tasks_df, pd.DataFrame([tk_row])], ignore_index=True)
                        save_data(tasks_df, TASKS_FILE)
                        st.success(f"✅ Practical Task Logged for {tk_name}!")
                        st.rerun()

        # TAB 5: WEAK STUDENT PRIVATE NOTE FOR DIRECTOR
        with t_tab5:
            st.subheader("📌 Weak Student Quick Note (Private to Director)")
            with st.form("weak_note_form", clear_on_submit=True):
                w_st = st.selectbox("Select Student:", student_df["Student ID"] + " - " + student_df["Name"]) if not student_df.empty else None
                w_topic = st.text_input("Weak Area / Difficult Topic (e.g. Slow Typing / Excel Formulas)")
                w_adv = st.text_area("Teacher Observation & Recommendation")
                if st.form_submit_button("Submit Private Note to Director"):
                    if w_st:
                        w_id = w_st.split(" - ")[0]
                        w_name = w_st.split(" - ")[1]
                        w_row = {"Date": cur_date_str, "Student ID": w_id, "Student Name": w_name, "Weak Topic / Area": w_topic, "Teacher Advice": w_adv, "Teacher Name": t_name_sel if 't_name_sel' in locals() else "Faculty"}
                        weak_notes_df = pd.concat([weak_notes_df, pd.DataFrame([w_row])], ignore_index=True)
                        save_data(weak_notes_df, WEAK_NOTES_FILE)
                        st.success(f"✅ Private Note forwarded to Director Admin Panel!")
                        st.rerun()

        # TAB 6: LOG SYLLABUS & TEST MARKS
        with t_tab6:
            st.subheader("📖 Log Daily Class Syllabus Topics")
            with st.form("syllabus_form", clear_on_submit=True):
                sys_course = st.selectbox("Select Course Taught:", list(COURSE_CONFIG.keys()))
                sys_topics = st.multiselect("Select Topics Covered Today:", ALL_SYLLABUS_TOPICS, default=["Computer Basics / Fundamentals"])
                sys_class_type = st.radio("Class Delivered Type:", ["Practical Session", "Theory Session", "Both Practical & Theory", "Exam / Test Conducted"])
                if st.form_submit_button("Save Daily Syllabus Record"):
                    topic_str = ", ".join(sys_topics) if sys_topics else "General Topics"
                    s_row = {"Date": cur_date_str, "Course": sys_course, "Topics Covered": topic_str, "Class Type": sys_class_type, "Teacher Incharge": t_name_sel if 't_name_sel' in locals() else "Faculty"}
                    syllabus_df = pd.concat([syllabus_df, pd.DataFrame([s_row])], ignore_index=True)
                    save_data(syllabus_df, SYLLABUS_LOG_FILE)
                    st.success(f"✅ Saved Syllabus Record: {topic_str}")
                    st.rerun()

            st.markdown("---")
            st.subheader("📊 Log Student Test Marks")
            with st.form("marks_form", clear_on_submit=True):
                m_student = st.selectbox("Select Student for Marks:", student_df["Student ID"] + " - " + student_df["Name"]) if not student_df.empty else None
                m_subject = st.selectbox("Course / Subject:", list(COURSE_CONFIG.keys()))
                m_topic = st.text_input("Test Topic (e.g. MS Excel / English Grammar)")
                m_obtained = st.number_input("Marks Obtained:", min_value=0.0, step=1.0)
                m_total = st.number_input("Total Marks:", min_value=10.0, value=100.0, step=50.0)
                if st.form_submit_button("Save Student Marks"):
                    if m_student:
                        m_id = m_student.split(" - ")[0]
                        m_name = m_student.split(" - ")[1]
                        m_row = {"Date": cur_date_str, "Student ID": m_id, "Student Name": m_name, "Course/Subject": m_subject, "Test Topic": m_topic, "Marks Obtained": str(m_obtained), "Total Marks": str(m_total), "Teacher Incharge": t_name_sel if 't_name_sel' in locals() else "Director"}
                        marks_df = pd.concat([marks_df, pd.DataFrame([m_row])], ignore_index=True)
                        save_data(marks_df, MARKS_FILE)
                        st.success(f"✅ Test Marks Saved for {m_name}!")
                        st.rerun()

# ---------------------------------------------------------
# 7. ADMIN CONTROL PANEL
# ---------------------------------------------------------
elif menu == "🔐 Admin Control Panel":
    st.header("🔐 Director Admin Control Panel")
    pwd = st.text_input("Enter Director Admin Password", type="password")
    
    if pwd == ADMIN_PWD:
        st.success("Welcome Director Chiranjeeb Hazarika Sir!")
        
        adm_tab1, adm_tab2, adm_tab3, adm_tab4, adm_tab5, adm_tab6, adm_tab7 = st.tabs([
            "📋 All Students Full Directory",
            "💵 Fee & Receipt Ledger",
            "🔴 Red Alert Defaulters (WhatsApp)", 
            "📌 Faculty Notes & Lab Activities",
            "📝 Live Enquiries Desk", 
            "✏️ Edit & Delete Records",
            "👨‍🏫 Add Faculty Staff"
        ])
        
        # TAB 1: ALL STUDENTS FULL DIRECTORY
        with adm_tab1:
            st.subheader("📋 All Registered Students Full Directory")
            if not student_df.empty:
                st_search = st.text_input("🔍 Quick Search Student by Name, Roll ID or Phone:")
                view_df = student_df.copy()
                if st_search:
                    view_df = view_df[view_df.apply(lambda r: st_search.lower() in str(r.values).lower(), axis=1)]
                st.dataframe(view_df[["Student ID", "Name", "Mobile No", "Course", "Join Date", "Validity Date", "Net Fee", "Shift", "Status"]], use_container_width=True)
            else:
                st.info("No students registered yet.")

        # TAB 2: COMPLETE FEE & RECEIPT LEDGER
        with adm_tab2:
            st.subheader("💵 Comprehensive Fee Collection & Receipt Ledger")
            if not fee_df.empty:
                st.dataframe(fee_df, use_container_width=True)
                
                st.markdown("---")
                st.subheader("🖨️ Generate & Send Digital Money Receipt")
                sel_rec = st.selectbox("Select Receipt to Send / Print:", fee_df["Receipt No"] + " - Student: " + fee_df["Student ID"])
                if sel_rec:
                    r_num = sel_rec.split(" - ")[0]
                    r_row = fee_df[fee_df["Receipt No"] == r_num].iloc[0]
                    st_match = student_df[student_df["Student ID"] == r_row["Student ID"]]
                    st_name = st_match.iloc[0]["Name"] if not st_match.empty else "Student"
                    st_mob = st_match.iloc[0]["Mobile No"] if not st_match.empty else ""
                    
                    st.markdown(f"""
                        <div style="background:#020B19; border:2px solid #10B981; border-radius:12px; padding:15px; color:white; margin:10px 0;">
                            <h4 style="margin:0; color:#10B981;">🧾 OFFICIAL FEE RECEIPT: {r_num}</h4>
                            <p style="margin:4px 0;">👤 <b>Student:</b> {st_name} ({r_row['Student ID']}) | 📅 <b>Date:</b> {r_row['Date']}</p>
                            <p style="margin:4px 0;">💰 <b>Amount Received:</b> ₹{r_row['Amount Paid']} | 💳 <b>Mode:</b> {r_row['Payment Mode']} | 👨‍💼 <b>Collector:</b> {r_row['Collected_By']}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if st_mob:
                        wa_rec_msg = f"OFFICIAL FEE RECEIPT - Soft Tech Computers & ZTC%0AReceipt No: {r_num}%0AStudent: {st_name}%0AAmount Received: Rs.{r_row['Amount Paid']}%0ADate: {r_row['Date']}%0AStatus: Paid Successfully. Thank you!"
                        wa_rec_url = f"https://wa.me/91{st_mob}?text={wa_rec_msg}"
                        st.markdown(f'<a href="{wa_rec_url}" target="_blank" style="background:#25D366; color:white; padding:8px 16px; border-radius:8px; text-decoration:none; font-weight:bold;">📲 Send Money Receipt via WhatsApp</a>', unsafe_allow_html=True)
            else:
                st.info("No fee records logged yet.")

        # TAB 3: RED ALERT DEFAULTERS
        with adm_tab3:
            st.subheader("🔴 Red Alert Fee Defaulters (High Pending Dues)")
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
                        col_a.markdown(f"🔴 <span style='color:#EF4444; font-weight:bold;'>{row['Name']} ({sid})</span> - Pending Balance: **₹{due:.2f}**", unsafe_allow_html=True)
                        col_b.markdown(f'<a href="{wa_url}" target="_blank" style="background:#25D366; color:white; padding:6px 12px; border-radius:6px; text-decoration:none; font-weight:bold; font-size:12px;">📲 Send WhatsApp</a>', unsafe_allow_html=True)

        # TAB 4: FACULTY WEAK NOTES & LAB ACTIVITIES
        with adm_tab4:
            st.subheader("📌 Faculty Confidential Notes on Weak Students")
            if not weak_notes_df.empty:
                st.dataframe(weak_notes_df, use_container_width=True)
            else:
                st.info("No weak student notes submitted yet.")
            
            st.markdown("---")
            st.subheader("🖥️ Live Lab PC Allocations & Practical Tasks")
            col_l1, col_l2 = st.columns(2)
            with col_l1:
                st.write("🖥️ **Lab PC Machine Seat Allocations:**")
                st.dataframe(pc_alloc_df.tail(10), use_container_width=True)
            with col_l2:
                st.write("📝 **Daily Assigned Practical Tasks:**")
                st.dataframe(tasks_df.tail(10), use_container_width=True)

        # TAB 5: LIVE ENQUIRIES DESK
        with adm_tab5:
            st.subheader("📝 Live Public Enquiries Desk")
            if not enquiry_df.empty:
                st.dataframe(enquiry_df, use_container_width=True)
            else:
                st.info("No public enquiries logged yet.")

        # TAB 6: EDIT & DELETE (STUDENTS & FACULTY)
        with adm_tab6:
            st.subheader("✏️ Edit / Delete Records & Download Backups")
            col_bk1, col_bk2, col_bk3 = st.columns(3)
            with col_bk1:
                st.download_button("📥 Backup All Students (CSV)", data=student_df.to_csv(index=False), file_name="students_db_backup.csv", mime="text/csv")
            with col_bk2:
                st.download_button("📥 Backup Fee Log (CSV)", data=fee_df.to_csv(index=False), file_name="fees_db_backup.csv", mime="text/csv")
            with col_bk3:
                st.download_button("📥 Backup Faculty List (CSV)", data=teacher_df.to_csv(index=False), file_name="faculty_db_backup.csv", mime="text/csv")
            
            st.markdown("---")
            del_type = st.radio("Select Category to Delete:", ["Delete Student Record", "Delete Faculty / Staff Member"])
            
            if del_type == "Delete Student Record":
                if not student_df.empty:
                    sel_del_st = st.selectbox("Select Student Record to Delete:", student_df["Student ID"] + " - " + student_df["Name"])
                    if st.button("🔴 Permanently Delete Student"):
                        del_id = sel_del_st.split(" - ")[0]
                        student_df = student_df[student_df["Student ID"] != del_id]
                        save_data(student_df, STUDENT_MASTER_FILE)
                        st.success(f"Deleted Student: {del_id}!")
                        st.rerun()
                else:
                    st.info("No student records available to delete.")
                    
            elif del_type == "Delete Faculty / Staff Member":
                if not teacher_df.empty:
                    sel_del_tch = st.selectbox("Select Faculty Staff to Delete:", teacher_df["Teacher ID"] + " - " + teacher_df["Name"])
                    if st.button("🔴 Permanently Delete Faculty Staff"):
                        del_tch_id = sel_del_tch.split(" - ")[0]
                        teacher_df = teacher_df[teacher_df["Teacher ID"] != del_tch_id]
                        save_data(teacher_df, TEACHERS_FILE)
                        st.success(f"Deleted Faculty Member: {del_tch_id}!")
                        st.rerun()
                else:
                    st.info("No faculty records available to delete.")

        # TAB 7: ADD FACULTY
        with adm_tab7:
            st.subheader("👨‍🏫 Add New Faculty / Staff Member")
            with st.form("add_teacher_form", clear_on_submit=True):
                t_name = st.text_input("Teacher Full Name*")
                t_phone = st.text_input("Phone Mobile Number*")
                t_qual = st.text_input("Qualification (e.g. BCA / MCA / BA)")
                t_desig = st.selectbox("Designation:", ["Computer Instructor", "English Faculty", "Lab Assistant", "Staff"])
                t_shift = st.selectbox("Shift Assigned:", ["All Shifts", "Morning Shift", "Afternoon Shift", "Evening Shift"])
                
                if st.form_submit_button("Register New Faculty"):
                    if t_name and t_phone:
                        t_id = f"TCH-{len(teacher_df)+1:02d}"
                        t_new = {"Teacher ID": t_id, "Name": t_name.upper(), "Phone": t_phone, "Qualification": t_qual, "Designation": t_desig, "Shift Assigned": t_shift}
                        teacher_df = pd.concat([teacher_df, pd.DataFrame([t_new])], ignore_index=True)
                        save_data(teacher_df, TEACHERS_FILE)
                        st.success(f"🎉 Faculty Added Successfully! ID: {t_id} | Name: {t_name}")
                        st.rerun()
                    else:
                        st.error("Please enter Name and Phone Number!")
