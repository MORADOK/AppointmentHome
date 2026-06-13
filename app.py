import streamlit as st
import streamlit.components.v1 as components
import openpyxl
from io import BytesIO
import base64

# ==========================================
# 1. ฟังก์ชันแปลงโลโก้เพื่อใช้บนหน้าเว็บ
# ==========================================
def get_base64_image(image_path):
    """แปลงไฟล์รูปภาพเป็น Base64 เพื่อฝังใน HTML"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    except Exception:
        return "" # หากไม่มีรูปให้ปล่อยว่าง

# ==========================================
# 2. ฟังก์ชันสร้างหน้าเว็บสำหรับสั่งปริ้น (HTML Print)
# ==========================================
def generate_html_print_view(patient_data):
    """สร้างบัตรนัดในรูปแบบ HTML เพื่อให้เบราว์เซอร์สั่งปริ้นได้ตรงๆ"""
    brand_green = "#2C5E3B"
    brand_brown = "#8B5A2B"
    logo_base64 = get_base64_image("logo.png") # ต้องมีไฟล์ logo.png ในโฟลเดอร์เดียวกับโค้ด
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="th">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Tahoma', sans-serif; color: #333; }}
            .card {{ 
                width: 100%; max-width: 600px; margin: 0 auto; 
                border: 1px solid #ddd; padding-bottom: 20px;
            }}
            .header {{ 
                background-color: {brand_green}; color: white; 
                padding: 15px; display: flex; align-items: center; justify-content: center;
            }}
            .logo {{ width: 60px; height: auto; margin-right: 15px; }}
            .title {{ font-size: 18px; font-weight: bold; text-align: center; margin: 0; }}
            .subtitle {{ font-size: 14px; text-align: center; margin: 0; font-weight: normal; }}
            .content {{ padding: 20px; }}
            .row {{ display: flex; justify-content: space-between; margin-bottom: 15px; }}
            .highlight {{ color: {brand_green}; font-size: 18px; font-weight: bold; }}
            .section-title {{ color: {brand_brown}; font-weight: bold; border-bottom: 2px solid {brand_brown}; padding-bottom: 5px; margin-bottom: 15px; }}
            .instruction {{ color: {brand_brown}; font-weight: bold; margin-top: 20px; }}
            .footer {{ text-align: center; font-size: 12px; font-style: italic; margin-top: 20px; color: #666; }}
            
            @media print {{
                .no-print {{ display: none !important; }}
                .card {{ border: none; }}
            }}
            .print-btn {{
                background-color: {brand_green}; color: white; border: none; 
                padding: 10px 20px; font-size: 16px; border-radius: 5px; 
                cursor: pointer; width: 100%; font-weight: bold; margin-bottom: 20px;
            }}
        </style>
    </head>
    <body>
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
                    <div>วันที่นัด : {patient_data['appt_date']}</div>
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
    </body>
    </html>
    """
    return html_content

# ==========================================
# 3. ฟังก์ชันสร้างไฟล์ Excel แม่แบบสำรอง
# ==========================================
def generate_appointment_card(template_path, patient_data):
    wb = openpyxl.load_workbook(template_path)
    sheet = wb.active
    sheet['B6'] = f"ชื่อ - สกุล : {patient_data['name']}"
    sheet['D6'] = f"HN : {patient_data['hn']}"
    sheet['B10'] = f"วันที่นัด : {patient_data['appt_date']}"
    sheet['D10'] = f"เวลา : {patient_data['appt_time']}"
    sheet['B12'] = f"แพทย์ผู้ตรวจ : {patient_data['doctor']}"
    sheet['D12'] = f"รายการตรวจ : {patient_data['action']} ({patient_data['type']})"
    sheet['B14'] = f"📌 คำแนะนำในการปฏิบัติตัว : {patient_data['instruction']}"
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output

# ==========================================
# 4. หน้าจอ UI (Streamlit Frontend)
# ==========================================
st.set_page_config(page_title="ระบบออกบัตรนัด - รพ.โฮม", page_icon="🏥", layout="centered")

st.title("🏥 ระบบออกบัตรนัดหมาย")
st.markdown("**โรงพยาบาลโฮม ฉะเชิงเทรา**")
st.divider()

# --- ส่วนที่ 1: ข้อมูลคนไข้ ---
st.header("1. ข้อมูลคนไข้")
col_name, col_hn = st.columns(2)
with col_name:
    patient_name = st.text_input("👤 ชื่อ-นามสกุล", placeholder="เช่น นาย ธนายุทธ วิทยาประเสริฐ")
with col_hn:
    cn_number = st.text_input("🆔 รหัสคนไข้ (HN / CN)", placeholder="เช่น 0007234")

st.divider()

