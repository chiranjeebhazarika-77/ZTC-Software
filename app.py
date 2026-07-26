import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse
import os
import pytz

# Indian Standard Time (IST) Setup
IST = pytz.timezone('Asia/Kolkata')

def get_ist_now():
    return datetime.now(IST)

def get_ist_date_str():
    return get_ist_now().strftime("%Y-%m-%d")

def get_ist_time_str():
    return get_ist_now().strftime("%I:%M %p")

def get_ist_datetime_str():
    return get_ist_now().strftime("%Y-%m-%d %I:%M %p")

# Page Configuration
st.set_page_config(page_title="Soft Tech Computers", page_icon="💻", layout="wide")

# Custom Colorful & Bold Navigation Styling
st.markdown("""
<style>
    /* Custom Navigation Button Colors & Fonts */
    .stRadio > div {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 10px;
    }
    div[data-testid="stMarkdownContainer"] > p {
        font-size: 16px;
    }
    /* Highlight Cards */
    .card-box {
        border: 2px solid #004085;
        border-radius: 10px;
        padding: 15px;
        background-color: #f0f8ff;
    }
</style>
""", unsafe_allow_html=True)

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
STUDENT_PASSWORDS_FILE = "student_passwords.csv"
LOGO_FILE = "logo.jpg"
PHOTOS_DIR = "student_photos"

# Ensure Photos Directory Exists
if not os.path.exists(PHOTOS_DIR):
    os.makedirs(PHOTOS_DIR)

# Master Column Definitions Matching Record Form
student_cols = [
    'Student ID', 'Name', 'Father Name', 'Mother Name', 'Gender', 'DOB', 'Caste', 'Mobile No', 
    'Vill Town', 'PO', 'PS', 'PIN Code', 'District', 'Full Address', 'Course', 'Duration', 'Session', 
    'Join Date', 'Valid Up To', 'Batch Time', 'Admission Mode', 'Total Fee', 'Discount', 'Exam Fee', 
    'Paid', 'Payment Breakdown', 'Admission Date', 'Exam Date', 'Result Grade', 'Cert Issue Date', 
    'Exam Reg Status', 'Form Fillup Status', 'Admit Card Status', 'Cert No', 'Marksheet No'
]
attendance_cols = ['Date', 'Student ID', 'Name', 'Action', 'Time']
fee_collect_cols = ['Date', 'Collected By', 'Student ID', 'Student Name', 'Amount (₹)', 'Payment Mode', 'Fee Receipt No']
teacher_cols = ['Date', 'Teacher Name', 'Shift', 'In-Time', 'Out-Time', 'Class Type', 'Topics Taught', 'Status', 'Shift Wage (₹)']
teacher_master_cols = ['Teacher ID', 'Teacher Name', 'Mobile No', 'Designation']
feedback_cols = ['Timestamp', 'Student Name / ID', 'Rating', 'Teaching Quality', 'Lab Infrastructure', 'Comments']

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
                        df[col] = 8598.0
                    elif col == 'Discount':
                        df[col] = 0.0
                    elif col == 'Exam Fee':
                        df[col] = 999.0
                    elif col == 'Paid':
                        df[col] = 0.0
                    elif col == 'Payment Breakdown':
                        df[col] = "0"
                    elif col == 'Admission Date':
                        df[col] = get_ist_date_str()
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

# Load Clean Databases
student_df = load_clean_data(STUDENT_MASTER_FILE, student_cols, is_student_file=True)
attendance_df = load_clean_data(ATTENDANCE_LOG_FILE, attendance_cols)
fee_log_df = load_clean_data(FEE_COLLECTION_LOG_FILE, fee_collect_cols)
enquiry_db = load_clean_data(ENQUIRY_FILE, ['Name', 'Mobile', 'Course Selected', 'Timestamp'])
teacher_db = load_clean_data(TEACHER_LOG_FILE, teacher_cols)
teachers_master_df = load_clean_data(TEACHERS_MASTER_FILE, teacher_master_cols)
feedback_db = load_clean_data(FEEDBACK_FILE, feedback_cols)
routine_db = load_clean_data(ROUTINE_FILE, ['Shift', 'Timing', 'Days', 'Assigned Class'])

# Student Passwords DB
st_pass_cols = ['Student ID', 'Password']
st_pass_df = load_clean_data(STUDENT_PASSWORDS_FILE, st_pass_cols)

# Default Teachers if master is empty
if teachers_master_df.empty:
    teachers_master_df = pd.DataFrame([
        {"Teacher ID": "TC-01", "Teacher Name": "Zaan Hazarika", "Mobile No": "9854341170", "Designation": "Director / Instructor"},
        {"Teacher ID": "TC-02", "Teacher Name": "BIJOY KURMI", "Mobile No": "9854865864", "Designation": "Faculty"}
    ])

