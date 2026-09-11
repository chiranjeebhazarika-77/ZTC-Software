import streamlit as st
import pandas as pd
import datetime
import pytz
import sqlite3
import urllib.parse
import base64
import requests
import json
import threading
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
GSHEET_WEBAPP_URL = "https://script.google.com/macros/s/AKfycbyeLkWRqD_gHSIQzFBUEJ2kv1e6DpbaUkBB9_CV5l_95k8kg-tSyBnCC50W1TN0XwES/exec"

# -------------------------------------------------------------
# BACKGROUND CLOUD SYNC & RECOVERY ENGINE
# -------------------------------------------------------------
def push_sheet_async(sheet_name, df):
    def _worker():
        try:
            records = [df.columns.tolist()] + df.fillna("").astype(str).values.tolist()
            payload = {"action": "overwrite", "sheet_name": sheet_name, "rows": records}
            requests.post(GSHEET_WEBAPP_URL, data=json.dumps(payload), headers={"Content-Type": "application/json"}, timeout=8)
        except Exception:
            pass
    t = threading.Thread(target=_worker)
    t.daemon = True
    t.start()

def fetch_sheet_data(sheet_name):
    try:
        res = requests.get(f"{GSHEET_WEBAPP_URL}?sheet_name={sheet_name}", timeout=4)
        if res.status_code == 200:
            data = res.json()
            if isinstance(data, list) and len(data) > 1:
                return pd.DataFrame(data[1:], columns=data[0], dtype=str)
    except Exception:
        pass
    return None

