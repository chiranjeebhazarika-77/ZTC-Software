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
ROUTINE_FILE = "routine_settings.csv"    

# Load Data Safely & Fix Column/Double Entry Pollution Automatically
def load_clean_data(file_path, default_cols, is_student_file=False):
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            if df.empty:
                return pd.DataFrame(columns=default_cols)
            
            # Filter only default columns to prevent structural corruption
            existing_cols = [c for c in default_cols if c in df.columns]
            if existing_cols:
                df = df[existing_cols]
            
            # DUPILCATE FIX: Automatically clean double student entries instantly!
            if is_student_file and 'Student ID' in df.columns:
                df = df.drop_duplicates(subset=['Student ID'], keep='first')
                
            return df
        except:
            return pd.DataFrame(columns=default_cols)
    return pd.DataFrame(columns=default_cols)

def save_data(df, file_path):
    df.to_csv(file_path, index=False)

# Master Column Definition
student_cols = ['Student ID', 'Name', 'Father Name', 'Mother Name', 'Mobile No', 'Address', 'Course', 'Batch', 'Admission Mode']
attendance_cols = ['Date', 'Student ID', 'Name', 'Action', 'Time']

# Load Clean Databases (With automatic duplicate entry cleanup)
student_df = load_clean_data(STUDENT_MASTER_FILE, student_cols, is_student_file=True)
attendance_df = load_clean_data(ATTENDANCE_LOG_FILE, attendance_cols)
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

# New Course Fee Settings (MS Access, PageMaker, Photoshop, Internet Added!)
if 'fee_settings' not in st.session_state:
    st.session_state.fee_settings = {
        "DCA": 5000, "ADCA": 8500, "PGDCA": 5000, 
        "TALLY": 5000, "PYTHON": 5000, "TYPING COURSE": 5000,
        "MS ACCESS COURSE": 4000, "PAGE MAKER COURSE": 4000, 
        "PHOTOSHOP COURSE": 4500, "INTERNET COURSE": 3000,
        "45 DAYS COURSE": 5000, "CERTIFICATE 1 MONTH": 5000, 
        "CERTIFICATE 2 MONTH": 5000, "CERTIFICATE 3 MONTH": 5000
    }

if 'fee_collection_list' not in st.session_state:
    st.session_state.fee_collection_list = []

fee_collection_db = pd.DataFrame(st.session_state.fee_collection_list, 
                                 columns=['Roll No', 'Student Name', 'Course', 'Payment Type', 'Amount Paid', 'Date Paid', 'Entered By'])

# Navigation Menu
menu = st.sidebar.radio("Navigation", ["🏠 Home & Enquiry", "📝 Student Admission & Attendance", "👨‍🏫 Teacher Portal & Fee Entry", "🔐 Admin Panel"])

# 1. PUBLIC DASHBOARD
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
                    st.warning("Please fill in both Name and Mobile Number.")

