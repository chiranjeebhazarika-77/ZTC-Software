import streamlit as st
import pandas as pd
import requests
import json
import threading
import os

GSHEET_WEBAPP_URL = "https://script.google.com/macros/s/AKfycbyeLkWRqD_gHSIQzFBUEJ2kv1e6DpbaUkBB9_CV5l_95k8kg-tSyBnCC50W1TN0XwES/exec"

def push_to_cloud(sheet_name, df):
    def _worker():
        try:
            records = [df.columns.tolist()] + df.fillna("").values.tolist()
            payload = {"action": "overwrite", "sheet_name": sheet_name, "rows": records}
            requests.post(GSHEET_WEBAPP_URL, data=json.dumps(payload), headers={"Content-Type": "application/json"}, timeout=8)
        except Exception:
            pass
    t = threading.Thread(target=_worker)
    t.daemon = True
    t.start()

@st.cache_data(ttl=5, show_spinner=False)
def fetch_cloud(sheet_name):
    try:
        res = requests.get(f"{GSHEET_WEBAPP_URL}?sheet_name={sheet_name}", timeout=4)
        if res.status_code == 200:
            data = res.json()
            if isinstance(data, list) and len(data) > 1:
                return pd.DataFrame(data[1:], columns=data[0], dtype=str)
    except Exception:
        pass
    return None

def get_table(file_name, sheet_name, columns):
    df = fetch_cloud(sheet_name)
    if df is not None:
        for c in columns:
            if c not in df.columns: df[c] = ""
        df = df[columns].fillna("")
        df.to_csv(file_name, index=False)
        return df
        
    if os.path.exists(file_name):
        try:
            df_local = pd.read_csv(file_name, dtype=str)
            for c in columns:
                if c not in df_local.columns: df_local[c] = ""
            return df_local[columns].fillna("")
        except Exception:
            pass
            
    return pd.DataFrame(columns=columns)

def update_table(file_name, sheet_name, df):
    df.to_csv(file_name, index=False)
    st.cache_data.clear()
    push_to_cloud(sheet_name, df)