# -------------------------------------------------------------
# DATABASE ENGINE (SQLITE + AUTO-RECOVERY ON SERVER SLEEP)
# -------------------------------------------------------------
def get_db_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def add_col_if_missing(conn, table, col_def):
    c = conn.cursor()
    col_name = col_def.split()[0]
    c.execute(f"PRAGMA table_info({table})")
    cols = [r[1] for r in c.fetchall()]
    if col_name not in cols:
        try:
            c.execute(f"ALTER TABLE {table} ADD COLUMN {col_def}")
            conn.commit()
        except Exception:
            pass

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # System Settings (Password)
    c.execute('''
        CREATE TABLE IF NOT EXISTS system_settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    cur = c.execute("SELECT value FROM system_settings WHERE key = 'admin_pin'").fetchone()
    if not cur:
        c.execute("INSERT INTO system_settings (key, value) VALUES ('admin_pin', 'zaan123')")

    # Teachers Master
    c.execute('''
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            phone TEXT,
            email TEXT,
            qualification TEXT,
            designation TEXT,
            shift TEXT,
            address TEXT,
            id_proof TEXT,
            join_date TEXT
        )
    ''')
    add_col_if_missing(conn, "teachers", "email TEXT")
    add_col_if_missing(conn, "teachers", "qualification TEXT")
    add_col_if_missing(conn, "teachers", "address TEXT")
    add_col_if_missing(conn, "teachers", "id_proof TEXT")

    # Students Master
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            name TEXT,
            father_name TEXT,
            mother_name TEXT,
            gender TEXT,
            dob TEXT,
            mobile TEXT UNIQUE,
            address_vill TEXT,
            po TEXT,
            ps TEXT,
            pin TEXT,
            district TEXT,
            course TEXT,
            join_date TEXT,
            total_fee REAL,
            net_fee REAL,
            shift TEXT,
            status TEXT,
            lifecycle_stage TEXT,
            ho_reg_no TEXT,
            cert_serial_no TEXT,
            photo_base64 TEXT
        )
    ''')
    add_col_if_missing(conn, "students", "mother_name TEXT")
    add_col_if_missing(conn, "students", "gender TEXT")
    add_col_if_missing(conn, "students", "dob TEXT")
    add_col_if_missing(conn, "students", "address_vill TEXT")
    add_col_if_missing(conn, "students", "po TEXT")
    add_col_if_missing(conn, "students", "ps TEXT")
    add_col_if_missing(conn, "students", "pin TEXT")
    add_col_if_missing(conn, "students", "district TEXT")
    add_col_if_missing(conn, "students", "photo_base64 TEXT")

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
            marked_by TEXT,
            FOREIGN KEY (student_id) REFERENCES students (student_id) ON DELETE CASCADE
        )
    ''')
    add_col_if_missing(conn, "attendance", "marked_by TEXT")

    # Daily Student Teaching Log
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
    
    # Check default teacher
    check_t = c.execute("SELECT COUNT(*) FROM teachers").fetchone()[0]
    if check_t == 0:
        c.execute('''
            INSERT INTO teachers (name, phone, email, qualification, designation, shift, address, id_proof, join_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ("Chiranjeeb Hazarika (Director)", "9101026718", "ztcenterprise@gmail.com", "MCA / IT Specialist", "Director / Center Head", "All Shifts", "Kamarchuburi, Thelamara, Sonitpur", "ID-4159", str(datetime.date.today())))
    
    # Cloud Auto-Restoration if local is empty
    check_s = c.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    if check_s == 0:
        df_cloud_s = fetch_sheet_data("students_db")
        if df_cloud_s is not None and not df_cloud_s.empty:
            for _, r in df_cloud_s.iterrows():
                try:
                    c.execute('''
                        INSERT OR IGNORE INTO students (
                            student_id, name, father_name, mobile, course, net_fee, shift, status, lifecycle_stage
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        r.get("Student ID", ""), r.get("Name", ""), r.get("Father Name", ""), r.get("Mobile No", ""),
                        r.get("Course", ""), float(r.get("Net Fee", 2550.0) or 2550.0),
                        r.get("Shift", "Morning"), r.get("Status", "Active"), r.get("Stage", "Admission")
                    ))
                except Exception:
                    pass
                    
    conn.commit()
    conn.close()

init_db()

def sync_all_to_cloud(conn):
    try:
        st_df = pd.DataFrame([dict(r) for r in conn.execute("SELECT student_id as 'Student ID', name as 'Name', father_name as 'Father Name', mobile as 'Mobile No', course as 'Course', net_fee as 'Net Fee', shift as 'Shift', status as 'Status', lifecycle_stage as 'Stage' FROM students").fetchall()])
        if not st_df.empty: push_sheet_async("students_db", st_df)
        
        fee_df = pd.DataFrame([dict(r) for r in conn.execute("SELECT receipt_no as 'Receipt No', student_id as 'Student ID', date as 'Date', amount as 'Amount Paid', mode as 'Payment Mode', collector as 'Collected_By', remarks as 'Remarks' FROM fees").fetchall()])
        if not fee_df.empty: push_sheet_async("fees_db", fee_df)
    except Exception:
        pass

# -------------------------------------------------------------
# LIGHT & CRISP THEME CSS
# -------------------------------------------------------------
st.markdown("""
<style>
.stApp {
    background-color: #F8FAFC;
    color: #0F172A;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
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
        <span style="color:#059669; font-weight:bold;">🛡️ Cloud Protected (Zero-Loss Engine)</span>
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
    "📝 New Candidate Admission",
    "👨‍🏫 Faculty Desk & Attendance",
    "🔐 Director Master Command Center"
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
        st.info("💡 ছাত্ৰৰ নিজৰ পঞ্জীকৃত **ম’বাইল নম্বৰটোৱেই হ’ল লগ-ইন পাছৱৰ্ড**।")
        c_l1, c_l2 = st.columns(2)
        with c_l1:
            in_sid = st.text_input("Enter Student Roll ID (e.g. STC26-001):").strip().upper()
        with c_l2:
            in_mob = st.text_input("Enter Registered Mobile No (Password):", type="password").strip()
            
        col_btn1, col_btn2 = st.columns([1.2, 2])
        with col_btn1:
            if st.button("🟢 Login To My Dashboard", use_container_width=True):
                user = conn.execute("SELECT * FROM students WHERE student_id = ? AND mobile = ?", (in_sid, in_mob)).fetchone()
                if user:
                    st.session_state["s_auth_id"] = in_sid
                    st.rerun()
                else:
                    st.error("❌ Invalid Roll ID or Mobile Number!")
                    
        with col_btn2:
            wa_help_msg = "নমস্কাৰ ছাৰ, মই Soft Tech Computers & ZTC Academy-ৰ ছাত্ৰ। মই মোৰ লগ-ইন ৰোল নম্বৰ বা মোবাইল নম্বৰ পাহৰিছোঁ। অনুগ্ৰহ কৰি মোক সহায় কৰিবনে?"
            wa_help_url = f"https://wa.me/919101026718?text={urllib.parse.quote(wa_help_msg)}"
            st.markdown(f"""
            <a href="{wa_help_url}" target="_blank" style="text-decoration:none;">
                <div style="background-color:#F1F5F9; border:1px solid #CBD5E1; color:#0284C7; padding:8px 14px; border-radius:6px; font-weight:700; font-size:13px; text-align:center; display:inline-block; width:100%;">
                    📲 পাহৰি গ’ল নেকি? WhatsApp-ত সহায় বিচাৰক (Contact Office)
                </div>
            </a>
            """, unsafe_allow_html=True)
    else:
        sid = st.session_state["s_auth_id"]
        s = conn.execute("SELECT * FROM students WHERE student_id = ?", (sid,)).fetchone()
        
        col_hdr1, col_hdr2 = st.columns([1, 4])
        with col_hdr1:
            if s["photo_base64"]:
                st.image(s["photo_base64"], width=100)
            else:
                st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=90)
        with col_hdr2:
            st.markdown(f"""
            <div style="padding-top:10px;">
                <b style="font-size:20px; color:#0F172A;">{s['name']}</b><br>
                Roll ID: <b style="color:#0284C7;">{s['student_id']}</b> | Course: <b>{s['course']}</b> | Shift: <b>{s['shift']}</b><br>
                <span style="font-size:12px; color:#64748B;">Father: {s['father_name']} | Address: {s['address_vill'] or 'Sonitpur'}</span>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
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
        tab_a, tab_b, tab_c, tab_d = st.tabs(["📚 What I Learned (Daily Practice)", "📝 My Test Marks", "📸 Attendance Log", "💳 Fee Passbook"])
        
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
                st.dataframe(a_df[["date", "time_in", "status", "marked_by"]], use_container_width=True)
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
# 4. TUFEE FAST COUNTER
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
                
                sync_all_to_cloud(conn)
                
                new_due = max(0.0, due_b - pay_amt)
                st.success(f"🧾 Receipt Issued: {rc_num} | Amount: ₹{pay_amt}")
                
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
# 5. NEW CANDIDATE ADMISSION
# -------------------------------------------------------------
elif menu == "📝 New Candidate Admission":
    st.subheader("📝 Candidate New Admission (Detailed Data Capture)")
    existing_students = conn.execute("SELECT student_id FROM students").fetchall()
    year_code = str(datetime.date.today().year)[2:]
    next_id = f"STC{year_code}-{len(existing_students)+1:03d}"
    st.info(f"⚡ **Auto-Generated Roll ID:** `{next_id}`")
    
    with st.form("admission_detailed_form", clear_on_submit=True):
        st.write("##### 1. Personal & Guardian Details")
        col_a1, col_a2, col_a3 = st.columns(3)
        with col_a1:
            adm_name = st.text_input("Candidate Full Name*")
            adm_fname = st.text_input("Father's Name*")
        with col_a2:
            adm_mname = st.text_input("Mother's Name")
            adm_gender = st.selectbox("Gender*", ["Male", "Female", "Other"])
        with col_a3:
            adm_dob = st.date_input("Date of Birth*", value=datetime.date(2005, 1, 1), min_value=datetime.date(1985, 1, 1))
            adm_mob = st.text_input("Mobile Number (Unique / WhatsApp)*")
            
        st.write("##### 2. Residential Address")
        col_ad1, col_ad2, col_ad3, col_ad4 = st.columns(4)
        with col_ad1:
            adm_vill = st.text_input("Village / Town*")
        with col_ad2:
            adm_po = st.text_input("Post Office")
        with col_ad3:
            adm_ps = st.text_input("Police Station", value="Thelamara")
        with col_ad4:
            adm_dist = st.text_input("District", value="Sonitpur")
            adm_pin = st.text_input("PIN Code", value="784149")
            
        st.write("##### 3. Academic Course & Photo")
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            adm_course = st.selectbox("Course Selected*", [
                "PGDCA (12 Months)", "ADCA (12 Months)", "DCA (6 Months)", 
                "DTP (3 Months)", "Tally Prime with GST (3 Months)", "English Coaching"
            ])
            adm_shift = st.selectbox("Assigned Shift*", ["Morning (06:30-08:00 AM)", "Afternoon (04:00-05:30 PM)", "Evening (05:30-07:00 PM)"])
        with col_c2:
            adm_fee = st.number_input("Total Net Course Fee (₹)*", min_value=100.0, value=2550.0, step=50.0)
        with col_c3:
            photo_file = st.file_uploader("Upload Passport Size Photo (JPG/PNG)", type=["jpg", "jpeg", "png"])
            
        if st.form_submit_button("🟢 Complete Admission & Register"):
            if adm_name and adm_mob and adm_vill:
                photo_b64 = ""
                if photo_file:
                    photo_b64 = f"data:image/png;base64,{base64.b64encode(photo_file.read()).decode()}"
                try:
                    conn.execute('''
                        INSERT INTO students (
                            student_id, name, father_name, mother_name, gender, dob, mobile, 
                            address_vill, po, ps, pin, district, course, join_date, total_fee, 
                            net_fee, shift, status, lifecycle_stage, ho_reg_no, cert_serial_no, photo_base64
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        next_id, adm_name.upper(), adm_fname.upper(), adm_mname.upper(), adm_gender, str(adm_dob),
                        adm_mob, adm_vill.upper(), adm_po.upper(), adm_ps.upper(), adm_pin, adm_dist.upper(),
                        adm_course, str(datetime.date.today()), adm_fee, adm_fee, adm_shift, "Active",
                        "Admission", "Pending", "--", photo_b64
                    ))
                    conn.commit()
                    
                    sync_all_to_cloud(conn)
                    
                    st.success(f"🎉 Candidate Registered Successfully! Roll ID: {next_id}")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("🚨 This mobile number is already registered with another student!")
            else:
                st.error("Please fill Name, Mobile Number and Village/Town!")

