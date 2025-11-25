import streamlit as st
import pandas as pd
import sqlite3
from streamlit_extras.switch_page_button import switch_page

# =====================================================
# KONEKSI DATABASE
# =====================================================
conn = sqlite3.connect("akuntansi.db", check_same_thread=False)

# =====================================================
# CEK LOGIN
# =====================================================
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("⚠️ Silahkan login terlebih dahulu.")
    switch_page("login")
    st.stop()

if st.button("⬅️ Kembali ke Dashboard"):
    switch_page("dashboard")

st.title("💸 Jurnal Pengeluaran Kas")

# =====================================================
# AMBIL TRANSAKSI KAS (KREDIT)
# =====================================================
df = pd.read_sql_query("""
    SELECT * FROM jurnal_umum
    WHERE keterangan LIKE '%Kas%' AND kredit > 0
    ORDER BY tanggal ASC, id ASC
""", conn)

if df.empty:
    st.info("Belum ada transaksi Kas (kredit) yang tercatat di Jurnal Umum.")
    st.stop()

data_jpk = []

# =====================================================
# LOOP CARI PASANGAN DEBIT
# =====================================================
for idx, row in df.iterrows():
    tanggal = row["tanggal"]
    kredit_val = row["kredit"]
    kas_id = row["id"]

    # cari baris sebelum kas (akun lawan)
    pasangan = pd.read_sql_query("""
        SELECT * FROM jurnal_umum
        WHERE tanggal = ?
        AND id < ?
        ORDER BY id DESC
        LIMIT 1
    """, conn, params=(tanggal, kas_id))

    if not pasangan.empty:
        debit_akun = pasangan.iloc[0]["keterangan"].strip()
        debit_val = pasangan.iloc[0]["debit"]
    else:
        debit_akun = "(Akun Debit Tidak Ditemukan)"
        debit_val = kredit_val  # sebagai fallback

    data_jpk.append({
        "tanggal": tanggal,
        "Debit akun": debit_akun,
        "debit": debit_val,
        "Kredit akun": "Kas",
        "kredit": kredit_val
    })

df_jpk = pd.DataFrame(data_jpk)

# =====================================================
# FUNGSI PARSE RUPIAH (JIKA STRING)
# =====================================================
def parse_rp_string(s):
    if pd.isna(s):
        return None
    if isinstance(s, (int, float)):
        return s
    t = str(s).lower().replace("rp", "").replace(".", "").replace(",", "").strip()
    try:
        return float(t)
    except:
        return None


# ============================
# CEK KELENGKAPAN KOLOM
# ============================
# jika kolom debit belum ada -> buat dengan default 0
if "debit" not in df_jpk.columns:
    df_jpk["debit"] = 0

if "kredit" not in df_jpk.columns:
    df_jpk["kredit"] = 0

# ============================
# KONVERSI ANGKA
# ============================
def rupiah(x):
    if x is None or pd.isna(x) or x == 0:
        return ""
    return f"Rp {int(x):,}".replace(",", ".")

df_jpk["debit"] = df_jpk["debit"].astype(float)
df_jpk["kredit"] = df_jpk["kredit"].astype(float)

df_jpk["debit"] = df_jpk["debit"].apply(rupiah)
df_jpk["kredit"] = df_jpk["kredit"].apply(rupiah)


# =====================================================
# TAMPILKAN
# =====================================================
st.subheader("📄 Daftar Jurnal Pengeluaran Kas")
st.dataframe(df_jpk, use_container_width=True, hide_index=True)
