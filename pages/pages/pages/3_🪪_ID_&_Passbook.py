import streamlit as st
import db

st.set_page_config(page_title="ID Card & Passbook", page_icon="🪪", layout="wide")

st.markdown("""
<style>
.stApp { background-color: #0B1120; color: #E2E8F0; }
.id-card-container { width: 350px; background: #FFFFFF; border-radius: 14px; overflow: hidden; border: 2px solid #0284C7; margin: 15px auto; color: #0F172A; }
.id-card-header { background: #0F172A; color: white; padding: 12px; text-align: center; border-bottom: 3px solid #38BDF8; }
.id-card-body { padding: 16px; text-align: center; }
.id-name { font-size: 16px; font-weight: 800; text-transform: uppercase; margin: 6px 0; }
.id-roll { background: #E0F2FE; color: #0369A1; font-weight: 700; font-size: 12px; padding: 2px 10px; border-radius: 10px; display: inline-block; margin-bottom: 8px; }
.passbook-card { background: #FFFFFF; border: 2px solid #334155; border-radius: 8px; padding: 16px; max-width: 700px; margin: 15px auto; color: #0F172A; }
.passbook-table { width: 100%; border-collapse: collapse; font-size: 12px; margin-top: 10px; }
.passbook-table th, .passbook-table td { border: 1px solid #CBD5E1; padding: 6px; text-align: center; }
.passbook-table th { background: #F1F5F9; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

st.title("🪪 Printable ID Card & Passbook Desk")

student_cols = ["Student ID", "Name", "Father Name", "Mobile No", "Course", "Net Fee", "Shift", "Validity Date"]
fee_cols = ["Receipt No", "Student ID", "Date", "Amount Paid", "Payment Mode", "Collected_By"]

students_df = db.get_table("students_db.csv", "students_db", student_cols)
fees_df = db.get_table("fees_db.csv", "fees_db", fee_cols)

if not students_df.empty:
    student_opts = students_df["Student ID"] + " - " + students_df["Name"]
    sel_s = st.selectbox("Select Student to Preview / Print:", student_opts)
    
    if sel_s:
        sid = sel_s.split(" - ")[0]
        s = students_df[students_df["Student ID"] == sid].iloc[0]
        
        doc = st.radio("Choose Document:", ["🪪 Digital Student ID Card", "💳 Fee Installment Passbook"], horizontal=True)
        
        if doc == "🪪 Digital Student ID Card":
            qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data={s['Student ID']}"
            barcode_url = f"https://quickchart.io/barcode?type=code128&text={s['Student ID']}&width=160&height=32"
            
            st.markdown(f"""
            <div class="id-card-container">
                <div class="id-card-header">
                    <div style="font-size:13px; font-weight:800; color:#38BDF8;">SOFT TECH COMPUTERS & ZTC</div>
                    <div style="font-size:9.5px; color:#CBD5E1;">ISO 9001:2015 Certified | Center: 4159</div>
                </div>
                <div class="id-card-body">
                    <img src="https://cdn-icons-png.flaticon.com/512/3135/3135715.png" style="width:80px; height:80px; border-radius:50%; border:2px solid #0284C7;"><br>
                    <div class="id-name">{s['Name']}</div>
                    <div class="id-roll">ID: {s['Student ID']}</div>
                    <table style="width:100%; font-size:11px; text-align:left; line-height:1.5;">
                        <tr><td><b>Course:</b></td><td>{s['Course']}</td></tr>
                        <tr><td><b>Father:</b></td><td>{s['Father Name']}</td></tr>
                        <tr><td><b>Mobile:</b></td><td>{s['Mobile No']}</td></tr>
                        <tr><td><b>Shift:</b></td><td>{s['Shift']}</td></tr>
                    </table>
                    <div style="display:flex; justify-content:space-around; align-items:center; margin-top:10px;">
                        <img src="{qr_url}" style="width:65px; height:65px; border:1px solid #CBD5E1; padding:2px;">
                        <div>
                            <img src="{barcode_url}" style="width:130px;"><br>
                            <span style="font-size:9px; font-weight:bold;">Director Signature</span>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        else:
            p_logs = fees_df[fees_df["Student ID"] == sid]
            tot_paid = sum([float(a) for a in p_logs["Amount Paid"] if a])
            net_fee = float(s["Net Fee"]) if s["Net Fee"] else 0.0
            due = max(0.0, net_fee - tot_paid)
            
            rows = ""
            run_paid = 0.0
            for idx, (_, r) in enumerate(p_logs.iterrows(), 1):
                amt = float(r["Amount Paid"]) if r["Amount Paid"] else 0.0
                run_paid += amt
                rows += f"<tr><td>{idx}</td><td>{r['Date']}</td><td>{r['Receipt No']}</td><td style='color:#059669; font-weight:bold;'>₹{amt:.2f}</td><td style='color:#DC2626;'>₹{max(0.0, net_fee - run_paid):.2f}</td><td>{r['Payment Mode']}</td></tr>"
                
            if not rows:
                rows = "<tr><td colspan='6'>No installment deposits yet.</td></tr>"
                
            st.markdown(f"""
            <div class="passbook-card">
                <div style="text-align:center; border-bottom:2px solid #0284C7; padding-bottom:6px;">
                    <h3 style="margin:0;">SOFT TECH COMPUTERS & ZTC</h3>
                    <span style="font-size:11px; color:#64748B;">Student Fee Installment Passbook</span>
                </div>
                <div style="display:flex; justify-content:space-between; font-size:12px; margin:10px 0; background:#F8FAFC; padding:8px; border-radius:4px;">
                    <div><b>Name:</b> {s['Name']}<br><b>Roll ID:</b> {s['Student ID']}</div>
                    <div style="text-align:right;"><b>Total Fee:</b> ₹{net_fee:.2f}<br><b>Due Balance:</b> <span style="color:#DC2626; font-weight:bold;">₹{due:.2f}</span></div>
                </div>
                <table class="passbook-table">
                    <thead><tr><th>#</th><th>Date</th><th>Receipt No</th><th>Amount</th><th>Due Balance</th><th>Mode</th></tr></thead>
                    <tbody>{rows}</tbody>
                </table>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("No students found.")