# -------------------------------------------------------------
# 6. FACULTY DESK & ATTENDANCE
# -------------------------------------------------------------
elif menu == "👨‍🏫 Faculty Desk & Attendance":
    st.subheader("👨‍🏫 Faculty Management, Shift Punch & Student Attendance")
    now_ist = datetime.datetime.now(IST)
    st.info(f"🕒 **Current IST Clock:** `{now_ist.strftime('%I:%M:%S %p (%d-%B-%Y)')}`")
    
    t_tab1, t_tab2, t_tab3 = st.tabs([
        "📸 Take Student Attendance",
        "⏰ Teacher Self Punch (In/Out)",
        "➕ Register New Faculty (Detailed)"
    ])
    
    with t_tab1:
        st.write("##### 📸 Mark Daily Student Attendance")
        students_all = conn.execute("SELECT student_id, name, shift, course FROM students WHERE status='Active'").fetchall()
        teachers_list = [r["name"] for r in conn.execute("SELECT name FROM teachers").fetchall()]
        
        if students_all and teachers_list:
            col_att_m1, col_att_m2, col_att_m3 = st.columns(3)
            with col_att_m1:
                att_date = st.date_input("Attendance Date", value=datetime.date.today())
            with col_att_m2:
                teacher_marker = st.selectbox("Marked By (Teacher):", teachers_list, key="tch_marker")
            with col_att_m3:
                filter_shift = st.selectbox("Filter Shift:", ["All Shifts", "Morning (06:30-08:00 AM)", "Afternoon (04:00-05:30 PM)", "Evening (05:30-07:00 PM)"])
                
            filtered_students = students_all if filter_shift == "All Shifts" else [s for s in students_all if s["shift"] == filter_shift]
            st.write(f"Students Count: **{len(filtered_students)} Candidates**")
            
            with st.form("mark_student_att_form"):
                att_entries = {}
                for st_rec in filtered_students:
                    c_s1, c_s2 = st.columns([3, 2])
                    with c_s1:
                        st.write(f"**{st_rec['name']}** (`{st_rec['student_id']}`) - {st_rec['course']}")
                    with c_s2:
                        att_entries[st_rec['student_id']] = st.radio(
                            f"Status_{st_rec['student_id']}", 
                            ["Present", "Absent", "Late"], 
                            horizontal=True, 
                            key=f"att_rad_{st_rec['student_id']}",
                            label_visibility="collapsed"
                        )
                
                if st.form_submit_button("🟢 Save Attendance Register"):
                    time_str = now_ist.strftime("%I:%M %p")
                    date_str = str(att_date)
                    for sid_k, status_v in att_entries.items():
                        conn.execute("DELETE FROM attendance WHERE student_id = ? AND date = ?", (sid_k, date_str))
                        conn.execute('''
                            INSERT INTO attendance (student_id, date, time_in, status, marked_by)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (sid_k, date_str, time_str, status_v, teacher_marker))
                    conn.commit()
                    st.success(f"✅ Daily Attendance Saved Successfully on {date_str}!")
                    st.rerun()
        else:
            st.warning("Please add students and teachers first to take attendance.")
            
    with t_tab2:
        st.write("##### ⏰ Teacher Shift Punch & Automatic Salary Engine")
        teachers_list = [r["name"] for r in conn.execute("SELECT name FROM teachers").fetchall()]
        if teachers_list:
            t_name = st.selectbox("Select Teacher Name:", teachers_list, key="t_punch_sel")
            t_shift = st.selectbox("Assigned Shift:", [
                "Morning (06:30 - 08:00 AM)",
                "Afternoon (04:00 - 05:30 PM)",
                "Evening (05:30 - 07:00 PM)"
            ], key="t_shift_sel")
            
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
                
    with t_tab3:
        st.write("##### ➕ Register New Faculty Member (Detailed Profile)")
        with st.form("new_teacher_detailed_form", clear_on_submit=True):
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                nt_name = st.text_input("Faculty Full Name*")
                nt_phone = st.text_input("Mobile Number (WhatsApp)*")
                nt_email = st.text_input("Email Address")
                nt_qual = st.selectbox("Educational Qualification*", [
                    "MCA (Master of Computer Applications)",
                    "BCA / B.Sc IT / B.Tech",
                    "PGDCA / 'O' Level Certified",
                    "Graduate with Computer Diploma",
                    "Other Higher Qualification"
                ])
            with col_t2:
                nt_desig = st.selectbox("Designation*", ["Senior Computer Instructor", "Assistant Instructor", "Lab Assistant", "Guest Lecturer"])
                nt_shift = st.selectbox("Assigned Shift*", ["All Shifts", "Morning Shift (06:30-08:00 AM)", "Afternoon Shift (04:00-05:30 PM)", "Evening Shift (05:30-07:00 PM)"])
                nt_idproof = st.text_input("ID Proof (Aadhaar / Voter ID No)*")
                nt_address = st.text_area("Complete Residential Address (Vill, PO, PS, Dist, PIN)*")
                
            if st.form_submit_button("🟢 Register Faculty Member"):
                if nt_name and nt_phone and nt_address:
                    try:
                        conn.execute('''
                            INSERT INTO teachers (name, phone, email, qualification, designation, shift, address, id_proof, join_date)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (nt_name.strip(), nt_phone.strip(), nt_email.strip(), nt_qual, nt_desig, nt_shift, nt_address.strip(), nt_idproof.strip(), str(datetime.date.today())))
                        conn.commit()
                        st.success(f"🎉 Faculty Member '{nt_name}' Registered Successfully!")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("🚨 Teacher with this name is already registered!")
                else:
                    st.error("Please enter Name, Phone, and Complete Address!")

