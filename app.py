import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime, timedelta
import urllib.parse
import os
import pytz
import re

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

# Display DataFrame with Sl No. starting from 1
def get_display_df(df):
    if df.empty:
        return df
    disp_df = df.copy()
    disp_df.index = range(1, len(disp_df) + 1)
    disp_df.index.name = "Sl. No."
    return disp_df

# Smart Roll Number Auto-Generator
def generate_next_student_id(df):
    if df.empty or 'Student ID' not in df.columns:
        return "STC26-001"
    
    existing_ids = df['Student ID'].astype(str).tolist()
    numeric_parts = []
    
    for sid in existing_ids:
        numbers = re.findall(r'\d+', sid)
        if len(numbers) >= 2:
            try:
                numeric_parts.append(int(numbers[1]))
            except:
                pass
        elif len(numbers) == 1:
            try:
                numeric_parts.append(int(numbers[0]))
            except:
                pass
                
    if numeric_parts:
        next_num = max(numeric_parts) + 1
    else:
        next_num = len(df) + 1
        
    return f"STC26-{next_num:03d}"

# Exact Calendar Month Course End Date Calculator
def calculate_course_end_date(start_date_str, duration_str):
    try:
        dt = datetime.strptime(str(start_date_str).strip(), "%Y-%m-%d")
    except:
        dt = get_ist_now()
    
    d_str = str(duration_str).lower().strip()
    
    if "12" in d_str or "year" in d_str:
        try:
            end_dt = dt.replace(year=dt.year + 1) - timedelta(days=1)
        except ValueError:
            end_dt = dt + timedelta(days=365)
    elif "6" in d_str:
        month = dt.month - 1 + 6
        year = dt.year + month // 12
        month = month % 12 + 1
        day = min(dt.day, [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month-1])
        end_dt = datetime(year, month, day) - timedelta(days=1)
    elif "3" in d_str:
        month = dt.month - 1 + 3
        year = dt.year + month // 12
        month = month % 12 + 1
        day = min(dt.day, [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month-1])
        end_dt = datetime(year, month, day) - timedelta(days=1)
    elif "2" in d_str:
        month = dt.month - 1 + 2
        year = dt.year + month // 12
        month = month % 12 + 1
        day = min(dt.day, [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month-1])
        end_dt = datetime(year, month, day) - timedelta(days=1)
    elif "1" in d_str or "month" in d_str:
        month = dt.month - 1 + 1
        year = dt.year + month // 12
        month = month % 12 + 1
        day = min(dt.day, [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month-1])
        end_dt = datetime(year, month, day) - timedelta(days=1)
    elif "45" in d_str:
        end_dt = dt + timedelta(days=44)
    else:
        end_dt = dt + timedelta(days=179)
        
    return end_dt.strftime("%Y-%m-%d")

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
STUDENT_PASSWORDS_FILE = "student_passwords.csv"
LOGO_FILE = "logo.jpg"
PHOTOS_DIR = "student_photos"

# Safe Photo Directory Creation
os.makedirs(PHOTOS_DIR, exist_ok=True)

# Master Column Definitions
student_cols = [
    'Student ID', 'Name', 'Father Name', 'Mother Name', 'Gender', 'DOB', 'Caste', 'Mobile No', 
    'Vill Town', 'PO', 'PS', 'PIN Code', 'District', 'Full Address', 'Course', 'Duration', 'Session', 
    'Join Date', 'Valid Up To', 'Batch Time', 'Admission Mode', 'Total Fee', 'Discount', 'Exam Fee', 
    'Paid', 'Payment Breakdown', 'Admission Date', 'Exam Date', 'Result Grade', 'Cert Issue Date', 
    'Exam Reg Status', 'Form Fillup Status', 'Admit Card Status', 'Cert No', 'Marksheet No', 'Student Status'
]
attendance_cols = ['Date', 'Student ID', 'Name', 'Action', 'Time']
fee_collect_cols = ['Date', 'Collected By', 'Student ID', 'Student Name', 'Amount (₹)', 'Payment Mode', 'Fee Receipt No']
teacher_cols = ['Date', 'Teacher Name', 'Shift', 'In-Time', 'Out-Time', 'Class Type', 'Topics Taught', 'Status', 'Status Info', 'Late Reason', 'Shift Wage (₹)']
teacher_master_cols = ['Teacher ID', 'Teacher Name', 'Mobile No', 'Designation']

# Safe Data Loader
def load_clean_data(file_path, default_cols, is_student_file=False):
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path, dtype=str)
            if df.empty:
                return pd.DataFrame(columns=default_cols)
            
            if is_student_file and 'Student ID' in df.columns:
                df = df.drop_duplicates(subset=['Student ID'], keep='first')
            
            for col in default_cols:
                if col not in df.columns:
                    if col == 'Total Fee':
                        df[col] = "8598.0"
                    elif col == 'Discount':
                        df[col] = "0.0"
                    elif col == 'Exam Fee':
                        df[col] = "999.0"
                    elif col == 'Paid':
                        df[col] = "0.0"
                    elif col == 'Payment Breakdown':
                        df[col] = "0"
                    elif col == 'Admission Date':
                        df[col] = get_ist_date_str()
                    elif col == 'Student Status':
                        df[col] = "Active"
                    else:
                        df[col] = ""
            return df[default_cols]
        except:
            return pd.DataFrame(columns=default_cols)
    return pd.DataFrame(columns=default_cols)

def save_data(df, file_path):
    df.astype(str).to_csv(file_path, index=False)

# Passcode & Security Logic
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

# Load Master Databases
student_df = load_clean_data(STUDENT_MASTER_FILE, student_cols, is_student_file=True)
attendance_df = load_clean_data(ATTENDANCE_LOG_FILE, attendance_cols)
fee_log_df = load_clean_data(FEE_COLLECTION_LOG_FILE, fee_collect_cols)
enquiry_db = load_clean_data(ENQUIRY_FILE, ['Name', 'Mobile', 'Course Selected', 'Timestamp'])
teacher_db = load_clean_data(TEACHER_LOG_FILE, teacher_cols)
teachers_master_df = load_clean_data(TEACHERS_MASTER_FILE, teacher_master_cols)
routine_db = load_clean_data(ROUTINE_FILE, ['Shift', 'Timing', 'Days', 'Assigned Class'])

