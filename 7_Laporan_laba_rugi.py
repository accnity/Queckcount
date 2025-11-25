import streamlit as st
import pandas as pd
import sqlite3
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(page_title="Laporan Laba Rugi", page_icon= "📈")



if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("⚠️ Silahkan login terlebih dahulu.")
    switch_page("login")
    st.stop()

if st.button("⬅️ Kembali ke Dashboard"):
    switch_page("dashboard")

st.title("📈 Laporan Laba Rugi")

conn = sqlite3.connect("akuntansi.db", check_same_thread=False)
query = "SELECT * FROM jurnal_umum"
jurnal = pd.read_sql_query(query, conn)

if jurnal.empty:
    st.info("Belum ada data transaksi di Jurnal Umum")
    st.stop()

for kol in ["debit", "kredit"]:
    jurnal[kol] = (
        jurnal[kol]
        .astype(str)
        .str.replace("[^0-9,.-]", "", regex=True)
        .replace("", 0)
        .astype(float)
    )

pendapatan = jurnal[jurnal["keterangan"].str.contains("penjualan|pendapatan", case=False, na=False)]
beban = jurnal[jurnal["keterangan"].str.contains("beban|hpp", case=False, na=False)]

total_pendapatan = pendapatan["kredit"].sum() - pendapatan["debit"].sum()
total_beban = beban["debit"].sum()

laba_rugi = total_pendapatan - total_beban

# ===========================
# STYLE TABEL
# ===========================
def style_table(df):
    return (
        df.style.set_properties(
            **{
                "background-color": "#f9ffe8",
                "color": "#1a1a1a",
                "border-color": "#cadda3",
            }
        )
        .set_table_styles(
            [
                {"selector": "th", "props": "background-color: #d4e7b0; color: #000;"}
            ]
        )
    )

st.subheader ("📈 Pendapatan")
if not pendapatan.empty :
    pendapatan_tampil = pendapatan[["keterangan", "kredit"]].copy()
    pendapatan_tampil["kredit"] = pendapatan_tampil["kredit"].apply(lambda x: f"Rp {int(x):,}".replace(",","."))
    st.table(pendapatan_tampil)
else:
    st.write("Tidak ada akun pendapatan.")

st.subheader("📉 Beban")
if not beban.empty:
    beban_tampil = beban[["keterangan", "debit"]].copy()
    beban_tampil["debit"] = beban_tampil["debit"].apply(lambda x: f"Rp {int(x):,}".replace(",","."))
    st.table(beban_tampil)
else:
    st.write("Tidak ada akun beban.")

st.markdown("---")
st.subheader("💰 Laba/Rugi bersih")

if laba_rugi >= 0:
    st.success(f"**LABA**: Rp {int(laba_rugi):,}".replace(",","."))
else:
    st.error(f"**RUGI**: Rp {abs (int(laba_rugi)):,}".replace(",","."))   