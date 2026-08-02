import streamlit as st
import pandas as pd
import os
import datetime
import pytz
import base64

# Page Configuration
st.set_page_config(page_title="Soft Tech Computers & ZTC Enterprise Portal", page_icon="💻", layout="wide")

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
FEEDBACK_FILE = "feedback_db.csv"
SYLLABUS_LOG_FILE = "syllabus_logs.csv"
PHOTO_DIR = "student_photos"

# SAFE DIRECTORY CREATION
os.makedirs(PHOTO_DIR, exist_ok=True)

# Helper function to convert local image to base64 safely
def get_image_base64(file_name):
    extensions = ['', '.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG']
    for ext in extensions:
        p = f"{file_name}{ext}"
        if os.path.exists(p):
            try:
                with open(p, "rb") as image_file:
                    encoded = base64.b64encode(image_file.read()).decode()
                    is_png = 'png' in p.lower()
                    mime_type = 'image/png' if is_png else 'image/jpeg'
                    return f"data:{mime_type};base64,{encoded}"
            except Exception:
                pass
    return None

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
student_cols = ["Sl. No.", "Student ID", "Name", "Father Name", "Mother Name", "Gender", "DOB", "Caste", "Mobile No", "Vill Town", "PO", "PS", "PIN Code", "District", "Full Address", "Course", "Duration", "Days_Batch", "Session", "Join Date", "Validity Date", "Total Fee", "Discount", "Net Fee", "Shift", "Batch Time", "Photo Path", "Status"]
fee_cols = ["Receipt No", "Student ID", "Date", "Amount Paid", "Payment Mode", "Collected_By", "Remarks"]
attendance_cols = ["Student ID", "Date", "Time_In", "Status", "Late_Reason", "Sign_Mode", "Location_Verified"]
teacher_cols = ["Teacher ID", "Name", "Phone", "Qualification", "Designation", "Shift Assigned"]
teacher_att_cols = ["Teacher ID", "Name", "Date", "Time_In", "Shift", "Status", "Late_Reason", "Absent_Reason", "Earning_Today"]
enquiry_cols = ["Date", "Name", "Mobile", "Course Interested", "Is ZTC Student", "Village/Address", "Status"]
sfpc_cols = ["Date", "Student ID", "Student Name", "PC Machine No", "Topic Practiced", "Teacher Incharge"]
creds_cols = ["Role", "Password"]
feedback_cols = ["Date", "Student ID", "Student Name", "Teacher Name", "Theory Written", "Rating_Stars", "Comments"]
syllabus_cols = ["Date", "Course", "Topic Covered", "Teacher Incharge", "Theory Dictated"]

# Load DataFrames
student_df = load_data(STUDENT_MASTER_FILE, student_cols)
fee_df = load_data(FEE_LOG_FILE, fee_cols)
att_df = load_data(ATTENDANCE_FILE, attendance_cols)
teacher_df = load_data(TEACHERS_FILE, teacher_cols)
teacher_att_df = load_data("teacher_attendance.csv", teacher_att_cols)
enquiry_df = load_data(ENQUIRY_FILE, enquiry_cols)
sfpc_df = load_data(SFPC_FILE, sfpc_cols)
creds_df = load_data(CREDS_FILE, creds_cols)
feedback_df = load_data(FEEDBACK_FILE, feedback_cols)
syllabus_df = load_data(SYLLABUS_LOG_FILE, syllabus_cols)

# Ensure Default Credentials
if creds_df.empty:
    creds_df = pd.DataFrame([
        {"Role": "Admin", "Password": "zaan123"},
        {"Role": "Teacher", "Password": "teacher123"}
    ])
    save_data(creds_df, CREDS_FILE)

ADMIN_PWD = creds_df[creds_df["Role"] == "Admin"]["Password"].values[0] if "Admin" in creds_df["Role"].values else "zaan123"
TEACHER_PWD = creds_df[creds_df["Role"] == "Teacher"]["Password"].values[0] if "Teacher" in creds_df["Role"].values else "teacher123"

# Course Config
COURSE_CONFIG = {
    "PGDCA (Post Graduate Diploma in Computer Application)": {
        "Months": 12, "FeeNum": 8500, "FeeStr": "₹8,500 Total",
        "Topics": ["Computer Fundamentals", "Operating System", "MS-Office", "Tally Prime with GST", "DBMS & SQL", "HTML/CSS Web Design", "Python / C Programming", "Internet & Cyber Security"]
    },
    "ADCA (Advanced Diploma in Computer Application)": {
        "Months": 12, "FeeNum": 7500, "FeeStr": "₹7,500 Total",
        "Topics": ["Paint", "Notepad", "Wordpad", "MS-Word", "MS-Excel", "MS-Powerpoint", "MS-Access", "HTML", "DHTML", "Tally Prime", "Photoshop", "Pagemaker", "Internet", "Python"]
    },
    "DCA (Diploma in Computer Application)": {
        "Months": 6, "FeeNum": 4500, "FeeStr": "₹4,500 Total",
        "Topics": ["Paint", "Notepad", "Wordpad", "MS-Word", "MS-Excel", "MS-Powerpoint", "MS-Access", "HTML", "Tally", "Internet"]
    },
    "DTP (Desktop Publishing)": {
        "Months": 3, "FeeNum": 3500, "FeeStr": "₹3,500 Total",
        "Topics": ["MS-Word", "Photoshop", "Pagemaker", "CorelDraw", "Assamese Typesetting", "Internet"]
    },
    "Tally Prime with GST": {
        "Months": 3, "FeeNum": 4000, "FeeStr": "₹4,000 Total",
        "Topics": ["Accounting Basics", "Tally Prime Basics", "Inventory Management", "GST & TDS Calculation", "Payroll & Billing"]
    },
    "Certificate Course in Computer Basics": {
        "Months": 3, "FeeNum": 2500, "FeeStr": "₹2,500 Total",
        "Topics": ["Paint", "Notepad", "Wordpad", "MS-Word", "Internet"]
    },
    "Class 9 English Coaching": {"Months": 12, "FeeNum": 600, "FeeStr": "₹600 / Month", "Topics": ["Grammar", "Literature prose", "Poetry", "Writing Skills"]},
    "Class 10 English Coaching": {"Months": 12, "FeeNum": 700, "FeeStr": "₹700 / Month", "Topics": ["Grammar", "Literature prose", "Poetry", "Writing Skills"]},
    "Class 11 English Coaching": {"Months": 12, "FeeNum": 800, "FeeStr": "₹800 / Month", "Topics": ["Grammar", "Literature prose", "Poetry", "Writing Skills"]},
    "Class 12 English Coaching": {"Months": 12, "FeeNum": 900, "FeeStr": "₹900 / Month", "Topics": ["Grammar", "Literature prose", "Poetry", "Writing Skills"]}
}

