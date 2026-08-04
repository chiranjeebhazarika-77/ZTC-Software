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
ENQUIRY_FILE = "enquiries_db.csv"
SFPC_FILE = "sfpc_db.csv"
CREDS_FILE = "creds_db.csv"
FEEDBACK_FILE = "feedback_db.csv"
SYLLABUS_LOG_FILE = "syllabus_logs.csv"
MARKS_FILE = "marks_db.csv"
NOTICES_FILE = "notices_db.csv"
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
student_cols = ["Sl. No.", "Student ID", "Name", "Father Name", "Mother Name", "Gender", "DOB", "Caste", "Mobile No", "Vill Town", "PO", "PS", "PIN Code", "District", "Full Address", "Course", "Duration", "Days_Batch", "Session", "Join Date", "Validity Date", "Total Fee", "Discount", "Net Fee", "Shift", "Batch Time", "Photo Path", "Status"]
fee_cols = ["Receipt No", "Student ID", "Date", "Amount Paid", "Payment Mode", "Collected_By", "Remarks"]
attendance_cols = ["Student ID", "Date", "Time_In", "Status", "Late_Reason", "Sign_Mode", "Location_Verified"]
teacher_cols = ["Teacher ID", "Name", "Phone", "Qualification", "Designation", "Shift Assigned"]
teacher_att_cols = ["Teacher ID", "Name", "Date", "Time_In", "Shift", "Status", "Late_Mins", "Penalty_Deduction", "Net_Earning_Today"]
enquiry_cols = ["Date", "Name", "Mobile", "Course Interested", "Is ZTC Student", "Village/Address", "Status"]
sfpc_cols = ["Date", "Student ID", "Student Name", "PC Machine No", "Topic Practiced", "Teacher Incharge"]
creds_cols = ["Role", "Password"]
feedback_cols = ["Date", "Student ID", "Student Name", "Teacher Name", "Theory Written", "Rating_Stars", "Comments"]
syllabus_cols = ["Date", "Course", "Topics Covered", "Class Type", "Teacher Incharge"]
marks_cols = ["Date", "Student ID", "Student Name", "Course/Subject", "Test Topic", "Marks Obtained", "Total Marks", "Teacher Incharge"]
notices_cols = ["Date", "Notice Title", "Notice Content", "Category", "Posted By"]

# Load DataFrames
student_df = load_data(STUDENT_MASTER_FILE, student_cols)
fee_df = load_data(FEE_LOG_FILE, fee_cols)
att_df = load_data(ATTENDANCE_FILE, attendance_cols)
teacher_df = load_data(TEACHERS_FILE, teacher_cols)
teacher_att_df = load_data("teacher_attendance.csv", teacher_att_cols)
enquiry_df = load_data(ENQUIRY_FILE, enquiry_cols)
sfpc_df = load_data(SFPC_FILE, sfpc_cols)
creds_df = load_data(CREDS_FILE, creds_cols)
feedback_df = load_data(FEEDBACK_FILE, feedback_cols)
syllabus_df = load_data(SYLLABUS_LOG_FILE, syllabus_cols)
marks_df = load_data(MARKS_FILE, marks_cols)
notices_df = load_data(NOTICES_FILE, notices_cols)

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