# Student Passwords DB
st_pass_cols = ['Student ID', 'Password']
st_pass_df = load_clean_data(STUDENT_PASSWORDS_FILE, st_pass_cols)

# Ensure All Students Have Credentials Initialized
if not student_df.empty:
    updated_passwords = False
    for _, srow in student_df.iterrows():
        sid = str(srow['Student ID']).strip()
        smob = str(srow['Mobile No']).strip()
        if sid and sid not in st_pass_df['Student ID'].astype(str).values:
            new_pass_entry = pd.DataFrame([[sid, smob]], columns=st_pass_df.columns)
            st_pass_df = pd.concat([st_pass_df, new_pass_entry], ignore_index=True)
            updated_passwords = True
    if updated_passwords:
        save_data(st_pass_df, STUDENT_PASSWORDS_FILE)

# Default Teachers Initialization
if teachers_master_df.empty:
    teachers_master_df = pd.DataFrame([
        {"Teacher ID": "TC-01", "Teacher Name": "Chiranjeeb Hazarika", "Mobile No": "9854341170", "Designation": "Director / Instructor"},
        {"Teacher ID": "TC-02", "Teacher Name": "BIJOY KURMI", "Mobile No": "9854865864", "Designation": "Faculty"}
    ])
    save_data(teachers_master_df, TEACHERS_MASTER_FILE)

# Fixed Routine
if routine_db.empty:
    routine_db = pd.DataFrame([
        {"Shift": "Morning Shift", "Timing": "07:30 AM - 09:00 AM", "Days": "MWF / TTS Slots", "Assigned Class": "Computer ADCA/DCA"},
        {"Shift": "Afternoon Shift", "Timing": "04:00 PM - 05:30 PM", "Days": "MWF / TTS Slots", "Assigned Class": "Computer Batch A"},
        {"Shift": "Evening Shift", "Timing": "05:30 PM - 07:00 PM", "Days": "MWF / TTS Slots", "Assigned Class": "Computer Batch B"}
    ])

# Session States (Added New Certificate Courses)
if 'fee_settings' not in st.session_state:
    st.session_state.fee_settings = {
        "ADCA": 8598, "DCA": 5500, "DTP": 4000, "Tally": 4500,
        "Certificate (3 Months)": 2500, "Certificate (2 Months)": 1500, "Certificate (45 Days)": 1000
    }

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

SHIFT_TIMINGS = {
    "Morning Shift": "07:30",
    "Afternoon Shift": "16:00",
    "Evening Shift": "17:30"
}

student_options = [f"{row['Student ID']} - {row['Name']}" for _, row in student_df.iterrows()] if not student_df.empty else []
teacher_options = [f"{row['Teacher ID']} - {row['Teacher Name']}" for _, row in teachers_master_df.iterrows()] if not teachers_master_df.empty else []

# Fast Navigation Menu
st.sidebar.title("💻 STC Portal")
menu = st.sidebar.radio("Navigation Menu:", [
    "🏠 Home & Public Enquiry", 
    "📝 New Student Admission", 
    "🔑 Student Login Portal", 
    "🎯 Sunday Free Practice Class (SFPC)", 
    "👨‍🏫 Teacher Portal & Fee Counter", 
    "👨‍👩‍👧 Parents Live Student Tracker", 
    "🔐 Admin Control Panel"
])

# ==========================================
# 1. PUBLIC DASHBOARD & ENQUIRY
# ==========================================
if menu == "🏠 Home & Public Enquiry":
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

    # Marquee (Moving) Student of the Month
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
        winner_items_html = ""
        for winner in top_winners:
            wid = winner['id']
            wname = winner['name']
            p_path = os.path.join(PHOTOS_DIR, f"{wid}.jpg")
            img_src = f"app/static/{wid}.jpg" if os.path.exists(p_path) else "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
            
            winner_items_html += f'<div style="display: inline-block; text-align: center; margin-right: 40px; background: #ffffff; padding: 10px; border-radius: 12px; border: 2px solid #ffc107; box-shadow: 2px 2px 8px rgba(0,0,0,0.1);"><img src="{img_src}" style="width: 80px; height: 80px; border-radius: 50%; object-fit: cover; border: 2px solid #004085;"><br><span style="font-size: 15px; font-weight: bold; color: #004085;">⭐ {wname}</span><br><span style="font-size: 12px; color: #28a745; font-weight: bold;">{wid} ({max_count} Days Attended)</span></div>'

        full_marquee_html = f'''
        <div style="background-color: #fff8e1; border: 2px solid #ffe082; padding: 15px; border-radius: 12px; margin-top: 10px; overflow: hidden;">
            <marquee behavior="scroll" direction="left" scrollamount="8" onmouseover="this.stop();" onmouseout="this.start();">
                <div style="display: flex; align-items: center;">
                    <span style="font-size: 20px; font-weight: bold; color: #d32f2f; margin-right: 30px;">🏆 STUDENT OF THE MONTH CHAMPIONS 🏆</span>
                    {winner_items_html}
                </div>
            </marquee>
        </div>'''
        st.markdown(full_marquee_html, unsafe_allow_html=True)
    else:
        st.info("🌟 **Student of the Month:** Will be announced based on monthly attendance performance!")

    st.markdown("---")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 🗓️ Active Class Time Table / Routine")
        st.table(get_display_df(routine_db))

        st.markdown("### 🪙 Courses & Course Packages")
        fees_list = [{"Course/Class": k, "Total Course Fee": f"₹ {v}/-"} for k, v in st.session_state.fee_settings.items()]
        st.table(get_display_df(pd.DataFrame(fees_list)))

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

                    st.markdown(f'''<a href="{whatsapp_url}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:10px 20px; border-radius:8px; font-weight:bold; font-size:15px; cursor:pointer; width:100%; margin-top:10px;">📲 Send Details directly on WhatsApp</button></a>''', unsafe_allow_html=True)
                else:
                    st.error("⚠️ Please fill in both Name and Mobile Number to view fee!")