# Clean Fixed STC Routine
if routine_db.empty:
    routine_db = pd.DataFrame([
        {"Shift": "Morning Shift", "Timing": "07:30 AM - 09:00 AM", "Days": "MWF / TTS Slots", "Assigned Class": "Computer ADCA/DCA"},
        {"Shift": "Afternoon Shift", "Timing": "04:00 PM - 05:30 PM", "Days": "MWF / TTS Slots", "Assigned Class": "Computer Batch A"},
        {"Shift": "Evening Shift", "Timing": "05:30 PM - 07:00 PM", "Days": "MWF / TTS Slots", "Assigned Class": "Computer Batch B"}
    ])

# Session States
if 'fee_settings' not in st.session_state:
    st.session_state.fee_settings = {"ADCA": 8598, "DCA": 5500, "DTP": 4000, "Tally": 4500}

AVAILABLE_TOPICS = [
    "Basic Computer", "MS Word", "MS Excel", "MS PPT", "MS Access", "HTML / DHTML", 
    "Tally ERP 9 / Prime", "Python Programming", "PageMaker", "Photoshop", "Internet & Cyber Security", "Paint / WordPad"
]

BATCH_OPTIONS = [
    "MWF (Morning - 07:30 AM)",
    "MWF (Afternoon - 04:00 PM)",
    "MWF (Evening - 05:30 PM)",
    "TTS (Morning - 07:30 AM)",
    "TTS (Afternoon - 04:00 PM)",
    "TTS (Evening - 05:30 PM)",
    "Regular Daily Batch"
]

PAYMENT_MODES = ["Cash", "UPI (GooglePay/PhonePe/Paytm)", "Online / NetBanking", "Card / Cheque"]

# Helper Options
student_options = []
if not student_df.empty:
    student_options = [f"{row['Student ID']} - {row['Name']}" for _, row in student_df.iterrows()]

teacher_options = []
if not teachers_master_df.empty:
    teacher_options = [f"{row['Teacher ID']} - {row['Teacher Name']}" for _, row in teachers_master_df.iterrows()]

# Navigation Menu Options
st.sidebar.markdown("## 💻 STC Navigation Portal")
menu = st.sidebar.radio("Go to Section:", [
    "🔵 🏠 Home & Public Enquiry", 
    "🟢 📝 New Student Admission", 
    "🟣 🔑 Student Login Portal", 
    "🟠 🎯 Sunday Free Practice Class (SFPC)", 
    "🔴 👨‍🏫 Teacher Portal & Fee Counter", 
    "🔵 👨‍👩‍👧 Parents Live Student Tracker", 
    "🟤 🔐 Admin Control Panel"
])

