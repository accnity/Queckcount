import streamlit as st
from streamlit_extras.switch_page_button import switch_page

# ------------------------------------
#   CONFIG
# ------------------------------------
st.set_page_config(
    page_title="Login — Queckcount",
    page_icon="🔐",
    layout="centered",
)


with st.container():
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image("QUECKCOUNT.png", width=250)  



# Akun yang diizinkan
USERS = {
    "admin": "123",
    "putri": "bebek01",   # kalau mau tambah user lain tinggal tambah di sini
}

# ------------------------------------
#   STATE
# ------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ------------------------------------
#   UI ELEGAN (TANPA HTML)
# ------------------------------------
st.title("🔐 Login — Queckcount")
st.caption("Silahkan login menggunakan username & password terlebih dahulu.")

st.write("")
st.write("")

# ------------------------------------
#   FORM LOGIN
# ------------------------------------
with st.form("login_form", clear_on_submit=False):
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    submit = st.form_submit_button("Login")

if submit:
    if username in USERS and USERS[username] == password:
        st.session_state.logged_in = True
        st.session_state.username = username
        st.success("Login berhasil! Mengarahkan ke Dashboard...")
        #switch_page("Dashboard")
        st.markdown("[➡️ Ke Dashboard](Dashboard)")

    else:
        st.error("Username atau password salah.")

# ------------------------------------
#   JIKA SUDAH LOGIN
# ------------------------------------
if st.session_state.logged_in:
    st.success(f"Kamu sudah login sebagai **{st.session_state.username}**")
    if st.button("Ke Dashboard"):
        st.markdown("[➡️ Ke Dashboard](Dashboard)")
        #switch_page("Dashboard")