# ==========================================
# 2. NEW STUDENT ADMISSION FORM
# ==========================================
elif menu == "📝 New Student Admission":
    st.title("📝 Student Record & Registration Form")
    st.markdown("<h4 style='color: #004085;'>SOFT TECH COMPUTERS, KAMARCHUBURI, THELAMARA</h4>", unsafe_allow_html=True)
    
    st.warning("🔒 **Secure Section: Staff / Admin Access Only**")
    auth_pin = st.text_input("Enter Passcode (Teacher PIN or Admin Password) to unlock form", type="password")
    
    if auth_pin == get_teacher_pin() or auth_pin == get_admin_password():
        st.success("✅ Access Granted! Fill out the formal record form below.")
        
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
            s_duration = ac2.selectbox("Duration *", ["12 Months", "6 Months", "3 Months", "2 Months", "1 Month", "45 Days"])
            s_session = ac3.text_input("Session *", value="2026-2027")

            ac4, ac5 = st.columns(2)
            s_join_date = ac4.text_input("Join Date (YYYY-MM-DD) *", value=get_ist_date_str())
            
            auto_calculated_valid_date = calculate_course_end_date(s_join_date, s_duration)
            s_valid_upto = ac5.text_input("Valid Up To (Exact 1-Year/Duration Match) *", value=auto_calculated_valid_date)
            
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
                    new_id = generate_next_student_id(student_df)
                    today_date_str = get_ist_date_str()
                    full_addr_str = f"Vill- {s_vill}, P.O.- {s_po}, P.S.- {s_ps}, PIN- {s_pin}, Dist- {s_dist}"
                    
                    if s_photo is not None:
                        photo_save_path = os.path.join(PHOTOS_DIR, f"{new_id}.jpg")
                        with open(photo_save_path, "wb") as f:
                            f.write(s_photo.getbuffer())

                    breakdown = f"1st Installment [Admission Fee]: ₹{int(s_initial_pay)} ({s_pay_mode}) [Receipt No: {s_receipt_no}] on {today_date_str}"
                    
                    new_row = pd.DataFrame([[
                        str(new_id), str(s_name), str(s_father), str(s_mother), str(s_gender), str(s_dob), str(s_caste), str(s_mobile),
                        str(s_vill), str(s_po), str(s_ps), str(s_pin), str(s_dist), str(full_addr_str), str(s_course), str(s_duration), str(s_session), str(s_join_date), str(s_valid_upto), str(s_batch),
                        str(s_mode), str(s_exact_fee), str(s_discount), str(s_exam_fee), str(s_initial_pay), str(breakdown), str(today_date_str),
                        "Pending", "Pending", "Pending", "No", "Pending", "Pending", "N/A", "N/A", "Active"
                    ]], columns=student_df.columns)
                    
                    student_df = pd.concat([student_df, new_row], ignore_index=True)
                    save_data(student_df, STUDENT_MASTER_FILE)

                    pass_row = pd.DataFrame([[str(new_id), str(s_mobile)]], columns=st_pass_df.columns)
                    st_pass_df = pd.concat([st_pass_df, pass_row], ignore_index=True)
                    save_data(st_pass_df, STUDENT_PASSWORDS_FILE)

                    new_log = pd.DataFrame([[str(today_date_str), "Self / Desk", str(new_id), str(s_name), str(s_initial_pay), str(s_pay_mode), str(s_receipt_no)]], columns=fee_log_df.columns)
                    fee_log_df = pd.concat([fee_log_df, new_log], ignore_index=True)
                    save_data(fee_log_df, FEE_COLLECTION_LOG_FILE)

                    st.success(f"🎉 **Student Record Saved Successfully!** Generated Roll No: **{new_id}**")
                    st.info(f"🗓️ **Exact Course End Date:** `{s_valid_upto}`")
                    st.info(f"🔑 **Default Student Login Password:** `{s_mobile}`")
                else:
                    st.error("⚠️ Please fill in all mandatory fields!")
    elif auth_pin:
        st.error("❌ Incorrect Passcode! Access Denied.")

