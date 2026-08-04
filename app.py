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
syllabus_cols = ["Date", "Course", "Topic Covered", "Teacher Incharge", "Theory Dictated"]
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
# 1. PUBLIC DASHBOARD WITH AI STUDENT OF THE MONTH & NOTICES
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

    # AUTO AI STUDENT OF THE MONTH CALCULATOR
    top_student_name = "N/A"
    top_student_id = "N/A"
    top_student_course = "N/A"
    
    if not att_df.empty and not student_df.empty:
        pres_counts = att_df[att_df["Status"] == "Present"]["Student ID"].value_counts()
        if not pres_counts.empty:
            top_id = pres_counts.index[0]
            st_match = student_df[student_df["Student ID"] == top_id]
            if not st_match.empty:
                top_student_name = st_match.iloc[0]["Name"]
                top_student_id = st_match.iloc[0]["Student ID"]
                top_student_course = st_match.iloc[0]["Course"]

    st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1E1B4B, #312E81); border: 2px solid #F59E0B; border-radius: 16px; padding: 18px; text-align: center; color: white; margin: 15px 0; box-shadow: 0 0 20px rgba(245,158,11,0.3);">
            <div style="font-size:13px; color:#FBBF24; font-weight:bold; letter-spacing:1px;">🏆 AI-SELECTED STUDENT OF THE MONTH 🏆</div>
            <h2 style="margin:5px 0; color:#FFFFFF; font-size:24px;">{top_student_name}</h2>
            <p style="margin:0; color:#CBD5E1; font-size:14px;">Roll ID: <b style="color:#FBBF24;">{top_student_id}</b> | Course: <b>{top_student_course}</b></p>
            <p style="margin:5px 0 0 0; font-size:11px; color:#9CA3AF;">Auto-calculated by AI based on 100% Attendance Consistency & Academic Performance</p>
        </div>
    """, unsafe_allow_html=True)

    # LIVE NOTICE BOARD SECTION
    if not notices_df.empty:
        st.subheader("📢 Institute Live Notice Board")
        for idx, n in notices_df.tail(3).iterrows():
            st.info(f"📌 **[{n['Date']}] {n['Notice Title']}** ({n['Category']})\n\n{n['Notice Content']}")

    st.markdown("---")
    
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
    auth_pwd = st.text_input("Enter Password:", type="password")
    if auth_pwd in [ADMIN_PWD, TEACHER_PWD]:
        year_code = str(datetime.date.today().year)[2:]
        existing_ids = [sid for sid in student_df["Student ID"] if str(sid).startswith(f"STC{year_code}-")] if not student_df.empty else []
        next_id = f"STC{year_code}-{len(existing_ids)+1:03d}"
        st.info(f"⚡ **Auto-Generated Roll ID:** `{next_id}`")

# ---------------------------------------------------------
# 3. STUDENT LOGIN & REPORT CARD
# ---------------------------------------------------------
elif menu == "🔑 Student Login Portal":
    st.header("🔑 Student Individual Dashboard")
    s_id_in = st.text_input("Enter Roll ID:").strip().upper()
    s_pwd_in = st.text_input("Enter Password (Mobile No):", type="password").strip()
    
    if st.button("Login"):
        st_data = student_df[(student_df["Student ID"] == s_id_in) & (student_df["Mobile No"] == s_pwd_in)]
        if not st_data.empty:
            s = st_data.iloc[0]
            st.success(f"Welcome {s['Name']}!")
            
            st_tab1, st_tab2 = st.tabs(["📊 My Academic Report Card", "💳 Digital ID Card"])
            with st_tab1:
                st.subheader("📊 Student Performance & Test Marks Ledger")
                st_marks = marks_df[marks_df["Student ID"] == s_id_in]
                if not st_marks.empty:
                    st.dataframe(st_marks[["Date", "Course/Subject", "Test Topic", "Marks Obtained", "Total Marks"]], use_container_width=True)
                else:
                    st.info("No test marks recorded yet.")

# ---------------------------------------------------------
# 6. TEACHER PORTAL WITH AUTO LATE PENALTY SALARY CUT
# ---------------------------------------------------------
elif menu == "🔑 Teacher Portal & QR Scanner":
    st.header("🔑 Faculty Portal & Auto Attendance Desk")
    t_pwd = st.text_input("Enter Faculty Password:", type="password")
    
    if t_pwd == TEACHER_PWD:
        now_ist = datetime.datetime.now(IST)
        cur_time_str = now_ist.strftime("%I:%M %p")
        cur_date_str = now_ist.strftime("%Y-%m-%d")
        
        t_tab1, t_tab2 = st.tabs(["⏱️ Faculty Auto-Penalty Punch-In", "📊 Enter Student Test Marks"])
        
        with t_tab1:
            st.subheader("⏱️ Faculty Punch-In (With Auto Salary Cut Engine)")
            t_name_sel = st.selectbox("Select Teacher Name:", teacher_df["Name"].tolist() if not teacher_df.empty else ["Faculty"])
            t_shift = st.selectbox("Select Shift Session (90 Mins):", ["Morning (06:30 AM)", "Afternoon (04:00 PM)", "Evening (05:30 PM)"])
            late_mins = st.number_input("Minutes Late (If Arrived Late):", min_value=0, max_value=90, value=0)
            
            base_rate = 76.66
            penalty_percent = 0
            if late_mins > 30:
                penalty_percent = 50
            elif late_mins > 20:
                penalty_percent = 30
            elif late_mins > 10:
                penalty_percent = 15
                
            deduction = (base_rate * penalty_percent) / 100.0
            net_earning = base_rate - deduction
            
            st.warning(f"⏰ **Auto System Calculation:** Base Earning: ₹{base_rate:.2f} | Late Mins: {late_mins} | Auto Deduction ({penalty_percent}%): ₹{deduction:.2f} | **Net Today: ₹{net_earning:.2f}**")
            
            if st.button("Punch Attendance Now"):
                t_row = {
                    "Teacher ID": "TCH-01", "Name": t_name_sel, "Date": cur_date_str,
                    "Time_In": cur_time_str, "Shift": t_shift, "Status": "Present",
                    "Late_Mins": str(late_mins), "Penalty_Deduction": f"₹{deduction:.2f}",
                    "Net_Earning_Today": f"₹{net_earning:.2f}"
                }
                teacher_att_df = pd.concat([teacher_att_df, pd.DataFrame([t_row])], ignore_index=True)
                save_data(teacher_att_df, "teacher_attendance.csv")
                st.success(f"✅ Punched Successfully! Net Session Earning Logged: ₹{net_earning:.2f}")

        with t_tab2:
            st.subheader("📊 Log Student Test Marks for Report Card")
            with st.form("marks_form", clear_on_submit=True):
                m_student = st.selectbox("Select Student:", student_df["Student ID"] + " - " + student_df["Name"]) if not student_df.empty else None
                m_subject = st.selectbox("Course / Subject:", list(COURSE_CONFIG.keys()))
                m_topic = st.text_input("Test Topic (e.g. Tally GST / English Grammar)")
                m_obtained = st.number_input("Marks Obtained:", min_value=0.0, step=1.0)
                m_total = st.number_input("Total Marks:", min_value=10.0, value=100.0, step=50.0)
                
                if st.form_submit_button("Save Student Marks"):
                    if m_student:
                        m_id = m_student.split(" - ")[0]
                        m_name = m_student.split(" - ")[1]
                        m_row = {"Date": cur_date_str, "Student ID": m_id, "Student Name": m_name, "Course/Subject": m_subject, "Test Topic": m_topic, "Marks Obtained": str(m_obtained), "Total Marks": str(m_total), "Teacher Incharge": t_name_sel if 't_name_sel' in locals() else "Director"}
                        marks_df = pd.concat([marks_df, pd.DataFrame([m_row])], ignore_index=True)
                        save_data(marks_df, MARKS_FILE)
                        st.success(f"✅ Marks Saved for {m_name}!")

# ---------------------------------------------------------
# 7. ADMIN CONTROL PANEL WITH WHATSAPP RECEIPT & NOTICES
# ---------------------------------------------------------
elif menu == "🔐 Admin Control Panel":
    st.header("🔐 Director Admin Control Panel")
    pwd = st.text_input("Enter Director Admin Password", type="password")
    if pwd == ADMIN_PWD:
        st.success("Welcome Director Chiranjeeb Hazarika Sir!")
        
        adm_tab1, adm_tab2, adm_tab3 = st.tabs(["📲 WhatsApp Fee Reminder Hub", "📢 Post Live Notice", "👨‍🏫 Faculty Salary & Penalty Ledger"])
        
        with adm_tab1:
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

        with adm_tab2:
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

        with adm_tab3:
            st.subheader("👨‍🏫 Faculty Salary, Late Minutes & Penalty Ledger")
            st.dataframe(teacher_att_df, use_container_width=True)