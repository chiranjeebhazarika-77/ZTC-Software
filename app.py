import streamlit as st
import pandas as pd
import os
import datetime
import pytz

# Page Configuration
st.set_page_config(page_title="Soft Tech Computers & ZTC Portal", page_icon="💻", layout="wide")

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
teacher_cols = ["Teacher ID", "Name", "Phone", "Qualification", "Designation", "Shift Assigned"]
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

# Ensure Default Teachers
if teacher_df.empty:
    teacher_df = pd.DataFrame([
        {"Teacher ID": "TCH-01", "Name": "Chiranjeeb Hazarika", "Phone": "9282373221", "Qualification": "Director", "Designation": "Founder & Head", "Shift Assigned": "All"},
        {"Teacher ID": "TCH-02", "Name": "Faculty Teacher 1", "Phone": "9800000000", "Qualification": "MCA", "Designation": "IT Instructor", "Shift Assigned": "Morning"}
    ])
    save_data(teacher_df, TEACHERS_FILE)

# Default Passwords setup
if creds_df.empty:
    creds_df = pd.DataFrame([
        {"Role": "Admin", "Password": "zaan123"},
        {"Role": "Teacher", "Password": "teacher123"}
    ])
    save_data(creds_df, CREDS_FILE)

ADMIN_PWD = creds_df[creds_df["Role"] == "Admin"]["Password"].values[0] if "Admin" in creds_df["Role"].values else "zaan123"
TEACHER_PWD = creds_df[creds_df["Role"] == "Teacher"]["Password"].values[0] if "Teacher" in creds_df["Role"].values else "teacher123"

# Course Fee Structure Reference
COURSE_FEE_MAP = {
    "DCA": "₹4,500", "ADCA": "₹7,500", "DTP": "₹3,500", "Tally Prime": "₹4,000",
    "Class 9 English Coaching": "₹600 / Month", "Class 10 English Coaching": "₹700 / Month",
    "Class 11 English Coaching": "₹800 / Month", "Class 12 English Coaching": "₹900 / Month",
    "Certificate Course": "₹2,500"
}

# Navigation Menu (Parents Live Tracker Removed)
st.sidebar.title("💻 STC & ZTC Portal")
menu = st.sidebar.radio("Navigation Menu:", [
    "🏠 Home & Public Dashboard",
    "📝 New Student Admission",
    "🔑 Student Login Portal",
    "🎯 Sunday Free Practice Class (SFPC)",
    "🔑 Teacher Portal & Fee Counter",
    "🔐 Admin Control Panel"
])