# ==========================================
# 3. STUDENT LOGIN PORTAL
# ==========================================
elif menu == "🔑 Student Login Portal":
    st.title("🔑 Student Self-Service Login Portal")
    
    if 'student_logged_in' not in st.session_state:
        st.session_state.student_logged_in = False
        st.session_state.logged_student_id = ""

    if not st.session_state.student_logged_in:
        st.subheader("Login to Access Your Record Form & Fee Dues")
        st.info("💡 **Username:** Your Roll Number (e.g. STC26-001) | **Password:** Your Registered Mobile No.")

        with st.form("student_login_form"):
            login_user = st.text_input("Roll Number / Student ID").strip().upper()
            login_pass = st.text_input("Password", type="password").strip()
            
            if st.form_submit_button("🔑 Login Now"):
                matched_st_master = student_df[student_df['Student ID'].astype(str).str.upper() == login_user]
                matched_pass = st_pass_df[st_pass_df['Student ID'].astype(str).str.upper() == login_user]
                
                user_authenticated = False
                
                if not matched_pass.empty:
                    correct_pass = str(matched_pass.iloc[0]['Password']).strip()
                    if login_pass == correct_pass:
                        user_authenticated = True
                
                if not user_authenticated and not matched_st_master.empty:
                    actual_mobile = str(matched_st_master.iloc[0]['Mobile No']).strip()
                    if login_pass == actual_mobile:
                        user_authenticated = True
                        p_idx = st_pass_df[st_pass_df['Student ID'] == login_user].index
                        if not p_idx.empty:
                            st_pass_df.loc[p_idx, 'Password'] = actual_mobile
                        else:
                            st_pass_df = pd.concat([st_pass_df, pd.DataFrame([[login_user, actual_mobile]], columns=st_pass_df.columns)], ignore_index=True)
                        save_data(st_pass_df, STUDENT_PASSWORDS_FILE)

                if user_authenticated:
                    st.session_state.student_logged_in = True
                    st.session_state.logged_student_id = login_user
                    st.success("✅ Login Successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid Roll Number or Password!")
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
            
            stab1, stab2, stab3, stab4 = st.tabs(["🆔 AI Futuristic Digital ID Card", "💳 Fee Installment Record Form", "⏱️ Attendance & Badges", "🎟️ Exam, Admit Card & Result"])

            with stab1:
                st.markdown("### 🆔 SOFT TECH COMPUTERS - FUTURISTIC DIGITAL ID CARD")
                
                p_path = os.path.join(PHOTOS_DIR, f"{st_id}.jpg")
                avatar_url = f"app/static/{st_id}.jpg" if os.path.exists(p_path) else "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
                qr_code_url = f"https://api.qrserver.com/v1/create-qr-code/?size=120x120&data={st_id}"
                barcode_url = f"https://barcode.tec-it.com/barcode.ashx?data={st_id}&code=Code128&translate-esc=false"

                card_component_code = f"""
                <!DOCTYPE html>
                <html>
                <head>
                <link href="https://fonts.googleapis.com/css2?family=Great+Vibes&display=swap" rel="stylesheet">
                <style>
                  body {{ margin: 0; padding: 10px; background-color: transparent; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; text-align: center; }}
                  .card {{
                    max-width: 580px;
                    margin: auto;
                    background: linear-gradient(135deg, #000b18 0%, #00244a 100%);
                    border: 2px solid #00f2fe;
                    border-radius: 16px;
                    padding: 20px;
                    color: #ffffff;
                    box-shadow: 0 0 25px rgba(0, 242, 254, 0.4);
                    position: relative;
                    box-sizing: border-box;
                    text-align: left;
                  }}
                  .neon-bar {{
                    position: absolute; top: 0; left: 0; width: 100%; height: 5px;
                    background: linear-gradient(90deg, #00f2fe, #4facfe, #00f2fe);
                    border-top-left-radius: 16px; border-top-right-radius: 16px;
                  }}
                  .header {{ text-align: center; border-bottom: 1px solid rgba(255,255,255,0.15); padding-bottom: 10px; margin-bottom: 15px; }}
                  .header h2 {{ margin: 0; color: #00f2fe; font-size: 20px; text-transform: uppercase; letter-spacing: 2px; font-weight: 900; text-shadow: 0 0 8px rgba(0,242,254,0.6); }}
                  .header p {{ margin: 3px 0 0 0; font-size: 11px; color: #cccccc; letter-spacing: 0.5px; }}
                  .header .iso {{ font-size: 10px; color: #28a745; font-weight: bold; margin-top: 2px; }}
                  .body-grid {{ display: flex; gap: 20px; align-items: center; }}
                  .photo-box {{ flex: 0 0 120px; text-align: center; }}
                  .photo-img {{ width: 110px; height: 110px; border-radius: 50%; object-fit: cover; border: 3px solid #00f2fe; box-shadow: 0 0 15px rgba(0,242,254,0.5); }}
                  .id-badge {{ margin-top: 10px; background: rgba(0, 242, 254, 0.2); border: 1px solid #00f2fe; border-radius: 12px; padding: 4px 10px; font-size: 11px; font-weight: bold; color: #00f2fe; display: inline-block; }}
                  .info-box {{ flex: 1; font-size: 13px; line-height: 1.7; }}
                  .st-name {{ font-size: 19px; font-weight: 900; color: #ffffff; text-transform: uppercase; margin-bottom: 6px; letter-spacing: 1px; }}
                  .label {{ color: #00f2fe; font-weight: 600; }}
                  .footer-grid {{ margin-top: 15px; display: flex; justify-content: space-between; align-items: flex-end; border-top: 1px dashed rgba(255,255,255,0.2); padding-top: 12px; }}
                  .barcode-img {{ height: 38px; background: #fff; padding: 3px; border-radius: 4px; }}
                  
                  .sign-box {{ text-align: center; }}
                  .sign-font {{
                    font-family: 'Great Vibes', cursive, sans-serif;
                    font-size: 24px;
                    color: #ffffff;
                    text-shadow: 0 0 8px #00f2fe, 0 0 12px #00f2fe;
                  }}
                  .sign-title {{
                    font-size: 9px;
                    color: #00f2fe;
                    border-top: 1px dashed #00f2fe;
                    padding-top: 2px;
                    font-weight: bold;
                    text-transform: uppercase;
                    margin-top: 2px;
                  }}
                  
                  .qr-img {{ width: 55px; height: 55px; border-radius: 6px; border: 1px solid #00f2fe; background: #fff; padding: 2px; }}
                  
                  .print-btn {{
                    margin-top: 18px;
                    background: linear-gradient(90deg, #00f2fe, #4facfe);
                    color: #000000;
                    border: none;
                    padding: 10px 24px;
                    border-radius: 20px;
                    font-weight: bold;
                    font-size: 13px;
                    cursor: pointer;
                    box-shadow: 0 0 12px rgba(0, 242, 254, 0.5);
                    transition: 0.3s;
                  }}
                  .print-btn:hover {{ background: #ffffff; box-shadow: 0 0 18px rgba(0, 242, 254, 0.8); }}

                  @media print {{
                    body {{ background: transparent; padding: 0; }}
                    .no-print {{ display: none !important; }}
                    .card {{
                      box-shadow: none !important;
                      -webkit-print-color-adjust: exact !important;
                      print-color-adjust: exact !important;
                    }}
                  }}
                </style>
                </head>
                <body>
                  <div class="card">
                    <div class="neon-bar"></div>
                    <div class="header">
                      <h2>Soft Tech Computers</h2>
                      <p>KAMARCHUBURI, THELAMARA, SONITPUR | CENTER CODE: 4159</p>
                      <p class="iso">ISO 9001:2015 CERTIFIED INSTITUTION</p>
                    </div>
                    <div class="body-grid">
                      <div class="photo-box">
                        <img class="photo-img" src="{avatar_url}" alt="Photo">
                        <div class="id-badge">ID: {st_id}</div>
                      </div>
                      <div class="info-box">
                        <div class="st-name">{s_info['Name']}</div>
                        <div><span class="label">Course:</span> {s_info['Course']} ({s_info['Duration']})</div>
                        <div><span class="label">Batch Time:</span> {s_info['Batch Time']}</div>
                        <div><span class="label">Validity:</span> {s_info['Join Date']} to <span style="color:#28a745; font-weight:bold;">{s_info['Valid Up To']}</span></div>
                        <div><span class="label">Contact:</span> +91 {s_info['Mobile No']}</div>
                      </div>
                    </div>
                    <div class="footer-grid">
                      <div>
                        <img class="barcode-img" src="{barcode_url}">
                        <div style="font-size:8px; color:#aaa; text-align:center; margin-top:2px;">DIGITAL TRACKING ID</div>
                      </div>
                      
                      <div class="sign-box">
                        <div class="sign-font">Chiranjeeb Hazarika</div>
                        <div class="sign-title">Director & Founder</div>
                      </div>
                      
                      <div>
                        <img class="qr-img" src="{qr_code_url}">
                      </div>
                    </div>
                  </div>
                  
                  <button class="print-btn no-print" onclick="window.print()">🖨️ Print / Save ID Card as PDF</button>
                </body>
                </html>
                """
                
                components.html(card_component_code, height=430)

            with stab2:
                st.subheader("💳 Student Record Form - Fee Installment Details")
                
                try:
                    tot = float(s_info['Total Fee'])
                except:
                    tot = 8598.0
                try:
                    paid = float(s_info['Paid'])
                except:
                    paid = 0.0
                due = tot - paid

                try:
                    discount = float(s_info['Discount'])
                except:
                    discount = 0.0
                try:
                    exam_fee = float(s_info['Exam Fee'])
                except:
                    exam_fee = 999.0

                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Exact Course Fee", f"₹{tot}/-")
                c2.metric("Discount Allowed", f"₹{discount}/-")
                c3.metric("Exam Fee", f"₹{exam_fee}/-")
                c4.metric("Total Paid Till Now", f"₹{paid}/-", delta=f"Pending Balance Due: ₹{due}/-")

                st.markdown("---")
                st.markdown("### 📋 Formally Formatted 1st to 15th Fee Installment Ledger")
                
                breakdown_str = str(s_info['Payment Breakdown'])
                installments_list = []
                
                if breakdown_str and breakdown_str != "0":
                    entries = breakdown_str.split("|")
                    for idx, entry in enumerate(entries, 1):
                        if entry.strip():
                            installments_list.append({
                                "Installment No": f"{idx}st / {idx}nd / {idx}rd / {idx}th",
                                "Payment Description & Receipt Details": entry.strip()
                            })
                
                if installments_list:
                    st.table(get_display_df(pd.DataFrame(installments_list)))
                else:
                    st.info("No installment payments recorded yet.")

            with stab3:
                st.subheader("⏱️ Daily Attendance, Performance Badge & Duration")
                
                st_att_logs = attendance_df[attendance_df['Student ID'] == st_id] if not attendance_df.empty else pd.DataFrame()
                st_att_count = len(st_att_logs)
                total_classes = 20  
                att_pct = round((st_att_count / total_classes) * 100, 1) if total_classes > 0 else 0
                
                if att_pct >= 100:
                    badge_str = "🏆 ATTENDANCE CHAMPION (100% Attended)"
                    badge_color = "#28a745"
                elif att_pct >= 85:
                    badge_str = "🔥 STAR PERFORMER STUDENT (85%+ Attended)"
                    badge_color = "#ffc107"
                elif att_pct >= 75:
                    badge_str = "⭐ REGULAR LEARNER (75%+ Attended)"
                    badge_color = "#17a2b8"
                else:
                    badge_str = "⚠️ ATTENDANCE LOW (Below 75%)"
                    badge_color = "#dc3545"

                st.markdown(f'<div style="background-color: {badge_color}; color: white; padding: 10px 20px; border-radius: 10px; font-weight: bold; font-size: 16px; text-align: center; margin-bottom: 15px;">{badge_str}</div>', unsafe_allow_html=True)

                st.write(f"**Total Attended Days:** {st_att_count} Days (**{att_pct}%**)")
                st.progress(min(att_pct / 100.0, 1.0))
                
                st.markdown("#### ⏳ Class Time Duration Standard: **90 Minutes / Shift**")

            with stab4:
                st.subheader("🎟️ Final Examination Lifecycle Tracker")
                
                try:
                    tot = float(s_info['Total Fee'])
                except:
                    tot = 8598.0
                try:
                    paid = float(s_info['Paid'])
                except:
                    paid = 0.0
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
elif menu == "🎯 Sunday Free Practice Class (SFPC)":
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

            try:
                tot = float(s_info['Total Fee'])
            except:
                tot = 8598.0
            try:
                paid = float(s_info['Paid'])
            except:
                paid = 0.0

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
elif menu == "👨‍🏫 Teacher Portal & Fee Counter":
    st.title("👨‍🏫 Teacher & Staff Desk")
    
    current_teacher_pin = get_teacher_pin()
    t_pin_input = st.text_input("Enter Teacher Passcode / PIN", type="password")

    if t_pin_input == current_teacher_pin:
        st.success("Access Granted to Staff Desk.")
        ttab1, ttab2 = st.tabs(["⏱️ Teacher Shift & Class Log", "💵 Collect Fee & Issue Receipt"])

        with ttab1:
            st.subheader("Teacher Class Logging (Auto Live System Time)")
            with st.form("teacher_log_form"):
                t_selected_teacher = st.selectbox("Select Teacher Name", teacher_options if teacher_options else ["TC-01 - Chiranjeeb Hazarika"])
                t_shift = st.selectbox("Shift", ["Morning Shift", "Afternoon Shift", "Evening Shift"])
                
                live_time_now_str = get_ist_time_str()
                st.info(f"🕒 **System Live Clock Capture:** `{live_time_now_str}`")

                t_class_type = st.radio("Class Type", ["Theory", "Practical", "Both Theory & Practical"])
                t_selected_topics = st.multiselect("Select Topics Taught Today", AVAILABLE_TOPICS)
                t_status = st.selectbox("Status", ["Present", "Absent / Leave"])

                late_reason = st.selectbox("Reason for Late Entry (If arriving late) *", ["N/A - On Time", "🚗 Traffic Jam / Road Block", "🤒 Health Issue / Not Well", "🏠 Family Emergency", "🛵 Vehicle Breakdown", "📌 Other Personal Reason"])
                st_info = st.selectbox("Absent Status Information *", ["N/A - Present", "✅ Informed (By Phone/WhatsApp/Physical)", "❌ Uninformed / Absent Without Notice"])

                if st.form_submit_button("Submit Class Log"):
                    
                    is_valid = True
                    # Validate Shift Timing dynamically based on the submitted t_shift
                    if t_status == "Present":
                        shift_start_str = SHIFT_TIMINGS.get(t_shift, "07:30")
                        try:
                            shift_start_dt = datetime.strptime(shift_start_str, "%H:%M").time()
                            curr_time_dt = get_ist_now().time()
                            shift_start_mins = shift_start_dt.hour * 60 + shift_start_dt.minute
                            curr_time_mins = curr_time_dt.hour * 60 + curr_time_dt.minute
                            
                            if (curr_time_mins - shift_start_mins) > 10:
                                if late_reason == "N/A - On Time":
                                    st.error(f"🔴 **LATE ENTRY DETECTED:** You are logging in later than the {shift_start_str} start time. Please select a valid Reason for Late Entry!")
                                    is_valid = False
                                else:
                                    st.warning("🟡 Logged with Late Reason.")
                            else:
                                st.success("🟢 **ON TIME ENTRY**")
                        except Exception as e:
                            pass
                    
                    if is_valid:
                        t_teacher_name = t_selected_teacher.split(" - ")[1] if " - " in t_selected_teacher else t_selected_teacher
                        today_str = get_ist_date_str()
                        topics_str = ", ".join(t_selected_topics) if t_selected_topics else "General"
                        shift_wage = str(round(230.0 / 3.0, 2)) if t_status == "Present" else "0.0"

                        new_t_log = pd.DataFrame([[str(today_str), str(t_teacher_name), str(t_shift), str(live_time_now_str), str(live_time_now_str), str(t_class_type), str(topics_str), str(t_status), str(st_info), str(late_reason), str(shift_wage)]], columns=teacher_db.columns)
                        teacher_db = pd.concat([teacher_db, new_t_log], ignore_index=True)
                        save_data(teacher_db, TEACHER_LOG_FILE)
                        st.success(f"✅ **Class log recorded successfully at {live_time_now_str}!** Saved to Salary Log.")

        with ttab2:
            st.subheader("💵 Deposit Student Fee (Manual Receipt Sync)")
            
            if not student_df.empty:
                t_collector = st.selectbox("Collector / Teacher", teacher_options if teacher_options else ["TC-01 - Chiranjeeb Hazarika"])
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
                    student_df.at[idx, 'Paid'] = str(new_paid)

                    today_date_str = get_ist_date_str()
                    old_bd = str(student_df.at[idx, 'Payment Breakdown']) if pd.notnull(student_df.at[idx, 'Payment Breakdown']) else ""
                    new_bd = f"{old_bd} | Installment: ₹{int(t_add_amt)} ({t_fee_pmode}) [Receipt No: {t_manual_rec_no}] on {today_date_str}"
                    student_df.at[idx, 'Payment Breakdown'] = new_bd

                    save_data(student_df, STUDENT_MASTER_FILE)

                    new_fee_entry = pd.DataFrame([[str(today_date_str), str(teacher_name_input), str(t_f_sid), str(st_name_val), str(t_add_amt), str(t_fee_pmode), str(t_manual_rec_no)]], columns=fee_log_df.columns)
                    fee_log_df = pd.concat([fee_log_df, new_fee_entry], ignore_index=True)
                    save_data(fee_log_df, FEE_COLLECTION_LOG_FILE)

                    st.success(f"✅ **Fee Entry Saved!** Linked Manual Receipt No: **{t_manual_rec_no}**")
                    st.rerun()

