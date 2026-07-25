import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse
import os
import pytz

# Page Configuration
st.set_page_config(page_title="Soft Tech Computers", page_icon="💻", layout="wide")

# File Paths
STUDENT_MASTER_FILE = "students_db.csv"
ATTENDANCE_LOG_FILE = "attendance_log.csv"
ENQUIRY_FILE = "enquiry_data.csv"
FEE_FILE = "course_fees_db.csv"
TEACHER_LOG_FILE = "teacher_attendance.csv"
TEACHERS_MASTER_FILE = "teachers_db.csv"
FEE_COLLECTION_LOG_FILE = "fee_collection_log.csv"
FEEDBACK_FILE = "student_feedback.csv"
ROUTINE_FILE = "routine_settings.csv"
PASSWORD_FILE = "passwords.csv"
TEACHER_PIN_FILE = "teacher_pin.csv"
LOGO_FILE = "logo.jpg"

# Load Data Safely & Fix Missing Columns
def load_clean_data(file_path, default_cols, is_student_file=False):
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            if df.empty:
                return pd.DataFrame(columns=default_cols)
            
            if is_student_file and 'Student ID' in df.columns:
                df = df.drop_duplicates(subset=['Student ID'], keep='first')
            
            for col in default_cols:
                if col not in df.columns:
                    if col == 'Total Fee':
                        df[col] = 8500.0
                    elif col == 'Paid':
                        df[col] = 0.0
                    elif col == 'Payment Breakdown':
                        df[col] = "0"
                    elif col == 'Admission Date':
                        df[col] = datetime.now().strftime("%Y-%m-%d")
                    else:
                        df[col] = ""
            return df[default_cols]
        except:
            return pd.DataFrame(columns=default_cols)
    return pd.DataFrame(columns=default_cols)

def save_data(df, file_path):
    df.to_csv(file_path, index=False)

# Password & PIN Management
def get_admin_password():
    if os.path.exists(PASSWORD_FILE):
        try:
            pdf = pd.read_csv(PASSWORD_FILE)
            if not pdf.empty and "password" in pdf.columns:
                return str(pdf["password"].iloc[0])
        except:
            pass
    return "admin123"

def set_admin_password(new_pass):
    pdf = pd.DataFrame([{"password": str(new_pass)}])
    pdf.to_csv(PASSWORD_FILE, index=False)

def get_teacher_pin():
    if os.path.exists(TEACHER_PIN_FILE):
        try:
            tpdf = pd.read_csv(TEACHER_PIN_FILE)
            if not tpdf.empty and "pin" in tpdf.columns:
                return str(tpdf["pin"].iloc[0])
        except:
            pass
    return "1234"

def set_teacher_pin(new_pin):
    tpdf = pd.DataFrame([{"pin": str(new_pin)}])
    tpdf.to_csv(TEACHER_PIN_FILE, index=False)

# Master Column Definitions
student_cols = ['Student ID', 'Name', 'Father Name', 'Mother Name', 'Mobile No', 'Address', 'Course', 'Batch', 'Admission Mode', 'Total Fee', 'Paid', 'Payment Breakdown', 'Admission Date']
attendance_cols = ['Date', 'Student ID', 'Name', 'Action', 'Time']
fee_collect_cols = ['Date', 'Collected By', 'Student ID', 'Student Name', 'Amount (₹)', 'Payment Mode']
teacher_cols = ['Date', 'Teacher Name', 'Shift', 'In-Time', 'Out-Time', 'Class Type', 'Topics Taught', 'Status', 'Shift Wage (₹)']
teacher_master_cols = ['Teacher ID', 'Teacher Name', 'Mobile No', 'Designation']
feedback_cols = ['Timestamp', 'Student Name / ID', 'Rating', 'Teaching Quality', 'Lab Infrastructure', 'Comments']

# Load Clean Databases
student_df = load_clean_data(STUDENT_MASTER_FILE, student_cols, is_student_file=True)
attendance_df = load_clean_data(ATTENDANCE_LOG_FILE, attendance_cols)
fee_log_df = load_clean_data(FEE_COLLECTION_LOG_FILE, fee_collect_cols)
enquiry_db = load_clean_data(ENQUIRY_FILE, ['Name', 'Mobile', 'Course Selected', 'Timestamp'])
teacher_db = load_clean_data(TEACHER_LOG_FILE, teacher_cols)
teachers_master_df = load_clean_data(TEACHERS_MASTER_FILE, teacher_master_cols)
feedback_db = load_clean_data(FEEDBACK_FILE, feedback_cols)
routine_db = load_clean_data(ROUTINE_FILE, ['Shift', 'Timing', 'Days', 'Assigned Class'])

