import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side
from openpyxl.drawing.image import Image as OpenpyxlImage
import os

def build_eco_template():
    logo_path = 'logo.png' 
    if not os.path.exists(logo_path):
        print(f"❌ ไม่พบไฟล์โลโก้: {logo_path}")
        return

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Eco Appointment Card"

    ws.sheet_view.showGridLines = False

    brand_green = "2C5E3B"
    brand_brown = "8B5A2B"

    ws.row_dimensions[1].height = 10 
    ws.row_dimensions[2].height = 90 # ลดความสูง Header ลงนิดหน่อยเพราะไม่มีสีพื้นหลัง

    ws.column_dimensions['A'].width = 3
    ws.column_dimensions['B'].width = 30 
    ws.column_dimensions['C'].width = 25
    ws.column_dimensions['D'].width = 45 

    img = OpenpyxlImage(logo_path)
    scale_factor = 0.35 # ปรับขนาดเล็กลงนิดนึงให้ดูคลีนๆ
    img.width = int(img.width * scale_factor)
    img.height = int(img.height * scale_factor)
    ws.add_image(img, 'B2') 

    # Header แบบไม่มีสีพื้นหลัง (ใช้ตัวหนังสือสีเขียวเข้ม)
    ws.merge_cells('C2:D2')
    header_cell = ws['C2']
    header_cell.value = "👨‍⚕️ โรงพยาบาลโฮม ฉะเชิงเทรา\nบัตรนัดหมาย | Appointment Card"
    header_cell.font = Font(name='Tahoma', size=16, bold=True, color=brand_green)
    header_cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

    # ตีเส้นใต้ Header
    green_bottom_border = Border(bottom=Side(border_style="thick", color=brand_green))
    ws['C2'].border = green_bottom_border
    ws['D2'].border = green_bottom_border
    ws['B2'].border = green_bottom_border

    # ข้อมูลคนไข้
    row_patient_info = 6
    ws.row_dimensions[row_patient_info].height = 25
    ws[f'B{row_patient_info}'] = "ชื่อ - สกุล :" 
    ws[f'B{row_patient_info}'].font = Font(name='Tahoma', size=12, bold=True)
    ws[f'D{row_patient_info}'] = "HN :"       
    ws[f'D{row_patient_info}'].font = Font(name='Tahoma', size=12, bold=True)

    # รายละเอียดการนัด
    row_appt_details = 8
    ws.row_dimensions[row_appt_details].height = 25
    brown_bottom_border = Border(bottom=Side(border_style="medium", color=brand_brown))
    ws.merge_cells(f'B{row_appt_details}:D{row_appt_details}')
    ws[f'B{row_appt_details}'] = "🗓️ รายละเอียดการนัดหมาย"
    ws[f'B{row_appt_details}'].font = Font(name='Tahoma', size=12, bold=True, color=brand_brown)
    for col in ['B', 'C', 'D']:
        ws[f'{col}{row_appt_details}'].border = brown_bottom_border

    # วันที่และเวลา
    row_datetime = 10
    ws.row_dimensions[row_datetime].height = 45
    ws[f'B{row_datetime}'] = "วันที่นัด : "
    ws[f'B{row_datetime}'].font = Font(name='Tahoma', size=16, bold=True, color=brand_green)
    ws[f'B{row_datetime}'].alignment = Alignment(vertical='center')
    
    ws[f'D{row_datetime}'] = "เวลา : "
    ws[f'D{row_datetime}'].font = Font(name='Tahoma', size=16, bold=True, color=brand_green)
    ws[f'D{row_datetime}'].alignment = Alignment(vertical='center')

    # แพทย์และรายการตรวจ
    row_doc_action = 12
    ws.row_dimensions[row_doc_action].height = 25
    ws[f'B{row_doc_action}'] = "แพทย์ผู้ตรวจ : "
    ws[f'B{row_doc_action}'].font = Font(name='Tahoma', size=12)
    ws[f'D{row_doc_action}'] = "รายการตรวจ : "
    ws[f'D{row_doc_action}'].font = Font(name='Tahoma', size=12)

    # คำแนะนำ
    row_instruction = 14
    ws.row_dimensions[row_instruction].height = 30
    ws.merge_cells(f'B{row_instruction}:D{row_instruction}')
    ws[f'B{row_instruction}'] = "📌 คำแนะนำในการปฏิบัติตัว: "
    ws[f'B{row_instruction}'].font = Font(name='Tahoma', size=12, bold=True, color=brand_brown)
    ws[f'B{row_instruction}'].alignment = Alignment(vertical='center')

    # Footer
    row_footer = 16
    ws.row_dimensions[row_footer].height = 20
    ws.merge_cells(f'B{row_footer}:D{row_footer}')
    ws[f'B{row_footer}'] = "📍 หากต้องการเลื่อนนัด/สอบถามข้อมูลเพิ่มเติม โทร 038-511-123 (กรุณานำยาเดิมมาด้วยทุกครั้ง)"
    ws[f'B{row_footer}'].font = Font(name='Tahoma', size=10, italic=True)
    ws[f'B{row_footer}'].alignment = Alignment(horizontal='center', vertical='center')

    # เซฟไฟล์
    wb.save("Template.xlsx")
    print("✅ สร้างไฟล์ Template.xlsx (Eco Mode) สำเร็จ!")

if __name__ == "__main__":
    build_eco_template()
