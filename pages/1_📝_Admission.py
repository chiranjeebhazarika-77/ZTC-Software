import streamlit as st
import pandas as pd
import datetime
import os
import db

st.set_page_config(page_title="Student Admission", page_icon="📝", layout="wide")

st.markdown("""
<style>
.stApp { background-color: #0B1120; color: #E2E8F0; }
div.stButton > button { background-color: #10B981 !important; color: white !important; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

st.title("📝 New Candidate Admission")

student_cols = [
    "Sl. No.", "Student ID", "Name", "Father Name", "Mother Name", "Gender", "DOB", "Mobile No", 
    "Vill Town", "District", "Course", "Duration", "Session", "Join Date", "Validity Date", 
    "Total Fee", "Discount", "Net Fee", "Shift", "Status"
]

students_df = db.get_table("students_db.csv", "students_db", student_cols)

year_code = str(datetime.date.today().year)[2:]
next_id = f"STC{year_code}-{len(students_df)+1:03d}"
st.info(f"⚡ **Auto-Generated Roll ID:** `{next_id}`")

with st.form("adm_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Student Full Name*")
        fname = st.text_input("Father's Name*")
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        dob = st.date_input("Date of Birth", value=datetime.date(2005, 1, 1))
        mobile = st.text_input("Mobile Number (Unique Key)*")
    with col2:
        vill = st.text_input("Village / Town*")
        dist = st.text_input("District", value="Sonitpur")
        course = st.selectbox("Course Selected*", ["DCA (6 Months)", "ADCA (12 Months)", "PGDCA (12 Months)", "DTP (3 Months)", "Tally Prime with GST (3 Months)"])
        shift = st.selectbox("Shift Assigned", ["Morning (06:30-08:00 AM)", "Afternoon (04:00-05:30 PM)", "Evening (05:30-07:00 PM)"])
        fee = st.number_input("Course Fee (₹)", min_value=100.0, value=2550.0, step=50.0)
        
    if st.form_submit_button("🟢 Complete Admission"):
        if not name or not mobile:
            st.error("Please fill Name and Mobile Number!")
        else:
            new_row = {
                "Sl. No.": str(len(students_df)+1), "Student ID": next_id, "Name": name.upper(),
                "Father Name": fname.upper(), "Mother Name": "", "Gender": gender, "DOB": str(dob),
                "Mobile No": mobile, "Vill Town": vill.upper(), "District": dist.upper(),
                "Course": course, "Duration": "Course Duration", "Session": f"{datetime.date.today().year}",
                "Join Date": str(datetime.date.today()), "Validity Date": str(datetime.date.today() + datetime.timedelta(days=180)),
                "Total Fee": str(fee), "Discount": "0", "Net Fee": str(fee), "Shift": shift, "Status": "Active"
            }
            students_df = pd.concat([students_df, pd.DataFrame([new_row])], ignore_index=True)
            db.update_table("students_db.csv", "students_db", students_df)
            st.success(f"🎉 Student {name} registered with Roll ID: {next_id}")
            st.rerun()