# ==========================================
# 1. PUBLIC DASHBOARD & ENQUIRY
# ==========================================
if "🏠 Home & Public Enquiry" in menu:
    header_col1, header_col2 = st.columns([1, 4])
    with header_col1:
        if os.path.exists(LOGO_FILE):
            st.image(LOGO_FILE, width=130)
        else:
            st.title("💻 STC")
            
    with header_col2:
        st.markdown("<h1 style='color: #004085; margin-bottom: 0px;'>SOFT TECH COMPUTERS</h1>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: #28a745; margin-top: 0px;'>An ISO 9001:2015 Certified Computer Training Institute | Since 2020</h4>", unsafe_allow_html=True)
        st.write("📍 **Location:** Kamarchuburi, Thelamara, Sonitpur, Assam - 784149 (Associate Center Code: 4159)")

    st.markdown("---")

    # MULTI-WINNER 100% ATTENDANCE HIGHLIGHT WITH PHOTOS & MARQUEE
    st.markdown("### 🏆 Student of the Month & 100% Attendance Champions")
    
    top_winners = []
    max_count = 0

    if not attendance_df.empty:
        att_counts = attendance_df['Student ID'].value_counts()
        if not att_counts.empty:
            max_count = att_counts.max()
            top_ids = att_counts[att_counts == max_count].index.tolist()
            
            for tid in top_ids:
                matched = student_df[student_df['Student ID'] == tid]
                tname = matched.iloc[0]['Name'] if not matched.empty else tid
                top_winners.append({"id": tid, "name": tname})

    if top_winners:
        winner_names_str = ", ".join([f"{w['name']} ({w['id']})" for w in top_winners])
        
        photo_cols = st.columns(min(len(top_winners), 5))
        for idx, winner in enumerate(top_winners[:5]):
            wid = winner['id']
            wname = winner['name']
            p_path = os.path.join(PHOTOS_DIR, f"{wid}.jpg")
            
            with photo_cols[idx]:
                if os.path.exists(p_path):
                    st.image(p_path, caption=f"⭐ {wname}", width=110)
                else:
                    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", caption=f"⭐ {wname}", width=100)

        marquee_html = f'''
        <div style="background-color: #fff3cd; border: 2px solid #ffeba2; padding: 12px; border-radius: 10px; margin-top: 10px;">
            <marquee behavior="scroll" direction="left" scrollamount="7" style="font-size: 18px; font-weight: bold; color: #856404;">
                🌟 Congratulations to our 100% Attendance Champions ({max_count} Days Attended): <b>{winner_names_str}</b>! Keep up the brilliant dedication! 🌟
            </marquee>
        </div>
        '''
        st.markdown(marquee_html, unsafe_allow_html=True)
    else:
        st.info("🌟 **Student of the Month:** Will be announced based on monthly attendance performance!")

    st.markdown("---")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 🗓️ Active Class Time Table / Routine")
        st.table(routine_db)

        st.markdown("### 🪙 Courses & Course Packages")
        fees_list = [{"Course/Class": k, "Total Course Fee": f"₹ {v}/-"} for k, v in st.session_state.fee_settings.items()]
        st.table(pd.DataFrame(fees_list))

        st.markdown("### 🤖 Smart AI Course Recommendation Assistant")
        with st.expander("✨ Find the Best Course for You"):
            user_interest = st.selectbox("What is your primary goal?", ["Basic Computer Knowledge", "Office Work & Jobs", "Graphic Design & Publishing", "Accounting & Finance"])
            
            if user_interest == "Basic Computer Knowledge":
                st.write("👉 **Recommended:** **DCA (Diploma in Computer Applications)** — Fee: ₹5,500/-")
            elif user_interest == "Office Work & Jobs":
                st.write("👉 **Recommended:** **ADCA (Advance Diploma in Computer Applications)** — Fee: ₹8,598/-")
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
                    
                    new_enq = pd.DataFrame([[enq_name, enq_mobile, enq_course, get_ist_datetime_str()]], columns=enquiry_db.columns)
                    enquiry_db = pd.concat([enquiry_db, new_enq], ignore_index=True)
                    save_data(enquiry_db, ENQUIRY_FILE)

                    st.success(f"✅ **Enquiry Registered!** Total Course Fee for **{enq_course}** is **₹{selected_fee}/-**")

                    msg_text = f"Hello Soft Tech Computers!\nI submitted an enquiry:\nName: {enq_name}\nPhone: {enq_mobile}\nCourse: {enq_course}"
                    encoded_msg = urllib.parse.quote(msg_text)
                    whatsapp_number = "919854341170"
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
# 2. NEW STUDENT ADMISSION FORM ONLY
# ==========================================
elif "New Student Admission" in menu:
    st.title("📝 Student Record & Registration Form")
    st.markdown("<h4 style='color: #004085;'>SOFT TECH COMPUTERS, KAMARCHUBURI, THELAMARA</h4>", unsafe_allow_html=True)
    st.info("Fill out the formal student record form below to register new admission.")

    with st.form("admission_form"):
        st.markdown("#### 👤 Student Personal Details")
        c1, c2 = st.columns(2)
        s_name = c1.text_input("Student Name *")
        s_father = c2.text_input("Father Name *")
        s_mother = c1.text_input("Mother Name *")
        s_gender = c2.selectbox("Gender *", ["Male", "Female", "Other"])
        
        c3, c4 = st.columns(2)
        s_dob = c3.text_input("D.O.B (DD-MM-YYYY) *", value="01-01-2008")
        s_caste = c4.selectbox("Caste *", ["General", "OBC / MOBC", "SC", "ST", "Other"])
        s_mobile = c3.text_input("Contact No. (Mobile) *")
        s_photo = c4.file_uploader("Upload Student Photo (JPG/PNG)", type=['jpg', 'jpeg', 'png'])

        st.markdown("---")
        st.markdown("#### 🏡 Mandatory Address Breakup (Separate Cells)")
        a1, a2 = st.columns(2)
        s_vill = a1.text_input("Village / Town (Vill) *")
        s_po = a2.text_input("Post Office (P.O.) *")
        s_ps = a1.text_input("Police Station (P.S.) *")
        s_pin = a2.text_input("PIN Code *")
        s_dist = a1.text_input("District *", value="Sonitpur")

        st.markdown("---")
        st.markdown("#### 📚 Academic & Course Duration Details")
        ac1, ac2, ac3 = st.columns(3)
        s_course = ac1.selectbox("Course Selected *", list(st.session_state.fee_settings.keys()))
        s_duration = ac2.selectbox("Duration *", ["12 Months", "6 Months", "3 Months", "1 Month"])
        s_session = ac3.text_input("Session *", value="2026-2027")

        ac4, ac5 = st.columns(2)
        s_join_date = ac4.text_input("Join Date *", value=get_ist_date_str())
        s_valid_upto = ac5.text_input("Valid Up To *", value="30-10-2027")
        s_batch = st.selectbox("Batch Time Schedule *", BATCH_OPTIONS)
        s_mode = st.selectbox("Admission Mode *", ["Monthly Installments", "Full Onetime"])

        st.markdown("---")
        st.markdown("#### 💳 Initial Admission Fee & Receipt Details")
        fc1, fc2, fc3 = st.columns(3)
        s_exact_fee = fc1.number_input("Exact Course Fee (₹)", value=8598.0)
        s_discount = fc2.number_input("Discount (₹)", value=0.0)
        s_exam_fee = fc3.number_input("Exam Fee (₹)", value=999.0)

        fc4, fc5, fc6 = st.columns(3)
        s_initial_pay = fc4.number_input("Initial Admission Fee Paid (₹) *", min_value=0.0, value=999.0)
        s_pay_mode = fc5.selectbox("Payment Mode *", PAYMENT_MODES)
        s_receipt_no = fc6.text_input("Manual Fee Receipt No. *", value="001")

        if st.form_submit_button("🎓 Confirm & Save Student Record"):
            existing_mobiles = student_df['Mobile No'].astype(str).tolist() if not student_df.empty else []
            
            if str(s_mobile).strip() in existing_mobiles:
                st.error("❌ **Duplicate Mobile Blocked:** This Contact Number is already registered for another student!")
            elif s_name and s_mobile and s_vill and s_po and s_ps and s_pin and s_dist and s_receipt_no:
                new_id = f"STC26-00{len(student_df)+1}"
                today_date_str = get_ist_date_str()
                full_addr_str = f"Vill- {s_vill}, P.O.- {s_po}, P.S.- {s_ps}, PIN- {s_pin}, Dist- {s_dist}"
                
                # Save Photo
                if s_photo is not None:
                    photo_save_path = os.path.join(PHOTOS_DIR, f"{new_id}.jpg")
                    with open(photo_save_path, "wb") as f:
                        f.write(s_photo.getbuffer())

                breakdown = f"1st Installment [Admission Fee]: ₹{int(s_initial_pay)} ({s_pay_mode}) [Receipt No: {s_receipt_no}] on {today_date_str}"
                
                new_row = pd.DataFrame([[
                    new_id, s_name, s_father, s_mother, s_gender, s_dob, s_caste, str(s_mobile),
                    s_vill, s_po, s_ps, str(s_pin), s_dist, full_addr_str, s_course, s_duration, s_session, s_join_date, s_valid_upto, s_batch,
                    s_mode, s_exact_fee, s_discount, s_exam_fee, s_initial_pay, breakdown, today_date_str,
                    "Pending", "Pending", "Pending", "No", "Pending", "Pending", "N/A", "N/A"
                ]], columns=student_df.columns)
                
                student_df = pd.concat([student_df, new_row], ignore_index=True)
                save_data(student_df, STUDENT_MASTER_FILE)

                # Set Default Student Password as Mobile Number
                pass_row = pd.DataFrame([[new_id, str(s_mobile)]], columns=st_pass_df.columns)
                st_pass_df = pd.concat([st_pass_df, pass_row], ignore_index=True)
                save_data(st_pass_df, STUDENT_PASSWORDS_FILE)

                # Log Payment
                new_log = pd.DataFrame([[today_date_str, "Self / Desk", new_id, s_name, s_initial_pay, s_pay_mode, s_receipt_no]], columns=fee_log_df.columns)
                fee_log_df = pd.concat([fee_log_df, new_log], ignore_index=True)
                save_data(fee_log_df, FEE_COLLECTION_LOG_FILE)

                st.success(f"🎉 **Student Record Saved Successfully!** Generated Roll No: **{new_id}**")
                st.info(f"🔑 **Default Student Login Password:** `{s_mobile}`")
            else:
                st.error("⚠️ Please fill in all mandatory fields (including separate Address fields)!")

