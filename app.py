import streamlit as st
import pandas as pd
import os
import datetime
import pytz
import base64

# Page Configuration
st.set_page_config(page_title="Soft Tech Computers & ZTC Portal", page_icon="💻", layout="wide")

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
PHOTO_DIR = "student_photos"

# SAFE DIRECTORY CREATION
os.makedirs(PHOTO_DIR, exist_ok=True)

# Helper function to convert local image to base64 safely
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

# Safe Loader
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
fee_cols = ["Receipt No", "Student ID", "Date", "Amount Paid", "Payment Mode", "Remarks"]
attendance_cols = ["Student ID", "Date", "Time_In", "Status", "Late_Reason", "Sign_Mode", "Location_Verified"]
teacher_cols = ["Teacher ID", "Name", "Phone", "Qualification", "Designation", "Shift Assigned"]
teacher_att_cols = ["Teacher ID", "Name", "Date", "Time_In", "Shift", "Status", "Late_Reason", "Absent_Reason", "Earning_Today"]
enquiry_cols = ["Date", "Name", "Mobile", "Course Interested", "Village/Address", "Status"]
sfpc_cols = ["Date", "Student ID", "Student Name", "PC Machine No", "Topic Practiced", "Teacher Incharge"]
creds_cols = ["Role", "Password"]
feedback_cols = ["Date", "Student ID", "Student Name", "Teacher Name", "Theory Written", "Rating_Stars", "Comments"]
syllabus_cols = ["Date", "Course", "Topic Covered", "Teacher Incharge", "Theory Dictated"]

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

# Course Config & Dynamic Topics
COURSE_CONFIG = {
    "ADCA (Advanced Diploma in Computer Application)": {
        "Months": 12, "Fee": "₹7,500 Total",
        "Topics": ["Paint", "Notepad", "Wordpad", "MS-Word", "MS-Excel", "MS-Powerpoint", "MS-Access", "HTML", "DHTML", "Tally Prime", "Photoshop", "Pagemaker", "Internet", "Python"]
    },
    "DCA (Diploma in Computer Application)": {
        "Months": 6, "Fee": "₹4,500 Total",
        "Topics": ["Paint", "Notepad", "Wordpad", "MS-Word", "MS-Excel", "MS-Powerpoint", "MS-Access", "HTML", "Tally", "Internet"]
    },
    "DTP (Desktop Publishing)": {
        "Months": 3, "Fee": "₹3,500 Total",
        "Topics": ["MS-Word", "Photoshop", "Pagemaker", "CorelDraw", "Assamese Typesetting", "Internet"]
    },
    "Tally Prime with GST": {
        "Months": 3, "Fee": "₹4,000 Total",
        "Topics": ["Accounting Basics", "Tally Prime Basics", "Inventory Management", "GST & TDS Calculation", "Payroll & Billing"]
    },
    "Class 9 English Coaching": {"Months": 12, "Fee": "₹600 / Month", "Topics": ["Grammar", "Literature prose", "Poetry", "Writing Skills"]},
    "Class 10 English Coaching": {"Months": 12, "Fee": "₹700 / Month", "Topics": ["Grammar", "Literature prose", "Poetry", "Writing Skills"]},
    "Class 11 English Coaching": {"Months": 12, "Fee": "₹800 / Month", "Topics": ["Grammar", "Literature prose", "Poetry", "Writing Skills"]},
    "Class 12 English Coaching": {"Months": 12, "Fee": "₹900 / Month", "Topics": ["Grammar", "Literature prose", "Poetry", "Writing Skills"]},
    "Certificate Course in Computer Basics": {"Months": 2, "Fee": "₹2,500 Total", "Topics": ["Paint", "Notepad", "Wordpad", "MS-Word", "Internet"]}
}

# Navigation Menu (CLEAN PUBLIC SIDEBAR)
st.sidebar.title("💻 STC & ZTC Portal")
menu = st.sidebar.radio("Navigation Menu:", [
    "🏠 Home & Public Dashboard",
    "📝 New Student Admission",
    "🔑 Student Login Portal",
    "🎯 Sunday Free Practice Class (SFPC)",
    "💵 Fee Counter Desk",
    "🔑 Teacher Portal & QR Scanner",
    "🔐 Admin Control Panel"
])

