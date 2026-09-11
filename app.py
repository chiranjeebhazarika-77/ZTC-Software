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
ADMIN_PIN = "zaan123"

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
    # Teachers Master
    c.execute('''
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            phone TEXT,
            designation TEXT,
            shift TEXT,
            join_date TEXT
        )
    ''')
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
    # Daily Student Teaching Log (Theory / Practical / Both)
    c.execute('''
        CREATE TABLE IF NOT EXISTS daily_class_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            student_id TEXT,
            teacher_name TEXT,
            topic TEXT,
            class_type TEXT,
            remarks TEXT,
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
    
    # Default Teacher if empty
    check_t = c.execute("SELECT COUNT(*) FROM teachers").fetchone()[0]
    if check_t == 0:
        c.execute("INSERT INTO teachers (name, phone, designation, shift, join_date) VALUES (?, ?, ?, ?, ?)",
                  ("Chiranjeeb Hazarika (Director)", "9101026718", "Director / Head", "All Shifts", str(datetime.date.today())))
    conn.commit()
    conn.close()

init_db()

# -------------------------------------------------------------
# HIGH-CONTRAST LIGHT & CRISP THEME CSS (CLEAN & READABLE)
# -------------------------------------------------------------
st.markdown("""
<style>
/* Clean Off-White Background */
.stApp {
    background-color: #F8FAFC;
    color: #0F172A;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
/* Crisp Top Bar */
.top-navbar {
    background: #FFFFFF;
    border-bottom: 2px solid #E2E8F0;
    padding: 14px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: -60px;
    margin-left: -4rem;
    margin-right: -4rem;
    margin-bottom: 24px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
/* White & Bright Hero Card */
.hero-wrapper {
    background: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 12px;
    padding: 22px 26px;
    margin-bottom: 20px;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.05);
}
.hero-tag-pill {
    background: #FFF7ED;
    border: 1px solid #F97316;
    color: #C2410C;
    font-size: 11px;
    font-weight: 800;
    padding: 4px 14px;
    border-radius: 20px;
    display: inline-block;
    margin-bottom: 10px;
}
.hero-main-title {
    font-size: 28px;
    font-weight: 900;
    color: #0F172A;
    margin: 0 0 8px 0;
}
.pill-item {
    font-size: 11.5px;
    font-weight: 700;
    padding: 5px 12px;
    border-radius: 6px;
    display: inline-flex;
    margin-right: 8px;
    margin-top: 6px;
}
.pill-orange { background: #EA580C; color: white; }
.pill-green { background: #059669; color: white; }
.pill-blue { background: #0284C7; color: white; }

/* Light Content Cards */
.portal-card {
    background: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 12px;
    padding: 18px;
    margin-bottom: 16px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}
.card-header-flex {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #E2E8F0;
    padding-bottom: 8px;
    margin-bottom: 12px;
}
/* High-Contrast Inputs & Dataframes */
div[data-testid="stMetric"] {
    background: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
    padding: 14px !important;
    border-radius: 10px !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.03);
}
div[data-testid="stMetricLabel"] { color: #475569 !important; font-weight: 600 !important; }
div[data-testid="stMetricValue"] { color: #0284C7 !important; font-weight: 900 !important; }

div.stButton > button {
    background-color: #059669 !important;
    color: white !important;
    border-radius: 6px !important;
    font-weight: 700 !important;
    border: none !important;
    padding: 8px 18px !important;
}
div.stButton > button:hover {
    background-color: #047857 !important;
}
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
.passbook-table th { background: #F1F5F9; font-weight: 700; color: #0F172A; }
</style>
""", unsafe_allow_html=True)

# Top Bar
st.markdown("""
<div class="top-navbar">
    <div style="display:flex; align-items:center; gap:12px;">
        <span style="background:#0284C7; color:white; font-weight:900; padding:6px 12px; border-radius:8px; font-size:16px;">STC</span>
        <div>
            <b style="font-size:17px; color:#0F172A;">Soft Tech Computers & ZTC Enterprise</b><br>
            <span style="font-size:11px; color:#64748B;">ISO 9001:2015 Certified | Center Code: 4159 (Kamarchuburi, Thelamara)</span>
        </div>
    </div>
    <div style="font-size:12px; color:#475569; text-align:right;">
        Academic Session: <b style="color:#0F172A;">2026-27</b><br>
        <span style="color:#059669; font-weight:bold;">● System Live (Zero-Lag Engine)</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Navigation
st.sidebar.title("💻 Portal Navigation")
menu = st.sidebar.radio("Select Module:", [
    "🌐 Public Dashboard & Enquiry",
    "🔑 Student Self-Service Portal",
    "📚 Daily Class Activity (Practical/Theory)",
    "💵 TuFee Fast Counter",
    "📝 Admission & Lifecycle Management",
    "👨‍🏫 Faculty Desk & Attendance",
    "🔐 Director Financial Locker (Private)"
])

conn = get_db_connection()

# -------------------------------------------------------------
# 1. PUBLIC DASHBOARD & ENQUIRY
# -------------------------------------------------------------
if menu == "🌐 Public Dashboard & Enquiry":
    st.markdown("""
    <div class="hero-wrapper">
        <div class="hero-tag-pill">🛡️ GOVT REGD IT ACADEMY • SONITPUR, ASSAM</div>
        <h1 class="hero-main-title">Soft Tech Computers & ZTC Enterprise</h1>
        <p style="color:#475569; font-size:14px; line-height:1.7; margin:0 0 12px 0;">
            An accredited institution under Center Code <b style="color:#C2410C;">4159</b> providing ISO 9001:2015 certified technical computer courses with Sarva India nationwide accreditation.
        </p>
        <div>
            <span class="pill-item pill-orange"># CENTER CODE: 4159</span>
            <span class="pill-item pill-green">✓ Operational & Verified</span>
            <span class="pill-item pill-blue">🏛️ ISO 9001:2015 Certified</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col_p1, col_p2 = st.columns([1.6, 1.2])
    with col_p1:
        st.markdown("""
        <div class="portal-card">
            <div class="card-header-flex">
                <b style="color:#0F172A; font-size:16px;">🏛️ Accredited Career Programs</b>
                <span style="color:#0284C7; font-size:11px; font-weight:bold;">CENTER: 4159</span>
            </div>
            <p style="color:#475569; font-size:13.5px; line-height:1.7;">
                • <b>PGDCA / ADCA:</b> 12 Months Advanced Diploma with Programming & DTP<br>
                • <b>DCA:</b> 6 Months Fundamental Computing & Office Automation<br>
                • <b>Tally Prime with GST:</b> Commercial Accounting, Billing & Taxation<br>
                • <b>DTP:</b> Graphic Designing (Photoshop, Pagemaker, CorelDraw)<br>
                • <b>English Coaching:</b> Class 9 to 12 Board Curriculum
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_p2:
        st.markdown("""
        <div class="portal-card">
            <div class="card-header-flex">
                <b style="color:#0F172A; font-size:16px;">ℹ️ Official Center Details</b>
                <span style="color:#059669; font-size:11px; font-weight:bold;">ACCREDITED</span>
            </div>
            <div style="font-size:13px; line-height:2.0; color:#334155;">
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
    st.subheader("🔑 Student Dashboard (Attendance, Daily Learning, Marks & Passbook)")
    
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
        <div style="background:#FFFFFF; border:1px solid #CBD5E1; border-radius:10px; padding:16px 20px; margin-bottom:15px; box-shadow:0 2px 6px rgba(0,0,0,0.04);">
            <b style="font-size:18px; color:#0F172A;">Welcome, {s['name']}</b> | Roll ID: <b style="color:#0284C7;">{s['student_id']}</b> | Course: <b>{s['course']}</b>
        </div>
        """, unsafe_allow_html=True)
        
        # Calculations: Attendance, Marks, Fees
        att_rows = conn.execute("SELECT * FROM attendance WHERE student_id = ?", (sid,)).fetchall()
        tot_days = len(att_rows)
        present_days = len([r for r in att_rows if r["status"] in ["Present", "Late"]])
        att_pct = (present_days / tot_days * 100) if tot_days > 0 else 100.0
        
        fee_rows = conn.execute("SELECT * FROM fees WHERE student_id = ?", (sid,)).fetchall()
        tot_paid = sum([r["amount"] for r in fee_rows])
        net_f = s["net_fee"] if s["net_fee"] else 0.0
        due_f = max(0.0, net_f - tot_paid)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Classroom Attendance", f"{att_pct:.1f}%", f"{present_days}/{tot_days} Days")
        c2.metric("Fee Deposited", f"₹{tot_paid:,.2f}", f"Net: ₹{net_f:,.2f}")
        c3.metric("Remaining Due", f"₹{due_f:,.2f}", delta="-Due" if due_f > 0 else "Cleared", delta_color="inverse")
        
        st.markdown("---")
        
        tab_a, tab_b, tab_c, tab_d = st.tabs(["📚 What I Learned (Daily Practical/Theory)", "📝 My Test Marks", "📸 Attendance Log", "💳 Fee Passbook"])
        
        with tab_a:
            st.write("**Topics Practiced & Learned in Class:**")
            c_logs = conn.execute("SELECT * FROM daily_class_logs WHERE student_id = ? ORDER BY id DESC", (sid,)).fetchall()
            if c_logs:
                cl_df = pd.DataFrame([dict(r) for r in c_logs])
                st.dataframe(cl_df[["date", "topic", "class_type", "teacher_name", "remarks"]], use_container_width=True)
            else:
                st.info("No individual class practice records logged yet.")
                
        with tab_b:
            st.write("**Unit Tests & Examination Results:**")
            marks_rows = conn.execute("SELECT * FROM marks WHERE student_id = ?", (sid,)).fetchall()
            if marks_rows:
                m_df = pd.DataFrame([dict(r) for r in marks_rows])
                st.dataframe(m_df[["date", "test_topic", "marks_obtained", "total_marks"]], use_container_width=True)
            else:
                st.info("No test marks recorded yet.")
                
        with tab_c:
            st.write("**Attendance History:**")
            if att_rows:
                a_df = pd.DataFrame([dict(r) for r in att_rows])
                st.dataframe(a_df[["date", "time_in", "status"]], use_container_width=True)
            else:
                st.info("No attendance records logged yet.")
                
        with tab_d:
            rows_html = ""
            run_paid = 0.0
            for idx, r in enumerate(fee_rows, 1):
                run_paid += r["amount"]
                rows_html += f"<tr><td>{idx}</td><td>{r['date']}</td><td>{r['receipt_no']}</td><td style='color:#059669; font-weight:bold;'>₹{r['amount']:.2f}</td><td style='color:#DC2626;'>₹{max(0.0, net_f - run_paid):.2f}</td><td>{r['mode']}</td><td>{r['collector']}</td></tr>"
            if not rows_html:
                rows_html = "<tr><td colspan='7'>No fee deposits recorded yet.</td></tr>"
                
            st.markdown(f"""
            <div class="passbook-box">
                <div style="text-align:center; border-bottom:2px solid #0284C7; padding-bottom:6px;">
                    <h3 style="margin:0;">SOFT TECH COMPUTERS & ZTC ENTERPRISE</h3>
                    <span style="font-size:11px; color:#64748B;">Student Fee Installment Passbook</span>
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
# 3. DAILY CLASS ACTIVITY (PRACTICAL / THEORY / BOTH)
# -------------------------------------------------------------
elif menu == "📚 Daily Class Activity (Practical/Theory)":
    st.subheader("📚 Daily Classroom Activity & Practical Lab Register")
    st.write("শিক্ষকে আজি কোন ছাত্ৰক কি শিকালে (প্ৰেক্টিকেল, থিয়ৰী নে দুয়োটা) তাৰ এন্ট্ৰি:")
    
    tab_cl1, tab_cl2 = st.tabs(["📝 Record Today's Class for Student", "📋 Review Daily Class History"])
    
    teachers_list = [r["name"] for r in conn.execute("SELECT name FROM teachers").fetchall()]
    students_list = conn.execute("SELECT student_id, name FROM students").fetchall()
    
    with tab_cl1:
        if students_list:
            with st.form("daily_class_form", clear_on_submit=True):
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    sel_st = st.selectbox("Select Student:*", [f"{r['student_id']} - {r['name']}" for r in students_list])
                    sel_tch = st.selectbox("Teacher Incharge:*", teachers_list)
                    class_mode = st.radio("Session Type / Mode:*", ["Practical Lab Only", "Theory Lecture Only", "Both (Theory + Practical)"], horizontal=True)
                with col_c2:
                    today_topic = st.text_input("Topic Covered (e.g. MS Word Resume, Tally GST Billing, Photoshop Tools)*")
                    class_remarks = st.text_input("Teacher Feedback / Lab Performance", value="Completed Exercise Well")
                    
                if st.form_submit_button("🟢 Save Today's Class Entry"):
                    if today_topic:
                        sid_val = sel_st.split(" - ")[0]
                        conn.execute('''
                            INSERT INTO daily_class_logs (date, student_id, teacher_name, topic, class_type, remarks)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (str(datetime.date.today()), sid_val, sel_tch, today_topic, class_mode, class_remarks))
                        conn.commit()
                        st.success(f"✅ Recorded {class_mode} on '{today_topic}' for {sel_st}!")
                        st.rerun()
                    else:
                        st.error("Please enter Topic Covered!")
        else:
            st.info("No students registered yet.")
            
    with tab_cl2:
        st.write("**Recent Classroom Practice Logs:**")
        all_logs = conn.execute('''
            SELECT d.date, d.student_id, s.name as student_name, d.teacher_name, d.topic, d.class_type, d.remarks
            FROM daily_class_logs d
            LEFT JOIN students s ON d.student_id = s.student_id
            ORDER BY d.id DESC LIMIT 20
        ''').fetchall()
        if all_logs:
            st.dataframe(pd.DataFrame([dict(r) for r in all_logs]), use_container_width=True)
        else:
            st.info("No class logs recorded yet.")