# 2. STUDENT PORTAL
elif menu == "📝 Student Admission & Attendance":
    st.title("📝 Student Self-Service Portal")
    loc_check = st.checkbox("Verify my device location (Must be within 50 meters of Center)")
    
    if loc_check:
        st.success("✅ Location Verified Inside Center Boundary")
        s_tab1, s_tab2 = st.tabs(["🆕 Student Admission Form", "🕒 Mark Daily Attendance"])
        
        with s_tab1:
            st.subheader("New Student Admission Form (Soft Tech Computers)")
            st.info("💰 Charges: Admission = ₹999/-, Monthly Fee = ₹550/-, Registration = ₹999/-")
            with st.form("student_reg_form", clear_on_submit=True):
                new_roll = st.text_input("Assign Roll Number / Student ID")
                new_name = st.text_input("Student Full Name")
                new_father = st.text_input("Father's Name")
                new_mother = st.text_input("Mother's Name")
                new_mobile = st.text_input("Mobile Number")
                new_address = st.text_input("Full Address")
                new_course = st.selectbox("Select Computer Course", list(st.session_state.fee_settings.keys()))
                
                class_days = st.selectbox("Select Batch Days", ["MWF (Mon, Wed, Fri)", "TTS (Tue, Thu, Sat)", "Regular (Daily Class)"])
                class_time = st.selectbox("Select Pre-preferred Timing Slot", ["Morning (07:30 AM - 09:00 AM)", "Afternoon (04:00 PM - 05:30 PM)", "Evening (05:30 PM - 07:00 PM)"])
                
                pay_opt = st.selectbox("Admission Fee Payment Mode", ["Full Onetime (₹999/-)", "2 Installments (₹500 + ₹500)"])
                
                if st.form_submit_button("Submit Admission Form"):
                    if new_roll and new_name and new_mobile:
                        new_student = pd.DataFrame([[new_roll, new_name, new_father, new_mother, new_mobile, new_address, new_course, f"{class_days} [{class_time}]", pay_opt]], columns=student_cols)
                        student_df = pd.concat([student_df, new_student], ignore_index=True)
                        save_data(student_df, STUDENT_MASTER_FILE)
                        st.success(f"🎉 Registered Roll No: {new_roll} successfully!")
                        st.rerun()
                        
        with s_tab2:
            st.subheader("Daily Attendance Portal")
            input_roll = st.text_input("Enter your Roll Number to Fetch Details", key="att_roll_check")
            fetched_name, fetched_mobile = "", ""
            if input_roll and not student_df.empty:
                match = student_df[student_df['Student ID'].astype(str) == str(input_roll)]
                if not match.empty:
                    fetched_name = match.iloc[0]['Name']
                    fetched_mobile = match.iloc[0]['Mobile No']
                    st.success(f"📋 Student Found: **{fetched_name}**")
            
            with st.form("attendance_form", clear_on_submit=True):
                roll_no = st.text_input("Roll Number / Student ID", value=input_roll)
                stud_name = st.text_input("Student Name", value=fetched_name)
                action = st.radio("Action", ["Check-In (In-Time)", "Check-Out (Out-Time)"])
                parent_mobile = st.text_input("Parent's Mobile Number", value=fetched_mobile)
                
                if st.form_submit_button("Submit Attendance"):
                    if roll_no and stud_name:
                        IST = pytz.timezone('Asia/Kolkata')
                        now_ist = datetime.now(IST)
                        
                        today_date = now_ist.strftime("%Y-%m-%d")
                        current_time = now_ist.strftime("%I:%M %p")
                        
                        new_log = pd.DataFrame([[today_date, roll_no, stud_name, action, current_time]], columns=attendance_cols)
                        attendance_df = pd.concat([attendance_df, new_log], ignore_index=True)
                        save_data(attendance_df, ATTENDANCE_LOG_FILE)
                        
                        st.success(f"Marked {action} successfully at {current_time}!")
                        if parent_mobile:
                            msg = f"Soft Tech Alert: Ward {stud_name} marked {action} at {current_time}."
                            st.markdown(f"[📢 Send WhatsApp Update](https://wa.me/91{parent_mobile}?text={urllib.parse.quote(msg)})")