# ---------------------------------------------------------
# 1. HIGH-TECH HOME & PUBLIC DASHBOARD
# ---------------------------------------------------------
if menu == "🏠 Home & Public Dashboard":
    dp2_b64 = get_image_base64("dp2")
    if dp2_b64:
        st.markdown(f'<img src="{dp2_b64}" style="width:100%; max-height:280px; object-fit:contain; border-radius:15px; border:2px solid #00F0FF; box-shadow: 0 0 20px rgba(0, 240, 255, 0.3); margin-bottom:12px;">', unsafe_allow_html=True)
    
    st.markdown("""
        <div style="
            background: linear-gradient(135deg, #020B19 0%, #0F172A 50%, #1E3A8A 100%);
            padding: 12px 20px; border-radius: 12px; text-align: center; color: white;
            border: 1.5px solid #00F0FF; box-shadow: 0 0 15px rgba(0, 240, 255, 0.2); margin-bottom: 20px;
        ">
            <h4 style="margin:0; color:#FBBF24; font-size:15px; font-weight:bold;">MAKE YOURSELF DIGITAL | AN ISO 9001:2015 CERTIFIED INSTITUTION</h4>
            <p style="margin:4px 0 0 0; font-size:13px; color:#CBD5E1;">Kamarchuburi, Near Thelamara, Sonitpur, Assam - 784149 | Center Code: 4159 | Contact: +91 9101026718</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div style="background-color: #FEF3C7; border: 1.5px solid #F59E0B; padding: 8px 15px; border-radius: 10px; margin-bottom: 20px;">
            <marquee style="color: #B45309; font-weight: bold; font-size: 15px;">
                🏆 STUDENT OF THE MONTH: CONGRATULATIONS TO OUR TOP PERFORMERS! WORK HARD & SHINE BRIGHT AT SOFT TECH COMPUTERS & ZTC! 🏆
            </marquee>
        </div>
    """, unsafe_allow_html=True)

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

    st.subheader("📚 Courses Offered & Duration")
    pub_course_list = [{"Course Name": k, "Duration": f"{v['Months']} Months"} for k, v in COURSE_CONFIG.items()]
    pub_course_df = pd.DataFrame(pub_course_list)
    pub_course_df.index = range(1, len(pub_course_df) + 1)
    st.table(pub_course_df)

    st.markdown("---")

    col_p1, col_p2 = st.columns([1, 2])
    with col_p1:
        st.subheader("📲 Portal Access QR")
        st.markdown("""
            <div style="border:2px dashed #2563EB; background-color:#EFF6FF; padding:18px; border-radius:14px; text-align:center;">
                <h3 style="color:#1E3A8A; margin-top:0;">🌐 Scan to Enter Portal</h3>
                <img src="https://api.qrserver.com/v1/create-qr-code/?size=160x160&data=https://stcztc.streamlit.app" style="width:130px; height:130px; border-radius:8px;">
                <p style="font-weight:bold; color:#2563EB; margin-top:8px;">stcztc.streamlit.app</p>
            </div>
        """, unsafe_allow_html=True)

    with col_p2:
        st.subheader("📝 Course Enquiry Desk")
        with st.form("pub_enq_form", clear_on_submit=False):
            e_name = st.text_input("Your Full Name*")
            e_mobile = st.text_input("Contact Mobile Number*")
            e_course = st.selectbox("Select Interested Course*", list(COURSE_CONFIG.keys()))
            e_addr = st.text_input("Village / Address")
            
            if st.form_submit_button("Submit & Reveal Course Fee"):
                if not e_name or not e_mobile:
                    st.error("Please enter Name and Mobile Number!")
                else:
                    e_row = {"Date": str(datetime.date.today()), "Name": e_name.upper(), "Mobile": e_mobile, "Course Interested": e_course, "Village/Address": e_addr.upper(), "Status": "Enquired"}
                    enquiry_df = pd.concat([enquiry_df, pd.DataFrame([e_row])], ignore_index=True)
                    save_data(enquiry_df, ENQUIRY_FILE)
                    revealed_fee = COURSE_CONFIG[e_course]["Fee"]
                    st.balloons()
                    st.success(f"🎉 Thank you {e_name}! Course Fee for {e_course}: {revealed_fee}")

    # 🤖 AI HELPDESK BOT FOR PUBLIC
    with st.expander("🤖 Instant AI Helpdesk Assistant (Click to Ask Question)"):
        user_q = st.text_input("Type your question here (e.g. timing, location, director, courses):")
        if user_q:
            q_lower = user_q.lower()
            if "fee" in q_lower or "cost" in q_lower:
                st.info("💡 Course fees vary from ₹2,500 to ₹7,500. Please fill out the Enquiry Form above to reveal exact fee!")
            elif "timing" in q_lower or "time" in q_lower or "shift" in q_lower:
                st.info("💡 Batches run in Morning (06:30 AM), Afternoon (04:00 PM), and Evening (05:30 PM).")
            elif "director" in q_lower or "owner" in q_lower:
                st.info("💡 Soft Tech Computers & ZTC is founded & directed by Chiranjeeb Hazarika (Zaan) Sir.")
            elif "location" in q_lower or "address" in q_lower:
                st.info("💡 Located at Kamarchuburi, Near Thelamara, Sonitpur, Assam - 784149.")
            else:
                st.info("💡 Welcome to STC & ZTC! You can contact office directly at +91 9101026718.")

