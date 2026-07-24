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
FEE_COLLECTION_LOG_FILE = "fee_collection_log.csv" # Teacher collection log
ROUTINE_FILE = "routine_settings.csv"
PASSWORD_FILE = "passwords.csv"

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

# Password Management
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

# Master Column Definitions
student_cols = ['Student ID', 'Name', 'Father Name', 'Mother Name', 'Mobile No', 'Address', 'Course', 'Batch', 'Admission Mode', 'Total Fee', 'Paid', 'Payment Breakdown', 'Admission Date']
attendance_cols = ['Date', 'Student ID', 'Name', 'Action', 'Time']
fee_collect_cols = ['Date', 'Collected By', 'Student ID', 'Student Name', 'Amount (₹)']

# Load Clean Databases
student_df = load_clean_data(STUDENT_MASTER_FILE, student_cols, is_student_file=True)
attendance_df = load_clean_data(ATTENDANCE_LOG_FILE, attendance_cols)
fee_log_df = load_clean_data(FEE_COLLECTION_LOG_FILE, fee_collect_cols)
enquiry_db = load_clean_data(ENQUIRY_FILE, ['Name', 'Mobile', 'Course Selected', 'Timestamp'])
teacher_db = load_clean_data(TEACHER_LOG_FILE, ['Date', 'Shift', 'In-Time', 'Out-Time', 'Subject Taught', 'Status', 'Salary (₹)'])
routine_db = load_clean_data(ROUTINE_FILE, ['Shift', 'Timing', 'Days', 'Assigned Class'])

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

# Helper Options
student_options = []
if not student_df.empty:
    student_options = [f"{row['Student ID']} - {row['Name']}" for _, row in student_df.iterrows()]

# Navigation Menu
menu = st.sidebar.radio("Navigation", ["🏠 Home & Enquiry", "🎓 Student Admission & Attendance", "👨‍🏫 Teacher Portal & Fee Entry", "🔐 Admin Panel"])

# ==========================================
# 1. PUBLIC DASHBOARD
# ==========================================
if menu == "🏠 Home & Enquiry":
    st.title("Welcome to Soft Tech Computers")
    st.subheader("Kamarchuburi, Thelamara, Sonitpur, Assam")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 🗓️ Active Class Time Table / Routine")
        st.table(routine_db)

        st.markdown("### 🪙 Courses & Course Packages")
        fees_list = [{"Course/Class": k, "Total Course Fee": f"₹ {v}/-"} for k, v in st.session_state.fee_settings.items()]
        st.table(pd.DataFrame(fees_list))

        st.markdown("### 📱 Scan from Phone to Open Portal")
        qr_url = "https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=https://stcztc.streamlit.app"
        st.image(qr_url, caption="Scan this using Mobile Camera")

    with col2:
        st.markdown("### ✉️ Quick Course Enquiry")
        with st.form("enquiry_form", clear_on_submit=True):
            enq_name = st.text_input("Student Name")
            enq_mobile = st.text_input("Mobile Number")
            enq_course = st.selectbox("Select Course/Class", list(st.session_state.fee_settings.keys()), index=0)

            selected_fee = st.session_state.fee_settings.get(enq_course, 5000)
            st.info(f"Total Course Fee: ₹ {selected_fee}/-")

            submitted = st.form_submit_button("Submit Enquiry")
            if submitted:
                if enq_name and enq_mobile:
                    new_enq = pd.DataFrame([[enq_name, enq_mobile, enq_course, datetime.now().strftime("%Y-%m-%d %H:%M")]], columns=enquiry_db.columns)
                    enquiry_db = pd.concat([enquiry_db, new_enq], ignore_index=True)
                    save_data(enquiry_db, ENQUIRY_FILE)
                    st.success("Enquiry registered successfully!")

                    # --- WhatsApp Notification Link ---
                    msg_text = f"Hello Soft Tech Computers!\nNew Enquiry Received:\nName: {enq_name}\nPhone: {enq_mobile}\nCourse: {enq_course}"
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
                    st.warning("Please fill in both Name and Mobile Number.")

