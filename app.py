import streamlit as st
import pandas as pd
import datetime
import pytz
import base64
import db

st.set_page_config(
    page_title="Soft Tech Computers & ZTC Enterprise",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

IST = pytz.timezone('Asia/Kolkata')

# Columns definitions
student_cols = [
    "Sl. No.", "Student ID", "Name", "Father Name", "Mother Name", "Gender", "DOB", "Mobile No", 
    "Vill Town", "District", "Course", "Duration", "Days_Batch", "Session", "Join Date", "Validity Date", 
    "Total Fee", "Discount", "Net Fee", "Shift", "Status", "HO_Reg_No", "Stage_AdmitCard", "Stage_Cert_Status", "Cert_Serial_No"
]
fee_cols = ["Receipt No", "Student ID", "Date", "Amount Paid", "Payment Mode", "Collected_By", "Remarks"]
attendance_cols = ["Student ID", "Date", "Time_In", "Status"]
teacher_cols = ["Teacher ID", "Name", "Phone", "Designation", "Shift Assigned"]

# Fetch sanitized data from db engine
student_df = db.get_table("students_db.csv", "students_db", student_cols)
fee_df = db.get_table("fees_db.csv", "fees_db", fee_cols)
att_df = db.get_table("attendance_db.csv", "attendance_db", attendance_cols)
teacher_df = db.get_table("teachers_db.csv", "teachers_db", teacher_cols)

# Filter orphan fees automatically
valid_sids = set(student_df["Student ID"].dropna().astype(str).str.strip()) if not student_df.empty else set()
if not fee_df.empty:
    fee_df = fee_df[fee_df["Student ID"].astype(str).str.strip().isin(valid_sids)]

# Modern Slate-Navy Dark Theme CSS
st.markdown("""
<style>
.stApp { background-color: #0B1120; color: #E2E8F0; font-family: 'Segoe UI', Tahoma, sans-serif; }
.top-navbar { background-color: #0F172A; border-bottom: 1px solid #1E293B; padding: 12px 20px; display: flex; justify-content: space-between; align-items: center; margin-top: -60px; margin-left: -4rem; margin-right: -4rem; margin-bottom: 20px; }
.hero-wrapper { background: #0F172A; border: 1px solid #1E293B; border-radius: 14px; padding: 22px 26px; margin-bottom: 20px; }
.hero-tag-pill { background: rgba(249, 115, 22, 0.12); border: 1px solid #FB923C; color: #FB923C; font-size: 11px; font-weight: 700; padding: 4px 12px; border-radius: 20px; display: inline-block; margin-bottom: 10px; }
.hero-main-title { font-size: 28px; font-weight: 900; color: #FFFFFF; margin: 0 0 8px 0; }
.pill-item { font-size: 11px; font-weight: 700; padding: 5px 12px; border-radius: 6px; display: inline-flex; margin-right: 6px; margin-top: 6px; }
.pill-orange { background: #EA580C; color: white; }
.pill-green { background: #059669; color: white; }
.pill-blue { background: #2563EB; color: white; }
.portal-card { background: #0F172A; border: 1px solid #1E293B; border-radius: 12px; padding: 18px; margin-bottom: 16px; }
div.stButton > button { background-color: #10B981 !important; color: white !important; border-radius: 6px !important; font-weight: 700 !important; border: none !important; }
div.stButton > button:hover { background-color: #059669 !important; }
div[data-testid="stMetric"] { background: #0F172A; border: 1px solid #1E293B; padding: 12px; border-radius: 10px; }
div[data-testid="stMetricValue"] { color: #38BDF8 !important; font-weight: 800 !important; }

/* Printable ID Card & Passbook */
.id-card-container { width: 350px; background: #FFFFFF; border-radius: 12px; overflow: hidden; border: 2px solid #0284C7; margin: 15px auto; color: #0F172A; }
.id-card-header { background: #0F172A; color: white; padding: 12px; text-align: center; border-bottom: 3px solid #38BDF8; }
.passbook-card { background: #FFFFFF; border: 2px solid #334155; border-radius: 8px; padding: 16px; max-width: 700px; margin: 15px auto; color: #0F172A; }
.passbook-table { width: 100%; border-collapse: collapse; font-size: 12px; margin-top: 10px; }
.passbook-table th, .passbook-table td { border: 1px solid #CBD5E1; padding: 6px; text-align: center; }
.passbook-table th { background: #F1F5F9; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# Top Bar
st.markdown("""
<div class="top-navbar">
    <div style="display:flex; align-items:center; gap:10px;">
        <span style="background:#10B981; color:white; font-weight:900; padding:4px 10px; border-radius:8px;">STC</span>
        <b style="font-size:16px; color:#F8FAFC;">Soft Tech Computers & ZTC Enterprise</b>
    </div>
    <span style="font-size:12px; color:#94A3B8;">Code: <b>4159 (Kamarchuburi, Sonitpur)</b> | Academic Session: 2026-27</span>
</div>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.title("💻 Portal Navigation")
if st.sidebar.button("🔄 Sync & Reload Data", use_container_width=True):
    st.cache_data.clear()
    st.sidebar.success("Refreshed from Google Sheet!")
    st.rerun()

menu = st.sidebar.radio("Select Module:", [
    "⚡ Dashboard Overview",
    "📝 New Student Admission",
    "💵 Fee Counter Desk",
    "🪪 ID Card & Passbook Desk",
    "📸 Student Attendance",
    "🔐 Director Admin Panel"
])

# 1. DASHBOARD
if menu == "⚡ Dashboard Overview":
    st.markdown("""
    <div class="hero-wrapper">
        <div class="hero-tag-pill">🛡️ GOVT REGD IT ACADEMY • SONITPUR, ASSAM</div>
        <h1 class="hero-main-title">Soft Tech Computers & ZTC Enterprise</h1>
        <p style="color:#94A3B8; font-size:13.5px; line-height:1.6; margin:0 0 10px 0;">
            An accredited institution under Center Code <b style="color:#FB923C;">4159</b> providing ISO 9001:2015 certified technical computer courses with Sarva India nationwide accreditation.
        </p>
        <div>
            <span class="pill-item pill-orange"># CENTER CODE: 4159</span>
            <span class="pill-item pill-green">✓ System Online</span>
            <span class="pill-item pill-blue">🏛️ ISO 9001:2015</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Enrolled Trainees", f"{len(student_df)} Active")
    tot_coll = sum([float(a) for a in fee_df["Amount Paid"] if a]) if not fee_df.empty else 0.0
    c2.metric("Total Fee Collected", f"₹{tot_coll:,.2f}")
    c3.metric("Center Status", "Operational (Code: 4159)")
    
    st.markdown("---")
    st.subheader("📋 Enrolled Candidates Quick Directory")
    if not student_df.empty:
        st.dataframe(student_df[["Student ID", "Name", "Course", "Mobile No", "Net Fee", "Status"]], use_container_width=True)
    else:
        st.info("No candidates registered yet.")

# 2. ADMISSION
elif menu == "📝 New Student Admission":
    st.subheader("📝 New Candidate Admission Data Capture Format")
    year_code = str(datetime.date.today().year)[2:]
    next_id = f"STC{year_code}-{len(student_df)+1:03d}"
    st.info(f"⚡ **Auto-Generated Roll ID:** `{next_id}`")
    
    with st.form("admission_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Candidate Full Name*")
            fname = st.text_input("Father's Name*")
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            dob = st.date_input("Date of Birth", value=datetime.date(2005, 1, 1))
            mobile = st.text_input("Mobile Number (Unique Key)*")
        with col2:
            vill = st.text_input("Village / Town*")
            dist = st.text_input("District", value="Sonitpur")
            course = st.selectbox("Course Selected*", [
                "PGDCA (12 Months)", "ADCA (12 Months)", "DCA (6 Months)", 
                "DTP (3 Months)", "Tally Prime with GST (3 Months)", "English Coaching"
            ])
            shift = st.selectbox("Shift Assigned", ["Morning (06:30-08:00 AM)", "Afternoon (04:00-05:30 PM)", "Evening (05:30-07:00 PM)"])
            fee = st.number_input("Course Fee (₹)", min_value=100.0, value=2550.0, step=50.0)
            
        if st.form_submit_button("🟢 Submit Admission"):
            if not name or not mobile:
                st.error("Please enter Name and Mobile Number!")
            else:
                new_row = {
                    "Sl. No.": str(len(student_df) + 1), "Student ID": next_id, "Name": name.upper(),
                    "Father Name": fname.upper(), "Mother Name": "", "Gender": gender, "DOB": str(dob),
                    "Mobile No": mobile, "Vill Town": vill.upper(), "District": dist.upper(),
                    "Course": course, "Duration": "Certified", "Days_Batch": "Regular", "Session": "2026-27",
                    "Join Date": str(datetime.date.today()), "Validity Date": str(datetime.date.today() + datetime.timedelta(days=180)),
                    "Total Fee": str(fee), "Discount": "0", "Net Fee": str(fee), "Shift": shift, "Status": "Active",
                    "HO_Reg_No": "Pending", "Stage_AdmitCard": "Pending", "Stage_Cert_Status": "In Process", "Cert_Serial_No": "--"
                }
                student_df = pd.concat([student_df, pd.DataFrame([new_row])], ignore_index=True)
                db.update_table("students_db.csv", "students_db", student_df)
                st.success(f"🎉 Candidate Registered! Roll ID: {next_id}")
                st.rerun()

# 3. FEE COUNTER
elif menu == "💵 Fee Counter Desk":
    st.subheader("💵 Student Fee Collection Counter Desk")
    if not student_df.empty:
        s_opts = student_df["Student ID"] + " - " + student_df["Name"]
        sel_s = st.selectbox("Select Student:", s_opts)
        if sel_s:
            sid = sel_s.split(" - ")[0]
            s_rec = student_df[student_df["Student ID"] == sid].iloc[0]
            p_logs = fee_df[fee_df["Student ID"] == sid]
            
            tot_paid = sum([float(a) for a in p_logs["Amount Paid"] if a])
            net_f = float(s_rec["Net Fee"]) if s_rec["Net Fee"] else 0.0
            due_f = max(0.0, net_f - tot_paid)
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Fee", f"₹{net_f:.2f}")
            c2.metric("Total Paid", f"₹{tot_paid:.2f}")
            c3.metric("Due Balance", f"₹{due_f:.2f}", delta="-Due" if due_f > 0 else "Cleared", delta_color="inverse")
            
            st.markdown("---")
            with st.form("fee_collect_form", clear_on_submit=True):
                pay_amt = st.number_input("Amount Deposited (₹)*", min_value=100.0, step=100.0)
                pay_mode = st.selectbox("Payment Mode", ["Cash", "UPI / GPay", "Bank Transfer"])
                collector = st.text_input("Collected By", value="Chiranjeeb Hazarika")
                remarks = st.text_input("Remarks", value="Installment Deposit")
                
                if st.form_submit_button("🟢 Issue Receipt & Save"):
                    rc_no = f"REC-{datetime.date.today().strftime('%Y%m%d')}-{len(fee_df)+1:03d}"
                    f_row = {
                        "Receipt No": rc_no, "Student ID": sid, "Date": str(datetime.date.today()),
                        "Amount Paid": str(pay_amt), "Payment Mode": pay_mode, "Collected_By": collector, "Remarks": remarks
                    }
                    fee_df = pd.concat([fee_df, pd.DataFrame([f_row])], ignore_index=True)
                    db.update_table("fees_db.csv", "fees_db", fee_df)
                    st.success(f"🧾 Receipt Issued! No: {rc_no} | Amount: ₹{pay_amt}")
                    st.rerun()
    else:
        st.info("No active students found.")

# 4. ID & PASSBOOK
elif menu == "🪪 ID Card & Passbook Desk":
    st.subheader("🪪 Printable ID Card & Fee Installment Passbook Desk")
    if not student_df.empty:
        s_opts = student_df["Student ID"] + " - " + student_df["Name"]
        sel_s = st.selectbox("Select Candidate to Preview:", s_opts)
        if sel_s:
            sid = sel_s.split(" - ")[0]
            s = student_df[student_df["Student ID"] == sid].iloc[0]
            choice = st.radio("Select Document:", ["🪪 Digital Student ID Card", "💳 Fee Passbook Card"], horizontal=True)
            
            if choice == "🪪 Digital Student ID Card":
                qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data={s['Student ID']}"
                st.markdown(f"""
                <div class="id-card-container">
                    <div class="id-card-header">
                        <div style="font-size:13px; font-weight:800; color:#38BDF8;">SOFT TECH COMPUTERS & ZTC</div>
                        <div style="font-size:9.5px; color:#CBD5E1;">ISO 9001:2015 Certified | Center: 4159</div>
                    </div>
                    <div style="padding:16px; text-align:center;">
                        <img src="https://cdn-icons-png.flaticon.com/512/3135/3135715.png" style="width:75px; height:75px; border-radius:50%; border:2px solid #0284C7;"><br>
                        <b style="font-size:16px; text-transform:uppercase;">{s['Name']}</b><br>
                        <span style="background:#E0F2FE; color:#0369A1; font-weight:700; font-size:11px; padding:2px 10px; border-radius:10px;">ID: {s['Student ID']}</span>
                        <table style="width:100%; font-size:11px; text-align:left; margin-top:10px; line-height:1.6;">
                            <tr><td><b>Course:</b></td><td>{s['Course']}</td></tr>
                            <tr><td><b>Father:</b></td><td>{s['Father Name']}</td></tr>
                            <tr><td><b>Mobile:</b></td><td>{s['Mobile No']}</td></tr>
                            <tr><td><b>Shift:</b></td><td>{s['Shift']}</td></tr>
                        </table>
                        <div style="display:flex; justify-content:space-around; align-items:center; margin-top:12px;">
                            <img src="{qr_url}" style="width:60px; height:60px; border:1px solid #CBD5E1; padding:2px;">
                            <div style="font-size:9.5px; font-weight:bold; border-top:1px solid #0F172A; padding-top:4px;">Director Signature</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                p_logs = fee_df[fee_df["Student ID"] == sid]
                tot_p = sum([float(a) for a in p_logs["Amount Paid"] if a])
                net_f = float(s["Net Fee"]) if s["Net Fee"] else 0.0
                due_f = max(0.0, net_f - tot_p)
                
                rows = ""
                curr_run = 0.0
                for idx, (_, r) in enumerate(p_logs.iterrows(), 1):
                    amt = float(r["Amount Paid"]) if r["Amount Paid"] else 0.0
                    curr_run += amt
                    rows += f"<tr><td>{idx}</td><td>{r['Date']}</td><td>{r['Receipt No']}</td><td style='color:#059669; font-weight:bold;'>₹{amt:.2f}</td><td style='color:#DC2626;'>₹{max(0.0, net_f - curr_run):.2f}</td><td>{r['Payment Mode']}</td></tr>"
                if not rows:
                    rows = "<tr><td colspan='6'>No installment payments yet.</td></tr>"
                    
                st.markdown(f"""
                <div class="passbook-card">
                    <div style="text-align:center; border-bottom:2px solid #0284C7; padding-bottom:6px;">
                        <h3 style="margin:0;">SOFT TECH COMPUTERS & ZTC</h3>
                        <span style="font-size:11px; color:#64748B;">Official Student Fee Installment Passbook</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; font-size:12px; margin:10px 0; background:#F8FAFC; padding:8px; border-radius:4px;">
                        <div><b>Candidate:</b> {s['Name']}<br><b>Roll ID:</b> {s['Student ID']}</div>
                        <div style="text-align:right;"><b>Total Fee:</b> ₹{net_f:.2f}<br><b>Net Due:</b> <span style="color:#DC2626; font-weight:bold;">₹{due_f:.2f}</span></div>
                    </div>
                    <table class="passbook-table">
                        <thead><tr><th>#</th><th>Date</th><th>Receipt No</th><th>Paid</th><th>Due</th><th>Mode</th></tr></thead>
                        <tbody>{rows}</tbody>
                    </table>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No candidates found.")

# 5. ATTENDANCE
elif menu == "📸 Student Attendance":
    st.subheader("📸 Daily Classroom Attendance Log")
    if not student_df.empty:
        with st.form("att_form", clear_on_submit=True):
            att_sid = st.selectbox("Select Student:", student_df["Student ID"] + " - " + student_df["Name"])
            att_stat = st.selectbox("Status", ["Present", "Absent", "Late"])
            if st.form_submit_button("🟢 Mark Attendance"):
                sid_val = att_sid.split(" - ")[0]
                now_t = datetime.datetime.now(IST).strftime("%I:%M %p")
                att_row = {"Student ID": sid_val, "Date": str(datetime.date.today()), "Time_In": now_t, "Status": att_stat}
                att_df = pd.concat([att_df, pd.DataFrame([att_row])], ignore_index=True)
                db.update_table("attendance_db.csv", "attendance_db", att_df)
                st.success(f"✅ Marked {att_stat} for {att_sid}!")
                st.rerun()
        if not att_df.empty:
            st.dataframe(att_df.tail(15), use_container_width=True)
    else:
        st.info("No students found.")

# 6. ADMIN PANEL
elif menu == "🔐 Director Admin Panel":
    st.subheader("🔐 Director Admin Control Panel")
    pwd = st.text_input("Enter Director Admin Password:", type="password")
    if pwd == "zaan123":
        st.success("Authorized Access Granted!")
        a_tab1, a_tab2 = st.tabs(["📋 Student Master & Cascade Delete", "💰 Fee Dues Ledger"])
        
        with a_tab1:
            st.write("**Manage Candidates & Permanent Deletion:**")
            if not student_df.empty:
                st.dataframe(student_df[["Student ID", "Name", "Mobile No", "Course", "Net Fee", "Status"]], use_container_width=True)
                del_sid = st.selectbox("Select Student to Delete:", student_df["Student ID"] + " - " + student_df["Name"], key="del_s_box")
                if st.button("🔴 Permanently Delete Student & All Fee Records"):
                    s_del_id = del_sid.split(" - ")[0]
                    student_df = student_df[student_df["Student ID"] != s_del_id]
                    fee_df = fee_df[fee_df["Student ID"] != s_del_id]
                    att_df = att_df[att_df["Student ID"] != s_del_id]
                    db.update_table("students_db.csv", "students_db", student_df)
                    db.update_table("fees_db.csv", "fees_db", fee_df)
                    db.update_table("attendance_db.csv", "attendance_db", att_df)
                    st.success(f"🗑️ Candidate {s_del_id} and associated logs deleted cleanly!")
                    st.rerun()
                    
        with a_tab2:
            st.write("**Student Outstanding Dues Ledger:**")
            if not student_df.empty:
                ledger = []
                for _, s in student_df.iterrows():
                    sid = s["Student ID"]
                    p_logs = fee_df[fee_df["Student ID"] == sid]
                    tot_p = sum([float(a) for a in p_logs["Amount Paid"] if a])
                    net_f = float(s["Net Fee"]) if s["Net Fee"] else 0.0
                    due_f = max(0.0, net_f - tot_p)
                    ledger.append({
                        "Roll ID": sid, "Name": s["Name"], "Course": s["Course"],
                        "Total Fee": f"₹{net_f:.2f}", "Paid": f"₹{tot_p:.2f}", "Due Balance": f"₹{due_f:.2f}",
                        "Status": "Cleared" if due_f <= 0 else "Pending Due"
                    })
                st.dataframe(pd.DataFrame(ledger), use_container_width=True)
