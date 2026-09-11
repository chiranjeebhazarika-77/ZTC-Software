import streamlit as st
import pandas as pd
import datetime
import db

st.set_page_config(page_title="Fee Counter Desk", page_icon="💵", layout="wide")

st.markdown("""
<style>
.stApp { background-color: #0B1120; color: #E2E8F0; }
div.stButton > button { background-color: #10B981 !important; color: white !important; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

st.title("💵 Student Fee Counter Desk")

student_cols = ["Student ID", "Name", "Net Fee", "Status"]
fee_cols = ["Receipt No", "Student ID", "Date", "Amount Paid", "Payment Mode", "Collected_By", "Remarks"]

students_df = db.get_table("students_db.csv", "students_db", student_cols)
fees_df = db.get_table("fees_db.csv", "fees_db", fee_cols)

if not students_df.empty:
    student_opts = students_df["Student ID"] + " - " + students_df["Name"]
    sel_s = st.selectbox("Select Student:", student_opts)
    
    if sel_s:
        sid = sel_s.split(" - ")[0]
        s_data = students_df[students_df["Student ID"] == sid].iloc[0]
        p_logs = fees_df[fees_df["Student ID"] == sid]
        
        tot_paid = sum([float(a) for a in p_logs["Amount Paid"] if a])
        net_fee = float(s_data["Net Fee"]) if s_data["Net Fee"] else 0.0
        due = max(0.0, net_fee - tot_paid)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Course Fee", f"₹{net_fee:.2f}")
        c2.metric("Amount Paid", f"₹{tot_paid:.2f}")
        c3.metric("Remaining Due", f"₹{due:.2f}", delta="-Due" if due > 0 else "Cleared", delta_color="inverse")
        
        st.markdown("---")
        with st.form("fee_form", clear_on_submit=True):
            amt = st.number_input("Deposit Amount (₹)*", min_value=100.0, step=100.0)
            mode = st.selectbox("Payment Mode", ["Cash", "UPI / GPay", "Bank Transfer"])
            collector = st.text_input("Collected By", value="Chiranjeeb Hazarika")
            remarks = st.text_input("Remarks", value="Installment Fee")
            
            if st.form_submit_button("🟢 Issue Receipt & Save Deposit"):
                rc_no = f"REC-{datetime.date.today().strftime('%Y%m%d')}-{len(fees_df)+1:03d}"
                new_fee = {
                    "Receipt No": rc_no, "Student ID": sid, "Date": str(datetime.date.today()),
                    "Amount Paid": str(amt), "Payment Mode": mode, "Collected_By": collector, "Remarks": remarks
                }
                fees_df = pd.concat([fees_df, pd.DataFrame([new_fee])], ignore_index=True)
                db.update_table("fees_db.csv", "fees_db", fees_df)
                st.success(f"🧾 Receipt {rc_no} issued! Amount: ₹{amt}")
                st.rerun()
else:
    st.info("No students found. Please add a student first.")
