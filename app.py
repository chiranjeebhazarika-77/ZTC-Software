import streamlit as st
import db

st.set_page_config(
    page_title="STC-ZTC Enterprise Portal", 
    page_icon="🎓", 
    layout="wide",
    initial_sidebar_state="expanded"  # চাইডবাৰ সদায় মেল খাই থাকিব
)

st.markdown("""
<style>
.stApp { background-color: #0B1120; color: #E2E8F0; font-family: 'Segoe UI', Tahoma, sans-serif; }
.hero-box { background: #0F172A; border: 1px solid #1E293B; border-radius: 14px; padding: 24px; margin-bottom: 20px; }
.hero-tag { background: rgba(249,115,22,0.12); border: 1px solid #FB923C; color: #FB923C; font-size: 11px; font-weight: 700; padding: 4px 12px; border-radius: 20px; display: inline-block; margin-bottom: 10px; }
.hero-title { font-size: 28px; font-weight: 900; color: #FFFFFF; margin: 0 0 8px 0; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero-box">
    <div class="hero-tag">🛡️ GOVT REGD IT ACADEMY • SONITPUR, ASSAM</div>
    <div class="hero-title">Soft Tech Computers & ZTC Enterprise</div>
    <p style="color:#94A3B8; font-size:14px; margin:0;">
        Center Code: <b>4159</b> | ISO 9001:2015 Certified | Sarva India Affiliated IT Academy
    </p>
</div>
""", unsafe_allow_html=True)

student_cols = ["Student ID", "Name", "Course", "Net Fee", "Status"]
students = db.get_table("students_db.csv", "students_db", student_cols)

col1, col2, col3 = st.columns(3)
col1.metric("Enrolled Trainees", f"{len(students)} Active")
col2.metric("Center Code", "4159 (Assam)")
col3.metric("System Engine", "Multi-page Architecture (0-Lag)")

st.info("👈 বাওঁফালৰ চাইডবাৰৰ পৰা **Admission, Fees, ID Card** আদি সকলো মডিউল খুলি কাম কৰিব পাৰা।")
