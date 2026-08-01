import streamlit as st
import pandas as pd
import os
import datetime
import base64

# Page Configuration
st.set_page_config(page_title="Soft Tech Computers & ZTC Portal", page_icon="💻", layout="wide")

# Paths for CSV Files & Storage
STUDENT_MASTER_FILE = "students_db.csv"
FEE_LOG_FILE = "fees_db.csv"
ATTENDANCE_FILE = "attendance_db.csv"
TEACHERS_FILE = "teachers_db.csv"
ENQUIRY_FILE = "enquiries_db.csv"
SFPC_FILE = "sfpc_db.csv"
CREDS_FILE = "creds_db.csv"
PHOTO_DIR = "student_photos"

if not os.path.exists(PHOTO_DIR):
    os.makedirs(PHOTO_DIR)

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
student_cols = ["Sl. No.", "Student ID", "Name", "Father Name", "Mother Name", "Gender", "DOB", "Caste", "Mobile No", "Vill Town", "PO", "PS", "PIN Code", "District", "Full Address", "Course", "Duration", "Session", "Join Date", "Validity Date", "Total Fee", "Discount", "Net Fee", "Shift", "Batch Time", "Photo Path", "Status"]
fee_cols = ["Receipt No", "Student ID", "Date", "Amount Paid", "Payment Mode", "Remarks"]
attendance_cols = ["Student ID", "Date", "Status", "Sign_Mode", "Location_Verified"]
teacher_cols = ["Teacher ID", "Name", "Phone", "Qualification", "Designation", "Shift Assigned", "Punch Date", "In Time", "Status"]
enquiry_cols = ["Date", "Name", "Mobile", "Course Interested", "Village/Address", "Status"]
sfpc_cols = ["Date", "Student ID", "Student Name", "PC Machine No", "Topic Practiced", "Teacher Incharge"]
creds_cols = ["Role", "Password"]

# Load DataFrames
student_df = load_data(STUDENT_MASTER_FILE, student_cols)
fee_df = load_data(FEE_LOG_FILE, fee_cols)
att_df = load_data(ATTENDANCE_FILE, attendance_cols)
teacher_df = load_data(TEACHERS_FILE, teacher_cols)
enquiry_df = load_data(ENQUIRY_FILE, enquiry_cols)
sfpc_df = load_data(SFPC_FILE, sfpc_cols)
creds_df = load_data(CREDS_FILE, creds_cols)

# Default Passwords setup
if creds_df.empty:
    creds_df = pd.DataFrame([
        {"Role": "Admin", "Password": "zaan123"},
        {"Role": "Teacher", "Password": "teacher123"}
    ])
    save_data(creds_df, CREDS_FILE)

ADMIN_PWD = creds_df[creds_df["Role"] == "Admin"]["Password"].values[0] if "Admin" in creds_df["Role"].values else "zaan123"
TEACHER_PWD = creds_df[creds_df["Role"] == "Teacher"]["Password"].values[0] if "Teacher" in creds_df["Role"].values else "teacher123"

# Course Fee Map
COURSE_FEE_MAP = {
    "DCA": "₹4,500", "ADCA": "₹7,500", "DTP": "₹3,500", "Tally Prime": "₹4,000",
    "Class 9 English Coaching": "₹600 / Month", "Class 10 English Coaching": "₹700 / Month",
    "Class 11 English Coaching": "₹800 / Month", "Class 12 English Coaching": "₹900 / Month",
    "Certificate Course": "₹2,500"
}

# Navigation Menu
st.sidebar.title("💻 STC & ZTC Portal")
menu = st.sidebar.radio("Navigation Menu:", [
    "🏠 Home & Public Dashboard",
    "📝 New Student Admission",
    "🔑 Student Login & Digital ID Card",
    "🎯 Sunday Free Practice Class (SFPC)",
    "🔑 High-Tech Teacher Portal",
    "👨‍👩‍👧 Parents Live Student Tracker",
    "🔐 Admin Control Panel"
])