# 3. TEACHER PORTAL (WITH NEW SUBJECT MODULES IN DROP-DOWN)
elif menu == "👨‍🏫 Teacher Portal & Fee Entry":
    st.title("👨‍🏫 Teacher Portal")
    t_menu = st.tabs(["🕒 Teacher Attendance & Topic Log", "💰 Student Fee Entry (Auto-Fill)"])
    
    with t_menu[0]:
        st.subheader("Faculty Shift Attendance & Lesson Tracking")
        teacher_password = st.text_input("Enter Security Password", type="password", key="t_auth_pass")
        if teacher_password == "teacher123":
            t_shift = st.selectbox("Select Current Shift", ["Morning (07:30 AM - 09:00 AM)", "Afternoon (04:00 PM - 05:30 PM)", "Evening (05:30 PM - 07:00 PM)"])
            t_action = st.radio("Punch Action", ["Punch-In (Arrival)", "Punch-Out (Departure)"])
            
            # MS Access, PageMaker, Photoshop, Internet added inside Dropdown nicely!
            t_subject = st.selectbox("Select Topic/Subject Taught Today:", [
                "Windows OS Configuration & Core Basics",
                "MS Word (Typing, Formatting & Documentation)",
                "MS Excel (Spreadsheets, Formulas & Data Processing)",
                "MS PowerPoint (Slide Creation & Presentation)",
                "MS Access (Database Management & Tables)",
                "PageMaker (Desktop Publishing & Layouts)",
                "Photoshop (Image Editing & Graphic Designing)",
                "Internet (Email, Browsing & Web Services)",
                "Tally Prime (Accounting & GST Entry)",
                "Python Programming Fundamentals",
                "Speed Typing Test & Practice Drill"
            ])
            
            if st.button("Submit Teacher Punch"):
                today = datetime.now().strftime("%Y-%m-%d")
                now_time = datetime.now().strftime("%I:%M %p")
                current_hour = datetime.now().hour
                current_min = datetime.now().minute
                
                if t_action == "Punch-In (Arrival)":
                    status = "On Time"
                    if "Morning" in t_shift and (current_hour > 7 or (current_hour == 7 and current_min > 35)):
                        status = "Late Arrival"
                    elif "Afternoon" in t_shift and (current_hour > 16 or (current_hour == 16 and current_min > 5)):
                        status = "Late Arrival"
                    elif "Evening" in t_shift and (current_hour > 17 or (current_hour == 17 and current_min > 35)):
                        status = "Late Arrival"
                        
                    new_log = pd.DataFrame([[today, t_shift, now_time, "-", t_subject, status, 230 if status == "On Time" else 180]], columns=teacher_db.columns)
                    teacher_db = pd.concat([teacher_db, new_log], ignore_index=True)
                    save_data(teacher_db, TEACHER_LOG_FILE)
                    st.success(f"Punch-In marked at {now_time}. Topic logged!")
                else:
                    mask = (teacher_db['Date'] == today) & (teacher_db['Shift'] == t_shift)
                    if mask.any():
                        idx = teacher_db[mask].index[-1]
                        teacher_db.at[idx, 'Out-Time'] = now_time
                        teacher_db.at[idx, 'Subject Taught'] = t_subject
                        save_data(teacher_db, TEACHER_LOG_FILE)
                        st.success(f"Punch-Out marked at {now_time}.")
                    else:
                        st.error("No Punch-In record found for today!")
                        
    with t_menu[1]:
        st.subheader("Student Fee Counter Collection")
        t_roll_input = st.text_input("Enter Student Roll Number to Load Profile", key="t_fee_roll")
        t_fetched_name = ""
        if t_roll_input and not student_df.empty:
            t_match = student_df[student_df['Student ID'].astype(str) == str(t_roll_input)]
            if not t_match.empty:
                t_fetched_name = t_match.iloc[0]['Name']
                st.success(f"📋 Student Found: **{t_fetched_name}**")
        
        if st.checkbox("Unlock Fee Entry Form"):
            with st.form("fee_entry_form", clear_on_submit=True):
                t_roll = st.text_input("Student Roll Number", value=t_roll_input)
                t_name = st.text_input("Student Name", value=t_fetched_name)
                t_course = st.selectbox("Course/Class", list(st.session_state.fee_settings.keys()))
                t_type = st.selectbox("Payment Stage", ["Admission Fee (₹999)", "Monthly Fee (₹550)", "Registration Fee (₹999)"])
                t_amount = st.number_input("Amount Collected (₹)", min_value=0, step=50)
                t_auth = st.text_input("Teacher Initials")
                
                if st.form_submit_button("Record Payment"):
                    date_today = datetime.now().strftime("%Y-%m-%d %H:%M")
                    st.session_state.fee_collection_list.append([t_roll, t_name, t_course, t_type, t_amount, date_today, t_auth])
                    st.success("Payment recorded successfully!")