# ---------------------------------------------------------
# 2. NEW STUDENT ADMISSION
# ---------------------------------------------------------
elif menu == "📝 New Student Admission":
    st.header("📝 New Student Registration Form")
    auth_pwd = st.text_input("Enter Staff / Admin Password to Unlock Form:", type="password")
    
    if auth_pwd in [ADMIN_PWD, TEACHER_PWD]:
        st.success("Authorized Access Granted!")
        
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
                    year_code = str(datetime.date.today().year)[2:]
                    existing_ids = [sid for sid in student_df["Student ID"] if str(sid).startswith(f"STC{year_code}-")]
                    next_num = len(existing_ids) + 1
                    new_id = f"STC{year_code}-{next_num:03d}"
                    
                    photo_path = ""
                    if photo_file is not None:
                        photo_path = os.path.join(PHOTO_DIR, f"{new_id}.png")
                        with open(photo_path, "wb") as f:
                            f.write(photo_file.getbuffer())
                            
                    net_fee = float(total_fee) - float(discount)
                    dur_months = COURSE_CONFIG[course]["Months"]
                    validity_date = join_date + datetime.timedelta(days=dur_months * 30)
                    
                    new_row = {
                        "Sl. No.": str(len(student_df) + 1), "Student ID": new_id, "Name": name.upper(),
                        "Father Name": fname.upper(), "Mother Name": mname.upper(), "Gender": gender,
                        "DOB": str(dob), "Caste": caste, "Mobile No": mobile, "Vill Town": vill.upper(),
                        "PO": po.upper(), "PS": ps.upper(), "PIN Code": pin, "District": dist.upper(),
                        "Full Address": f"{vill}, {po}, {ps}, {dist} - {pin}".upper(), "Course": course,
                        "Duration": f"{dur_months} Months", "Days_Batch": days_batch, "Session": session,
                        "Join Date": str(join_date), "Validity Date": str(validity_date),
                        "Total Fee": str(total_fee), "Discount": str(discount), "Net Fee": str(net_fee),
                        "Shift": shift, "Batch Time": batch_time, "Photo Path": photo_path, "Status": "Active"
                    }
                    student_df = pd.concat([student_df, pd.DataFrame([new_row])], ignore_index=True)
                    save_data(student_df, STUDENT_MASTER_FILE)
                    
                    st.success(f"🎉 Registered Successfully! Roll ID: {new_id} | End Date: {validity_date}")

