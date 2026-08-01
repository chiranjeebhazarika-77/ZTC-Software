import streamlit as st
import pandas as pd
import os
import datetime

# Page Configuration
st.set_page_config(page_title="Soft Tech Computers & ZTC Portal", page_icon="💻", layout="wide")

# Paths for CSV Files
STUDENT_MASTER_FILE = "students_db.csv"
FEE_LOG_FILE = "fees_db.csv"
ATTENDANCE_FILE = "attendance_db.csv"
TEACHERS_FILE = "teachers_db.csv"
ENQUIRY_FILE = "enquiries_db.csv"
SFPC_FILE = "sfpc_db.csv"

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
enquiry_cols = ["Date", "Name", "Mobile", "Course Interested", "Village/Address", "Status"]
sfpc_cols = ["Date", "Student ID", "Student Name", "PC Machine No", "Topic Practiced", "Teacher Incharge"]

# Load DataFrames
student_df = load_data(STUDENT_MASTER_FILE, student_cols)
fee_df = load_data(FEE_LOG_FILE, fee_cols)
att_df = load_data(ATTENDANCE_FILE, attendance_cols)
teacher_df = load_data(TEACHERS_FILE, teacher_cols)
enquiry_df = load_data(ENQUIRY_FILE, enquiry_cols)
sfpc_df = load_data(SFPC_FILE, sfpc_cols)

# Standard Course Fee Structure Reference
COURSE_FEE_MAP = {
    "DCA": "₹4,500",
    "ADCA": "₹7,500",
    "DTP": "₹3,500",
    "Tally Prime": "₹4,000",
    "Class 9 English Coaching": "₹600 / Month",
    "Class 10 English Coaching": "₹700 / Month",
    "Class 11 English Coaching": "₹800 / Month",
    "Class 12 English Coaching": "₹900 / Month",
    "Certificate Course": "₹2,500"
}

# Navigation Menu
st.sidebar.title("💻 STC & ZTC Portal")
menu = st.sidebar.radio("Navigation Menu:", [
    "🏠 Public Dashboard & Enquiry",
    "📝 New Student Admission",
    "🔑 Student Login Portal",
    "🎯 Sunday Free Practice Class (SFPC)",
    "🔑 Teacher Portal & Fee Counter",
    "👨‍👩‍👧 Parents Live Student Tracker",
    "🔐 Admin Control Panel"
])

