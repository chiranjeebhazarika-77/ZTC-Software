import streamlit as st
import pandas as pd
import os
import datetime

# Page Configuration
st.set_page_config(page_title="Soft Tech Computers & ZTC Portal", page_icon="💻", layout="wide")

# Center Location Credentials (STC Center: Kamarchuburi, Thelamara)
STC_LAT = 26.683389
STC_LON = 92.556680

# Paths for CSV Files
STUDENT_MASTER_FILE = "students_db.csv"
FEE_LOG_FILE = "fees_db.csv"
ATTENDANCE_FILE = "attendance_db.csv"
TEACHERS_FILE = "teachers_db.csv"

# Function to load CSV safely
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

# Function to save CSV
def save_data(df, file_path):
    df.to_csv(file_path, index=False)

# Columns definitions
student_cols = ["Sl. No.", "Student ID", "Name", "Father Name", "Mother Name", "Gender", "DOB", "Caste", "Mobile No", "Vill Town", "PO", "PS", "PIN Code", "District", "Full Address", "Course", "Duration", "Session", "Join Date", "Validity Date", "Total Fee", "Discount", "Net Fee", "Shift", "Batch Time", "Status"]
fee_cols = ["Receipt No", "Student ID", "Date", "Amount Paid", "Payment Mode", "Remarks"]
attendance_cols = ["Student ID", "Date", "Status", "Sign_Mode", "Location_Verified"]
teacher_cols = ["Teacher ID", "Name", "Phone", "Qualification", "Designation", "Shift Assigned", "Shift Start Time"]

# Load DataFrames
student_df = load_data(STUDENT_MASTER_FILE, student_cols)
fee_df = load_data(FEE_LOG_FILE, fee_cols)
att_df = load_data(ATTENDANCE_FILE, attendance_cols)
teacher_df = load_data(TEACHERS_FILE, teacher_cols)

# Navigation Menu
st.sidebar.title("💻 STC & ZTC Portal")
menu = st.sidebar.radio("Navigation Menu:", [
    "🏠 Home & Public Enquiry",
    "📱 Smart QR & Mobile Attendance",
    "📝 New Student Admission",
    "🔑 Student Login Portal",
    "🎯 Sunday Free Practice Class (SFPC)",
    "🔑 Teacher Portal & Fee Counter",
    "👨‍👩‍👧 Parents Live Student Tracker",
    "🔐 Admin Control Panel"
])

# ---------------------------------------------------------
# 1. HOME & PUBLIC ENQUIRY
# ---------------------------------------------------------
if menu == "🏠 Home & Public Enquiry":
    st.title("Welcome to Soft Tech Computers & ZTC")
    st.write("### Quality IT & Academic Education Center (Center Code: 4159)")
    st.info("📍 Location: Kamarchuburi, Thelamara, Sonitpur | Google Geo: 26.683389, 92.556680")
    
    col_h1, col_h2 = st.columns(2)
    with col_h1:
        st.success("⏰ **Morning Shift Revised Timing:** 06:30 AM to 08:00 AM (90 Mins Session)")
    with col_h2:
        st.success("📱 **Smart Mobile QR Scanner & Touch Sign Attendance Active**")