# ==========================================
# 3. STUDENT LOGIN PORTAL (PRIVACY SECURED)
# ==========================================
elif "Student Login Portal" in menu:
    st.title("🔑 Student Self-Service Login Portal")
    
    if 'student_logged_in' not in st.session_state:
        st.session_state.student_logged_in = False
        st.session_state.logged_student_id = ""

    if not st.session_state.student_logged_in:
        st.subheader("Login to Access Your Record Form & Fee Dues")
        st.info("💡 **Username:** Your Roll Number (e.g. STC26-001) | **Password:** Your Registered Mobile No.")

        with st.form("student_login_form"):
            login_user = st.text_input("Roll Number / Student ID")
            login_pass = st.text_input("Password", type="password")
            
            if st.form_submit_button("🔑 Login Now"):
                matched_pass = st_pass_df[st_pass_df['Student ID'].astype(str).str.upper() == login_user.strip().upper()]
                
                if not matched_pass.empty:
                    correct_pass = str(matched_pass.iloc[0]['Password'])
                    if login_pass.strip() == correct_pass:
                        st.session_state.student_logged_in = True
                        st.session_state.logged_student_id = login_user.strip().upper()
                        st.success("✅ Login Successful!")
                        st.rerun()
                    else:
                        st.error("❌ Incorrect Password!")
                else:
                    st.error("❌ Invalid Roll Number / Student ID!")
    else:
        st_id = st.session_state.logged_student_id
        matched_st = student_df[student_df['Student ID'] == st_id]

        if not matched_st.empty:
            s_info = matched_st.iloc[0]
            
            st.sidebar.success(f"👤 Logged in as: {s_info['Name']}")
            if st.sidebar.button("🚪 Logout"):
                st.session_state.student_logged_in = False
                st.session_state.logged_student_id = ""
                st.rerun()

            st.title(f"Welcome, {s_info['Name']}! 👋")
            
            stab1, stab2, stab3, stab4 = st.tabs(["🆔 Digital ID Card (QR)", "💳 Fee Installment Record Form", "⏱️ Attendance & Progress", "🎟️ Exam, Admit Card & Result"])

            with stab1:
                st.markdown("### 🆔 SOFT TECH COMPUTERS - DIGITAL STUDENT ID CARD")
                
                id_col1, id_col2 = st.columns([1, 2])
                p_path = os.path.join(PHOTOS_DIR, f"{st_id}.jpg")
                
                with id_col1:
                    if os.path.exists(p_path):
                        st.image(p_path, width=160, caption=f"Roll No: {st_id}")
                    else:
                        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=140, caption="Student Avatar")
                    
                    # Generate Digital QR Code for ID
                    qr_code_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={st_id}"
                    st.image(qr_code_url, caption="Digital Attendance QR", width=120)

                with id_col2:
                    st.markdown(f"#### **SOFT TECH COMPUTERS, KAMARCHUBURI, THELAMARA**")
                    st.markdown(f"**Roll No:** `{st_id}`")
                    st.write(f"**Student Name:** {s_info['Name']}")
                    st.write(f"**Father Name:** {s_info['Father Name']} | **Mother Name:** {s_info['Mother Name']}")
                    st.write(f"**Gender:** {s_info['Gender']} | **D.O.B:** {s_info['DOB']} | **Caste:** {s_info['Caste']}")
                    st.write(f"**Course:** {s_info['Course']} | **Duration:** {s_info['Duration']} | **Session:** {s_info['Session']}")
                    st.write(f"**Batch Time Schedule:** {s_info['Batch Time']}")
                    st.write(f"**Address:** {s_info['Full Address']}")

            with stab2:
                st.subheader("💳 Student Record Form - Fee Installment Details")
                
                tot = float(s_info['Total Fee']) if pd.notnull(s_info['Total Fee']) else 8598.0
                paid = float(s_info['Paid']) if pd.notnull(s_info['Paid']) else 0.0
                due = tot - paid
                discount = float(s_info['Discount']) if pd.notnull(s_info['Discount']) else 0.0
                exam_fee = float(s_info['Exam Fee']) if pd.notnull(s_info['Exam Fee']) else 999.0

                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Course Fee", f"₹{tot}/-")
                c2.metric("Discount", f"₹{discount}/-")
                c3.metric("Exam Fee", f"₹{exam_fee}/-")
                c4.metric("Total Paid Till Now", f"₹{paid}/-", delta=f"Pending Due: ₹{due}/-")

                st.markdown("---")
                st.markdown("### 📋 Paid Installments Ledger & Receipt History")
                breakdown_text = str(s_info['Payment Breakdown'])
                st.info(f"`{breakdown_text}`")

            with stab3:
                st.subheader("⏱️ Daily Attendance & Course Progress")
                st_att_count = len(attendance_df[attendance_df['Student ID'] == st_id]) if not attendance_df.empty else 0
                total_classes = 20  
                att_pct = round((st_att_count / total_classes) * 100, 1) if total_classes > 0 else 0
                
                st.write(f"**Total Attended Days:** {st_att_count} Days (**{att_pct}%**)")
                st.progress(min(att_pct / 100.0, 1.0))

            with stab4:
                st.subheader("🎟️ Final Examination Lifecycle Tracker")
                
                tot = float(s_info['Total Fee']) if pd.notnull(s_info['Total Fee']) else 8598.0
                paid = float(s_info['Paid']) if pd.notnull(s_info['Paid']) else 0.0
                due = tot - paid

                e_col1, e_col2 = st.columns(2)
                
                with e_col1:
                    st.markdown("#### 🟢 Exam Eligibility Check")
                    if due <= 1500 and att_pct >= 75:
                        st.success("🎉 **STATUS: ELIGIBLE FOR FINAL EXAMINATION!** (Pending balance is within ₹1500 limit)")
                    else:
                        st.error("🔴 **STATUS: EXAM FORM FILL-UP BLOCKED**")
                        if due > 1500:
                            st.warning(f"⚠️ Pending balance is ₹{due}/- (Must be ₹1500 or less to give exam).")
                        if att_pct < 75:
                            st.warning(f"⚠️ Attendance is {att_pct}% (Must be 75% or higher).")

                with e_col2:
                    st.markdown("#### 📑 Official Examination & Result Details")
                    st.write(f"* **SARVA Final Registration Status:** `{s_info['Exam Reg Status']}`")
                    st.write(f"* **Exam Form Fill-up Status:** `{s_info['Form Fillup Status']}`")
                    st.write(f"* **Admit Card Status:** `{s_info['Admit Card Status']}`")
                    st.write(f"* **Exam Date:** `{s_info['Exam Date']}`")
                    st.write(f"* **Final Result / Grade:** `{s_info['Result Grade']}`")
                    st.write(f"* **Official Cert Issue Date:** `{s_info['Cert Issue Date']}`")
                    st.write(f"* **Certificate Number:** `{s_info['Cert No']}`")
                    st.write(f"* **Marksheet Number:** `{s_info['Marksheet No']}`")