# -------------------------------------------------------------
# 4. TUFEE FAST COUNTER (COLLECT & WHATSAPP RECEIPT ONLY)
# -------------------------------------------------------------
elif menu == "💵 TuFee Fast Counter":
    st.subheader("💵 TuFee Instant Counter (Collect Fee & Send WhatsApp Receipt)")
    students = conn.execute("SELECT * FROM students").fetchall()
    
    if students:
        s_options = [f"{r['student_id']} - {r['name']} ({r['mobile']})" for r in students]
        sel_s = st.selectbox("Select Candidate to Collect Fee:", s_options)
        sel_sid = sel_s.split(" - ")[0]
        s_data = conn.execute("SELECT * FROM students WHERE student_id = ?", (sel_sid,)).fetchone()
        
        p_rows = conn.execute("SELECT * FROM fees WHERE student_id = ?", (sel_sid,)).fetchall()
        tot_p = sum([r["amount"] for r in p_rows])
        net_f = s_data["net_fee"] if s_data["net_fee"] else 0.0
        due_b = max(0.0, net_f - tot_p)
        
        st.info(f"Student: **{s_data['name']}** | Course Fee: **₹{net_f:.2f}** | Current Due: **₹{due_b:.2f}**")
        
        teachers_list = [r["name"] for r in conn.execute("SELECT name FROM teachers").fetchall()]
        
        with st.form("counter_fee_form", clear_on_submit=True):
            pay_amt = st.number_input("Deposit Amount (₹)*", min_value=50.0, step=100.0, value=500.0)
            pay_mode = st.selectbox("Payment Mode", ["Cash", "UPI / GPay", "Bank Transfer"])
            collector = st.selectbox("Collected By (Teacher/Staff):", teachers_list)
            remarks = st.text_input("Remarks", value="Course Installment Fee")
            
            if st.form_submit_button("🟢 Collect Fee & Issue Receipt"):
                rc_num = f"REC-{datetime.date.today().strftime('%Y%m%d')}-{len(conn.execute('SELECT id FROM fees').fetchall())+1:03d}"
                today_str = str(datetime.date.today())
                conn.execute("INSERT INTO fees (receipt_no, student_id, date, amount, mode, collector, remarks) VALUES (?, ?, ?, ?, ?, ?, ?)",
                             (rc_num, sel_sid, today_str, pay_amt, pay_mode, collector, remarks))
                conn.commit()
                
                new_due = max(0.0, due_b - pay_amt)
                st.success(f"🧾 Receipt Issued: {rc_num} | Amount: ₹{pay_amt}")
                
                # Direct WhatsApp Link
                raw_msg = f"""🧾 *OFFICIAL FEE RECEIPT - SOFT TECH COMPUTERS & ZTC*
(Center Code: 4159 | Kamarchuburi, Sonitpur)

Dear {s_data['name']}, your course installment fee has been successfully received.

• Receipt No: *{rc_num}*
• Roll ID: *{sel_sid}*
• Course: *{s_data['course']}*
• Amount Paid: *₹{pay_amt:.2f}* ({pay_mode})
• Remaining Due Balance: *₹{new_due:.2f}*
• Collected By: *{collector}*
• Date: *{today_str}*

Thank you for learning with Soft Tech Computers & ZTC!
Contact: 9101026718"""
                wa_url = f"https://wa.me/91{s_data['mobile']}?text={urllib.parse.quote(raw_msg)}"
                st.markdown(f"""
                <a href="{wa_url}" target="_blank" style="text-decoration:none;">
                    <div style="background-color:#25D366; color:white; padding:10px 18px; border-radius:6px; font-weight:bold; display:inline-block; margin-top:8px;">
                        📲 Send Official WhatsApp Receipt to Student (+91 {s_data['mobile']})
                    </div>
                </a>
                """, unsafe_allow_html=True)
    else:
        st.info("No students registered yet.")

