import streamlit as st
import openpyxl
from io import BytesIO
import base64
from datetime import datetime

# ==========================================
# 1. ฟังก์ชันแปลงโลโก้เพื่อใช้บนหน้าเว็บ
# ==========================================
def get_base64_image(image_path):
    """แปลงไฟล์รูปภาพเป็น Base64 เพื่อฝังใน HTML"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    except Exception:
        return "" 

# ==========================================
# 2. ฟังก์ชันแปลงวันที่คริสต์ศักราช เป็น วันที่ภาษาไทย
# ==========================================
def format_thai_date(date_obj):
    thai_months = [
        "", "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", 
        "มิถุนายน", "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
    ]
    day = date_obj.day
    month = thai_months[date_obj.month]
    year_buddhist = date_obj.year + 543
    return f"{day} {month} {year_buddhist}"

# ==========================================
# 3. ฟังก์ชันสร้างหน้าเว็บสำหรับสั่งปริ้น (HTML Print View)
# ==========================================
def generate_html_print_view(patient_data):
    brand_green = "#2C5E3B"
    brand_brown = "#8B5A2B"
    logo_base64 = get_base64_image("logo.png") 
    
    html_content = f"""
    <div class="card">
        <button class="no-print print-btn" onclick="window.print()">🖨️ คลิกที่นี่เพื่อสั่งปริ้นบัตรนัด (Print)</button>
        
        <div class="header">
            <img src="data:image/png;base64,{logo_base64}" class="logo" alt="Logo">
            <div>
                <p class="title">โรงพยาบาลโฮม ฉะเชิงเทรา</p>
                <p class="subtitle">บัตรนัดหมาย | Appointment Card</p>
            </div>
        </div>
        
        <div class="content">
            <div class="row">
                <div><b>ชื่อ - สกุล :</b> {patient_data['name']}</div>
                <div><b>HN :</b> {patient_data['hn']}</div>
            </div>
            
            <div class="section-title">🗓️ รายละเอียดการนัดหมาย ({patient_data['type']})</div>
            
            <div class="row highlight">
                <div>วันที่นัด : {patient_data['appt_date_th']}</div>
                <div>เวลา : {patient_data['appt_time']}</div>
            </div>
            
            <div class="row">
                <div><b>แพทย์ผู้ตรวจ :</b> {patient_data['doctor']}</div>
                <div><b>รายการตรวจ :</b> {patient_data['action']}</div>
            </div>
            
            <div class="instruction">
                📌 คำแนะนำในการปฏิบัติตัว: <span style="font-weight: normal; color: #333;">{patient_data['instruction']}</span>
            </div>
            
            <div class="footer">
                📍 หากต้องการเลื่อนนัด/สอบถามข้อมูลเพิ่มเติม โทร 038-511-123<br>
                (กรุณานำยาเดิมมาด้วยทุกครั้ง)
            </div>
        </div>
    </div>

    <style>
        .card {{ 
            width: 100%; max-width: 600px; margin: 0 auto; 
            border: 1px solid #ddd; padding-bottom: 20px;
            font-family: 'Tahoma', sans-serif; color: #333;
            background-color: white;
        }}
        .header {{ 
            background-color: {brand_green}; color: white; 
            padding: 15px; display: flex; align-items: center; justify-content: center;
        }}
        .logo {{ width: 60px; height: auto; margin-right: 15px; }}
        .title {{ font-size: 20px; font-weight: bold; text-align: center; margin: 0; color: #FFFFFF !important; text-shadow: 1px 1px 2px rgba(0,0,0,0.3); }}
        .subtitle {{ font-size: 14px; text-align: center; margin: 0; font-weight: normal; color: #EEEEEE !important; }}
        .content {{ padding: 20px; }}
        .row {{ display: flex; justify-content: space-between; margin-bottom: 15px; }}
        .highlight {{ color: {brand_green}; font-size: 18px; font-weight: bold; }}
        .section-title {{ color: {brand_brown}; font-weight: bold; border-bottom: 2px solid {brand_brown}; padding-bottom: 5px; margin-bottom: 15px; }}
        .instruction {{ color: {brand_brown}; font-weight: bold; margin-top: 20px; }}
        .footer {{ text-align: center; font-size: 12px; font-style: italic; margin-top: 20px; color: #666; }}
        .print-btn {{
            background-color: {brand_green}; color: white; border: none; 
            padding: 10px 20px; font-size: 16px; border-radius: 5px; 
            cursor: pointer; width: 100%; font-weight: bold; margin-bottom: 20px;
        }}
        
        @media print {{
            body * {{
                visibility: hidden;
            }}
            .card, .card * {{
                visibility: visible;
            }}
            .card {{
                position: fixed;
                left: 0;
                top: 0;
                width: 100%;
                border: none !important;
                margin: 0;
                padding: 0;
            }}
            .no-print {{ display: none !important; }}
        }}
    </style>
    """
    return html_content

# ==========================================
# 4. ฟังก์ชันสร้างไฟล์ Excel สำรอง (อัปเดตชื่อไฟล์ Template ผูกมัดตรงนี้)
# ==========================================
def generate_appointment_card(template_path, patient_data):
    wb = openpyxl.load_workbook(template_path)
    sheet = wb.active
    sheet['B6'] = f"ชื่อ - สกุล : {patient_data['name']}"
    sheet['D6'] = f"HN : {patient_data['hn']}"
    sheet['B10'] = f"วันที่นัด : {patient_data['appt_date_th']}"
    sheet['D10'] = f"เวลา : {patient_data['appt_time']}"
    sheet['B12'] = f"แพทย์ผู้ตรวจ : {patient_data['doctor']}"
    sheet['D12'] = f"รายการตรวจ : {patient_data['action']} ({patient_data['type']})"
    sheet['B14'] = f"📌 คำแนะนำในการปฏิบัติตัว : {patient_data['instruction']}"
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output

# ==========================================
# 5. หน้าจอ UI (Streamlit Frontend)
# ==========================================
st.set_page_config(page_title="ระบบออกบัตรนัด - รพ.โฮม", page_icon="🏥", layout="centered")

st.title("🏥 ระบบออกบัตรนัดหมาย")
st.markdown("**โรงพยาบาลโฮม ฉะเชิงเทรา**")
st.divider()

st.header("1. ข้อมูลคนไข้")
col_name, col_hn = st.columns(2)
with col_name:
    patient_name = st.text_input("👤 ชื่อ-นามสกุล", placeholder="ก๊อบปี้ชื่อมาวางที่นี่")
with col_hn:
    cn_number = st.text_input("🆔 รหัสคนไข้ (HN / CN)", placeholder="ก๊อบปี้ HN มาวางที่นี่")

st.divider()

st.header("2. รายละเอียดการนัดหมาย")

appt_type = st.radio("🛠️ ประเภทการนัดหมาย", ["มาติดตามอาการ", "มาเจาะเลือด"], horizontal=True)

default_instruction = "รับประทานยาและปฏิบัติตัวตามแพทย์สั่ง"
default_action = "ตรวจติดตามอาการทั่วไป"

if appt_type == "มาเจาะเลือด":
    default_action = "เจาะเลือด ตรวจสุขภาพเบื้องต้น"
    fasting_option = st.selectbox("🥩 ต้องงดน้ำและงดอาหารหรือไม่?", ["ต้องงดน้ำและอาหาร", "ไม่ต้องงดน้ำและอาหาร"])
    
    if fasting_option == "ต้องงดน้ำและอาหาร":
        default_instruction = "งดน้ำ-งดอาหาร 6-8 ชั่วโมงก่อนตรวจ"
        default_action = "เจาะเลือด FBS + Lipid ก่อนพบแพทย์"
    else:
        default_instruction = "ไม่ต้องงดน้ำและอาหาร สามารถรับประทานอาหารมาได้ตามปกติ"
        default_action = "เจาะเลือดทั่วไป (ไม่ต้องงดอาหาร)"

st.write("") 

col_date, col_time = st.columns(2)
with col_date:
    selected_date = st.date_input("📅 เลือกวันที่นัดหมาย", value=datetime.today())
    appt_date_thai = format_thai_date(selected_date)
    st.caption(f"รูปแบบบนบัตรนัด: `{appt_date_thai}`") 

with col_time:
    time_slots = [
        "08.00 - 10.00 น.",
        "10.00 - 12.00 น.",
        "13.00 - 15.00 น.",
        "15.00 - 16.30 น.",
        "กำหนดเวลาเอง..."
    ]
    selected_time = st.selectbox("⏰ เลือกเวลานัด", time_slots)
    
    if selected_time == "กำหนดเวลาเอง...":
        appt_time = st.text_input("พิมพ์เวลานัดเอง", placeholder="เช่น 09.30 น.")
    else:
        appt_time = selected_time

col_doc, col_act = st.columns(2)
with col_doc:
    doctor = st.selectbox("👨‍⚕️ แพทย์ผู้ตรวจ", ["นพ.อภิสิทธิ์ สื่อประเสริฐสิทธิ์", "ระบุแพทย์ท่านอื่น..."])
    if doctor == "ระบุแพทย์ท่านอื่น...":
        doctor = st.text_input("พิมพ์ชื่อแพทย์ผู้ตรวจ")
with col_act:
    action = st.text_input("🩺 รายการตรวจ", value=default_action)

instruction = st.text_input("📌 คำแนะนำเพิ่มเติม", value=default_instruction)

st.divider()

st.header("3. สร้างและสั่งปริ้นบัตรนัด")

# 🚨 เปลี่ยนชื่อไฟล์ฝั่งโค้ดหลักให้ค้นหาไฟล์ "Template.xlsx" ตรงตามที่คุณกำหนดไว้
TEMPLATE_FILENAME = "Template.xlsx"

if st.button("✨ สร้างบัตรนัดหมาย", type="primary", use_container_width=True):
    if not patient_name or not cn_number:
        st.warning("⚠️ กรุณากรอก 'ชื่อ-นามสกุล' และ 'รหัสคนไข้' ของคนไข้ก่อนครับ")
    elif not appt_time:
        st.warning("⚠️ กรุณาระบุเวลานัดหมาย")
    else:
        data_to_fill = {
            "name": patient_name.strip(),
            "hn": cn_number.strip(),
            "type": appt_type,
            "appt_date_th": appt_date_thai,
            "appt_time": appt_time.strip(),
            "doctor": doctor.strip(),
            "action": action.strip(),
            "instruction": instruction.strip()
        }
        
        st.success("🎉 บัตรนัดพร้อมพิมพ์แล้ว! ตรวจสอบความถูกต้องและสั่งพิมพ์ด้านล่างได้เลย")
        
        html_view = generate_html_print_view(data_to_fill)
        st.markdown(html_view, unsafe_allow_html=True)
        
        try:
            excel_file = generate_appointment_card(TEMPLATE_FILENAME, data_to_fill)
            st.download_button(
                label="📥 ดาวน์โหลดเป็นไฟล์ Excel สำรอง",
                data=excel_file,
                file_name=f"Appointment_{cn_number}_{patient_name}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except FileNotFoundError:
            st.error(f"❌ ไม่สามารถสร้างไฟล์ Excel ได้เนื่องจากไม่พบไฟล์ที่ชื่อ '{TEMPLATE_FILENAME}' บนคลาวด์")
            st.info("💡 วิธีแก้: ตรวจสอบให้แน่ใจว่าได้เปลี่ยนชื่อไฟล์เทมเพลตบน GitHub เป็น Template.xlsx และอยู่ในโฟลเดอร์เดียวกับโค้ดตัวนี้แล้ว")