# ==========================================
# 4. SUNDAY FREE PRACTICE CLASS (SFPC)
# ==========================================
elif "Sunday Free Practice Class" in menu:
    st.title("🎯 Sunday Free Practice Class (SFPC) Portal")
    st.info("💡 **SFPC Eligibility Rule:** Attendance ≥ 75% AND Paid Admission Fee (₹999) + minimum 50% of monthly fee dues till date.")

    sfpc_query = st.text_input("Enter Roll Number (Student ID) or Mobile Number")
    if sfpc_query:
        matched = student_df[(student_df['Student ID'].astype(str).str.contains(sfpc_query, case=False, na=False)) | 
                             (student_df['Mobile No'].astype(str).str.contains(sfpc_query, case=False, na=False))]
        
        if not matched.empty:
            s_info = matched.iloc[0]
            st_id = s_info['Student ID']
            
            st_att_count = len(attendance_df[attendance_df['Student ID'] == st_id]) if not attendance_df.empty else 0
            att_pct = round((st_att_count / 20.0) * 100, 1)
            
            try:
                adm_date_str = str(s_info['Admission Date']) if pd.notnull(s_info['Admission Date']) and str(s_info['Admission Date']) != "" else get_ist_date_str()
                adm_dt = datetime.strptime(adm_date_str, "%Y-%m-%d")
            except:
                adm_dt = datetime.now()

            today_dt = datetime.now()
            days_passed = (today_dt - adm_dt).days
            months_enrolled = max(1, round(days_passed / 30.0, 1))

            tot = float(s_info['Total Fee']) if pd.notnull(s_info['Total Fee']) else 8598.0
            paid = float(s_info['Paid']) if pd.notnull(s_info['Paid']) else 0.0

            monthly_rate = 550.0
            total_monthly_due_till_now = months_enrolled * monthly_rate
            required_50_pct_monthly = total_monthly_due_till_now * 0.5
            
            min_required_fee_total = 999.0 + required_50_pct_monthly
            fee_cleared = (paid >= min_required_fee_total) or (paid >= tot)

            st.markdown(f"### 👤 Student Profile: **{s_info['Name']}** ({st_id})")
            st.write(f"* **Attendance Status:** {st_att_count} Days attended (**{att_pct}%**) [Min Required: 75%]")
            st.write(f"* **Enrolled Duration:** {months_enrolled} Month(s) | **Total Paid:** ₹{paid}/-")
            st.write(f"* **Required Minimum Fee for SFPC:** ₹{int(min_required_fee_total)}/- (Admission ₹999 + 50% Monthly Dues)")

            st.markdown("---")
            if att_pct >= 75 and fee_cleared:
                st.success("🎉 **STATUS: ELIGIBLE FOR SUNDAY FREE PRACTICE CLASS (SFPC)!**")
            else:
                st.error("⚠️ **STATUS: NOT ELIGIBLE FOR SFPC THIS SUNDAY.**")
                if att_pct < 75:
                    st.warning(f"❌ Attendance Low: Currently {att_pct}%. Minimum 75% required.")
                if not fee_cleared:
                    st.warning(f"❌ Fee Dues Shortage: Paid ₹{paid}/-. Must pay at least ₹{int(min_required_fee_total)}/- to qualify for SFPC.")
        else:
            st.error("No Student found with this Roll Number or Mobile Number!")