# ---------------------------------------------------------
# 3. STUDENT LOGIN PORTAL (INCLUDES INSTALLMENT CARD & JOURNEY CIRCLE)
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
            "🔄 My Academic Journey",
            "⏱️ Live IST Punch-In",
            "📖 Syllabus & Feedback"
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
                    <div>
                        <img src="{logo_b64 if logo_b64 else ''}" style="width:55px; height:55px; border-radius:50%; border:2px solid #00F0FF;">
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
                        <p style="margin:3px 0; font-size:12px; color:#00F0FF;"><b>Schedule:</b> <span style="color:white;">{s.get('Days_Batch', 'MWF')}</span></p>
                        <p style="margin:3px 0; font-size:12px; color:#00F0FF;"><b>Validity:</b> <span style="color:white;">{s['Join Date']} to {s['Validity Date']}</span></p>
                        <p style="margin:3px 0; font-size:12px; color:#00F0FF;"><b>Mobile:</b> <span style="color:white;">+91 {s['Mobile No']}</span></p>
                    </div>
                </div>
                <div style="border-top:1px dashed rgba(255,255,255,0.2); padding-top:10px; display:flex; align-items:center; justify-content:space-between;">
                    <div style="text-align:left;">
                        <div style="background:white; padding:3px 6px; border-radius:4px; display:inline-block;">
                            <div style="font-family:'Courier New', monospace; font-weight:bold; color:black; font-size:12px;">||||||||||||||||||</div>
                            <div style="font-size:8px; color:black; font-weight:bold; text-align:center;">{s['Student ID']}</div>
                        </div>
                    </div>
                    <div style="text-align:center;">
                        <div style="font-family:cursive; color:#00F0FF; font-size:16px;">Chiranjeeb Hazarika</div>
                        <div style="font-size:9px; color:#00F0FF; font-weight:bold;">DIRECTOR</div>
                    </div>
                    <div>
                        <img src="https://api.qrserver.com/v1/create-qr-code/?size=60x60&data={s['Student ID']}" style="width:50px; height:50px; border-radius:4px; background:white; padding:2px;">
                    </div>
                </div>
            </div>
            """
            st.markdown(id_card_html, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🖨️ Direct Print ID Card"):
                st.components.v1.html("<script>window.print();</script>", height=0)

        # 💵 DIGITAL INSTALLMENT PASSBOOK CARD
        with st_tab2:
            st.subheader("💵 Student Fee Installment Record Passbook")
            net_f = float(s["Net Fee"]) if s["Net Fee"] else 0.0
            st_paid_logs = fee_df[fee_df["Student ID"] == s_id]
            tot_p = sum([float(amt) for amt in st_paid_logs["Amount Paid"] if amt])
            bal_due = net_f - tot_p
            
            col_m1, col_m2, col_m3 = st.columns(3)
            col_m1.metric("Net Total Course Fee", f"₹{net_f:.2f}")
            col_m2.metric("Total Deposit Paid", f"₹{tot_p:.2f}")
            col_m3.metric("Remaining Balance Due", f"₹{bal_due:.2f}", delta="-Pending" if bal_due > 0 else "Fully Cleared")
            
            st.markdown("---")
            st.write("📋 **Detailed Deposit Transactions History:**")
            if not st_paid_logs.empty:
                disp_fee_df = st_paid_logs[["Receipt No", "Date", "Amount Paid", "Payment Mode", "Remarks"]].copy()
                disp_fee_df.index = range(1, len(disp_fee_df) + 1)
                st.table(disp_fee_df)
            else:
                st.info("No installment payments logged yet.")

        # 🔄 STUDENT ACADEMIC LIFECYCLE (STUDY CIRCLE MOVED HERE)
        with st_tab3:
            st.subheader("🔄 My Academic Journey & Status Tracker")
            st.markdown("""
                <div style="background:#F0F9FF; border:2px solid #0284C7; padding:15px; border-radius:12px;">
                    <h4 style="color:#0369A1; margin-top:0;">📋 Official STC Academic Stages:</h4>
                    <ol>
                        <li><b>1. Admission Taken</b> — Completed</li>
                        <li><b>2. Topic-Wise Syllabus Learning</b> — In Progress</li>
                        <li><b>3. Registration Completed</b> — SARVA / Head Office Code</li>
                        <li><b>4. Final Exam Form Fillup</b> — Form Submitted</li>
                        <li><b>5. Admit Card Issued</b> — Generated</li>
                        <li><b>6. Final Exam Conducted</b> — Exam Completed</li>
                        <li><b>7. Certificate & Marksheet Issued</b> — Completed</li>
                    </ol>
                </div>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.progress(0.4)
            st.info("Current Active Status: **Stage 2: Topic-Wise Syllabus Learning**")

        # ⏱️ LIVE IST PUNCH IN
        with st_tab4:
            st.subheader("⏱️ Live IST Attendance Punch-In")
            now_ist = datetime.datetime.now(IST)
            cur_time_str = now_ist.strftime("%I:%M:%S %p")
            cur_date_str = now_ist.strftime("%Y-%m-%d")
            
            st.info(f"Current IST Time: **{cur_time_str}** | Date: **{cur_date_str}**")
            
            today_att = att_df[(att_df["Student ID"] == s_id) & (att_df["Date"] == cur_date_str)]
            if today_att.empty:
                st_late_reason = st.selectbox("Reason for Arrival Time (If Late):", ["On Time", "School / College Class", "Traffic Issue", "Personal Work", "Rain / Weather", "Health Issue"])
                if st.button("Click to Punch In Attendance Now"):
                    att_row = {"Student ID": s_id, "Date": cur_date_str, "Time_In": cur_time_str, "Status": "Present", "Late_Reason": st_late_reason, "Sign_Mode": "Classroom", "Location_Verified": "Campus"}
                    att_df = pd.concat([att_df, pd.DataFrame([att_row])], ignore_index=True)
                    save_data(att_df, ATTENDANCE_FILE)
                    st.success(f"✅ Attendance Punched at {cur_time_str} IST!")
                    st.rerun()
            else:
                st.success(f"✅ Already Punched Today at {today_att.iloc[0]['Time_In']} IST!")

        # 📖 SYLLABUS & FEEDBACK
        with st_tab5:
            st.subheader("📖 Course Modules & Star Feedback")
            st_course = s["Course"]
            available_topics = COURSE_CONFIG.get(st_course, {}).get("Topics", ["General Computer Basics"])
            st.info(f"Course Modules for {st_course}: " + ", ".join(available_topics))
            
            st.markdown("---")
            with st.form("st_feed_form", clear_on_submit=True):
                tch_name = st.selectbox("Select Instructor:", teacher_df["Name"].tolist() if not teacher_df.empty else ["Director"])
                th_written = st.radio("Did the teacher dictate Theory Notes today?", ["Yes, Theory Dictated", "No, Only Practical / Discussion"])
                stars = st.select_slider("Rate Today's Class Session (Stars):", options=["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"], value="⭐⭐⭐⭐⭐")
                comments = st.text_area("Feedback or Issues for Director:")
                
                if st.form_submit_button("Submit Feedback"):
                    f_row = {"Date": str(datetime.date.today()), "Student ID": s_id, "Student Name": s["Name"], "Teacher Name": tch_name, "Theory Written": th_written, "Rating_Stars": stars, "Comments": comments}
                    feedback_df = pd.concat([feedback_df, pd.DataFrame([f_row])], ignore_index=True)
                    save_data(feedback_df, FEEDBACK_FILE)
                    st.success("✅ Feedback Sent Directly to Director Admin Desk!")