# -------------------------------------------------------------
# 5. ADMISSION & LIFECYCLE MANAGEMENT
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
            
            st.write(f"Candidate: **{s_rec['name']}** | Current Stage: <b style='color:#059669;'>{s_rec['lifecycle_stage']}</b>", unsafe_allow_html=True)
            
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
                    conn.execute("DELETE FROM daily_class_logs WHERE student_id = ?", (t_sid,))
                    conn.commit()
                    st.success(f"Candidate {t_sid} and all linked records deleted completely!")
                    st.rerun()

# -------------------------------------------------------------
# 6. FACULTY DESK, ADD TEACHER & ATTENDANCE
# -------------------------------------------------------------
elif menu == "👨‍🏫 Faculty Desk & Attendance":
    st.subheader("👨‍🏫 Faculty Management & Shift Attendance Punch")
    now_ist = datetime.datetime.now(IST)
    st.info(f"🕒 **Current IST Clock:** `{now_ist.strftime('%I:%M:%S %p (%d-%B-%Y)')}`")
    
    t_tab1, t_tab2 = st.tabs(["⏰ Teacher Daily Punch (In/Out)", "➕ Add New Teacher / Faculty"])
    
    with t_tab1:
        teachers_list = [r["name"] for r in conn.execute("SELECT name FROM teachers").fetchall()]
        if teachers_list:
            t_name = st.selectbox("Select Teacher Name:", teachers_list)
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
            st.write("**Recent Teacher Shift Logs:**")
            t_logs = conn.execute("SELECT teacher_name, date, shift, time_in, time_out, late_mins, status FROM teacher_punches ORDER BY id DESC LIMIT 10").fetchall()
            if t_logs:
                st.dataframe(pd.DataFrame([dict(r) for r in t_logs]), use_container_width=True)
        else:
            st.warning("No teachers registered yet. Please add a teacher in Tab 2.")
            
    with t_tab2:
        st.write("**➕ Register New Faculty / Teacher:**")
        with st.form("new_teacher_form", clear_on_submit=True):
            nt_name = st.text_input("Teacher Full Name*")
            nt_phone = st.text_input("Mobile Number*")
            nt_desig = st.selectbox("Designation", ["Computer Instructor", "Lab Assistant", "Guest Lecturer"])
            nt_shift = st.selectbox("Preferred Shift", ["All Shifts", "Morning Shift", "Evening Shift"])
            
            if st.form_submit_button("🟢 Register Teacher"):
                if nt_name and nt_phone:
                    try:
                        conn.execute("INSERT INTO teachers (name, phone, designation, shift, join_date) VALUES (?, ?, ?, ?, ?)",
                                     (nt_name.strip(), nt_phone.strip(), nt_desig, nt_shift, str(datetime.date.today())))
                        conn.commit()
                        st.success(f"🎉 Teacher {nt_name} Registered Successfully!")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("🚨 Teacher with this name is already registered!")
                else:
                    st.error("Please enter Name and Phone number!")
                    
        st.write("**Current Faculty List:**")
        all_teachers = conn.execute("SELECT * FROM teachers").fetchall()
        if all_teachers:
            st.dataframe(pd.DataFrame([dict(r) for r in all_teachers]), use_container_width=True)