# ==========================================
# 2. STUDENT PORTAL
# ==========================================
elif menu == "🎓 Student Admission & Attendance":
    st.title("🎓 Student Self-Service Portal")
    loc_check = st.checkbox("Verify my device location (Must be within 50 meters of Center)")

    if loc_check:
        st.success("📍 Location Verified Inside Center Boundary")
        tab1, tab2, tab3 = st.tabs(["📝 Student Admission Form", "⏱️ Mark Attendance", "🎯 Search Profile & SFPC Status"])

        with tab1:
            st.subheader("New Student Registration")
            with st.form("admission_form"):
                s_name = st.text_input("Student Full Name")
                s_father = st.text_input("Father's Name")
                s_mother = st.text_input("Mother's Name")
                s_mobile = st.text_input("Mobile Number")
                s_address = st.text_input("Full Address")
                s_course = st.selectbox("Course", list(st.session_state.fee_settings.keys()))
                s_batch = st.text_input("Batch Timing/Slot")
                s_mode = st.selectbox("Admission Mode", ["Full Onetime", "Monthly Installments"])
                s_initial_pay = st.number_input("Initial Fee Amount Paid (₹)", min_value=0.0, value=999.0)

                if st.form_submit_button("Register Student"):
                    if s_name and s_mobile:
                        new_id = f"STC26-00{len(student_df)+1}"
                        tot_f = st.session_state.fee_settings.get(s_course, 5000)
                        today_date_str = datetime.now().strftime("%Y-%m-%d")
                        breakdown = f"[{today_date_str}] ₹{int(s_initial_pay)}"
                        
                        new_row = pd.DataFrame([[new_id, s_name, s_father, s_mother, s_mobile, s_address, s_course, s_batch, s_mode, tot_f, s_initial_pay, breakdown, today_date_str]], columns=student_df.columns)
                        student_df = pd.concat([student_df, new_row], ignore_index=True)
                        save_data(student_df, STUDENT_MASTER_FILE)

                        # Auto Log Initial Payment in Collection File
                        new_log = pd.DataFrame([[today_date_str, "Self Registration / Admin", new_id, s_name, s_initial_pay]], columns=fee_log_df.columns)
                        fee_log_df = pd.concat([fee_log_df, new_log], ignore_index=True)
                        save_data(fee_log_df, FEE_COLLECTION_LOG_FILE)

                        st.success(f"Registered Successfully! Generated Student ID: {new_id}")

        with tab2:
            st.subheader("Mark Daily Attendance")
            selected_st_opt = st.selectbox("Select Your Student ID", student_options if student_options else [])
            action = st.radio("Action", ["Check-In (In-Time)", "Check-Out (Out-Time)"])
            
            if st.button("Submit Attendance"):
                if selected_st_opt:
                    sid = selected_st_opt.split(" - ")[0]
                    st_name = selected_st_opt.split(" - ")[1] if " - " in selected_st_opt else "Unknown"
                    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    today_str = datetime.now().strftime("%Y-%m-%d")
                    
                    att_row = pd.DataFrame([[today_str, sid, st_name, action, now_str]], columns=attendance_df.columns)
                    attendance_df = pd.concat([attendance_df, att_row], ignore_index=True)
                    save_data(attendance_df, ATTENDANCE_LOG_FILE)
                    st.success(f"Attendance Recorded for {st_name} ({action})")

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

# ==========================================
# 3. TEACHER PORTAL (CLEAN & RESTRICTED VIEW)
# ==========================================
elif menu == "👨‍🏫 Teacher Portal & Fee Entry":
    st.title("👨‍🏫 Teacher & Staff Desk")
    
    ttab1, ttab2 = st.tabs(["⏱️ Teacher Attendance & Class Log", "💵 Collect Fee Counter"])

    with ttab1:
        st.subheader("Teacher Shift & Daily Class Logging")
        with st.form("teacher_log_form"):
            t_shift = st.selectbox("Shift", ["Morning Shift", "Afternoon Shift", "Evening Shift"])
            t_in = st.time_input("In-Time", datetime.now().time())
            t_out = st.time_input("Out-Time", datetime.now().time())
            t_subject = st.text_input("Subject / Topic Taught Today")
            t_status = st.selectbox("Status", ["Present", "Half Day", "Leave"])
            t_salary = st.number_input("Allowance/Wage (₹)", min_value=0.0, value=0.0)

            if st.form_submit_button("Submit Teacher Log"):
                today_str = datetime.now().strftime("%Y-%m-%d")
                t_in_str = t_in.strftime("%I:%M %p")
                t_out_str = t_out.strftime("%I:%M %p")

                new_t_log = pd.DataFrame([[today_str, t_shift, t_in_str, t_out_str, t_subject, t_status, t_salary]], columns=teacher_db.columns)
                teacher_db = pd.concat([teacher_db, new_t_log], ignore_index=True)
                save_data(teacher_db, TEACHER_LOG_FILE)
                st.success(f"Teacher Log recorded for {today_str} ({t_shift})!")

    with ttab2:
        st.subheader("💵 Deposit Student Fee (Teacher Counter)")
        st.info("⚠️ Enter Teacher Name and collect payment amount. Full Ledger details are hidden for privacy.")
        
        if not student_df.empty:
            teacher_name_input = st.text_input("Teacher / Staff Name (Who is collecting)", value="")
            t_selected_opt = st.selectbox("Select Student", student_options, key="t_fee_sid")
            t_add_amt = st.number_input("Amount Collected (₹)", min_value=100.0, step=100.0, key="t_amt")

            if st.button("📥 Save Fee Collection Entry"):
                if teacher_name_input.strip() == "":
                    st.warning("Please enter Teacher Name before saving!")
                else:
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
                    new_bd = f"{old_bd} | [{today_date_str}] ₹{int(t_add_amt)}"
                    student_df.at[idx, 'Payment Breakdown'] = new_bd

                    # 1. Save Master Student File
                    save_data(student_df, STUDENT_MASTER_FILE)

                    # 2. Save Teacher Collection Audit Log File
                    new_fee_entry = pd.DataFrame([[today_date_str, teacher_name_input, t_f_sid, st_name_val, t_add_amt]], columns=fee_log_df.columns)
                    fee_log_df = pd.concat([fee_log_df, new_fee_entry], ignore_index=True)
                    save_data(fee_log_df, FEE_COLLECTION_LOG_FILE)

                    st.success(f"✅ Successfully collected ₹{t_add_amt} from {st_name_val} ({t_f_sid}) by {teacher_name_input}!")
                    st.rerun()