# ---------------------------------------------------------
# 1. RESTORED AGOR PUBLIC DASHBOARD (WITH DP1, DP2, DP3)
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
    col_m2.metric("Total Enrolled", "500+ Students")
    col_m3.metric("Alumni Network", "350+ Students")
    col_m4.metric("Certified Graduates", "200+ Certified")

    st.markdown("""
        <div style="background-color: #FEF3C7; border: 1.5px solid #F59E0B; padding: 8px 15px; border-radius: 10px; margin: 15px 0;">
            <marquee style="color: #B45309; font-weight: bold; font-size: 15px;">
                🏆 SPECIAL OFFER: ZTC Tuition Students Get 50% OFF on STC Admission! | Class 11 STC Computer Students Get 100% FREE Admission at ZTC! 🏆
            </marquee>
        </div>
    """, unsafe_allow_html=True)

    # HIGH-TECH COMBO OFFERS SHOWCASE CARD
    st.markdown("""
        <div style="display: flex; gap: 15px; flex-wrap: wrap; margin-bottom: 20px;">
            <div style="flex: 1; min-width: 280px; background: linear-gradient(135deg, #EFF6FF, #DBEAFE); border: 2px solid #2563EB; border-radius: 14px; padding: 18px; box-shadow: 0 4px 12px rgba(37,99,235,0.15);">
                <span style="background:#2563EB; color:white; padding:4px 12px; border-radius:12px; font-size:11px; font-weight:bold; letter-spacing:0.5px;">ZTC SPECIAL OFFER</span>
                <h4 style="color:#1E3A8A; margin:10px 0 4px 0; font-size:16px;">ZTC Tuition ➔ STC Computer</h4>
                <p style="margin:0; font-size:14px; color:#1E293B;">Get <b style="color:#2563EB; font-size:16px;">50% DISCOUNT</b> on STC Computer Course Admission Fee for all ZTC Tuition Students!</p>
            </div>
            <div style="flex: 1; min-width: 280px; background: linear-gradient(135deg, #ECFDF5, #D1FAE5); border: 2px solid #10B981; border-radius: 14px; padding: 18px; box-shadow: 0 4px 12px rgba(16,185,129,0.15);">
                <span style="background:#10B981; color:white; padding:4px 12px; border-radius:12px; font-size:11px; font-weight:bold; letter-spacing:0.5px;">CLASS 11 MEGA OFFER</span>
                <h4 style="color:#065F46; margin:10px 0 4px 0; font-size:16px;">Class 11 STC ➔ ZTC Tuition</h4>
                <p style="margin:0; font-size:14px; color:#1E293B;">Get <b style="color:#10B981; font-size:16px;">100% FREE Admission Fee</b> at ZTC Tuition when enrolled in STC Computer Class 11!</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # RESTORED DP1 & DP3 IMAGES (DIRECTOR'S MESSAGE & KEY TECH)
    dp3_b64 = get_image_base64("dp3")
    dp1_b64 = get_image_base64("dp1")
    
    col_img1, col_img2 = st.columns(2)
    with col_img1:
        if dp3_b64:
            st.markdown('<h4 style="color:#1E3A8A; margin:0 0 8px 0;">🛠️ Key Technologies Taught</h4>', unsafe_allow_html=True)
            st.markdown(f'<img src="{dp3_b64}" style="width:100%; border-radius:12px; border:2px solid #2563EB; box-shadow:0 0 10px rgba(37,99,235,0.2);">', unsafe_allow_html=True)
    with col_img2:
        if dp1_b64:
            st.markdown('<h4 style="color:#1E3A8A; margin:0 0 8px 0;">📜 Director\'s Message</h4>', unsafe_allow_html=True)
            st.markdown(f'<img src="{dp1_b64}" style="width:100%; border-radius:12px; border:2px solid #00F0FF; box-shadow:0 0 10px rgba(0,240,255,0.2);">', unsafe_allow_html=True)

    st.markdown("---")

    # SMALL COMPACT STUDENT OF THE MONTH BADGE
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

    # LIVE NOTICES
    if not notices_df.empty:
        st.subheader("📢 Institute Live Notice Board")
        for idx, n in notices_df.tail(2).iterrows():
            st.info(f"📌 **[{n['Date']}] {n['Notice Title']}** ({n['Category']})\n\n{n['Notice Content']}")

    st.subheader("📚 Courses Offered & Duration")
    pub_course_list = [{"Course Name": k, "Duration": f"{v['Months']} Months" if "Certificate" not in k else "3 Months / 2 Months / 45 Days"} for k, v in COURSE_CONFIG.items()]
    pub_course_df = pd.DataFrame(pub_course_list)
    pub_course_df.index = range(1, len(pub_course_df) + 1)
    st.table(pub_course_df)

    st.markdown("---")

    # SMART SEARCH BAR
    user_q = st.text_input("Ask Zaan AI / Search Student Roll No (e.g. 'Hiya Das', 'STC26-001'):")
    if user_q:
        q_clean = user_q.strip().lower()
        matched = False
        if not student_df.empty:
            for idx, r in student_df.iterrows():
                st_name = str(r["Name"]).lower()
                st_id = str(r["Student ID"]).lower()
                if st_name in q_clean or st_id in q_clean:
                    st.success(f"🔍 **Student Record Found:**")
                    st.markdown(f"""
                        <div style="background:#0F172A; border:2px solid #00F0FF; padding:15px; border-radius:12px; color:white;">
                            <h3 style="margin:0; color:#00F0FF;">🆔 ROLL ID: {r['Student ID']}</h3>
                            <p style="margin:4px 0;">👤 <b>Name:</b> {r['Name']} | 📚 <b>Course:</b> {r['Course']}</p>
                            <p style="margin:4px 0;">⏰ <b>Shift:</b> {r['Shift']} ({r['Batch Time']})</p>
                        </div>
                    """, unsafe_allow_html=True)
                    matched = True
                    break

# ---------------------------------------------------------
# 1.5 ONLINE CERTIFICATE VERIFICATION TAB
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
        
        with st.form("add_student_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Student Full Name*")
                fname = st.text_input("Father's Name*")
                mname = st.text_input("Mother's Name*")
                gender = st.selectbox("Gender", ["Male", "Female", "Other"])
                dob = st.date_input("Date of Birth", min_value=datetime.date(1990, 1, 1))
                caste = st.selectbox("Caste", ["General", "OBC / MOBC", "ST", "SC", "Other"])
                mobile = st.text_input("Mobile Number (Unique Key)*")
                photo_file = st.file_uploader("Upload Passport Size Photo", type=["jpg", "jpeg", "png"])
                
            with col2:
                vill = st.text_input("Village / Town*")
                po = st.text_input("Post Office")
                ps = st.text_input("Police Station", value="THELAMARA")
                pin = st.text_input("PIN Code", value="784149")
                dist = st.text_input("District", value="Sonitpur")
                course = st.selectbox("Course Selected*", list(COURSE_CONFIG.keys()))
                cert_dur = st.selectbox("Course Duration Option*", ["12 Months", "6 Months", "3 Months", "2 Months", "45 Days"])
                days_batch = st.selectbox("Class Schedule Days*", ["MWF (Monday, Wednesday, Friday)", "TTS (Tuesday, Thursday, Saturday)", "Regular (Daily Classes)"])
                
            col3, col4 = st.columns(2)
            with col3:
                session = st.text_input("Session", value=f"{datetime.date.today().year}-{datetime.date.today().year+1}")
                join_date = st.date_input("Joining Date", value=datetime.date.today())
                total_fee = st.number_input("Total Course Fee (₹)", min_value=0.0, value=2550.0, step=100.0)
                discount = st.number_input("Discount Allowed (₹)", min_value=0.0, step=50.0)
                
            with col4:
                shift = st.selectbox("Shift Assigned", ["Morning (06:30-08:00 AM)", "Afternoon (04:00-05:30 PM)", "Evening (05:30-07:00 PM)"])
                batch_time = st.text_input("Batch Timing", value="90 Minutes Session")
                
            if st.form_submit_button("Submit Admission"):
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
                    days_add = 365 if "12" in cert_dur else (180 if "6" in cert_dur else 90)
                    validity_date = join_date + datetime.timedelta(days=days_add)
                    
                    new_row = {
                        "Sl. No.": str(len(student_df) + 1), "Student ID": next_id, "Name": name.upper(),
                        "Father Name": fname.upper(), "Mother Name": mname.upper(), "Gender": gender,
                        "DOB": str(dob), "Caste": caste, "Mobile No": mobile, "Vill Town": vill.upper(),
                        "PO": po.upper(), "PS": ps.upper(), "PIN Code": pin, "District": dist.upper(),
                        "Full Address": f"{vill}, {po}, {ps}, {dist} - {pin}".upper(), "Course": course,
                        "Duration": cert_dur, "Days_Batch": days_batch, "Session": session,
                        "Join Date": str(join_date), "Validity Date": str(validity_date),
                        "Total Fee": str(total_fee), "Discount": str(discount), "Net Fee": str(net_fee),
                        "Shift": shift, "Batch Time": batch_time, "Photo Path": photo_path, "Status": "Active"
                    }
                    student_df = pd.concat([student_df, pd.DataFrame([new_row])], ignore_index=True)
                    save_data(student_df, STUDENT_MASTER_FILE)
                    st.success(f"🎉 Registered Successfully! Roll ID: {next_id}")

# ---------------------------------------------------------
# 3. STUDENT LOGIN PORTAL (COMPLETE DASHBOARD INTEGRATION)
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

        st_tab1, st_tab2, st_tab3, st_tab4, st_tab5 = st.tabs([
            "💳 Digital ID Card",
            "💵 My Installment Passbook Card",
            "📊 My Test Marks & Report Card",
            "⏱️ Attendance Log",
            "🔄 My Academic Journey"
        ])
        
        with st_tab1:
            st_photo_b64 = get_image_base64(s["Photo Path"]) if s["Photo Path"] else None
            logo_b64 = get_image_base64("logo")
            
            id_card_html = f"""
            <div id="print_id_card" style="background:#020B19; border:2px solid #00F0FF; border-radius:16px; padding:20px; color:white; max-width:680px; margin:auto; box-shadow:0 0 20px rgba(0,240,255,0.3); font-family:Arial, sans-serif;">
                <div style="display:flex; align-items:center; justify-content:space-between; border-bottom:1px solid rgba(255,255,255,0.2); padding-bottom:10px;">
                    <div>
                        <h2 style="margin:0; color:#00F0FF; font-size:22px; font-weight:bold;">SOFT TECH COMPUTERS & ZTC</h2>
                        <p style="margin:2px 0 0 0; font-size:10px; color:#CBD5E1;">KAMARCHUBURI, THELAMARA, SONITPUR | CENTER CODE: 4159</p>
                    </div>
                </div>
                <div style="display:flex; align-items:center; justify-content:space-between; margin:15px 0;">
                    <div style="text-align:center; flex:1;">
                        <img src="{st_photo_b64 if st_photo_b64 else 'https://cdn-icons-png.flaticon.com/512/3135/3135715.png'}" style="width:105px; height:105px; border-radius:50%; border:2px solid #00F0FF; object-fit:cover;">
                        <div style="margin-top:5px; color:#00F0FF; font-weight:bold; font-size:12px;">ID: {s['Student ID']}</div>
                    </div>
                    <div style="flex:2; padding-left:20px;">
                        <h3 style="margin:0; color:#FFFFFF; font-size:20px;">{s['Name']}</h3>
                        <p style="margin:3px 0; font-size:12px; color:#00F0FF;"><b>Course:</b> <span style="color:white;">{s['Course']}</span></p>
                        <p style="margin:3px 0; font-size:12px; color:#00F0FF;"><b>Validity:</b> <span style="color:white;">{s['Join Date']} to {s['Validity Date']}</span></p>
                    </div>
                </div>
            </div>
            """
            st.markdown(id_card_html, unsafe_allow_html=True)

        with st_tab2:
            st.subheader("💵 My Installment Passbook Ledger")
            net_f = float(s["Net Fee"]) if s["Net Fee"] else 0.0
            st_paid_logs = fee_df[fee_df["Student ID"] == s_id]
            tot_p = sum([float(amt) for amt in st_paid_logs["Amount Paid"] if amt])
            bal_due = net_f - tot_p
            
            col_m1, col_m2, col_m3 = st.columns(3)
            col_m1.metric("Net Total Course Fee", f"₹{net_f:.2f}")
            col_m2.metric("Total Deposit Paid", f"₹{tot_p:.2f}")
            col_m3.metric("Remaining Balance Due", f"₹{bal_due:.2f}", delta="-Pending" if bal_due > 0 else "Fully Cleared")
            
            st.markdown("---")
            if not st_paid_logs.empty:
                st.table(st_paid_logs[["Receipt No", "Date", "Amount Paid", "Payment Mode", "Collected_By", "Remarks"]])
            else:
                st.info("No installment payments logged yet.")

        with st_tab3:
            st.subheader("📊 My Test Marks & Academic Report Card")
            st_marks = marks_df[marks_df["Student ID"] == s_id]
            if not st_marks.empty:
                st.dataframe(st_marks[["Date", "Course/Subject", "Test Topic", "Marks Obtained", "Total Marks"]], use_container_width=True)
            else:
                st.info("No test marks recorded yet.")

        with st_tab4:
            st.subheader("⏱️ My Class Attendance Log")
            st_att = att_df[att_df["Student ID"] == s_id]
            if not st_att.empty:
                st.dataframe(st_att[["Date", "Time_In", "Status", "Late_Reason"]], use_container_width=True)
            else:
                st.info("No attendance records logged yet.")

        with st_tab5:
            st.subheader("🔄 My Academic Stage Tracker")
            st.progress(0.4)
            st.info("Current Active Status: Stage 2 - Practical & Theory Learning")

# ---------------------------------------------------------
# 4. SUNDAY PRACTICE CLASS (SFPC - ADMISSION + MONTHLY BILL RULE)
# ---------------------------------------------------------
elif menu == "🎯 Sunday Free Practice Class (SFPC)":
    st.header("🎯 Sunday Free Practice Class (SFPC) Eligibility Portal")
    check_id = st.text_input("Enter Student Roll ID (e.g. STC26-001):").strip().upper()
    
    if check_id:
        st_res = student_df[student_df["Student ID"] == check_id]
        if not st_res.empty:
            s = st_res.iloc[0]
            try:
                j_date = datetime.datetime.strptime(str(s["Join Date"]), "%Y-%m-%d").date()
            except Exception:
                j_date = datetime.date.today()
                
            months_active = max(1, (datetime.date.today().year - j_date.year) * 12 + datetime.date.today().month - j_date.month)
            
            # RULE: Admission Fee ₹999 + Per Month ₹550
            total_bill = 999.0 + (months_active * 550.0)
            
            p_logs = fee_df[fee_df["Student ID"] == check_id]
            tot_paid = sum([float(a) for a in p_logs["Amount Paid"] if a])
            fee_cleared_perc = (tot_paid / total_bill * 100) if total_bill > 0 else 100.0
            
            s_att = att_df[att_df["Student ID"] == check_id]
            p_days = len(s_att[s_att["Status"] == "Present"])
            tot_classes = max(1, len(s_att))
            att_perc = (p_days / tot_classes * 100)
            
            col_c1, col_c2 = st.columns(2)
            col_c1.metric("Fee Bill Cleared Status", f"{fee_cleared_perc:.1f}%", delta="Target ≥50%")
            col_c2.metric("Attendance Record", f"{att_perc:.1f}%", delta="Target ≥75%")
            
            st.write(f"<b>Bill Details:</b> Total Months Active: {months_active} | Total Generated Bill: ₹{total_bill:.2f} | Total Paid: ₹{tot_paid:.2f}")
            
            if fee_cleared_perc >= 50.0 and att_perc >= 75.0:
                st.balloons()
                st.success(f"🎉 Welcome **{s['Name']}**! You are ELIGIBLE for Sunday Free Practice Lab Access!")
            else:
                st.error(f"❌ NOT ELIGIBLE! Requires ≥50% Fee Clearance (Current: {fee_cleared_perc:.1f}%) AND ≥75% Attendance (Current: {att_perc:.1f}%).")
        else:
            st.error("Invalid Student Roll ID!")

# ---------------------------------------------------------
# 5. FEE COUNTER DESK (REAL-TIME BALANCE DUE CALCULATOR)
# ---------------------------------------------------------
elif menu == "💵 Fee Counter Desk":
    st.header("💵 Student Fee Collection Counter Desk")
    f_pwd = st.text_input("Enter Staff / Teacher Password:", type="password")
    
    if f_pwd in [ADMIN_PWD, TEACHER_PWD]:
        col_st1, col_st2 = st.columns(2)
        with col_st1:
            collector_name = st.selectbox("Fee Collector Name:", teacher_df["Name"].tolist() if not teacher_df.empty else ["Director Sir"])
        with col_st2:
            sel_sid = st.selectbox("Select Student ID:", student_df["Student ID"] + " - " + student_df["Name"]) if not student_df.empty else None
            
        if sel_sid:
            sid = sel_sid.split(" - ")[0]
            s_rec = student_df[student_df["Student ID"] == sid].iloc[0]
            paid_logs = fee_df[fee_df["Student ID"] == sid]
            total_paid = sum([float(amt) for amt in paid_logs["Amount Paid"] if amt])
            net = float(s_rec["Net Fee"]) if s_rec["Net Fee"] else 0.0
            due = net - total_paid
            
            st.markdown(f"""
                <div style="background:#0F172A; border:2px solid #00F0FF; padding:15px; border-radius:12px; color:white; margin:10px 0;">
                    <h3 style="margin:0; color:#00F0FF;">👤 Student: {s_rec['Name']} ({sid})</h3>
                    <p style="margin:4px 0; font-size:15px;">💰 <b>Net Total Fee:</b> ₹{net:.2f} | 💵 <b>Total Paid So Far:</b> ₹{total_paid:.2f}</p>
                    <h4 style="margin:4px 0; color:#EF4444;">🔴 Remaining Balance Due: ₹{due:.2f}</h4>
                </div>
            """, unsafe_allow_html=True)
            
            with st.form("fee_collect_form", clear_on_submit=True):
                pay_amt = st.number_input("Amount Received Paid (₹)", min_value=100.0, step=100.0)
                pay_mode = st.selectbox("Payment Mode", ["Cash", "UPI / GPay", "Bank Transfer"])
                remarks = st.text_input("Remarks / Installment Month", value="Installment Fee Deposit")
                
                if st.form_submit_button("Issue Receipt & Save Deposit"):
                    rc_num = f"REC-{datetime.date.today().strftime('%Y%m%d')}-{len(fee_df)+1:03d}"
                    f_row = {"Receipt No": rc_num, "Student ID": sid, "Date": str(datetime.date.today()), "Amount Paid": str(pay_amt), "Payment Mode": pay_mode, "Collected_By": collector_name, "Remarks": remarks}
                    fee_df = pd.concat([fee_df, pd.DataFrame([f_row])], ignore_index=True)
                    save_data(fee_df, FEE_LOG_FILE)
                    st.success(f"✅ Receipt Issued Successfully! Receipt No: {rc_num}")

# ---------------------------------------------------------
# 6. TEACHER PORTAL & ATTENDANCE & MULTI-TOPIC SYLLABUS LOG
# ---------------------------------------------------------
elif menu == "🔑 Teacher Portal & QR Scanner":
    st.header("🔑 Faculty Portal & Class Management Desk")
    t_pwd = st.text_input("Enter Faculty Password:", type="password")
    
    if t_pwd == TEACHER_PWD:
        now_ist = datetime.datetime.now(IST)
        cur_time_str = now_ist.strftime("%I:%M %p")
        cur_date_str = now_ist.strftime("%Y-%m-%d")
        
        t_tab1, t_tab2, t_tab3, t_tab4 = st.tabs([
            "📸 Scan / Mark Student Attendance", 
            "⏱️ Faculty Self Punch-In", 
            "📖 Log Class Syllabus & Topics",
            "📊 Log Student Test Marks"
        ])
        
        with t_tab1:
            st.subheader("📸 Scan / Mark Student Attendance")
            if not student_df.empty:
                sel_student_att = st.selectbox("Select Student to Mark Present:", student_df["Student ID"] + " - " + student_df["Name"])
                if st.button("Mark Student Present Now"):
                    st_id_scan = sel_student_att.split(" - ")[0]
                    st_name_scan = sel_student_att.split(" - ")[1]
                    att_row = {"Student ID": st_id_scan, "Date": cur_date_str, "Time_In": cur_time_str, "Status": "Present", "Late_Reason": "Marked by Teacher", "Sign_Mode": "Teacher Portal", "Location_Verified": "Campus"}
                    att_df = pd.concat([att_df, pd.DataFrame([att_row])], ignore_index=True)
                    save_data(att_df, ATTENDANCE_FILE)
                    st.success(f"✅ Marked Present for {st_name_scan} ({st_id_scan}) at {cur_time_str} IST!")

        with t_tab2:
            st.subheader("⏱️ Faculty Punch-In & Shift Session Tracker")
            t_name_sel = st.selectbox("Select Teacher Name:", teacher_df["Name"].tolist() if not teacher_df.empty else ["Faculty"])
            t_shift = st.selectbox("Select Shift Session:", ["Morning (06:30 AM)", "Afternoon (04:00 PM)", "Evening (05:30 PM)"])
            
            st.info(f"Current IST Punch Time: **{cur_time_str}** | Date: **{cur_date_str}**")
            late_mins = st.number_input("Enter Minutes Late (If Arrived Late):", min_value=0, max_value=90, value=0)
            
            base_rate = 76.66
            penalty_percent = 0
            if late_mins > 30: penalty_percent = 50
            elif late_mins > 20: penalty_percent = 30
            elif late_mins > 10: penalty_percent = 15
                
            deduction = (base_rate * penalty_percent) / 100.0
            net_earning = base_rate - deduction
            
            st.write(f"**Earning Summary:** Base: ₹{base_rate:.2f} | Penalty Deducted ({penalty_percent}%): ₹{deduction:.2f} | **Net Today: ₹{net_earning:.2f}**")
            
            if st.button("Punch Faculty Attendance Now"):
                t_row = {
                    "Teacher ID": "TCH-01", "Name": t_name_sel, "Date": cur_date_str,
                    "Time_In": cur_time_str, "Shift": t_shift, "Status": "Present",
                    "Late_Mins": str(late_mins), "Penalty_Deduction": f"₹{deduction:.2f}",
                    "Net_Earning_Today": f"₹{net_earning:.2f}"
                }
                teacher_att_df = pd.concat([teacher_att_df, pd.DataFrame([t_row])], ignore_index=True)
                save_data(teacher_att_df, "teacher_attendance.csv")
                st.success(f"✅ Punched Successfully at {cur_time_str} IST!")

        with t_tab3:
            st.subheader("📖 Log Daily Class Syllabus (Multi-Topic Selection)")
            with st.form("syllabus_form", clear_on_submit=True):
                sys_course = st.selectbox("Select Course Taught:", list(COURSE_CONFIG.keys()))
                
                # MULTI-SELECT FOR TOPICS
                sys_topics = st.multiselect("Select Topics Covered Today (Multiple allowed):", ALL_SYLLABUS_TOPICS, default=["Computer Basics / Fundamentals"])
                sys_class_type = st.radio("Class Delivered Type:", ["Practical Session", "Theory Session", "Both Practical & Theory", "Exam / Test Conducted"])
                
                if st.form_submit_button("Save Daily Syllabus Record"):
                    topic_str = ", ".join(sys_topics) if sys_topics else "General Topics"
                    s_row = {"Date": cur_date_str, "Course": sys_course, "Topics Covered": topic_str, "Class Type": sys_class_type, "Teacher Incharge": t_name_sel if 't_name_sel' in locals() else "Faculty"}
                    syllabus_df = pd.concat([syllabus_df, pd.DataFrame([s_row])], ignore_index=True)
                    save_data(syllabus_df, SYLLABUS_LOG_FILE)
                    st.success(f"✅ Saved Syllabus Record: {topic_str} ({sys_class_type})")

        with t_tab4:
            st.subheader("📊 Log Student Test Marks")
            with st.form("marks_form", clear_on_submit=True):
                m_student = st.selectbox("Select Student:", student_df["Student ID"] + " - " + student_df["Name"]) if not student_df.empty else None
                m_subject = st.selectbox("Course / Subject:", list(COURSE_CONFIG.keys()))
                m_topic = st.text_input("Test Topic")
                m_obtained = st.number_input("Marks Obtained:", min_value=0.0, step=1.0)
                m_total = st.number_input("Total Marks:", min_value=10.0, value=100.0, step=50.0)
                
                if st.form_submit_button("Save Test Marks"):
                    if m_student:
                        m_id = m_student.split(" - ")[0]
                        m_name = m_student.split(" - ")[1]
                        m_row = {"Date": cur_date_str, "Student ID": m_id, "Student Name": m_name, "Course/Subject": m_subject, "Test Topic": m_topic, "Marks Obtained": str(m_obtained), "Total Marks": str(m_total), "Teacher Incharge": t_name_sel if 't_name_sel' in locals() else "Director"}
                        marks_df = pd.concat([marks_df, pd.DataFrame([m_row])], ignore_index=True)
                        save_data(marks_df, MARKS_FILE)
                        st.success(f"✅ Marks Saved for {m_name}!")

# ---------------------------------------------------------
# 7. ADMIN CONTROL PANEL (WITH ADD TEACHER OPTION)
# ---------------------------------------------------------
elif menu == "🔐 Admin Control Panel":
    st.header("🔐 Director Admin Control Panel")
    pwd = st.text_input("Enter Director Admin Password", type="password")
    
    if pwd == ADMIN_PWD:
        st.success("Welcome Director Chiranjeeb Hazarika Sir!")
        
        adm_tab1, adm_tab2, adm_tab3, adm_tab4 = st.tabs([
            "👨‍🏫 Add & View Faculty/Staff", 
            "📲 WhatsApp Fee Reminder", 
            "📢 Post Live Notice", 
            "👨‍🏫 Faculty Salary & Attendance Ledger"
        ])
        
        with adm_tab1:
            st.subheader("👨‍🏫 Add New Faculty / Teacher Staff")
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
                    else:
                        st.error("Please enter Name and Phone Number!")
            
            st.markdown("---")
            st.write("📋 **Current Registered Faculty Roster:**")
            st.dataframe(teacher_df, use_container_width=True)

        with adm_tab2:
            st.subheader("📲 One-Click WhatsApp Fee Due Reminder System")
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
                        col_a.write(f"👤 **{row['Name']}** ({sid}) - Pending Due: :red[₹{due:.2f}]")
                        col_b.markdown(f'<a href="{wa_url}" target="_blank" style="background:#25D366; color:white; padding:6px 12px; border-radius:6px; text-decoration:none; font-weight:bold; font-size:12px;">📲 Send WhatsApp</a>', unsafe_allow_html=True)

        with adm_tab3:
            st.subheader("📢 Post New Notice to Live Public Board")
            with st.form("notice_form", clear_on_submit=True):
                n_title = st.text_input("Notice Title:")
                n_cat = st.selectbox("Category:", ["General Notice", "Exam Schedule", "Holiday Alert", "Special Offer"])
                n_content = st.text_area("Notice Details / Announcement Text:")
                if st.form_submit_button("Post Notice Now"):
                    n_row = {"Date": str(datetime.date.today()), "Notice Title": n_title, "Notice Content": n_content, "Category": n_cat, "Posted By": "Director"}
                    notices_df = pd.concat([notices_df, pd.DataFrame([n_row])], ignore_index=True)
                    save_data(notices_df, NOTICES_FILE)
                    st.success("✅ Notice Posted to Public Dashboard!")

        with adm_tab4:
            st.subheader("👨‍🏫 Faculty Salary, Late Minutes & Penalty Ledger")
            st.dataframe(teacher_att_df, use_container_width=True)