# Default Teachers if master is empty
if teachers_master_df.empty:
    teachers_master_df = pd.DataFrame([
        {"Teacher ID": "TC-01", "Teacher Name": "Zaan Hazarika", "Mobile No": "9854341170", "Designation": "Director / Instructor"},
        {"Teacher ID": "TC-02", "Teacher Name": "BIJOY KURMI", "Mobile No": "9854865864", "Designation": "Faculty"}
    ])

# Clean Fixed STC Routine
if routine_db.empty:
    routine_db = pd.DataFrame([
        {"Shift": "Morning Shift", "Timing": "07:30 AM - 09:00 AM", "Days": "Regular", "Assigned Class": "Computer ADCA/DCA"},
        {"Shift": "Afternoon Shift", "Timing": "04:00 PM - 05:30 PM", "Days": "MWF / TTS Slots", "Assigned Class": "Computer Batch A"},
        {"Shift": "Evening Shift", "Timing": "05:30 PM - 07:00 PM", "Days": "MWF / TTS Slots", "Assigned Class": "Computer Batch B"}
    ])

# Session States
if 'fee_settings' not in st.session_state:
    st.session_state.fee_settings = {"ADCA": 8500, "DCA": 5500, "DTP": 4000, "Tally": 4500}

AVAILABLE_TOPICS = [
    "Basic", "Word", "Excel", "PPT", "Access", "HTML", "DHTML", 
    "Tally", "Python", "PageMaker", "Photoshop", "Internet", "Paint", "WordPad", "Notepad"
]
BATCH_OPTIONS = ["MWF", "TTS", "Regular"]
PAYMENT_MODES = ["Cash", "UPI (GooglePay/PhonePe/Paytm)", "Online / NetBanking", "Card / Cheque"]

# Helper Options
student_options = []
if not student_df.empty:
    student_options = [f"{row['Student ID']} - {row['Name']}" for _, row in student_df.iterrows()]

teacher_options = []
if not teachers_master_df.empty:
    teacher_options = [f"{row['Teacher ID']} - {row['Teacher Name']}" for _, row in teachers_master_df.iterrows()]

# Navigation Menu
menu = st.sidebar.radio("Navigation", ["🏠 Home & Enquiry", "🎓 Student Admission & Attendance", "👨‍🏫 Teacher Portal & Fee Entry", "🔐 Admin Panel"])