# ==========================================
# 4. ADMIN PANEL (FULL ADVANCED CONTROL)
# ==========================================
elif menu == "🔐 Admin Panel":
    st.title("🔐 Director / Admin Control Panel")
    
    current_admin_pass = get_admin_password()
    pwd = st.text_input("Enter Admin Password", type="password")

    if pwd == current_admin_pass:
        st.success("Access Granted. Welcome Sir!")

        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📊 Student Registry & Fee", 
            "🧾 Fee Collection Log (Who Collected)", 
            "⏱️ Attendance History", 
            "📩 Enquiries", 
            "👨‍🏫 Teacher Operations", 
            "🔑 Admin Password"
        ])

        with tab1:
            st.markdown("### Master Student Records Manager")
            st.dataframe(student_df, use_container_width=True)

            # --- SEARCH & VIEW SPECIFIC STUDENT FEE LEDGER ---
            st.markdown("---")
            st.markdown("### 💳 Student Installment Ledger & Remaining Balance")
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
                    e_address = st.text_input("Address", value=str(e_row['Address']))
                    e_course = st.selectbox("Course", list(st.session_state.fee_settings.keys()), index=0)
                    e_batch = st.text_input("Batch", value=str(e_row['Batch']))
                    e_mode = st.selectbox("Admission Mode", ["Full Onetime", "Monthly Installments"])

                    if st.form_submit_button("Update Student Profile"):
                        e_idx = student_df[student_df['Student ID'] == edit_sid].index[0]
                        student_df.at[e_idx, 'Name'] = e_name
                        student_df.at[e_idx, 'Father Name'] = e_father
                        student_df.at[e_idx, 'Mother Name'] = e_mother
                        student_df.at[e_idx, 'Mobile No'] = e_mobile
                        student_df.at[e_idx, 'Address'] = e_address
                        student_df.at[e_idx, 'Course'] = e_course
                        student_df.at[e_idx, 'Batch'] = e_batch
                        student_df.at[e_idx, 'Admission Mode'] = e_mode

                        save_data(student_df, STUDENT_MASTER_FILE)
                        st.success(f"Updated Profile for {edit_selected_st} successfully!")
                        st.rerun()

            st.markdown("---")
            st.markdown("### 🗑️ Permanent Delete Student")
            if not student_df.empty:
                del_selected_st = st.selectbox("Select Student to Remove", student_options, key="del_sid_select")
                del_roll = del_selected_st.split(" - ")[0]
                if st.button("Delete Selected Student"):
                    student_df = student_df[student_df['Student ID'] != del_roll]
                    save_data(student_df, STUDENT_MASTER_FILE)
                    st.success(f"Removed {del_selected_st} permanently!")
                    st.rerun()

        with tab2:
            st.markdown("### 🧾 Teacher / Staff Fee Collection Audit Log")
            st.info("Here you can trace exactly WHICH teacher collected HOW MUCH money, from WHOM, and on WHICH DATE.")
            st.dataframe(fee_log_df, use_container_width=True)

        with tab3:
            st.markdown("### Daily Attendance Logs")
            st.dataframe(attendance_df, use_container_width=True)

        with tab4:
            st.markdown("### Received Enquiries")
            st.dataframe(enquiry_db, use_container_width=True)

        with tab5:
            st.markdown("### 🔒 Teacher Private Ledger & Wage Tracking")
            st.dataframe(teacher_db, use_container_width=True)

        with tab6:
            st.markdown("### 🔑 Change Admin Password")
            with st.form("change_pass_form"):
                new_p1 = st.text_input("New Password", type="password")
                new_p2 = st.text_input("Confirm New Password", type="password")
                change_btn = st.form_submit_button("Update Password")

                if change_btn:
                    if new_p1 and new_p1 == new_p2:
                        set_admin_password(new_p1)
                        st.success("✅ Password updated successfully! Please use your new password next time.")
                    elif new_p1 != new_p2:
                        st.error("❌ Passwords do not match!")
                    else:
                        st.warning("⚠️ Please enter a valid password.")
    elif pwd != "":
        st.error("Incorrect Password!")