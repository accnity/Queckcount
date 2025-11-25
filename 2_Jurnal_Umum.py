import streamlit as st
import pandas as pd
import sqlite3
from streamlit_extras.switch_page_button import switch_page

# =====================================================
# KONEKSI DATABASE
# =====================================================
conn = sqlite3.connect("akuntansi.db", check_same_thread=False)
c =conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS jurnal_umum (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tanggal TEXT,
    keterangan TEXT,
    ref TEXT,
    debit REAL,
    kredit REAL
)
""")

conn.commit()

# =====================================================
# CEK LOGIN
# =====================================================
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("⚠️ Silahkan login terlebih dahulu.")
    switch_page("login")
    st.stop()

if st.button("⬅️ Kembali ke Dashboard"):
    switch_page("dashboard")

st.title("📘 Jurnal Umum")

# =====================================================
# LOAD DATA
# =====================================================
df = pd.read_sql_query("SELECT * FROM jurnal_umum ORDER BY id ASC", conn)

df["debit"] = pd.to_numeric(df["debit"], errors="coerce")
df["kredit"] = pd.to_numeric(df["kredit"], errors="coerce")

total_debit = df["debit"].sum()
total_kredit = df["kredit"].sum()

# =====================================================
# FORMAT RUPIAH
# =====================================================
def rupiah(x):
    if x is None or x == 0 or pd.isna(x):
        return ""
    return f"Rp {x:,.0f}".replace(",",".")

# =====================================================
# FORMAT KREDIT MENJOROK
# =====================================================
def format_keterangan(row):
    if row["kredit"] and row["kredit"] > 0:
        return "    " + row["keterangan"]  # indent pakai em-space
    return row["keterangan"]

df_display = df.copy()
df_display["keterangan"] = df_display.apply(format_keterangan, axis=1)

df_display["debit"] = df_display["debit"].apply(rupiah)
df_display["kredit"] = df_display["kredit"].apply(rupiah)

total_row = {
    "tanggal": "",
    "keterangan": "TOTAL",
    "ref": "",
    "debit": rupiah(total_debit),
    "kredit": rupiah(total_kredit),
}
df_display = pd.concat([df_display, pd.DataFrame([total_row])], ignore_index=True)

# =====================================================
# METRIC
# =====================================================
col1, col2 = st.columns(2)
with col1:
    st.metric("Total Debit", rupiah(total_debit))
with col2:
    st.metric("Total Kredit", rupiah(total_kredit))

# =====================================================
# TAMPILKAN TABEL RAPI
# =====================================================
st.subheader("📄 Daftar Transaksi Jurnal Umum")

df_display_no_id = df_display.drop(columns=["id"], errors="ignore")
#st.data_editor(
    #df_display_no_id,
    #use_container_width=True,
    #hide_index=True,
    #disabled=True,
    #column_config={
        #"tanggal": st.column_config.Column("Tanggal", width=110),
        #"keterangan": st.column_config.Column("Keterangan", width=250),
        #"ref": st.column_config.Column("Ref", width=60),
        #"debit": st.column_config.Column("Debit", width=120),
        #"kredit": st.column_config.Column("Kredit", width=120),
    #}
#)
# ============================
# STYLE TABEL BIAR TIDAK NYATU
# ============================
styled_df = df_display_no_id.style.set_properties(
    **{
        'background-color': '#f9ffe8',   # warna tabel beda dari background
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

st.dataframe(
    styled_df,
    use_container_width=True,
    height=380
)


# =====================================================
# FORM TAMBAH TRANSAKSI
# =====================================================
st.divider()
st.subheader("➕ Tambah Transaksi Baru")

with st.form("form_jurnal", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        tanggal = st.date_input("Tanggal transaksi")
        keterangan = st.text_input("Keterangan")
        debit = st.text_input("Debit (isi salah satu)")
    with col2:
        ref = st.text_input("Ref (opsional)")
        kredit = st.text_input("Kredit (isi salah satu)")

    submitted = st.form_submit_button("💾 Simpan Transaksi")

if submitted:
    if not keterangan:
        st.warning("Keterangan wajib diisi!")
        st.stop()
    if debit and kredit:
        st.error("Isi salah satu: debit ATAU kredit.")
        st.stop()
    if not debit and not kredit:
        st.error("Isi minimal salah satu: debit ATAU kredit.")
        st.stop()

    debit_val = int(debit) if debit else 0
    kredit_val = int(kredit) if kredit else 0

    # =====================================================
    # GENERATE REF OTOMATIS JIKA KOSONG
    # =====================================================
    import pandas as pd
    df_temp = pd.read_sql_query("SELECT * FROM jurnal_umum", conn)
    if ref.strip() == "":
        if len(df_temp) == 0:
            ref_final = "1"
        else:
            ref_final = str(int(df_temp["id"].max()) + 1)
    else:
        ref_final = ref

    # =====================================================
    # SIMPAN KE DATABASE
    # =====================================================
    c.execute("""
        INSERT INTO jurnal_umum (tanggal, keterangan, ref, debit, kredit)
        VALUES (?, ?, ?, ?, ?)
    """, (str(tanggal), keterangan, ref_final, debit_val, kredit_val))

    conn.commit()
    st.success("Transaksi berhasil ditambahkan!")
    st.rerun()

# =====================================================
# HAPUS TRANSAKSI
# =====================================================
st.divider()
st.subheader("🗑️ Hapus Transaksi")

if len(df) > 0:
    df_list = df.copy()
    df_list["label"] = df_list.apply(
        lambda row: f"[{row['tanggal']}] {row['keterangan']} — D:{int(row['debit']) if row['debit'] else 0} / K:{int(row['kredit']) if row['kredit'] else 0}",
        axis=1
    )

    selected_id = st.selectbox(
        "Pilih transaksi yang ingin dihapus:",
        options=df_list["id"].tolist(),
        format_func=lambda x: df_list.loc[df_list["id"] == x, "label"].values[0]
    )

    if st.button("Hapus"):
        c.execute("DELETE FROM jurnal_umum WHERE id = ?", (selected_id,))
        conn.commit()
        st.success("Transaksi berhasil dihapus!")
        st.rerun()

else:
    st.info("Belum ada data untuk dihapus")


