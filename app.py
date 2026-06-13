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
    
    # ดึงข้อมูลจากเซลล์ (ลองดึง A4 ก่อน ถ้าว่างให้หาใน B4 ตามรูปแบบของ Winclinic)
    raw_name = sheet['A4'].value or sheet['B4'].value
    raw_cn = sheet['D4'].value or sheet['C4'].value 

    # Data Cleaning (ทำความสะอาดข้อมูล)
    patient_name = str(raw_name).strip() if raw_name else "ไม่พบชื่อ"
    
    # จัดการรหัส CN โดยตัดคำว่า "CN:" ออกให้เหลือแต่ตัวเลข
    cn_number = ""
    if raw_cn:
        cn_number = str(raw_cn).replace("CN:", "").replace("cn:", "").strip()

    return patient_name, cn_number

# ==========================================
# 2. ฟังก์ชันสร้างบัตรนัด (ลง Template Modern)
# ==========================================
def generate_appointment_card(template_path, patient_data):
    """หยอดข้อมูลลงใน Template ดีไซน์ใหม่ที่มีโลโก้ (อัปเดตตำแหน่ง Cell แล้ว)"""
    wb = openpyxl.load_workbook(template_path)
    sheet = wb.active

    # หยอดข้อมูลลง Template ตามตำแหน่งใหม่ (Modern Design)
    sheet['B6'] = f"ชื่อ - สกุล : {patient_data['name']}"
    sheet['D6'] = f"HN : {patient_data['hn']}"
    
    sheet['B10'] = f"วันที่นัด : {patient_data['appt_date']}"
    sheet['D10'] = f"เวลา : {patient_data['appt_time']}"
    
    sheet['B12'] = f"แพทย์ผู้ตรวจ : {patient_data['doctor']}"
    sheet['D12'] = f"รายการตรวจ : {patient_data['action']}"
    
    sheet['B14'] = f"📌 คำแนะนำในการปฏิบัติตัว : {patient_data['instruction']}"

    # บันทึกไฟล์ลงในหน่วยความจำชั่วคราว
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output

# ==========================================
# 3. หน้าจอ UI (Streamlit Frontend)
# ==========================================
st.set_page_config(page_title="ระบบออกบัตรนัด - รพ.โฮม", page_icon="🏥", layout="centered")

# แสดงหัวเว็บ
st.title("🏥 ระบบออกบัตรนัดหมาย")
st.markdown("**โรงพยาบาลโฮม ฉะเชิงเทรา (Auto-Fill จาก Winclinic)**")
st.divider()

# ขั้นตอนที่ 1: อัปโหลดไฟล์จาก Winclinic
st.header("1. ดึงข้อมูลคนไข้")
uploaded_winclinic = st.file_uploader("📂 อัปโหลดไฟล์ Excel ที่ได้จาก Winclinic", type=["xlsx", "xls"])

if uploaded_winclinic:
    # อ่านข้อมูลอัตโนมัติ
    try:
        patient_name, cn_number = extract_winclinic_data(uploaded_winclinic)
        st.success("✅ ดึงข้อมูลสำเร็จ!")
        st.info(f"**👤 ชื่อ-สกุล:** {patient_name}  |  **🆔 HN:** {cn_number}")
    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาดในการอ่านไฟล์ Winclinic: {e}")
        st.stop()

    st.divider()

    # ขั้นตอนที่ 2: กรอกข้อมูลการนัดหมาย
    st.header("2. รายละเอียดการนัดหมาย")
    col1, col2 = st.columns(2)
    with col1:
        appt_date = st.text_input("📅 วันที่นัดหมาย", placeholder="เช่น 12 สิงหาคม 2569")
        appt_time = st.text_input("⏰ เวลานัด", placeholder="เช่น 08.00 - 10.00 น.")
    with col2:
        doctor = st.selectbox("👨‍⚕️ แพทย์ผู้ตรวจ", ["นพ.อภิสิทธิ์ สื่อประเสริฐสิทธิ์", "ระบุแพทย์ท่านอื่น..."])
        if doctor == "ระบุแพทย์ท่านอื่น...":
            doctor = st.text_input("พิมพ์ชื่อแพทย์ผู้ตรวจ")
            
        action = st.text_input("🩺 รายการตรวจ", value="เจาะเลือด FBS + Lipid ก่อนพบแพทย์")
    
    instruction = st.text_input("📌 คำแนะนำเพิ่มเติม", value="งดน้ำ-งดอาหาร 6-8 ชั่วโมงก่อนตรวจ")

    st.divider()

    # ขั้นตอนที่ 3: สร้างและดาวน์โหลด
    st.header("3. สร้างบัตรนัด")
    
    # กำหนดชื่อไฟล์ Template ที่ต้องใช้
    TEMPLATE_FILENAME = "Template.xlsx"
    
    if st.button("🖨️ สร้างไฟล์บัตรนัด (Excel)", type="primary", use_container_width=True):
        if not appt_date or not appt_time:
            st.warning("⚠️ กรุณาระบุวันที่และเวลานัดหมายให้ครบถ้วน")
        else:
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
                # เรียกใช้งานฟังก์ชันหยอดข้อมูล
                excel_file = generate_appointment_card(TEMPLATE_FILENAME, data_to_fill)
                
                st.balloons()
                st.success("🎉 สร้างบัตรนัดเสร็จสมบูรณ์! พร้อมสั่งปริ้นได้เลย")
                
                # ปุ่มดาวน์โหลด
                st.download_button(
                    label="📥 ดาวน์โหลดไฟล์บัตรนัด",
                    data=excel_file,
                    file_name=f"Appointment_{cn_number}_{patient_name}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            except FileNotFoundError:
                st.error(f"❌ ไม่พบไฟล์แม่แบบ '{TEMPLATE_FILENAME}'")
                st.info(f"💡 คำแนะนำ: กรุณาตรวจสอบว่ามีไฟล์ {TEMPLATE_FILENAME} อยู่ในโฟลเดอร์เดียวกับโค้ด app.py หรือไม่ (หรืออัปโหลดขึ้น GitHub ให้ครบถ้วน)")