# ==========================================
# 6. PARENTS LIVE TRACKER
# ==========================================
elif menu == "👨‍👩‍👧 Parents Live Student Tracker":
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
elif menu == "🔐 Admin Control Panel":
    st.title("🔐 Director / Admin Control Panel")
    
    current_admin_pass = get_admin_password()
    pwd = st.text_input("Enter Director Admin Password", type="password")

    if pwd == current_admin_pass:
        st.success("Access Granted. Welcome Sir!")

        tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
            "📊 Master Student Registry", 
            "💵 Quick Fee/Attendance Updater",
            "✏️ Edit Student Details",
            "👨‍🏫 Faculty Manager (Edit/Delete)",
            "🚨 Smart Overdue Alerts",
            "🔑 Credentials Ledger (Change Pass)",
            "🧾 Fee Audit Log", 
            "🔐 Security Settings"
        ])

        # TAB 1: ALL STUDENTS LIST
        with tab1:
            st.markdown(f"### Master Student Records ({len(student_df)} Total Students)")
            st.dataframe(get_display_df(student_df), height=700, use_container_width=True)

        # TAB 2: DIRECT QUICK FEE & BULK ATTENDANCE UPDATER
        with tab2:
            st.markdown("### ⚡ Direct Bulk Fee & Past Attendance Updater")
            st.info("💡 **Use this for 6-month past record adjustment:** Enter total paid fee or add bulk past attended days in 1-click.")

            if not student_df.empty:
                q_selected_st = st.selectbox("Select Student for Direct Update", student_options, key="quick_st_select")
                q_sid = q_selected_st.split(" - ")[0]
                q_idx = student_df[student_df['Student ID'] == q_sid].index[0]
                q_row = student_df.loc[q_idx]

                q_col1, q_col2 = st.columns(2)

                with q_col1:
                    st.markdown("#### 💵 Direct Paid Fee Adjustment")
                    try:
                        curr_paid_val = float(q_row['Paid'])
                    except:
                        curr_paid_val = 0.0

                    new_direct_paid = st.number_input("Update Total Paid Fee Till Date (₹)", value=curr_paid_val, step=100.0)
                    fee_note = st.text_input("Payment Note / Receipt Reference", value="Bulk 6-Month Past Fee Update")

                    if st.button("💾 Update Total Paid Fee"):
                        student_df.at[q_idx, 'Paid'] = str(new_direct_paid)
                        
                        today_str = get_ist_date_str()
                        old_bd = str(student_df.at[q_idx, 'Payment Breakdown']) if pd.notnull(student_df.at[q_idx, 'Payment Breakdown']) else ""
                        new_bd = f"{old_bd} | Admin Direct Update: ₹{int(new_direct_paid)} [{fee_note}] on {today_str}"
                        student_df.at[q_idx, 'Payment Breakdown'] = new_bd

                        save_data(student_df, STUDENT_MASTER_FILE)

                        # Audit Log
                        new_fee_entry = pd.DataFrame([[str(today_str), "Admin Direct", str(q_sid), str(q_row['Name']), str(new_direct_paid), "Adjustment", "ADMIN-SET"]], columns=fee_log_df.columns)
                        fee_log_df = pd.concat([fee_log_df, new_fee_entry], ignore_index=True)
                        save_data(fee_log_df, FEE_COLLECTION_LOG_FILE)

                        st.success(f"✅ Paid Fee updated to ₹{new_direct_paid}/- for {q_row['Name']}!")
                        st.rerun()

                with q_col2:
                    st.markdown("#### ⏱️ Direct Bulk Attendance Generator")
                    curr_att_count = len(attendance_df[attendance_df['Student ID'] == q_sid]) if not attendance_df.empty else 0
                    st.write(f"Current Attended Logs in System: **{curr_att_count} Days**")

                    add_days = st.number_input("Add Bulk Past Present Days (e.g., 40 days)", min_value=1, max_value=200, value=10)

                    if st.button("➕ Inject Past Attendance Records"):
                        today_str = get_ist_date_str()
                        new_att_entries = []
                        for i in range(int(add_days)):
                            new_att_entries.append([today_str, q_sid, q_row['Name'], "Present", get_ist_time_str()])
                        
                        new_att_df = pd.DataFrame(new_att_entries, columns=attendance_df.columns)
                        attendance_df = pd.concat([attendance_df, new_att_df], ignore_index=True)
                        save_data(attendance_df, ATTENDANCE_LOG_FILE)

                        st.success(f"🎉 Added {add_days} Days of Attendance for {q_row['Name']}!")
                        st.rerun()

        # TAB 3: EDIT STUDENT PROFILE
        with tab3:
            st.markdown("### ✏️ Edit Student Personal Profile, Address & Course Status")
            if not student_df.empty:
                edit_selected_st = st.selectbox("Select Student to Modify Record", student_options, key="edit_prof_select")
                edit_sid = edit_selected_st.split(" - ")[0]
                e_idx = student_df[student_df['Student ID'] == edit_sid].index[0]
                e_row = student_df.loc[e_idx]

                with st.form("admin_edit_full_profile_form"):
                    st.markdown("#### 👤 Update Personal & Contact Details")
                    p1, p2 = st.columns(2)
                    up_name = p1.text_input("Student Name", value=str(e_row['Name']))
                    up_father = p2.text_input("Father Name", value=str(e_row['Father Name']))
                    up_mother = p1.text_input("Mother Name", value=str(e_row['Mother Name']))
                    up_mobile = p2.text_input("Mobile No", value=str(e_row['Mobile No']))

                    st.markdown("#### 💳 Fee & Financial Records")
                    f1, f2 = st.columns(2)
                    up_tot_fee = f1.text_input("Exact Course Fee (₹)", value=str(e_row['Total Fee']))
                    up_paid_fee = f2.text_input("Total Paid Fee (₹)", value=str(e_row['Paid']))

                    st.markdown("#### 🏡 Update Address Details")
                    a1, a2, a3 = st.columns(3)
                    up_vill = a1.text_input("Village/Town", value=str(e_row['Vill Town']))
                    up_po = a2.text_input("P.O.", value=str(e_row['PO']))
                    up_ps = a3.text_input("P.S.", value=str(e_row['PS']))
                    
                    a4, a5 = st.columns(2)
                    up_pin = a4.text_input("PIN Code", value=str(e_row['PIN Code']))
                    up_dist = a5.text_input("District", value=str(e_row['District']))

                    st.markdown("#### 🎓 Course Status & Lifecycle")
                    s1, s2 = st.columns(2)
                    up_batch = s1.selectbox("Batch Time", BATCH_OPTIONS, index=BATCH_OPTIONS.index(e_row['Batch Time']) if e_row['Batch Time'] in BATCH_OPTIONS else 0)
                    up_status = s2.selectbox("Student Status (Pass Out / Active)", ["Active", "Passed Out", "Left / Discontinued"], index=0 if e_row['Student Status']=="Active" else (1 if e_row['Student Status']=="Passed Out" else 2))

                    if st.form_submit_button("💾 Save Profile Changes"):
                        student_df.at[e_idx, 'Name'] = str(up_name)
                        student_df.at[e_idx, 'Father Name'] = str(up_father)
                        student_df.at[e_idx, 'Mother Name'] = str(up_mother)
                        student_df.at[e_idx, 'Mobile No'] = str(up_mobile).strip()
                        student_df.at[e_idx, 'Total Fee'] = str(up_tot_fee)
                        student_df.at[e_idx, 'Paid'] = str(up_paid_fee)
                        student_df.at[e_idx, 'Vill Town'] = str(up_vill)
                        student_df.at[e_idx, 'PO'] = str(up_po)
                        student_df.at[e_idx, 'PS'] = str(up_ps)
                        student_df.at[e_idx, 'PIN Code'] = str(up_pin)
                        student_df.at[e_idx, 'District'] = str(up_dist)
                        student_df.at[e_idx, 'Full Address'] = f"Vill- {up_vill}, P.O.- {up_po}, P.S.- {up_ps}, PIN- {up_pin}, Dist- {up_dist}"
                        student_df.at[e_idx, 'Batch Time'] = str(up_batch)
                        student_df.at[e_idx, 'Student Status'] = str(up_status)

                        save_data(student_df, STUDENT_MASTER_FILE)
                        st.success(f"✅ Record for {up_name} ({edit_sid}) updated successfully!")
                        st.rerun()

                st.markdown("---")
                st.markdown("### 🗑️ Permanent Delete Student Record")
                st.warning("⚠️ **Danger Zone:** Deleting a student will completely remove them from the database.")
                
                del_confirm = st.checkbox(f"I confirm that I want to delete student **{e_row['Name']} ({edit_sid})** permanently.")
                if st.button("🗑️ Delete Student Permanently") and del_confirm:
                    student_df = student_df.drop(e_idx).reset_index(drop=True)
                    save_data(student_df, STUDENT_MASTER_FILE)
                    
                    st_pass_df = st_pass_df[st_pass_df['Student ID'] != edit_sid].reset_index(drop=True)
                    save_data(st_pass_df, STUDENT_PASSWORDS_FILE)
                    
                    st.success("❌ Student deleted permanently!")
                    st.rerun()

        # TAB 4: MANAGE TEACHERS (ADD, EDIT, DELETE)
        with tab4:
            st.markdown("### 👨‍🏫 Faculty / Teacher Master Registry")
            st.dataframe(get_display_df(teachers_master_df), use_container_width=True)

            t_add_col, t_edit_col = st.columns(2)

            with t_add_col:
                st.markdown("#### ➕ Add New Teacher / Faculty")
                with st.form("add_teacher_form"):
                    new_t_id = st.text_input("Teacher ID", value=f"TC-0{len(teachers_master_df)+1}")
                    new_t_name = st.text_input("Full Name *")
                    new_t_mob = st.text_input("Mobile No *")
                    new_t_desig = st.selectbox("Designation", ["Faculty / Instructor", "Lab Assistant", "Guest Teacher", "Director"])

                    if st.form_submit_button("➕ Save New Teacher"):
                        if new_t_name and new_t_mob:
                            new_t_row = pd.DataFrame([{"Teacher ID": str(new_t_id), "Teacher Name": str(new_t_name), "Mobile No": str(new_t_mob), "Designation": str(new_t_desig)}])
                            teachers_master_df = pd.concat([teachers_master_df, new_t_row], ignore_index=True)
                            save_data(teachers_master_df, TEACHERS_MASTER_FILE)
                            st.success(f"✅ Teacher **{new_t_name}** added successfully!")
                            st.rerun()
                        else:
                            st.error("Please fill Name and Mobile No!")

            with t_edit_col:
                st.markdown("#### ✏️ Edit / 🗑️ Delete Teacher")
                if not teachers_master_df.empty:
                    current_teachers = [f"{r['Teacher ID']} - {r['Teacher Name']}" for _, r in teachers_master_df.iterrows()]
                    
                    with st.form("edit_delete_teacher_form"):
                        sel_t_combo = st.selectbox("Select Teacher to Update/Delete", current_teachers)
                        sel_tid = sel_t_combo.split(" - ")[0]
                        t_idx = teachers_master_df[teachers_master_df['Teacher ID'] == sel_tid].index[0]
                        sel_t_row = teachers_master_df.loc[t_idx]

                        up_t_name = st.text_input("Name", value=sel_t_row['Teacher Name'])
                        up_t_mob = st.text_input("Mobile No", value=sel_t_row['Mobile No'])
                        desig_options = ["Faculty / Instructor", "Lab Assistant", "Guest Teacher", "Director"]
                        cur_desig = sel_t_row['Designation']
                        up_t_desig = st.selectbox("Designation", desig_options, index=desig_options.index(cur_desig) if cur_desig in desig_options else 0)
                        
                        del_t_confirm = st.checkbox("Check here to confirm permanent deletion")
                        
                        e_btn1, e_btn2 = st.columns(2)
                        upd_t_btn = e_btn1.form_submit_button("💾 Update Details")
                        del_t_btn = e_btn2.form_submit_button("🗑️ Delete Teacher")
                        
                        if upd_t_btn:
                            teachers_master_df.at[t_idx, 'Teacher Name'] = str(up_t_name)
                            teachers_master_df.at[t_idx, 'Mobile No'] = str(up_t_mob)
                            teachers_master_df.at[t_idx, 'Designation'] = str(up_t_desig)
                            save_data(teachers_master_df, TEACHERS_MASTER_FILE)
                            st.success(f"✅ Details updated for {sel_tid}!")
                            st.rerun()
                            
                        if del_t_btn:
                            if del_t_confirm:
                                teachers_master_df = teachers_master_df.drop(t_idx).reset_index(drop=True)
                                save_data(teachers_master_df, TEACHERS_MASTER_FILE)
                                st.success(f"✅ Teacher {sel_tid} removed from master database!")
                                st.rerun()
                            else:
                                st.error("⚠️ Please check the confirmation box to delete.")

        # TAB 5: OVERDUE ALERTS
        with tab5:
            st.markdown("### 🚨 Smart Overdue Fee Defaulters Tracker")
            overdue_list = []
            if not student_df.empty:
                for _, srow in student_df.iterrows():
                    try:
                        tot = float(srow['Total Fee'])
                    except:
                        tot = 8598.0
                    try:
                        paid = float(srow['Paid'])
                    except:
                        paid = 0.0
                    due = tot - paid
                    
                    if due > 1500:
                        overdue_list.append({
                            "Student ID": srow['Student ID'],
                            "Name": srow['Name'],
                            "Mobile No": srow['Mobile No'],
                            "Course": srow['Course'],
                            "Total Fee": f"₹{tot}",
                            "Paid": f"₹{paid}",
                            "Pending Due": f"₹{due}"
                        })
            
            if overdue_list:
                od_df = pd.DataFrame(overdue_list)
                st.error(f"⚠️ **Found {len(overdue_list)} Student(s) with Pending Fees > ₹1500!**")
                st.table(get_display_df(od_df))
            else:
                st.success("🎉 No Overdue Fee Defaulters found!")

        # TAB 6: CREDENTIALS LEDGER (CHANGE STUDENT PASSWORD)
        with tab6:
            st.markdown("### 🔑 Student Credentials Ledger")
            st.dataframe(get_display_df(st_pass_df), use_container_width=True)
            
            st.markdown("#### 🔄 Change Student Login Password")
            if not st_pass_df.empty:
                with st.form("change_student_password_form"):
                    pass_st_list = st_pass_df['Student ID'].tolist()
                    sel_pass_id = st.selectbox("Select Student ID", pass_st_list)
                    new_st_password = st.text_input("Enter New Password (e.g. Mobile No)")
                    
                    if st.form_submit_button("💾 Save New Password"):
                        if new_st_password:
                            p_idx = st_pass_df[st_pass_df['Student ID'] == sel_pass_id].index[0]
                            st_pass_df.at[p_idx, 'Password'] = str(new_st_password).strip()
                            save_data(st_pass_df, STUDENT_PASSWORDS_FILE)
                            st.success(f"✅ Password changed successfully for {sel_pass_id}!")
                            st.rerun()
                        else:
                            st.error("Please enter a valid password.")

        # TAB 7: FEE AUDIT
        with tab7:
            st.markdown("### 🧾 Fee Audit Log with Receipt Numbers")
            st.dataframe(get_display_df(fee_log_df), use_container_width=True)

        # TAB 8: SECURITY SETTINGS
        with tab8:
            st.markdown("### 🔐 Admin & Teacher Passcode Settings")
            curr_adm_pwd = get_admin_password()
            curr_t_pin = get_teacher_pin()

            with st.form("security_update_form"):
                new_admin_pass = st.text_input("New Admin Password", value=curr_adm_pwd, type="password")
                new_teacher_pin = st.text_input("New Teacher PIN", value=curr_t_pin, type="password")

                if st.form_submit_button("💾 Save Passcodes"):
                    set_admin_password(new_admin_pass.strip())
                    set_teacher_pin(new_teacher_pin.strip())
                    st.success("✅ Security Passcodes Updated Successfully!")
                    st.rerun()