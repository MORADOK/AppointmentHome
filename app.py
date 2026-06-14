import streamlit as st
from pathlib import Path

from utils import hide_streamlit_style, brand_green

# ==========================================
# 0. ตั้งค่าหน้าและซ่อนเมนู (เรียก set_page_config ที่เดียวตรงนี้เท่านั้น)
# ==========================================
st.set_page_config(page_title="ระบบจัดการ รพ.โฮม", page_icon="🏥", layout="wide")
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# CSS ตกแต่งปุ่มเมนูให้ดูเป็นแท็บ
st.markdown(
    f"""
    <style>
    [data-testid="stPageLink"] a {{
        border: 1px solid #cfd8d2;
        border-radius: 8px;
        padding: 8px 14px !important;
        background-color: #f7f9f8;
        font-weight: 600;
        transition: all 0.15s ease;
    }}
    /* บังคับสีตัวอักษร/ไอคอนให้เป็นเขียวเข้ม มองเห็นได้ทั้งโหมดสว่างและมืด */
    [data-testid="stPageLink"] a p,
    [data-testid="stPageLink"] a span,
    [data-testid="stPageLink"] a * {{
        color: {brand_green} !important;
    }}
    [data-testid="stPageLink"] a:hover {{
        background-color: {brand_green};
        border-color: {brand_green};
    }}
    [data-testid="stPageLink"] a:hover * {{
        color: white !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# โฟลเดอร์ที่ไฟล์ app.py นี้อยู่ (สร้าง path แบบเต็ม กัน path หาไฟล์ไม่เจอ)
BASE_DIR = Path(__file__).parent

# ==========================================
# 1. กำหนดหน้า
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

# ปิดเมนูเริ่มต้นของ Streamlit (sidebar/top) แล้วสร้างเมนูเองด้านล่าง
nav = st.navigation([receipt_page, appointment_page], position="hidden")

# ==========================================
# 2. เมนูที่สร้างเอง (อยู่ในเนื้อหา จึงไม่หายเหมือน sidebar/header)
# ==========================================
st.markdown(
    f"<h3 style='color:{brand_green}; margin:0 0 0.6rem 0;'>🏥 ระบบให้บริการ รพ.โฮม ฉะเชิงเทรา</h3>",
    unsafe_allow_html=True,
)

col1, col2, _ = st.columns([1.2, 1.2, 4])
with col1:
    st.page_link(receipt_page, label="ใบเสร็จรับเงิน", icon="🧾", width="stretch")
with col2:
    st.page_link(appointment_page, label="บัตรนัดหมาย", icon="🏥", width="stretch")

st.divider()

# ==========================================
# 3. แสดงเนื้อหาของหน้าที่เลือก
# ==========================================
nav.run()
