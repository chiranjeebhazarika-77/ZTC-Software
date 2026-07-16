import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Page Config and Beautiful Dark Blue Theme
st.set_page_config(page_title="Soft Tech Computers & ZTC", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0B111E; color: #E2E8F0; }
    .sidebar .sidebar-content { background-color: #1E293B; }
    .main-header {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        padding: 25px; border-radius: 12px; text-align: center;
        margin-bottom: 25px; border: 1px solid #334155;
    }
    .main-title { color: #FFFFFF; font-size: 32px; font-weight: 800; letter-spacing: 1.5px; margin: 0; }
    .main-subtitle { color: #38BDF8; font-size: 16px; margin-top: 5px; font-weight: 600; }
    div.stButton > button:first-child {
        background-color: #2563EB; color: white; border-radius: 6px;
        border: none; padding: 0.5rem 1rem; font-weight: bold;
    }
    .metric-box {
        background-color: #1E293B; padding: 20px; border-radius: 8px;
        border-left: 5px solid #2563EB; margin-bottom: 15px;
    }
    .metric-box.collection { border-left-color: #10B981; }
    .metric-box.dues { border-left-color: #EF4444; }
    .m-title { font-size: 14px; color: #94A3B8; font-weight: 600; }
    .m-val { font-size: 24px; font-weight: bold; color: #FFFFFF; }
    
    input, select, textarea, div[data-baseweb="select"] {
        background-color: #1E293B !important; color: #FFFFFF !important;
    }
    .lock-message {
        background-color: #1E293B; padding: 30px; border-radius: 10px;
        border: 1px dashed #3B82F6; text-align: center; margin-top: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Database File Paths
STUDENT_DB = "students_db.csv"
TEACHER_DB = "teachers_db.csv"
T_ATTENDANCE_DB = "teacher_attendance.csv"
SYLLABUS_DB = "syllabus_logs.csv"
SETTINGS_FILE = "system_settings.csv"
COURSE_FEE_FILE = "course_fees_db.csv"
PASSWORD_FILE = "passwords.csv"

COURSES = ["DCA", "ADCA", "PGDCA", "CERTIFICATE 1 MONTH", "CERTIFICATE 2 MONTH", "CERTIFICATE 3 MONTH", "45 DAYS COURSE", "TALLY", "PYTHON", "TYPING COURSE", "Class 9 English", "Class 10 English", "Class 11 English", "Class 12 English", "BA English"]

# Load/Save Passwords Function
def load_passwords():
    if os.path.exists(PASSWORD_FILE):
        try:
            df = pd.read_csv(PASSWORD_FILE)
            return {"admin": str(df.at[0, "admin"]), "teacher": str(df.at[0, "teacher"])}
        except: pass
    df = pd.DataFrame([{"admin": "admin123", "teacher": "teacher123"}])
    df.to_csv(PASSWORD_FILE, index=False)
    return {"admin": "admin123", "teacher": "teacher123"}

def save_passwords(admin_pwd, teacher_pwd):
    df = pd.DataFrame([{"admin": admin_pwd, "teacher": teacher_pwd}])
    df.to_csv(PASSWORD_FILE, index=False)

# Universal Data Loaders
def load_data(file_path, default_cols, default_row):
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            for col in default_cols:
                if col not in df.columns: df[col] = ""
            return df[default_cols]
        except: pass
    df = pd.DataFrame([default_row], columns=default_cols)
    df.to_csv(file_path, index=False)
    return df

def save_data(df, file_path):
    df.to_csv(file_path, index=False)

def load_course_fees():
    if os.path.exists(COURSE_FEE_FILE):
        try:
            df = pd.read_csv(COURSE_FEE_FILE)
            return dict(zip(df["Course"], df["Fee"]))
        except: pass
    default_fees = {c: 5000 for c in COURSES}
    default_fees["ADCA"] = 8500
    default_fees["Class 10 English"] = 8499
    pd.DataFrame(list(default_fees.items()), columns=["Course", "Fee"]).to_csv(COURSE_FEE_FILE, index=False)
    return default_fees

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            df = pd.read_csv(SETTINGS_FILE)
            return {"PER_DAY_SALARY": int(df.at[0, "PER_DAY_SALARY"]), "LATE_FINE": int(df.at[0, "LATE_FINE"]), "MORNING_START": str(df.at[0, "MORNING_START"]), "AFTERNOON_START": str(df.at[0, "AFTERNOON_START"])}
        except: pass
    df = pd.DataFrame([{"PER_DAY_SALARY": 230, "LATE_FINE": 50, "MORNING_START": "07:30", "AFTERNOON_START": "16:00"}])
    df.to_csv(SETTINGS_FILE, index=False)
    return {"PER_DAY_SALARY": 230, "LATE_FINE": 50, "MORNING_START": "07:30", "AFTERNOON_START": "16:00"}

# Load configurations
pwds = load_passwords()
sys_settings = load_settings()
PER_DAY_SALARY = sys_settings["PER_DAY_SALARY"]
LATE_FINE = sys_settings["LATE_FINE"]
MORNING_START = sys_settings["MORNING_START"]
AFTERNOON_START = sys_settings["AFTERNOON_START"]
COURSE_FEES_DICT = load_course_fees()

# Initialize Databases
student_cols = ["Student ID", "Name", "Father Name", "Mother Name", "DOB", "Mobile No", "Address", "Institute", "Course", "Batch", "Admission Fee", "Total Fee", "Paid", "Attended"]
default_student = {"Student ID": "STC26-001", "Name": "Hiya Das", "Father Name": "Moni Das", "Mother Name": "Rumi Das", "DOB": "2010-05-12", "Mobile No": "9876543210", "Address": "Kamarchuburi", "Institute": "Soft Tech Computers", "Course": "ADCA", "Batch": "MWF", "Admission Fee": 999, "Total Fee": 8500, "Paid": 4999, "Attended": 16}
st.session_state.student_db = load_data(STUDENT_DB, student_cols, default_student)

teacher_cols = ["Teacher ID", "Teacher Name", "Mobile No", "Subject/Expertise", "Status"]
default_teacher = {"Teacher ID": "TCH26-001", "Teacher Name": "Zaan Hazarika", "Mobile No": "9999999999", "Subject/Expertise": "English & IT", "Status": "Active"}
st.session_state.teacher_db = load_data(TEACHER_DB, teacher_cols, default_teacher)

t_att_cols = ["Date", "Time", "Teacher ID", "Teacher Name", "Punch Type", "Punch Status", "Fine Deducted", "Earnings"]
default_t_att = {"Date": "2026-05-02", "Time": "07:25:00", "Teacher ID": "TCH26-001", "Teacher Name": "Zaan Hazarika", "Punch Type": "Morning In", "Punch Status": "On Time", "Fine Deducted": 0, "Earnings": 230}
st.session_state.teacher_attendance = load_data(T_ATTENDANCE_DB, t_att_cols, default_t_att)

syllabus_cols = ["Date", "Student ID", "Student Name", "Course", "Teacher Name", "Topic Covered", "Remarks"]
default_syllabus = {"Date": "2026-05-02", "Student ID": "STC26-001", "Student Name": "Hiya Das", "Course": "ADCA", "Teacher Name": "Zaan Hazarika", "Topic Covered": "Basics of Windows", "Remarks": "Good Progress"}
st.session_state.syllabus_logs = load_data(SYLLABUS_DB, syllabus_cols, default_syllabus)

# Sidebar Branding
st.sidebar.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
if os.path.exists("logo.jpg"): st.sidebar.image("logo.jpg", width=120)
st.sidebar.markdown("<h3 style='color: white; margin-top: 10px;'>🔑 Control Panel</h3></div>", unsafe_allow_html=True)

user_role = st.sidebar.radio("Go To:", ["Student Kiosk", "Teacher Panel", "Admin Portal"])

# Dynamic Main Heading Generator
heading_extension = "(Student Kiosk)"
if user_role == "Teacher Panel": heading_extension = "(Teacher Portal)"
elif user_role == "Admin Portal": heading_extension = "(Admin Portal)"

st.markdown(f'<div class="main-header"><div class="main-title">🏛️ SOFT TECH COMPUTERS & ZTC {heading_extension}</div><div class="main-subtitle">⚡ Integrated Educational Management System | Center Code: 4159 ⚡</div></div>', unsafe_allow_html=True)

# Helper function to display clean dataframes starting from Index 1 instead of 0
def show_clean_dataframe(df):
    if len(df) > 0:
        display_df = df.copy()
        display_df.index = range(1, len(display_df) + 1)
        st.dataframe(display_df, use_container_width=True)
    else:
        st.info("No records found in this database.")

# --- I. STUDENT KIOSK ---
if user_role == "Student Kiosk":
    st.title("🎓 Student Self-Service Kiosk")
    action = st.selectbox("Choose Action:", ["📝 1. Full Admission Form", "✋ 2. Mark Student Attendance & Benefits"])
    
    if action == "📝 1. Full Admission Form":
        st.subheader("📋 New Student Registration Form")
        with st.form("admission_form"):
            col_a, col_b = st.columns(2)
            with col_a:
                s_name = st.text_input("Student Full Name:")
                s_father = st.text_input("Father's Name:")
                s_mother = st.text_input("Mother's Name:")
                s_dob = st.text_input("Date of Birth (YYYY-MM-DD):")
                s_mobile = st.text_input("Mobile Number:")
            with col_b:
                s_address = st.text_input("Full Address:")
                s_inst = st.selectbox("Institute Name:", ["Soft Tech Computers", "ZTC (Zaan Tuition Center)"])
                s_course = st.selectbox("Select Course:", COURSES)
                s_batch = st.selectbox("Select Batch:", ["MWF", "TTS", "Regular"])
                s_adm_fee = st.number_input("Admission Fee Paid (₹):", value=999)
                auto_fee = COURSE_FEES_DICT.get(s_course, 5000)
                s_total_fee = st.number_input("Total Course Fee (₹):", value=int(auto_fee))
            
            if st.form_submit_button("Submit Form & Register Me"):
                if s_name and s_mobile:
                    df = st.session_state.student_db
                    new_id = f"STC26-{len(df)+1:03d}"
                    new_row = {"Student ID": new_id, "Name": s_name, "Father Name": s_father, "Mother Name": s_mother, "DOB": s_dob, "Mobile No": s_mobile, "Address": s_address, "Institute": s_inst, "Course": s_course, "Batch": s_batch, "Admission Fee": s_adm_fee, "Total Fee": s_total_fee, "Paid": s_adm_fee, "Attended": 0}
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    save_data(df, STUDENT_DB); st.session_state.student_db = df; st.success(f"🎉 Registered! ID: {new_id}"); st.rerun()
                else: st.error("Error: Fill Name and Mobile Number.")
                    
    elif action == "✋ 2. Mark Student Attendance & Benefits":
        st.subheader("📝 Attendance Marker")
        if len(st.session_state.student_db) > 0 and st.session_state.student_db["Student ID"].tolist():
            s_id = st.selectbox("Select Your Student ID:", st.session_state.student_db["Student ID"].tolist())
            df_st = st.session_state.student_db
            current_st = df_st[df_st["Student ID"] == s_id].iloc[0]
            
            fees_paid = float(current_st["Paid"]) if current_st["Paid"] else 0.0
            total_fees = float(current_st["Total Fee"]) if current_st["Total Fee"] else 0.0
            classes_attended = int(current_st["Attended"]) if current_st["Attended"] else 0
            
            st.info(f"Student: **{current_st['Name']}** | Batch: **{current_st['Batch']}** | Paid: **₹{fees_paid}**")
            if fees_paid > (total_fees / 2.0) and classes_attended >= 15:
                st.markdown('<div style="background-color: #10B981; padding: 15px; border-radius: 8px; color: white;">🎉 Eligible for SUNDAY FREE PRACTICAL CLASS!</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="background-color: #1E293B; padding: 15px; border-radius: 8px; color: #94A3B8;">🔒 Lock Status: Sunday Practical (Maintain Fees & Attendance)</div>', unsafe_allow_html=True)

            if st.button("Confirm & Mark Attendance"):
                df = st.session_state.student_db
                idx = df[df["Student ID"] == s_id].index[0]
                df.at[idx, "Attended"] = int(df.at[idx, "Attended"] if df.at[idx, "Attended"] else 0) + 1
                save_data(df, STUDENT_DB); st.success("✅ Attendance marked!"); st.rerun()
        else: st.warning("No students registered yet.")

# --- II. TEACHER PANEL ---
elif user_role == "Teacher Panel":
    st.title("👨‍🏫 Faculty Operations & Update Desk")
    
    t_pwd_input = st.sidebar.text_input("Teacher Password:", type="password", key="t_pwd")
    if t_pwd_input != pwds["teacher"]:
        st.markdown("""
        <div class="lock-message">
            <h2 style='color: #EF4444;'>🔒 Teacher Portal Locked</h2>
            <p style='color: #94A3B8; font-size:16px;'>Please enter the authorized <b>Teacher Password</b> in the left sidebar configuration block to reveal daily punch options.</p>
        </div>
        """, unsafe_allow_html=True)
        st.stop()
        
    t_action = st.selectbox("Select Action:", ["⏰ 1. Live Time Attendance (4-Way)", "📚 2. Student Syllabus Tracking Log"])
    teacher_list = st.session_state.teacher_db["Teacher Name"].tolist()
    
    if t_action == "⏰ 1. Live Time Attendance (4-Way)":
        st.subheader("🔴 Faculty 4-Way Daily Punch Terminal")
        t_name_select = st.selectbox("Select Your Name:", teacher_list)
        
        df_att_all = st.session_state.teacher_attendance
        df_t_logs = df_att_all[df_att_all["Teacher Name"] == t_name_select] if len(df_att_all) > 0 else pd.DataFrame()
        total_days = df_t_logs["Date"].nunique() if len(df_t_logs) > 0 else 0
        total_lates = len(df_t_logs[df_t_logs["Punch Status"] == "LATE"]) if len(df_t_logs) > 0 else 0
        net_earnings = (total_days * PER_DAY_SALARY) - (total_lates * LATE_FINE)
        
        st.markdown(f"### 📊 Salary & Shift Ledger")
        tc1, tc2, tc3 = st.columns(3)
        with tc1: st.info(f"📆 Total Working Days Logged: **{total_days}**")
        with tc2: st.warning(f"⚠️ Total Lates Flagged: **{total_lates}**")
        with tc3: st.success(f"💰 Net Payout Accumulation: **₹{max(0, net_earnings)}**")
        
        p_col1, p_col2, p_col3, p_col4 = st.columns(4)
        now = datetime.now(); live_date = now.strftime("%Y-%m-%d"); live_time = now.strftime("%H:%M:%S"); current_hour_min = now.strftime("%H:%M")
        t_id = st.session_state.teacher_db[st.session_state.teacher_db["Teacher Name"] == t_name_select].iloc[0]["Teacher ID"]
        
        def execute_punch(punch_type, time_limit, is_in_punch=True):
            status = "On Time"; fine = 0
            if is_in_punch and current_hour_min > time_limit: status = "LATE"; fine = LATE_FINE
            new_log = {"Date": live_date, "Time": live_time, "Teacher ID": t_id, "Teacher Name": t_name_select, "Punch Type": punch_type, "Punch Status": status, "Fine Deducted": fine, "Earnings": PER_DAY_SALARY}
            updated_df = pd.concat([st.session_state.teacher_attendance, pd.DataFrame([new_log])], ignore_index=True)
            save_data(updated_df, T_ATTENDANCE_DB); st.session_state.teacher_attendance = updated_df; st.success(f"⏱️ {punch_type} Registered!"); st.rerun()

        with p_col1:
            if st.button("🌅 1. Morning IN"): execute_punch("Morning In", MORNING_START, is_in_punch=True)
        with p_col2:
            if st.button("🚶‍♂️ 2. Morning OUT"): execute_punch("Morning Out", "", is_in_punch=False)
        with p_col3:
            if st.button("🌆 3. Afternoon IN"): execute_punch("Afternoon In", AFTERNOON_START, is_in_punch=True)
        with p_col4:
            if st.button("🏠 4. Afternoon OUT"): execute_punch("Afternoon Out", "", is_in_punch=False)

    elif t_action == "📚 2. Student Syllabus Tracking Log":
        st.subheader("📖 Track Progress")
        df_stu = st.session_state.student_db
        if len(df_stu) > 0 and df_stu["Student ID"].tolist():
            with st.form("syllabus_form"):
                t_name_select = st.selectbox("Faculty Name:", teacher_list)
                s_id_select = st.selectbox("Select Student ID:", df_stu["Student ID"].tolist())
                stu_row = df_stu[df_stu["Student ID"] == s_id_select].iloc[0]
                topic_covered = st.text_input("Topic Covered Today:")
                remarks = st.text_area("Remarks:")
                if st.form_submit_button("Save Progress"):
                    if topic_covered:
                        new_syl = {"Date": datetime.now().strftime("%Y-%m-%d"), "Student ID": s_id_select, "Student Name": stu_row['Name'], "Course": stu_row['Course'], "Teacher Name": t_name_select, "Topic Covered": topic_covered, "Remarks": remarks}
                        updated_syl = pd.concat([st.session_state.syllabus_logs, pd.DataFrame([new_syl])], ignore_index=True)
                        save_data(updated_syl, SYLLABUS_DB); st.session_state.syllabus_logs = updated_syl; st.success("Saved!"); st.rerun()
        else: st.warning("No students registered.")

# --- III. ADMIN PORTAL ---
elif user_role == "Admin Portal":
    st.title("📊 Master Executive Command Center")
    
    a_pwd_input = st.sidebar.text_input("Admin Password:", type="password", key="a_pwd")
    if a_pwd_input != pwds["admin"]:
        st.markdown("""
        <div class="lock-message">
            <h2 style='color: #EF4444;'>🔒 Admin Security Portal Locked</h2>
            <p style='color: #94A3B8; font-size:16px;'>Please enter the correct corporate <b>Admin Password</b> inside the left sidebar field box to display managerial operations dashboard tables.</p>
        </div>
        """, unsafe_allow_html=True)
        st.stop()
        
    with st.expander("🔐 Security & System Password Reset Center"):
        st.subheader("Modify Administrative Gateway Passwords")
        with st.form("pwd_reset_form"):
            new_admin_pwd = st.text_input("Change Admin Password:", value=pwds["admin"])
            new_teacher_pwd = st.text_input("Change Teacher Password:", value=pwds["teacher"])
            if st.form_submit_button("Lock & Update Passwords Permanently"):
                save_passwords(new_admin_pwd, new_teacher_pwd)
                st.success("🎉 Passwords updated successfully in system database config file!")
                st.rerun()
    
    with st.expander("⚠️ Master System Reset Controls (Data Clearance)"):
        rc1, rc2 = st.columns(2)
        with rc1:
            if st.button("🚨 Reset ALL Teacher Attendance Logs"):
                empty = pd.DataFrame(columns=["Date", "Time", "Teacher ID", "Teacher Name", "Punch Type", "Punch Status", "Fine Deducted", "Earnings"])
                save_data(empty, T_ATTENDANCE_DB); st.session_state.teacher_attendance = empty; st.warning("Wiped Logs!"); st.rerun()
        with rc2:
            if st.button("🚨 Reset ALL Student Records to Default"):
                empty_stu = pd.DataFrame([default_student], columns=student_cols)
                save_data(empty_stu, STUDENT_DB); st.session_state.student_db = empty_stu; st.warning("Reset Students!"); st.rerun()

    with st.expander("⚙️ System Control: Salary, Fines & Shift Timings"):
        with st.form("system_settings_form"):
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                set_pay = st.number_input("Per Day Salary (₹):", value=PER_DAY_SALARY)
                set_fine = st.number_input("Late Punch Fine (₹):", value=LATE_FINE)
            with col_s2:
                set_morning = st.text_input("Morning Entry Limit (HH:MM):", value=MORNING_START)
                set_afternoon = st.text_input("Afternoon Entry Limit (HH:MM):", value=AFTERNOON_START)
            if st.form_submit_button("Save System Rules"):
                pd.DataFrame([{"PER_DAY_SALARY": set_pay, "LATE_FINE": set_fine, "MORNING_START": set_morning, "AFTERNOON_START": set_afternoon}]).to_csv(SETTINGS_FILE, index=False)
                st.success("Rules Updated!"); st.rerun()

    with st.expander("💸 Collect Installment / Student Fee"):
        df_stu = st.session_state.student_db
        if len(df_stu) > 0 and df_stu["Student ID"].tolist():
            s_id_pay = st.selectbox("Select Student ID:", df_stu["Student ID"].tolist(), key="pay_select")
            c_row_pay = df_stu[df_stu["Student ID"] == s_id_pay].iloc[0]
            st.warning(f"Student: {c_row_pay['Name']} | Paid: ₹{c_row_pay['Paid']} / ₹{c_row_pay['Total Fee']}")
            with st.form("collect_fee_form"):
                inst_amount = st.number_input("Enter Amount (₹):", value=550)
                if st.form_submit_button("Confirm Payment"):
                    idx = df_stu[df_stu["Student ID"] == s_id_pay].index[0]
                    df_stu.at[idx, "Paid"] = float(df_stu.at[idx, "Paid"] if df_stu.at[idx, "Paid"] else 0) + float(inst_amount)
                    save_data(df_stu, STUDENT_DB); st.success("Payment Added!"); st.rerun()
        else: st.warning("No students registered yet.")

    with st.expander("🛠️ Master Control: Edit / Delete Single Student Records"):
        df_stu = st.session_state.student_db
        if len(df_stu) > 0 and df_stu["Student ID"].tolist():
            s_id_manage = st.selectbox("Select Student ID to Manage:", df_stu["Student ID"].tolist(), key="manage_select")
            c_row = df_stu[df_stu["Student ID"] == s_id_manage].iloc[0]
            
            st.markdown("### 📝 Edit Details")
            with st.form("admin_edit_student"):
                e_name = st.text_input("Name:", value=str(c_row.get("Name", "")))
                e_total = st.number_input("Total Fee:", value=int(c_row.get("Total Fee", 5000) if c_row.get("Total Fee") else 5000))
                e_paid = st.number_input("Total Paid:", value=int(c_row.get("Paid", 0) if c_row.get("Paid") else 0))
                if st.form_submit_button("Update Master Record"):
                    idx = df_stu[df_stu["Student ID"] == s_id_manage].index[0]
                    df_stu.at[idx, "Name"], df_stu.at[idx, "Total Fee"], df_stu.at[idx, "Paid"] = e_name, e_total, e_paid
                    save_data(df_stu, STUDENT_DB); st.success("Updated!"); st.rerun()
            
            st.markdown("---")
            st.markdown("### 🚨 Danger Zone")
            if st.button(f"🗑️ Delete Student {s_id_manage} Permanently", key="single_del_btn"):
                df_stu = df_stu[df_stu["Student ID"] != s_id_manage]
                save_data(df_stu, STUDENT_DB); st.session_state.student_db = df_stu; st.success("Removed Student!"); st.rerun()
        else: st.warning("Registry empty.")

    # 👨‍🏫 NEW: TEACHER DATA MANAGEMENT BOX (ডিলিট কৰিবলৈ) 👨‍🏫
    with st.expander("🛠️ Faculty Master Control: Edit / Delete Teacher Records"):
        df_tch = st.session_state.teacher_db
        if len(df_tch) > 0 and df_tch["Teacher ID"].tolist():
            t_id_manage = st.selectbox("Select Teacher ID to Manage:", df_tch["Teacher ID"].tolist(), key="t_manage_select")
            t_row = df_tch[df_tch["Teacher ID"] == t_id_manage].iloc[0]
            st.info(f"Selected Faculty: **{t_row['Teacher Name']}** | Expertise: **{t_row['Subject/Expertise']}**")
            
            # ছিংগেল শিক্ষক ডিলিট কৰা বুটাম
            if st.button(f"🗑️ Delete Teacher {t_row['Teacher Name']} Permanently", key="single_t_del_btn"):
                df_tch = df_tch[df_tch["Teacher ID"] != t_id_manage]
                save_data(df_tch, TEACHER_DB)
                st.session_state.teacher_db = df_tch
                st.success(f"💥 Faculty {t_row['Teacher Name']} completely removed from database!")
                st.rerun()
        else: st.warning("No teacher records available.")

    # Financial Summary Dashboard
    df_stu = st.session_state.student_db
    df_stu["Total Fee"] = pd.to_numeric(df_stu["Total Fee"], errors='coerce').fillna(0)
    df_stu["Paid"] = pd.to_numeric(df_stu["Paid"], errors='coerce').fillna(0)
    total_dues = df_stu["Total Fee"].sum() - df_stu["Paid"].sum()
    
    col1, col2, col3 = st.columns(3)
    with col1: st.markdown(f'<div class="metric-box"><div class="m-title">Total Students</div><div class="m-val">{len(df_stu)}</div></div>', unsafe_allow_html=True)
    with col2: st.markdown(f'<div class="metric-box collection"><div class="m-title">Gross Revenue</div><div class="m-val">₹{df_stu["Paid"].sum():,}</div></div>', unsafe_allow_html=True)
    with col3: st.markdown(f'<div class="metric-box dues"><div class="m-title">Outstanding Dues</div><div class="m-val">₹{total_dues:,}</div></div>', unsafe_allow_html=True)
    
    t1, t2, t3, t4 = st.tabs(["📋 Student Roster", "🕒 Faculty Attendance Logs", "📚 Syllabus Progress", "👨‍🏫 Authorized Faculty"])
    with t1: show_clean_dataframe(df_stu)
    with t2: show_clean_dataframe(st.session_state.teacher_attendance)
    with t3: show_clean_dataframe(st.session_state.syllabus_logs)
    with t4: show_clean_dataframe(st.session_state.teacher_db)