# ---------------------------------------------------------
# 2. SMART QR & MOBILE ATTENDANCE (NEW FEATURE)
# ---------------------------------------------------------
elif menu == "📱 Smart QR & Mobile Attendance":
    st.header("📱 Smart Student QR & Mobile Display Signature Attendance")
    st.write("Scan Notice Board QR code or enter Student ID below to mark daily attendance with Digital Touch Sign.")
    
    col_q1, col_q2 = st.columns([1, 2])
    
    with col_q1:
        st.markdown("""
        <div style="border:2px dashed #1E3A8A; padding:15px; border-radius:10px; text-align:center; background:#EFF6FF;">
            <h4 style="color:#1E3A8A; margin:0;">📍 Notice Board Scanner</h4>
            <p style="font-size:12px; color:#475569;">Verified STC Geo-Location:<br><b>Lat: 26.683389 | Long: 92.556680</b></p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_q2:
        with st.form("student_qr_att_form", clear_on_submit=True):
            s_id_input = st.text_input("Enter Student ID (e.g. STC26-001):").strip().upper()
            touch_sign_name = st.text_input("Digital Touch Signature / Verification Name:")
            loc_check = st.checkbox("Verify Present inside STC/ZTC Campus Location", value=True)
            
            sub_att = st.form_submit_button("Submit Self Attendance")
            
            if sub_att:
                if not s_id_input:
                    st.error("Please enter a valid Student ID!")
                elif s_id_input not in student_df["Student ID"].values:
                    st.error("Student ID not found in Master Registry!")
                else:
                    today_str = str(datetime.date.today())
                    st_name = student_df[student_df["Student ID"] == s_id_input]["Name"].values[0]
                    
                    # Record Attendance
                    att_row = {
                        "Student ID": s_id_input,
                        "Date": today_str,
                        "Status": "Present",
                        "Sign_Mode": "Mobile Signature" if touch_sign_name else "QR Scan",
                        "Location_Verified": "Yes (26.683389, 92.556680)" if loc_check else "Self"
                    }
                    att_df = pd.concat([att_df, pd.DataFrame([att_row])], ignore_index=True)
                    save_data(att_df, ATTENDANCE_FILE)
                    
                    st.balloons()
                    st.success(f"🎉 Attendance Marked Successfully for **{st_name} ({s_id_input})** on {today_str}!")

# ---------------------------------------------------------
# 3. NEW STUDENT ADMISSION (FORM RESET + MEMORY AUTO-FILL)
# ---------------------------------------------------------
elif menu == "📝 New Student Admission":
    st.header("📝 New Student Registration Form")
    st.write("💡 *Memory Auto-Fill Enabled: Previously saved Village, PO, PS and PIN Codes can be quick-selected!*")
    
    # Extract unique memory items from existing student registry
    vills_mem = [v for v in student_df["Vill Town"].unique() if str(v).strip() and str(v) != "nan"]
    pos_mem = [p for p in student_df["PO"].unique() if str(p).strip() and str(p) != "nan"]
    pss_mem = [ps for ps in student_df["PS"].unique() if str(ps).strip() and str(ps) != "nan"]
    pins_mem = [pin for pin in student_df["PIN Code"].unique() if str(pin).strip() and str(pin) != "nan"]

    # Session State Memory Handlers
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        sel_vill_mem = st.selectbox("🧠 Saved Village/Town Memory:", ["-- Type New or Select Saved --"] + vills_mem)
    with col_m2:
        sel_po_mem = st.selectbox("🧠 Saved PO Memory:", ["-- Type New or Select Saved --"] + pos_mem)

    with st.form("admission_form_v2", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Student Name*")
            fname = st.text_input("Father's Name*")
            mname = st.text_input("Mother's Name*")
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            dob = st.date_input("Date of Birth", min_value=datetime.date(1990, 1, 1))
            caste = st.selectbox("Caste", ["General", "OBC / MOBC", "ST", "SC", "Other"])
            mobile = st.text_input("Mobile Number*")
            
        with col2:
            vill_val = sel_vill_mem if sel_vill_mem != "-- Type New or Select Saved --" else ""
            po_val = sel_po_mem if sel_po_mem != "-- Type New or Select Saved --" else ""
            
            vill = st.text_input("Village / Town*", value=vill_val)
            po = st.text_input("Post Office", value=po_val)
            ps = st.text_input("Police Station", value="THELAMARA" if not pss_mem else pss_mem[0])
            pin = st.text_input("PIN Code", value="784149" if not pins_mem else pins_mem[0])
            dist = st.text_input("District", value="Sonitpur")
            
            course = st.selectbox("Course Selected*", ["DCA", "ADCA", "DTP", "Tally Prime", "Certificate Course", "Class 9 English", "Class 10 English", "Class 11 English", "Class 12 English"])
            duration = st.selectbox("Course Duration", ["1 Month", "3 Months", "6 Months", "12 Months"])
            
        col3, col4 = st.columns(2)
        with col3:
            session = st.text_input("Session", value=f"{datetime.date.today().year}-{datetime.date.today().year+1}")
            join_date = st.date_input("Joining Date", value=datetime.date.today())
            total_fee = st.number_input("Total Course Fee (₹)", min_value=0.0, step=100.0)
            discount = st.number_input("Discount Allowed (₹)", min_value=0.0, step=50.0)
            
        with col4:
            shift = st.selectbox("Shift Assigned", ["Morning (06:30 AM - 08:00 AM)", "Afternoon", "Evening"])
            batch_time = st.text_input("Batch Timing", value="06:30 AM - 08:00 AM (90 Mins)")
            
        submitted = st.form_submit_button("Submit & Generate Student ID (Clears Form)")
        
        if submitted:
            if not name or not mobile:
                st.error("Please fill in mandatory fields (Name and Mobile Number)!")
            else:
                year_code = str(datetime.date.today().year)[2:]
                existing_ids = [sid for sid in student_df["Student ID"] if str(sid).startswith(f"STC{year_code}-")]
                next_num = len(existing_ids) + 1
                new_id = f"STC{year_code}-{next_num:03d}"
                
                net_fee = float(total_fee) - float(discount)
                validity = join_date + datetime.timedelta(days=180 if "6" in duration else 365)
                
                new_row = {
                    "Sl. No.": str(len(student_df) + 1),
                    "Student ID": new_id,
                    "Name": name.upper(),
                    "Father Name": fname.upper(),
                    "Mother Name": mname.upper(),
                    "Gender": gender,
                    "DOB": str(dob),
                    "Caste": caste,
                    "Mobile No": mobile,
                    "Vill Town": vill.upper(),
                    "PO": po.upper(),
                    "PS": ps.upper(),
                    "PIN Code": pin,
                    "District": dist.upper(),
                    "Full Address": f"{vill}, {po}, {ps}, {dist} - {pin}".upper(),
                    "Course": course,
                    "Duration": duration,
                    "Session": session,
                    "Join Date": str(join_date),
                    "Validity Date": str(validity),
                    "Total Fee": str(total_fee),
                    "Discount": str(discount),
                    "Net Fee": str(net_fee),
                    "Shift": shift,
                    "Batch Time": batch_time,
                    "Status": "Active"
                }
                
                student_df = pd.concat([student_df, pd.DataFrame([new_row])], ignore_index=True)
                save_data(student_df, STUDENT_MASTER_FILE)
                st.success(f"🎉 Student Registered Successfully! ID Assigned: **{new_id}**. Form Reset Completed!")

# ---------------------------------------------------------
# 4. STUDENT LOGIN PORTAL
# ---------------------------------------------------------
elif menu == "🔑 Student Login Portal":
    st.header("🔑 Student Individual Dashboard")
    search_id = st.text_input("Enter Student ID / Roll Number (e.g., STC26-001):").strip().upper()
    
    if search_id:
        st_data = student_df[student_df["Student ID"] == search_id]
        if not st_data.empty:
            s = st_data.iloc[0]
            st.success(f"Welcome, **{s['Name']}**!")
            
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Course Enrolled", s["Course"])
            col_b.metric("Shift & Batch", f"{s['Shift']} ({s['Batch Time']})")
            
            net = float(s["Net Fee"]) if s["Net Fee"] else 0.0
            paid_logs = fee_df[fee_df["Student ID"] == search_id]
            total_paid = sum([float(amt) for amt in paid_logs["Amount Paid"] if amt])
            due = net - total_paid
            
            col_c.metric("Total Fee Due", f"₹{due:.2f}")
            
            s_att = att_df[att_df["Student ID"] == search_id]
            p_days = len(s_att[s_att["Status"] == "Present"])
            a_days = len(s_att[s_att["Status"] == "Absent"])
            tot_c = p_days + a_days
            perc = (p_days / tot_c * 100) if tot_c > 0 else 0.0
            
            st.write(f"### 📊 Attendance Performance: {p_days}/{tot_c} Days ({perc:.1f}%)")
            st.progress(perc / 100)
        else:
            st.error("No record found for this Student ID.")

# ---------------------------------------------------------
# 5. SUNDAY PRACTICE CLASS
# ---------------------------------------------------------
elif menu == "🎯 Sunday Free Practice Class (SFPC)":
    st.header("🎯 Sunday Free Practice Class Management")

# ---------------------------------------------------------
# 6. TEACHER PORTAL (LATE ARRIVAL ALERT ADDED)
# ---------------------------------------------------------
elif menu == "🔑 Teacher Portal & Fee Counter":
    st.header("💳 Teacher Portal, Fee Counter & Faculty Attendance")
    
    # Teacher Late Arrival Checker
    st.subheader("👨‍🏫 Teacher Punch-in & Late Warning Check")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        t_shift = st.selectbox("Select Teacher Shift:", ["Morning (06:30 AM)", "Afternoon (12:30 PM)", "Evening (03:30 PM)"])
    with col_t2:
        punch_time = st.time_input("Punch-in Time Check:", value=datetime.datetime.now().time())
        
    # Morning shift check (> 06:35 AM is late)
    if "Morning" in t_shift and punch_time > datetime.time(6, 35):
        st.error(f"⚠️ **You are Late!** Morning shift starts at 06:30 AM. Punch-in recorded at {punch_time.strftime('%I:%M %p')}. Please inform Director!")
    elif "Morning" in t_shift:
        st.success(f"✅ On Time Arrival! Morning shift punch-in recorded at {punch_time.strftime('%I:%M %p')}.")

    st.markdown("---")
    tab1, tab2, tab3 = st.tabs(["💵 Deposit Fee", "📅 Daily Attendance Marking", "📋 Batch Bulk Attendance"])
    
    with tab1:
        st.subheader("Collect Fee & Issue Receipt")
        sel_sid = st.selectbox("Select Student for Fee Payment:", student_df["Student ID"] + " - " + student_df["Name"]) if not student_df.empty else None
        
        if sel_sid:
            sid = sel_sid.split(" - ")[0]
            s_rec = student_df[student_df["Student ID"] == sid].iloc[0]
            paid_logs = fee_df[fee_df["Student ID"] == sid]
            total_paid = sum([float(amt) for amt in paid_logs["Amount Paid"] if amt])
            net = float(s_rec["Net Fee"]) if s_rec["Net Fee"] else 0.0
            due = net - total_paid
            
            st.write(f"**Net Course Fee:** ₹{net:.2f} | **Total Paid Till Date:** ₹{total_paid:.2f} | **Current Due:** :red[₹{due:.2f}]")
            
            with st.form("pay_fee_form", clear_on_submit=True):
                pay_amt = st.number_input("Amount to Deposit (₹)", min_value=1.0, max_value=max(due, 10000.0), step=100.0)
                pay_mode = st.selectbox("Payment Mode", ["Cash", "UPI / Google Pay", "Bank Transfer", "Card"])
                remarks = st.text_input("Receipt Remarks / Note", value="Installment Payment")
                
                pay_sub = st.form_submit_button("Process Payment & Issue Receipt")
                if pay_sub:
                    rc_num = f"REC-{datetime.date.today().strftime('%Y%m%d')}-{len(fee_df)+1:03d}"
                    f_row = {
                        "Receipt No": rc_num,
                        "Student ID": sid,
                        "Date": str(datetime.date.today()),
                        "Amount Paid": str(pay_amt),
                        "Payment Mode": pay_mode,
                        "Remarks": remarks
                    }
                    fee_df = pd.concat([fee_df, pd.DataFrame([f_row])], ignore_index=True)
                    save_data(fee_df, FEE_LOG_FILE)
                    st.success(f"✅ Payment Received! Issued Receipt No: **{rc_num}**")

    with tab2:
        st.subheader("Daily Attendance (Single Student)")
        sel_s_att = st.selectbox("Select Student ID:", student_df["Student ID"] + " - " + student_df["Name"], key="att_s") if not student_df.empty else None
        if sel_s_att:
            sid_a = sel_s_att.split(" - ")[0]
            att_date = st.date_input("Attendance Date", value=datetime.date.today())
            att_status = st.radio("Status", ["Present", "Absent"], horizontal=True)
            
            if st.button("Mark Attendance"):
                att_row = {"Student ID": sid_a, "Date": str(att_date), "Status": att_status, "Sign_Mode": "Manual", "Location_Verified": "Manual"}
                att_df = pd.concat([att_df, pd.DataFrame([att_row])], ignore_index=True)
                save_data(att_df, ATTENDANCE_FILE)
                st.success(f"Marked {att_status} for {sid_a} on {att_date}")

    with tab3:
        st.subheader("Batch Wise Bulk Attendance")
        sel_shift = st.selectbox("Filter Shift:", ["All", "Morning (06:30 AM - 08:00 AM)", "Afternoon", "Evening"])
        b_df = student_df if sel_shift == "All" else student_df[student_df["Shift"] == sel_shift]
        
        if not b_df.empty:
            st.write(f"Marking attendance for **{len(b_df)}** students")
            b_date = st.date_input("Bulk Date", value=datetime.date.today(), key="bulk_d")
            
            present_dict = {}
            for idx, row in b_df.iterrows():
                present_dict[row["Student ID"]] = st.checkbox(f"{row['Student ID']} - {row['Name']} ({row['Course']})", value=True)
                
            if st.button("Submit Bulk Attendance"):
                new_att_entries = []
                for st_id, is_p in present_dict.items():
                    status = "Present" if is_p else "Absent"
                    new_att_entries.append({"Student ID": st_id, "Date": str(b_date), "Status": status, "Sign_Mode": "Bulk", "Location_Verified": "Classroom"})
                    
                att_df = pd.concat([att_df, pd.DataFrame(new_att_entries)], ignore_index=True)
                save_data(att_df, ATTENDANCE_FILE)
                st.success("✅ Bulk Attendance Recorded Successfully!")

# ---------------------------------------------------------
# 7. PARENTS LIVE TRACKER
# ---------------------------------------------------------
elif menu == "👨‍👩‍👧 Parents Live Student Tracker":
    st.header("👨‍👩‍👧 Parents Live Performance Tracker")

# ---------------------------------------------------------
# 8. ADMIN CONTROL PANEL
# ---------------------------------------------------------
elif menu == "🔐 Admin Control Panel":
    st.header("🔐 Director Admin Control Panel")
    pwd = st.text_input("Enter Director Admin Password", type="password")
    
    if pwd == "zaan123":
        st.success("Access Granted. Welcome Sir!")
        
        adm_tab1, adm_tab2 = st.tabs([
            "📊 Master Student Registry",
            "⚡ Quick Fee/Attendance Updater"
        ])
        
        with adm_tab1:
            st.subheader("Master Student Records")
            if not student_df.empty:
                disp_df = student_df.copy()
                disp_df["Sl. No."] = range(1, len(disp_df) + 1)
                st.dataframe(disp_df, use_container_width=True)
                
                csv_data = student_df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download Full Student Database (students_db.csv)", data=csv_data, file_name="students_db.csv", mime="text/csv")
                
        with adm_tab2:
            st.subheader("⚡ Direct Bulk Fee & Attendance Overwrite")
            sel_st_up = st.selectbox("Select Student for Overwrite:", student_df["Student ID"] + " - " + student_df["Name"]) if not student_df.empty else None
            
            if sel_st_up:
                sel_id = sel_st_up.split(" - ")[0]
                curr_p = len(att_df[(att_df["Student ID"] == sel_id) & (att_df["Status"] == "Present")])
                curr_a = len(att_df[(att_df["Student ID"] == sel_id) & (att_df["Status"] == "Absent")])
                curr_tot = curr_p + curr_a
                
                st.info(f"Current System Logs — **Total Class:** {curr_tot} Days | **Present:** {curr_p} Days | **Absent:** {curr_a} Days")
                
                col_att1, col_att2 = st.columns(2)
                with col_att1:
                    new_tot_class = st.number_input("Total Class Held Till Date", min_value=0, value=max(curr_tot, 39), step=1)
                with col_att2:
                    new_pres_days = st.number_input("Total Present Days", min_value=0, value=max(curr_p, 27), step=1)
                    
                if st.button("Overwrite & Fix Attendance Record"):
                    if new_pres_days > new_tot_class:
                        st.error("Present days cannot be greater than Total Classes Held!")
                    else:
                        att_df = att_df[att_df["Student ID"] != sel_id]
                        new_recs = []
                        today_s = str(datetime.date.today())
                        
                        for _ in range(int(new_pres_days)):
                            new_recs.append({"Student ID": sel_id, "Date": today_s, "Status": "Present", "Sign_Mode": "Admin Overwrite", "Location_Verified": "Admin"})
                            
                        needed_absent = int(new_tot_class) - int(new_pres_days)
                        for _ in range(needed_absent):
                            new_recs.append({"Student ID": sel_id, "Date": today_s, "Status": "Absent", "Sign_Mode": "Admin Overwrite", "Location_Verified": "Admin"})
                            
                        new_att_df = pd.DataFrame(new_recs)
                        att_df = pd.concat([att_df, new_att_df], ignore_index=True)
                        save_data(att_df, ATTENDANCE_FILE)
                        st.success(f"🎉 Attendance Overwritten! Total: {new_tot_class} Days, Present: {new_pres_days} Days, Absent: {needed_absent} Days.")
                        st.rerun()

    elif pwd:
        st.error("Incorrect Admin Password!")