# ==========================================
# 5. TEACHER PORTAL & FEE COUNTER
# ==========================================
elif "Teacher Portal" in menu:
    st.title("👨‍🏫 Teacher & Staff Desk")
    
    current_teacher_pin = get_teacher_pin()
    t_pin_input = st.text_input("Enter Teacher Passcode / PIN", type="password")

    if t_pin_input == current_teacher_pin:
        st.success("Access Granted to Staff Desk.")
        ttab1, ttab2 = st.tabs(["⏱️ Teacher Shift & Class Topics Log", "💵 Collect Fee & Issue Receipt"])

        with ttab1:
            st.subheader("Teacher Class Logging")
            with st.form("teacher_log_form"):
                t_selected_teacher = st.selectbox("Select Teacher Name", teacher_options if teacher_options else ["TC-01 - Zaan Hazarika"])
                t_shift = st.selectbox("Shift", ["Morning Shift", "Afternoon Shift", "Evening Shift"])
                t_in = st.time_input("In-Time", get_ist_now().time())
                t_out = st.time_input("Out-Time", get_ist_now().time())
                
                t_class_type = st.radio("Class Type", ["Theory", "Practical", "Both Theory & Practical"])
                t_selected_topics = st.multiselect("Select Topics Taught Today", AVAILABLE_TOPICS)
                t_status = st.selectbox("Status", ["Present", "Leave / Absent"])

                if st.form_submit_button("Submit Class Log"):
                    t_teacher_name = t_selected_teacher.split(" - ")[1] if " - " in t_selected_teacher else t_selected_teacher
                    today_str = get_ist_date_str()
                    t_in_str = t_in.strftime("%I:%M %p")
                    t_out_str = t_out.strftime("%I:%M %p")
                    topics_str = ", ".join(t_selected_topics) if t_selected_topics else "General"
                    
                    shift_wage = round(230.0 / 3.0, 2) if t_status == "Present" else 0.0

                    new_t_log = pd.DataFrame([[today_str, t_teacher_name, t_shift, t_in_str, t_out_str, t_class_type, topics_str, t_status, shift_wage]], columns=teacher_db.columns)
                    teacher_db = pd.concat([teacher_db, new_t_log], ignore_index=True)
                    save_data(teacher_db, TEACHER_LOG_FILE)
                    st.success("✅ **Class log recorded successfully! Saved to Salary Log.**")

        with ttab2:
            st.subheader("💵 Deposit Student Fee (Manual Receipt Sync)")
            
            if not student_df.empty:
                t_collector = st.selectbox("Collector / Teacher", teacher_options if teacher_options else ["TC-01 - Zaan Hazarika"])
                t_selected_opt = st.selectbox("Select Student", student_options)
                
                col_m1, col_m2, col_m3 = st.columns(3)
                t_add_amt = col_m1.number_input("Amount Collected (₹)", min_value=100.0, step=100.0)
                t_fee_pmode = col_m2.selectbox("Payment Mode", PAYMENT_MODES)
                t_manual_rec_no = col_m3.text_input("Manual Fee Receipt No. *", value="002")

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

                    today_date_str = get_ist_date_str()
                    old_bd = str(student_df.at[idx, 'Payment Breakdown']) if pd.notnull(student_df.at[idx, 'Payment Breakdown']) else ""
                    new_bd = f"{old_bd} | Installment: ₹{int(t_add_amt)} ({t_fee_pmode}) [Receipt No: {t_manual_rec_no}] on {today_date_str}"
                    student_df.at[idx, 'Payment Breakdown'] = new_bd

                    save_data(student_df, STUDENT_MASTER_FILE)

                    new_fee_entry = pd.DataFrame([[today_date_str, teacher_name_input, t_f_sid, st_name_val, t_add_amt, t_fee_pmode, t_manual_rec_no]], columns=fee_log_df.columns)
                    fee_log_df = pd.concat([fee_log_df, new_fee_entry], ignore_index=True)
                    save_data(fee_log_df, FEE_COLLECTION_LOG_FILE)

                    st.success(f"✅ **Fee Entry Saved!** Linked Manual Receipt No: **{t_manual_rec_no}**")
                    st.rerun()