# ==========================================
# 1. PUBLIC DASHBOARD
# ==========================================
if menu == "🏠 Home & Enquiry":
    header_col1, header_col2 = st.columns([1, 4])
    with header_col1:
        if os.path.exists(LOGO_FILE):
            st.image(LOGO_FILE, width=130)
        else:
            st.title("💻 STC")
            
    with header_col2:
        st.markdown("<h1 style='color: #004085; margin-bottom: 0px;'>Soft Tech Computers</h1>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: #28a745; margin-top: 0px;'>An ISO 9001:2015 Certified Computer Training Institute | Since 2020</h4>", unsafe_allow_html=True)
        st.write("📍 **Location:** Kamarchuburi, Thelamara, Sonitpur, Assam - 784149 (Associate Center Code: 4159)")

    st.markdown("---")

    # --- TOP HIGHLIGHT: STUDENT OF THE MONTH ---
    st.markdown("### 🏆 Student of the Month")
    if not attendance_df.empty:
        top_att = attendance_df['Student ID'].value_counts()
        if not top_att.empty:
            top_st_id = top_att.index[0]
            top_count = top_att.iloc[0]
            matched_top = student_df[student_df['Student ID'] == top_st_id]
            top_name = matched_top.iloc[0]['Name'] if not matched_top.empty else top_st_id
            
            st.success(f"🌟 **Congratulations!** **{top_name}** ({top_st_id}) is our **Student of the Month** with **{top_count}** class attendances! 🎉")
    else:
        st.info("🌟 **Student of the Month:** Will be announced based on attendance performance!")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 🗓️ Active Class Time Table / Routine")
        st.table(routine_db)

        st.markdown("### 🪙 Courses & Course Packages")
        fees_list = [{"Course/Class": k, "Total Course Fee": f"₹ {v}/-"} for k, v in st.session_state.fee_settings.items()]
        st.table(pd.DataFrame(fees_list))

        # --- AI COURSE ADVISOR FEATURE ---
        st.markdown("### 🤖 Smart AI Course Recommendation Assistant")
        with st.expander("✨ Find the Best Course for You"):
            user_interest = st.selectbox("What is your primary goal?", ["Basic Computer Knowledge", "Office Work & Jobs", "Graphic Design & Publishing", "Accounting & Finance"])
            
            if user_interest == "Basic Computer Knowledge":
                st.write("👉 **Recommended:** **DCA (Diploma in Computer Applications)** — Fee: ₹5,500/-")
            elif user_interest == "Office Work & Jobs":
                st.write("👉 **Recommended:** **ADCA (Advance Diploma in Computer Applications)** — Fee: ₹8,500/-")
            elif user_interest == "Graphic Design & Publishing":
                st.write("👉 **Recommended:** **DTP (Desktop Publishing)** — Fee: ₹4,000/-")
            elif user_interest == "Accounting & Finance":
                st.write("👉 **Recommended:** **Tally ERP 9 / Prime** — Fee: ₹4,500/-")

        st.markdown("### 📱 Scan from Phone to Open Portal")
        qr_url = "https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=https://stcztc.streamlit.app"
        st.image(qr_url, caption="Scan this using Mobile Camera")

    with col2:
        st.markdown("### ✉️ Quick Course Enquiry")
        st.info("💡 **Enter Name & Mobile No below and submit to view Course Fee.**")

        with st.form("enquiry_form"):
            enq_name = st.text_input("Student Name *")
            enq_mobile = st.text_input("Mobile Number *")
            enq_course = st.selectbox("Select Course/Class *", list(st.session_state.fee_settings.keys()), index=0)

            submitted = st.form_submit_button("Submit Enquiry to View Fee")
            if submitted:
                if enq_name and enq_mobile:
                    selected_fee = st.session_state.fee_settings.get(enq_course, 5000)
                    
                    # Save Enquiry Data
                    new_enq = pd.DataFrame([[enq_name, enq_mobile, enq_course, datetime.now().strftime("%Y-%m-%d %H:%M")]], columns=enquiry_db.columns)
                    enquiry_db = pd.concat([enquiry_db, new_enq], ignore_index=True)
                    save_data(enquiry_db, ENQUIRY_FILE)

                    st.success(f"✅ **Enquiry Registered!** Total Course Fee for **{enq_course}** is **₹{selected_fee}/-**")

                    # WhatsApp Link
                    msg_text = f"Hello Soft Tech Computers!\nI submitted an enquiry:\nName: {enq_name}\nPhone: {enq_mobile}\nCourse: {enq_course}"
                    encoded_msg = urllib.parse.quote(msg_text)
                    whatsapp_number = "919101026718"
                    whatsapp_url = f"https://wa.me/{whatsapp_number}?text={encoded_msg}"

                    st.markdown(f'''
                        <a href="{whatsapp_url}" target="_blank">
                            <button style="background-color:#25D366; color:white; border:none; padding:10px 20px; border-radius:8px; font-weight:bold; font-size:15px; cursor:pointer; width:100%; margin-top:10px;">
                                📲 Send Details directly on WhatsApp
                            </button>
                        </a>
                    ''', unsafe_allow_html=True)
                else:
                    st.error("⚠️ Please fill in both Name and Mobile Number to view fee!")