# ---------------------------------------------------------
# 1. HOME & PUBLIC DASHBOARD
# ---------------------------------------------------------
if menu == "🏠 Home & Public Dashboard":
    col_l1, col_l2 = st.columns([1, 4])
    with col_l1:
        st.image("https://raw.githubusercontent.com/zaan-hazarika/ztc-software/main/STC%20LOGO.jpeg", width=140)
    with col_l2:
        st.markdown("""
            <div style="background-color:#1E3A8A; padding:15px; border-radius:12px; color:white;">
                <h1 style="margin:0; font-size:30px;">💻 SOFT TECH COMPUTERS & ZTC</h1>
                <h3 style="margin:2px 0; color:#FBBF24; font-size:16px;">MAKE YOURSELF DIGITAL | AN ISO CERTIFIED INSTITUTE</h3>
                <p style="margin:0; font-size:13px;">Kamarchuburi, Thelamara, Sonitpur, Assam | Center Code: 4159</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_p1, col_p2 = st.columns([1, 2])
    with col_p1:
        st.subheader("📲 Portal Access Scanner")
        st.markdown("""
            <div style="border:2px dashed #2563EB; background-color:#EFF6FF; padding:18px; border-radius:12px; text-align:center;">
                <h3 style="color:#1E3A8A; margin-top:0;">🌐 Scan to Login</h3>
                <p style="color:#475569; font-size:12px;">Direct Student Access QR Code</p>
                <img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://stcztc.streamlit.app" style="width:130px; height:130px;">
                <p style="font-weight:bold; color:#2563EB; margin-top:8px;">stcztc.streamlit.app</p>
            </div>
        """, unsafe_allow_html=True)

    with col_p2:
        st.subheader("📝 Course Fee Enquiry Desk")
        with st.form("pub_enq_form", clear_on_submit=True):
            e_name = st.text_input("Your Full Name*")
            e_mobile = st.text_input("Contact Mobile Number*")
            e_course = st.selectbox("Select Course*", list(COURSE_FEE_MAP.keys()))
            e_addr = st.text_input("Village / Address")
            
            if st.form_submit_button("Submit & View Course Fee"):
                if not e_name or not e_mobile:
                    st.error("Please enter Name and Mobile Number!")
                else:
                    e_row = {"Date": str(datetime.date.today()), "Name": e_name.upper(), "Mobile": e_mobile, "Course Interested": e_course, "Village/Address": e_addr.upper(), "Status": "Enquired"}
                    enquiry_df = pd.concat([enquiry_df, pd.DataFrame([e_row])], ignore_index=True)
                    save_data(enquiry_df, ENQUIRY_FILE)
                    
                    st.markdown("""
                        <div style="background-color:#DCFCE7; border:2px solid #22C55E; padding:15px; border-radius:10px;">
                            <h4 style="color:#15803D; margin:0;">✅ Enquiry Registered Successfully!</h4>
                            <p style="margin:5px 0 0 0;">Estimated Course Fee: <b>{}</b></p>
                        </div>
                    """.format(COURSE_FEE_MAP.get(e_course)), unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. NEW STUDENT ADMISSION
# ---------------------------------------------------------
elif menu == "📝 New Student Admission":
    st.header("📝 New Student Registration Form")
    auth_pwd = st.text_input("Enter Staff / Admin Password to Unlock Form:", type="password")
    
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
                mobile = st.text_input("Mobile Number (Used as Password)*")
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
                total_fee = st.number_input("Total Course Fee (₹)", min_value=0.0, value=2550.0, step=100.0)
                discount = st.number_input("Discount Allowed (₹)", min_value=0.0, step=50.0)
                
            with col4:
                shift = st.selectbox("Shift Assigned", ["Morning (06:30-08:00 AM)", "Afternoon (04:00-05:30 PM)", "Evening (05:30-07:00 PM)"])
                batch_time = st.text_input("Batch Timing", value="90 Minutes Session")
                
            if st.form_submit_button("Submit Admission (Resets Form)"):
                if not name or not mobile:
                    st.error("Please fill in mandatory fields (Name and Mobile)!")
                else:
                    year_code = str(datetime.date.today().year)[2:]
                    existing_ids = [sid for sid in student_df["Student ID"] if str(sid).startswith(f"STC{year_code}-")]
                    next_num = len(existing_ids) + 1
                    new_id = f"STC{year_code}-{next_num:03d}"
                    
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
                    
                    st.markdown("""
                        <div style="background-color:#DCFCE7; border:2px solid #22C55E; padding:15px; border-radius:10px; text-align:center;">
                            <h3 style="color:#15803D; margin:0;">🎉 Student Registered Successfully!</h3>
                            <p style="margin:5px 0 0 0; font-size:16px;">Assigned Roll ID: <b>{}</b> | Password: <b>{}</b></p>
                        </div>
                    """.format(new_id, mobile), unsafe_allow_html=True)
    elif auth_pwd:
        st.error("Incorrect Password!")

# ---------------------------------------------------------
# 3. STUDENT LOGIN PORTAL (PASSWORD = MOBILE NUMBER)
# ---------------------------------------------------------
elif menu == "🔑 Student Login Portal":
    st.header("🔑 Student Individual Dashboard")
    
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        s_id_in = st.text_input("Enter Student Roll ID (e.g., STC26-001):").strip().upper()
    with col_l2:
        s_pwd_in = st.text_input("Enter Student Password (Mobile Number):", type="password").strip()
        
    if s_id_in and s_pwd_in:
        st_data = student_df[(student_df["Student ID"] == s_id_in) & (student_df["Mobile No"] == s_pwd_in)]
        if not st_data.empty:
            s = st_data.iloc[0]
            st.success(f"Welcome, **{s['Name']}**!")
            
            # Financial & Bill Calculations
            net = float(s["Net Fee"]) if s["Net Fee"] else 0.0
            paid_logs = fee_df[fee_df["Student ID"] == s_id_in]
            total_paid = sum([float(amt) for amt in paid_logs["Amount Paid"] if amt])
            due = net - total_paid
            
            # Month calculation for Bill Alert
            j_date = datetime.datetime.strptime(s["Join Date"], "%Y-%m-%d").date() if s["Join Date"] else datetime.date.today()
            months_active = max(1, (datetime.date.today().year - j_date.year) * 12 + datetime.date.today().month - j_date.month)
            expected_bill = 999.0 + (months_active * 550.0) + 999.0  # Admission + Monthly + Exam
            
            paid_percentage = (total_paid / expected_bill * 100) if expected_bill > 0 else 100.0
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Course Enrolled", s["Course"])
            col2.metric("Total Bill Till Date", f"₹{expected_bill:.2f}")
            col3.metric("Total Paid", f"₹{total_paid:.2f}")
            col4.metric("Pending Balance Due", f"₹{due:.2f}")
            
            # 🚨 50% FEE DEFAULTER HIGHLIGHT WARNING
            if paid_percentage < 50.0:
                st.markdown(f"""
                    <div style="background-color:#FEE2E2; border:2px solid #EF4444; padding:15px; border-radius:10px; margin-top:10px;">
                        <h4 style="color:#991B1B; margin:0;">🚨 ATTENTION: FEE PAYMENT OVERDUE WARNING!</h4>
                        <p style="margin:5px 0 0 0; color:#B91C1C;">You have paid only <b>{paid_percentage:.1f}%</b> of your expected bill (₹{expected_bill:.2f}). Please clear at least 50% to maintain active status!</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.success(f"✅ Fee Payment Status Good ({paid_percentage:.1f}% Paid)")

            # 🤖 AI SMART ADVICE FOR STUDENT
            st.markdown("---")
            st.subheader("🤖 AI Smart Guidance Assistant")
            s_att = att_df[att_df["Student ID"] == s_id_in]
            p_days = len(s_att[s_att["Status"] == "Present"])
            
            if p_days > 20 and paid_percentage >= 50.0:
                st.info("💡 **AI Advice:** Excellent Performance! You are maintaining strong attendance and regular fee payments. Keep up the great work!")
            else:
                st.warning("💡 **AI Advice:** Focus on attending all classes regularly and ensure timely monthly installment deposits to qualify for SFPC free lab access.")
                
        else:
            st.error("Invalid Student Roll ID or Password (Mobile Number)!")

# ---------------------------------------------------------
# 4. SUNDAY PRACTICE CLASS (SFPC)
# ---------------------------------------------------------
elif menu == "🎯 Sunday Free Practice Class (SFPC)":
    st.header("🎯 Sunday Free Practice Class (SFPC) Portal")
    
    sfpc_tab1, sfpc_tab2 = st.tabs(["🔍 Check Eligibility", "📝 Log Practice Session"])
    
    with sfpc_tab1:
        check_id = st.text_input("Enter Student Roll ID:").strip().upper()
        if check_id:
            st_res = student_df[student_df["Student ID"] == check_id]
            if not st_res.empty:
                s = st_res.iloc[0]
                p_logs = fee_df[fee_df["Student ID"] == check_id]
                tot_paid = sum([float(a) for a in p_logs["Amount Paid"] if a])
                
                s_att = att_df[att_df["Student ID"] == check_id]
                p_days = len(s_att[s_att["Status"] == "Present"])
                tot_c = len(s_att)
                att_perc = (p_days / tot_c * 100) if tot_c > 0 else 0.0
                
                if att_perc >= 50.0 and tot_paid >= 1500.0:
                    st.success(f"🎉 **{s['Name']}** is ELIGIBLE for SFPC Lab Access!")
                else:
                    st.error(f"❌ Not Eligible! Requires ≥50% Attendance and Fee Clearance.")

    with sfpc_tab2:
        with st.form("sfpc_form", clear_on_submit=True):
            col_sf1, col_sf2 = st.columns(2)
            with col_sf1:
                sf_sid = st.selectbox("Select Student:", student_df["Student ID"] + " - " + student_df["Name"]) if not student_df.empty else None
                sf_date = st.date_input("Practice Date", value=datetime.date.today())
                sf_mc = st.selectbox("Assigned Lab Machine:", [f"Lab PC - {i:02d}" for i in range(1, 21)])
            with col_sf2:
                sf_topic = st.text_input("Topic Practiced")
                sf_teacher = st.selectbox("Instructor Incharge:", teacher_df["Name"].tolist() if not teacher_df.empty else ["Director"])
            
            if st.form_submit_button("Log SFPC Practice Session"):
                sid_code = sf_sid.split(" - ")[0]
                s_name_val = sf_sid.split(" - ")[1]
                sf_row = {"Date": str(sf_date), "Student ID": sid_code, "Student Name": s_name_val, "PC Machine No": sf_mc, "Topic Practiced": sf_topic, "Teacher Incharge": sf_teacher}
                sfpc_df = pd.concat([sfpc_df, pd.DataFrame([sf_row])], ignore_index=True)
                save_data(sfpc_df, SFPC_FILE)
                st.success(f"✅ SFPC Session Logged Successfully!")

# ---------------------------------------------------------
# 5. HIGH-TECH TEACHER PORTAL & EXACT IST TIME PUNCH
# ---------------------------------------------------------
elif menu == "🔑 Teacher Portal & Fee Counter":
    st.header("🔑 High-Tech Faculty Management Portal")
    t_pwd = st.text_input("Enter Teacher Access Password:", type="password")
    
    if t_pwd == TEACHER_PWD:
        st.success("Welcome Faculty Member!")
        
        # EXACT IST TIME PUNCH (Asia/Kolkata)
        now_ist = datetime.datetime.now(IST)
        cur_time_str = now_ist.strftime("%I:%M %p")
        cur_date_str = now_ist.strftime("%Y-%m-%d")
        
        st.markdown(f"""
            <div style="background:#0F172A; color:#38BDF8; padding:15px; border-radius:10px; text-align:center;">
                <h3 style="margin:0;">⏱️ SYSTEM IST TIME PUNCH-IN: {cur_time_str}</h3>
                <p style="margin:0; font-size:12px; color:#94A3B8;">Indian Standard Time (IST) Date: {cur_date_str}</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            t_name_sel = st.selectbox("Select Teacher Name:", teacher_df["Name"].tolist() if not teacher_df.empty else ["Chiranjeeb Hazarika"])
            t_shift = st.selectbox("Select Shift Session:", ["Morning (06:30-08:00 AM)", "Afternoon (04:00-05:30 PM)", "Evening (05:30-07:00 PM)"])
        with col_t2:
            if st.button("Punch Self Attendance Now"):
                t_row = {"Teacher ID": f"TCH-{len(teacher_df)+1:02d}", "Name": t_name_sel, "Shift Assigned": t_shift, "Punch Date": cur_date_str, "In Time": cur_time_str, "Status": "Present"}
                save_data(pd.concat([teacher_df, pd.DataFrame([t_row])], ignore_index=True), TEACHERS_FILE)
                st.markdown("""
                    <div style="background-color:#DCFCE7; border:2px solid #22C55E; padding:12px; border-radius:8px; text-align:center;">
                        <h4 style="color:#15803D; margin:0;">✅ Attendance Punched at {} IST for {}</h4>
                    </div>
                """.format(cur_time_str, t_name_sel), unsafe_allow_html=True)
                
        st.markdown("---")
        
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
                        st.success(f"✅ Receipt Issued: {rc_num}")

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
                    st.success("✅ Class Attendance Recorded!")

# ---------------------------------------------------------
# 6. ADMIN CONTROL PANEL (ADD TEACHERS + EDIT DATA + DEFAULTERS)
# ---------------------------------------------------------
elif menu == "🔐 Admin Control Panel":
    st.header("🔐 Director Admin Control Panel")
    pwd = st.text_input("Enter Director Admin Password", type="password")
    
    if pwd == ADMIN_PWD:
        st.success("Access Granted. Welcome Director Sir!")
        
        adm_tab1, adm_tab2, adm_tab3, adm_tab4, adm_tab5, adm_tab6 = st.tabs([
            "📊 Master Registry & Defaulters",
            "✏️ Edit Student Data & Password",
            "👨‍🏫 Faculty Manager (Add Teacher)",
            "📩 Enquiries Ledger",
            "📋 Attendance Log",
            "🔑 Security & Passwords"
        ])
        
        # TAB 1: MASTER REGISTRY & HIGHLIGHTED DEFAULTERS
        with adm_tab1:
            st.subheader("📊 Master Student Records with 50% Fee Defaulters")
            if not student_df.empty:
                defaulters = []
                for idx, s in student_df.iterrows():
                    sid = s["Student ID"]
                    p_logs = fee_df[fee_df["Student ID"] == sid]
                    tot_paid = sum([float(amt) for amt in p_logs["Amount Paid"] if amt])
                    
                    j_date = datetime.datetime.strptime(s["Join Date"], "%Y-%m-%d").date() if s["Join Date"] else datetime.date.today()
                    m_act = max(1, (datetime.date.today().year - j_date.year) * 12 + datetime.date.today().month - j_date.month)
                    exp_bill = 999.0 + (m_act * 550.0) + 999.0
                    paid_p = (tot_paid / exp_bill * 100) if exp_bill > 0 else 100.0
                    
                    if paid_p < 50.0:
                        defaulters.append({"Student ID": sid, "Name": s["Name"], "Mobile": s["Mobile No"], "Bill (₹)": exp_bill, "Paid (₹)": tot_paid, "Paid %": f"{paid_p:.1f}%"})
                
                if defaulters:
                    st.error("🚨 CRITICAL DEFAULTERS LIST (<50% Paid)")
                    st.table(pd.DataFrame(defaulters))
                
                st.dataframe(student_df, use_container_width=True)

        # TAB 2: EDIT STUDENT DATA & PASSWORDS
        with adm_tab2:
            st.subheader("✏️ Edit Student Profile & Credentials")
            if not student_df.empty:
                edit_sid = st.selectbox("Select Student to Edit:", student_df["Student ID"] + " - " + student_df["Name"])
                if edit_sid:
                    e_id = edit_sid.split(" - ")[0]
                    s_row = student_df[student_df["Student ID"] == e_id].iloc[0]
                    
                    with st.form("edit_st_form"):
                        col_e1, col_e2 = st.columns(2)
                        with col_e1:
                            e_name = st.text_input("Name", value=s_row["Name"])
                            e_mobile = st.text_input("Mobile No (Student Password)", value=s_row["Mobile No"])
                            e_course = st.selectbox("Course", list(COURSE_FEE_MAP.keys()), index=0)
                        with col_e2:
                            e_total_fee = st.text_input("Total Fee", value=s_row["Total Fee"])
                            e_discount = st.text_input("Discount", value=s_row["Discount"])
                            e_status = st.selectbox("Status", ["Active", "Completed", "Dropped"])
                            
                        if st.form_submit_button("Update Student Details"):
                            student_df.loc[student_df["Student ID"] == e_id, "Name"] = e_name.upper()
                            student_df.loc[student_df["Student ID"] == e_id, "Mobile No"] = e_mobile
                            student_df.loc[student_df["Student ID"] == e_id, "Course"] = e_course
                            student_df.loc[student_df["Student ID"] == e_id, "Total Fee"] = e_total_fee
                            student_df.loc[student_df["Student ID"] == e_id, "Discount"] = e_discount
                            student_df.loc[student_df["Student ID"] == e_id, "Net Fee"] = str(float(e_total_fee) - float(e_discount))
                            student_df.loc[student_df["Student ID"] == e_id, "Status"] = e_status
                            
                            save_data(student_df, STUDENT_MASTER_FILE)
                            st.success(f"✅ Updated Profile for {e_id}!")
                            st.rerun()

        # TAB 3: ADD NEW TEACHER / FACULTY
        with adm_tab3:
            st.subheader("👨‍🏫 Add New Faculty / Teacher")
            with st.form("add_tch_form", clear_on_submit=True):
                col_t1, col_t2 = st.columns(2)
                with col_t1:
                    new_t_name = st.text_input("Teacher Name*")
                    new_t_phone = st.text_input("Contact Number*")
                with col_t2:
                    new_t_qual = st.text_input("Qualification")
                    new_t_shift = st.selectbox("Shift Assigned", ["All", "Morning", "Afternoon", "Evening"])
                    
                if st.form_submit_button("Add Teacher"):
                    if new_t_name:
                        t_new_row = {"Teacher ID": f"TCH-{len(teacher_df)+1:02d}", "Name": new_t_name, "Phone": new_t_phone, "Qualification": new_t_qual, "Designation": "Instructor", "Shift Assigned": new_t_shift}
                        teacher_df = pd.concat([teacher_df, pd.DataFrame([t_new_row])], ignore_index=True)
                        save_data(teacher_df, TEACHERS_FILE)
                        st.success(f"✅ Added New Teacher: {new_t_name}")
                        st.rerun()

            st.dataframe(teacher_df, use_container_width=True)

        with adm_tab4:
            st.subheader("📩 Public Enquiries Log")
            st.dataframe(enquiry_df, use_container_width=True)

        with adm_tab5:
            st.subheader("📋 Attendance Log")
            st.dataframe(att_df, use_container_width=True)

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