# -------------------------------------------------------------
# 7. DIRECTOR MASTER COMMAND CENTER (WITH LIVE CLOUD TEST)
# -------------------------------------------------------------
elif menu == "🔐 Director Master Command Center":
    st.subheader("🔐 Director Master Command Center (Executive Control)")
    
    stored_pin_row = conn.execute("SELECT value FROM system_settings WHERE key = 'admin_pin'").fetchone()
    current_admin_pin = stored_pin_row["value"] if stored_pin_row else "zaan123"
    
    adm_pass = st.text_input("Enter Director Master Security Password:", type="password")
    
    if adm_pass == current_admin_pin:
        st.success("Authorized Director Access Granted! Welcome Chiranjeeb Hazarika Sir.")
        
        dir_t1, dir_t2, dir_t3, dir_t4, dir_t5 = st.tabs([
            "📊 Executive Morning Briefing",
            "✏️ Edit & Remove Students",
            "💰 Financials & Fee Dues",
            "💾 1-Click Excel & Cloud Test",
            "🛡️ Security & Password Change"
        ])
        
        with dir_t1:
            st.write("##### ☀️ Executive Financial & Operational Overview")
            today_str = str(datetime.date.today())
            month_str = today_str[:7]
            
            all_fees = conn.execute("SELECT * FROM fees").fetchall()
            today_fees = [r for r in all_fees if r["date"] == today_str]
            today_cash = sum([r["amount"] for r in today_fees if r["mode"] == "Cash"])
            today_online = sum([r["amount"] for r in today_fees if r["mode"] != "Cash"])
            
            month_fees = [r for r in all_fees if r["date"].startswith(month_str)]
            month_tot = sum([r["amount"] for r in month_fees])
            
            all_students = conn.execute("SELECT * FROM students").fetchall()
            tot_expected = sum([r["net_fee"] for r in all_students if r["net_fee"]])
            tot_coll = sum([r["amount"] for r in all_fees])
            tot_due = max(0.0, tot_expected - tot_coll)
            
            c_b1, c_b2, c_b3, c_b4 = st.columns(4)
            c_b1.metric("Today's Total Cash in Hand", f"₹{today_cash:,.2f}", f"Online: ₹{today_online:,.2f}")
            c_b2.metric("This Month's Revenue", f"₹{month_tot:,.2f}")
            c_b3.metric("Total Outstanding Dues", f"₹{tot_due:,.2f}", delta="-Market Due", delta_color="inverse")
            c_b4.metric("Active Candidates", f"{len(all_students)} Trainees")
            
            st.markdown("---")
            st.write("##### ⚠️ Candidate Drop-out & Long Absence Alert")
            absent_alerts = []
            for s_rec in all_students:
                s_att = conn.execute("SELECT status FROM attendance WHERE student_id = ? ORDER BY id DESC LIMIT 5", (s_rec["student_id"],)).fetchall()
                if s_att:
                    recent_statuses = [r["status"] for r in s_att]
                    if recent_statuses.count("Absent") >= 3:
                        absent_alerts.append({"Roll ID": s_rec["student_id"], "Name": s_rec["name"], "Mobile": s_rec["mobile"], "Course": s_rec["course"], "Recent Trend": f"{recent_statuses.count('Absent')}/5 Days Absent"})
            if absent_alerts:
                st.warning("🚨 The following candidates have missed multiple consecutive classes! Please contact them:")
                st.dataframe(pd.DataFrame(absent_alerts), use_container_width=True)
            else:
                st.info("✅ All active students are maintaining regular classroom attendance.")
                
            st.write("##### ⏰ Today's Faculty Punctuality & Punch Status")
            today_punches = conn.execute("SELECT * FROM teacher_punches WHERE date = ?", (today_str,)).fetchall()
            if today_punches:
                st.dataframe(pd.DataFrame([dict(r) for r in today_punches]), use_container_width=True)
            else:
                st.write("No teacher punches recorded for today yet.")

        with dir_t2:
            st.write("##### ✏️ Update Student Profile & Permanent Cascade Deletion")
            all_students = conn.execute("SELECT * FROM students").fetchall()
            if all_students:
                s_opts = [f"{r['student_id']} - {r['name']} ({r['course']})" for r in all_students]
                chosen_s = st.selectbox("Select Student to Edit or Remove:", s_opts)
                target_sid = chosen_s.split(" - ")[0]
                s_data = conn.execute("SELECT * FROM students WHERE student_id = ?", (target_sid,)).fetchone()
                
                col_ed1, col_ed2 = st.columns(2)
                with col_ed1:
                    st.write("**Edit Candidate Information:**")
                    with st.form("edit_student_form"):
                        ed_name = st.text_input("Candidate Name", value=s_data["name"])
                        ed_fname = st.text_input("Father's Name", value=s_data["father_name"])
                        ed_mname = st.text_input("Mother's Name", value=s_data["mother_name"] or "")
                        ed_mob = st.text_input("Mobile Number", value=s_data["mobile"])
                        ed_course = st.selectbox("Course", ["PGDCA (12 Months)", "ADCA (12 Months)", "DCA (6 Months)", "DTP (3 Months)", "Tally Prime with GST (3 Months)", "English Coaching"], index=["PGDCA (12 Months)", "ADCA (12 Months)", "DCA (6 Months)", "DTP (3 Months)", "Tally Prime with GST (3 Months)", "English Coaching"].index(s_data["course"]) if s_data["course"] in ["PGDCA (12 Months)", "ADCA (12 Months)", "DCA (6 Months)", "DTP (3 Months)", "Tally Prime with GST (3 Months)", "English Coaching"] else 0)
                        ed_shift = st.selectbox("Shift", ["Morning (06:30-08:00 AM)", "Afternoon (04:00-05:30 PM)", "Evening (05:30-07:00 PM)"])
                        ed_fee = st.number_input("Course Net Fee (₹)", value=float(s_data["net_fee"]) if s_data["net_fee"] else 2550.0)
                        ed_stage = st.selectbox("Lifecycle Stage", ["Admission", "Learning/Tests", "Course Completed", "HO Registered", "Exam Appeared", "Certificate Handover"], index=["Admission", "Learning/Tests", "Course Completed", "HO Registered", "Exam Appeared", "Certificate Handover"].index(s_data["lifecycle_stage"]) if s_data["lifecycle_stage"] in ["Admission", "Learning/Tests", "Course Completed", "HO Registered", "Exam Appeared", "Certificate Handover"] else 0)
                        ed_ho = st.text_input("HO Registration No", value=s_data["ho_reg_no"] or "")
                        ed_cert = st.text_input("Certificate Serial No", value=s_data["cert_serial_no"] or "")
                        
                        if st.form_submit_button("🟢 Update Candidate Details"):
                            conn.execute('''
                                UPDATE students SET
                                    name = ?, father_name = ?, mother_name = ?, mobile = ?,
                                    course = ?, shift = ?, net_fee = ?, total_fee = ?,
                                    lifecycle_stage = ?, ho_reg_no = ?, cert_serial_no = ?
                                WHERE student_id = ?
                            ''', (ed_name.upper(), ed_fname.upper(), ed_mname.upper(), ed_mob.strip(),
                                  ed_course, ed_shift, ed_fee, ed_fee, ed_stage, ed_ho.strip(), ed_cert.strip(), target_sid))
                            conn.commit()
                            sync_all_to_cloud(conn)
                            st.success(f"✅ Student {target_sid} Updated Successfully!")
                            st.rerun()
                            
                with col_ed2:
                    st.write("**Permanent Cascade Delete:**")
                    st.warning(f"⚠️ Are you sure you want to permanently delete **{s_data['name']} ({target_sid})**? This will cleanly erase all linked fee deposits, test marks, daily learning logs, and attendance records.")
                    confirm_del = st.checkbox(f"I confirm permanent deletion of student {target_sid}")
                    if st.button("🔴 Permanently Delete Student"):
                        if confirm_del:
                            conn.execute("DELETE FROM students WHERE student_id = ?", (target_sid,))
                            conn.execute("DELETE FROM fees WHERE student_id = ?", (target_sid,))
                            conn.execute("DELETE FROM attendance WHERE student_id = ?", (target_sid,))
                            conn.execute("DELETE FROM marks WHERE student_id = ?", (target_sid,))
                            conn.execute("DELETE FROM daily_class_logs WHERE student_id = ?", (target_sid,))
                            conn.commit()
                            sync_all_to_cloud(conn)
                            st.success(f"🗑️ Candidate {target_sid} and all linked records removed completely!")
                            st.rerun()
                        else:
                            st.error("Please tick the confirmation checkbox above first!")
            else:
                st.info("No candidates registered.")

        with dir_t3:
            st.write("##### 💰 Defaulters & Outstanding Installment Ledger")
            dues_list = []
            all_students = conn.execute("SELECT * FROM students").fetchall()
            for s_item in all_students:
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
                st.write("**Send WhatsApp Reminder to Defaulters:**")
                for d in dues_list:
                    st.markdown(f"• **{d['Name']}** (Due: {d['Due Balance']}): [📲 Send WhatsApp Reminder]({d['Reminder Link']})")
            else:
                st.success("🎉 All enrolled students have completely cleared their fees!")

        with dir_t4:
            st.write("##### 💾 1-Click Excel Backup & Live Cloud Sync Test")
            st.info("Download complete real-time data to Excel/CSV or test live background Google Sheet connectivity.")
            
            if st.button("🌐 Test Live Google Sheet Connection Now"):
                try:
                    res_test = requests.get(f"{GSHEET_WEBAPP_URL}?sheet_name=students_db", timeout=5)
                    if res_test.status_code == 200:
                        st.success(f"✅ Google Sheet Connected Successfully! Response Code: {res_test.status_code} (Active Cloud Sync)")
                    else:
                        st.error(f"⚠️ Response received but status code: {res_test.status_code}")
                except Exception as e:
                    st.error(f"❌ Connection Failed: {e}")
                    
            st.markdown("<br>", unsafe_allow_html=True)
            c_exp1, c_exp2, c_exp3 = st.columns(3)
            with c_exp1:
                df_st = pd.DataFrame([dict(r) for r in conn.execute("SELECT student_id, name, father_name, mobile, course, shift, net_fee, join_date, lifecycle_stage, ho_reg_no, cert_serial_no FROM students").fetchall()])
                if not df_st.empty:
                    csv_st = df_st.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Export Students Master (CSV)", data=csv_st, file_name=f"Students_Backup_{today_str}.csv", mime="text/csv", use_container_width=True)
            with c_exp2:
                df_fee = pd.DataFrame([dict(r) for r in conn.execute("SELECT receipt_no, student_id, date, amount, mode, collector, remarks FROM fees").fetchall()])
                if not df_fee.empty:
                    csv_fee = df_fee.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Export Fee Receipts (CSV)", data=csv_fee, file_name=f"Fees_Ledger_{today_str}.csv", mime="text/csv", use_container_width=True)
            with c_exp3:
                df_att = pd.DataFrame([dict(r) for r in conn.execute("SELECT student_id, date, time_in, status, marked_by FROM attendance").fetchall()])
                if not df_att.empty:
                    csv_att = df_att.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Export Attendance (CSV)", data=csv_att, file_name=f"Attendance_Log_{today_str}.csv", mime="text/csv", use_container_width=True)

        with dir_t5:
            st.write("##### 🛡️ Change Director Security Password")
            with st.form("change_admin_pwd_form"):
                cur_pwd = st.text_input("Enter Current Password*", type="password")
                new_pwd = st.text_input("Enter New Password*", type="password")
                confirm_pwd = st.text_input("Confirm New Password*", type="password")
                
                if st.form_submit_button("🔒 Update Director Password"):
                    if cur_pwd != current_admin_pin:
                        st.error("Current password does not match!")
                    elif len(new_pwd) < 4:
                        st.error("New password must be at least 4 characters!")
                    elif new_pwd != confirm_pwd:
                        st.error("New password and confirm password do not match!")
                    else:
                        conn.execute("INSERT OR REPLACE INTO system_settings (key, value) VALUES ('admin_pin', ?)", (new_pwd.strip(),))
                        conn.commit()
                        st.success("🎉 Director Password updated successfully! Please remember your new password.")
                        st.rerun()
                        
    elif adm_pass:
        st.error("❌ Incorrect Director Security Password!")

conn.close()

# Footer
st.markdown("""
<div style="text-align:center; padding:20px; font-size:12px; color:#64748B; border-top:1px solid #E2E8F0; margin-top:40px;">
Soft Tech Computers & ZTC Enterprise Management System © 2026 | Center Code: 4159 | Kamarchuburi, Thelamara, Sonitpur - 784149
</div>
""", unsafe_allow_html=True)