# ---------------------------------------------------------
# 4. SUNDAY PRACTICE CLASS (SFPC) - SECURE ROLL NUMBER SEARCH
# ---------------------------------------------------------
elif menu == "🎯 Sunday Free Practice Class (SFPC)":
    st.header("🎯 Sunday Free Practice Class (SFPC) Eligibility Portal")
    st.info("🔒 Enter your Roll ID below to verify your private Sunday Lab Access status.")
    
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
            total_bill = 999.0 + (months_active * 550.0)
            
            p_logs = fee_df[fee_df["Student ID"] == check_id]
            tot_paid = sum([float(a) for a in p_logs["Amount Paid"] if a])
            fee_cleared_perc = (tot_paid / total_bill * 100) if total_bill > 0 else 100.0
            
            s_att = att_df[att_df["Student ID"] == check_id]
            p_days = len(s_att[s_att["Status"] == "Present"])
            tot_classes = max(1, len(s_att))
            att_perc = (p_days / tot_classes * 100)
            
            col_c1, col_c2 = st.columns(2)
            col_c1.metric("Fee Cleared Status", f"{fee_cleared_perc:.1f}%", delta="Target ≥50%")
            col_c2.metric("Attendance Record", f"{att_perc:.1f}%", delta="Target ≥75%")
            
            if fee_cleared_perc >= 50.0 and att_perc >= 75.0:
                st.balloons()
                st.success(f"🎉 Welcome **{s['Name']}**! You are ELIGIBLE for Sunday Practice Lab Access!")
            else:
                st.error(f"❌ NOT ELIGIBLE! Requires ≥50% Fee Clearance (Current: {fee_cleared_perc:.1f}%) AND ≥75% Attendance (Current: {att_perc:.1f}%).")
        else:
            st.error("Invalid Student Roll ID!")

