import streamlit as st
import pandas as pd
from streamlit_extras.switch_page_button import switch_page

if"logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("⚠️ silahkan login terlebih dahulu.")
    st.switch_page("login.py")

st.set_page_config(page_title="Dashboard", layout="centered")

# ====== HEADER SIMPLE ======
st.title("Dashboard")
st.caption("Silakan pilih menu yang tersedia di bawah.")

st.write("") 

# ====== GRID MENU =====
col1, col2 = st.columns(2)

with col1:
    if st.button("📘 Jurnal Umum"):
        switch_page("Jurnal_umum")

    if st.button("📗 Buku Besar"):
        switch_page("Buku_besar")

    if st.button("📙 Neraca Saldo"):
        switch_page("Neraca_saldo")

with col2:
    if st.button("💵 Jurnal Penerimaan Kas"):
        switch_page("Jurnal_Penerimaan_Kas")

    if st.button("💳 Jurnal Pengeluaran Kas"):
        switch_page("Jurnal_Pengeluaran_Kas")

    if st.button("📈 Laporan Laba Rugi"):
        switch_page("Laporan_Laba_Rugi")

st.write("---")

# ====== LOGOUT ======
if st.button("🚪 Logout"):
    st.session_state["logged_in"] = False
    switch_page("login")
