# ==========================================
# 2. STUDENT PORTAL
# ==========================================
elif menu == "🎓 Student Admission & Attendance":
    st.title("🎓 Student Self-Service Portal")
    loc_check = st.checkbox("📍 Mandatory: Verify Device GPS Location (Must be within Center Boundary)")

    if loc_check:
        st.success("📍 GPS Location Verified Inside Center Boundary")
        tab1, tab2, tab3, tab4 = st.tabs(["📝 Official Admission Form", "⏱️ Mark Attendance", "🎯 Search Profile & SFPC", "⭐ Feedback & Review"])

        with tab1:
            st.subheader("📋 New Student Formal Admission Form")
            with st.form("admission_form"):
                st.markdown("#### 👤 Personal & Family Details")
                col_a, col_b = st.columns(2)
                s_name = col_a.text_input("Student Full Name *")
                s_mobile = col_b.text_input("Mobile Number *")
                s_father = col_a.text_input("Father's Name *")
                s_mother = col_b.text_input("Mother's Name *")

                st.markdown("---")
                st.markdown("#### 🏡 Mandatory Address Breakup")
                a_col1, a_col2 = st.columns(2)
                addr_vill = a_col1.text_input("Village / Town (Vill) *")
                addr_po = a_col2.text_input("Post Office (P.O.) *")
                addr_ps = a_col1.text_input("Police Station (P.S.) *")
                addr_pin = a_col2.text_input("PIN Code *")
                addr_dist = a_col1.text_input("District *", value="Sonitpur")

                st.markdown("---")
                st.markdown("#### 📚 Academic & Fee Details")
                c_col1, c_col2, c_col3 = st.columns(3)
                s_course = c_col1.selectbox("Selected Course *", list(st.session_state.fee_settings.keys()))
                s_batch = c_col2.selectbox("Batch Schedule *", BATCH_OPTIONS)
                s_mode = c_col3.selectbox("Admission Mode *", ["Monthly Installments", "Full Onetime"])

                p_col1, p_col2 = st.columns(2)
                s_initial_pay = p_col1.number_input("Initial Fee Paid (₹) *", min_value=0.0, value=999.0)
                s_pay_mode = p_col2.selectbox("Payment Mode *", PAYMENT_MODES)

                if st.form_submit_button("🎓 Confirm Registration"):
                    existing_mobiles = student_df['Mobile No'].astype(str).tolist() if not student_df.empty else []
                    
                    if str(s_mobile).strip() in existing_mobiles:
                        st.error("❌ **Duplicate Registration Blocked:** This Mobile Number is already registered for another student!")
                    elif s_name and s_mobile and addr_vill and addr_po and addr_ps and addr_pin and addr_dist:
                        new_id = f"STC26-00{len(student_df)+1}"
                        tot_f = st.session_state.fee_settings.get(s_course, 5000)
                        today_date_str = datetime.now().strftime("%Y-%m-%d")
                        
                        formatted_address = f"Vill- {addr_vill}, P.O.- {addr_po}, P.S.- {addr_ps}, PIN- {addr_pin}, Dist- {addr_dist}"
                        breakdown = f"[{today_date_str}] ₹{int(s_initial_pay)} ({s_pay_mode})"
                        
                        new_row = pd.DataFrame([[new_id, s_name, s_father, s_mother, str(s_mobile), formatted_address, s_course, s_batch, s_mode, tot_f, s_initial_pay, breakdown, today_date_str]], columns=student_df.columns)
                        student_df = pd.concat([student_df, new_row], ignore_index=True)
                        save_data(student_df, STUDENT_MASTER_FILE)

                        # Auto Log Payment
                        new_log = pd.DataFrame([[today_date_str, "Self Registration / Admin", new_id, s_name, s_initial_pay, s_pay_mode]], columns=fee_log_df.columns)
                        fee_log_df = pd.concat([fee_log_df, new_log], ignore_index=True)
                        save_data(fee_log_df, FEE_COLLECTION_LOG_FILE)

                        st.success(f"🎉 **Registration Successful!** Generated Student ID: **{new_id}**")
                    else:
                        st.error("⚠️ Please fill in all mandatory fields!")

        with tab2:
            st.subheader("Mark Daily Attendance (Private Search)")
            st.info("🔎 Search student by Roll No or Mobile No to mark attendance.")
            
            att_search = st.text_input("Enter Student Roll Number or Mobile Number", key="att_s_q")
            if att_search:
                matched_att = student_df[(student_df['Student ID'].astype(str).str.contains(att_search, case=False, na=False)) | 
                                         (student_df['Mobile No'].astype(str).str.contains(att_search, case=False, na=False))]
                
                if not matched_att.empty:
                    st_row = matched_att.iloc[0]
                    sid = st_row['Student ID']
                    st_name = st_row['Name']
                    
                    st.success(f"👤 **Student Found:** {st_name} ({sid})")
                    action = st.radio("Action", ["Check-In (In-Time)", "Check-Out (Out-Time)"])
                    
                    if st.button("Submit Attendance Now"):
                        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        today_str = datetime.now().strftime("%Y-%m-%d")
                        
                        att_row = pd.DataFrame([[today_str, sid, st_name, action, now_str]], columns=attendance_df.columns)
                        attendance_df = pd.concat([attendance_df, att_row], ignore_index=True)
                        save_data(attendance_df, ATTENDANCE_LOG_FILE)
                        st.success(f"✅ **Attendance Recorded Successfully** for **{st_name}** ({action}) at {now_str}")
                else:
                    st.error("No student found with this Roll Number or Mobile Number!")

        with tab3:
            st.subheader("🔎 Search Student Profile & SFPC Eligibility")
            search_query = st.text_input("Enter Roll Number (Student ID) or Mobile Number")
            
            if search_query:
                matched = student_df[(student_df['Student ID'].astype(str).str.contains(search_query, case=False, na=False)) | 
                                     (student_df['Mobile No'].astype(str).str.contains(search_query, case=False, na=False))]
                
                if not matched.empty:
                    s_info = matched.iloc[0]
                    st_id = s_info['Student ID']
                    
                    st_att_count = len(attendance_df[attendance_df['Student ID'] == st_id]) if not attendance_df.empty else 0
                    total_classes = 20  
                    att_pct = round((st_att_count / total_classes) * 100, 1) if total_classes > 0 else 0
                    
                    try:
                        adm_date_str = str(s_info['Admission Date']) if pd.notnull(s_info['Admission Date']) and str(s_info['Admission Date']) != "" else "2026-01-01"
                        adm_dt = datetime.strptime(adm_date_str, "%Y-%m-%d")
                    except:
                        adm_dt = datetime(2026, 1, 1)

                    today_dt = datetime.now()
                    days_passed = (today_dt - adm_dt).days
                    months_enrolled = max(1, round(days_passed / 30.0, 1))

                    try:
                        tot = float(s_info['Total Fee'])
                    except:
                        tot = 8500.0
                    
                    try:
                        paid = float(s_info['Paid'])
                    except:
                        paid = 0.0

                    breakdown = str(s_info['Payment Breakdown']) if pd.notnull(s_info['Payment Breakdown']) and str(s_info['Payment Breakdown']) != "" else f"₹{int(paid)}"
                    
                    monthly_rate = 550
                    total_monthly_due_till_now = months_enrolled * monthly_rate
                    required_50_pct_monthly = total_monthly_due_till_now * 0.5
                    
                    min_required_fee_total = 999 + required_50_pct_monthly
                    fee_cleared = paid >= min_required_fee_total or paid >= tot
                    
                    st.markdown("---")
                    st.markdown(f"### 👤 Profile Details: **{s_info['Name']}** ({st_id})")
                    c1, c2, c3 = st.columns(3)
                    c1.write(f"**Course:** {s_info['Course']}")
                    c1.write(f"**Batch:** {s_info['Batch']}")
                    c2.write(f"**Father:** {s_info['Father Name']}")
                    c2.write(f"**Mobile:** {s_info['Mobile No']}")
                    c3.write(f"**Address:** {s_info['Address']}")
                    c3.write(f"**Admission Date:** {s_info['Admission Date']}")

                    st.markdown("### 💳 Fee Status & Payment History Ledger")
                    st.info(f"**Total Course Fee:** ₹{tot} | **Total Paid:** ₹{paid} | **Due Balance:** ₹{tot - paid}")
                    st.success(f"📊 **Installment Breakdown:** `{breakdown}`")

                    st.markdown("### 🎯 Sunday Free Practice Class (SFPC) Criteria")
                    st.write(f"* **Attendance Status:** {st_att_count} Days attended (**{att_pct}%**) [Min Required: 75%]")
                    st.write(f"* **Calculated Fee Status:** Paid ₹{paid} / Required ₹{min_required_fee_total}")

                    if att_pct >= 75 and fee_cleared:
                        st.success("🎉 **STATUS: ELIGIBLE FOR SUNDAY FREE PRACTICE CLASS (SFPC)!**")
                    else:
                        st.error("⚠️ **STATUS: NOT ELIGIBLE FOR SFPC YET.**")
                        if att_pct < 75:
                            st.warning(f"❌ Attendance Low: Currently {att_pct}%. Needs minimum 75%.")
                        if not fee_cleared:
                            st.warning(f"❌ Fee Due: Need to pay at least ₹{min_required_fee_total} (Admission + 50% monthly dues).")
                else:
                    st.error("No Student found with this Roll Number or Mobile Number!")

        with tab4:
            st.subheader("⭐ Submit Student Feedback & Institute Review")
            with st.form("feedback_form", clear_on_submit=True):
                fb_st_name = st.text_input("Your Name / Student ID")
                fb_rating = st.slider("Overall Rating for Center", 1, 5, 5)
                fb_teach_q = st.selectbox("Teaching Quality", ["Excellent", "Good", "Average", "Needs Improvement"])
                fb_lab_q = st.selectbox("Computer Lab & PC Maintenance", ["Excellent", "Good", "Average", "Needs Improvement"])
                fb_comments = st.text_area("Your Suggestions / Feedback")

                if st.form_submit_button("Submit Feedback"):
                    if fb_st_name:
                        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                        new_fb = pd.DataFrame([[now_str, fb_st_name, fb_rating, fb_teach_q, fb_lab_q, fb_comments]], columns=feedback_db.columns)
                        feedback_db = pd.concat([feedback_db, new_fb], ignore_index=True)
                        save_data(feedback_db, FEEDBACK_FILE)
                        st.success("✅ **Thank you for your valuable feedback!**")
                    else:
                        st.warning("Please enter your Name or Student ID.")
    else:
        st.warning("⚠️ Please verify GPS Location checkbox above to access Student Portal.")

