import streamlit as st
import pandas as pd
import sqlite3
from streamlit_extras.switch_page_button import switch_page

# =====================================================
# KONEKSI DATABASE
# =====================================================
conn = sqlite3.connect("akuntansi.db", check_same_thread=False)

# Cek login
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("⚠️ Silahkan login terlebih dahulu.")
    switch_page("login")
    st.stop()

if st.button("⬅️ Kembali ke Dashboard"):
    switch_page("dashboard")

st.title("📗 Buku Besar")

# =====================================================
# AMBIL DATA JURNAL
# =====================================================
df = pd.read_sql_query("SELECT * FROM jurnal_umum ORDER BY id ASC", conn)

if df.empty:
    st.info("Belum ada transaksi di jurnal umum.")
    st.stop()

# =====================================================
# DAFTAR AKUN OTOMATIS
# =====================================================
def bersihkan_akun(text):
    return text.strip()

df["akun"] = df["keterangan"].apply(bersihkan_akun)
akun_list = sorted(df["akun"].unique())

# =====================================================
# SALDO NORMAL AKUN
# =====================================================
saldo_normal = {
    # ASET
    "Kas": "debit",
    "Persediaan Pakan": "debit",
    "Persediaan Barang Dagang": "debit",
    "Perlengkapan": "debit",
    "Peralatan": "debit",
    "Piutang": "debit",

    # BEBAN
    "Beban listrik": "debit",
    "Beban gaji": "debit",
    "Beban bahan bakar": "debit",

    # HPP
    "HPP": "debit",

    # PENDAPATAN
    "Penjualan": "kredit",

    # MODAL & UTANG (jika nanti dipakai)
    "Modal": "kredit",
    "Utang": "kredit"
}

# =====================================================
# PILIH AKUN
# =====================================================
pilih = st.selectbox("Pilih akun:", ["-- pilih akun --"] + akun_list)

if pilih == "-- pilih akun --":
    st.info("Silakan pilih akun terlebih dahulu.")
    st.stop()

# Filter data untuk akun ini
df_akun = df[df["akun"] == pilih].copy()

# Format angka
df_akun["debit"] = pd.to_numeric(df_akun["debit"], errors="coerce").fillna(0)
df_akun["kredit"] = pd.to_numeric(df_akun["kredit"], errors="coerce").fillna(0)

# =====================================================
# HITUNG SALDO BUKU BESAR
# =====================================================
saldo = 0
saldo_list = []

# cek saldo normal
normal = saldo_normal.get(pilih, "debit")

for _, row in df_akun.iterrows():

    if normal == "debit":  # saldo normal debit
        if row["debit"] > 0:
            saldo += row["debit"]
        else:
            saldo -= row["kredit"]

    else:  # saldo normal kredit
        if row["kredit"] > 0:
            saldo += row["kredit"]
        else:
            saldo -= row["debit"]

    saldo_list.append(saldo)

df_akun["Saldo"] = saldo_list


# =====================================================
# FORMAT RUPIAH
# =====================================================
def rp(x):
    if x == 0:
        return ""
    return f"Rp {x:,.0f}".replace(",", ".")


df_akun["debit"] = df_akun["debit"].apply(rp)
df_akun["kredit"] = df_akun["kredit"].apply(rp)
df_akun["Saldo"] = df_akun["Saldo"].apply(rp)

df_display_no_id = df_akun[["tanggal", "keterangan", "ref", "debit", "kredit", "Saldo"]].copy()

styled_df = df_display_no_id.style.set_properties(
    **{
        'background-color': '#f9ffe8',   # warna isi tabel beda dari background
        'color': '#1a1a1a',
        'border-color': '#5c6d3a',
        'border-style': 'solid',
        'border-width': '1px'
    }
).set_table_styles([
    {
        'selector': 'th',
        'props': [
            ('background-color', '#e3f2c3'),
            ('color', '#1a1a1a'),
            ('font-weight', 'bold'),
            ('border', '1px solid #5c6d3a')
        ]
    }
])
st.subheader(f"📘 Buku Besar – {pilih}")

st.dataframe(
    df_akun[["tanggal", "keterangan", "ref", "debit", "kredit", "Saldo"]],
    use_container_width=True,
    hide_index=True
)

