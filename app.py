import streamlit as st
import pandas as pd
import datetime
import pytz
import sqlite3
import urllib.parse
import os

# Page Setup
st.set_page_config(
    page_title="Soft Tech Computers & ZTC Enterprise",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

IST = pytz.timezone('Asia/Kolkata')
DB_FILE = "ztc_academy.db"

# -------------------------------------------------------------
# LIGHTNING-FAST LOCAL DATABASE ENGINE (SQLITE)
# -------------------------------------------------------------
def get_db_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    # Students Master
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            name TEXT,
            father_name TEXT,
            mobile TEXT UNIQUE,
            course TEXT,
            join_date TEXT,
            total_fee REAL,
            net_fee REAL,
            shift TEXT,
            status TEXT,
            lifecycle_stage TEXT,
            ho_reg_no TEXT,
            cert_serial_no TEXT
        )
    ''')
    # Fees Ledger
    c.execute('''
        CREATE TABLE IF NOT EXISTS fees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            receipt_no TEXT,
            student_id TEXT,
            date TEXT,
            amount REAL,
            mode TEXT,
            collector TEXT,
            remarks TEXT,
            FOREIGN KEY (student_id) REFERENCES students (student_id) ON DELETE CASCADE
        )
    ''')
    # Student Attendance
    c.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            date TEXT,
            time_in TEXT,
            status TEXT,
            FOREIGN KEY (student_id) REFERENCES students (student_id) ON DELETE CASCADE
        )
    ''')
    # Exam / Test Marks
    c.execute('''
        CREATE TABLE IF NOT EXISTS marks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            test_topic TEXT,
            marks_obtained REAL,
            total_marks REAL,
            date TEXT,
            FOREIGN KEY (student_id) REFERENCES students (student_id) ON DELETE CASCADE
        )
    ''')
    # Syllabus Covered Log
    c.execute('''
        CREATE TABLE IF NOT EXISTS syllabus_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course TEXT,
            topic_name TEXT,
            date TEXT,
            teacher_name TEXT
        )
    ''')
    # Teacher Attendance & Daily Salary Punch
    c.execute('''
        CREATE TABLE IF NOT EXISTS teacher_punches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_name TEXT,
            date TEXT,
            shift TEXT,
            time_in TEXT,
            time_out TEXT,
            late_mins INTEGER,
            penalty_cut REAL,
            net_batch_earning REAL,
            status TEXT
        )
    ''')
    # Public Enquiries
    c.execute('''
        CREATE TABLE IF NOT EXISTS enquiries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            name TEXT,
            mobile TEXT,
            course TEXT,
            address TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# -------------------------------------------------------------
# HIGH-END SLATE-NAVY MODERN PORTAL CSS
# -------------------------------------------------------------
st.markdown("""
<style>
.stApp {
    background-color: #0B1120;
    color: #E2E8F0;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
.top-navbar {
    background-color: #0F172A;
    border-bottom: 1px solid #1E293B;
    padding: 14px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: -60px;
    margin-left: -4rem;
    margin-right: -4rem;
    margin-bottom: 24px;
}
.hero-wrapper {
    background: #0F172A;
    border: 1px solid #1E293B;
    border-radius: 14px;
    padding: 24px 28px;
    margin-bottom: 24px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
}
.hero-tag-pill {
    background: rgba(249, 115, 22, 0.12);
    border: 1px solid rgba(249, 115, 22, 0.5);
    color: #FB923C;
    font-size: 11px;
    font-weight: 700;
    padding: 5px 14px;
    border-radius: 20px;
    display: inline-block;
    margin-bottom: 12px;
}
.hero-main-title {
    font-size: 30px;
    font-weight: 900;
    color: #FFFFFF;
    margin: 0 0 8px 0;
}
.pill-item {
    font-size: 11.5px;
    font-weight: 700;
    padding: 6px 14px;
    border-radius: 6px;
    display: inline-flex;
    margin-right: 8px;
    margin-top: 6px;
}
.pill-orange { background: #EA580C; color: white; }
.pill-green { background: #059669; color: white; }
.pill-blue { background: #2563EB; color: white; }
.portal-card {
    background: #0F172A;
    border: 1px solid #1E293B;
    border-radius: 12px;
    padding: 20px;
    height: 100%;
    margin-bottom: 16px;
}
.card-header-flex {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #1E293B;
    padding-bottom: 10px;
    margin-bottom: 14px;
}
div.stButton > button {
    background-color: #10B981 !important;
    color: white !important;
    border-radius: 6px !important;
    font-weight: 700 !important;
    border: none !important;
    padding: 8px 18px !important;
}
div.stButton > button:hover {
    background-color: #059669 !important;
}
div[data-testid="stMetric"] {
    background: #0F172A;
    border: 1px solid #1E293B;
    padding: 14px;
    border-radius: 10px;
}
div[data-testid="stMetricValue"] { color: #38BDF8 !important; font-weight: 800 !important; }
.passbook-box {
    background: #FFFFFF;
    border: 2px solid #334155;
    border-radius: 10px;
    padding: 18px;
    color: #0F172A;
    margin: 15px auto;
}
.passbook-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
    margin-top: 10px;
}
.passbook-table th, .passbook-table td {
    border: 1px solid #CBD5E1;
    padding: 7px;
    text-align: center;
}
.passbook-table th { background: #F1F5F9; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# Top Bar
st.markdown("""
<div class="top-navbar">
    <div style="display:flex; align-items:center; gap:12px;">
        <span style="background:#10B981; color:white; font-weight:900; padding:6px 12px; border-radius:8px; font-size:16px;">STC</span>
        <div>
            <b style="font-size:17px; color:#F8FAFC;">Soft Tech Computers & ZTC Enterprise</b><br>
            <span style="font-size:11px; color:#38BDF8;">ISO 9001:2015 Certified | Center Code: 4159 (Kamarchuburi, Sonitpur)</span>
        </div>
    </div>
    <div style="font-size:12px; color:#94A3B8;">Session: <b>2026-27</b> | <span style="color:#10B981;">● Online Engine</span></div>
</div>
""", unsafe_allow_html=True)

# Navigation
st.sidebar.title("💻 Portal Navigation")
menu = st.sidebar.radio("Select Module:", [
    "🌐 Public Dashboard & Enquiry",
    "🔑 Student Self-Service Portal",
    "💵 TuFee Fast Counter & Dues",
    "📝 Admission & Lifecycle Management",
    "⏰ Faculty Attendance & Salary",
    "📚 Syllabus Covered & Homework Desk"
])

conn = get_db_connection()

# -------------------------------------------------------------
# 1. PUBLIC DASHBOARD & ADMISSION ENQUIRY
# -------------------------------------------------------------
if menu == "🌐 Public Dashboard & Enquiry":
    st.markdown("""
    <div class="hero-wrapper">
        <div class="hero-tag-pill">🛡️ GOVT REGD IT ACADEMY • SONITPUR, ASSAM</div>
        <h1 class="hero-main-title">Soft Tech Computers & ZTC Enterprise</h1>
        <p style="color:#94A3B8; font-size:14px; line-height:1.7; margin:0 0 14px 0;">
            An accredited institution under Center Code <b style="color:#FB923C;">4159</b> providing ISO 9001:2015 certified technical computer courses with Sarva India nationwide accreditation. Practical oriented computer software training for youth empowerment.
        </p>
        <div>
            <span class="pill-item pill-orange"># CENTER CODE: 4159</span>
            <span class="pill-item pill-green">✓ Operational & Active</span>
            <span class="pill-item pill-blue">🏛️ ISO 9001:2015 Certified</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col_p1, col_p2 = st.columns([1.6, 1.2])
    with col_p1:
        st.markdown("""
        <div class="portal-card">
            <div class="card-header-flex">
                <b style="color:#F8FAFC; font-size:16px;">🏛️ Institutional Information & Courses</b>
                <span style="color:#38BDF8; font-size:11px; font-weight:bold;">CODE: 4159</span>
            </div>
            <p style="color:#94A3B8; font-size:13.5px; line-height:1.7;">
                Soft Tech Computers & ZTC Enterprise offers Govt-recognized computer certification programs:
                <br>• <b>PGDCA / ADCA:</b> 12 Months Advanced Diploma
                <br>• <b>DCA:</b> 6 Months Computer Application
                <br>• <b>Tally Prime with GST:</b> Professional Accounting & Billing
                <br>• <b>DTP:</b> Desktop Publishing (Photoshop, Pagemaker, DTP)
                <br>• <b>High School English Coaching:</b> Class 9 to 12
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_p2:
        st.markdown("""
        <div class="portal-card">
            <div class="card-header-flex">
                <b style="color:#F8FAFC; font-size:16px;">ℹ️ Center Contact & Location</b>
                <span style="color:#10B981; font-size:11px; font-weight:bold;">VERIFIED</span>
            </div>
            <div style="font-size:13px; line-height:2.0; color:#E2E8F0;">
                📍 <b>Location:</b> Kamarchuburi, Thelamara, Sonitpur<br>
                📮 <b>PIN Code:</b> 784149, Assam<br>
                📞 <b>Director:</b> Chiranjeeb Hazarika (9101026718)<br>
                📜 <b>Affiliation:</b> Sarva India (HP Head Office)
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    st.subheader("📜 Online Certificate Verification")
    v_id = st.text_input("Enter Student Roll ID (e.g. STC26-001):", key="pub_v_id").strip().upper()
    if v_id:
        match_s = conn.execute("SELECT * FROM students WHERE student_id = ?", (v_id,)).fetchone()
        if match_s:
            st.success(f"✅ RECORD VERIFIED: {match_s['name']} | Course: {match_s['course']} | Status: {match_s['status']} (Center Code: 4159)")
        else:
            st.error("❌ No official matching record found in institute database.")
            
    st.markdown("---")
    with st.expander("📝 Submit Public Admission / Course Enquiry", expanded=False):
        with st.form("enquiry_form", clear_on_submit=True):
            enq_name = st.text_input("Full Name*")
            enq_mob = st.text_input("Mobile No (WhatsApp)*")
            enq_course = st.selectbox("Course Interested:", ["PGDCA (12M)", "ADCA (12M)", "DCA (6M)", "Tally Prime GST", "DTP", "English Coaching"])
            enq_addr = st.text_input("Village / Address*")
            if st.form_submit_button("🟢 Submit Enquiry"):
                if enq_name and enq_mob:
                    conn.execute("INSERT INTO enquiries (date, name, mobile, course, address) VALUES (?, ?, ?, ?, ?)",
                                 (str(datetime.date.today()), enq_name.upper(), enq_mob, enq_course, enq_addr.upper()))
                    conn.commit()
                    st.success("🎉 Enquiry Submitted! Our center team will contact you shortly.")
                else:
                    st.error("Please fill Name and Mobile Number!")

# -------------------------------------------------------------
# 2. STUDENT SELF-SERVICE PORTAL
# -------------------------------------------------------------
elif menu == "🔑 Student Self-Service Portal":
    st.subheader("🔑 Student Dashboard (Attendance, Marks, Syllabus Covered & Fees)")
    
    if "s_auth_id" not in st.session_state:
        st.session_state["s_auth_id"] = None

    if not st.session_state["s_auth_id"]:
        c_l1, c_l2 = st.columns(2)
        with c_l1:
            in_sid = st.text_input("Enter Student Roll ID:").strip().upper()
        with c_l2:
            in_mob = st.text_input("Enter Registered Mobile No (Password):", type="password").strip()
            
        if st.button("🟢 Login To My Dashboard", use_container_width=True):
            user = conn.execute("SELECT * FROM students WHERE student_id = ? AND mobile = ?", (in_sid, in_mob)).fetchone()
            if user:
                st.session_state["s_auth_id"] = in_sid
                st.rerun()
            else:
                st.error("❌ Invalid Roll ID or Mobile Number!")
    else:
        sid = st.session_state["s_auth_id"]
        s = conn.execute("SELECT * FROM students WHERE student_id = ?", (sid,)).fetchone()
        
        st.markdown(f"""
        <div style="background:#0F172A; border:1px solid #1E293B; border-radius:10px; padding:16px 20px; margin-bottom:15px;">
            <b style="font-size:18px; color:#FFFFFF;">Welcome, {s['name']}</b> | Roll ID: <b style="color:#38BDF8;">{s['student_id']}</b> | Course: <b>{s['course']}</b>
        </div>
        """, unsafe_allow_html=True)
        
        # Lifecycle Pipeline Stepper
        curr_stage = s["lifecycle_stage"] if s["lifecycle_stage"] else "Admission"
        stages = ["Admission", "Learning/Tests", "Course Completed", "HO Registered", "Exam Appeared", "Certificate Handover"]
        
        st.write("**Student Lifecycle Progress:**")
        stepper_cols = st.columns(6)
        for idx, stg in enumerate(stages):
            is_done = stages.index(curr_stage) >= idx if curr_stage in stages else False
            stepper_cols[idx].markdown(f"""
            <div style="text-align:center; background:{'#059669' if is_done else '#1E293B'}; color:white; padding:8px 4px; border-radius:6px; font-size:11px; font-weight:bold;">
                {'✓ ' if is_done else ''}{stg}
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Calculations: Attendance, Marks, Fees
        att_rows = conn.execute("SELECT * FROM attendance WHERE student_id = ?", (sid,)).fetchall()
        tot_days = len(att_rows)
        present_days = len([r for r in att_rows if r["status"] in ["Present", "Late"]])
        att_pct = (present_days / tot_days * 100) if tot_days > 0 else 100.0
        
        fee_rows = conn.execute("SELECT * FROM fees WHERE student_id = ?", (sid,)).fetchall()
        tot_paid = sum([r["amount"] for r in fee_rows])
        net_f = s["net_fee"] if s["net_fee"] else 0.0
        due_f = max(0.0, net_f - tot_paid)
        
        marks_rows = conn.execute("SELECT * FROM marks WHERE student_id = ?", (sid,)).fetchall()
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Attendance Score", f"{att_pct:.1f}%", f"{present_days}/{tot_days} Days")
        c2.metric("Total Fee Paid", f"₹{tot_paid:,.2f}", f"Net: ₹{net_f:,.2f}")
        c3.metric("Remaining Due", f"₹{due_f:,.2f}", delta="-Due" if due_f > 0 else "Cleared", delta_color="inverse")
        c4.metric("Current Stage", curr_stage)
        
        st.markdown("---")
        
        tab_a, tab_b, tab_c, tab_d = st.tabs(["📚 What I Learned (Syllabus Covered)", "📝 Exam & Test Marks", "📸 Attendance Log", "💳 Installment Passbook"])
        
        with tab_a:
            st.write(f"**Topics Covered by Faculty for Course ({s['course']}):**")
            syl_rows = conn.execute("SELECT * FROM syllabus_logs WHERE course = ? ORDER BY id DESC", (s["course"],)).fetchall()
            if syl_rows:
                syl_df = pd.DataFrame([dict(r) for r in syl_rows])
                st.dataframe(syl_df[["date", "topic_name", "teacher_name"]], use_container_width=True)
            else:
                st.info("No syllabus logs entered for this course yet.")
                
        with tab_b:
            st.write("**Unit Tests & Exam Results:**")
            if marks_rows:
                m_df = pd.DataFrame([dict(r) for r in marks_rows])
                st.dataframe(m_df[["date", "test_topic", "marks_obtained", "total_marks"]], use_container_width=True)
            else:
                st.info("No test marks recorded yet.")
                
        with tab_c:
            st.write("**Classroom Attendance History:**")
            if att_rows:
                a_df = pd.DataFrame([dict(r) for r in att_rows])
                st.dataframe(a_df[["date", "time_in", "status"]], use_container_width=True)
            else:
                st.info("No attendance records logged yet.")
                
        with tab_d:
            st.write("**Student Fee Passbook Ledger:**")
            rows_html = ""
            run_paid = 0.0
            for idx, r in enumerate(fee_rows, 1):
                run_paid += r["amount"]
                rows_html += f"<tr><td>{idx}</td><td>{r['date']}</td><td>{r['receipt_no']}</td><td style='color:#059669; font-weight:bold;'>₹{r['amount']:.2f}</td><td style='color:#DC2626;'>₹{max(0.0, net_f - run_paid):.2f}</td><td>{r['mode']}</td><td>{r['collector']}</td></tr>"
            if not rows_html:
                rows_html = "<tr><td colspan='7'>No fee payments deposited yet.</td></tr>"
                
            st.markdown(f"""
            <div class="passbook-box">
                <div style="text-align:center; border-bottom:2px solid #0284C7; padding-bottom:6px;">
                    <h3 style="margin:0;">SOFT TECH COMPUTERS & ZTC ENTERPRISE</h3>
                    <span style="font-size:11px; color:#64748B;">Official Student Installment Passbook</span>
                </div>
                <div style="display:flex; justify-content:space-between; font-size:12.5px; margin:10px 0; background:#F8FAFC; padding:8px;">
                    <div><b>Candidate:</b> {s['name']}<br><b>Roll ID:</b> {s['student_id']}</div>
                    <div style="text-align:right;"><b>Course Fee:</b> ₹{net_f:.2f}<br><b>Due Balance:</b> <b style="color:#DC2626;">₹{due_f:.2f}</b></div>
                </div>
                <table class="passbook-table">
                    <thead><tr><th>#</th><th>Date</th><th>Receipt No</th><th>Paid</th><th>Due</th><th>Mode</th><th>Collector</th></tr></thead>
                    <tbody>{rows_html}</tbody>
                </table>
            </div>
            """, unsafe_allow_html=True)
            
        if st.button("🔒 Logout"):
            st.session_state["s_auth_id"] = None
            st.rerun()

# -------------------------------------------------------------
# 3. TUFEE FAST COUNTER & DUES (WITH 1-CLICK WHATSAPP)
# -------------------------------------------------------------
elif menu == "💵 TuFee Fast Counter & Dues":
    st.subheader("💵 TuFee Instant Fee Collection & 1-Click WhatsApp Desk")
    
    t_f1, t_f2 = st.tabs(["⚡ Collect Fee & Send WhatsApp Receipt", "📢 Dues Ledger & WhatsApp Reminder"])
    
    with t_f1:
        students = conn.execute("SELECT * FROM students").fetchall()
        if students:
            s_options = [f"{r['student_id']} - {r['name']} ({r['mobile']})" for r in students]
            sel_s = st.selectbox("Select Candidate:", s_options)
            sel_sid = sel_s.split(" - ")[0]
            s_data = conn.execute("SELECT * FROM students WHERE student_id = ?", (sel_sid,)).fetchone()
            
            p_rows = conn.execute("SELECT * FROM fees WHERE student_id = ?", (sel_sid,)).fetchall()
            tot_p = sum([r["amount"] for r in p_rows])
            net_f = s_data["net_fee"] if s_data["net_fee"] else 0.0
            due_b = max(0.0, net_f - tot_p)
            
            col_inf1, col_inf2, col_inf3 = st.columns(3)
            col_inf1.metric("Course Net Fee", f"₹{net_f:.2f}")
            col_inf2.metric("Total Deposited", f"₹{tot_p:.2f}")
            col_inf3.metric("Current Due", f"₹{due_b:.2f}", delta="-Due" if due_b > 0 else "Cleared", delta_color="inverse")
            
            with st.form("quick_fee_form", clear_on_submit=True):
                pay_amt = st.number_input("Deposit Amount (₹)*", min_value=50.0, step=100.0, value=500.0)
                pay_mode = st.selectbox("Payment Mode", ["Cash", "UPI / GPay", "Bank Transfer"])
                collector = st.text_input("Collector Name", value="Chiranjeeb Hazarika")
                remarks = st.text_input("Remarks", value="Course Installment Fee")
                
                if st.form_submit_button("🟢 Collect Fee & Save"):
                    rc_num = f"REC-{datetime.date.today().strftime('%Y%m%d')}-{len(conn.execute('SELECT id FROM fees').fetchall())+1:03d}"
                    today_str = str(datetime.date.today())
                    conn.execute("INSERT INTO fees (receipt_no, student_id, date, amount, mode, collector, remarks) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                 (rc_num, sel_sid, today_str, pay_amt, pay_mode, collector, remarks))
                    conn.commit()
                    
                    new_due = max(0.0, due_b - pay_amt)
                    st.success(f"🧾 Receipt Issued: {rc_num} | Amount: ₹{pay_amt}")
                    
                    # 1-Click WhatsApp Receipt Link
                    raw_msg = f"""🧾 *OFFICIAL FEE RECEIPT - SOFT TECH COMPUTERS & ZTC*
(Center Code: 4159 | Kamarchuburi, Sonitpur)

Dear {s_data['name']}, your course installment fee has been successfully received.

• Receipt No: *{rc_num}*
• Roll ID: *{sel_sid}*
• Course: *{s_data['course']}*
• Amount Paid: *₹{pay_amt:.2f}* ({pay_mode})
• Remaining Due Balance: *₹{new_due:.2f}*
• Date: *{today_str}*

Thank you for learning with Soft Tech Computers & ZTC!
Contact: 9101026718"""
                    wa_url = f"https://wa.me/91{s_data['mobile']}?text={urllib.parse.quote(raw_msg)}"
                    st.markdown(f"""
                    <a href="{wa_url}" target="_blank" style="text-decoration:none;">
                        <div style="background-color:#25D366; color:white; padding:10px 18px; border-radius:6px; font-weight:bold; display:inline-block; margin-top:8px;">
                            📲 Send Official WhatsApp Receipt to Candidate (+91 {s_data['mobile']})
                        </div>
                    </a>
                    """, unsafe_allow_html=True)
        else:
            st.info("No students found. Please register a student first.")
            
    with t_f2:
        st.write("**Candidate Outstanding Fee Dues Ledger:**")
        students_all = conn.execute("SELECT * FROM students").fetchall()
        dues_list = []
        for s_item in students_all:
            s_id = s_item["student_id"]
            paid_sum = sum([r["amount"] for r in conn.execute("SELECT amount FROM fees WHERE student_id = ?", (s_id,)).fetchall()])
            net_amt = s_item["net_fee"] if s_item["net_fee"] else 0.0
            due_amt = max(0.0, net_amt - paid_sum)
            if due_amt > 0:
                raw_rem = f"""📢 *FEE DUE REMINDER - SOFT TECH COMPUTERS & ZTC*
Dear {s_item['name']} ({s_item['student_id']}),
This is a gentle reminder that your installment fee of *₹{due_amt:.2f}* for course *{s_item['course']}* is currently pending.
Kindly clear your due balance at the center counter.
Director Contact: 9101026718"""
                rem_link = f"https://wa.me/91{s_item['mobile']}?text={urllib.parse.quote(raw_rem)}"
                dues_list.append({
                    "Roll ID": s_id,
                    "Name": s_item["name"],
                    "Mobile": s_item["mobile"],
                    "Course": s_item["course"],
                    "Net Fee": f"₹{net_amt:.2f}",
                    "Paid": f"₹{paid_sum:.2f}",
                    "Due Balance": f"₹{due_amt:.2f}",
                    "WhatsApp Reminder Link": rem_link
                })
        if dues_list:
            dues_df = pd.DataFrame(dues_list)
            st.dataframe(dues_df[["Roll ID", "Name", "Mobile", "Course", "Net Fee", "Paid", "Due Balance"]], use_container_width=True)
            st.write("**Click to Send Direct WhatsApp Reminders:**")
            for d in dues_list:
                st.markdown(f"• **{d['Name']}** (Due: {d['Due Balance']}): [📲 Send WhatsApp Reminder]({d['WhatsApp Reminder Link']})")
        else:
            st.success("🎉 All enrolled students have completely cleared their fees!")

# -------------------------------------------------------------
# 4. ADMISSION & LIFECYCLE MANAGEMENT
# -------------------------------------------------------------
elif menu == "📝 Admission & Lifecycle Management":
    st.subheader("📝 Candidate Admission & Student Lifecycle Progression")
    
    adm_t1, adm_t2 = st.tabs(["➕ New Student Admission", "🔄 Manage Lifecycle Stages & Cascade Delete"])
    
    with adm_t1:
        existing_students = conn.execute("SELECT student_id FROM students").fetchall()
        year_code = str(datetime.date.today().year)[2:]
        next_id = f"STC{year_code}-{len(existing_students)+1:03d}"
        st.info(f"⚡ **Auto-Generated Roll ID:** `{next_id}`")
        
        with st.form("admission_form", clear_on_submit=True):
            col_a1, col_a2 = st.columns(2)
            with col_a1:
                adm_name = st.text_input("Full Name*")
                adm_fname = st.text_input("Father's Name*")
                adm_mob = st.text_input("Mobile Number (Unique Key)*")
            with col_a2:
                adm_course = st.selectbox("Course Selected*", ["PGDCA (12 Months)", "ADCA (12 Months)", "DCA (6 Months)", "DTP (3 Months)", "Tally Prime with GST (3 Months)", "English Coaching"])
                adm_shift = st.selectbox("Assigned Shift", ["Morning (06:30-08:00 AM)", "Afternoon (04:00-05:30 PM)", "Evening (05:30-07:00 PM)"])
                adm_fee = st.number_input("Total Net Fee (₹)*", min_value=100.0, value=2550.0, step=50.0)
                
            if st.form_submit_button("🟢 Complete Admission"):
                if adm_name and adm_mob:
                    try:
                        conn.execute('''
                            INSERT INTO students (student_id, name, father_name, mobile, course, join_date, total_fee, net_fee, shift, status, lifecycle_stage, ho_reg_no, cert_serial_no)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (next_id, adm_name.upper(), adm_fname.upper(), adm_mob, adm_course, str(datetime.date.today()), adm_fee, adm_fee, adm_shift, "Active", "Admission", "Pending", "--"))
                        conn.commit()
                        st.success(f"🎉 Candidate Registered Successfully! Roll ID: {next_id}")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("🚨 This mobile number is already registered with another student!")
                else:
                    st.error("Please fill Name and Mobile Number!")
                    
    with adm_t2:
        students_all = conn.execute("SELECT * FROM students").fetchall()
        if students_all:
            s_opts = [f"{r['student_id']} - {r['name']}" for r in students_all]
            target_s = st.selectbox("Select Candidate to Update Stage or Delete:", s_opts)
            t_sid = target_s.split(" - ")[0]
            s_rec = conn.execute("SELECT * FROM students WHERE student_id = ?", (t_sid,)).fetchone()
            
            st.write(f"Candidate: **{s_rec['name']}** | Current Stage: <b style='color:#10B981;'>{s_rec['lifecycle_stage']}</b>", unsafe_allow_html=True)
            
            col_stg1, col_stg2 = st.columns(2)
            with col_stg1:
                new_stg = st.selectbox("Update Lifecycle Stage:", [
                    "Admission", "Learning/Tests", "Course Completed", "HO Registered", "Exam Appeared", "Certificate Handover"
                ], index=["Admission", "Learning/Tests", "Course Completed", "HO Registered", "Exam Appeared", "Certificate Handover"].index(s_rec['lifecycle_stage']) if s_rec['lifecycle_stage'] in ["Admission", "Learning/Tests", "Course Completed", "HO Registered", "Exam Appeared", "Certificate Handover"] else 0)
                new_ho = st.text_input("HP HO Reg No (if registered):", value=s_rec["ho_reg_no"])
                new_cert = st.text_input("Certificate Serial No (if handed over):", value=s_rec["cert_serial_no"])
                if st.button("🟢 Save Updated Stage"):
                    conn.execute("UPDATE students SET lifecycle_stage = ?, ho_reg_no = ?, cert_serial_no = ? WHERE student_id = ?",
                                 (new_stg, new_ho, new_cert, t_sid))
                    conn.commit()
                    st.success("✅ Lifecycle Stage Updated Successfully!")
                    st.rerun()
                    
            with col_stg2:
                st.write("**🔴 Permanent Cascade Delete (Complete Clean):**")
                st.warning("Deleting will permanently remove candidate, all fees, marks and attendance with ZERO ghost data left.")
                if st.button("🗑️ Delete Candidate & All Records", key="del_cand_btn"):
                    conn.execute("DELETE FROM students WHERE student_id = ?", (t_sid,))
                    conn.execute("DELETE FROM fees WHERE student_id = ?", (t_sid,))
                    conn.execute("DELETE FROM attendance WHERE student_id = ?", (t_sid,))
                    conn.execute("DELETE FROM marks WHERE student_id = ?", (t_sid,))
                    conn.commit()
                    st.success(f"Candidate {t_sid} and all linked records deleted completely!")
                    st.rerun()

