import streamlit as st
import base64
import pandas as pd

from utils import (
    brand_green,
    brand_brown,
    logo_base64,
    format_thai_date,
)


# ==========================================
# 1. ฟังก์ชันสร้างหน้าเว็บบัตรนัด (HTML)
# ==========================================
def generate_appt_html(data):
    html = f"""<!DOCTYPE html><html lang="th"><head><meta charset="UTF-8"><style>
        * {{ -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }}
        body {{ font-family: 'Tahoma', sans-serif; color: #333; }}
        .card {{ max-width: 720px; margin: 0 auto; border: 1px solid #ddd; padding-bottom: 20px; background-color: white; }}
        .header {{ border-bottom: 2px solid {brand_green}; padding: 15px; display: flex; align-items: center; justify-content: center; margin-bottom: 15px; }}
        .logo {{ width: 60px; margin-right: 15px; }}
        .title {{ font-size: 20px; font-weight: bold; margin: 0; color: {brand_green}; }}
        .subtitle {{ font-size: 14px; margin: 0; color: #555; }}
        .content {{ padding: 0 20px; }}
        .row {{ display: flex; justify-content: space-between; margin-bottom: 10px; }}
        .print-btn {{ background-color: {brand_green}; color: white; border: none; padding: 10px; cursor: pointer; width: 100%; font-size: 16px; margin-bottom: 10px; }}
        @media print {{ .no-print {{ display: none !important; }} .card {{ border: none; }} }}
    </style></head><body>
        <button class="no-print print-btn" onclick="window.print()">🖨️ ปริ้นบัตรนัด</button>
        <div class="card">
            <div class="header"><img src="data:image/png;base64,{logo_base64}" class="logo">
            <div><p class="title">โรงพยาบาลโฮม ฉะเชิงเทรา</p><p class="subtitle">บัตรนัดหมาย | Appointment Card</p></div></div>
            <div class="content">
                <div class="row"><div><b>ชื่อ:</b> {data['name']}</div><div><b>HN:</b> {data['hn']}</div></div>
                <hr>
                <div class="row"><div style="color:{brand_green}; font-weight:bold;">วันที่นัด: {data['appt_date']}</div>
                <div style="color:{brand_green}; font-weight:bold;">เวลา: {data['appt_time']}</div></div>
                <div class="row"><div><b>แพทย์:</b> {data['doctor']}</div></div>
                <div class="row"><div><b>รายการ:</b> {data['action']}</div></div>
                <p style="color:{brand_brown}; font-weight:bold;">📌 คำแนะนำ: <span style="color:#333; font-weight:normal;">{data['instruction']}</span></p>
                <p style="text-align:center; font-size:12px; margin-top:20px;">โทร 038-511-123 (กรุณานำยาเดิมมาด้วยทุกครั้ง)</p>
            </div>
        </div>
    </body></html>"""
    return base64.b64encode(html.encode('utf-8')).decode('utf-8')


# ==========================================
# 2. หน้าจอ UI
# ==========================================
st.title("🏥 ระบบออกบัตรนัดหมาย รพ.โฮม")

# --- ส่วนที่ 1: ป้อนข้อมูลคนไข้เอง ---
st.markdown("### 1️⃣ ข้อมูลคนไข้")
col_p1, col_p2 = st.columns(2)
with col_p1:
    patient_name = st.text_input("👤 ชื่อ-นามสกุลคนไข้", placeholder="เช่น นางสมหญิง ใจดี")
with col_p2:
    hn_number = st.text_input("🆔 รหัสคนไข้ (HN)", placeholder="เช่น 00012345")

st.divider()

# --- ส่วนที่ 2: รายละเอียดนัดหมาย ---
st.markdown("### 2️⃣ รายละเอียดการนัดหมาย")
appt_type = st.radio(
    "ประเภทนัดหมาย",
    ["มาติดตามอาการ", "มาเจาะเลือด", "นัด Ultrasound"],
    horizontal=True,
)

# ค่าเริ่มต้น
default_action = "ตรวจติดตามอาการทั่วไป"
default_instruction = "รับประทานยาและปฏิบัติตัวตามแพทย์สั่ง"

# ตารางชนิด Ultrasound + คำแนะนำการเตรียมตัว (มาตรฐานทั่วไป พนักงานปรับแก้ได้)
US_PREP = {
    "ช่องท้องส่วนบน (ตับ ถุงน้ำดี ตับอ่อน ม้าม)": {
        "action": "Ultrasound Upper Abdomen",
        "instruction": "งดน้ำ-งดอาหาร อย่างน้อย 6-8 ชั่วโมงก่อนตรวจ",
    },
    "ช่องท้องส่วนล่าง / อุ้งเชิงกราน": {
        "action": "Ultrasound Lower Abdomen / Pelvis",
        "instruction": "ดื่มน้ำ 4-6 แก้วก่อนตรวจประมาณ 1 ชั่วโมง และกลั้นปัสสาวะให้กระเพาะปัสสาวะเต็ม",
    },
    "ช่องท้องทั้งหมด (Whole Abdomen)": {
        "action": "Ultrasound Whole Abdomen",
        "instruction": "งดน้ำ-งดอาหาร 6-8 ชั่วโมง และกลั้นปัสสาวะให้กระเพาะปัสสาวะเต็มก่อนตรวจ",
    },
    "ไต / ระบบทางเดินปัสสาวะ (KUB)": {
        "action": "Ultrasound KUB",
        "instruction": "ดื่มน้ำ 4-6 แก้วก่อนตรวจประมาณ 1 ชั่วโมง และกลั้นปัสสาวะให้กระเพาะปัสสาวะเต็ม",
    },
    "ครรภ์ (สูติ-นรีเวช)": {
        "action": "Ultrasound Obstetric",
        "instruction": "ครรภ์อ่อน (อายุครรภ์น้อย): กลั้นปัสสาวะให้กระเพาะปัสสาวะเต็ม | ครรภ์แก่: ไม่ต้องเตรียมตัวพิเศษ",
    },
    "ไทรอยด์ (Thyroid)": {
        "action": "Ultrasound Thyroid",
        "instruction": "ไม่ต้องเตรียมตัวพิเศษ งดสวมสร้อยคอ/เครื่องประดับบริเวณคอ",
    },
    "เต้านม (Breast)": {
        "action": "Ultrasound Breast",
        "instruction": "ไม่ต้องเตรียมตัวพิเศษ งดทาแป้ง/โลชั่นบริเวณเต้านมและรักแร้ในวันตรวจ",
    },
    "หัวใจ (Echo)": {
        "action": "Echocardiogram",
        "instruction": "ไม่ต้องเตรียมตัวพิเศษ รับประทานอาหารและยาได้ตามปกติ",
    },
    "หลอดเลือด (Doppler)": {
        "action": "Doppler Ultrasound",
        "instruction": "ไม่ต้องเตรียมตัวพิเศษ (หากตรวจหลอดเลือดในช่องท้อง อาจต้องงดอาหาร 6 ชั่วโมง)",
    },
}

