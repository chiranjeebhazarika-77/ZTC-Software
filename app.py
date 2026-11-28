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
GSHEET_WEBAPP_URL = "https://script.google.com/macros/s/AKfycbz7SLKcHy7ovrUhagSMAKKNycHn_LjxSDX42PYAsegKOS-4O_CBGHT2svMPzMZ48kJp/exec"

# -------------------------------------------------------------
# OFFICIAL COURSE CATALOG & STANDARDIZED PRICING
# -------------------------------------------------------------
COURSE_CATALOG = {
    "PGDCA (12 Months)": {
        "fee": 8599.0, 
        "duration": "12 Months", 
        "desc": "Post Graduate Diploma in Computer Applications (Programming, Database, Advanced Automation)"
    },
    "ADCA (12 Months)": {
        "fee": 8599.0, 
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
       c.execute("INSERT INTO system_settings (key, value) VALUES ('admin_pin', '1234')")
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
    # Exam & Assessment Desk Records
    c.execute('''
        CREATE TABLE IF NOT EXISTS exam_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            course TEXT,
            exam_title TEXT,
            exam_date TEXT,
            theory_marks REAL DEFAULT 0,
            practical_marks REAL DEFAULT 0,
            total_marks REAL DEFAULT 0,
            max_marks REAL DEFAULT 100,
            percentage REAL DEFAULT 0,
            grade TEXT,
            recorded_by TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
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
# Automatic startup sync if local database gets reset by Streamlit Cloud reboot
try:
    chk_conn = get_db_connection()
    c_count = chk_conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    if c_count == 0:
        restore_database_from_cloud(chk_conn)
    chk_conn.close()
except Exception:
    pass
    # --- AUTO-RESTORE NOV BACKLOG ON SLEEP / RESTART ---
    try:
        res = c.execute("SELECT COUNT(*) as cnt FROM teacher_punches WHERE teacher_name = 'BIJOY KURMI' AND date BETWEEN '2026-11-01' AND '2026-11-27'").fetchone()
        if res and res[0] == 0:
            shifts_pool = ["Morning Slot: 07:00 AM - 08:30 AM", "Afternoon Slot: 03:00 PM - 05:00 PM", "Evening Slot: 05:30 PM - 07:00 PM"]
            
            # 39 verified present shifts (Nov 1 to Nov 24)
            for i in range(39):
                d_day = min(1 + (i // 3), 24)
                d_str = f"2026-11-{d_day:02d}"
                s_slot = shifts_pool[i % 3]
                c.execute("""
                    INSERT INTO teacher_punches (date, teacher_name, shift, time_in, time_out, late_mins, penalty_cut, net_batch_earning, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (d_str, "BIJOY KURMI", s_slot, "10:00 AM", "12:00 PM", 0, 0.0, 76.67, "Present"))
                
            # 6 initial leaves
            for j in range(6):
                d_day = 18 + (j // 3)
                d_str = f"2026-11-{d_day:02d}"
                s_slot = shifts_pool[j % 3]
                c.execute("""
                    INSERT INTO teacher_punches (date, teacher_name, shift, time_in, time_out, late_mins, penalty_cut, net_batch_earning, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (d_str, "BIJOY KURMI", s_slot, "LEAVE", "LEAVE", 0, 0.0, 0.0, "Leave"))
            
            # 25 Nov (3 leaves)
            for s in shifts_pool:
                c.execute("INSERT INTO teacher_punches (date, teacher_name, shift, time_in, time_out, late_mins, penalty_cut, net_batch_earning, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                          ('2026-11-25', 'BIJOY KURMI', s, 'LEAVE', 'LEAVE', 0, 0.0, 0.0, 'Leave'))

            # 26 Nov (2 leaves)
            for s in [shifts_pool[1], shifts_pool[2]]:
                c.execute("INSERT INTO teacher_punches (date, teacher_name, shift, time_in, time_out, late_mins, penalty_cut, net_batch_earning, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                          ('2026-11-26', 'BIJOY KURMI', s, 'LEAVE', 'LEAVE', 0, 0.0, 0.0, 'Leave'))

            # 27 Nov (3 leaves)
            for s in shifts_pool:
                c.execute("INSERT INTO teacher_punches (date, teacher_name, shift, time_in, time_out, late_mins, penalty_cut, net_batch_earning, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                          ('2026-11-27', 'BIJOY KURMI', s, 'LEAVE', 'LEAVE', 0, 0.0, 0.0, 'Leave'))
            conn.commit()
    except Exception as e:
        pass    
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
        ex_df = pd.DataFrame([dict(r) for r in conn.execute("SELECT student_id as 'Student ID', course as 'Course', exam_title as 'Exam Title', exam_date as 'Exam Date', theory_marks as 'Theory', practical_marks as 'Practical', total_marks as 'Total', max_marks as 'Max Marks', percentage as 'Percentage', grade as 'Grade', recorded_by as 'Recorded By' FROM exam_records").fetchall()])
        if not ex_df.empty: push_sheet_async("exam_records_db", ex_df)
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
    df_ex = fetch_sheet_data("exam_records_db")
    if df_ex is not None and not df_ex.empty:
        for _, r in df_ex.iterrows():
            sid = str(r.get("Student ID", "")).strip()
            ex_t = str(r.get("Exam Title", "")).strip()
            ex_d = str(r.get("Exam Date", "")).strip()
            if sid and ex_t:
                chk = conn.execute("SELECT id FROM exam_records WHERE student_id = ? AND exam_title = ? AND exam_date = ?", (sid, ex_t, ex_d)).fetchone()
                if not chk:
                    conn.execute('''
                        INSERT INTO exam_records (student_id, course, exam_title, exam_date, theory_marks, practical_marks, total_marks, max_marks, percentage, grade, recorded_by)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (sid, str(r.get("Course", "")), ex_t, ex_d, float(r.get("Theory", 0) or 0), float(r.get("Practical", 0) or 0), float(r.get("Total", 0) or 0), float(r.get("Max Marks", 100) or 100), float(r.get("Percentage", 0) or 0), str(r.get("Grade", "")), str(r.get("Recorded By", ""))))
        restored_items.append("Exam Records")
    df_att = fetch_sheet_data("attendance_db")
    if df_att is not None and not df_att.empty:
        for _, r in df_att.iterrows():
            sid = str(r.get("Student ID", "")).strip()
            dt = str(r.get("Date", "")).strip()
            if sid and dt:
                chk = conn.execute("SELECT 1 FROM attendance WHERE student_id = ? AND date = ?", (sid, dt)).fetchone()
                if not chk:
                    conn.execute('''
                        INSERT INTO attendance (student_id, date, time_in, status, marked_by)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (sid, dt, str(r.get("Time In", "")), str(r.get("Status", "Present")), str(r.get("Marked By", "Office"))))
        restored_items.append("Attendance")    
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
# ==========================================
# SIDEBAR NAVIGATION
# ==========================================
menu = st.sidebar.radio(
    "Select Operational Desk:",
    [
        "🌐 Public Dashboard & Enquiry",
        "🔑 Student Self-Service Portal",
        "⚡ Bulk Session & Attendance Desk",
        "📸 Attendance Kiosk",
        "📝 Exam & Assessment Desk",
        "💳 Tuition Fee Fast Counter",
        "📝 New Candidate Admission",
        "📚 Daily Class Activity (Lab/Theory)",
        "👨‍🏫 Faculty Desk & Honorarium",
        "🔐 Director Master Command Center"
    ]
)
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
            
        # Resolve Student Photo safely (Base64 / URL / Default Avatar)
        photo_src = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
        for p_col in ["photo_base64", "photo", "student_photo", "image"]:
            if p_col in s.keys() and s[p_col]:
                raw_p = str(s[p_col]).strip()
                if raw_p.startswith("data:image") or raw_p.startswith("http"):
                    photo_src = raw_p
                else:
                    photo_src = f"data:image/jpeg;base64,{raw_p}"
                break

        col_hdr1, col_hdr2 = st.columns([1.2, 4.5])
        with col_hdr1:
            st.markdown(f"""
            <div style="display: flex; justify-content: center; align-items: center; padding-top: 5px;">
                <img src="{photo_src}" style="width: 105px; height: 105px; border-radius: 50%; object-fit: cover; border: 3px solid #0284c7; box-shadow: 0 4px 12px rgba(2,132,199,0.3);" />
            </div>
            """, unsafe_allow_html=True)
        with col_hdr2:
            st.markdown(f"""
            <div style="padding-top: 5px;">
                <b style="font-size: 22px; color: #0f172a; text-transform: uppercase;">{s['name']}</b><br>
                Roll ID: <b style="color: #0284c7; font-size: 15px;">{s['student_id']}</b> &nbsp;|&nbsp; 
                Course: <b>{s['course']}</b> &nbsp;|&nbsp; 
                Shift: <b>{s['shift']}</b><br>
                <span style="font-size: 12.5px; color: #64748b;">
                    Sarva HO Reg No: <b>{s['ho_reg_no'] or 'Pending Verification'}</b> &nbsp;|&nbsp; Center Code: <b>4159</b>
                </span>
            </div>
            """, unsafe_allow_html=True)

        # Official Digital ID Card (SONA Neon Cyan Theme)
        with st.expander("🪪 View & Print Digital Student ID Card (PVC Card)", expanded=False):
            validity_val = f"{s['join_date']} to End" if ('join_date' in s.keys() and s['join_date']) else "2026 - 2027"
            mob_val = s['mobile'] if ('mobile' in s.keys() and s['mobile']) else "Institute Desk"
            
            id_card_html = f"""<div style="background: #040914; border: 2.5px solid #00e5ff; border-radius: 16px; padding: 24px 28px; max-width: 620px; margin: 15px auto; color: white; font-family: 'Segoe UI', Roboto, Helvetica, sans-serif; box-shadow: 0 0 25px rgba(0, 229, 255, 0.35);">
<div style="text-align: center; border-bottom: 1.5px solid #004d66; padding-bottom: 12px; margin-bottom: 18px;">
<h2 style="margin: 0; color: #00e5ff; font-size: 22px; font-weight: 800; letter-spacing: 2.5px; text-transform: uppercase; text-shadow: 0 0 10px rgba(0, 229, 255, 0.7);">SOFT TECH COMPUTERS</h2>
<p style="margin: 4px 0 2px 0; font-size: 11px; color: #cfd8dc; letter-spacing: 1px;">KAMARCHUBURI, THELAMARA, SONITPUR | CENTER CODE: 4159</p>
<p style="margin: 0; font-size: 10.5px; color: #00e676; font-weight: bold; letter-spacing: 1.2px;">ISO 9001:2015 CERTIFIED INSTITUTION</p>
</div>
<div style="display: flex; align-items: center; gap: 24px;">
<div style="text-align: center; width: 140px; flex-shrink: 0;">
<div style="width: 120px; height: 120px; border-radius: 50%; border: 3px solid #00e5ff; box-shadow: 0 0 18px rgba(0, 229, 255, 0.65); overflow: hidden; margin: 0 auto; background: #001020;">
<img src="{photo_src}" style="width: 100%; height: 100%; object-fit: cover;" />
</div>
<div style="border: 1.5px solid #00e5ff; border-radius: 20px; padding: 4px 12px; color: #00e5ff; font-weight: bold; font-size: 11.5px; display: inline-block; margin-top: 12px; background: rgba(0, 229, 255, 0.08); letter-spacing: 0.5px;">
ID: {s['student_id']}
</div>
</div>
<div style="flex: 1; line-height: 1.75;">
<h3 style="margin: 0 0 8px 0; color: #ffffff; font-size: 22px; font-weight: 800; text-transform: uppercase; letter-spacing: 1px;">{s['name']}</h3>
<div style="font-size: 13.5px;"><span style="color: #00e5ff; font-weight: 600;">Course:</span> <b>{s['course']}</b></div>
<div style="font-size: 13.5px;"><span style="color: #00e5ff; font-weight: 600;">Batch Time:</span> <b>{s['shift']}</b></div>
<div style="font-size: 13.5px;"><span style="color: #00e5ff; font-weight: 600;">Validity:</span> <b>{validity_val}</b></div>
<div style="font-size: 13.5px;"><span style="color: #00e5ff; font-weight: 600;">Contact:</span> <b>+91 {mob_val}</b></div>
</div>
</div>
<div style="border-top: 1px dashed #004d66; margin: 18px 0 14px 0;"></div>
<div style="display: flex; justify-content: space-between; align-items: center;">
<div style="text-align: left;">
<div style="background: white; padding: 4px 6px; border-radius: 4px; display: inline-block;">
<svg width="125" height="34" viewBox="0 0 125 34">
<rect width="125" height="34" fill="white"/>
<rect x="5" y="3" width="3" height="20" fill="black"/><rect x="10" y="3" width="1" height="20" fill="black"/><rect x="13" y="3" width="4" height="20" fill="black"/><rect x="20" y="3" width="2" height="20" fill="black"/><rect x="25" y="3" width="1" height="20" fill="black"/><rect x="28" y="3" width="5" height="20" fill="black"/><rect x="36" y="3" width="2" height="20" fill="black"/><rect x="41" y="3" width="3" height="20" fill="black"/><rect x="47" y="3" width="1" height="20" fill="black"/><rect x="51" y="3" width="4" height="20" fill="black"/><rect x="58" y="3" width="2" height="20" fill="black"/><rect x="63" y="3" width="5" height="20" fill="black"/><rect x="71" y="3" width="2" height="20" fill="black"/><rect x="76" y="3" width="3" height="20" fill="black"/><rect x="82" y="3" width="1" height="20" fill="black"/><rect x="86" y="3" width="4" height="20" fill="black"/><rect x="93" y="3" width="2" height="20" fill="black"/><rect x="98" y="3" width="3" height="20" fill="black"/><rect x="104" y="3" width="2" height="20" fill="black"/><rect x="109" y="3" width="4" height="20" fill="black"/><rect x="116" y="3" width="2" height="20" fill="black"/>
<text x="62" y="30" text-anchor="middle" font-size="8.5" font-family="monospace" font-weight="bold" fill="black">{s['student_id']}</text>
</svg>
</div>
<div style="font-size: 10px; color: #80deea; letter-spacing: 1px; margin-top: 3px;">DIGITAL TRACKING ID</div>
</div>
<div style="text-align: center;">
<div style="font-family: 'Brush Script MT', 'Dancing Script', cursive; font-size: 26px; color: #00e5ff; text-shadow: 0 0 10px rgba(0, 229, 255, 0.7); line-height: 1;">Chiranjeeb Hazarika</div>
<div style="border-top: 1px solid #004d66; margin-top: 4px; padding-top: 3px; font-size: 9.5px; color: #00e5ff; font-weight: bold; letter-spacing: 1.5px;">DIRECTOR & FOUNDER</div>
</div>
<div>
<img src="https://api.qrserver.com/v1/create-qr-code/?size=90x90&data=https://stcztc.streamlit.app?sid={s['student_id']}" style="width: 65px; height: 65px; border: 2px solid #00e5ff; border-radius: 6px; padding: 2px; background: white;" />
</div>
</div>
</div>"""
            clean_id_card = "\n".join(l.strip() for l in id_card_html.splitlines())
            st.markdown(clean_id_card, unsafe_allow_html=True)
            st.caption("🖨️ **Print Instructions:** Press **Ctrl + P** to print this official digital PVC ID card.")

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
            st.write("**Unit Tests & Examination Performance Desk:**")
            stud_marks = conn.execute("""
                SELECT id, exam_date, exam_title, course, theory_marks, practical_marks, total_marks, max_marks, percentage, grade, recorded_by
                FROM exam_records
                WHERE student_id = ?
                ORDER BY id DESC
            """, (sid,)).fetchall()

            if stud_marks:
                # Top performance summary metrics
                tot_exams = len(stud_marks)
                valid_scores = [m['percentage'] for m in stud_marks if m['grade'] != "Absent"]
                avg_score = round(sum(valid_scores) / len(valid_scores), 1) if valid_scores else 0.0

                m_col1, m_col2 = st.columns(2)
                with m_col1:
                    st.metric("Total Assessments Evaluated", f"{tot_exams} Exams")
                with m_col2:
                    st.metric("Overall Average Performance", f"{avg_score}%")

                st.markdown("---")

                st_info = conn.execute("SELECT name, course, shift FROM students WHERE student_id = ?", (sid,)).fetchone()
                student_name_disp = st_info['name'] if st_info else sid

                for m in stud_marks:
                    is_ab = (m['grade'] == "Absent")
                    if is_ab:
                        badge_bg = "#ffebee"
                        badge_color = "#c62828"
                        badge_label = "ABSENT"
                        th_disp = "AB"
                        pr_disp = "AB"
                        tot_disp = "0"
                        pct_disp = "0%"
                    else:
                        pct = m['percentage']
                        if pct >= 80:
                            badge_bg = "#e8f5e9"
                            badge_color = "#1b5e20"
                        elif pct >= 60:
                            badge_bg = "#e3f2fd"
                            badge_color = "#0d47a1"
                        elif pct >= 45:
                            badge_bg = "#fff8e1"
                            badge_color = "#b78103"
                        else:
                            badge_bg = "#fbe9e7"
                            badge_color = "#d84315"
                        
                        badge_label = m['grade']
                        th_disp = str(int(m['theory_marks']))
                        pr_disp = str(int(m['practical_marks']))
                        tot_disp = str(int(m['total_marks']))
                        pct_disp = f"{m['percentage']}%"

                    # Standard Colored Portal Card
                    card_summary_html = f"""<div style="background: #ffffff; border: 1px solid #cfd8dc; border-left: 6px solid #1a237e; border-radius: 8px; padding: 18px 22px; margin-bottom: 14px; box-shadow: 0 2px 6px rgba(0,0,0,0.04);">
<div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #eceff1; padding-bottom: 10px; margin-bottom: 12px;">
<div>
<h4 style="margin: 0; color: #1a237e; font-size: 18px; font-weight: 700;">{m['exam_title']}</h4>
<span style="font-size: 13px; color: #546e7a;">Course: <b>{m['course']}</b> | Date: <b>{m['exam_date']}</b></span>
</div>
<div>
<span style="background: {badge_bg}; color: {badge_color}; padding: 6px 14px; border-radius: 20px; font-weight: bold; font-size: 13px; border: 1px solid {badge_color};">
{badge_label}
</span>
</div>
</div>
<div style="display: flex; gap: 14px; margin-bottom: 12px;">
<div style="flex: 1; background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 6px; padding: 10px; text-align: center;">
<div style="font-size: 12px; color: #6c757d; font-weight: 600;">Theory Marks</div>
<div style="font-size: 18px; font-weight: bold; color: #212529; margin-top: 2px;">{th_disp}</div>
</div>
<div style="flex: 1; background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 6px; padding: 10px; text-align: center;">
<div style="font-size: 12px; color: #6c757d; font-weight: 600;">Practical Marks</div>
<div style="font-size: 18px; font-weight: bold; color: #212529; margin-top: 2px;">{pr_disp}</div>
</div>
<div style="flex: 1; background: #e8eaf6; border: 1px solid #c5cae9; border-radius: 6px; padding: 10px; text-align: center;">
<div style="font-size: 12px; color: #1a237e; font-weight: 600;">Total / Max</div>
<div style="font-size: 18px; font-weight: bold; color: #1a237e; margin-top: 2px;">{tot_disp} / {int(m['max_marks'])}</div>
</div>
<div style="flex: 1; background: #e0f2f1; border: 1px solid #b2dfdb; border-radius: 6px; padding: 10px; text-align: center;">
<div style="font-size: 12px; color: #004d40; font-weight: 600;">Percentage</div>
<div style="font-size: 18px; font-weight: bold; color: #004d40; margin-top: 2px;">{pct_disp}</div>
</div>
</div>
<div style="font-size: 12.5px; color: #78909c; text-align: right;">
Evaluated by: <b>{m['recorded_by']}</b>
</div>
</div>"""
                    st.markdown(card_summary_html, unsafe_allow_html=True)

                    # Student Printable Colored Marksheet View
                    with st.expander(f"📜 View & Print Colored Marksheet ({m['exam_title']})"):
                        colored_marksheet_html = f"""<div style="background: #ffffff; border: 3px double #1a237e; border-radius: 8px; padding: 30px; font-family: 'Times New Roman', serif; max-width: 680px; margin: 10px auto; color: #111; box-shadow: 0 4px 15px rgba(0,0,0,0.08);">
<div style="text-align: center; border-bottom: 2px solid #1a237e; padding-bottom: 12px; margin-bottom: 16px;">
<h2 style="margin: 0; color: #1a237e; font-size: 22px; letter-spacing: 1.5px; text-transform: uppercase;">SOFT-TECH COMPUTERS & ZTC ENTERPRISE</h2>
<p style="margin: 4px 0; font-size: 13.5px; color: #37474f;">Kamarchuburi, Thelamara, Sonitpur, Assam - 784149 | Contact: 9101026718</p>
<span style="background: #e8eaf6; color: #1a237e; border: 1px solid #9fa8da; padding: 2px 10px; border-radius: 4px; font-size: 12px; font-weight: bold;">
Accredited Center Code: 4159 (Sarva Education / SITED Recognized)
</span>
</div>
<div style="text-align: center; margin-bottom: 18px;">
<h3 style="margin: 0; color: #b78103; font-size: 17px; letter-spacing: 1px; text-decoration: underline;">OFFICIAL STATEMENT OF ASSESSMENT PERFORMANCE</h3>
</div>
<table style="width: 100%; border-collapse: collapse; font-size: 13.5px; margin-bottom: 18px; background: #fdfdfd; border: 1px solid #cfd8dc;">
<tr>
<td style="padding: 8px 12px; border: 1px solid #cfd8dc; width: 50%;"><b>Candidate Name:</b> {student_name_disp}</td>
<td style="padding: 8px 12px; border: 1px solid #cfd8dc; width: 50%;"><b>Enrollment Roll ID:</b> <span style="color:#1a237e; font-weight:bold;">{sid}</span></td>
</tr>
<tr>
<td style="padding: 8px 12px; border: 1px solid #cfd8dc;"><b>Course Enrolled:</b> {m['course']}</td>
<td style="padding: 8px 12px; border: 1px solid #cfd8dc;"><b>Assessment Module:</b> {m['exam_title']}</td>
</tr>
<tr>
<td style="padding: 8px 12px; border: 1px solid #cfd8dc;"><b>Date of Examination:</b> {m['exam_date']}</td>
<td style="padding: 8px 12px; border: 1px solid #cfd8dc;"><b>Training Institute:</b> Soft-Tech Computers (4159)</td>
</tr>
</table>
<table style="width: 100%; border-collapse: collapse; font-size: 13.5px; text-align: center; margin-bottom: 25px; border: 1.5px solid #1a237e;">
<thead>
<tr style="background-color: #1a237e; color: white;">
<th style="padding: 10px; border: 1px solid #1a237e;">Theory Marks</th>
<th style="padding: 10px; border: 1px solid #1a237e;">Practical Marks</th>
<th style="padding: 10px; border: 1px solid #1a237e;">Total Obtained</th>
<th style="padding: 10px; border: 1px solid #1a237e;">Maximum Marks</th>
<th style="padding: 10px; border: 1px solid #1a237e;">Percentage (%)</th>
<th style="padding: 10px; border: 1px solid #1a237e;">Awarded Grade</th>
</tr>
</thead>
<tbody>
<tr style="font-weight: bold; font-size: 14px; background: #fafafa;">
<td style="padding: 12px; border: 1px solid #cfd8dc;">{th_disp}</td>
<td style="padding: 12px; border: 1px solid #cfd8dc;">{pr_disp}</td>
<td style="padding: 12px; border: 1px solid #cfd8dc; color: #1a237e;">{tot_disp}</td>
<td style="padding: 12px; border: 1px solid #cfd8dc;">{int(m['max_marks'])}</td>
<td style="padding: 12px; border: 1px solid #cfd8dc; color: #004d40;">{pct_disp}</td>
<td style="padding: 12px; border: 1px solid #cfd8dc; color: {badge_color};">{badge_label}</td>
</tr>
</tbody>
</table>
<div style="margin-top: 45px; display: flex; justify-content: space-between; font-size: 13px; padding: 0 20px;">
<div style="text-align: center;">
<p style="margin: 0; border-top: 1px solid #37474f; padding-top: 5px; width: 170px;">
<b>Faculty In-Charge</b><br><span style="font-size:12px; color:#546e7a;">{m['recorded_by']}</span>
</p>
</div>
<div style="text-align: center;">
<p style="margin: 0; border-top: 1px solid #1a237e; padding-top: 5px; width: 170px; color:#1a237e;">
<b>Authorized Director</b><br><span style="font-size:12px; color:#546e7a;">Soft-Tech Computers</span>
</p>
</div>
</div>
</div>"""
                        clean_sheet = "\n".join(l.strip() for l in colored_marksheet_html.splitlines())
                        st.markdown(clean_sheet, unsafe_allow_html=True)
                        st.caption("🖨️ **Print Instructions:** Press **Ctrl + P** to print colored copy or 'Save as PDF'.")
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
        teachers_list = [r["name"] for r in conn.execute("SELECT name FROM teachers").fetchall()]
        
        # 1. Date selection
        bk_date = st.date_input("Session Date*", value=datetime.date.today())
        weekday_name = bk_date.strftime("%A")
        default_batch_idx = 1 if weekday_name in ["Monday", "Wednesday", "Friday"] else (2 if weekday_name in ["Tuesday", "Thursday", "Saturday"] else 0)

        # 2. Filters Row
        c_bk1, c_bk2, c_bk3 = st.columns(3)
        with c_bk1:
            bk_teacher = st.selectbox("Staff / Incharge*", teachers_list)
        with c_bk2:
            shift_options = [
                "All Shifts",
                "Morning Slot: 07:00 AM - 08:30 AM",
                "Afternoon Slot: 04:00 PM - 05:30 PM",
                "Evening Slot: 05:30 PM - 07:00 PM"
            ]
            bk_filter_shift = st.selectbox("Filter Shift*", shift_options)
        with c_bk3:
            bk_filter_batch = st.selectbox(f"Batch Routine ({weekday_name})*", ["All Batches", "MWF (Mon-Wed-Fri)", "TTS (Tue-Thu-Sat)"], index=default_batch_idx)

        # 3. Direct Strong SQL Query (Shob student filter)
        query = "SELECT student_id, name, shift, course FROM students WHERE status='Active'"
        params = []

        if bk_filter_shift != "All Shifts":
            shift_prefix = bk_filter_shift.split(":")[0]  # 'Morning Slot' বা 'Evening Slot' বাচি ল'ব
            query += " AND shift LIKE ?"
            params.append(f"%{shift_prefix}%")

        if bk_filter_batch == "MWF (Mon-Wed-Fri)":
            query += " AND (shift NOT LIKE '%TTS%')"
        elif bk_filter_batch == "TTS (Tue-Thu-Sat)":
            query += " AND shift LIKE '%TTS%'"

        query += " ORDER BY student_id ASC"
        filtered_list = conn.execute(query, params).fetchall()

        st.write(f"Total Trainees in Queue: **{len(filtered_list)} Candidates**")
        form_key = f"bulk_reg_{bk_date}_{str(bk_filter_shift)[:5]}_{default_batch_idx}"
        with st.form(key=form_key):
            bulk_status = {}
            bulk_fee_amt = {}

            for s_item in filtered_list:
                c_b1, c_b2, c_b3 = st.columns([2.5, 1.8, 1.5])
                with c_b1:
                    st.markdown(f"**{s_item['name']}** ({s_item['student_id']})<br><span style='font-size:11px; color:#607d8b;'>Shift: {s_item['shift']}</span>", unsafe_allow_html=True)

                existing_att = conn.execute(
                    "SELECT status FROM attendance WHERE student_id = ? AND date = ?", 
                    (s_item['student_id'], str(bk_date))
                ).fetchone()

                status_opts = ["Present", "Absent", "Late", "Leave"]
                def_idx = 0
                if existing_att and existing_att["status"] in status_opts:
                    def_idx = status_opts.index(existing_att["status"])

                with c_b2:
                    bulk_status[s_item['student_id']] = st.radio(
                        f"Status_{s_item['student_id']}",
                        status_opts,
                        index=def_idx,
                        horizontal=True,
                        key=f"bk_stat_{bk_date}_{s_item['student_id']}"
                    )

                with c_b3:
                    bulk_fee_amt[s_item['student_id']] = st.number_input(
                        f"Deposit (₹) ({s_item['student_id']})",
                        min_value=0.0,
                        step=50.0,
                        value=0.0,
                        key=f"bk_fee_{bk_date}_{s_item['student_id']}"
                    )

            if st.form_submit_button("💾 Save Bulk Attendance & Process Receipts", type="primary"):
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
                st.success(f"✅ Bulk register saved! {len(filtered_list)} attendance records verified and {fees_logged} fee deposits logged.")
                st.toast("✅ Attendance & Fee Receipts Saved Successfully!", icon="🎉")
                import time
                time.sleep(1.5)
                st.session_state["bulk_reset_cnt"] = st.session_state.get("bulk_reset_cnt", 0) + 1
                st.rerun()
# ----------------------------------------------------
# ATTENDANCE KIOSK (SELF-SERVICE)
# ----------------------------------------------------
elif menu == "📸 Attendance Kiosk":
    st.markdown("## 📸 Self-Service Attendance Kiosk")
    now_ist = datetime.datetime.now(IST)
    today_str = now_ist.strftime("%Y-%m-%d")
    time_str = now_ist.strftime("%H:%M")
    day_name = now_ist.strftime("%A")

    if "kiosk_unlocked" not in st.session_state:
        st.session_state["kiosk_unlocked"] = False
    if "kiosk_active_sid" not in st.session_state:
        st.session_state["kiosk_active_sid"] = None

    # 1. PIN Lock Security
    if not st.session_state["kiosk_unlocked"]:
        st.info("🔒 Please enter the Staff or Admin PIN to unlock the Kiosk.")
        k_pin = st.text_input("Enter Staff / Admin PIN:", type="password", key="kiosk_pin_in")
        if st.button("🔓 Unlock Kiosk", type="primary"):
            if str(k_pin).strip() in [str(staff_pin_val), str(admin_pin_val)]:
                st.session_state["kiosk_unlocked"] = True
                st.rerun()
            else:
                st.error("❌ Invalid PIN! Please try again.")
    else:
        top_c1, top_c2 = st.columns([4, 1])
        with top_c1:
            st.caption(f"📅 Date: **{today_str} ({day_name})** | ⏰ IST Time: **{time_str}**")
        with top_c2:
            if st.button("🔒 Lock Kiosk", use_container_width=True):
                st.session_state["kiosk_unlocked"] = False
                st.session_state["kiosk_active_sid"] = None
                st.rerun()

        # 2. Auto Routine & Shift Filter
        default_r = "MWF" if day_name in ["Monday", "Wednesday", "Friday"] else ("TTS" if day_name in ["Tuesday", "Thursday", "Saturday"] else "All")
        r_opts = ["All", "MWF", "TTS"]
        all_rows = [dict(r) for r in conn.execute("SELECT * FROM students ORDER BY student_id").fetchall()]
        active_st = [s for s in all_rows if str(s.get("status", "Active")).lower() != "inactive"]
        shift_opts = ["All Shifts"] + sorted(list(set([str(s.get("shift", "")) for s in active_st if s.get("shift")])))

        f_c1, f_c2 = st.columns(2)
        with f_c1:
            sel_routine = st.selectbox("Routine Filter (Auto IST):", r_opts, index=r_opts.index(default_r))
        with f_c2:
            sel_shift = st.selectbox("Shift Filter:", shift_opts)

        # 3. Active Single Camera Verification Popup
        active_sid = st.session_state.get("kiosk_active_sid")
        if active_sid:
            st_obj = next((s for s in active_st if s["student_id"] == active_sid), None)
            if st_obj:
                st.markdown("---")
                st.warning(f"📸 **{st_obj['name']} ({active_sid})** — Click a live photo to verify your attendance:")
                cam_snap = st.camera_input("Click Live Photo", key=f"kiosk_cam_{active_sid}")
                if st.button("❌ Cancel", key="kiosk_cancel"):
                    st.session_state["kiosk_active_sid"] = None
                    st.rerun()
                if cam_snap is not None:
                    chk_a = conn.execute("SELECT 1 FROM attendance WHERE student_id = ? AND date = ?", (active_sid, today_str)).fetchone()
                    if not chk_a:
                        conn.execute(
                            "INSERT INTO attendance (student_id, date, time_in, status, marked_by) VALUES (?, ?, ?, ?, ?)",
                            (active_sid, today_str, time_str, "Present", "Attendance Kiosk")
                        )
                        conn.commit()
                        sync_all_to_cloud(conn)
                    st.session_state["kiosk_active_sid"] = None
                    st.success(f"✅ Attendance marked for {st_obj['name']} at {time_str} IST!")
                    st.rerun()
                st.markdown("---")

        # 4. Filtered Student Photo Grid
        filtered_st = active_st
        if sel_routine != "All":
            filtered_st = [s for s in filtered_st if sel_routine in str(s.get("shift", "")).upper()]
        if sel_shift != "All Shifts":
            filtered_st = [s for s in filtered_st if str(s.get("shift", "")) == sel_shift]

        att_today = {
            r["student_id"]: (r["status"], r["time_in"])
            for r in conn.execute("SELECT student_id, status, time_in FROM attendance WHERE date = ?", (today_str,)).fetchall()
        }

        if not filtered_st:
            st.info("No active students found for this routine or shift.")
        else:
            p_col = next((c for c in filtered_st[0].keys() if "photo" in c.lower()), "photo_base64")
            cols = st.columns(4)
            for idx, s in enumerate(filtered_st):
                sid = s["student_id"]
                with cols[idx % 4]:
                    with st.container(border=True):
                        ph = s.get(p_col)
                        if ph and len(str(ph)) > 50:
                            st.markdown(f'<div style="text-align:center;"><img src="data:image/jpeg;base64,{ph}" style="width:90px; height:90px; object-fit:cover; border-radius:50%; border:2px solid #2563eb;"></div>', unsafe_allow_html=True)
                        else:
                            initials = "".join([w[0] for w in str(s.get("name", "S")).split()[:2]]).upper()
                            st.markdown(f'<div style="width:90px; height:90px; border-radius:50%; background:#e2e8f0; color:#1e293b; display:flex; align-items:center; justify-content:center; font-size:28px; font-weight:bold; margin:auto;">{initials}</div>', unsafe_allow_html=True)
                        st.markdown(f"<div style='text-align:center; margin-top:6px;'><b>{s['name']}</b><br><span style='font-size:12px; color:#64748b;'>{sid}</span></div>", unsafe_allow_html=True)
                        if sid in att_today:
                            st_val, tm_val = att_today[sid]
                            if str(st_val).lower() == "present":
                                st.success(f"✅ {st_val} ({tm_val})")
                            elif str(st_val).lower() == "absent":
                                st.error(f"❌ {st_val}")
                            elif str(st_val).lower() == "leave":
                                st.warning(f"🟡 {st_val}")
                            else:
                                st.info(f"ℹ️ {st_val} ({tm_val})")
                        else:
                            if st.button("📸 Present", key=f"kbtn_{sid}", use_container_width=True):
                                st.session_state["kiosk_active_sid"] = sid
                                st.rerun()
# ----------------------------------------------------
# EXAM & ASSESSMENT DESK
# ----------------------------------------------------
elif menu == "📝 Exam & Assessment Desk":
    st.markdown("### 📝 Exam & Assessment Management Desk")
    st.caption("Record Theory & Practical marks, evaluate batch performances, and publish results to the Student Portal.")

    if verify_staff_access("Exam Desk"):
        ex_tab1, ex_tab2 = st.tabs(["✍️ Bulk Marks Entry", "📊 Assessment Archives & Print Station"])

        with ex_tab1:
            st.markdown("#### Record Batch Exam Marks")

            # Notification alert on successful submission
            if "exam_success_banner" in st.session_state:
                st.success(st.session_state.pop("exam_success_banner"))

            # Form Reset Key Management
            if "exam_form_version" not in st.session_state:
                st.session_state["exam_form_version"] = 100

            c_e1, c_e2, c_e3, c_e4 = st.columns(4)
            with c_e1:
                ex_date = st.date_input("Exam Date", datetime.date.today(), key=f"ex_date_in_{st.session_state['exam_form_version']}")
            with c_e2:
                courses_raw = [r[0] for r in conn.execute("SELECT DISTINCT course FROM students WHERE course IS NOT NULL").fetchall()]
                ex_course = st.selectbox("Course Filter", ["All Courses"] + sorted(courses_raw), key=f"ex_course_sel_{st.session_state['exam_form_version']}")
            with c_e3:
                shifts_raw = [r[0] for r in conn.execute("SELECT DISTINCT shift FROM students WHERE shift IS NOT NULL").fetchall()]
                ex_shift = st.selectbox("Batch / Shift Filter", ["All Shifts / Batches"] + sorted(shifts_raw), key=f"ex_shift_sel_{st.session_state['exam_form_version']}")
            with c_e4:
                ex_teacher = st.selectbox("Evaluator / Teacher", ["CHIRANJEEB HAZARIKA", "BIJOY KURMI", "Staff"], key=f"ex_eval_{st.session_state['exam_form_version']}")

            c_e5, c_e6, c_e7 = st.columns(3)
            with c_e5:
                ex_title = st.text_input("Exam Title / Module", placeholder="e.g. Monthly Test 1 / MS Word Practical", key=f"ex_title_in_{st.session_state['exam_form_version']}")
            with c_e6:
                max_theory = st.number_input("Full Marks (Theory)", min_value=0, max_value=200, value=50, step=5, key=f"m_th_{st.session_state['exam_form_version']}")
            with c_e7:
                max_practical = st.number_input("Full Marks (Practical)", min_value=0, max_value=200, value=50, step=5, key=f"m_pr_{st.session_state['exam_form_version']}")

            total_max = max_theory + max_practical

            # Fetch candidates matching both course and shift filters
            query = "SELECT student_id, name, course, shift FROM students WHERE 1=1"
            params = []
            if ex_course != "All Courses":
                query += " AND course = ?"
                params.append(ex_course)
            if ex_shift != "All Shifts / Batches":
                query += " AND shift = ?"
                params.append(ex_shift)
            query += " ORDER BY student_id ASC"
            c_students = conn.execute(query, params).fetchall()

            st.write(f"**Eligible Candidates in Batch:** `{len(c_students)} Students` | **Total Assessment Marks:** `{total_max}`")

            if len(c_students) > 0 and ex_title.strip():
                with st.form(key=f"bulk_exam_form_v_{st.session_state['exam_form_version']}"):
                    theory_inputs = {}
                    practical_inputs = {}
                    absent_flags = {}
                    skip_flags = {}

                    st.markdown("---")
                    h1, h2, h3, h4 = st.columns([2.5, 1.2, 1.2, 0.9])
                    with h1:
                        st.markdown("**Student Details**")
                    with h2:
                        st.markdown(f"**Theory (Max {max_theory})**")
                    with h3:
                        st.markdown(f"**Practical (Max {max_practical})**")
                    with h4:
                        st.markdown("**Status**")

                    for st_item in c_students:
                        sid = st_item['student_id']
                        col_s1, col_s2, col_s3, col_s4 = st.columns([2.5, 1.2, 1.2, 0.9])
                        with col_s1:
                            st.markdown(f"**{st_item['name']}** (`{sid}`)<br><span style='font-size:11px; color:#607d8b;'>{st_item['course']} | {st_item['shift']}</span>", unsafe_allow_html=True)
                        with col_s2:
                            theory_inputs[sid] = st.number_input(f"T_{sid}", min_value=0, max_value=int(max_theory), value=0, step=1, label_visibility="collapsed", key=f"t_{sid}_{st.session_state['exam_form_version']}", format="%d")
                        with col_s3:
                            practical_inputs[sid] = st.number_input(f"P_{sid}", min_value=0, max_value=int(max_practical), value=0, step=1, label_visibility="collapsed", key=f"p_{sid}_{st.session_state['exam_form_version']}", format="%d")
                        with col_s4:
                            absent_flags[sid] = st.checkbox("Absent", key=f"ab_{sid}_{st.session_state['exam_form_version']}")
                            skip_flags[sid] = st.checkbox("Skip (N/A)", key=f"sk_{sid}_{st.session_state['exam_form_version']}")

                    if st.form_submit_button("💾 Save & Publish Assessment Scores"):
                        date_str = str(ex_date)
                        saved_cnt = 0
                        for st_item in c_students:
                            sid = st_item['student_id']
                            if skip_flags[sid]:
                                continue
                            is_ab = absent_flags[sid]

                            if is_ab:
                                t_score = 0
                                p_score = 0
                                tot_score = 0
                                pct = 0.0
                                grade_str = "Absent"
                            else:
                                t_score = int(theory_inputs[sid])
                                p_score = int(practical_inputs[sid])
                                tot_score = t_score + p_score
                                pct = round((tot_score / total_max) * 100, 2) if total_max > 0 else 0.0

                                if pct >= 80:
                                    grade_str = "A+ (Excellent)"
                                elif pct >= 60:
                                    grade_str = "A (Very Good)"
                                elif pct >= 45:
                                    grade_str = "B (Good)"
                                elif pct >= 34:
                                    grade_str = "C (Pass)"
                                else:
                                    grade_str = "F (Needs Improvement)"

                            conn.execute("""
                                INSERT INTO exam_records (student_id, course, exam_title, exam_date, theory_marks, practical_marks, total_marks, max_marks, percentage, grade, recorded_by)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (sid, st_item['course'], ex_title.strip(), date_str, t_score, p_score, tot_score, total_max, pct, grade_str, ex_teacher))
                            saved_cnt += 1

                        conn.commit()
                        sync_all_to_cloud(conn)
                        # Clear inputs and show green banner
                        st.session_state["exam_form_version"] += 1
                        st.session_state["exam_success_banner"] = f"Submitted Successfully! Recorded assessment marks for {saved_cnt} students."
                        st.rerun()
            elif not ex_title.strip():
                st.info("💡 Please enter an Exam Title/Module above to load the marks entry sheet.")

        with ex_tab2:
            st.markdown("#### 📊 Assessment Archives & Print Station")

            print_mode = st.radio("Select Print / View Mode:", ["📋 Batch Result Sheet (Notice Board)", "🎓 Individual Student Marksheet", "📁 Full Records Table"], horizontal=True)

            if print_mode == "📋 Batch Result Sheet (Notice Board)":
                st.info("💡 Consolidated batch tabulation sheet in Times New Roman font for notice board display.")

                distinct_exams = conn.execute("SELECT DISTINCT exam_title FROM exam_records ORDER BY id DESC").fetchall()
                exam_options = [r[0] for r in distinct_exams] if distinct_exams else []

                if exam_options:
                    c_nb1, c_nb2 = st.columns(2)
                    with c_nb1:
                        sel_exam = st.selectbox("Select Exam Title / Module:", exam_options, key="nb_exam_sel")
                    with c_nb2:
                        sel_exam_dates = [r[0] for r in conn.execute("SELECT DISTINCT exam_date FROM exam_records WHERE exam_title = ? ORDER BY id DESC", (sel_exam,)).fetchall()]
                        sel_date = st.selectbox("Select Exam Date:", sel_exam_dates, key="nb_date_sel")

                    batch_res = conn.execute("""
                        SELECT e.student_id, s.name, e.course, e.theory_marks, e.practical_marks, e.total_marks, e.max_marks, e.percentage, e.grade, e.recorded_by
                        FROM exam_records e
                        LEFT JOIN students s ON e.student_id = s.student_id
                        WHERE e.exam_title = ? AND e.exam_date = ?
                        ORDER BY e.student_id ASC
                    """, (sel_exam, sel_date)).fetchall()

                    if batch_res:
                        evaluator_name = batch_res[0]['recorded_by'] if batch_res[0]['recorded_by'] else "Faculty In-Charge"

                        rows_html = ""
                        for idx, r in enumerate(batch_res, 1):
                            if r['grade'] == "Absent":
                                th_disp = "<span style='color:red; font-weight:bold;'>AB</span>"
                                pr_disp = "<span style='color:red; font-weight:bold;'>AB</span>"
                                tot_disp = "0 / " + str(int(r['max_marks']))
                                pct_disp = "0%"
                                grd_disp = "<span style='color:red; font-weight:bold;'>Absent</span>"
                            else:
                                th_disp = str(int(r['theory_marks']))
                                pr_disp = str(int(r['practical_marks']))
                                tot_disp = f"{int(r['total_marks'])} / {int(r['max_marks'])}"
                                pct_disp = f"{r['percentage']}%"
                                grd_disp = r['grade']

                            rows_html += f"""<tr style="border-bottom: 1px solid #444; text-align: center; height: 30px; font-family: 'Times New Roman', Times, serif;">
<td style="padding: 6px; border: 1px solid #555;">{idx}</td>
<td style="padding: 6px; font-weight: bold; border: 1px solid #555;">{r['student_id']}</td>
<td style="padding: 6px; text-align: left; border: 1px solid #555;">{r['name']}</td>
<td style="padding: 6px; border: 1px solid #555; font-size: 12px;">{r['course']}</td>
<td style="padding: 6px; border: 1px solid #555;">{th_disp}</td>
<td style="padding: 6px; border: 1px solid #555;">{pr_disp}</td>
<td style="padding: 6px; font-weight: bold; border: 1px solid #555;">{tot_disp}</td>
<td style="padding: 6px; font-weight: bold; border: 1px solid #555;">{pct_disp}</td>
<td style="padding: 6px; font-weight: bold; border: 1px solid #555;">{grd_disp}</td>
</tr>"""

                        raw_notice_board = f"""<div style="background: white; color: black; border: 2px solid black; padding: 30px; border-radius: 4px; font-family: 'Times New Roman', Times, serif; max-width: 840px; margin: 15px auto;">
<div style="text-align: center; border-bottom: 2px solid black; padding-bottom: 12px; margin-bottom: 15px;">
<h2 style="margin: 0; text-transform: uppercase; letter-spacing: 1.5px; font-family: 'Times New Roman', Times, serif; font-size: 22px;">SOFT-TECH COMPUTERS & ZTC ENTERPRISE</h2>
<p style="margin: 4px 0; font-size: 14px; font-family: 'Times New Roman', Times, serif;">Kamarchuburi, Thelamara, Sonitpur, Assam - 784149 | Ph: 9101026718</p>
<p style="margin: 2px 0; font-size: 13px; font-family: 'Times New Roman', Times, serif; font-weight: bold;">Accredited Center Code: 4159 (Sarva Education / SITED Recognized)</p>
</div>
<div style="text-align: center; margin-bottom: 15px;">
<h3 style="margin: 0; text-decoration: underline; letter-spacing: 1px; font-family: 'Times New Roman', Times, serif; font-size: 17px;">CONSOLIDATED ASSESSMENT TABULATION SHEET</h3>
<p style="margin: 6px 0 0 0; font-size: 14px; font-family: 'Times New Roman', Times, serif;"><b>Assessment Module:</b> {sel_exam} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Date:</b> {sel_date}</p>
</div>
<table style="width: 100%; border-collapse: collapse; font-size: 13px; font-family: 'Times New Roman', Times, serif; margin-top: 15px; border: 1.5px solid black;">
<thead>
<tr style="background-color: #f5f5f5; border-bottom: 2px solid black; text-align: center; font-family: 'Times New Roman', Times, serif;">
<th style="padding: 8px; border: 1px solid black; width: 35px;">Sl</th>
<th style="padding: 8px; border: 1px solid black; width: 95px;">Roll / ID</th>
<th style="padding: 8px; border: 1px solid black; text-align: left;">Student Name</th>
<th style="padding: 8px; border: 1px solid black; width: 95px;">Course</th>
<th style="padding: 8px; border: 1px solid black; width: 65px;">Theory</th>
<th style="padding: 8px; border: 1px solid black; width: 65px;">Practical</th>
<th style="padding: 8px; border: 1px solid black; width: 85px;">Total</th>
<th style="padding: 8px; border: 1px solid black; width: 75px;">% Score</th>
<th style="padding: 8px; border: 1px solid black; width: 110px;">Grade</th>
</tr>
</thead>
<tbody>
{rows_html}
</tbody>
</table>
<div style="margin-top: 60px; display: flex; justify-content: space-between; font-size: 13px; font-family: 'Times New Roman', Times, serif; padding: 0 20px;">
<div style="text-align: center;">
<p style="margin: 0; border-top: 1px solid black; padding-top: 6px; width: 200px; font-family: 'Times New Roman', Times, serif;"><b>Evaluated By</b><br>{evaluator_name}</p>
</div>
<div style="text-align: center;">
<p style="margin: 0; border-top: 1px solid black; padding-top: 6px; width: 200px; font-family: 'Times New Roman', Times, serif;"><b>Director / Center In-Charge</b><br>Soft-Tech Computers & ZTC</p>
</div>
</div>
</div>"""
                        clean_nb_html = "\n".join(l.strip() for l in raw_notice_board.splitlines())
                        st.markdown(clean_nb_html, unsafe_allow_html=True)
                        st.caption("🖨️ **Print Instructions:** Press **Ctrl + P**, choose 'Save as PDF' or select your printer for A4 sheet output.")
                else:
                    st.info("No exam records found to generate batch result.")

            elif print_mode == "🎓 Individual Student Marksheet":
                st.info("💡 Official individual performance scorecard in Times New Roman font.")

                st_candidates = conn.execute("""
                    SELECT DISTINCT e.student_id, s.name 
                    FROM exam_records e
                    LEFT JOIN students s ON e.student_id = s.student_id
                    ORDER BY e.student_id ASC
                """).fetchall()

                if st_candidates:
                    c_opts = [f"{r['student_id']} - {r['name']}" for r in st_candidates]
                    sel_stud = st.selectbox("Select Candidate:", c_opts, key="single_marksheet_stud")
                    sel_sid = sel_stud.split(" - ")[0]

                    stud_ex_records = conn.execute("""
                        SELECT id, exam_title, exam_date, course, theory_marks, practical_marks, total_marks, max_marks, percentage, grade, recorded_by
                        FROM exam_records
                        WHERE student_id = ?
                        ORDER BY id DESC
                    """, (sel_sid,)).fetchall()

                    if stud_ex_records:
                        ex_list = [f"{r['exam_title']} ({r['exam_date']}) - ID:{r['id']}" for r in stud_ex_records]
                        sel_ex_str = st.selectbox("Select Module / Exam Record:", ex_list, key="single_record_sel")
                        rec_id = int(sel_ex_str.split("ID:")[1])

                        rec = [r for r in stud_ex_records if r['id'] == rec_id][0]
                        st_detail = conn.execute("SELECT name, course, shift FROM students WHERE student_id = ?", (sel_sid,)).fetchone()
                        student_full_name = st_detail['name'] if st_detail else sel_stud.split(" - ")[1]

                        if rec['grade'] == "Absent":
                            th_val = "<span style='color:red;'>Absent</span>"
                            pr_val = "<span style='color:red;'>Absent</span>"
                            tot_val = "0"
                            pct_val = "0%"
                            grd_val = "<span style='color:red;'>Absent</span>"
                        else:
                            th_val = str(int(rec['theory_marks']))
                            pr_val = str(int(rec['practical_marks']))
                            tot_val = str(int(rec['total_marks']))
                            pct_val = f"{rec['percentage']}%"
                            grd_val = rec['grade']

                        raw_single_card = f"""<div style="background: white; color: black; border: 2.5px solid black; padding: 30px; border-radius: 4px; font-family: 'Times New Roman', Times, serif; max-width: 680px; margin: 20px auto;">
<div style="text-align: center; border-bottom: 2px solid black; padding-bottom: 12px; margin-bottom: 15px;">
<h2 style="margin: 0; letter-spacing: 1.5px; font-family: 'Times New Roman', Times, serif; font-size: 22px;">SOFT-TECH COMPUTERS & ZTC ENTERPRISE</h2>
<p style="margin: 4px 0; font-size: 14px; font-family: 'Times New Roman', Times, serif;">Kamarchuburi, Thelamara, Sonitpur, Assam - 784149</p>
<p style="margin: 2px 0; font-size: 12.5px; font-family: 'Times New Roman', Times, serif; font-weight: bold;">Accredited Center Code: 4159 (Sarva Education / SITED Recognized)</p>
</div>
<div style="text-align: center; margin-bottom: 20px;">
<h3 style="margin: 0; letter-spacing: 1px; text-decoration: underline; font-family: 'Times New Roman', Times, serif; font-size: 16px;">STUDENT PERFORMANCE SCORECARD</h3>
</div>
<div style="font-size: 14px; line-height: 1.8; margin-bottom: 20px; border: 1px solid black; padding: 12px 16px; font-family: 'Times New Roman', Times, serif; background: #fafafa;">
<table style="width: 100%; border-collapse: collapse; font-family: 'Times New Roman', Times, serif;">
<tr>
<td style="width: 50%;"><b>Candidate Name:</b> {student_full_name}</td>
<td style="width: 50%;"><b>Student Roll / ID:</b> {sel_sid}</td>
</tr>
<tr>
<td><b>Course Enrolled:</b> {rec['course']}</td>
<td><b>Exam / Module:</b> {rec['exam_title']}</td>
</tr>
<tr>
<td><b>Assessment Date:</b> {rec['exam_date']}</td>
<td><b>Academic Center:</b> Soft-Tech Computers (4159)</td>
</tr>
</table>
</div>
<table style="width: 100%; border-collapse: collapse; font-size: 13.5px; font-family: 'Times New Roman', Times, serif; margin: 20px 0; border: 1.5px solid black;">
<thead>
<tr style="background: #f5f5f5; text-align: center; border-bottom: 1.5px solid black; font-family: 'Times New Roman', Times, serif;">
<th style="padding: 9px; border: 1px solid black;">Theory Marks</th>
<th style="padding: 9px; border: 1px solid black;">Practical Marks</th>
<th style="padding: 9px; border: 1px solid black;">Total Obtained</th>
<th style="padding: 9px; border: 1px solid black;">Max Marks</th>
<th style="padding: 9px; border: 1px solid black;">Percentage</th>
<th style="padding: 9px; border: 1px solid black;">Awarded Grade</th>
</tr>
</thead>
<tbody>
<tr style="text-align: center; font-weight: bold; font-size: 14px; font-family: 'Times New Roman', Times, serif;">
<td style="padding: 12px; border: 1px solid black;">{th_val}</td>
<td style="padding: 12px; border: 1px solid black;">{pr_val}</td>
<td style="padding: 12px; border: 1px solid black;">{tot_val}</td>
<td style="padding: 12px; border: 1px solid black;">{int(rec['max_marks'])}</td>
<td style="padding: 12px; border: 1px solid black;">{pct_val}</td>
<td style="padding: 12px; border: 1px solid black;">{grd_val}</td>
</tr>
</tbody>
</table>
<div style="margin-top: 55px; display: flex; justify-content: space-between; font-size: 13px; font-family: 'Times New Roman', Times, serif; padding: 0 20px;">
<div style="text-align: center;">
<p style="margin: 0; border-top: 1px solid black; padding-top: 5px; width: 170px; font-family: 'Times New Roman', Times, serif;"><b>Faculty In-Charge</b><br>{rec['recorded_by'] if rec['recorded_by'] else 'Teacher'}</p>
</div>
<div style="text-align: center;">
<p style="margin: 0; border-top: 1px solid black; padding-top: 5px; width: 170px; font-family: 'Times New Roman', Times, serif;"><b>Center Director</b><br>Soft-Tech Computers</p>
</div>
</div>
</div>"""
                        clean_card_html = "\n".join(l.strip() for l in raw_single_card.splitlines())
                        st.markdown(clean_card_html, unsafe_allow_html=True)
                        st.caption("🖨️ **Print Instructions:** Press **Ctrl + P** to print this official student scorecard.")
                else:
                    st.info("No candidates found with assessment records.")

            elif print_mode == "📁 Full Records Table":
                st.markdown("#### All Assessment Records Database")
                rec_data = conn.execute("""
                    SELECT e.exam_date, e.student_id, s.name, e.course, e.exam_title, e.theory_marks, e.practical_marks, e.total_marks, e.max_marks, e.percentage, e.grade, e.recorded_by 
                    FROM exam_records e 
                    LEFT JOIN students s ON e.student_id = s.student_id 
                    ORDER BY e.id DESC
                """).fetchall()

                if rec_data:
                    import pandas as pd
                    df_ex = pd.DataFrame(rec_data, columns=["Date", "Student ID", "Name", "Course", "Exam Title", "Theory", "Practical", "Total", "Max", "Percentage (%)", "Grade", "Teacher"])
                    st.dataframe(df_ex, use_container_width=True)
                else:
                    st.info("No exam records saved yet.")
# -------------------------------------------------------------
# 4. TUFEE FAST COUNTER
# -------------------------------------------------------------
elif menu == "💳 Tuition Fee Fast Counter":
    st.subheader("💳 TuFee Instant Counter (Collect Fee & Send WhatsApp Receipt)")
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
                adm_shift_slot = st.selectbox("Assigned Shift Slot*", [
                "Morning Slot: 07:00 AM - 08:30 AM",
                "Afternoon Slot: 04:00 PM - 05:30 PM",
                "Evening Slot: 05:30 PM - 07:00 PM"
            ])
                adm_routine = st.selectbox("Batch Routine*", ["MWF (Mon-Wed-Fri)", "TTS (Tue-Thu-Sat)"])
                adm_shift = f"{adm_shift_slot} ({adm_routine[:3]})"
            with col_c2:
                adm_fee = st.number_input("Confirmed Net Fee (₹)*", min_value=100.0, value=default_course_fee, step=50.0)
            with col_c3:
                photo_file = st.file_uploader("Upload Passport Size Photo (JPG/PNG)*", type=["jpg", "jpeg", "png"])
            
                
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
                # --- DATE LOCK & DIRECTOR OVERRIDE ---
                col_dt1, col_dt2 = st.columns([1.5, 1])
                with col_dt1:
                    req_backdate = st.checkbox("⚠️ Need Back-dated / Missed Date Entry?", help="Only Director can unlock past dates.")
                
                entry_date = datetime.date.today()
                if not req_backdate:
                    st.info(f"🔒 **Date Locked to Today:** `{entry_date.strftime('%d-%b-%Y')}` (Faculty Mode)")
                else:
                    with col_dt2:
                        dir_pin = st.text_input("🔑 Director PIN:", type="password")
                    if dir_pin == "zaan123":
                        entry_date = st.date_input("Select Approved Past Date:", value=datetime.date.today(), max_value=datetime.date.today())
                        st.success("✅ Director Approved: Date unlocked!")
                    elif dir_pin:
                        st.error("⛔ ACCESS DENIED: Faculty cannot back-date entries.")
                        entry_date = datetime.date.today()
                    else:
                        st.warning("🔒 Director PIN required to unlock calendar.")
                        entry_date = datetime.date.today()                
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
                        module_options = [
                            # --- Office Productivity Suite ---
                            "📄 MS Word (Docs, Formats & Official Drafting)",
                            "📊 MS Excel (Formulas, Sheets & Data Analysis)",
                            "📽️ MS PowerPoint (Slide Decks & Animations)",
                            "🗄️ MS Access (Databases & Record Management)",
                            
                            # --- Creative DTP & Media Graphics ---
                            "📰 Adobe PageMaker (Assamese DTP & Layout Design)",
                            "🎨 Adobe Photoshop (Graphics, Photo Edit & ID Card)",
                            
                            # --- Financial Accounting & ERP ---
                            "💼 TallyPrime (GST Invoicing, Inventory & Ledgers)",
                            "📊 Tally.ERP 9 (Core Accounts & Vouchers)",
                            
                            # --- Web Development & Programming ---
                            "🌐 HTML / DHTML (Web Structure & Coding)",
                            "🐍 Python Programming (Logic, Apps & Scripting)",
                            
                            # --- IT Essentials & Computer Foundation ---
                            "🎨 MS Paint (Basics & Mouse Controls)",
                            "📝 Notepad (Text Editing & Coding Basics)",
                            "📄 WordPad (Basic Rich Text Formatting)",
                            "🌐 Internet Essentials (Email, Web Portals & Cyber)",
                            "⌨️ Typing Master (Assamese & English Speed Lab)",
                            
                            # --- Special ---
                            "🎯 Special Revision / Student Practical Project"
                        ]
                        selected_module = st.selectbox("Select Learning Track / Software:*", module_options)
                        topic_detail = st.text_input("Core Chapter / Practical Task Done (e.g., Table tags, Salary Sheet, Visiting Card):*")
                        today_topic = f"{selected_module} ➔ {topic_detail.strip()}" if topic_detail.strip() else selected_module
                        class_remarks = st.text_input("Teacher Feedback / Lab Performance*", value="Completed Practical Exercise Well")
                        
                    if st.form_submit_button("🟢 Save Today's Class Entry"):
                        if today_topic:
                            sid_val = sel_st.split(" - ")[0]
                            conn.execute('''
                                INSERT INTO daily_class_logs (date, student_id, teacher_name, topic, class_type, remarks)
                                VALUES (?, ?, ?, ?, ?, ?)
                            ''', (str(entry_date), sid_val, sel_tch, today_topic, class_mode, class_remarks))
                            conn.commit()
                            sync_all_to_cloud(conn)
                            st.success(f"✅ Recorded {class_mode} on '{today_topic}' for {sel_st}!")
                            st.rerun()
                        else:
                            st.error("Please enter Topic Covered!")
            else:
                st.info("No students registered yet.")
                
        with tab_cl2:
            st.write("### 🔍 Filter & Review Class History")
    
            col_f1, col_f2 = st.columns(2)
            with col_f1:
            # ছাত্ৰ বাছনি কৰাৰ ফিল্টাৰ
            student_opts = ["-- All Students --"] + [f"{r['student_id']} - {r['name']}" for r in conn.execute("SELECT student_id, name FROM students ORDER BY name ASC").fetchall()]
            sel_student_filter = st.selectbox("Filter by Student:", student_opts)
    
        with col_f2:
            # ক'ৰ্ছ/মডিউল বাছনি কৰাৰ ফিল্টাৰ
            module_filter_opts = ["-- All Modules --", "MS Word", "MS Excel", "MS PowerPoint", "Adobe PageMaker", "Adobe Photoshop", "TallyPrime", "Tally.ERP 9", "HTML", "Python", "Paint", "Notepad", "Typing Master"]
            sel_module_filter = st.selectbox("Filter by Module:", module_filter_opts)

        # কুৱেৰী প্ৰস্তুত কৰা
        query = """
            SELECT d.date as Date, d.student_id as [Student ID], s.name as [Student Name], 
                   d.teacher_name as [Faculty], d.topic as [Topic / Software Covered], 
                   d.class_type as [Mode], d.remarks as [Remarks]
            FROM daily_class_logs d
            LEFT JOIN students s ON d.student_id = s.student_id
            WHERE 1=1
        """
        params = []

        if sel_student_filter != "-- All Students --":
            filter_sid = sel_student_filter.split(" - ")[0].strip()
            query += " AND d.student_id = ?"
            params.append(filter_sid)
    
        if sel_module_filter != "-- All Modules --":
            query += " AND d.topic LIKE ?"
            params.append(f"%{sel_module_filter}%")
    
        query += " ORDER BY d.id DESC LIMIT 50"
    
        filtered_logs = conn.execute(query, params).fetchall()
        
        if filtered_logs:
            df_logs = pd.DataFrame([dict(r) for r in filtered_logs])
            st.dataframe(df_logs, use_container_width=True)
        else:
            st.info("ℹ️ No class logs match your selected filter.")

# -------------------------------------------------------------
# 7. FACULTY DESK & STRICT HONORARIUM ENGINE (₹230 / 3 SHIFTS)
# -------------------------------------------------------------
elif menu == "👨‍🏫 Faculty Desk & Honorarium":
    st.subheader("👨‍🏫 Faculty Management & Session-Linked Honorarium Engine")
    now_ist = datetime.datetime.now(IST)
    st.info(f"🕒 **Current IST Clock:** `{now_ist.strftime('%I:%M:%S %p (%d-%B-%Y)')}`")
    
    if verify_staff_access("Faculty Desk"):
        # --- CHECK ADMIN SECRET LOCK FOR TODAY ---
        today_str = str(datetime.date.today())
        import os
        is_unlocked = (st.session_state.get("teacher_unlock_date") == today_str)
        if os.path.exists("attendance_lock.txt"):
            try:
                with open("attendance_lock.txt") as f:
                    if f.read().strip() == today_str:
                        is_unlocked = True
            except:
                pass

        if not is_unlocked:
            st.warning("🔒 Teacher attendance window is currently closed. It will open during institute session hours.")
            st.info("ℹ️ For Student Attendance, Exam Desk, or Admission Desk, please use the sidebar navigation.")
            st.stop()
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
                
                col_tp1, col_tp2, col_tp3 = st.columns(3)
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
                                st.markdown(f"""
                                <style>
                                @keyframes blinker {{
                                    0% {{ opacity: 1.0; border-color: #d32f2f; box-shadow: 0 0 12px rgba(211,47,47,0.8); }}
                                    50% {{ opacity: 0.25; border-color: #ffcdd2; box-shadow: none; }}
                                    100% {{ opacity: 1.0; border-color: #d32f2f; box-shadow: 0 0 12px rgba(211,47,47,0.8); }}
                                }}
                                .blink-alert-box {{
                                    background-color: #ffebee;
                                    border: 3px solid #d32f2f;
                                    border-radius: 10px;
                                    padding: 15px;
                                    text-align: center;
                                    animation: blinker 1s linear infinite;
                                    margin-top: 10px;
                                    margin-bottom: 15px;
                                }}
                                </style>
                                <div class="blink-alert-box">
                                    <h3 style="color: #b71c1c; margin: 0; font-size: 18px;">🚨 ATTENTION FACULTY: DELAYED PUNCH IN ({late_by} MINS LATE)</h3>
                                    <p style="color: #212121; margin: 8px 0 0 0; font-size: 14px; font-weight: bold;">
                                        ⚠️ Late arrival beyond permitted grace limit recorded.<br>
                                        Automated session audit logged & honorarium penalty applied under institute service rules.
                                    </p>
                                </div>
                                """, unsafe_allow_html=True)
                                import time
                                time.sleep(4)
                            else:
                                st.success(f"✅ On-Time Session Punch IN at {time_str}! Shift successfully verified.")
                                import time
                                time.sleep(2)
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
                with col_tp3:
                    if st.button("🟡 Mark Leave (₹0)", use_container_width=True):
                        today_str = str(datetime.date.today())
                        conn.execute('''
                            INSERT INTO teacher_punches (teacher_name, date, shift, time_in, time_out, late_mins, penalty_cut, net_batch_earning, status)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (t_name, today_str, t_shift, "LEAVE", "LEAVE", 0, 0.0, 0.0, "Leave"))
                        conn.commit()
                        sync_all_to_cloud(conn)
                        st.info(f"Recorded: {t_name} marked on Official Leave (₹0 Payout).")
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
        # --- SECRET TEACHER ATTENDANCE SWITCH ---
        today_str = str(datetime.date.today())
        import os
        is_unlocked = st.session_state.get("teacher_unlock_date") == today_str
        unlock_switch = st.toggle("🔓 Unlock Teacher Attendance for Today", value=is_unlocked)

        if unlock_switch:
            st.session_state["teacher_unlock_date"] = today_str
            with open("attendance_lock.txt", "w") as f:
                f.write(today_str)
            st.caption("🟢 Teacher attendance desk is currently ACTIVE for today.")
        else:
            st.session_state["teacher_unlock_date"] = None
            if os.path.exists("attendance_lock.txt"):
                os.remove("attendance_lock.txt")
            st.caption("🔴 Teacher attendance desk is currently LOCKED.")
        st.divider()      
        dir_t1, dir_t2, dir_t3, dir_t4, dir_t5, dir_t6, dir_t7, dir_t8 = st.tabs([
            "📋 Executive Briefing",
            "💬 Public Enquiries (Leads)",
            "⭐ Teacher Ratings & Audit",
            "✏️ Edit & Remove Students",
            "💰 Financials & Fee Dues",
            "💾 1-Click Excel Backup",
            "🔐 Security & PIN Settings",
            "👥 All Students Directory"
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
            st.markdown("---")
            st.subheader("💰 Faculty Honorarium & Payroll Settlement (Director Confidential)")

            f_list_raw = conn.execute("SELECT DISTINCT name FROM teachers").fetchall()
            faculty_names = [r["name"] for r in f_list_raw] if f_list_raw else []
        if not faculty_names:
            p_names = conn.execute("SELECT DISTINCT teacher_name FROM teacher_punches").fetchall()
            faculty_names = [r["teacher_name"] for r in p_names if r["teacher_name"]]

        if faculty_names:
            f_col1, f_col2 = st.columns([2, 2])
            with f_col1:
                sel_fac = st.selectbox("Select Faculty Member:", faculty_names, key="dir_pay_fac")
            with f_col2:
                pay_filter = st.selectbox("Filter Period:", ["Current Month", "All Time Records"], key="dir_pay_period")

            if pay_filter == "Current Month":
                curr_month = str(datetime.date.today())[:7]
                punches = conn.execute(
                    "SELECT * FROM teacher_punches WHERE teacher_name = ? AND date LIKE ? ORDER BY date DESC, id DESC",
                    (sel_fac, f"{curr_month}%")
                ).fetchall()
            else:
                punches = conn.execute(
                    "SELECT * FROM teacher_punches WHERE teacher_name = ? ORDER BY date DESC, id DESC",
                    (sel_fac,)
                ).fetchall()

            if punches:
                p_df = pd.DataFrame([dict(r) for r in punches])
                
                leave_mask = (p_df["status"].astype(str).str.lower() == "leave") | (p_df["time_in"] == "LEAVE")
                total_shifts = len(p_df[~leave_mask])
                total_leaves = len(p_df[leave_mask])
                total_penalties = float(p_df["penalty_cut"].fillna(0).sum()) if "penalty_cut" in p_df.columns else 0.0
                total_payable = float(p_df["net_batch_earning"].fillna(0).sum()) if "net_batch_earning" in p_df.columns else 0.0

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Verified Shifts", f"{total_shifts} Sessions")
                m2.metric("Official Leaves", f"{total_leaves} Days")
                m3.metric("Late Penalties", f"₹{total_penalties:,.2f}")
                m4.metric("Total Payable Payout", f"₹{total_payable:,.2f}")

                st.caption(f"Showing shift-by-shift verified ledger for **{sel_fac}** ({pay_filter}):")
                disp_cols = [c for c in ["date", "shift", "time_in", "time_out", "late_mins", "penalty_cut", "net_batch_earning", "status"] if c in p_df.columns]
                st.dataframe(p_df[disp_cols], use_container_width=True)
            else:
                st.info(f"No attendance or punch records found for {sel_fac} ({pay_filter}).")
        else:
            st.info("No registered faculty members found in database.")
# --- ONE TIME NOVEMBER BACKFILL BUTTON (UP TO NOV 27) ---
        with st.expander("⚙️ November 1–27 Attendance Backfill (Director Only)"):
            if st.button("📥 Insert Nov 1-27 Backlog Records (39 Present, 14 Leave)", type="secondary"):
                # Clean existing backlog for Nov 1-27 if any to avoid duplicates
                conn.execute("DELETE FROM teacher_punches WHERE teacher_name = 'BIJOY KURMI' AND date BETWEEN '2026-11-01' AND '2026-11-27'")
                
                shifts_pool = ["Morning Slot: 07:00 AM - 08:30 AM", "Afternoon Slot: 03:00 PM - 05:00 PM", "Evening Slot: 05:30 PM - 07:00 PM"]
                inserted_present = 0
                inserted_leave = 0
                
                # 39 verified present shifts (Nov 1 to Nov 24)
                for i in range(39):
                    d_day = min(1 + (i // 3), 24)
                    d_str = f"2026-11-{d_day:02d}"
                    s_slot = shifts_pool[i % 3]
                    conn.execute("""
                        INSERT INTO teacher_punches (date, teacher_name, shift, time_in, time_out, late_mins, penalty_cut, net_batch_earning, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (d_str, "BIJOY KURMI", s_slot, "10:00 AM", "12:00 PM", 0, 0.0, 76.67, "Present"))
                    inserted_present += 1
                    
                # 6 verified earlier leaves (before Nov 25)
                for j in range(6):
                    d_day = 18 + (j // 3)
                    d_str = f"2026-11-{d_day:02d}"
                    s_slot = shifts_pool[j % 3]
                    conn.execute("""
                        INSERT INTO teacher_punches (date, teacher_name, shift, time_in, time_out, late_mins, penalty_cut, net_batch_earning, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (d_str, "BIJOY KURMI", s_slot, "LEAVE", "LEAVE", 0, 0.0, 0.0, "Leave"))
                    inserted_leave += 1
                
                # Nov 25 (Wednesday - 3 shifts leave)
                for s in shifts_pool:
                    conn.execute("INSERT INTO teacher_punches (date, teacher_name, shift, time_in, time_out, late_mins, penalty_cut, net_batch_earning, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                 ('2026-11-25', 'BIJOY KURMI', s, 'LEAVE', 'LEAVE', 0, 0.0, 0.0, 'Leave'))
                    inserted_leave += 1

                # Nov 26 (Thursday - Afternoon & Evening 2 shifts leave)
                for s in [shifts_pool[1], shifts_pool[2]]:
                    conn.execute("INSERT INTO teacher_punches (date, teacher_name, shift, time_in, time_out, late_mins, penalty_cut, net_batch_earning, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                 ('2026-11-26', 'BIJOY KURMI', s, 'LEAVE', 'LEAVE', 0, 0.0, 0.0, 'Leave'))
                    inserted_leave += 1

                # Nov 27 (Friday - 3 shifts leave)
                for s in shifts_pool:
                    conn.execute("INSERT INTO teacher_punches (date, teacher_name, shift, time_in, time_out, late_mins, penalty_cut, net_batch_earning, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                 ('2026-11-27', 'BIJOY KURMI', s, 'LEAVE', 'LEAVE', 0, 0.0, 0.0, 'Leave'))
                    inserted_leave += 1
                    
                conn.commit()
                sync_all_to_cloud(conn)
                st.success(f"✅ Successfully restored! 39 Present & 14 Leave shifts added up to Nov 27.")
                st.rerun()
        # TAB 4: EDIT STUDENTS
        with dir_t4:
            st.write("#### Update Student Profile & Sarva Head Office Reg No")
            all_students = conn.execute("SELECT * FROM students").fetchall()
            if all_students:
                s_opts = [f"{r['student_id']} - {r['name']} ({r['course']})" for r in all_students]
                chosen_s = st.selectbox("Select Student to Edit or Remove:", s_opts)
                target_sid = chosen_s.split(" - ")[0]
                s_data = conn.execute("SELECT * FROM students WHERE student_id = ?", (target_sid,)).fetchone()

                col_ed1, col_ed2 = st.columns(2)
                with col_ed1:
                    st.write("***Edit Candidate Information:***")
                    with st.form("edit_student_form"):
                        ed_name = st.text_input("Candidate Name*", value=s_data["name"])
                        ed_fname = st.text_input("Father's Name*", value=s_data["father_name"])
                        ed_mname = st.text_input("Mother's Name*", value=s_data["mother_name"] or "")
                        ed_mob = st.text_input("Mobile Number*", value=s_data["mobile"])
                        ed_course = st.selectbox("Course*", COURSE_NAMES, index=COURSE_NAMES.index(s_data["course"]) if s_data["course"] in COURSE_NAMES else 0)
                        
                        curr_sh_str = str(s_data["shift"] or "")
                        col_esh1, col_esh2 = st.columns(2)
                        with col_esh1:
                            base_shift_opts = [
                                "Morning Slot: 07:00 AM - 08:30 AM",
                                "Afternoon Slot: 04:00 PM - 05:30 PM",
                                "Evening Slot: 05:30 PM - 07:00 PM"
                            ]
                            d_s_idx = 0
                            for idx, bso in enumerate(base_shift_opts):
                                if bso.split(":")[0] in curr_sh_str:
                                    d_s_idx = idx
                                    break
                            ed_shift_base = st.selectbox("Shift Slot*", base_shift_opts, index=d_s_idx)
                        with col_esh2:
                            d_r_idx = 1 if "TTS" in curr_sh_str else 0
                            ed_routine = st.selectbox("Routine*", ["MWF (Mon-Wed-Fri)", "TTS (Tue-Thu-Sat)"], index=d_r_idx)

                        ed_shift = f"{ed_shift_base} ({ed_routine[:3]})"
                        ed_fee = st.number_input("Course Net Fee (₹)*", value=float(s_data["net_fee"]) if s_data["net_fee"] else COURSE_CATALOG[ed_course]["fee"])
                        ed_stage = st.selectbox("Lifecycle Stage*", ["Admission", "Learning/Tests", "Course Completed", "HO Registered", "Exam Appeared", "Certificate Handover"], index=["Admission", "Learning/Tests", "Course Completed", "HO Registered", "Exam Appeared", "Certificate Handover"].index(s_data["lifecycle_stage"]) if s_data["lifecycle_stage"] in ["Admission", "Learning/Tests", "Course Completed", "HO Registered", "Exam Appeared", "Certificate Handover"] else 0)
                        ed_ho = st.text_input("Sarva HO Registration No (From admin.sarvaeducation.in)*", value=s_data["ho_reg_no"] or "")
                        ed_cert = st.text_input("Certificate Serial No*", value=s_data["cert_serial_no"] or "")

                        if st.form_submit_button("🟢 Update Candidate Details"):
                            conn.execute("UPDATE students SET name = ?, father_name = ?, mother_name = ?, mobile = ?, course = ?, shift = ?, net_fee = ?, lifecycle_stage = ?, ho_reg_no = ?, cert_serial_no = ? WHERE student_id = ?", (ed_name.upper(), ed_fname.upper(), ed_mname.upper(), ed_mob.strip(), ed_course, ed_shift, ed_fee, ed_stage, ed_ho.strip(), ed_cert.strip(), target_sid))
                            conn.commit()
                            sync_all_to_cloud(conn)
                            st.success(f"Student {target_sid} Updated Successfully!")
                            st.rerun()
                            
        with col_ed2:
            st.write("**📸 Update Student Photo**")
            p_col = next((c for c in s_data.keys() if "photo" in c.lower()), "photo_base64")
            curr_photo = s_data[p_col] if p_col in s_data.keys() else None
            if curr_photo and len(str(curr_photo)) > 50:
                st.markdown(f'<img src="data:image/jpeg;base64,{curr_photo}" style="width:100px; height:100px; object-fit:cover; border-radius:8px; border:1px solid #ccc;">', unsafe_allow_html=True)
            p_mode = st.radio("Photo Source", ["Direct Camera", "Gallery Upload"], horizontal=True, key=f"pmode_{target_sid}")
            new_photo = st.camera_input("Click Live Photo", key=f"cam_{target_sid}") if p_mode == "Direct Camera" else st.file_uploader("Upload Photo", type=["jpg", "jpeg", "png"], key=f"up_{target_sid}")
            if new_photo is not None:
                if st.button("💾 Save New Photo", key=f"save_ph_{target_sid}"):
                    try:
                        from PIL import Image
                        import io
                        img = Image.open(new_photo).convert("RGB")
                        img.thumbnail((300, 300))
                        buf = io.BytesIO()
                        img.save(buf, format="JPEG", quality=70)
                        b64_img = base64.b64encode(buf.getvalue()).decode()
                    except Exception:
                        b64_img = base64.b64encode(new_photo.getvalue()).decode()
                    conn.execute(f"UPDATE students SET {p_col} = ? WHERE student_id = ?", (b64_img, target_sid))
                    conn.commit()
                    sync_all_to_cloud(conn)
                    st.success(f"Photo updated for {target_sid}!")
                    st.rerun()
            st.markdown("---")
            st.write("***Danger Zone: Remove Student***")
            confirm_del = st.checkbox(f"I confirm to permanently delete student {target_sid}", key=f"del_chk_{target_sid}")
            if confirm_del:
                if st.button("🔴 Permanently Delete Student", type="primary"):
                    conn.execute("DELETE FROM students WHERE student_id = ?", (target_sid,))
                    conn.execute("DELETE FROM fees WHERE student_id = ?", (target_sid,))
                    conn.execute("DELETE FROM attendance WHERE student_id = ?", (target_sid,))
                    conn.execute("DELETE FROM marks WHERE student_id = ?", (target_sid,))
                    conn.execute("DELETE FROM daily_class_logs WHERE student_id = ?", (target_sid,))
                    conn.execute("DELETE FROM teacher_ratings WHERE student_id = ?", (target_sid,))
                    conn.commit()
                    sync_all_to_cloud(conn)
                    st.success(f"Student {target_sid} removed completely!")
                    st.rerun()
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
            # Mistaken / Duplicate Fee Reversal Utility
            st.markdown("---")
            st.write("#### 🗑️ Reverse / Delete Mistaken Fee Entry")
            
            recent_fees_df = pd.read_sql("""
                SELECT id AS [Fee ID], student_id AS [Roll ID], amount AS [Amount (₹)], date AS [Date], mode AS [Mode] 
                FROM fees 
                ORDER BY id DESC LIMIT 100
            """, conn)
            st.write("**Recent Fee Transactions (Check the Fee ID to delete):**")
            st.dataframe(recent_fees_df, use_container_width=True, hide_index=True)
            
            col_del1, col_del2 = st.columns([2, 1])
            with col_del1:
                del_fee_id = st.number_input("Enter Fee ID to permanently remove:", min_value=1, step=1, key="input_del_fee")
            with col_del2:
                st.write("")
                st.write("")
                if st.button("🚨 Delete This Fee Entry", key="btn_del_fee"):
                    conn.execute("DELETE FROM fees WHERE id = ?", (del_fee_id,))
                    conn.commit()
                    st.success(f"Transaction Fee ID {del_fee_id} deleted successfully!")
                    st.rerun()

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
                            sync_all_to_cloud(conn)
                            st.success("Director Password updated successfully!")
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
        with dir_t8:
            st.write("### 👥 All Enrolled Students Master Directory")
            
            df_students = pd.read_sql("""
                SELECT 
                    student_id AS [Roll ID],
                    name AS [Full Name],
                    father_name AS [Father's Name],
                    mobile AS [Mobile],
                    course AS [Course],
                    shift AS [Shift & Routine],
                    net_fee AS [Net Fee (₹)],
                    lifecycle_stage AS [Lifecycle Stage],
                    ho_reg_no AS [Sarva HO Reg],
                    cert_serial_no AS [Certificate Serial]
                FROM students
                ORDER BY student_id ASC
            """, conn)
            
            if not df_students.empty:
                col_s1, col_s2 = st.columns([3, 1])
                with col_s1:
                    search_q = st.text_input("🔍 Quick Search (Search by Name, Roll ID, Mobile, or Course):", key="search_master_dir")
                with col_s2:
                    st.write("")
                    st.write("")
                    csv_data = df_students.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download Directory (CSV)",
                        data=csv_data,
                        file_name="All_Students_Directory.csv",
                        mime="text/csv",
                        key="dl_master_all_students"
                    )

                if search_q:
                    df_students = df_students[
                        df_students["Full Name"].astype(str).str.contains(search_q, case=False, na=False) |
                        df_students["Roll ID"].astype(str).str.contains(search_q, case=False, na=False) |
                        df_students["Mobile"].astype(str).str.contains(search_q, case=False, na=False) |
                        df_students["Course"].astype(str).str.contains(search_q, case=False, na=False)
                    ]

                st.dataframe(df_students, use_container_width=True, hide_index=True)
                st.info(f"Total Students: {len(df_students)}")
            else:
                st.warning("No student records found in database.")
                       
    elif adm_pass:
        st.error("❌ Incorrect Director Security Password!")

conn.close()

# Footer
st.markdown("""
<div style="text-align:center; padding:20px; font-size:12px; color:#64748B; border-top:1px solid #E2E8F0; margin-top:40px;">
Soft-Tech Computers & ZTC Enterprise Management System © 2026 | SITED Center Code: 4159 | Kamarchuburi, Thelamara, Sonitpur - 784149
</div>
""", unsafe_allow_html=True)