# --- ส่วนที่ 2: รายละเอียดการนัดหมาย ---
st.header("2. รายละเอียดการนัดหมาย")

# 2.1 ส่วนการเลือกประเภทการนัดหมาย (ออพชั่นใหม่ที่เพิ่มเข้ามา)
appt_type = st.radio("🛠️ ประเภทการนัดหมาย", ["มาติดตามอาการ", "มาเจาะเลือด"], horizontal=True)

# ค่าเริ่มต้นของคำแนะนำและรายการตรวจ
default_instruction = "รับประทานยาและปฏิบัติตัวตามแพทย์สั่ง"
default_action = "ตรวจติดตามอาการทั่วไป"

if appt_type == "มาเจาะเลือด":
    default_action = "เจาะเลือด ตรวจสุขภาพเบื้องหลัง"
    # ถามต่อทันทีว่างดน้ำงดอาหารไหม
    fasting_option = st.selectbox("🥩 ต้องงดน้ำและงดอาหารหรือไม่?", ["ต้องงดน้ำและอาหาร", "ไม่ต้องงดน้ำและอาหาร"])
    
    if fasting_option == "ต้องงดน้ำและอาหาร":
        default_instruction = "งดน้ำ-งดอาหาร 6-8 ชั่วโมงก่อนตรวจ"
        default_action = "เจาะเลือด FBS + Lipid ก่อนพบแพทย์"
    else:
        default_instruction = "ไม่ต้องงดน้ำและอาหาร สามารถรับประทานอาหารมาได้ตามปกติ"
        default_action = "เจาะเลือดทั่วไป (ไม่ต้องงดอาหาร)"

st.write("") # เว้นบรรทัด

# 2.2 ส่วนกรอก วันที่ เวลา แพทย์
col_date, col_time = st.columns(2)
with col_date:
    appt_date = st.text_input("📅 วันที่นัดหมาย", placeholder="เช่น 12 สิงหาคม 2569")
with col_time:
    appt_time = st.text_input("⏰ เวลานัด", placeholder="เช่น 08.00 - 10.00 น.")
    
col_doc, col_act = st.columns(2)
with col_doc:
    doctor = st.selectbox("👨‍⚕️ แพทย์ผู้ตรวจ", ["นพ.อภิสิทธิ์ สื่อประเสริฐสิทธิ์", "ระบุแพทย์ท่านอื่น..."])
    if doctor == "ระบุแพทย์ท่านอื่น...":
        doctor = st.text_input("พิมพ์ชื่อแพทย์ผู้ตรวจ")
with col_act:
    # เปลี่ยนค่า value ตามประเภทงานที่เลือกด้านบนอัตโนมัติ แต่ยังแก้ไขได้
    action = st.text_input("🩺 รายการตรวจ", value=default_action)

# เปลี่ยนค่า value คำแนะนำตามประเภทงานที่เลือกด้านบนอัตโนมัติ แต่ยังแก้ไขได้
instruction = st.text_input("📌 คำแนะนำเพิ่มเติม", value=default_instruction)

st.divider()

# --- ส่วนที่ 3: สร้างและสั่งปริ้นบัตรนัด ---
st.header("3. สร้างและสั่งปริ้นบัตรนัด")

if st.button("✨ สร้างบัตรนัดหมาย", type="primary", use_container_width=True):
    if not patient_name or not cn_number or not appt_date or not appt_time:
        st.warning("⚠️ กรุณากรอก 'ชื่อ-นามสกุล', 'รหัสคนไข้', 'วันที่' และ 'เวลา' ให้ครบถ้วน")
    else:
        # รวบรวมข้อมูลทั้งหมด
        data_to_fill = {
            "name": patient_name.strip(),
            "hn": cn_number.strip(),
            "type": appt_type,
            "appt_date": appt_date.strip(),
            "appt_time": appt_time.strip(),
            "doctor": doctor.strip(),
            "action": action.strip(),
            "instruction": instruction.strip()
        }
        
        st.success("🎉 บัตรนัดถูกสร้างตามเงื่อนไขเรียบร้อย! คุณสามารถกดสั่งปริ้นที่หน้าต่างด้านล่างนี้ได้เลยครับ")
        
        # แสดงหน้าจอ HTML สำหรับสั่งปริ้นโดยตรง
        html_view = generate_html_print_view(data_to_fill)
        components.html(html_view, height=560, scrolling=True)
        
        # ปุ่มสำรองสำหรับดาวน์โหลด Excel
        try:
            excel_file = generate_appointment_card("Template_Modern_With_Logo.xlsx", data_to_fill)
            st.download_button(
                label="📥 ดาวน์โหลดเป็นไฟล์ Excel สำรอง",
                data=excel_file,
                file_name=f"Appointment_{cn_number}_{patient_name}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except FileNotFoundError:
            pass