# ==========================================
# 3. TEACHER PORTAL
# ==========================================
elif menu == "👨‍🏫 Teacher Portal & Fee Entry":
    st.title("👨‍🏫 Teacher & Staff Desk")
    
    t_loc_check = st.checkbox("Verify location (Must be inside center boundary)", key="t_loc")
    current_teacher_pin = get_teacher_pin()
    t_pin_input = st.text_input("Enter Teacher Passcode / PIN", type="password", key="t_pin")

    if t_loc_check and t_pin_input == current_teacher_pin:
        st.success("Access Granted to Staff Desk.")
        ttab1, ttab2 = st.tabs(["⏱️ Teacher Class & Topics Log", "💵 Collect Fee Counter"])

        with ttab1:
            st.subheader("Teacher Shift, Class Type & Topics Logging")
            with st.form("teacher_log_form"):
                t_selected_teacher = st.selectbox("Select Teacher Name", teacher_options if teacher_options else ["TC-01 - Zaan Hazarika"])
                t_shift = st.selectbox("Shift", ["Morning Shift", "Afternoon Shift", "Evening Shift"])
                t_in = st.time_input("In-Time", datetime.now().time())
                t_out = st.time_input("Out-Time", datetime.now().time())
                
                t_class_type = st.radio("Class Type Conducted Today", ["Theory", "Practical", "Both Theory & Practical"])
                t_selected_topics = st.multiselect("Select Topics Taught Today (Multiple allowed)", AVAILABLE_TOPICS)
                t_status = st.selectbox("Status", ["Present", "Leave / Absent"])

                if st.form_submit_button("Submit Teacher Log"):
                    t_teacher_name = t_selected_teacher.split(" - ")[1] if " - " in t_selected_teacher else t_selected_teacher
                    today_str = datetime.now().strftime("%Y-%m-%d")
                    t_in_str = t_in.strftime("%I:%M %p")
                    t_out_str = t_out.strftime("%I:%M %p")
                    topics_str = ", ".join(t_selected_topics) if t_selected_topics else "General"
                    
                    shift_wage = round(230.0 / 3.0, 2) if t_status == "Present" else 0.0

                    new_t_log = pd.DataFrame([[today_str, t_teacher_name, t_shift, t_in_str, t_out_str, t_class_type, topics_str, t_status, shift_wage]], columns=teacher_db.columns)
                    teacher_db = pd.concat([teacher_db, new_t_log], ignore_index=True)
                    save_data(teacher_db, TEACHER_LOG_FILE)
                    st.success("✅ **Class log recorded successfully!**")

        with ttab2:
            st.subheader("💵 Deposit Student Fee (Teacher Counter)")
            st.write("Collect cash/payment and submit entry below.")
            
            if not student_df.empty:
                t_collector = st.selectbox("Select Teacher / Collector Name", teacher_options if teacher_options else ["TC-01 - Zaan Hazarika"], key="t_coll_sel")
                t_selected_opt = st.selectbox("Select Student", student_options, key="t_fee_sid")
                
                col_m1, col_m2 = st.columns(2)
                t_add_amt = col_m1.number_input("Amount Collected (₹)", min_value=100.0, step=100.0, key="t_amt")
                t_fee_pmode = col_m2.selectbox("Payment Mode", PAYMENT_MODES, key="t_pmode")

                if st.button("Submit Fee Entry"):
                    teacher_name_input = t_collector.split(" - ")[1] if " - " in t_collector else t_collector
                    t_f_sid = t_selected_opt.split(" - ")[0]
                    st_name_val = t_selected_opt.split(" - ")[1] if " - " in t_selected_opt else "Student"
                    idx = student_df[student_df['Student ID'] == t_f_sid].index[0]

                    try:
                        old_paid = float(student_df.at[idx, 'Paid'])
                    except:
                        old_paid = 0.0

                    new_paid = old_paid + t_add_amt
                    student_df.at[idx, 'Paid'] = new_paid

                    today_date_str = datetime.now().strftime("%Y-%m-%d")
                    old_bd = str(student_df.at[idx, 'Payment Breakdown']) if pd.notnull(student_df.at[idx, 'Payment Breakdown']) and str(student_df.at[idx, 'Payment Breakdown']) != "" else f"₹{int(old_paid)}"
                    new_bd = f"{old_bd} | [{today_date_str}] ₹{int(t_add_amt)} ({t_fee_pmode})"
                    student_df.at[idx, 'Payment Breakdown'] = new_bd

                    save_data(student_df, STUDENT_MASTER_FILE)

                    new_fee_entry = pd.DataFrame([[today_date_str, teacher_name_input, t_f_sid, st_name_val, t_add_amt, t_fee_pmode]], columns=fee_log_df.columns)
                    fee_log_df = pd.concat([fee_log_df, new_fee_entry], ignore_index=True)
                    save_data(fee_log_df, FEE_COLLECTION_LOG_FILE)

                    st.success("✅ **Fee Entry Saved Successfully!**")
                    st.rerun()
    elif t_pin_input != "" and t_pin_input != current_teacher_pin:
        st.error("Incorrect Teacher Passcode/PIN!")