# -------------------------------------------------------------
# 5. FACULTY ATTENDANCE & SALARY (REPLACED CLEAN TITLE)
# -------------------------------------------------------------
elif menu == "⏰ Faculty Attendance & Salary":
    st.subheader("⏰ Faculty Shift Punch & Automated Salary Engine")
    now_ist = datetime.datetime.now(IST)
    st.info(f"🕒 **Current IST Clock:** `{now_ist.strftime('%I:%M:%S %p (%d-%B-%Y)')}`")
    
    st.markdown("""
    <div style="background:#0F172A; border:1px solid #1E293B; border-radius:8px; padding:12px 16px; font-size:13px; margin-bottom:14px;">
        💡 <b>Salary Rule:</b> 3 Batches (90+90+90 = 270 Mins) = <b>₹230 / Day</b> (₹76.67 per 90-min batch | ₹0.852/Min). Late arrival automatically calculates penalty deduction.
    </div>
    """, unsafe_allow_html=True)
    
    t_name = st.selectbox("Select Teacher Name:", ["Senior Instructor", "Assistant Faculty", "Guest Faculty"])
    t_shift = st.selectbox("Assigned Shift:", [
        "Morning (06:30 - 08:00 AM)",
        "Afternoon (04:00 - 05:30 PM)",
        "Evening (05:30 - 07:00 PM)"
    ])
    
    shift_start_mins = 6 * 60 + 30 if "Morning" in t_shift else (16 * 60 if "Afternoon" in t_shift else 17 * 60 + 30)
    current_mins = now_ist.hour * 60 + now_ist.minute
    late_by = max(0, current_mins - shift_start_mins)
    is_late = late_by > 5
    
    base_batch_pay = 230.0 / 3.0
    per_min_rate = 230.0 / 270.0
    penalty_amt = round(min(late_by * per_min_rate, base_batch_pay), 2) if is_late else 0.0
    net_batch_earning = round(max(0.0, base_batch_pay - penalty_amt), 2)
    
    col_tp1, col_tp2 = st.columns(2)
    with col_tp1:
        if st.button("🟢 Teacher Punch IN Now", use_container_width=True):
            today_str = str(datetime.date.today())
            time_str = now_ist.strftime("%I:%M %p")
            stat_val = "Late" if is_late else "On-Time"
            conn.execute('''
                INSERT INTO teacher_punches (teacher_name, date, shift, time_in, time_out, late_mins, penalty_cut, net_batch_earning, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (t_name, today_str, t_shift, time_str, "--", late_by, penalty_amt, net_batch_earning, stat_val))
            conn.commit()
            if is_late:
                st.warning(f"🚨 Late by {late_by} mins! Penalty: ₹{penalty_amt:.2f} | Net Shift Pay: ₹{net_batch_earning:.2f}")
            else:
                st.success(f"✅ On-Time Punch IN at {time_str}! Shift Pay: ₹{base_batch_pay:.2f}")
            st.rerun()
            
    with col_tp2:
        if st.button("🔴 Teacher Punch OUT Now", use_container_width=True):
            today_str = str(datetime.date.today())
            time_str = now_ist.strftime("%I:%M %p")
            conn.execute("UPDATE teacher_punches SET time_out = ? WHERE teacher_name = ? AND date = ? AND time_out = '--'",
                         (time_str, t_name, today_str))
            conn.commit()
            st.success(f"✅ Punched OUT at {time_str}!")
            st.rerun()
            
    st.markdown("---")
    st.write("**Recent Teacher Shift & Earning Logs:**")
    t_logs = conn.execute("SELECT * FROM teacher_punches ORDER BY id DESC LIMIT 10").fetchall()
    if t_logs:
        st.dataframe(pd.DataFrame([dict(r) for r in t_logs]), use_container_width=True)

# -------------------------------------------------------------
# 6. SYLLABUS COVERED & HOMEWORK DESK
# -------------------------------------------------------------
elif menu == "📚 Syllabus Covered & Homework Desk":
    st.subheader("📚 Daily Syllabus Covered & Student Unit Test Marks")
    
    t_s1, t_s2 = st.tabs(["📖 Record Today's Topics Covered", "📝 Record Unit Test / Exam Marks"])
    
    with t_s1:
        with st.form("syl_form", clear_on_submit=True):
            s_course = st.selectbox("Course:", ["PGDCA (12 Months)", "ADCA (12 Months)", "DCA (6 Months)", "DTP (3 Months)", "Tally Prime with GST (3 Months)", "English Coaching"])
            s_topic = st.text_input("Topics Taught in Class Today (e.g. MS Excel Formulas, Tally GST Invoice, C Basics)*")
            s_teacher = st.text_input("Faculty Incharge", value="Chiranjeeb Hazarika")
            if st.form_submit_button("🟢 Save Topic to Course"):
                if s_topic:
                    conn.execute("INSERT INTO syllabus_logs (course, topic_name, date, teacher_name) VALUES (?, ?, ?, ?)",
                                 (s_course, s_topic, str(datetime.date.today()), s_teacher))
                    conn.commit()
                    st.success(f"✅ Topic recorded for {s_course}!")
                    st.rerun()
                else:
                    st.error("Please enter Topic Name!")
        s_all = conn.execute("SELECT * FROM syllabus_logs ORDER BY id DESC LIMIT 15").fetchall()
        if s_all:
            st.dataframe(pd.DataFrame([dict(r) for r in s_all]), use_container_width=True)
            
    with t_s2:
        students_m = conn.execute("SELECT student_id, name FROM students").fetchall()
        if students_m:
            with st.form("marks_form", clear_on_submit=True):
                m_sid = st.selectbox("Select Candidate:", [f"{r['student_id']} - {r['name']}" for r in students_m])
                m_topic = st.text_input("Test / Exam Title (e.g. MS Word Practical Test, Unit-1 Exam)*")
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    m_obt = st.number_input("Marks Obtained*", min_value=0.0, max_value=100.0, value=40.0)
                with col_m2:
                    m_tot = st.number_input("Total Marks*", min_value=1.0, max_value=100.0, value=50.0)
                    
                if st.form_submit_button("🟢 Post Marks to Student Record"):
                    sid_val = m_sid.split(" - ")[0]
                    if m_topic:
                        conn.execute("INSERT INTO marks (student_id, test_topic, marks_obtained, total_marks, date) VALUES (?, ?, ?, ?, ?)",
                                     (sid_val, m_topic, m_obt, m_tot, str(datetime.date.today())))
                        conn.commit()
                        st.success(f"✅ Marks posted for {m_sid}!")
                        st.rerun()
                    else:
                        st.error("Please enter Test Name!")
            m_all = conn.execute("SELECT * FROM marks ORDER BY id DESC LIMIT 15").fetchall()
            if m_all:
                st.dataframe(pd.DataFrame([dict(r) for r in m_all]), use_container_width=True)
        else:
            st.info("No students found.")

conn.close()

# Footer
st.markdown("""
<div style="text-align:center; padding:20px; font-size:12px; color:#64748B; border-top:1px solid #1E293B; margin-top:40px;">
Soft Tech Computers & ZTC Enterprise Management System © 2026 | Center Code: 4159 | Kamarchuburi, Thelamara, Sonitpur - 784149
</div>
""", unsafe_allow_html=True)
