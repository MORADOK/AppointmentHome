import streamlit as st
from pathlib import Path

from utils import hide_streamlit_style

# ==========================================
# 0. ตั้งค่าหน้าและซ่อนเมนู (เรียก set_page_config ที่เดียวตรงนี้เท่านั้น)
# ==========================================
st.set_page_config(page_title="ระบบจัดการ รพ.โฮม", page_icon="🏥", layout="wide")
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# โฟลเดอร์ที่ไฟล์ app.py นี้อยู่ (ใช้สร้าง path แบบเต็ม กัน path หาไฟล์ไม่เจอ)
BASE_DIR = Path(__file__).parent

# ==========================================
# 1. กำหนดหน้าและเมนูนำทาง (แสดงที่แถบด้านบน ไม่ใช้ sidebar)
# ==========================================
receipt_page = st.Page(
    BASE_DIR / "views" / "receipt.py",
    title="ใบเสร็จรับเงิน",
    icon="🧾",
    url_path="receipt",
    default=True,          # หน้าแรกที่เปิดขึ้นมา
)

appointment_page = st.Page(
    BASE_DIR / "views" / "appointment.py",
    title="บัตรนัดหมาย",
    icon="🏥",
    url_path="appointment",
)

# position="top" = เมนูอยู่แถบบน (เลี่ยงปัญหา sidebar หาย/เปิดไม่ได้)
pg = st.navigation([receipt_page, appointment_page], position="top")
pg.run()