# ---------------------------------------------------------
# 5. FEE COUNTER DESK
# ---------------------------------------------------------
elif menu == "💵 Fee Counter Desk":
    st.header("💵 Student Fee Collection Counter")
    f_pwd = st.text_input("Enter Staff Password:", type="password")
    if f_pwd in [ADMIN_PWD, TEACHER_PWD]:
        sel_sid = st.selectbox("Select Student:", student_df["Student ID"] + " - " + student_df["Name"]) if not student_df.empty else None
        if sel_sid:
            sid = sel_sid.split(" - ")[0]
            s_rec = student_df[student_df["Student ID"] == sid].iloc[0]
            paid_logs = fee_df[fee_df["Student ID"] == sid]
            total_paid = sum([float(amt) for amt in paid_logs["Amount Paid"] if amt])
            net = float(s_rec["Net Fee"]) if s_rec["Net Fee"] else 0.0
            due = net - total_paid
            
            st.write(f"**Net Fee:** ₹{net:.2f} | **Total Paid:** ₹{total_paid:.2f} | **Due:** :red[₹{due:.2f}]")
            with st.form("fee_collect_form", clear_on_submit=True):
                pay_amt = st.number_input("Amount Paid (₹)", min_value=100.0, step=100.0)
                pay_mode = st.selectbox("Payment Mode", ["Cash", "UPI / GPay", "Bank Transfer"])
                remarks = st.text_input("Remarks", value="Monthly Installment")
                if st.form_submit_button("Issue Receipt"):
                    rc_num = f"REC-{datetime.date.today().strftime('%Y%m%d')}-{len(fee_df)+1:03d}"
                    f_row = {"Receipt No": rc_num, "Student ID": sid, "Date": str(datetime.date.today()), "Amount Paid": str(pay_amt), "Payment Mode": pay_mode, "Remarks": remarks}
                    fee_df = pd.concat([fee_df, pd.DataFrame([f_row])], ignore_index=True)
                    save_data(fee_df, FEE_LOG_FILE)
                    st.success(f"✅ Receipt Issued: {rc_num}")