if appt_type == "มาเจาะเลือด":
    fasting_option = st.selectbox(
        "🥩 ต้องงดน้ำและงดอาหารหรือไม่?",
        ["ต้องงดน้ำและอาหาร", "ไม่ต้องงดน้ำและอาหาร"]
    )
    if fasting_option == "ต้องงดน้ำและอาหาร":
        default_action = "เจาะเลือด FBS + Lipid ก่อนพบแพทย์"
        default_instruction = "งดน้ำ-งดอาหาร 6-8 ชั่วโมงก่อนตรวจ"
    else:
        default_action = "เจาะเลือดทั่วไป (ไม่ต้องงดอาหาร)"
        default_instruction = "ไม่ต้องงดน้ำและอาหาร สามารถรับประทานอาหารมาได้ตามปกติ"

elif appt_type == "นัด Ultrasound":
    us_type = st.selectbox("🩻 ชนิดการตรวจ Ultrasound", list(US_PREP.keys()))
    default_action = f"Ultrasound {us_type}"
    default_instruction = US_PREP[us_type]["instruction"]
    st.info(f"📋 **การเตรียมตัว:** {default_instruction}")
    st.caption("หมายเหตุ: คำแนะนำเป็นมาตรฐานทั่วไป กรุณาตรวจสอบ/ปรับตามแนวทางของโรงพยาบาลและคำสั่งแพทย์")

# --- ส่วนที่ 3: คำนวณวันนัดอัตโนมัติ ---
st.markdown("**📅 ระบบคำนวณวันนัดอัตโนมัติ**")
col_c1, col_c2, col_c3 = st.columns([1, 1, 2])
with col_c1:
    adv_num = st.number_input("จำนวนล่วงหน้า", min_value=0, value=0, step=1,
                              help="ใส่ตัวเลข 0 หากต้องการใช้วันที่ปัจจุบัน")
with col_c2:
    adv_unit = st.selectbox("หน่วย", ["วัน (Days)", "สัปดาห์ (Weeks)", "เดือน (Months)"])

base_date = pd.Timestamp.today()
if adv_num > 0:
    if "วัน" in adv_unit:
        calc_date = base_date + pd.DateOffset(days=adv_num)
    elif "สัปดาห์" in adv_unit:
        calc_date = base_date + pd.DateOffset(weeks=adv_num)
    else:
        calc_date = base_date + pd.DateOffset(months=adv_num)
else:
    calc_date = base_date

with col_c3:
    final_date = st.date_input("🗓️ ปฏิทิน (ระบบคำนวณให้อัตโนมัติ ปรับคลิกแก้ได้)",
                               value=calc_date.date())
    appt_date_thai = format_thai_date(final_date)

col_t1, col_t2 = st.columns(2)
with col_t1:
    appt_date_text = st.text_input("รูปแบบวันที่บนบัตร (แก้ไขข้อความได้)", value=appt_date_thai)
with col_t2:
    time_sel = st.selectbox("เวลานัด",
                            ["08.00 - 10.00 น.", "10.00 - 12.00 น.",
                             "13.00 - 15.00 น.", "15.00 - 16.30 น."])

col_d1, col_d2 = st.columns(2)
with col_d1:
    doc_appt = st.text_input("แพทย์ผู้ตรวจ", value="นพ.อภิสิทธิ์ สื่อประเสริฐสิทธิ์")
with col_d2:
    act_appt = st.text_input("รายการตรวจ", value=default_action)
ins_appt = st.text_input("คำแนะนำ", value=default_instruction)

st.divider()

# --- ส่วนที่ 4: สร้างพรีวิว ---
if st.button("✨ สร้างหน้าพรีวิวสำหรับปริ้นบัตรนัด", type="primary", width='stretch'):
    if not patient_name:
        st.error("⚠️ กรุณากรอกชื่อคนไข้ก่อนครับ")
    else:
        data_appt = {
            "name": patient_name,
            "hn": hn_number,
            "type": appt_type,
            "appt_date": appt_date_text,
            "appt_time": time_sel,
            "doctor": doc_appt,
            "action": act_appt,
            "instruction": ins_appt,
        }
        st.markdown(
            f'<iframe src="data:text/html;base64,{generate_appt_html(data_appt)}" '
            f'width="100%" height="500" style="border:none;"></iframe>',
            unsafe_allow_html=True
        )
