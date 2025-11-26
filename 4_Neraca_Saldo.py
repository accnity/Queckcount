import streamlit as st
import pandas as pd
import sqlite3
import io
import re
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(page_title="Neraca Saldo", page_icon="📊")

# ==========================================================
# KONEKSI DATABASE
# ==========================================================
conn = sqlite3.connect("akuntansi.db", check_same_thread=False)
c = conn.cursor()

@st.cache_data
def load_jurnal():
   return pd.read_sql_query("SELECT * FROM jurnal_umum ORDER BY id ASC", conn)


# ==========================================================
# CEK LOGIN
# ==========================================================
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
  st.warning("⚠️ Silahkan login terlebih dahulu.")
  switch_page("login")
  st.stop()

if st.button ("⬅️ Kembali ke Dashboard"):
  switch_page("dashboard")

st.title("📊 Neraca Saldo")

df = pd.read_sql_query("SELECT * FROM jurnal_umum ORDER BY id ASC", conn)

if df.empty:
    st.info("Belum ada transaksi di jurnal umum.")
    st.stop()

# ==========================================================
# FUNGSI BANTUAN
# ==========================================================
def parse_rupiah(value):
  """Ubah teks seperti 'Rp 1.000.000' jadi angka 1000000"""
  if pd.isna(value) or value == "":
    return 0.0
  if isinstance(value,(int,float)):
    return float(value)
  value = str(value)
  value = re.sub(r"[^0-9,.-]","", value)
  value = value.replace(",", ".")
  try :
    return float(value)
  except:
    return 0.0
  
def format_rp(x):
    """Format angka ke format Rupiah"""
    print(f"format_rp called with {x}")  # Debugging line
    try:
        x = float(x)
    except:
        return x
    return f"Rp {x:,.0f}".replace(",", ".")

  
# ==========================================================
# AMBIL DATA DARI DATABASE
# ==========================================================
df_jurnal_umum = pd.read_sql_query("SELECT * FROM jurnal_umum ORDER BY id ASC", conn)

# Normalisasi data
df_jurnal_umum["debit"] = df_jurnal_umum["debit"].apply(parse_rupiah)
df_jurnal_umum["kredit"] = df_jurnal_umum["kredit"].apply(parse_rupiah)




# ==========================================================
# TRIAL BALANCE
# ==========================================================
df_jurnal_umum["saldo"] = df_jurnal_umum["debit"] - df_jurnal_umum["kredit"]
saldo_df = df_jurnal_umum.groupby("keterangan", as_index=False).agg({"debit": "sum", "kredit": "sum", "saldo": "sum"})

# Menambahkan kolom "ref" dari jurnal umum ke Neraca Saldo
saldo_df["ref"] = df_jurnal_umum.groupby("keterangan")["ref"].first().reset_index(drop=True)

# Mengganti kolom kosong dengan ref dari jurnal umum
saldo_df["keterangan"] = saldo_df["keterangan"] + " (" + saldo_df["ref"] + ")"

# Hanya mengambil kolom yang relevan: keterangan, debit, kredit, saldo, ref
saldo_df = saldo_df[["keterangan", "debit", "kredit", "saldo"]]

# Menampilkan Trial Balance (Neraca Saldo)
st.dataframe(saldo_df.copy(), use_container_width=True)


# ==========================================================
# TAMPILKAN TOTAL DEBIT DAN KREDIT
# ==========================================================
total_debit = df_jurnal_umum["debit"].sum()
total_kredit = df_jurnal_umum["kredit"].sum()

col1, col2 = st.columns(2)
with col1:
    st.metric("Total Debit", format_rp(total_debit))
with col2:
    st.metric("Total Kredit", format_rp(total_kredit))