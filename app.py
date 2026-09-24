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
import math

# Page Setup
st.set_page_config(
    page_title="Soft-Tech Computers & ZTC Enterprise | Sarva India 4159",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

IST = pytz.timezone('Asia/Kolkata')
DB_FILE = "ztc_academy.db"
GSHEET_WEBAPP_URL = "https://script.google.com/macros/s/AKfycbyeLkWRqD_gHSIQzFBUEJ2kv1e6DpbaUkBB9_CV5l_95k8kg-tSyBnCC50W1TN0XwES/exec"

# -------------------------------------------------------------
# OFFICIAL COURSE CATALOG & STANDARDIZED PRICING
# -------------------------------------------------------------
COURSE_CATALOG = {
    "PGDCA (12 Months)": {
        "fee": 8499.0, 
        "duration": "12 Months", 
        "desc": "Post Graduate Diploma in Computer Applications (Programming, Database, Advanced Automation)"
    },
    "ADCA (12 Months)": {
        "fee": 8499.0, 
        "duration": "12 Months", 
        "desc": "Advanced Diploma in Computer Applications (Complete Office Computing & Commercial Modules)"
    },
    "DCA (6 Months)": {
        "fee": 4999.0, 
        "duration": "6 Months", 
        "desc": "Diploma in Computer Applications (Fundamentals, OS, Office Suite & Internet Tech)"
    },
    "Tally Prime with GST (3 Months)": {
        "fee": 3499.0, 
        "duration": "3 Months", 
        "desc": "Computerized Financial Accounting, Inventory Management & Direct GST Billing"
    },
    "DTP Graphics (3 Months)": {
        "fee": 3499.0, 
        "duration": "3 Months", 
        "desc": "Desktop Publishing & Designing Suite (Photoshop, PageMaker, CorelDraw)"
    },
    "English Coaching (6 Months)": {
        "fee": 3999.0, 
        "duration": "6 Months", 
        "desc": "Class 9 to 12 Board Curriculum, Applied Grammar & Spoken Communication"
    }
}

COURSE_NAMES = list(COURSE_CATALOG.keys())

# -------------------------------------------------------------
# LOGO LOADER (BASE64)
# -------------------------------------------------------------
def get_logo_html():
    for f in ["logo.jpg", "logo.png", "logo.jpeg"]:
        if os.path.exists(f):
            try:
                with open(f, "rb") as img_f:
                    b64 = base64.b64encode(img_f.read()).decode()
                    return f'<img src="data:image/jpeg;base64,{b64}" style="height:48px; width:48px; border-radius:8px; object-fit:contain; background:white; padding:2px; border:1px solid #CBD5E1;">'
            except Exception:
                pass
    return '<span style="background:#0284C7; color:white; font-weight:900; padding:8px 12px; border-radius:8px; font-size:16px;">STC</span>'

# -------------------------------------------------------------
# ASYNCHRONOUS GOOGLE SHEET SYNC
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
        res = requests.get(f"{GSHEET_WEBAPP_URL}?sheet_name={sheet_name}", timeout=6)
        if res.status_code == 200:
            data = res.json()
            if isinstance(data, list) and len(data) > 1:
                return pd.DataFrame(data[1:], columns=data[0], dtype=str)
    except Exception:
        pass
    return None

# -------------------------------------------------------------
# DATABASE ENGINE (SQLITE)
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
    
    # System Settings
    c.execute('''CREATE TABLE IF NOT EXISTS system_settings (key TEXT PRIMARY KEY, value TEXT)''')
    if not c.execute("SELECT value FROM system_settings WHERE key = 'admin_pin'").fetchone():
        c.execute("INSERT INTO system_settings (key, value) VALUES ('admin_pin', 'zaan123')")
    if not c.execute("SELECT value FROM system_settings WHERE key = 'staff_pin'").fetchone():
        c.execute("INSERT INTO system_settings (key, value) VALUES ('staff_pin', 'ztc4159')")

    # Teachers Master
    c.execute('''
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE, phone TEXT, email TEXT, qualification TEXT,
            designation TEXT, shift TEXT, address TEXT, id_proof TEXT, join_date TEXT
        )
    ''')
    add_col_if_missing(conn, "teachers", "email TEXT")
    add_col_if_missing(conn, "teachers", "qualification TEXT")
    add_col_if_missing(conn, "teachers", "address TEXT")
    add_col_if_missing(conn, "teachers", "id_proof TEXT")

    # Students Master
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY, name TEXT, father_name TEXT, mother_name TEXT,
            gender TEXT, dob TEXT, mobile TEXT UNIQUE, address_vill TEXT, po TEXT,
            ps TEXT, pin TEXT, district TEXT, course TEXT, join_date TEXT,
            total_fee REAL, net_fee REAL, shift TEXT, status TEXT, lifecycle_stage TEXT,
            ho_reg_no TEXT, cert_serial_no TEXT, photo_base64 TEXT
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
            id INTEGER PRIMARY KEY AUTOINCREMENT, receipt_no TEXT, student_id TEXT,
            date TEXT, amount REAL, mode TEXT, collector TEXT, remarks TEXT,
            FOREIGN KEY (student_id) REFERENCES students (student_id) ON DELETE CASCADE
        )
    ''')
    
    # Student Attendance
    c.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT, student_id TEXT, date TEXT,
            time_in TEXT, status TEXT, marked_by TEXT,
            FOREIGN KEY (student_id) REFERENCES students (student_id) ON DELETE CASCADE
        )
    ''')
    add_col_if_missing(conn, "attendance", "marked_by TEXT")

    # Daily Teaching Log
    c.execute('''
        CREATE TABLE IF NOT EXISTS daily_class_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, student_id TEXT,
            teacher_name TEXT, topic TEXT, class_type TEXT, remarks TEXT,
            FOREIGN KEY (student_id) REFERENCES students (student_id) ON DELETE CASCADE
        )
    ''')
    
    # Test Marks
    c.execute('''
        CREATE TABLE IF NOT EXISTS marks (
            id INTEGER PRIMARY KEY AUTOINCREMENT, student_id TEXT, test_topic TEXT,
            marks_obtained REAL, total_marks REAL, date TEXT,
            FOREIGN KEY (student_id) REFERENCES students (student_id) ON DELETE CASCADE
        )
    ''')
    
    # Teacher Attendance & Shifts
    c.execute('''
        CREATE TABLE IF NOT EXISTS teacher_punches (
            id INTEGER PRIMARY KEY AUTOINCREMENT, teacher_name TEXT, date TEXT,
            shift TEXT, time_in TEXT, time_out TEXT, late_mins INTEGER,
            penalty_cut REAL, net_batch_earning REAL, status TEXT
        )
    ''')
    
    # Public Enquiries
    c.execute('''
        CREATE TABLE IF NOT EXISTS enquiries (
            id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, name TEXT,
            mobile TEXT, course TEXT, address TEXT
        )
    ''')
    
    # Teacher Ratings
    c.execute('''
        CREATE TABLE IF NOT EXISTS teacher_ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, student_id TEXT,
            teacher_name TEXT, rating_teaching INTEGER, rating_understanding INTEGER,
            rating_character INTEGER, review_comment TEXT,
            FOREIGN KEY (student_id) REFERENCES students (student_id) ON DELETE CASCADE
        )
    ''')
    
    if c.execute("SELECT COUNT(*) FROM teachers").fetchone()[0] == 0:
        c.execute('''
            INSERT INTO teachers (name, phone, email, qualification, designation, shift, address, id_proof, join_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ("Chiranjeeb Hazarika (Director)", "9101026718", "ztcenterprise@gmail.com", "MCA / IT Specialist", "Director / Center Head", "All Shifts", "Kamarchuburi, Thelamara, Sonitpur", "ID-4159", str(datetime.date.today())))
        c.execute('''
            INSERT OR IGNORE INTO teachers (name, phone, email, qualification, designation, shift, address, id_proof, join_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ("BIJOY KURMI", "9101026718", "bijoy@gmail.com", "Senior Computer Faculty", "Instructor", "Morning Slot: 07:00 AM - 08:30 AM", "Kamarchuburi, Sonitpur", "ID-STAFF", str(datetime.date.today())))
    
    conn.commit()
    conn.close()

init_db()

# Multi-Table Cloud Sync
def sync_all_to_cloud(conn):
    try:
        st_df = pd.DataFrame([dict(r) for r in conn.execute("SELECT student_id as 'Student ID', name as 'Name', father_name as 'Father Name', mobile as 'Mobile No', course as 'Course', net_fee as 'Net Fee', shift as 'Shift', status as 'Status', lifecycle_stage as 'Stage' FROM students").fetchall()])
        if not st_df.empty: push_sheet_async("students_db", st_df)
        
        fee_df = pd.DataFrame([dict(r) for r in conn.execute("SELECT receipt_no as 'Receipt No', student_id as 'Student ID', date as 'Date', amount as 'Amount Paid', mode as 'Payment Mode', collector as 'Collected_By', remarks as 'Remarks' FROM fees").fetchall()])
        if not fee_df.empty: push_sheet_async("fees_db", fee_df)

        t_df = pd.DataFrame([dict(r) for r in conn.execute("SELECT name as 'Teacher Name', phone as 'Mobile', designation as 'Designation', qualification as 'Qualification', shift as 'Shift', id_proof as 'ID Proof', address as 'Address', join_date as 'Join Date' FROM teachers").fetchall()])
        if not t_df.empty: push_sheet_async("teachers_db", t_df)

        tp_df = pd.DataFrame([dict(r) for r in conn.execute("SELECT date as 'Date', teacher_name as 'Teacher Name', shift as 'Shift', time_in as 'Time In', time_out as 'Time Out', late_mins as 'Late (Mins)', net_batch_earning as 'Net Shift Earning', status as 'Status' FROM teacher_punches").fetchall()])
        if not tp_df.empty: push_sheet_async("teacher_attendance", tp_df)

        att_df = pd.DataFrame([dict(r) for r in conn.execute("SELECT student_id as 'Student ID', date as 'Date', time_in as 'Time In', status as 'Status', marked_by as 'Marked By' FROM attendance").fetchall()])
        if not att_df.empty: push_sheet_async("attendance_db", att_df)

        syl_df = pd.DataFrame([dict(r) for r in conn.execute("SELECT date as 'Date', student_id as 'Student ID', teacher_name as 'Teacher', topic as 'Topic Covered', class_type as 'Mode', remarks as 'Feedback' FROM daily_class_logs").fetchall()])
        if not syl_df.empty: push_sheet_async("syllabus_logs", syl_df)

        enq_df = pd.DataFrame([dict(r) for r in conn.execute("SELECT date as 'Date', name as 'Candidate Name', mobile as 'Mobile', course as 'Course Interested', address as 'Address' FROM enquiries").fetchall()])
        if not enq_df.empty: push_sheet_async("enquiries_db", enq_df)
    except Exception:
        pass

def restore_database_from_cloud(conn):
    restored_items = []
    df_st = fetch_sheet_data("students_db")
    if df_st is not None and not df_st.empty:
        for _, r in df_st.iterrows():
            sid = r.get("Student ID", "").strip()
            if sid:
                name = r.get("Name", "")
                fname = r.get("Father Name", "")
                mob = r.get("Mobile No", "")
                course = r.get("Course", "")
                default_f = COURSE_CATALOG.get(course, {}).get("fee", 4999.0)
                net_fee = float(r.get("Net Fee", default_f)) if r.get("Net Fee") else default_f
                shift = r.get("Shift", "Morning Slot: 07:00 AM - 08:30 AM")
                stat = r.get("Status", "Active")
                stage = r.get("Stage", "Admission")
                conn.execute('''
                    INSERT OR REPLACE INTO students (
                        student_id, name, father_name, mobile, course, total_fee, net_fee, shift, status, lifecycle_stage, join_date, ho_reg_no, cert_serial_no
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (sid, name, fname, mob, course, net_fee, net_fee, shift, stat, stage, str(datetime.date.today()), "Pending", "--"))
        restored_items.append("Students")

    df_fee = fetch_sheet_data("fees_db")
    if df_fee is not None and not df_fee.empty:
        for _, r in df_fee.iterrows():
            rc = r.get("Receipt No", "").strip()
            sid = r.get("Student ID", "").strip()
            if rc and sid:
                dt = r.get("Date", str(datetime.date.today()))
                amt = float(r.get("Amount Paid", 0.0)) if r.get("Amount Paid") else 0.0
                mode = r.get("Payment Mode", "Cash")
                col = r.get("Collected_By", "Office")
                rem = r.get("Remarks", "Fee Deposit")
                chk = conn.execute("SELECT id FROM fees WHERE receipt_no = ?", (rc,)).fetchone()
                if not chk:
                    conn.execute('''
                        INSERT INTO fees (receipt_no, student_id, date, amount, mode, collector, remarks)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (rc, sid, dt, amt, mode, col, rem))
        restored_items.append("Fees")

    df_t = fetch_sheet_data("teachers_db")
    if df_t is not None and not df_t.empty:
        for _, r in df_t.iterrows():
            t_name = r.get("Teacher Name", "").strip()
            if t_name:
                conn.execute('''
                    INSERT OR IGNORE INTO teachers (name, phone, designation, qualification, shift, id_proof, address, join_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (t_name, r.get("Mobile", ""), r.get("Designation", "Instructor"), r.get("Qualification", ""), r.get("Shift", "All Shifts"), r.get("ID Proof", ""), r.get("Address", ""), str(datetime.date.today())))
        restored_items.append("Teachers")

    conn.commit()
    return restored_items

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
    padding: 12px 24px;
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
    font-size: 26px;
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
.pill-red { background: #DC2626; color: white; }

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
logo_markup = get_logo_html()
st.markdown(f"""
<div class="top-navbar">
    <div style="display:flex; align-items:center; gap:14px;">
        {logo_markup}
        <div>
            <b style="font-size:17px; color:#0F172A;">Soft-Tech Computers & ZTC Enterprise</b><br>
            <span style="font-size:11px; color:#64748B;">SITED Govt Licensed (MCA/ROC Reg. U72900HP2008NPL030981) | Center Code: 4159 (Kamarchuburi, Sonitpur)</span>
        </div>
    </div>
    <div style="font-size:12px; color:#475569; text-align:right;">
        Sarva Franchise Renewal: <b style="color:#059669;">27-Dec-2026</b><br>
        <span style="color:#0284C7; font-weight:bold;">🛡️ SITED Cloud Connected</span>
    </div>
</div>
""", unsafe_allow_html=True)

conn = get_db_connection()

admin_pin_val = conn.execute("SELECT value FROM system_settings WHERE key = 'admin_pin'").fetchone()["value"]
staff_pin_row = conn.execute("SELECT value FROM system_settings WHERE key = 'staff_pin'").fetchone()
staff_pin_val = staff_pin_row["value"] if staff_pin_row else "ztc4159"

# -------------------------------------------------------------
# SIDEBAR
# -------------------------------------------------------------
st.sidebar.title("💻 Portal Navigation")
menu = st.sidebar.radio("Select Operational Desk:", [
    "🌐 Public Dashboard & Enquiry",
    "🔑 Student Self-Service Portal",
    "⚡ Bulk Session & Attendance Desk",
    "💵 TuFee Fast Counter",
    "📝 New Candidate Admission",
    "📚 Daily Class Activity (Lab/Theory)",
    "👨‍🏫 Faculty Desk & Honorarium",
    "🔐 Director Master Command Center"
])

st.sidebar.markdown("---")
st.sidebar.write("### ☁️ Cloud & Google Sheet")
if st.sidebar.button("📥 Pull / Restore Data from Google Sheet", use_container_width=True):
    items = restore_database_from_cloud(conn)
    if items:
        st.sidebar.success(f"✅ Restored: {', '.join(items)} from Google Sheet!")
        st.rerun()
    else:
        st.sidebar.info("Cloud already up-to-date or no records fetched.")

if st.sidebar.button("🔄 Push All Data to Google Sheet", use_container_width=True):
    sync_all_to_cloud(conn)
    st.sidebar.success("🚀 Records Synced to Cloud Successfully!")

def verify_staff_access(module_name):
    st.markdown(f"#### 🔒 Staff Access Control: {module_name}")
    st.caption("Authorized faculty and administrative personnel only.")
    input_pin = st.text_input("Enter Staff / Instructor PIN:", type="password", key=f"pin_{module_name}")
    if input_pin in [staff_pin_val, admin_pin_val]:
        return True
    elif input_pin:
        st.error("❌ Invalid PIN! Please contact the Director.")
        return False
    return False

# -------------------------------------------------------------
# 1. PUBLIC DASHBOARD & ENQUIRY (PRIVACY PROTECTED)
# -------------------------------------------------------------
if menu == "🌐 Public Dashboard & Enquiry":
    st.markdown("""
    <div class="hero-wrapper">
        <div class="hero-tag-pill">🏛️ SARVA I.T & EDUCATIONAL DEVELOPMENT (INDIA) • SITED ACCREDITED</div>
        <h1 class="hero-main-title">Soft-Tech Computers & ZTC Enterprise</h1>
        <p style="color:#475569; font-size:14px; line-height:1.7; margin:0 0 12px 0;">
            Accredited Center Code <b style="color:#C2410C;">4159</b> under Sarva Education (SITED). Licensed by Govt. of India (Lic No: 2/114/T-1/08/D, MCA/NR New Delhi, ROC Certified Reg No/CIN: U72900HP2008NPL030981).
        </p>
        <div>
            <span class="pill-item pill-orange"># CENTER CODE: 4159</span>
            <span class="pill-item pill-green">✓ SITED Govt Verified</span>
            <span class="pill-item pill-blue">🏛️ ISO 9001:2015 Certified</span>
            <span class="pill-item pill-red">📅 Valid Till: 27-Dec-2026</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col_p1, col_p2 = st.columns([1.6, 1.2])
    with col_p1:
        st.markdown("""
        <div class="portal-card">
            <div class="card-header-flex">
                <b style="color:#0F172A; font-size:16px;">🏛️ Accredited Professional Programs Offered</b>
                <span style="color:#0284C7; font-size:11px; font-weight:bold;">SARVA CODE: 4159</span>
            </div>
            <p style="color:#475569; font-size:13.5px; line-height:1.9;">
                • <b>PGDCA (12 Months):</b> Post Graduate Diploma in Computer Applications<br>
                • <b>ADCA (12 Months):</b> Advanced Diploma in Computer Applications<br>
                • <b>DCA (6 Months):</b> Diploma in Computer Applications & Automation<br>
                • <b>Tally Prime with GST (3 Months):</b> Financial Accounting, Inventory & Taxation<br>
                • <b>DTP Graphics (3 Months):</b> Graphic Designing (Photoshop, PageMaker, Corel)<br>
                • <b>English Coaching (6 Months):</b> Board English Curriculum (Class 9 to 12)<br>
                <span style="font-size:12px; color:#059669; font-weight:bold;">💡 Sunday Free Practice Class (SFPC) facility available for regular enrolled trainees.</span>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_p2:
        st.markdown("""
        <div class="portal-card">
            <div class="card-header-flex">
                <b style="color:#0F172A; font-size:16px;">ℹ️ Official Center Credentials</b>
                <span style="color:#059669; font-size:11px; font-weight:bold;">ACCREDITED</span>
            </div>
            <div style="font-size:13px; line-height:2.0; color:#334155;">
                🏢 <b>Center Name:</b> Soft-Tech Computers<br>
                📍 <b>Location:</b> Kamarchuburi, Thelamara, Sonitpur, Assam - 784149<br>
                📞 <b>Director Desk:</b> Chiranjeeb Hazarika (9101026718)<br>
                🌐 <b>National Network:</b> Sarva India (SITED)
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    st.subheader("📜 Certificate & Center Verification")
    col_v1, col_v2 = st.columns([1.5, 1.5])
    with col_v1:
        v_id = st.text_input("Local Institute Roll ID (e.g. STC26-001):", key="pub_v_id").strip().upper()
        if v_id:
            match_s = conn.execute("SELECT * FROM students WHERE student_id = ?", (v_id,)).fetchone()
            if match_s:
                st.success(f"✅ RECORD VERIFIED: {match_s['name']} | Course: {match_s['course']} | Status: {match_s['status']} (Center Code: 4159)")
            else:
                st.error("❌ No official matching record found in institute database.")
    with col_v2:
        st.write("**Verify on National Sarva Head Office Portal:**")
        st.markdown("""
        <a href="https://sarvaindia.com/index.aspx" target="_blank" style="text-decoration:none;">
            <div style="background-color:#0284C7; color:white; padding:10px 16px; border-radius:6px; font-weight:bold; text-align:center; margin-top:24px;">
                🔍 Verify Center Code 4159 on SarvaIndia.com
            </div>
        </a>
        """, unsafe_allow_html=True)
            
    st.markdown("---")
    
    # -------------------------------------------------------------
    # PRIVACY PROTECTED ENQUIRY & PROSPECTUS UNLOCK ENGINE
    # -------------------------------------------------------------
    st.subheader("📝 Request Course Details, Syllabus & Official Fee Prospectus")
    st.caption("Submit your details below to instantly unlock the official curriculum syllabus and approved fee structure.")
    
    with st.form("enquiry_form", clear_on_submit=False):
        col_enq1, col_enq2 = st.columns(2)
        with col_enq1:
            enq_name = st.text_input("Candidate / Guardian Full Name*")
            enq_mob = st.text_input("Mobile No (WhatsApp)*", placeholder="10-digit number")
        with col_enq2:
            enq_course = st.selectbox("Select Course Interested:*", COURSE_NAMES)
            enq_addr = st.text_input("Village / Town Address*")
            
        submitted = st.form_submit_button("🟢 Unlock Course Details & Fee Structure")
        
        if submitted:
            if enq_name.strip() and len(enq_mob.strip()) >= 10 and enq_addr.strip():
                # Save lead securely to database
                conn.execute("INSERT INTO enquiries (date, name, mobile, course, address) VALUES (?, ?, ?, ?, ?)",
                             (str(datetime.date.today()), enq_name.upper().strip(), enq_mob.strip(), enq_course, enq_addr.upper().strip()))
                conn.commit()
                sync_all_to_cloud(conn)
                
                # Retrieve course specs
                c_data = COURSE_CATALOG[enq_course]
                
                st.markdown(f"""
                <div style="background:#F0FDF4; border:2px solid #22C55E; border-radius:10px; padding:18px; margin-top:14px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <b style="font-size:18px; color:#15803D;">🎉 Official Fee Structure Unlocked for: {enq_course}</b>
                        <span style="background:#166534; color:white; font-size:11px; font-weight:bold; padding:4px 10px; border-radius:14px;">VERIFIED LEAD</span>
                    </div>
                    <hr style="margin:10px 0; border-top:1px solid #BBF7D0;">
                    <div style="font-size:14px; color:#1F2937; line-height:1.9;">
                        • <b>Candidate Name:</b> {enq_name.upper()}<br>
                        • <b>Course Duration:</b> {c_data['duration']}<br>
                        • <b>Curriculum Focus:</b> {c_data['desc']}<br>
                        • <b>Approved Total Package Fee:</b> <b style="font-size:22px; color:#166534;">₹{c_data['fee']:,.0f}/-</b> <span style="font-size:12px; color:#4B5563;">(Installment options available)</span><br>
                        • <b>National Certification:</b> Sarva Education (SITED Govt Approved, Center: 4159)
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Pre-filled WhatsApp response link for student
                prospectus_wa_msg = f"""Hello Sir, I submitted an enquiry for *{enq_course}* at Soft-Tech Computers & ZTC Academy.
Name: {enq_name.upper()}
Address: {enq_addr.upper()}
Please share the detailed syllabus and class schedule."""
                prospectus_wa_url = f"https://wa.me/919101026718?text={urllib.parse.quote(prospectus_wa_msg)}"
                
                st.markdown(f"""
                <a href="{prospectus_wa_url}" target="_blank" style="text-decoration:none;">
                    <div style="background-color:#25D366; color:white; padding:12px 18px; border-radius:6px; font-weight:bold; font-size:14px; text-align:center; margin-top:12px; display:inline-block;">
                        📲 Receive Official Prospectus & Class Schedule on WhatsApp
                    </div>
                </a>
                """, unsafe_allow_html=True)
            else:
                st.error("Please fill your Full Name, 10-digit WhatsApp Number, and Village/Town Address to view course fee details!")

# -------------------------------------------------------------
# 2. STUDENT SELF-SERVICE PORTAL (WITH SFPC ELIGIBILITY ENGINE)
# -------------------------------------------------------------
elif menu == "🔑 Student Self-Service Portal":
    st.subheader("🔑 Student Dashboard (Attendance, Passbook, Learning Logs & SFPC Status)")
    
    if "s_auth_id" not in st.session_state:
        st.session_state["s_auth_id"] = None

    if not st.session_state["s_auth_id"]:
        st.info("💡 Default Password: Use your registered 10-digit mobile number to access your student dashboard.")
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
                    st.error("❌ Invalid Roll ID or Mobile Number! Use 'Pull Data from Google Sheet' on sidebar if registered recently.")
                    
        with col_btn2:
            wa_help_msg = "Hello Sir, I am a registered student at Soft-Tech Computers & ZTC Academy. I need assistance retrieving my login credentials."
            wa_help_url = f"https://wa.me/919101026718?text={urllib.parse.quote(wa_help_msg)}"
            st.markdown(f"""
            <a href="{wa_help_url}" target="_blank" style="text-decoration:none;">
                <div style="background-color:#F1F5F9; border:1px solid #CBD5E1; color:#0284C7; padding:8px 14px; border-radius:6px; font-weight:700; font-size:13px; text-align:center; display:inline-block; width:100%;">
                    📲 Forgot Credentials? Request Help via WhatsApp (Support Desk)
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
                <span style="font-size:12px; color:#64748B;">Sarva HO Reg No: <b>{s['ho_reg_no'] or 'Processing at Head Office'}</b> | Center Code: <b>4159</b></span>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        att_rows = conn.execute("SELECT * FROM attendance WHERE student_id = ?", (sid,)).fetchall()
        tot_days = len(att_rows)
        present_days = len([r for r in att_rows if r["status"] in ["Present", "Late"]])
        att_pct = (present_days / tot_days * 100) if tot_days > 0 else 100.0
        
        fee_rows = conn.execute("SELECT * FROM fees WHERE student_id = ?", (sid,)).fetchall()
        tot_paid = sum([r["amount"] for r in fee_rows])
        net_f = s["net_fee"] if s["net_fee"] else COURSE_CATALOG.get(s["course"], {}).get("fee", 4999.0)
        due_f = max(0.0, net_f - tot_paid)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Classroom Attendance", f"{att_pct:.1f}%", f"{present_days}/{tot_days} Days")
        c2.metric("Fee Deposited", f"₹{tot_paid:,.2f}", f"Total Net: ₹{net_f:,.2f}")
        c3.metric("Remaining Due", f"₹{due_f:,.2f}", delta="-Due" if due_f > 0 else "Cleared", delta_color="inverse")
        
        st.markdown("---")
        
        # SFPC Eligibility Engine
        try:
            join_dt = datetime.datetime.strptime(s["join_date"], "%Y-%m-%d").date()
        except Exception:
            join_dt = datetime.date.today()
        today = datetime.date.today()
        months_active = max(1, (today.year - join_dt.year) * 12 + today.month - join_dt.month + 1)
        
        sfpc_total_payable = min(net_f, 999.0 + (months_active - 1) * 550.0)
        sfpc_paid_pct = (tot_paid / sfpc_total_payable * 100) if sfpc_total_payable > 0 else 100.0
        
        sfpc_fee_eligible = sfpc_paid_pct >= 50.0
        sfpc_att_eligible = att_pct >= 75.0
        sfpc_overall_eligible = sfpc_fee_eligible and sfpc_att_eligible
        
        st.markdown("#### 🏛️ Sunday Free Practice Class (SFPC) Access Card")
        if sfpc_overall_eligible:
            st.success("🟢 **SFPC PASS: ELIGIBLE (Free Weekend Lab Unlocked)**\nYou are eligible for complimentary Sunday practice sessions. Maintain regular attendance and installment schedule.")
        else:
            st.error("🔴 **SFPC ACCESS LOCKED (Criteria Not Met)**\nComplimentary weekend lab practice requires minimum 75% classroom attendance and at least 50% cumulative fee clearance.")
            
        c_sf1, c_sf2, c_sf3 = st.columns(3)
        c_sf1.info(f"**Payable Till Current Month:** ₹{sfpc_total_payable:,.2f}\n\n**Total Paid:** ₹{tot_paid:,.2f} ({sfpc_paid_pct:.1f}% cleared)")
        c_sf2.info(f"**Fee Status (Min 50% Required):**\n\n{'✅ PASS (>= 50% Paid)' if sfpc_fee_eligible else '❌ FAILED (< 50% Paid)'}")
        c_sf3.info(f"**Attendance Status (Min 75% Required):**\n\n{'✅ PASS (>= 75%)' if sfpc_att_eligible else '❌ FAILED (< 75%)'}")
        
        st.markdown("---")
        tab_a, tab_b, tab_c, tab_d, tab_e, tab_f = st.tabs([
            "📚 What I Learned (Daily Practice)", 
            "📝 Test Marks", 
            "📸 Attendance Register", 
            "💳 Fee Passbook",
            "⭐ Rate My Teacher (Feedback)",
            "🏛️ Sarva India HO Verification"
        ])
        
        with tab_a:
            st.write("**Topics Practiced & Teacher Lab Performance Feedback:**")
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
            st.write("**Class Attendance History:**")
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
                    <h3 style="margin:0;">SOFT-TECH COMPUTERS & ZTC ENTERPRISE</h3>
                    <span style="font-size:11px; color:#64748B;">Student Fee Installment Passbook (Center Code: 4159)</span>
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
            
        with tab_e:
            st.write("##### ⭐ Rate Your Instructor (Teacher Quality & Behavior Review)")
            st.caption("Your honest rating helps the Director maintain top teaching quality. (Strictly Confidential)")
            teachers_list = [r["name"] for r in conn.execute("SELECT name FROM teachers").fetchall()]
            
            with st.form("teacher_rating_form", clear_on_submit=True):
                target_teacher = st.selectbox("Select Teacher to Review:*", teachers_list)
                col_r1, col_r2, col_r3 = st.columns(3)
                with col_r1:
                    r_teach = st.slider("1. Teaching Methodology & Subject Clarity (1 to 5 Stars)*", min_value=1, max_value=5, value=5)
                with col_r2:
                    r_und = st.slider("2. Concept Explanation & Doubt Clearing (1 to 5 Stars)*", min_value=1, max_value=5, value=5)
                with col_r3:
                    r_char = st.slider("3. Faculty Professionalism & Punctuality (1 to 5 Stars)*", min_value=1, max_value=5, value=5)
                    
                rev_text = st.text_input("Your Feedback or Suggestion (Optional):", placeholder="e.g. Clears doubts very politely and thoroughly.")
                
                if st.form_submit_button("🟢 Submit Teacher Review"):
                    conn.execute('''
                        INSERT INTO teacher_ratings (date, student_id, teacher_name, rating_teaching, rating_understanding, rating_character, review_comment)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (str(datetime.date.today()), sid, target_teacher, r_teach, r_und, r_char, rev_text.strip()))
                    conn.commit()
                    st.success(f"🎉 Thank you, {s['name']}! Your review for {target_teacher} has been submitted securely.")

        with tab_f:
            st.write("##### 🏛️ National Sarva India Certificate Verification")
            st.info(f"Your Sarva Head Office Registration: `{s['ho_reg_no'] or 'Processing at Head Office'}`")
            st.markdown("""
            <a href="https://sarvaindia.com/index.aspx" target="_blank" style="text-decoration:none;">
                <div style="background-color:#059669; color:white; padding:10px 16px; border-radius:6px; font-weight:bold; display:inline-block;">
                    🔍 Verify on Sarva India Head Office Portal (sarvaindia.com)
                </div>
            </a>
            """, unsafe_allow_html=True)
            
        if st.button("🔒 Logout"):
            st.session_state["s_auth_id"] = None
            st.rerun()

# -------------------------------------------------------------
# 3. BULK SESSION & ATTENDANCE DESK
# -------------------------------------------------------------
elif menu == "⚡ Bulk Session & Attendance Desk":
    st.subheader("⚡ Bulk Session & Attendance Fast Register")
    st.caption("Perform rapid multi-candidate attendance marking and direct fee receipt generation in one centralized view.")
    
    if verify_staff_access("Bulk Session Desk"):
        all_students = conn.execute("SELECT student_id, name, shift, course FROM students WHERE status='Active'").fetchall()
        teachers_list = [r["name"] for r in conn.execute("SELECT name FROM teachers").fetchall()]
        
        if all_students:
            c_bk1, c_bk2, c_bk3 = st.columns(3)
            with c_bk1:
                bk_date = st.date_input("Session Date:", value=datetime.date.today())
            with c_bk2:
                bk_teacher = st.selectbox("Staff / Incharge:", teachers_list)
            with c_bk3:
                bk_filter_shift = st.selectbox("Filter Shift:", ["All Shifts", "Morning Slot: 07:00 AM - 08:30 AM", "Afternoon Slot: 04:00 PM - 05:30 PM", "Evening Slot: 05:30 PM - 07:00 PM"])
                
            filtered_list = all_students if bk_filter_shift == "All Shifts" else [s for s in all_students if s["shift"] == bk_filter_shift]
            st.write(f"Total Trainees in Queue: **{len(filtered_list)} Candidates**")
            
            with st.form("bulk_register_form"):
                bulk_status = {}
                bulk_fee_amt = {}
                
                for s_item in filtered_list:
                    c_b1, c_b2, c_b3 = st.columns([2.5, 1.8, 1.5])
                    with c_b1:
                        st.markdown(f"**{s_item['name']}** (`{s_item['student_id']}`)<br><span style='font-size:11px; color:#64748B;'>Course: {s_item['course']}</span>", unsafe_allow_html=True)
                    with c_b2:
                        bulk_status[s_item['student_id']] = st.radio(f"Status_{s_item['student_id']}", ["Present", "Absent", "Late"], horizontal=True, key=f"bk_stat_{s_item['student_id']}", label_visibility="collapsed")
                    with c_b3:
                        bulk_fee_amt[s_item['student_id']] = st.number_input(f"Deposit (₹) {s_item['student_id']}", min_value=0.0, step=50.0, value=0.0, key=f"bk_fee_{s_item['student_id']}", label_visibility="collapsed")
                    st.markdown("<hr style='margin:4px 0;'>", unsafe_allow_html=True)
                    
                if st.form_submit_button("🟢 Save Bulk Attendance & Process Receipts"):
                    date_str = str(bk_date)
                    now_str = datetime.datetime.now(IST).strftime("%I:%M %p")
                    fees_logged = 0
                    
                    for sid_k, stat_v in bulk_status.items():
                        conn.execute("DELETE FROM attendance WHERE student_id = ? AND date = ?", (sid_k, date_str))
                        conn.execute("INSERT INTO attendance (student_id, date, time_in, status, marked_by) VALUES (?, ?, ?, ?, ?)",
                                     (sid_k, date_str, now_str, stat_v, bk_teacher))
                        
                        deposit = bulk_fee_amt[sid_k]
                        if deposit > 0:
                            rc_num = f"REC-{datetime.date.today().strftime('%Y%m%d')}-{len(conn.execute('SELECT id FROM fees').fetchall())+1:03d}"
                            conn.execute("INSERT INTO fees (receipt_no, student_id, date, amount, mode, collector, remarks) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                         (rc_num, sid_k, date_str, deposit, "Cash", bk_teacher, "Bulk Counter Deposit"))
                            fees_logged += 1
                            
                    conn.commit()
                    sync_all_to_cloud(conn)
                    st.success(f"🎉 Bulk register saved! {len(filtered_list)} attendance records verified and {fees_logged} fee deposits logged.")
                    st.rerun()
        else:
            st.info("No active candidates registered in database.")

# -------------------------------------------------------------
# 4. TUFEE FAST COUNTER
# -------------------------------------------------------------
elif menu == "💵 TuFee Fast Counter":
    st.subheader("💵 TuFee Instant Counter (Collect Fee & Send WhatsApp Receipt)")
    if verify_staff_access("TuFee Counter"):
        students = conn.execute("SELECT * FROM students").fetchall()
        if students:
            s_options = [f"{r['student_id']} - {r['name']} ({r['mobile']})" for r in students]
            sel_s = st.selectbox("Select Candidate to Collect Fee:", s_options)
            sel_sid = sel_s.split(" - ")[0]
            s_data = conn.execute("SELECT * FROM students WHERE student_id = ?", (sel_sid,)).fetchone()
            
            p_rows = conn.execute("SELECT * FROM fees WHERE student_id = ?", (sel_sid,)).fetchall()
            tot_p = sum([r["amount"] for r in p_rows])
            net_f = s_data["net_fee"] if s_data["net_fee"] else COURSE_CATALOG.get(s_data["course"], {}).get("fee", 4999.0)
            due_b = max(0.0, net_f - tot_p)
            
            st.info(f"Student: **{s_data['name']}** | Course: **{s_data['course']}** | Standard Fee: **₹{net_f:.2f}** | Current Due: **₹{due_b:.2f}**")
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
                    
                    raw_msg = f"""🧾 *OFFICIAL FEE RECEIPT - SOFT-TECH COMPUTERS & ZTC*
(Center Code: 4159 | Sarva India Affiliated)

Dear {s_data['name']}, your course installment fee has been successfully received.

• Receipt No: *{rc_num}*
• Roll ID: *{sel_sid}*
• Course: *{s_data['course']}*
• Amount Paid: *₹{pay_amt:.2f}* ({pay_mode})
• Remaining Due Balance: *₹{new_due:.2f}*
• Collected By: *{collector}*
• Date: *{today_str}*

Thank you for learning with Soft-Tech Computers & ZTC!
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
            st.info("No candidates registered.")

# -------------------------------------------------------------
# 5. NEW CANDIDATE ADMISSION (AUTO-FEE FROM CATALOG)
# -------------------------------------------------------------
elif menu == "📝 New Candidate Admission":
    st.subheader("📝 Candidate New Admission (Standardized Course Fee Mapping)")
    if verify_staff_access("Admission Desk"):
        existing_students = conn.execute("SELECT student_id FROM students").fetchall()
        year_code = str(datetime.date.today().year)[2:]
        next_id = f"STC{year_code}-{len(existing_students)+1:03d}"
        st.info(f"⚡ **Auto-Generated Roll ID:** `{next_id}`")
        
        c_pick1, c_pick2 = st.columns([2, 1.5])
        with c_pick1:
            adm_course = st.selectbox("Select Accredited Course*", COURSE_NAMES, key="pick_adm_course")
        default_course_fee = COURSE_CATALOG[adm_course]["fee"]
        with c_pick2:
            st.markdown(f"""
            <div style="background:#F0FDF4; border:1px solid #86EFAC; border-radius:8px; padding:10px 16px; margin-top:12px;">
                <span style="font-size:12px; color:#15803D;">Standard Package Fee:</span><br>
                <b style="font-size:20px; color:#166534;">₹{default_course_fee:,.0f}</b> <span style="font-size:12px; color:#64748B;">({COURSE_CATALOG[adm_course]['duration']})</span>
            </div>
            """, unsafe_allow_html=True)
            
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
                
            st.write("##### 3. Academic Batch & Fee Configuration")
            col_c1, col_c2, col_c3 = st.columns(3)
            with col_c1:
                adm_shift = st.selectbox("Assigned Shift Slot*", [
                    "Morning Slot: 07:00 AM - 08:30 AM", 
                    "Afternoon Slot: 04:00 PM - 05:30 PM", 
                    "Evening Slot: 05:30 PM - 07:00 PM"
                ])
            with col_c2:
                adm_fee = st.number_input("Confirmed Net Fee (₹)*", min_value=100.0, value=default_course_fee, step=50.0)
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
                        st.success(f"🎉 Candidate Registered Successfully! Roll ID: {next_id} | Official Fee: ₹{adm_fee:,.2f}")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("🚨 This mobile number is already registered with another student!")
            else:
                st.error("Please fill Name, Mobile Number and Village/Town!")

# -------------------------------------------------------------
# 6. DAILY CLASS ACTIVITY
# -------------------------------------------------------------
elif menu == "📚 Daily Class Activity (Lab/Theory)":
    st.subheader("📚 Daily Classroom Activity & Practical Lab Register")
    if verify_staff_access("Daily Class Activity"):
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
                        class_mode = st.radio("Session Type / Mode:*", [
                            "Practical Lab Only", 
                            "Theory Lecture Only", 
                            "Both (Theory + Practical)",
                            "SFPC (Sunday Free Practice)"
                        ], horizontal=True)
                    with col_c2:
                        today_topic = st.text_input("Topic Covered (e.g. MS Word Resume, Tally GST Billing, Typing Speed Test)*")
                        class_remarks = st.text_input("Teacher Feedback / Lab Performance*", value="Completed Practical Exercise Well")
                        
                    if st.form_submit_button("🟢 Save Today's Class Entry"):
                        if today_topic:
                            sid_val = sel_st.split(" - ")[0]
                            conn.execute('''
                                INSERT INTO daily_class_logs (date, student_id, teacher_name, topic, class_type, remarks)
                                VALUES (?, ?, ?, ?, ?, ?)
                            ''', (str(datetime.date.today()), sid_val, sel_tch, today_topic, class_mode, class_remarks))
                            conn.commit()
                            sync_all_to_cloud(conn)
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
# 7. FACULTY DESK & STRICT HONORARIUM ENGINE (₹230 / 3 SHIFTS)
# -------------------------------------------------------------
elif menu == "👨‍🏫 Faculty Desk & Honorarium":
    st.subheader("👨‍🏫 Faculty Management & Session-Linked Honorarium Engine")
    now_ist = datetime.datetime.now(IST)
    st.info(f"🕒 **Current IST Clock:** `{now_ist.strftime('%I:%M:%S %p (%d-%B-%Y)')}`")
    
    if verify_staff_access("Faculty Desk"):
        t_tab1, t_tab2, t_tab3 = st.tabs([
            "⏰ Teacher Shift Punch (Strict IST Window)",
            "➕ Register Faculty Member (Detailed)",
            "📋 Faculty Ledger & Shift History"
        ])
        
        with t_tab1:
            st.markdown("""
            ##### ⏱️ Shift Schedule & Verified Honorarium Policy
            *Daily Allocation: **₹230.00** across 3 strict shifts (**₹76.67** per verified 90-minute session). Payout is strictly session-verified.*
            """)
            
            teachers_list = [r["name"] for r in conn.execute("SELECT name FROM teachers").fetchall()]
            if teachers_list:
                t_name = st.selectbox("Select Faculty Name:", teachers_list, key="t_punch_sel")
                t_shift = st.selectbox("Select Batch Slot (90 Mins):", [
                    "Morning Slot: 07:00 AM - 08:30 AM",
                    "Afternoon Slot: 04:00 PM - 05:30 PM",
                    "Evening Slot: 05:30 PM - 07:00 PM"
                ], key="t_shift_sel")
                
                if "Morning" in t_shift:
                    shift_start = 7 * 60
                    shift_end = 8 * 60 + 30
                    window_open = 6 * 60 + 45
                elif "Afternoon" in t_shift:
                    shift_start = 16 * 60
                    shift_end = 17 * 60 + 30
                    window_open = 15 * 60 + 45
                else:
                    shift_start = 17 * 60 + 30
                    shift_end = 19 * 60
                    window_open = 17 * 60 + 15
                    
                current_mins = now_ist.hour * 60 + now_ist.minute
                in_window = window_open <= current_mins <= shift_end
                late_by = max(0, current_mins - shift_start)
                is_late = late_by > 5
                
                base_shift_honorarium = round(230.0 / 3.0, 2)
                per_min_rate = 230.0 / 270.0
                penalty_amt = round(min(late_by * per_min_rate, base_shift_honorarium), 2) if is_late else 0.0
                net_shift_earning = round(max(0.0, base_shift_honorarium - penalty_amt), 2)
                
                col_tp1, col_tp2 = st.columns(2)
                with col_tp1:
                    if st.button("🟢 Teacher Punch IN (Session Start)", use_container_width=True):
                        if in_window:
                            today_str = str(datetime.date.today())
                            time_str = now_ist.strftime("%I:%M %p")
                            stat_val = "Late" if is_late else "On-Time"
                            conn.execute('''
                                INSERT INTO teacher_punches (teacher_name, date, shift, time_in, time_out, late_mins, penalty_cut, net_batch_earning, status)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (t_name, today_str, t_shift, time_str, "--", late_by, penalty_amt, net_shift_earning, stat_val))
                            conn.commit()
                            sync_all_to_cloud(conn)
                            if is_late:
                                st.warning(f"🚨 Punched IN with {late_by} mins delay! Late Penalty: ₹{penalty_amt:.2f} | Net Session Honorarium: ₹{net_shift_earning:.2f}")
                            else:
                                st.success(f"✅ On-Time Session Punch IN at {time_str}! Verified Payout: ₹{base_shift_honorarium:.2f}")
                            st.rerun()
                        else:
                            st.error(f"❌ Outside Approved Shift Window! Current time does not match {t_shift}.")
                            
                with col_tp2:
                    if st.button("🔴 Teacher Punch OUT (Session Concluded)", use_container_width=True):
                        today_str = str(datetime.date.today())
                        time_str = now_ist.strftime("%I:%M %p")
                        conn.execute("UPDATE teacher_punches SET time_out = ? WHERE teacher_name = ? AND date = ? AND time_out = '--'",
                                     (time_str, t_name, today_str))
                        conn.commit()
                        sync_all_to_cloud(conn)
                        st.success(f"✅ Punched OUT at {time_str}! Shift marked completed.")
                        st.rerun()
            else:
                st.warning("Please register faculty members first.")
                
        with t_tab2:
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
                    nt_shift = st.selectbox("Assigned Shift*", [
                        "All Shifts", 
                        "Morning Slot: 07:00 AM - 08:30 AM",
                        "Afternoon Slot: 04:00 PM - 05:30 PM",
                        "Evening Slot: 05:30 PM - 07:00 PM"
                    ])
                    nt_idproof = st.text_input("ID Proof (Voter ID / Driving License)*")
                    nt_address = st.text_area("Complete Residential Address (Vill, PO, PS, Dist, PIN)*")
                    
                if st.form_submit_button("🟢 Register Faculty Member"):
                    if nt_name and nt_phone and nt_address:
                        try:
                            conn.execute('''
                                INSERT INTO teachers (name, phone, email, qualification, designation, shift, address, id_proof, join_date)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (nt_name.strip(), nt_phone.strip(), nt_email.strip(), nt_qual, nt_desig, nt_shift, nt_address.strip(), nt_idproof.strip(), str(datetime.date.today())))
                            conn.commit()
                            sync_all_to_cloud(conn)
                            st.success(f"🎉 Faculty Member '{nt_name}' Registered & Synced Successfully!")
                            st.rerun()
                        except sqlite3.IntegrityError:
                            st.error("🚨 Teacher with this name is already registered!")
                    else:
                        st.error("Please enter Name, Phone, and Complete Address!")
                        
        with t_tab3:
            st.write("##### 📋 Verified Shift History & Honorarium Logs")
            t_logs = conn.execute("SELECT date, teacher_name, shift, time_in, time_out, late_mins, penalty_cut, net_batch_earning, status FROM teacher_punches ORDER BY id DESC LIMIT 25").fetchall()
            if t_logs:
                st.dataframe(pd.DataFrame([dict(r) for r in t_logs]), use_container_width=True)
            else:
                st.info("No punch logs recorded yet.")

# -------------------------------------------------------------
# 8. DIRECTOR MASTER COMMAND CENTER
# -------------------------------------------------------------
elif menu == "🔐 Director Master Command Center":
    st.subheader("🔐 Director Master Command Center (Executive Control)")
    adm_pass = st.text_input("Enter Director Master Security Password:", type="password")
    
    if adm_pass == admin_pin_val:
        st.success("Authorized Director Access Granted! Welcome Chiranjeeb Hazarika Sir.")
        
        dir_t1, dir_t2, dir_t3, dir_t4, dir_t5, dir_t6, dir_t7 = st.tabs([
            "📊 Executive Morning Briefing",
            "📋 Public Enquiries (Leads)",
            "⭐ Teacher Ratings & Audit",
            "✏️ Edit & Remove Students",
            "💰 Financials & Fee Dues",
            "💾 1-Click Excel Backup",
            "🛡️ Security & PIN Settings"
        ])
        
        # TAB 1: EXECUTIVE BRIEFING
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
            st.write("##### 🏛️ Sarva Education Head Office Sync")
            st.info("Official Sarva Center Renewal Due Date: **27-Dec-2026** | Total Students Registered at HO: **159**")
            st.markdown("""
            <a href="https://admin.sarvaeducation.in/admin/AdminHome.aspx" target="_blank" style="text-decoration:none;">
                <div style="background-color:#0284C7; color:white; padding:8px 14px; border-radius:6px; font-weight:bold; display:inline-block;">
                    🌐 Open Official Sarva Admin HO Portal (admin.sarvaeducation.in)
                </div>
            </a>
            """, unsafe_allow_html=True)

        # TAB 2: PUBLIC ENQUIRIES (LEADS MANAGEMENT)
        with dir_t2:
            st.write("##### 📋 Public Course & Admission Enquiries (Leads)")
            enq_rows = conn.execute("SELECT * FROM enquiries ORDER BY id DESC").fetchall()
            if enq_rows:
                st.info(f"Total Enquiries Received: **{len(enq_rows)} Candidates**")
                for enq in enq_rows:
                    with st.container():
                        col_eq1, col_eq2 = st.columns([3, 1.2])
                        with col_eq1:
                            target_c_fee = COURSE_CATALOG.get(enq['course'], {}).get("fee", 4999.0)
                            st.markdown(f"""
                            <b>{enq['name']}</b> | Course: <b style="color:#0284C7;">{enq['course']}</b> (Package Fee: ₹{target_c_fee:,.0f})<br>
                            <span style="font-size:12px; color:#64748B;">Date: {enq['date']} | Mobile: <b>{enq['mobile']}</b> | Address: {enq['address']}</span>
                            """, unsafe_allow_html=True)
                        with col_eq2:
                            lead_msg = f"Hello {enq['name']}, this is Chiranjeeb Hazarika from Soft-Tech Computers & ZTC Academy. Regarding your enquiry for {enq['course']}, would you like to schedule an admission counseling session at our center?"
                            wa_lead_url = f"https://wa.me/91{enq['mobile']}?text={urllib.parse.quote(lead_msg)}"
                            st.markdown(f"""
                            <a href="{wa_lead_url}" target="_blank" style="text-decoration:none;">
                                <div style="background-color:#25D366; color:white; padding:6px 12px; border-radius:6px; font-size:12px; font-weight:bold; text-align:center;">
                                    📲 Chat on WhatsApp
                                </div>
                            </a>
                            """, unsafe_allow_html=True)
                        st.markdown("<hr style='margin:8px 0;'>", unsafe_allow_html=True)
            else:
                st.info("No public enquiries received yet.")

        # TAB 3: TEACHER RATINGS
        with dir_t3:
            st.write("##### ⭐ Faculty Performance & Student Star Ratings (Director Confidential)")
            all_ratings = conn.execute('''
                SELECT r.date, r.student_id, s.name as student_name, r.teacher_name, 
                       r.rating_teaching, r.rating_understanding, r.rating_character, r.review_comment
                FROM teacher_ratings r
                LEFT JOIN students s ON r.student_id = s.student_id
                ORDER BY r.id DESC
            ''').fetchall()
            
            if all_ratings:
                r_df = pd.DataFrame([dict(r) for r in all_ratings])
                r_df["Avg Score (out of 5)"] = ((r_df["rating_teaching"] + r_df["rating_understanding"] + r_df["rating_character"]) / 3.0).round(1)
                
                st.write("**Overall Faculty Average Scores:**")
                summary_grp = r_df.groupby("teacher_name").agg({
                    "rating_teaching": "mean",
                    "rating_understanding": "mean",
                    "rating_character": "mean",
                    "Avg Score (out of 5)": "mean"
                }).round(2).reset_index()
                st.dataframe(summary_grp, use_container_width=True)
                
                st.markdown("---")
                st.write("**Individual Student Reviews & Comments:**")
                st.dataframe(r_df[["date", "student_name", "teacher_name", "rating_teaching", "rating_understanding", "rating_character", "Avg Score (out of 5)", "review_comment"]], use_container_width=True)
            else:
                st.info("No student feedback/ratings submitted yet.")

        # TAB 4: EDIT STUDENTS
        with dir_t4:
            st.write("##### ✏️ Update Student Profile & Sarva Head Office Reg No")
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
                        ed_course = st.selectbox("Course", COURSE_NAMES, index=COURSE_NAMES.index(s_data["course"]) if s_data["course"] in COURSE_NAMES else 0)
                        ed_shift = st.selectbox("Shift Slot", [
                            "Morning Slot: 07:00 AM - 08:30 AM", 
                            "Afternoon Slot: 04:00 PM - 05:30 PM", 
                            "Evening Slot: 05:30 PM - 07:00 PM"
                        ])
                        ed_fee = st.number_input("Course Net Fee (₹)", value=float(s_data["net_fee"]) if s_data["net_fee"] else COURSE_CATALOG[ed_course]["fee"])
                        ed_stage = st.selectbox("Lifecycle Stage", ["Admission", "Learning/Tests", "Course Completed", "HO Registered", "Exam Appeared", "Certificate Handover"], index=["Admission", "Learning/Tests", "Course Completed", "HO Registered", "Exam Appeared", "Certificate Handover"].index(s_data["lifecycle_stage"]) if s_data["lifecycle_stage"] in ["Admission", "Learning/Tests", "Course Completed", "HO Registered", "Exam Appeared", "Certificate Handover"] else 0)
                        ed_ho = st.text_input("Sarva HO Registration No (From admin.sarvaeducation.in)", value=s_data["ho_reg_no"] or "")
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
                    st.warning(f"⚠️ Are you sure you want to permanently delete **{s_data['name']} ({target_sid})**?")
                    confirm_del = st.checkbox(f"I confirm permanent deletion of student {target_sid}")
                    if st.button("🔴 Permanently Delete Student"):
                        if confirm_del:
                            conn.execute("DELETE FROM students WHERE student_id = ?", (target_sid,))
                            conn.execute("DELETE FROM fees WHERE student_id = ?", (target_sid,))
                            conn.execute("DELETE FROM attendance WHERE student_id = ?", (target_sid,))
                            conn.execute("DELETE FROM marks WHERE student_id = ?", (target_sid,))
                            conn.execute("DELETE FROM daily_class_logs WHERE student_id = ?", (target_sid,))
                            conn.execute("DELETE FROM teacher_ratings WHERE student_id = ?", (target_sid,))
                            conn.commit()
                            sync_all_to_cloud(conn)
                            st.success(f"🗑️ Candidate {target_sid} removed completely!")
                            st.rerun()
                        else:
                            st.error("Please tick confirmation checkbox first!")
            else:
                st.info("No candidates registered.")

        # TAB 5: FINANCIALS
        with dir_t5:
            st.write("##### 💰 Defaulters & Outstanding Installment Ledger")
            dues_list = []
            all_students = conn.execute("SELECT * FROM students").fetchall()
            for s_item in all_students:
                s_id = s_item["student_id"]
                paid_sum = sum([r["amount"] for r in conn.execute("SELECT amount FROM fees WHERE student_id = ?", (s_id,)).fetchall()])
                net_amt = s_item["net_fee"] if s_item["net_fee"] else COURSE_CATALOG.get(s_item["course"], {}).get("fee", 4999.0)
                due_amt = max(0.0, net_amt - paid_sum)
                if due_amt > 0:
                    raw_rem = f"""📢 *FEE DUE REMINDER - SOFT-TECH COMPUTERS & ZTC*
Dear {s_item['name']} ({s_item['student_id']}),
This is a reminder that your course fee installment of *₹{due_amt:.2f}* for course *{s_item['course']}* is pending.
Please clear the balance at the center desk.
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

        # TAB 6: BACKUP
        with dir_t6:
            st.write("##### 💾 1-Click Institute Complete Database Backup")
            c_exp1, c_exp2, c_exp3 = st.columns(3)
            with c_exp1:
                df_st = pd.DataFrame([dict(r) for r in conn.execute("SELECT student_id, name, father_name, mobile, course, shift, net_fee, join_date, lifecycle_stage, ho_reg_no, cert_serial_no FROM students").fetchall()])
                if not df_st.empty:
                    st.download_button("📥 Export Students (CSV)", data=df_st.to_csv(index=False).encode('utf-8'), file_name=f"Students_Backup_{today_str}.csv", mime="text/csv", use_container_width=True)
            with c_exp2:
                df_fee = pd.DataFrame([dict(r) for r in conn.execute("SELECT receipt_no, student_id, date, amount, mode, collector, remarks FROM fees").fetchall()])
                if not df_fee.empty:
                    st.download_button("📥 Export Fees (CSV)", data=df_fee.to_csv(index=False).encode('utf-8'), file_name=f"Fees_Ledger_{today_str}.csv", mime="text/csv", use_container_width=True)
            with c_exp3:
                df_att = pd.DataFrame([dict(r) for r in conn.execute("SELECT student_id, date, time_in, status, marked_by FROM attendance").fetchall()])
                if not df_att.empty:
                    st.download_button("📥 Export Attendance (CSV)", data=df_att.to_csv(index=False).encode('utf-8'), file_name=f"Attendance_Log_{today_str}.csv", mime="text/csv", use_container_width=True)

        # TAB 7: SECURITY SETTINGS
        with dir_t7:
            st.write("##### 🛡️ Change Security PINs (Director & Staff)")
            col_sec1, col_sec2 = st.columns(2)
            with col_sec1:
                st.write("**1. Change Director Master Password:**")
                with st.form("change_admin_pwd_form"):
                    cur_pwd = st.text_input("Current Director Password*", type="password")
                    new_pwd = st.text_input("New Director Password*", type="password")
                    confirm_pwd = st.text_input("Confirm New Password*", type="password")
                    if st.form_submit_button("🔒 Update Director Password"):
                        if cur_pwd != admin_pin_val:
                            st.error("Current password does not match!")
                        elif len(new_pwd) < 4:
                            st.error("Must be at least 4 characters!")
                        elif new_pwd != confirm_pwd:
                            st.error("Passwords do not match!")
                        else:
                            conn.execute("INSERT OR REPLACE INTO system_settings (key, value) VALUES ('admin_pin', ?)", (new_pwd.strip(),))
                            conn.commit()
                            st.success("🎉 Director Password updated successfully!")
                            st.rerun()
            with col_sec2:
                st.write("**2. Change Staff / Faculty Access PIN:**")
                st.caption(f"Current Staff PIN is: `{staff_pin_val}`")
                with st.form("change_staff_pin_form"):
                    new_s_pin = st.text_input("Enter New Staff PIN*", value=staff_pin_val)
                    if st.form_submit_button("🔑 Update Staff PIN"):
                        if len(new_s_pin.strip()) >= 4:
                            conn.execute("INSERT OR REPLACE INTO system_settings (key, value) VALUES ('staff_pin', ?)", (new_s_pin.strip(),))
                            conn.commit()
                            st.success("🎉 Staff PIN updated successfully!")
                            st.rerun()
                        else:
                            st.error("Staff PIN must be at least 4 characters!")
    elif adm_pass:
        st.error("❌ Incorrect Director Security Password!")

conn.close()

# Footer
st.markdown("""
<div style="text-align:center; padding:20px; font-size:12px; color:#64748B; border-top:1px solid #E2E8F0; margin-top:40px;">
Soft-Tech Computers & ZTC Enterprise Management System © 2026 | SITED Center Code: 4159 | Kamarchuburi, Thelamara, Sonitpur - 784149
</div>
""", unsafe_allow_html=True)
