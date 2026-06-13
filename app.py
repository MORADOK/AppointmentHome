import streamlit as st
import openpyxl
from io import BytesIO

# ==========================================
# 1. ฟังก์ชันดึงข้อมูลจากไฟล์ Winclinic
# ==========================================
def extract_winclinic_data(uploaded_file):
    """อ่านไฟล์ Excel ที่ Export จาก Winclinic และดึงชื่อ + CN"""
    wb = openpyxl.load_workbook(uploaded_file, data_only=True)
    sheet = wb.active
    
    # ดึงข้อมูลจากเซลล์ (ลองดึง A4 ก่อน ถ้าว่างให้หาใน B4)
    raw_name = sheet['A4'].value or sheet['B4'].value
    raw_cn = sheet['D4'].value or sheet['C4'].value # ดึงรหัส CN

    # Data Cleaning (ทำความสะอาดข้อมูล)
    patient_name = str(raw_name).strip() if raw_name else "ไม่พบชื่อ"
    
    # จัดการรหัส CN โดยตัดคำว่า "CN:" ออกให้เหลือแต่ตัวเลข
    cn_number = ""
    if raw_cn:
        cn_number = str(raw_cn).replace("CN:", "").replace("cn:", "").strip()

    return patient_name, cn_number

# ==========================================
# 2. ฟังก์ชันสร้างบัตรนัด (ลง Template สีเขียว)
# ==========================================
def generate_appointment_card(template_path, patient_data):
    wb = openpyxl.load_workbook(template_path)
    sheet = wb.active

    # หยอดข้อมูลลง Template
    sheet['B6'] = f"ชื่อ - สกุล : {patient_data['name']}"
    sheet['D6'] = f"HN : {patient_data['hn']}"
    sheet['B10'] = patient_data['appt_date']
    sheet['D10'] = patient_data['appt_time']
    sheet['B12'] = patient_data['doctor']
    sheet['D12'] = patient_data['action']
    sheet['B14'] = patient_data['instruction']

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output

# ==========================================
# 3. หน้าจอ UI (Streamlit)
# ==========================================
st.set_page_config(page_title="ระบบออกบัตรนัดอัตโนมัติ", page_icon="🏥")
st.title("🏥 ระบบออกบัตรนัด (Auto-Fill จาก Winclinic)")

# ขั้นตอนที่ 1: อัปโหลดไฟล์จาก Winclinic
st.header("1. อัปโหลดไฟล์ที่บันทึกจาก Winclinic")
uploaded_winclinic = st.file_uploader("ลากไฟล์ Excel จาก Winclinic มาวางที่นี่", type=["xlsx", "xls"])

if uploaded_winclinic:
    # อ่านข้อมูลอัตโนมัติ
    patient_name, cn_number = extract_winclinic_data(uploaded_winclinic)
    
    st.success("✅ ดึงข้อมูลสำเร็จ!")
    st.info(f"**ชื่อ-สกุล:** {patient_name}  |  **CN/HN:** {cn_number}")

    # ขั้นตอนที่ 2: กรอกข้อมูลการนัดหมาย
    st.header("2. รายละเอียดการนัดหมาย")
    col1, col2 = st.columns(2)
    with col1:
        appt_date = st.text_input("วันที่นัดหมาย", value="12 สิงหาคม 2569")
        appt_time = st.text_input("เวลานัด", value="08.00 - 10.00 น.")
    with col2:
        doctor = st.selectbox("แพทย์ผู้ตรวจ", ["นพ.อภิสิทธิ์ สื่อประเสริฐสิทธิ์", "นพ.ทดสอบ ระบบดี"])
        action = st.text_input("รายการตรวจ", value="เจาะเลือด FBS + Lipid ก่อนพบแพทย์")
    
    instruction = st.text_input("คำแนะนำ", value="งดน้ำ-งดอาหาร 6-8 ชั่วโมงก่อนตรวจ")

    # ขั้นตอนที่ 3: สร้างและดาวน์โหลด
    st.header("3. สร้างบัตรนัด")
    if st.button("🖨️ สร้างไฟล์บัตรนัด Excel", type="primary"):
        data_to_fill = {
            "name": patient_name,
            "hn": cn_number,
            "appt_date": appt_date,
            "appt_time": appt_time,
            "doctor": doctor,
            "action": action,
            "instruction": instruction
        }
        
        try:
            # ต้องเตรียมไฟล์ Template บัตรนัดสีเขียวไว้ชื่อ "Template.xlsx"
            excel_file = generate_appointment_card("Template.xlsx", data_to_fill)
            
            st.balloons()
            st.download_button(
                label="📥 ดาวน์โหลดไฟล์บัตรนัดพร้อมปริ้น",
                data=excel_file,
                file_name=f"Appointment_{cn_number}_{patient_name}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except FileNotFoundError:
            st.error("❌ ไม่พบไฟล์แม่แบบ 'Template.xlsx' ในโฟลเดอร์ กรุณาตรวจสอบ")