# ==========================================
# 4. ADMIN PANEL
# ==========================================
elif menu == "🔐 Admin Panel":
    st.title("🔐 Director / Admin Control Panel")
    
    current_admin_pass = get_admin_password()
    pwd = st.text_input("Enter Admin Password", type="password")

    if pwd == current_admin_pass:
        st.success("Access Granted. Welcome Sir!")

        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
            "📊 Student Registry & Balance", 
            "🧾 Fee Collection Audit Log", 
            "⏱️ Student Attendance Logs", 
            "👨‍🏫 Teacher Master & Salary Logs", 
            "📩 Enquiries", 
            "⭐ Student Feedbacks",
            "🔑 Security Settings"
        ])

        with tab1:
            st.markdown("### Master Student Records & Fee Summary Manager")
            
            disp_df = student_df.copy()
            disp_df['Total Fee'] = pd.to_numeric(disp_df['Total Fee'], errors='coerce').fillna(8500.0)
            disp_df['Paid'] = pd.to_numeric(disp_df['Paid'], errors='coerce').fillna(0.0)
            disp_df['Balance Due (₹)'] = disp_df['Total Fee'] - disp_df['Paid']
            
            view_cols = ['Student ID', 'Name', 'Mobile No', 'Course', 'Batch', 'Total Fee', 'Paid', 'Balance Due (₹)', 'Payment Breakdown', 'Admission Date']
            existing_view_cols = [c for c in view_cols if c in disp_df.columns]
            
            st.dataframe(disp_df[existing_view_cols], use_container_width=True)

            # --- SEARCH & VIEW SPECIFIC STUDENT FEE LEDGER ---
            st.markdown("---")
            st.markdown("### 💳 Search Individual Student Installment Ledger")
            if not student_df.empty:
                chk_st_opt = st.selectbox("Select Student to Check Fee Ledger", student_options, key="admin_chk_fee")
                chk_sid = chk_st_opt.split(" - ")[0]
                chk_row = student_df[student_df['Student ID'] == chk_sid].iloc[0]
                
                c_tot = float(chk_row['Total Fee']) if pd.notnull(chk_row['Total Fee']) else 8500.0
                c_paid = float(chk_row['Paid']) if pd.notnull(chk_row['Paid']) else 0.0
                c_due = c_tot - c_paid
                c_bd = str(chk_row['Payment Breakdown']) if pd.notnull(chk_row['Payment Breakdown']) else str(int(c_paid))
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Course Fee", f"₹{c_tot}")
                col2.metric("Total Fee Paid", f"₹{c_paid}")
                col3.metric("Pending Due Balance", f"₹{c_due}", delta=f"-₹{c_due}" if c_due > 0 else "Cleared")
                
                st.success(f"📋 **Installments Paid History:** `{c_bd}`")

            # --- EDIT STUDENT PROFILE SECTION ---
            st.markdown("---")
            st.markdown("### ✏️ Edit Student Profile Details")
            if not student_df.empty:
                edit_selected_st = st.selectbox("Select Student to Edit", student_options, key="edit_sid_select")
                edit_sid = edit_selected_st.split(" - ")[0]
                e_row = student_df[student_df['Student ID'] == edit_sid].iloc[0]

                with st.form("edit_student_form"):
                    e_name = st.text_input("Name", value=str(e_row['Name']))
                    e_father = st.text_input("Father Name", value=str(e_row['Father Name']))
                    e_mother = st.text_input("Mother Name", value=str(e_row['Mother Name']))
                    e_mobile = st.text_input("Mobile No", value=str(e_row['Mobile No']))
                    e_address = st.text_input("Full Address", value=str(e_row['Address']))
                    e_course = st.selectbox("Course", list(st.session_state.fee_settings.keys()), index=0)
                    e_batch = st.selectbox("Batch Schedule", BATCH_OPTIONS)
                    e_mode = st.selectbox("Admission Mode", ["Monthly Installments", "Full Onetime"])

                    if st.form_submit_button("Update Student Profile"):
                        e_idx = student_df[student_df['Student ID'] == edit_sid].index[0]
                        
                        student_df.loc[e_idx, 'Name'] = str(e_name)
                        student_df.loc[e_idx, 'Father Name'] = str(e_father)
                        student_df.loc[e_idx, 'Mother Name'] = str(e_mother)
                        student_df.loc[e_idx, 'Mobile No'] = str(e_mobile)
                        student_df.loc[e_idx, 'Address'] = str(e_address)
                        student_df.loc[e_idx, 'Course'] = str(e_course)
                        student_df.loc[e_idx, 'Batch'] = str(e_batch)
                        student_df.loc[e_idx, 'Admission Mode'] = str(e_mode)

                        save_data(student_df, STUDENT_MASTER_FILE)
                        st.success(f"✅ **Updated Profile for {edit_selected_st} successfully!**")
                        st.rerun()

            st.markdown("---")
            st.markdown("### 🗑️ Permanent Delete Student")
            if not student_df.empty:
                del_selected_st = st.selectbox("Select Student to Remove", student_options, key="del_sid_select")
                del_roll = del_selected_st.split(" - ")[0]
                if st.button("Delete Selected Student"):
                    student_df = student_df[student_df['Student ID'] != del_roll]
                    save_data(student_df, STUDENT_MASTER_FILE)
                    st.success(f"✅ **Removed {del_selected_st} permanently!**")
                    st.rerun()

        with tab2:
            st.markdown("### 🧾 Teacher / Staff Fee Collection Audit Log")
            st.info("Here you can trace exactly WHICH teacher collected HOW MUCH money, from WHOM, and on WHICH DATE with PAYMENT MODE.")
            st.dataframe(fee_log_df, use_container_width=True)

        with tab3:
            st.markdown("### ⏱️ Student Attendance Logs")
            if not attendance_df.empty:
                st.dataframe(attendance_df, use_container_width=True)
            else:
                st.write("No attendance logs found yet.")

        with tab4:
            st.markdown("### 👨‍🏫 Teacher Master & Daily Logs")
            st.subheader("➕ Register New Teacher / Faculty")
            with st.form("add_teacher_form"):
                new_t_code = f"TC-0{len(teachers_master_df)+1}"
                new_t_name = st.text_input("Teacher Full Name")
                new_t_mob = st.text_input("Mobile No")
                new_t_desig = st.text_input("Designation", value="Faculty")

                if st.form_submit_button("Add Teacher"):
                    if new_t_name:
                        t_new_row = pd.DataFrame([[new_t_code, new_t_name, str(new_t_mob), new_t_desig]], columns=teachers_master_df.columns)
                        teachers_master_df = pd.concat([teachers_master_df, t_new_row], ignore_index=True)
                        save_data(teachers_master_df, TEACHERS_MASTER_FILE)
                        st.success(f"✅ **Added Teacher {new_t_name} ({new_t_code}) successfully!**")
                        st.rerun()

            st.markdown("---")
            st.subheader("📋 Master Registered Teachers List")
            st.dataframe(teachers_master_df, use_container_width=True)

            st.markdown("---")
            st.subheader("🔒 Teacher Shift Logs & Correct Calculated Salary")
            if not teacher_db.empty:
                t_wages_df = teacher_db.copy()
                t_wages_df['Shift Wage (₹)'] = pd.to_numeric(t_wages_df['Shift Wage (₹)'], errors='coerce').fillna(0.0)
                
                total_teacher_salary = round(t_wages_df['Shift Wage (₹)'].sum(), 2)
                st.metric(label="Total Teacher Accumulated Wages/Salary", value=f"₹{total_teacher_salary}/-")
                st.dataframe(t_wages_df, use_container_width=True)
            else:
                st.write("No Teacher logs found yet.")

        with tab5:
            st.markdown("### Received Enquiries")
            st.dataframe(enquiry_db, use_container_width=True)

        with tab6:
            st.markdown("### ⭐ Received Student Feedbacks & Reviews")
            st.dataframe(feedback_db, use_container_width=True)

        with tab7:
            st.markdown("### 🔑 Admin Password & Teacher PIN Security Control")
            
            curr_pin_val = get_teacher_pin()
            st.success(f"📌 **Current Live Teacher PIN:** `{curr_pin_val}`")
            st.markdown("---")

            col_a, col_b = st.columns(2)

            with col_a:
                st.subheader("Change Admin Password")
                with st.form("change_pass_form"):
                    new_p1 = st.text_input("New Admin Password", type="password")
                    new_p2 = st.text_input("Confirm Admin Password", type="password")
                    if st.form_submit_button("Update Admin Password"):
                        if new_p1 and new_p1 == new_p2:
                            set_admin_password(new_p1)
                            st.success("✅ **Admin Password updated!**")
                        else:
                            st.error("Passwords do not match!")

            with col_b:
                st.subheader("Change / Update Teacher Passcode (PIN)")
                with st.form("change_tpin_form"):
                    new_pin = st.text_input("Enter New Teacher PIN (e.g. 1234)", type="password")
                    if st.form_submit_button("Update Teacher PIN"):
                        if new_pin.strip() != "":
                            set_teacher_pin(new_pin)
                            st.success("✅ **Teacher PIN updated successfully!**")
                            st.rerun()
    elif pwd != "":
        st.error("Incorrect Password!")