# -------------------------------------------------------------
# 7. DIRECTOR FINANCIAL LOCKER (100% PRIVATE)
# -------------------------------------------------------------
elif menu == "🔐 Director Financial Locker (Private)":
    st.subheader("🔐 Director Private Financial Locker & Dues Tracker")
    st.write("এই টেবটো কেৱল ডিৰেক্টৰৰ ব্যক্তিগত ব্যৱহাৰৰ বাবে। শিক্ষক বা আন কোনোৱে কালেকচন চাব নোৱাৰে।")
    
    adm_pass = st.text_input("Enter Director Security Password:", type="password")
    if adm_pass == ADMIN_PIN:
        st.success("Authorized Director Access Granted! (Welcome Chiranjeeb Hazarika Sir)")
        
        all_fees = conn.execute("SELECT * FROM fees").fetchall()
        total_collected = sum([r["amount"] for r in all_fees])
        
        students_all = conn.execute("SELECT * FROM students").fetchall()
        total_expected = sum([r["net_fee"] for r in students_all if r["net_fee"]])
        total_due = max(0.0, total_expected - total_collected)
        
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Total Fee Collected (Net)", f"₹{total_collected:,.2f}")
        col_m2.metric("Total Pending Dues", f"₹{total_due:,.2f}", delta="-Pending", delta_color="inverse")
        col_m3.metric("Total Active Trainees", f"{len(students_all)} Students")
        
        st.markdown("---")
        st.write("**💰 Complete Student Outstanding Dues Ledger:**")
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
                    "Reminder Link": rem_link
                })
        if dues_list:
            dues_df = pd.DataFrame(dues_list)
            st.dataframe(dues_df[["Roll ID", "Name", "Mobile", "Course", "Net Fee", "Paid", "Due Balance"]], use_container_width=True)
            st.write("**Send Direct WhatsApp Reminders to Defaulters:**")
            for d in dues_list:
                st.markdown(f"• **{d['Name']}** (Due: {d['Due Balance']}): [📲 Send WhatsApp Reminder]({d['Reminder Link']})")
        else:
            st.success("🎉 All enrolled students have completely cleared their fees!")
            
        st.markdown("---")
        st.write("**🧾 All Fee Transaction Receipts (Full History):**")
        if all_fees:
            st.dataframe(pd.DataFrame([dict(r) for r in all_fees]), use_container_width=True)
    elif adm_pass:
        st.error("❌ Incorrect Director Password!")

conn.close()

# Footer
st.markdown("""
<div style="text-align:center; padding:20px; font-size:12px; color:#64748B; border-top:1px solid #E2E8F0; margin-top:40px;">
Soft Tech Computers & ZTC Enterprise Management System © 2026 | Center Code: 4159 | Kamarchuburi, Thelamara, Sonitpur - 784149
</div>
""", unsafe_allow_html=True)