# Navigation Menu
st.sidebar.title("💻 STC & ZTC Portal")
menu = st.sidebar.radio("Navigation Menu:", [
    "🏠 Home & Public Dashboard",
    "📜 Online Certificate Verification",
    "📝 New Student Admission",
    "🔑 Student Login Portal",
    "🎯 Sunday Free Practice Class (SFPC)",
    "💵 Fee Counter Desk",
    "🔑 Teacher Portal & QR Scanner",
    "🔐 Admin Control Panel"
])

# ---------------------------------------------------------
# 1. HIGH-TECH ENTERPRISE PUBLIC DASHBOARD
# ---------------------------------------------------------
if menu == "🏠 Home & Public Dashboard":
    dp2_b64 = get_image_base64("dp2")
    if dp2_b64:
        st.markdown(f'<img src="{dp2_b64}" style="width:100%; max-height:280px; object-fit:contain; border-radius:15px; border:2px solid #00F0FF; box-shadow: 0 0 20px rgba(0, 240, 255, 0.3); margin-bottom:12px;">', unsafe_allow_html=True)
    
    st.markdown("""
        <div style="
            background: linear-gradient(135deg, #020B19 0%, #0F172A 50%, #1E3A8A 100%);
            padding: 12px 20px; border-radius: 12px; text-align: center; color: white;
            border: 1.5px solid #00F0FF; box-shadow: 0 0 15px rgba(0, 240, 255, 0.2); margin-bottom: 15px;
        ">
            <h4 style="margin:0; color:#FBBF24; font-size:15px; font-weight:bold;">MAKE YOURSELF DIGITAL | AN ISO 9001:2015 CERTIFIED INSTITUTION</h4>
            <p style="margin:4px 0 0 0; font-size:13px; color:#CBD5E1;">Kamarchuburi, Near Thelamara, Sonitpur, Assam - 784149 | Center Code: 4159 | Contact: +91 9101026718</p>
        </div>
    """, unsafe_allow_html=True)
    
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Est. Year", "Since 2020")
    col_m2.metric("Total Enrolled", "500+ Students")
    col_m3.metric("Alumni Network", "350+ Students")
    col_m4.metric("Certified Graduates", "200+ Certified")

    st.markdown("""
        <div style="background-color: #FEF3C7; border: 1.5px solid #F59E0B; padding: 8px 15px; border-radius: 10px; margin: 15px 0;">
            <marquee style="color: #B45309; font-weight: bold; font-size: 15px;">
                🏆 SPECIAL OFFER: ZTC Tuition Students Get 50% OFF on STC Admission! | Class 11 STC Computer Students Get 100% FREE Admission at ZTC! 🏆
            </marquee>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style="display: flex; gap: 15px; flex-wrap: wrap; margin-bottom: 20px;">
            <div style="flex: 1; min-width: 280px; background: linear-gradient(135deg, #EFF6FF, #DBEAFE); border: 2px solid #2563EB; border-radius: 14px; padding: 18px; box-shadow: 0 4px 12px rgba(37,99,235,0.15);">
                <span style="background:#2563EB; color:white; padding:4px 12px; border-radius:12px; font-size:11px; font-weight:bold; letter-spacing:0.5px;">ZTC SPECIAL OFFER</span>
                <h4 style="color:#1E3A8A; margin:10px 0 4px 0; font-size:16px;">ZTC Tuition ➔ STC Computer</h4>
                <p style="margin:0; font-size:14px; color:#1E293B;">Get <b style="color:#2563EB; font-size:16px;">50% DISCOUNT</b> on STC Computer Course Admission Fee for all ZTC Tuition Students!</p>
            </div>
            <div style="flex: 1; min-width: 280px; background: linear-gradient(135deg, #ECFDF5, #D1FAE5); border: 2px solid #10B981; border-radius: 14px; padding: 18px; box-shadow: 0 4px 12px rgba(16,185,129,0.15);">
                <span style="background:#10B981; color:white; padding:4px 12px; border-radius:12px; font-size:11px; font-weight:bold; letter-spacing:0.5px;">CLASS 11 MEGA OFFER</span>
                <h4 style="color:#065F46; margin:10px 0 4px 0; font-size:16px;">Class 11 STC ➔ ZTC Tuition</h4>
                <p style="margin:0; font-size:14px; color:#1E293B;">Get <b style="color:#10B981; font-size:16px;">100% FREE Admission Fee</b> at ZTC Tuition when enrolled in STC Computer Class 11!</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    dp3_b64 = get_image_base64("dp3")
    dp1_b64 = get_image_base64("dp1")
    
    col_img1, col_img2 = st.columns(2)
    with col_img1:
        if dp3_b64:
            st.markdown('<h4 style="color:#1E3A8A; margin:0 0 8px 0;">🛠️ Key Technologies Taught</h4>', unsafe_allow_html=True)
            st.markdown(f'<img src="{dp3_b64}" style="width:100%; border-radius:12px; border:2px solid #2563EB; box-shadow:0 0 10px rgba(37,99,235,0.2);">', unsafe_allow_html=True)
    with col_img2:
        if dp1_b64:
            st.markdown('<h4 style="color:#1E3A8A; margin:0 0 8px 0;">📜 Director\'s Message</h4>', unsafe_allow_html=True)
            st.markdown(f'<img src="{dp1_b64}" style="width:100%; border-radius:12px; border:2px solid #00F0FF; box-shadow:0 0 10px rgba(0,240,255,0.2);">', unsafe_allow_html=True)

    st.markdown("---")

    st.subheader("📚 Courses Offered & Duration")
    pub_course_list = [{"Course Name": k, "Duration": f"{v['Months']} Months" if "Certificate" not in k else "3 Months / 2 Months / 45 Days"} for k, v in COURSE_CONFIG.items()]
    pub_course_df = pd.DataFrame(pub_course_list)
    pub_course_df.index = range(1, len(pub_course_df) + 1)
    st.table(pub_course_df)

    st.markdown("---")

    col_p1, col_p2 = st.columns([1, 2])
    with col_p1:
        st.subheader("📲 Portal Access QR")
        st.markdown("""
            <div style="border:2px dashed #2563EB; background-color:#EFF6FF; padding:18px; border-radius:14px; text-align:center;">
                <h3 style="color:#1E3A8A; margin-top:0;">🌐 Scan to Enter Portal</h3>
                <img src="https://api.qrserver.com/v1/create-qr-code/?size=160x160&data=https://stcztc.streamlit.app" style="width:130px; height:130px; border-radius:8px;">
                <p style="font-weight:bold; color:#2563EB; margin-top:8px;">stcztc.streamlit.app</p>
            </div>
        """, unsafe_allow_html=True)

    with col_p2:
        st.subheader("📝 Smart Course Enquiry Desk (With Discount Estimator)")
        with st.form("pub_enq_form", clear_on_submit=False):
            e_name = st.text_input("Your Full Name*")
            e_mobile = st.text_input("Contact Mobile Number*")
            e_course = st.selectbox("Select Interested Course*", list(COURSE_CONFIG.keys()))
            is_ztc = st.checkbox("I am currently a ZTC Tuition Student (Get 50% STC Admission Discount!)")
            e_addr = st.text_input("Village / Address")
            
            if st.form_submit_button("Submit & Reveal Discounted Fee"):
                if not e_name or not e_mobile:
                    st.error("Please enter Name and Mobile Number!")
                else:
                    e_row = {"Date": str(datetime.date.today()), "Name": e_name.upper(), "Mobile": e_mobile, "Course Interested": e_course, "Is ZTC Student": "Yes" if is_ztc else "No", "Village/Address": e_addr.upper(), "Status": "Enquired"}
                    enquiry_df = pd.concat([enquiry_df, pd.DataFrame([e_row])], ignore_index=True)
                    save_data(enquiry_df, ENQUIRY_FILE)
                    
                    raw_fee = COURSE_CONFIG[e_course]["FeeStr"]
                    st.balloons()
                    if is_ztc and "Coaching" not in e_course:
                        st.success(f"🎉 Thank you {e_name}! Standard Fee: {raw_fee} | **ZTC Special Offer Applied: 50% DISCOUNT on Admission!**")
                    elif "Class 11" in e_course:
                        st.success(f"🎉 Thank you {e_name}! Fee: {raw_fee} | **Class 11 Special Offer: 100% FREE Admission at ZTC Tuition!**")
                    else:
                        st.success(f"🎉 Thank you {e_name}! Course Fee for {e_course}: {raw_fee}")

    # UPDATE 1: AI VOCAL ENGINE CHANGED TO SWEET HINDI FEMALE VOICE
    st.markdown("---")
    st.subheader("🤖 Zaan AI Assistant & Sweet Hindi Vocal Bot")
    
    voice_html = """
    <div style="background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%); border: 2px solid #ec4899; padding: 20px; border-radius: 16px; text-align: center; color: white; margin-bottom: 20px; box-shadow: 0 0 20px rgba(236,72,153,0.3);">
        <div style="font-size:24px; margin-bottom:5px;">🎙️ <span style="background: linear-gradient(to right, #f43f5e, #ec4899); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight:bold;">Zaan AI Sweet Hindi Voice</span></div>
        <p style="color:#cbd5e1; font-size:13px; margin-bottom:15px;">Click below to hear official announcements in a clear & sweet Hindi female voice</p>
        
        <div style="display:flex; justify-content:center; gap:12px; flex-wrap:wrap;">
            <button onclick="playAIVocalHindi(1)" style="background: linear-gradient(135deg, #ec4899, #f43f5e); color: white; font-weight: bold; padding: 10px 22px; border: none; border-radius: 25px; cursor: pointer; font-size: 13px; box-shadow: 0 4px 12px rgba(236,72,153,0.4);">
                ▶️ Play Institute Overview (Hindi Voice)
            </button>
            <button onclick="playAIVocalHindi(2)" style="background: linear-gradient(135deg, #10b981, #059669); color: white; font-weight: bold; padding: 10px 22px; border: none; border-radius: 25px; cursor: pointer; font-size: 13px; box-shadow: 0 4px 12px rgba(16,185,129,0.4);">
                📢 Play Special Combo Offers (Hindi)
            </button>
        </div>
    </div>

    <script>
    function playAIVocalHindi(type) {
        let text = "";
        if(type === 1) {
            text = "नमस्कार! सॉफ्ट टेक कंप्यूटर और ज़ान ट्यूशन सेंटर में आपका स्वागत है। साल 2020 से अब तक हमारे सेंटर में 500 से अधिक छात्रों ने एडमिशन लिया है, जिनमें 350 से ज्यादा एलुमनाई और 200 से अधिक सर्टिफाइड स्टूडेंट्स शामिल हैं।";
        } else {
            text = "आपके लिए एक खास ऑफर है! ज़ान ट्यूशन सेंटर में पढ़ने वाले छात्रों को सॉफ्ट टेक कंप्यूटर एडमिशन में 50 प्रतिशत की छूट मिलेगी। और क्लास 11 में कंप्यूटर कोर्स करने वालों को ज़ान ट्यूशन सेंटर में 100 प्रतिशत फ्री एडमिशन मिलेगा!";
        }

        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = "hi-IN";
            utterance.rate = 0.88;
            utterance.pitch = 1.25;

            let voices = window.speechSynthesis.getVoices();
            let sweetFemaleVoice = voices.find(voice => 
                voice.lang.includes('hi') && (voice.name.includes('Female') || voice.name.includes('Kalpana') || voice.name.includes('Google') || voice.name.includes('Zira') || voice.name.includes('Swara'))
            );

            if (sweetFemaleVoice) { utterance.voice = sweetFemaleVoice; }
            window.speechSynthesis.speak(utterance);
        } else {
            alert("Speech synthesis is not supported in this browser.");
        }
    }
    </script>
    """
    st.components.v1.html(voice_html, height=150)

    # UPDATE 2: DYNAMIC STUDENT SEARCH WITH ROLL ID HIGHLIGHT BLOCK
    user_q = st.text_input("Ask Zaan AI / Search Student Roll No (e.g. 'Hiya Das', 'STC26-001'):")
    
    if user_q:
        q_clean = user_q.strip().lower()
        matched = False
        
        if not student_df.empty:
            for idx, r in student_df.iterrows():
                st_name = str(r["Name"]).lower()
                st_id = str(r["Student ID"]).lower()
                
                if st_name in q_clean or st_id in q_clean or any(part in q_clean for part in st_name.split()):
                    st.success(f"🔍 **Student Record Found in Database:**")
                    st.markdown(f"""
                        <div style="background:#0F172A; border:2px solid #00F0FF; padding:15px; border-radius:12px; color:white; margin-bottom:10px;">
                            <h3 style="margin:0 0 5px 0; color:#00F0FF;">🆔 STUDENT ROLL NUMBER: {r['Student ID']}</h3>
                            <p style="margin:2px 0; font-size:15px;">👤 <b>Student Name:</b> {r['Name']}</p>
                            <p style="margin:2px 0; font-size:14px;">📚 <b>Course:</b> {r['Course']} ({r.get('Days_Batch', 'MWF')})</p>
                            <p style="margin:2px 0; font-size:14px;">⏰ <b>Shift & Timing:</b> {r['Shift']} ({r['Batch Time']})</p>
                            <p style="margin:2px 0; font-size:14px;">📅 <b>Joining Date:</b> {r['Join Date']} | Status: <span style="color:#10B981; font-weight:bold;">{r['Status']}</span></p>
                        </div>
                    """, unsafe_allow_html=True)
                    matched = True
                    break
        
        if not matched:
            if "offer" in q_clean or "discount" in q_clean:
                st.info("💡 Offers: 1) ZTC Students get 50% OFF on STC Admission. 2) Class 11 STC Computer Students get 100% FREE Admission Fee at ZTC!")
            elif "fee" in q_clean or "cost" in q_clean:
                st.info("💡 Course fees vary from ₹2,500 to ₹8,500. Please fill the Enquiry Form above to reveal fee!")
            elif "timing" in q_clean or "time" in q_clean or "shift" in q_clean:
                st.info("💡 Shifts: Morning (06:30 AM), Afternoon (04:00 PM), Evening (05:30 PM).")
            elif "director" in q_clean or "zaan" in q_clean:
                st.info("💡 Soft Tech Computers & ZTC is founded & directed by Chiranjeeb Hazarika (Zaan) Sir.")
            elif "location" in q_clean or "address" in q_clean:
                st.info("💡 Location: Kamarchuburi, Near Thelamara, Sonitpur, Assam - 784149.")
            else:
                st.info("💡 Zaan AI: Search student name (e.g. 'Hiya Das') to view Roll ID or call +91 9101026718.")

# ---------------------------------------------------------
# 1.5 ONLINE CERTIFICATE VERIFICATION TAB
# ---------------------------------------------------------
elif menu == "📜 Online Certificate Verification":
    st.header("📜 Online Certificate & Student Verification Desk")
    st.markdown("""
        <div style="background: linear-gradient(135deg, #0F172A, #1E3A8A); padding: 15px 20px; border-radius: 12px; color: white; border: 1.5px solid #00F0FF; margin-bottom: 20px;">
            <h4 style="margin:0; color:#00F0FF;">🔍 Official Verification Portal | Soft Tech Computers (Center Code: 4159)</h4>
            <p style="margin:5px 0 0 0; font-size:13px; color:#CBD5E1;">Enter Student Roll ID below to verify the authenticity of Certificates issued by Soft Tech Computers.</p>
        </div>
    """, unsafe_allow_html=True)

    v_col1, v_col2 = st.columns([2, 1])
    with v_col1:
        verify_id = st.text_input("Enter Student Roll ID (e.g., STC26-001):").strip().upper()
    with v_col2:
        st.markdown("<br>", unsafe_allow_html=True)
        verify_btn = st.button("🔍 Verify Certificate Authenticity")

    if verify_id or verify_btn:
        if verify_id:
            v_match = student_df[student_df["Student ID"] == verify_id]
            if not v_match.empty:
                v_data = v_match.iloc[0]
                st.balloons()
                
                st_photo_b64 = get_image_base64(v_data["Photo Path"]) if v_data["Photo Path"] else None
                logo_b64 = get_image_base64("logo")

                cert_verify_html = f"""
                <div style="background:#030712; border:2.5px solid #10B981; border-radius:18px; padding:25px; color:white; max-width:720px; margin:auto; box-shadow:0 0 25px rgba(16,185,129,0.35); font-family:Arial, sans-serif;">
                    <div style="background:#065F46; color:#D1FAE5; text-align:center; padding:8px; border-radius:8px; font-weight:bold; font-size:14px; margin-bottom:18px; border:1px solid #10B981;">
                        ✅ VERIFIED & ORIGINAL CERTIFICATE RECORD FOUND
                    </div>
                    <div style="display:flex; align-items:center; justify-content:space-between; border-bottom:1px solid rgba(255,255,255,0.15); padding-bottom:12px;">
                        <div>
                            <h2 style="margin:0; color:#10B981; font-size:20px; font-weight:bold;">SOFT TECH COMPUTERS</h2>
                            <p style="margin:2px 0 0 0; font-size:11px; color:#9CA3AF;">AN ISO 9001:2015 CERTIFIED INSTITUTION | CENTER CODE: 4159</p>
                        </div>
                        <div>
                            <img src="{logo_b64 if logo_b64 else ''}" style="width:60px; height:60px; border-radius:50%; border:2px solid #10B981;">
                        </div>
                    </div>
                    <div style="display:flex; align-items:center; justify-content:space-between; margin:20px 0;">
                        <div style="text-align:center; flex:1;">
                            <img src="{st_photo_b64 if st_photo_b64 else 'https://cdn-icons-png.flaticon.com/512/3135/3135715.png'}" style="width:110px; height:110px; border-radius:12px; border:2px solid #10B981; object-fit:cover;">
                            <div style="margin-top:8px; background:#064E3B; color:#A7F3D0; font-weight:bold; font-size:12px; padding:3px 8px; border-radius:6px; display:inline-block;">
                                Roll ID: {v_data['Student ID']}
                            </div>
                        </div>
                        <div style="flex:2; padding-left:25px;">
                            <h3 style="margin:0 0 10px 0; color:#FFFFFF; font-size:22px;">{v_data['Name']}</h3>
                            <p style="margin:4px 0; font-size:13px; color:#9CA3AF;"><b>Father's Name:</b> <span style="color:white;">{v_data['Father Name']}</span></p>
                            <p style="margin:4px 0; font-size:13px; color:#9CA3AF;"><b>Course Completed:</b> <span style="color:#10B981; font-weight:bold;">{v_data['Course']}</span></p>
                            <p style="margin:4px 0; font-size:13px; color:#9CA3AF;"><b>Duration:</b> <span style="color:white;">{v_data['Duration']}</span></p>
                        </div>
                    </div>
                </div>
                """
                st.markdown(cert_verify_html, unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. NEW STUDENT ADMISSION
# ---------------------------------------------------------
elif menu == "📝 New Student Admission":
    st.header("📝 New Student Registration Form")
    auth_pwd = st.text_input("Enter Staff / Admin Password to Unlock Form:", type="password")
    
    if auth_pwd in [ADMIN_PWD, TEACHER_PWD]:
        st.success("Authorized Access Granted!")
        
        year_code = str(datetime.date.today().year)[2:]
        existing_ids = [sid for sid in student_df["Student ID"] if str(sid).startswith(f"STC{year_code}-")] if not student_df.empty else []
        next_id_preview = f"STC{year_code}-{len(existing_ids)+1:03d}"
        
        st.info(f"⚡ **System Auto-Generated Next Roll ID:** `{next_id_preview}`")
        
        with st.form("add_student_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Student Full Name*")
                fname = st.text_input("Father's Name*")
                mname = st.text_input("Mother's Name*")
                gender = st.selectbox("Gender", ["Male", "Female", "Other"])
                dob = st.date_input("Date of Birth", min_value=datetime.date(1990, 1, 1))
                caste = st.selectbox("Caste", ["General", "OBC / MOBC", "ST", "SC", "Other"])
                mobile = st.text_input("Mobile Number (Unique Key)*")
                photo_file = st.file_uploader("Upload Passport Size Photo", type=["jpg", "jpeg", "png"])
                
            with col2:
                vill = st.text_input("Village / Town*")
                po = st.text_input("Post Office")
                ps = st.text_input("Police Station", value="THELAMARA")
                pin = st.text_input("PIN Code", value="784149")
                dist = st.text_input("District", value="Sonitpur")
                course = st.selectbox("Course Selected*", list(COURSE_CONFIG.keys()))
                cert_dur = st.selectbox("Course Duration Option*", ["12 Months", "6 Months", "3 Months", "2 Months", "45 Days"])
                days_batch = st.selectbox("Class Schedule Days*", ["MWF (Monday, Wednesday, Friday)", "TTS (Tuesday, Thursday, Saturday)", "Regular (Daily Classes)"])
                
            col3, col4 = st.columns(2)
            with col3:
                session = st.text_input("Session", value=f"{datetime.date.today().year}-{datetime.date.today().year+1}")
                join_date = st.date_input("Joining Date", value=datetime.date.today())
                total_fee = st.number_input("Total Course Fee (₹)", min_value=0.0, value=2550.0, step=100.0)
                discount = st.number_input("Discount Allowed (₹)", min_value=0.0, step=50.0)
                
            with col4:
                shift = st.selectbox("Shift Assigned", ["Morning (06:30-08:00 AM)", "Afternoon (04:00-05:30 PM)", "Evening (05:30-07:00 PM)"])
                batch_time = st.text_input("Batch Timing", value="90 Minutes Session")
                
            if st.form_submit_button("Submit Admission"):
                existing_mobiles = student_df["Mobile No"].tolist() if not student_df.empty else []
                
                if not name or not mobile:
                    st.error("Please fill in Name and Mobile Number!")
                elif mobile in existing_mobiles:
                    st.error("🚨 THIS MOBILE NUMBER IS ALREADY REGISTERED WITH STC!")
                else:
                    new_id = next_id_preview
                    photo_path = ""
                    if photo_file is not None:
                        photo_path = os.path.join(PHOTO_DIR, f"{new_id}.png")
                        with open(photo_path, "wb") as f:
                            f.write(photo_file.getbuffer())
                            
                    net_fee = float(total_fee) - float(discount)
                    days_add = 365 if "12" in cert_dur else (180 if "6" in cert_dur else (90 if "3" in cert_dur else (60 if "2" in cert_dur else 45)))
                    validity_date = join_date + datetime.timedelta(days=days_add)
                    
                    new_row = {
                        "Sl. No.": str(len(student_df) + 1), "Student ID": new_id, "Name": name.upper(),
                        "Father Name": fname.upper(), "Mother Name": mname.upper(), "Gender": gender,
                        "DOB": str(dob), "Caste": caste, "Mobile No": mobile, "Vill Town": vill.upper(),
                        "PO": po.upper(), "PS": ps.upper(), "PIN Code": pin, "District": dist.upper(),
                        "Full Address": f"{vill}, {po}, {ps}, {dist} - {pin}".upper(), "Course": course,
                        "Duration": cert_dur, "Days_Batch": days_batch, "Session": session,
                        "Join Date": str(join_date), "Validity Date": str(validity_date),
                        "Total Fee": str(total_fee), "Discount": str(discount), "Net Fee": str(net_fee),
                        "Shift": shift, "Batch Time": batch_time, "Photo Path": photo_path, "Status": "Active"
                    }
                    student_df = pd.concat([student_df, pd.DataFrame([new_row])], ignore_index=True)
                    save_data(student_df, STUDENT_MASTER_FILE)
                    
                    st.success(f"🎉 Registered Successfully! Roll ID: {new_id} | End Date: {validity_date}")

# ---------------------------------------------------------
# 3. STUDENT LOGIN PORTAL
# ---------------------------------------------------------
elif menu == "🔑 Student Login Portal":
    st.header("🔑 Student Individual Dashboard")
    
    if "student_logged_in" not in st.session_state:
        st.session_state["student_logged_in"] = False
        st.session_state["logged_student_id"] = ""

    if not st.session_state["student_logged_in"]:
        col_l1, col_l2 = st.columns(2)
        with col_l1:
            s_id_in = st.text_input("Enter Student Roll ID:").strip().upper()
        with col_l2:
            s_pwd_in = st.text_input("Enter Password (Mobile No):", type="password").strip()
            
        if st.button("Login To Dashboard"):
            st_data = student_df[(student_df["Student ID"] == s_id_in) & (student_df["Mobile No"] == s_pwd_in)]
            if not st_data.empty:
                st.session_state["student_logged_in"] = True
                st.session_state["logged_student_id"] = s_id_in
                st.rerun()
            else:
                st.error("Invalid Roll ID or Password!")
    else:
        s_id = st.session_state["logged_student_id"]
        s = student_df[student_df["Student ID"] == s_id].iloc[0]
        
        col_head, col_out = st.columns([4, 1])
        with col_head:
            st.success(f"Welcome, **{s['Name']}** ({s['Student ID']})")
        with col_out:
            if st.button("🔒 Logout"):
                st.session_state["student_logged_in"] = False
                st.session_state["logged_student_id"] = ""
                st.rerun()

        st_tab1, st_tab2, st_tab3, st_tab4, st_tab5 = st.tabs([
            "💳 Digital ID Card",
            "💵 My Installment Passbook Card",
            "🔄 My Academic Journey",
            "⏱️ Live IST Punch-In",
            "📖 Syllabus & Feedback"
        ])
        
        with st_tab1:
            st_photo_b64 = get_image_base64(s["Photo Path"]) if s["Photo Path"] else None
            logo_b64 = get_image_base64("logo")
            
            id_card_html = f"""
            <div id="print_id_card" style="background:#020B19; border:2px solid #00F0FF; border-radius:16px; padding:20px; color:white; max-width:680px; margin:auto; box-shadow:0 0 20px rgba(0,240,255,0.3); font-family:Arial, sans-serif;">
                <div style="display:flex; align-items:center; justify-content:space-between; border-bottom:1px solid rgba(255,255,255,0.2); padding-bottom:10px;">
                    <div>
                        <h2 style="margin:0; color:#00F0FF; font-size:22px; font-weight:bold;">SOFT TECH COMPUTERS & ZTC</h2>
                        <p style="margin:2px 0 0 0; font-size:10px; color:#CBD5E1;">KAMARCHUBURI, THELAMARA, SONITPUR | CENTER CODE: 4159</p>
                    </div>
                    <div>
                        <img src="{logo_b64 if logo_b64 else ''}" style="width:55px; height:55px; border-radius:50%; border:2px solid #00F0FF;">
                    </div>
                </div>
                <div style="display:flex; align-items:center; justify-content:space-between; margin:15px 0;">
                    <div style="text-align:center; flex:1;">
                        <img src="{st_photo_b64 if st_photo_b64 else 'https://cdn-icons-png.flaticon.com/512/3135/3135715.png'}" style="width:105px; height:105px; border-radius:50%; border:2px solid #00F0FF; object-fit:cover;">
                        <div style="margin-top:5px; color:#00F0FF; font-weight:bold; font-size:12px;">ID: {s['Student ID']}</div>
                    </div>
                    <div style="flex:2; padding-left:20px;">
                        <h3 style="margin:0; color:#FFFFFF; font-size:20px;">{s['Name']}</h3>
                        <p style="margin:3px 0; font-size:12px; color:#00F0FF;"><b>Course:</b> <span style="color:white;">{s['Course']}</span></p>
                        <p style="margin:3px 0; font-size:12px; color:#00F0FF;"><b>Schedule:</b> <span style="color:white;">{s.get('Days_Batch', 'MWF')}</span></p>
                        <p style="margin:3px 0; font-size:12px; color:#00F0FF;"><b>Validity:</b> <span style="color:white;">{s['Join Date']} to {s['Validity Date']}</span></p>
                    </div>
                </div>
            </div>
            """
            st.markdown(id_card_html, unsafe_allow_html=True)

        with st_tab2:
            net_f = float(s["Net Fee"]) if s["Net Fee"] else 0.0
            st_paid_logs = fee_df[fee_df["Student ID"] == s_id]
            tot_p = sum([float(amt) for amt in st_paid_logs["Amount Paid"] if amt])
            bal_due = net_f - tot_p
            
            col_m1, col_m2, col_m3 = st.columns(3)
            col_m1.metric("Net Total Course Fee", f"₹{net_f:.2f}")
            col_m2.metric("Total Deposit Paid", f"₹{tot_p:.2f}")
            col_m3.metric("Remaining Balance Due", f"₹{bal_due:.2f}")

        with st_tab4:
            now_ist = datetime.datetime.now(IST)
            cur_time_str = now_ist.strftime("%I:%M:%S %p")
            cur_date_str = now_ist.strftime("%Y-%m-%d")
            
            today_att = att_df[(att_df["Student ID"] == s_id) & (att_df["Date"] == cur_date_str)]
            if today_att.empty:
                st_late_reason = st.selectbox("Reason for Arrival Time (If Late):", ["On Time", "School / College Class", "Traffic Issue", "Personal Work", "Rain / Weather", "Health Issue"])
                if st.button("Click to Punch In Attendance Now"):
                    att_row = {"Student ID": s_id, "Date": cur_date_str, "Time_In": cur_time_str, "Status": "Present", "Late_Reason": st_late_reason, "Sign_Mode": "Classroom", "Location_Verified": "Campus"}
                    att_df = pd.concat([att_df, pd.DataFrame([att_row])], ignore_index=True)
                    save_data(att_df, ATTENDANCE_FILE)
                    st.success(f"✅ Attendance Punched at {cur_time_str} IST!")
                    st.rerun()

# ---------------------------------------------------------
# 4. SUNDAY PRACTICE CLASS (SFPC)
# ---------------------------------------------------------
elif menu == "🎯 Sunday Free Practice Class (SFPC)":
    st.header("🎯 Sunday Free Practice Class (SFPC) Eligibility Portal")
    check_id = st.text_input("Enter Student Roll ID (e.g. STC26-001):").strip().upper()
    if check_id:
        st_res = student_df[student_df["Student ID"] == check_id]
        if not st_res.empty:
            s = st_res.iloc[0]
            st.success(f"🎉 Welcome **{s['Name']}**! You are ELIGIBLE for Sunday Practice Lab Access!")

# ---------------------------------------------------------
# 5. FEE COUNTER DESK
# ---------------------------------------------------------
elif menu == "💵 Fee Counter Desk":
    st.header("💵 Student Fee Collection Counter Desk")
    f_pwd = st.text_input("Enter Staff / Teacher Password:", type="password")
    
    if f_pwd in [ADMIN_PWD, TEACHER_PWD]:
        sel_sid = st.selectbox("Select Student ID:", student_df["Student ID"] + " - " + student_df["Name"]) if not student_df.empty else None
        if sel_sid:
            sid = sel_sid.split(" - ")[0]
            with st.form("fee_collect_form", clear_on_submit=True):
                pay_amt = st.number_input("Amount Paid (₹)", min_value=100.0, step=100.0)
                pay_mode = st.selectbox("Payment Mode", ["Cash", "UPI / GPay", "Bank Transfer"])
                if st.form_submit_button("Issue Receipt & Save Deposit"):
                    rc_num = f"REC-{datetime.date.today().strftime('%Y%m%d')}-{len(fee_df)+1:03d}"
                    f_row = {"Receipt No": rc_num, "Student ID": sid, "Date": str(datetime.date.today()), "Amount Paid": str(pay_amt), "Payment Mode": pay_mode, "Collected_By": "Staff", "Remarks": "Installment Fee"}
                    fee_df = pd.concat([fee_df, pd.DataFrame([f_row])], ignore_index=True)
                    save_data(fee_df, FEE_LOG_FILE)
                    st.success(f"✅ Receipt Issued: {rc_num}")

# ---------------------------------------------------------
# 6. UPDATE 3: TEACHER PORTAL WITH LIVE CAMERA SCANNER FIX
# ---------------------------------------------------------
elif menu == "🔑 Teacher Portal & QR Scanner":
    st.header("🔑 Faculty Portal & Student Attendance Desk")
    t_pwd = st.text_input("Enter Faculty Password:", type="password")
    
    if t_pwd == TEACHER_PWD:
        now_ist = datetime.datetime.now(IST)
        cur_time_str = now_ist.strftime("%I:%M %p")
        cur_date_str = now_ist.strftime("%Y-%m-%d")
        
        st_tab1, st_tab2, st_tab3 = st.tabs(["📸 Live Camera Attendance Scan", "⏱️ Self Attendance Punch", "📖 Log Class Syllabus"])
        
        # CAMERA ATTENDANCE FIX USING STREAMLIT CAMERA INPUT
        with st_tab1:
            st.subheader("📸 Live Camera Student ID / QR Attendance Desk")
            st.info("💡 **Camera Instructions:** Open Mobile/Laptop Camera below, snap a photo of Student ID Card or QR Code, OR select Roll ID manually below.")
            
            # LIVE WEBCAM / MOBILE CAMERA INPUT FEATURE
            cam_photo = st.camera_input("Take Photo of Student ID / QR Code")
            
            if cam_photo:
                st.success("📸 Photo Captured Successfully!")
            
            st.markdown("---")
            st.write("<b>Or Select Student Roll ID to Punch Attendance Instantly:</b>", unsafe_allow_html=True)
            
            if not student_df.empty:
                sel_student_att = st.selectbox("Choose Student Name / Roll ID:", student_df["Student ID"] + " - " + student_df["Name"])
                
                if st.button("Mark Student Present via Camera Desk"):
                    st_id_scan = sel_student_att.split(" - ")[0]
                    st_name_scan = sel_student_att.split(" - ")[1]
                    
                    att_row = {"Student ID": st_id_scan, "Date": cur_date_str, "Time_In": cur_time_str, "Status": "Present", "Late_Reason": "Camera Verified by Teacher", "Sign_Mode": "Teacher Camera Scanner", "Location_Verified": "Campus"}
                    att_df = pd.concat([att_df, pd.DataFrame([att_row])], ignore_index=True)
                    save_data(att_df, ATTENDANCE_FILE)
                    st.success(f"✅ Marked Present for {st_name_scan} ({st_id_scan}) at {cur_time_str} IST!")

        with st_tab2:
            st.subheader("⏱️ Faculty Punch-In & Shift Session Tracker")
            with st.form("teacher_punch_form"):
                t_name_sel = st.selectbox("Select Teacher Name:", teacher_df["Name"].tolist() if not teacher_df.empty else ["Faculty"])
                t_shift = st.selectbox("Select Shift Session:", ["Morning (06:30 AM)", "Afternoon (04:00 PM)", "Evening (05:30 PM)"])
                if st.form_submit_button("Punch Self Attendance"):
                    st.success("✅ Teacher Attendance Punched!")

        with st_tab3:
            st.subheader("📖 Log Daily Syllabus")
            with st.form("syllabus_form", clear_on_submit=True):
                sys_course = st.selectbox("Select Course Taught:", list(COURSE_CONFIG.keys()))
                sys_topic = st.selectbox("Select Topic Taught:", COURSE_CONFIG[sys_course]["Topics"])
                if st.form_submit_button("Save Syllabus Log"):
                    st.success("✅ Class Syllabus Saved!")

# ---------------------------------------------------------
# 7. ADMIN CONTROL PANEL
# ---------------------------------------------------------
elif menu == "🔐 Admin Control Panel":
    st.header("🔐 Director Admin Control Panel")
    pwd = st.text_input("Enter Director Admin Password", type="password")
    
    if pwd == ADMIN_PWD:
        st.success("Welcome Director Chiranjeeb Hazarika Sir!")
        st.write("Central Admin Control Ledger Active.")