# ---------------------------------------------------------
# 1. PUBLIC DASHBOARD
# ---------------------------------------------------------
if menu == "🏠 Home & Public Dashboard":
    st.markdown("""
        <div style="background-color:#1E3A8A; padding:22px; border-radius:12px; text-align:center; color:white;">
            <h1 style="margin:0; font-size:32px;">💻 SOFT TECH COMPUTERS & ZTC</h1>
            <h3 style="margin:5px 0; color:#FBBF24; font-size:18px;">AN ISO CERTIFIED INSTITUTE</h3>
            <p style="margin:0; font-size:14px;">Kamarchuburi, Thelamara, Sonitpur, Assam | Center Code: 4159</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_p1, col_p2 = st.columns([1, 2])
    
    with col_p1:
        st.subheader("📲 Official Portal Scanner")
        st.markdown("""
            <div style="border:2px dashed #2563EB; background-color:#EFF6FF; padding:20px; border-radius:12px; text-align:center;">
                <h3 style="color:#1E3A8A; margin-top:0;">🌐 Portal Scanner</h3>
                <p style="color:#475569; font-size:13px;">Scan to open Center Portal on Mobile</p>
                <div style="font-size:50px;">📱🔗</div>
                <p style="font-weight:bold; color:#2563EB; margin-bottom:0;">stcztc.streamlit.app</p>
            </div>
        """, unsafe_allow_html=True)

    with col_p2:
        st.subheader("📝 Smart Course Fee Enquiry Desk")
        st.write("Enter details to reveal course fee structure and submit enquiry:")
        
        with st.form("pub_enq_form", clear_on_submit=True):
            e_name = st.text_input("Your Full Name*")
            e_mobile = st.text_input("Contact Mobile Number*")
            e_course = st.selectbox("Select Course*", list(COURSE_FEE_MAP.keys()))
            e_addr = st.text_input("Village / Address")
            
            e_sub = st.form_submit_button("Submit & Reveal Fee Structure")
            if e_sub:
                if not e_name or not e_mobile:
                    st.error("Please enter Name and Mobile Number!")
                else:
                    e_row = {
                        "Date": str(datetime.date.today()),
                        "Name": e_name.upper(),
                        "Mobile": e_mobile,
                        "Course Interested": e_course,
                        "Village/Address": e_addr.upper(),
                        "Status": "Enquired"
                    }
                    enquiry_df = pd.concat([enquiry_df, pd.DataFrame([e_row])], ignore_index=True)
                    save_data(enquiry_df, ENQUIRY_FILE)
                    
                    st.success(f"🎉 Thank you {e_name}! Course Fee for **{e_course}** is **{COURSE_FEE_MAP.get(e_course)}**")

# ---------------------------------------------------------
# 2. NEW STUDENT ADMISSION (PHOTO UPLOAD + AUTO RESET)
# ---------------------------------------------------------
elif menu == "📝 New Student Admission":
    st.header("📝 New Student Admission Form")
    auth_pwd = st.text_input("Enter Staff / Admin Authorization Password:", type="password")
    
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
                mobile = st.text_input("Mobile Number*")
                photo_file = st.file_uploader("Upload Passport Size Photo (.jpg, .png)*", type=["jpg", "jpeg", "png"])
                
            with col2:
                vill = st.text_input("Village / Town*")
                po = st.text_input("Post Office")
                ps = st.text_input("Police Station", value="THELAMARA")
                pin = st.text_input("PIN Code", value="784149")
                dist = st.text_input("District", value="Sonitpur")
                course = st.selectbox("Course Selected*", list(COURSE_FEE_MAP.keys()))
                duration = st.selectbox("Course Duration", ["1 Month", "3 Months", "6 Months", "12 Months"])
                
            col3, col4 = st.columns(2)
            with col3:
                session = st.text_input("Session", value=f"{datetime.date.today().year}-{datetime.date.today().year+1}")
                join_date = st.date_input("Joining Date", value=datetime.date.today())
                total_fee = st.number_input("Total Course Fee (₹)", min_value=0.0, step=100.0)
                discount = st.number_input("Discount Allowed (₹)", min_value=0.0, step=50.0)
                
            with col4:
                shift = st.selectbox("Shift Assigned", ["Morning (06:30-08:00 AM)", "Afternoon (04:00-05:30 PM)", "Evening (05:30-07:00 PM)"])
                batch_time = st.text_input("Batch Timing", value="90 Minutes Session")
                
            submitted = st.form_submit_button("Submit & Generate Student Roll ID")
            
            if submitted:
                if not name or not mobile:
                    st.error("Please fill in mandatory fields (Name and Mobile)!")
                else:
                    year_code = str(datetime.date.today().year)[2:]
                    existing_ids = [sid for sid in student_df["Student ID"] if str(sid).startswith(f"STC{year_code}-")]
                    next_num = len(existing_ids) + 1
                    new_id = f"STC{year_code}-{next_num:03d}"
                    
                    # Save Photo
                    photo_path = ""
                    if photo_file is not None:
                        photo_path = os.path.join(PHOTO_DIR, f"{new_id}.png")
                        with open(photo_path, "wb") as f:
                            f.write(photo_file.getbuffer())
                            
                    net_fee = float(total_fee) - float(discount)
                    validity = join_date + datetime.timedelta(days=180 if "6" in duration else 365)
                    
                    new_row = {
                        "Sl. No.": str(len(student_df) + 1), "Student ID": new_id, "Name": name.upper(),
                        "Father Name": fname.upper(), "Mother Name": mname.upper(), "Gender": gender,
                        "DOB": str(dob), "Caste": caste, "Mobile No": mobile, "Vill Town": vill.upper(),
                        "PO": po.upper(), "PS": ps.upper(), "PIN Code": pin, "District": dist.upper(),
                        "Full Address": f"{vill}, {po}, {ps}, {dist} - {pin}".upper(), "Course": course,
                        "Duration": duration, "Session": session, "Join Date": str(join_date),
                        "Validity Date": str(validity), "Total Fee": str(total_fee), "Discount": str(discount),
                        "Net Fee": str(net_fee), "Shift": shift, "Batch Time": batch_time,
                        "Photo Path": photo_path, "Status": "Active"
                    }
                    student_df = pd.concat([student_df, pd.DataFrame([new_row])], ignore_index=True)
                    save_data(student_df, STUDENT_MASTER_FILE)
                    st.success(f"🎉 Student Registered Successfully! Assigned Roll ID: **{new_id}**. Form Reset Completed!")
    elif auth_pwd:
        st.error("Incorrect Password!")

# ---------------------------------------------------------
# 3. STUDENT LOGIN & DIGITAL ID CARD
# ---------------------------------------------------------
elif menu == "🔑 Student Login & Digital ID Card":
    st.header("🔑 Student Individual Dashboard & Digital ID Card")
    search_id = st.text_input("Enter Student Roll ID (e.g., STC26-001):").strip().upper()
    
    if search_id:
        st_data = student_df[student_df["Student ID"] == search_id]
        if not st_data.empty:
            s = st_data.iloc[0]
            st.success(f"Welcome, **{s['Name']}**!")
            
            # Financial Ledger
            net = float(s["Net Fee"]) if s["Net Fee"] else 0.0
            paid_logs = fee_df[fee_df["Student ID"] == search_id]
            total_paid = sum([float(amt) for amt in paid_logs["Amount Paid"] if amt])
            due = net - total_paid
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Course Enrolled", s["Course"])
            col2.metric("Total Net Fee", f"₹{net:.2f}")
            col3.metric("Total Paid Till Date", f"₹{total_paid:.2f}")
            col4.metric("Remaining Due Balance", f"₹{due:.2f}", delta=f"-₹{due:.2f}" if due > 0 else "Cleared", delta_color="inverse")
            
            st.markdown("---")
            
            # DIGITAL ID CARD RENDERING
            st.subheader("💳 Official Student Digital ID Card")
            
            photo_p = s["Photo Path"] if s["Photo Path"] and os.path.exists(s["Photo Path"]) else None
            
            id_col1, id_col2 = st.columns([1, 2])
            with id_col1:
                if photo_p:
                    st.image(photo_p, caption=s["Name"], width=160)
                else:
                    st.info("👤 No Photo Uploaded")
            with id_col2:
                st.markdown(f"""
                <div style="border:3px solid #1E3A8A; border-radius:12px; padding:15px; background:#F8FAFC;">
                    <h3 style="color:#1E3A8A; margin:0;">SOFT TECH COMPUTERS & ZTC</h3>
                    <p style="margin:0; font-size:12px; color:#D97706; font-weight:bold;">AN ISO CERTIFIED INSTITUTE</p>
                    <hr style="margin:8px 0;">
                    <p style="margin:3px 0;"><b>Name:</b> {s['Name']}</p>
                    <p style="margin:3px 0;"><b>Roll ID:</b> <span style="color:#2563EB; font-weight:bold;">{s['Student ID']}</span></p>
                    <p style="margin:3px 0;"><b>Course:</b> {s['Course']}</p>
                    <p style="margin:3px 0;"><b>Father's Name:</b> {s['Father Name']}</p>
                    <p style="margin:3px 0;"><b>Shift:</b> {s['Shift']}</p>
                    <div style="background:#E2E8F0; padding:5px; border-radius:5px; margin-top:8px; text-align:center; font-family:monospace; letter-spacing:3px;">
                        ||||||| {s['Student ID']} |||||||
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
        else:
            st.error("No student record found for this Roll ID.")

# ---------------------------------------------------------
# 4. SUNDAY PRACTICE CLASS (SFPC - STRICT ELIGIBILITY)
# ---------------------------------------------------------
elif menu == "🎯 Sunday Free Practice Class (SFPC)":
    st.header("🎯 Sunday Free Practice Class (SFPC) Portal")
    st.info("📌 **SFPC Rules:** Student must have **≥75% Attendance** AND **≥50% Fee Paid** to qualify for free Sunday Lab practice!")
    
    sfpc_tab1, sfpc_tab2 = st.tabs(["🔍 Check Eligibility & History", "📝 Log SFPC Session"])
    
    with sfpc_tab1:
        check_id = st.text_input("Enter Student Roll ID (e.g. STC26-001):").strip().upper()
        if check_id:
            st_res = student_df[student_df["Student ID"] == check_id]
            if not st_res.empty:
                s = st_res.iloc[0]
                net = float(s["Net Fee"]) if s["Net Fee"] else 0.0
                
                # Attd Check
                s_att = att_df[att_df["Student ID"] == check_id]
                p_days = len(s_att[s_att["Status"] == "Present"])
                a_days = len(s_att[s_att["Status"] == "Absent"])
                tot_c = p_days + a_days
                att_perc = (p_days / tot_c * 100) if tot_c > 0 else 0.0
                
                # Fee Check
                p_logs = fee_df[fee_df["Student ID"] == check_id]
                tot_paid = sum([float(a) for a in p_logs["Amount Paid"] if a])
                fee_perc = (tot_paid / net * 100) if net > 0 else 0.0
                
                if att_perc >= 75.0 and fee_perc >= 50.0:
                    st.balloons()
                    st.success(f"🎉 **{s['Name']}** is **ELIGIBLE** for SFPC! (Attd: {att_perc:.1f}%, Fee Paid: {fee_perc:.1f}%)")
                else:
                    st.error(f"❌ **Not Eligible!** Required: ≥75% Attd & ≥50% Fee. Current -> Attd: {att_perc:.1f}%, Fee Paid: {fee_perc:.1f}%")
            else:
                st.error("Student ID Not Found!")

    with sfpc_tab2:
        with st.form("sfpc_form", clear_on_submit=True):
            col_sf1, col_sf2 = st.columns(2)
            with col_sf1:
                sf_sid = st.selectbox("Select Student:", student_df["Student ID"] + " - " + student_df["Name"]) if not student_df.empty else None
                sf_date = st.date_input("Practice Date", value=datetime.date.today())
                sf_mc = st.selectbox("Assigned Lab Machine:", [f"Lab PC - {i:02d}" for i in range(1, 21)])
            with col_sf2:
                sf_topic = st.text_input("Topic Practiced (e.g. Tally / Word)")
                sf_teacher = st.text_input("Instructor Incharge", value="Center Instructor")
            sf_sub = st.form_submit_button("Log SFPC Practice Session")
            if sf_sub and sf_sid:
                sid_code = sf_sid.split(" - ")[0]
                s_name_val = sf_sid.split(" - ")[1]
                sf_row = {"Date": str(sf_date), "Student ID": sid_code, "Student Name": s_name_val, "PC Machine No": sf_mc, "Topic Practiced": sf_topic, "Teacher Incharge": sf_teacher}
                sfpc_df = pd.concat([sfpc_df, pd.DataFrame([sf_row])], ignore_index=True)
                save_data(sfpc_df, SFPC_FILE)
                st.success(f"Logged SFPC for {s_name_val} on {sf_mc}")

# ---------------------------------------------------------
# 5. HIGH-TECH TEACHER PORTAL & AUTO IST TIME PUNCH
# ---------------------------------------------------------
elif menu == "🔑 High-Tech Teacher Portal":
    st.header("🔑 High-Tech Faculty Management Portal")
    t_pwd = st.text_input("Enter Teacher Access Password:", type="password")
    
    if t_pwd == TEACHER_PWD:
        st.success("Welcome Faculty Member!")
        
        # Automatic IST Time Punch-in
        now_ist = datetime.datetime.now()
        cur_time_str = now_ist.strftime("%I:%M %p")
        cur_date_str = str(datetime.date.today())
        
        st.markdown(f"""
            <div style="background:#0F172A; color:#38BDF8; padding:15px; border-radius:10px; text-align:center;">
                <h3 style="margin:0;">⏱️ SYSTEM IST TIME PUNCH-IN: {cur_time_str}</h3>
                <p style="margin:0; font-size:12px; color:#94A3B8;">System Date: {cur_date_str} | Geolocation: STC Campus</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            t_name = st.text_input("Teacher / Faculty Name:")
            t_shift = st.selectbox("Select Current Shift Session:", ["Morning (06:30-08:00 AM)", "Afternoon (04:00-05:30 PM)", "Evening (05:30-07:00 PM)"])
        with col_t2:
            if st.button("Punch Self Attendance Now"):
                if not t_name:
                    st.error("Please enter Teacher Name!")
                else:
                    t_row = {"Teacher ID": f"TCH-{len(teacher_df)+1:02d}", "Name": t_name, "Phone": "", "Qualification": "Faculty", "Designation": "Instructor", "Shift Assigned": t_shift, "Punch Date": cur_date_str, "In Time": cur_time_str, "Status": "Present"}
                    teacher_df = pd.concat([teacher_df, pd.DataFrame([t_row])], ignore_index=True)
                    save_data(teacher_df, TEACHERS_FILE)
                    st.success(f"🎉 Attendance Punched at {cur_time_str} for {t_name}!")
                    
        st.markdown("---")
        
        # Counter & Attendance Options
        tab1, tab2 = st.tabs(["💵 Collect Fee & Issue Receipt", "📋 Batch Bulk Attendance"])
        
        with tab1:
            sel_sid = st.selectbox("Select Student:", student_df["Student ID"] + " - " + student_df["Name"]) if not student_df.empty else None
            if sel_sid:
                sid = sel_sid.split(" - ")[0]
                s_rec = student_df[student_df["Student ID"] == sid].iloc[0]
                paid_logs = fee_df[fee_df["Student ID"] == sid]
                total_paid = sum([float(amt) for amt in paid_logs["Amount Paid"] if amt])
                net = float(s_rec["Net Fee"]) if s_rec["Net Fee"] else 0.0
                due = net - total_paid
                
                st.write(f"**Net Fee:** ₹{net:.2f} | **Total Paid:** ₹{total_paid:.2f} | **Due Balance:** :red[₹{due:.2f}]")
                with st.form("teacher_pay_form", clear_on_submit=True):
                    pay_amt = st.number_input("Deposit Amount (₹)", min_value=1.0, max_value=max(due, 10000.0), step=100.0)
                    pay_mode = st.selectbox("Mode", ["Cash", "UPI / Google Pay", "Bank Transfer"])
                    remarks = st.text_input("Remarks", value="Collected at Counter")
                    if st.form_submit_button("Issue Receipt"):
                        rc_num = f"REC-{datetime.date.today().strftime('%Y%m%d')}-{len(fee_df)+1:03d}"
                        f_row = {"Receipt No": rc_num, "Student ID": sid, "Date": str(datetime.date.today()), "Amount Paid": str(pay_amt), "Payment Mode": pay_mode, "Remarks": remarks}
                        fee_df = pd.concat([fee_df, pd.DataFrame([f_row])], ignore_index=True)
                        save_data(fee_df, FEE_LOG_FILE)
                        st.success(f"Receipt Issued: {rc_num}")

        with tab2:
            sel_shift = st.selectbox("Shift Filter:", ["All", "Morning (06:30-08:00 AM)", "Afternoon (04:00-05:30 PM)", "Evening (05:30-07:00 PM)"])
            b_df = student_df if sel_shift == "All" else student_df[student_df["Shift"] == sel_shift]
            if not b_df.empty:
                b_date = st.date_input("Date", value=datetime.date.today())
                present_dict = {}
                for idx, row in b_df.iterrows():
                    present_dict[row["Student ID"]] = st.checkbox(f"{row['Student ID']} - {row['Name']}", value=True)
                if st.button("Submit Class Attendance"):
                    new_entries = []
                    for st_id, is_p in present_dict.items():
                        new_entries.append({"Student ID": st_id, "Date": str(b_date), "Status": "Present" if is_p else "Absent", "Sign_Mode": "Classroom", "Location_Verified": "Campus"})
                    att_df = pd.concat([att_df, pd.DataFrame(new_entries)], ignore_index=True)
                    save_data(att_df, ATTENDANCE_FILE)
                    st.success("Attendance Recorded!")

    elif t_pwd:
        st.error("Incorrect Teacher Password!")

# ---------------------------------------------------------
# 6. PARENTS LIVE TRACKER
# ---------------------------------------------------------
elif menu == "👨‍👩‍👧 Parents Live Student Tracker":
    st.header("👨‍👩‍👧 Parents Live Performance Tracker")

# ---------------------------------------------------------
# 7. ADMIN CONTROL PANEL (EDIT STUDENT + PASSWORD CHANGE)
# ---------------------------------------------------------
elif menu == "🔐 Admin Control Panel":
    st.header("🔐 Director Admin Control Panel")
    pwd = st.text_input("Enter Director Admin Password", type="password")
    
    if pwd == ADMIN_PWD:
        st.success("Access Granted. Welcome Director Sir!")
        
        adm_tab1, adm_tab2, adm_tab3, adm_tab4, adm_tab5, adm_tab6 = st.tabs([
            "📊 Master Student Registry",
            "✏️ Edit Student Data",
            "📩 Public Enquiries Log",
            "📋 Full Attendance Records",
            "💰 Fee Collection Ledger",
            "🔑 Security & Password Change"
        ])
        
        with adm_tab1:
            st.dataframe(student_df, use_container_width=True)
            csv_data = student_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Database CSV", data=csv_data, file_name="students_db.csv")

        # EDIT STUDENT DATA
        with adm_tab2:
            st.subheader("✏️ Edit Student Information")
            if not student_df.empty:
                edit_sid = st.selectbox("Select Student to Edit:", student_df["Student ID"] + " - " + student_df["Name"])
                if edit_sid:
                    e_id = edit_sid.split(" - ")[0]
                    s_row = student_df[student_df["Student ID"] == e_id].iloc[0]
                    
                    with st.form("edit_st_form"):
                        col_e1, col_e2 = st.columns(2)
                        with col_e1:
                            e_name = st.text_input("Name", value=s_row["Name"])
                            e_mobile = st.text_input("Mobile No", value=s_row["Mobile No"])
                            e_course = st.selectbox("Course", list(COURSE_FEE_MAP.keys()), index=0)
                        with col_e2:
                            e_total_fee = st.text_input("Total Fee", value=s_row["Total Fee"])
                            e_discount = st.text_input("Discount", value=s_row["Discount"])
                            e_status = st.selectbox("Status", ["Active", "Completed", "Dropped"])
                            
                        if st.form_submit_button("Update Student Record"):
                            student_df.loc[student_df["Student ID"] == e_id, "Name"] = e_name.upper()
                            student_df.loc[student_df["Student ID"] == e_id, "Mobile No"] = e_mobile
                            student_df.loc[student_df["Student ID"] == e_id, "Course"] = e_course
                            student_df.loc[student_df["Student ID"] == e_id, "Total Fee"] = e_total_fee
                            student_df.loc[student_df["Student ID"] == e_id, "Discount"] = e_discount
                            student_df.loc[student_df["Student ID"] == e_id, "Net Fee"] = str(float(e_total_fee) - float(e_discount))
                            student_df.loc[student_df["Student ID"] == e_id, "Status"] = e_status
                            
                            save_data(student_df, STUDENT_MASTER_FILE)
                            st.success(f"Updated record for {e_id}!")
                            st.rerun()

        with adm_tab3:
            st.subheader("📩 Public Course Enquiries")
            st.dataframe(enquiry_df, use_container_width=True)

        with adm_tab4:
            st.subheader("📋 Complete Student & Teacher Attendance Log")
            st.dataframe(att_df, use_container_width=True)

        with adm_tab5:
            st.subheader("💰 Fee Collection Ledger")
            st.dataframe(fee_df, use_container_width=True)

        # CHANGE PASSWORDS
        with adm_tab6:
            st.subheader("🔑 Change Portal Passwords")
            new_admin_p = st.text_input("New Admin Password:", value=ADMIN_PWD)
            new_teach_p = st.text_input("New Teacher Password:", value=TEACHER_PWD)
            
            if st.button("Save New Passwords"):
                new_creds = pd.DataFrame([
                    {"Role": "Admin", "Password": new_admin_p},
                    {"Role": "Teacher", "Password": new_teach_p}
                ])
                save_data(new_creds, CREDS_FILE)
                st.success("🎉 Passwords Updated Successfully!")

    elif pwd:
        st.error("Incorrect Admin Password!")