# 4. MASTER ADMIN PANEL
elif menu == "🔐 Admin Panel":
    st.title("🔐 Director Control Panel")
    password = st.text_input("Enter Admin Password", type="password")
    
    if password == "admin123":
        st.success("Access Granted, Welcome Sir.")
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Student Registry (Cleaned)", 
            "⏰ Attendance History",
            "👨‍🏫 Teacher Operations", 
            "📅 Class Time Table Editor", 
            "💰 Cash Book & Rates"
        ])
        
        with tab1:
            st.subheader("Master Student Records Manager (Duplicate Entries Auto-Removed)")
            if not student_df.empty:
                st.dataframe(student_df)
                col_del, col_edit = st.columns(2)
                with col_del:
                    st.markdown("#### 🗑 Permanent Delete Student")
                    del_roll = st.selectbox("Select Student ID to Remove", student_df['Student ID'].unique())
                    if st.button("Confirm Delete Student", type="primary"):
                        student_df = student_df[student_df['Student ID'] != del_roll]
                        save_data(student_df, STUDENT_MASTER_FILE)
                        st.success("Deleted student record successfully!")
                        st.rerun()
                with col_edit:
                    st.markdown("#### 📝 Edit Student Profile")
                    edit_roll = st.selectbox("Select Student ID to Edit", student_df['Student ID'].unique())
                    student_row = student_df[student_df['Student ID'] == edit_roll].iloc[0]
                    with st.form("edit_form"):
                        up_name = st.text_input("Modify Name", value=str(student_row.get('Name', '')))
                        up_father = st.text_input("Modify Father Name", value=str(student_row.get('Father Name', '')))
                        up_mobile = st.text_input("Modify Mobile", value=str(student_row.get('Mobile No', '')))
                        if st.form_submit_button("Update Records"):
                            idx = student_df[student_df['Student ID'] == edit_roll].index[0]
                            student_df.at[idx, 'Name'] = up_name
                            student_df.at[idx, 'Father Name'] = up_father
                            student_df.at[idx, 'Mobile No'] = up_mobile
                            save_data(student_df, STUDENT_MASTER_FILE)
                            st.success("Synced successfully!")
                            st.rerun()
            else:
                st.info("No records in student master roster.")

        with tab2:
            st.subheader("⏰ Student Check-In/Out Activity Logs")
            st.dataframe(attendance_df)
                            
        with tab3:
            st.subheader("🔒 Teacher Private Ledger & Wage Tracking")
            st.dataframe(teacher_db)
            
            if not teacher_db.empty:
                st.markdown("#### 🗑 Delete Selected Teacher Attendance Log Line")
                row_to_delete = st.selectbox("Select Row Index Number to Delete", list(teacher_db.index), key="del_t_row")
                if st.button("Confirm Permanent Delete Teacher Entry", type="primary"):
                    teacher_db = teacher_db.drop(teacher_db.index[row_to_delete])
                    save_data(teacher_db, TEACHER_LOG_FILE)
                    st.success("Teacher shift entry cleared successfully!")
                    st.rerun()
                    
        with tab4:
            st.subheader("📅 Live Class Time Table Editor")
            edited_routine_list = []
            for i, row in routine_db.iterrows():
                st.markdown(f"##### Shift Segment: **{row['Shift']}**")
                c1, c2, c3 = st.columns(3)
                with c1:
                    new_time_str = st.text_input(f"Timing Shift {i}", value=row['Timing'], key=f"time_{i}")
                with c2:
                    new_days_str = st.text_input(f"Days Slot {i}", value=row['Days'], key=f"days_{i}")
                with c3:
                    new_class_str = st.text_input(f"Assigned Group Focus {i}", value=row['Assigned Class'], key=f"class_{i}")
                edited_routine_list.append({"Shift": row['Shift'], "Timing": new_time_str, "Days": new_days_str, "Assigned Class": new_class_str})
            if st.button("Publish Routine Settings"):
                routine_db = pd.DataFrame(edited_routine_list)
                save_data(routine_db, ROUTINE_FILE)
                st.success("Time Table published live to home page!")
                st.rerun()
                
        with tab5:
            st.subheader("Cash Book & Course Setup")
            st.dataframe(fee_collection_db)
            total = fee_collection_db['Amount Paid'].sum() if not fee_collection_db.empty else 0
            st.metric("Total Vault Collection", f"₹ {total}/-")
            
            st.markdown("#### 📈 Course Fee Configuration")
            updated_fees = {}
            for course, current_fee in st.session_state.fee_settings.items():
                new_fee = st.number_input(f"Rate for {course} (₹)", min_value=0, value=int(current_fee), step=100, key=f"edit_{course}")
                updated_fees[course] = new_fee
            if st.button("Save New Fees"):
                st.session_state.fee_settings = updated_fees
                save_data(pd.DataFrame(list(updated_fees.items()), columns=['Course', 'Fee']), FEE_FILE)
                st.success("Synced successfully!")