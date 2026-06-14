import streamlit as st

from utils import hide_streamlit_style

# ==========================================
# 0. ตั้งค่าหน้าและซ่อนเมนู (เรียก set_page_config ที่เดียวตรงนี้เท่านั้น)
# ==========================================
st.set_page_config(page_title="ระบบจัดการ รพ.โฮม", page_icon="🏥", layout="wide")
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ==========================================
# 1. กำหนดหน้าและเมนูนำทาง (Sidebar)
# ==========================================
receipt_page = st.Page(
    "views/receipt.py",
    title="ใบเสร็จรับเงิน",
    icon="🧾",
    url_path="receipt",
    default=True,          # หน้าแรกที่เปิดขึ้นมา
)

appointment_page = st.Page(
    "views/appointment.py",
    title="บัตรนัดหมาย",
    icon="🏥",
    url_path="appointment",
)

pg = st.navigation([receipt_page, appointment_page])
pg.run()