import streamlit as st

from utils import hide_streamlit_style, brand_green

# ==========================================
# 0. ตั้งค่าหน้าและซ่อนเมนู
# ==========================================
st.set_page_config(page_title="ระบบจัดการ รพ.โฮม", page_icon="🏥", layout="wide")
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ==========================================
# 1. หน้า Home / ต้อนรับ
# ==========================================
st.title("🏥 ระบบให้บริการ รพ.โฮม ฉะเชิงเทรา")
st.markdown(
    f"<p style='color:{brand_green}; font-size:18px;'>"
    "ยินดีต้อนรับ — กรุณาเลือกเมนูที่ต้องการใช้งาน</p>",
    unsafe_allow_html=True
)

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🏥 บัตรนัดหมาย")
    st.write("กรอกชื่อและ HN ของคนไข้เอง พร้อมระบบคำนวณวันนัดล่วงหน้าอัตโนมัติ และพรีวิวสำหรับปริ้นบัตรนัด")
    st.page_link("pages/2_🏥_บัตรนัดหมาย.py", label="➡️ ไปที่หน้าบัตรนัดหมาย", use_container_width=True)

with col2:
    st.markdown("### 🧾 ใบเสร็จรับเงิน")
    st.write("อัปโหลดไฟล์ Excel เพื่อดึงข้อมูลอัตโนมัติ จากนั้นออกใบเสร็จเป็นไฟล์ Excel หรือพรีวิวสำหรับปริ้น")
    st.page_link("pages/1_🧾_ใบเสร็จรับเงิน.py", label="➡️ ไปที่หน้าใบเสร็จรับเงิน", use_container_width=True)


st.divider()
st.caption("โรงพยาบาลโฮม ฉะเชิงเทรา | โทร 038-511-123")