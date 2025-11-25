import streamlit as st
import pandas as pd
import sqlite3
from streamlit_extras.switch_page_button import switch_page

conn = sqlite3.connect("akuntansi.db", check_same_thread=False)

# login check (sama seperti milikmu)
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("⚠️ Silahkan login terlebih dahulu.")
    switch_page("login")
    st.stop()

if st.button("⬅️ Kembali ke Dashboard"):
    switch_page("dashboard")

st.title("💰 Jurnal Penerimaan Kas")

# ambil baris yang mengandung kata "kas" dan berada di sisi DEBIT (penerimaan)
df = pd.read_sql_query("""
    SELECT * FROM jurnal_umum
    WHERE lower(keterangan) LIKE '%kas%' AND CAST(debit AS REAL) > 0
    ORDER BY tanggal ASC, id ASC
""", conn)

if df.empty:
    st.info("Belum ada transaksi Kas (debit) yang tercatat di Jurnal Umum.")
    st.stop()

data_jpk = []
for _, row in df.iterrows():
    tanggal = str(row["tanggal"])
    ref = row["ref"]
    debit_val = row["debit"]
    this_id = row["id"]

    # cari pasangan KREDIT (akun lawan) — exclude baris kas itu sendiri
    if ref and str(ref).strip() != "":
        kredit_row = pd.read_sql_query(
            """
            SELECT * FROM jurnal_umum
            WHERE tanggal = ? AND ref = ? AND CAST(kredit AS REAL) > 0 AND id != ?
            """,
            conn,
            params=(tanggal, str(ref), this_id)
        )
    else:
        kredit_row = pd.read_sql_query(
            """
            SELECT * FROM jurnal_umum
            WHERE tanggal = ? AND CAST(kredit AS REAL) > 0 AND lower(keterangan) NOT LIKE '%kas%' AND id != ?
            """,
            conn,
            params=(tanggal, this_id)
        )

    if not kredit_row.empty:
        kredit_akun = kredit_row.iloc[0]["keterangan"].strip()
        kredit_val = kredit_row.iloc[0]["kredit"]
    else:
        kredit_akun = "Penjualan"
        kredit_val = debit_val

    data_jpk.append({
        "tanggal": tanggal,
        "Debit akun": "Kas",
        "debit": debit_val,
        "Kredit akun": kredit_akun,
        "kredit": kredit_val
    })

df_jpk = pd.DataFrame(data_jpk)

def rupiah(x):
    if x is None or pd.isna(x) or x == 0:
        return ""
    return f"Rp {x:,.0f}".replace(",", ".")

df_jpk["debit"] = df_jpk["debit"].apply(rupiah)
df_jpk["kredit"] = df_jpk["kredit"].apply(rupiah)

st.subheader("📄 Daftar Jurnal Penerimaan Kas")
st.dataframe(df_jpk, use_container_width=True, hide_index=True)