# ---------------------------------------------------------
# 1. PUBLIC DASHBOARD & SMART ENQUIRY DESK
# ---------------------------------------------------------
if menu == "🏠 Public Dashboard & Enquiry":
    # Brand Header Logo Banner
    st.markdown("""
        <div style="background-color:#1E3A8A; padding:22px; border-radius:12px; text-align:center; color:white;">
            <h1 style="margin:0; font-size:34px;">💻 SOFT TECH COMPUTERS & ZTC</h1>
            <p style="margin:5px 0 0 0; font-size:16px;">Kamarchuburi, Thelamara, Sonitpur, Assam | Center Code: 4159</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 🏆 STUDENT OF THE MONTH (AUTOMATIC QUALIFICATION FILTER: Attendance > 75% AND Fee Paid > 50%)
    eligible_students = []
    if not student_df.empty:
        for idx, s in student_df.iterrows():
            sid = s["Student ID"]
            sname = s["Name"]
            net = float(s["Net Fee"]) if s["Net Fee"] else 0.0
            
            # Attendance Calculate
            s_att = att_df[att_df["Student ID"] == sid]
            p_days = len(s_att[s_att["Status"] == "Present"])
            a_days = len(s_att[s_att["Status"] == "Absent"])
            tot_c = p_days + a_days
            att_perc = (p_days / tot_c * 100) if tot_c > 0 else 0.0
            
            # Fee Calculate
            p_logs = fee_df[fee_df["Student ID"] == sid]
            tot_paid = sum([float(amt) for amt in p_logs["Amount Paid"] if amt])
            fee_perc = (tot_paid / net * 100) if net > 0 else 0.0
            
            if att_perc >= 75.0 and fee_perc >= 50.0:
                eligible_students.append(f"{sname} ({s['Course']}) - {att_perc:.0f}% Attd")

    star_text = " | ".join(eligible_students) if eligible_students else "SOFT TECH COMPUTERS & ZTC ACADEMIC EXCELLENCE"
    
    st.markdown(f"""
        <div style="background-color:#FEF3C7; border:1px solid #F59E0B; padding:10px 15px; border-radius:8px;">
            <marquee style="color:#B45309; font-weight:bold; font-size:16px;">
                🏆 STUDENT OF THE MONTH QUALIFIERS (75%+ Attendance & 50%+ Fee Cleared): {star_text} 🏆
            </marquee>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    col_p1, col_p2 = st.columns([1, 2])
    
    with col_p1:
        st.subheader("📲 Portal Access Scanner")
        st.markdown("""
            <div style="border:2px dashed #2563EB; background-color:#EFF6FF; padding:20px; border-radius:12px; text-align:center;">
                <h3 style="color:#1E3A8A; margin-top:0;">🌐 Portal Scanner</h3>
                <p style="color:#475569; font-size:13px;">Scan with Mobile Camera to access Portal</p>
                <div style="font-size:50px;">📱🔗</div>
                <p style="font-weight:bold; color:#2563EB; margin-bottom:0;">stcztc.streamlit.app</p>
            </div>
        """, unsafe_allow_html=True)

    with col_p2:
        st.subheader("📝 Course Fee Enquiry Desk")
        st.write("Enter your details to reveal Course Fee and register your enquiry with Center Admin:")
        
        with st.form("public_enquiry_form", clear_on_submit=False):
            e_name = st.text_input("Your Full Name*")
            e_mobile = st.text_input("Contact Mobile Number*")
            e_course = st.selectbox("Select Interested Course*", list(COURSE_FEE_MAP.keys()))
            e_addr = st.text_input("Village / Address")
            
            e_sub = st.form_submit_button("Submit & View Course Fee")
            
            if e_sub:
                if not e_name or not e_mobile:
                    st.error("Please enter Name and Mobile Number first!")
                else:
                    # Save Enquiry to Admin Database
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
                    
                    st.balloons()
                    st.success(f"🎉 Thank you **{e_name}**! Your enquiry for **{e_course}** is received!")
                    st.info(f"💡 **Estimated Course Fee for {e_course}:** **{COURSE_FEE_MAP.get(e_course, 'Contact Center')}**")

# ---------------------------------------------------------
# 2. NEW STUDENT ADMISSION (PASSWORD PROTECTED & AUTO-RESET)
# ---------------------------------------------------------
elif menu == "📝 New Student Admission":
    st.header("📝 New Student Registration Form")
    
    # Security Lock: Requires Admin or Teacher Password
    st.info("🔒 Security Lock: Entrance to Admission Form requires Staff Authorization.")
    auth_pwd = st.text_input("Enter Admin / Teacher Password to unlock form:", type="password")
    
    if auth_pwd in ["zaan123", "stc4159", "teacher123"]:
        st.success("Authorization Verified! Fill Student Details Below:")
        
        with st.form("admission_form_v3", clear_on_submit=True):
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
                shift = st.selectbox("Shift Assigned", ["Morning", "Afternoon", "Evening"])
                batch_time = st.text_input("Batch Timing", value="As Assigned")
                
            submitted = st.form_submit_button("Submit & Generate Roll ID (Clears Form Automatically)")
            
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
                    st.success(f"🎉 Student Registered Successfully! Assigned Roll ID: **{new_id}**. Form Reset Completed!")
    elif auth_pwd:
        st.error("Incorrect Staff Password! Access Denied.")

# ---------------------------------------------------------
# 3. STUDENT LOGIN PORTAL (FEE PAID & BALANCE DISPLAY)
# ---------------------------------------------------------
elif menu == "🔑 Student Login Portal":
    st.header("🔑 Student Individual Dashboard")
    search_id = st.text_input("Enter Student ID / Roll Number (e.g., STC26-001):").strip().upper()
    
    if search_id:
        st_data = student_df[student_df["Student ID"] == search_id]
        if not st_data.empty:
            s = st_data.iloc[0]
            st.success(f"Welcome, **{s['Name']}**!")
            
            # Calculate Fees
            net = float(s["Net Fee"]) if s["Net Fee"] else 0.0
            paid_logs = fee_df[fee_df["Student ID"] == search_id]
            total_paid = sum([float(amt) for amt in paid_logs["Amount Paid"] if amt])
            due = net - total_paid
            
            col_a, col_b, col_c, col_d = st.columns(4)
            col_a.metric("Course Enrolled", s["Course"])
            col_b.metric("Total Net Fee", f"₹{net:.2f}")
            col_c.metric("Total Fee Paid Till Date", f"₹{total_paid:.2f}")
            col_d.metric("Remaining Fee Balance Due", f"₹{due:.2f}", delta=f"-₹{due:.2f}" if due > 0 else "Cleared", delta_color="inverse")
            
            st.markdown("---")
            
            # Attendance Log
            s_att = att_df[att_df["Student ID"] == search_id]
            p_days = len(s_att[s_att["Status"] == "Present"])
            a_days = len(s_att[s_att["Status"] == "Absent"])
            tot_c = p_days + a_days
            perc = (p_days / tot_c * 100) if tot_c > 0 else 0.0
            
            st.write(f"### 📊 Attendance Performance: {p_days}/{tot_c} Days ({perc:.1f}%)")
            st.progress(perc / 100)
            
            # Receipts Ledger
            st.write("### 🧾 Payment Receipts History")
            if not paid_logs.empty:
                disp_pl = paid_logs.copy()
                disp_pl.index = range(1, len(disp_pl) + 1)
                st.table(disp_pl)
            else:
                st.info("No fee payments recorded yet.")
        else:
            st.error("No record found for this Student ID.")

# ---------------------------------------------------------
# 4. SUNDAY PRACTICE CLASS (SFPC)
# ---------------------------------------------------------
elif menu == "🎯 Sunday Free Practice Class (SFPC)":
    st.header("🎯 Sunday Free Practice Class (SFPC) Portal")
    
    sfpc_tab1, sfpc_tab2 = st.tabs(["🔍 Student Self Practice Search", "📝 Record New SFPC Practice Session"])
    
    with sfpc_tab1:
        st.subheader("Search Student SFPC History & PC Machine Allocation")
        sf_search_id = st.text_input("Enter Student ID (e.g., STC26-001):", key="sf_search").strip().upper()
        if sf_search_id:
            s_sf_logs = sfpc_df[sfpc_df["Student ID"] == sf_search_id]
            if not s_sf_logs.empty:
                st.success(f"Found {len(s_sf_logs)} SFPC practice session records!")
                disp_s_sf = s_sf_logs.copy()
                disp_s_sf.index = range(1, len(disp_s_sf) + 1)
                st.dataframe(disp_s_sf, use_container_width=True)
            else:
                st.info("No Sunday Practice session logged yet for this Student ID.")

    with sfpc_tab2:
        st.subheader("Log Student PC Allocation & Topic")
        with st.form("sfpc_form", clear_on_submit=True):
            col_sf1, col_sf2 = st.columns(2)
            with col_sf1:
                sf_sid = st.selectbox("Select Student:", student_df["Student ID"] + " - " + student_df["Name"]) if not student_df.empty else None
                sf_date = st.date_input("Practice Date", value=datetime.date.today())
                sf_mc = st.selectbox("Assigned PC Lab Machine:", [f"Lab PC - {i:02d}" for i in range(1, 21)])
            with col_sf2:
                sf_topic = st.text_input("Practical Topic (e.g., Tally Prime / MS Word / Typing)")
                sf_teacher = st.text_input("Instructor / Teacher Incharge", value="Center Instructor")
                
            sf_sub = st.form_submit_button("Record SFPC Practice Session")
            if sf_sub and sf_sid:
                sid_code = sf_sid.split(" - ")[0]
                s_name_val = sf_sid.split(" - ")[1]
                sf_row = {
                    "Date": str(sf_date),
                    "Student ID": sid_code,
                    "Student Name": s_name_val,
                    "PC Machine No": sf_mc,
                    "Topic Practiced": sf_topic,
                    "Teacher Incharge": sf_teacher
                }
                sfpc_df = pd.concat([sfpc_df, pd.DataFrame([sf_row])], ignore_index=True)
                save_data(sfpc_df, SFPC_FILE)
                st.success(f"✅ SFPC Session Recorded for {s_name_val} on {sf_mc}!")

# ---------------------------------------------------------
# 5. TEACHER PORTAL & FEE COUNTER
# ---------------------------------------------------------
elif menu == "🔑 Teacher Portal & Fee Counter":
    st.header("💳 Teacher Portal & Fee Payment Counter")
    
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
        sel_shift = st.selectbox("Filter Shift:", ["All", "Morning", "Afternoon", "Evening"])
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
# 6. PARENTS LIVE TRACKER
# ---------------------------------------------------------
elif menu == "👨‍👩‍👧 Parents Live Student Tracker":
    st.header("👨‍👩‍👧 Parents Live Performance Tracker")

# ---------------------------------------------------------
# 7. ADMIN CONTROL PANEL
# ---------------------------------------------------------
elif menu == "🔐 Admin Control Panel":
    st.header("🔐 Director Admin Control Panel")
    pwd = st.text_input("Enter Director Admin Password", type="password")
    
    if pwd == "zaan123":
        st.success("Access Granted. Welcome Director Sir!")
        
        adm_tab1, adm_tab2, adm_tab3, adm_tab4, adm_tab5, adm_tab6 = st.tabs([
            "📊 Master Student Registry",
            "🚨 Smart Overdue Dues",
            "💰 Fee Collection Ledger",
            "👨‍🏫 Faculty Manager",
            "⚡ Quick Fee/Attendance Updater",
            "📩 Public Enquiries Log"
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
            st.subheader("🚨 Overdue Dues & Pending List")
            if not student_df.empty:
                pending_list = []
                total_pending_all = 0.0
                for idx, s in student_df.iterrows():
                    sid = s["Student ID"]
                    sname = s["Name"]
                    net = float(s["Net Fee"]) if s["Net Fee"] else 0.0
                    p_logs = fee_df[fee_df["Student ID"] == sid]
                    tot_paid = sum([float(amt) for amt in p_logs["Amount Paid"] if amt])
                    due = net - tot_paid
                    if due > 0:
                        pending_list.append({"Student ID": sid, "Name": sname, "Course": s["Course"], "Mobile": s["Mobile No"], "Pending Due (₹)": f"{due:.2f}"})
                        total_pending_all += due
                st.error(f"### Total Pending Market Due: ₹{total_pending_all:,.2f}")
                if pending_list:
                    st.table(pd.DataFrame(pending_list))

        with adm_tab3:
            st.subheader("💰 Total Fee Collections Ledger")
            if not fee_df.empty:
                tot_coll = sum([float(a) for a in fee_df["Amount Paid"] if a])
                st.metric("Total Center Fee Collections", f"₹{tot_coll:,.2f}")
                st.dataframe(fee_df, use_container_width=True)

        with adm_tab4:
            st.subheader("👨‍🏫 Faculty Manager")
            st.dataframe(teacher_df, use_container_width=True)

        with adm_tab5:
            st.subheader("⚡ Direct Bulk Fee & Attendance Overwrite")
            sel_st_up = st.selectbox("Select Student for Overwrite:", student_df["Student ID"] + " - " + student_df["Name"]) if not student_df.empty else None
            if sel_st_up:
                sel_id = sel_st_up.split(" - ")[0]
                curr_p = len(att_df[(att_df["Student ID"] == sel_id) & (att_df["Status"] == "Present")])
                curr_a = len(att_df[(att_df["Student ID"] == sel_id) & (att_df["Status"] == "Absent")])
                curr_tot = curr_p + curr_a
                
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
                        st.success(f"🎉 Attendance Overwritten!")
                        st.rerun()

        with adm_tab6:
            st.subheader("📩 Public Enquiries Submitted from Portal")
            if not enquiry_df.empty:
                st.dataframe(enquiry_df, use_container_width=True)

    elif pwd:
        st.error("Incorrect Admin Password!")