# ==========================================
# 6. PARENTS LIVE TRACKER
# ==========================================
elif "Parents Live Student Tracker" in menu:
    st.title("👨‍👩‍👧 Parents Live Student Progress Tracker")
    st.info("Parents can monitor their child's attendance and course progress by entering their mobile number.")

    p_mobile = st.text_input("Enter Student Registered Mobile Number")
    if p_mobile:
        matched = student_df[student_df['Mobile No'].astype(str).str.contains(p_mobile, case=False, na=False)]
        
        if not matched.empty:
            s_info = matched.iloc[0]
            st_id = s_info['Student ID']
            
            st.markdown(f"### 👤 Student Name: **{s_info['Name']}** ({st_id})")
            st.write(f"**Course:** {s_info['Course']} | **Batch:** {s_info['Batch Time']}")
            
            st_att_count = len(attendance_df[attendance_df['Student ID'] == st_id]) if not attendance_df.empty else 0
            st.success(f"📊 **Attendance Progress:** Attended {st_att_count} days.")
        else:
            st.error("No student record found with this mobile number!")

# ==========================================
# 7. ADMIN CONTROL PANEL
# ==========================================
elif "Admin Control Panel" in menu:
    st.title("🔐 Director / Admin Control Panel")
    
    current_admin_pass = get_admin_password()
    pwd = st.text_input("Enter Director Admin Password", type="password")

    if pwd == current_admin_pass:
        st.success("Access Granted. Welcome Sir!")

        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Student Registry & Exam Manager", 
            "🔑 Student Login Credentials Ledger",
            "🧾 Fee Audit Log", 
            "👨‍🏫 Teacher Salary Logs", 
            "🔑 Security Settings"
        ])

        with tab1:
            st.markdown("### Master Student Records & Exam Lifecycle Manager")
            st.dataframe(student_df, use_container_width=True)

            st.markdown("---")
            st.markdown("### ✏️ Edit Student Exam Status & Result")
            if not student_df.empty:
                edit_selected_st = st.selectbox("Select Student to Update", student_options, key="adm_edit_st")
                edit_sid = edit_selected_st.split(" - ")[0]
                e_row = student_df[student_df['Student ID'] == edit_sid].iloc[0]

                with st.form("admin_edit_exam_form"):
                    col_x1, col_x2, col_x3 = st.columns(3)
                    e_reg = col_x1.selectbox("Registration Done?", ["Yes", "No"], index=0 if e_row['Exam Reg Status']=="Yes" else 1)
                    e_form = col_x2.selectbox("Form Fillup Status", ["Submitted", "Pending"], index=0 if e_row['Form Fillup Status']=="Submitted" else 1)
                    e_admit = col_x3.selectbox("Admit Card Status", ["Issued", "Pending"], index=0 if e_row['Admit Card Status']=="Issued" else 1)

                    col_y1, col_y2, col_y3 = st.columns(3)
                    e_ex_date = col_y1.text_input("Exam Date", value=str(e_row['Exam Date']))
                    e_grade = col_y2.text_input("Result / Grade", value=str(e_row['Result Grade']))
                    e_cert_date = col_y3.text_input("Cert Issue Date", value=str(e_row['Cert Issue Date']))

                    col_z1, col_z2 = st.columns(2)
                    e_cert_no = col_z1.text_input("Certificate No", value=str(e_row['Cert No']))
                    e_marksheet_no = col_z2.text_input("Marksheet No", value=str(e_row['Marksheet No']))

                    if st.form_submit_button("Update Exam Record"):
                        e_idx = student_df[student_df['Student ID'] == edit_sid].index[0]
                        student_df.loc[e_idx, 'Exam Reg Status'] = e_reg
                        student_df.loc[e_idx, 'Form Fillup Status'] = e_form
                        student_df.loc[e_idx, 'Admit Card Status'] = e_admit
                        student_df.loc[e_idx, 'Exam Date'] = e_ex_date
                        student_df.loc[e_idx, 'Result Grade'] = e_grade
                        student_df.loc[e_idx, 'Cert Issue Date'] = e_cert_date
                        student_df.loc[e_idx, 'Cert No'] = e_cert_no
                        student_df.loc[e_idx, 'Marksheet No'] = e_marksheet_no

                        save_data(student_df, STUDENT_MASTER_FILE)
                        st.success("✅ Exam record updated successfully!")
                        st.rerun()

        with tab2:
            st.markdown("### 🔑 Student Login Credentials Ledger (View & Reset Passwords)")
            st.dataframe(st_pass_df, use_container_width=True)

        with tab3:
            st.markdown("### 🧾 Fee Audit Log with Manual Receipt Numbers")
            st.dataframe(fee_log_df, use_container_width=True)

        with tab4:
            st.markdown("### 👨‍🏫 Teacher Shift Salary Logs")
            if not teacher_db.empty:
                t_wages_df = teacher_db.copy()
                t_wages_df['Shift Wage (₹)'] = pd.to_numeric(t_wages_df['Shift Wage (₹)'], errors='coerce').fillna(0.0)
                tot_salary = round(t_wages_df['Shift Wage (₹)'].sum(), 2)
                st.metric("Total Teacher Accumulated Wages", f"₹{tot_salary}/-")
                st.dataframe(t_wages_df, use_container_width=True)
            else:
                st.info("No Teacher Salary Logs found yet.")

        with tab5:
            st.markdown("### 🔑 Admin & Teacher Passcode Settings")
            curr_pin_val = get_teacher_pin()
            st.success(f"📌 Current Live Teacher PIN: `{curr_pin_val}`")