# ---------------------------------------------------------
# 6. TEACHER PORTAL & QR CODE SCANNER ATTENDANCE
# ---------------------------------------------------------
elif menu == "🔑 Teacher Portal & QR Scanner":
    st.header("🔑 Faculty Portal & Student QR Attendance Desk")
    t_pwd = st.text_input("Enter Faculty Password:", type="password")
    
    if t_pwd == TEACHER_PWD:
        now_ist = datetime.datetime.now(IST)
        cur_time_str = now_ist.strftime("%I:%M %p")
        cur_date_str = now_ist.strftime("%Y-%m-%d")
        
        st_tab1, st_tab2, st_tab3 = st.tabs(["📸 Scan Student QR Attendance", "⏱️ Self Attendance Punch", "📖 Log Class Syllabus"])
        
        with st_tab1:
            st.subheader("📸 Scan Student QR Code / Enter ID for Attendance")
            qr_scanned_id = st.text_input("Scan QR Code or Type Roll ID:").strip().upper()
            
            if qr_scanned_id:
                st_data = student_df[student_df["Student ID"] == qr_scanned_id]
                if not st_data.empty:
                    st_name = st_data.iloc[0]["Name"]
                    st.success(f"Student Recognized: **{st_name}** ({qr_scanned_id})")
                    
                    if st.button("Mark Student Present Now"):
                        att_row = {"Student ID": qr_scanned_id, "Date": cur_date_str, "Time_In": cur_time_str, "Status": "Present", "Late_Reason": "Scanned by Teacher", "Sign_Mode": "Teacher Mobile QR", "Location_Verified": "Campus"}
                        att_df = pd.concat([att_df, pd.DataFrame([att_row])], ignore_index=True)
                        save_data(att_df, ATTENDANCE_FILE)
                        st.success(f"✅ Marked Present for {st_name} at {cur_time_str} IST!")
                else:
                    st.error("Invalid QR / Student ID!")

        with st_tab2:
            st.subheader("⏱️ Faculty Punch-In & Shift Session Tracker")
            with st.form("teacher_punch_form"):
                t_name_sel = st.selectbox("Select Teacher Name:", teacher_df["Name"].tolist() if not teacher_df.empty else ["Faculty"])
                t_shift = st.selectbox("Select Shift Session (90 Mins Each):", ["Morning (06:30 AM)", "Afternoon (04:00 PM)", "Evening (05:30 PM)"])
                late_reason = st.selectbox("Late Reason (If Punching Late):", ["On Time", "Traffic Delay", "Personal Work", "Health Issue", "Weather"])
                absent_status = st.selectbox("Status Today:", ["Present & Teaching", "Absent (With Prior Info)", "Absent (Without Informing)"])
                
                if st.form_submit_button("Punch Self Attendance"):
                    earning = 76.66 if "Present" in absent_status else 0.0
                    t_row = {
                        "Teacher ID": "TCH-01", "Name": t_name_sel, "Date": cur_date_str,
                        "Time_In": cur_time_str, "Shift": t_shift, "Status": absent_status,
                        "Late_Reason": late_reason, "Absent_Reason": absent_status, "Earning_Today": str(earning)
                    }
                    teacher_att_df = pd.concat([teacher_att_df, pd.DataFrame([t_row])], ignore_index=True)
                    save_data(teacher_att_df, "teacher_attendance.csv")
                    st.success(f"✅ Punched at {cur_time_str} IST! Session Earnings: ₹{earning:.2f}")

        with st_tab3:
            st.subheader("📖 Log Daily Syllabus & Theory Dictated")
            with st.form("syllabus_form", clear_on_submit=True):
                sys_course = st.selectbox("Select Course Taught:", list(COURSE_CONFIG.keys()))
                sys_topic = st.selectbox("Select Topic Taught:", COURSE_CONFIG[sys_course]["Topics"])
                sys_th = st.radio("Theory Dictated to Batch?", ["Yes, Notes Given", "No, Practical Session"])
                if st.form_submit_button("Save Syllabus Log"):
                    s_row = {"Date": cur_date_str, "Course": sys_course, "Topic Covered": sys_topic, "Teacher Incharge": t_name_sel if 't_name_sel' in locals() else "Director", "Theory Dictated": sys_th}
                    syllabus_df = pd.concat([syllabus_df, pd.DataFrame([s_row])], ignore_index=True)
                    save_data(syllabus_df, SYLLABUS_LOG_FILE)
                    st.success("✅ Class Syllabus & Theory Record Saved!")

# ---------------------------------------------------------
# 7. ADMIN CONTROL PANEL
# ---------------------------------------------------------
elif menu == "🔐 Admin Control Panel":
    st.header("🔐 Director Admin Control Panel")
    pwd = st.text_input("Enter Director Admin Password", type="password")
    
    if pwd == ADMIN_PWD:
        st.success("Welcome Director Chiranjeeb Hazarika Sir!")
        
        adm_tab1, adm_tab2, adm_tab3, adm_tab4, adm_tab5 = st.tabs([
            "📊 Master Registry",
            "👨‍🏫 Faculty Attendance & Salary",
            "⭐ Student Star Feedbacks",
            "📩 Enquiries Ledger",
            "📋 Attendance Logs"
        ])
        
        with adm_tab1:
            st.dataframe(student_df, use_container_width=True)
            
        with adm_tab2:
            st.subheader("👨‍🏫 Faculty Attendance, Late Reasons & Salary Ledger")
            st.dataframe(teacher_att_df, use_container_width=True)
            
        with adm_tab3:
            st.subheader("⭐ Student Star Ratings & Theory Review")
            st.dataframe(feedback_df, use_container_width=True)
            
        with adm_tab4:
            st.dataframe(enquiry_df, use_container_width=True)
            
        with adm_tab5:
            st.dataframe(att_df, use_container_width=True)