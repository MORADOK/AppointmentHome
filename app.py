import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.drawing.image import Image as OpenpyxlImage
import os

def build_modern_template_with_logo_v2():
    # กำหนดเส้นทางโลโก้
    logo_path = 'logo.png' # อย่าลืมนำไฟล์ image_2.png มาเซฟเป็น logo.png ไว้ที่นี่
    
    if not os.path.exists(logo_path):
        print(f"❌ ไม่พบไฟล์โลโก้ที่ชื่อ: {logo_path}")
        print("กรุณาบันทึกโลโก้ (image_2.png) เป็นไฟล์ 'logo.png' ไว้ในโฟลเดอร์เดียวกับโค้ดนี้")
        return

    # 1. สร้างไฟล์ Excel ใหม่
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Modern Appointment Card"

    # 2. ปิดเส้นตาราง (Gridlines)
    ws.sheet_view.showGridLines = False

    # 3. กำหนดโค้ดสีประจำโรงพยาบาล
    brand_green = "2C5E3B" # เขียวเข้ม
    brand_brown = "8B5A2B" # น้ำตาล

    # 4. ตั้งค่า Rows
    ws.row_dimensions[1].height = 10 # Padding
    ws.row_dimensions[2].height = 110 # Header

    # 5. ปรับขนาดคอลัมน์
    ws.column_dimensions['A'].width = 3
    ws.column_dimensions['B'].width = 30 # Logo Area
    ws.column_dimensions['C'].width = 25
    ws.column_dimensions['D'].width = 45 # Title Area (ขยายเผื่อชื่อ รพ.)

    # 6. แทรกโลโก้
    img = OpenpyxlImage(logo_path)
    # ปรับขนาดภาพ (ย่อเหลือ 40% ให้ดูทันสมัย)
    scale_factor = 0.4
    img.width = int(img.width * scale_factor)
    img.height = int(img.height * scale_factor)
    ws.add_image(img, 'B2') # เริ่มวางที่เซลล์ B2

    # 7. สร้างแถบสีเขียวและข้อความ Title
    ws.merge_cells('C2:D2')
    header_cell = ws['C2']
    header_cell.value = "👨‍⚕️ โรงพยาบาลโฮม ฉะเชิงเทรา\nบัตรนัดหมาย | Appointment Card"
    
    # 7.1 **อัปเดต**: จัดรูปแบบ Title ให้ชัดเจน (สีขาวบริสุทธิ์ 'FFFFFF')
    header_cell.font = Font(
        name='Tahoma', 
        size=16, # ขยายขนาด
        bold=True, 
        color="FFFFFF" # สีขาวบริสุทธิ์สว่าง (Ensure it's Pure White)
    )
    header_cell.fill = PatternFill(start_color=brand_green, end_color=brand_green, fill_type="solid")
    # wrap_text=True เพื่อให้ขึ้นบรรทัดใหม่ตาม \n
    header_cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

    # 8. ส่วนข้อมูลคนไข้ (พิกัดสำหรับการหยอดข้อมูล)
    row_patient_info = 6
    ws.row_dimensions[row_patient_info].height = 25
    ws[f'B{row_patient_info}'] = "ชื่อ - สกุล :" 
    ws[f'B{row_patient_info}'].font = Font(name='Tahoma', size=12, bold=True)
    ws[f'D{row_patient_info}'] = "HN :"       
    ws[f'D{row_patient_info}'].font = Font(name='Tahoma', size=12, bold=True)

    # 9. ส่วนรายละเอียดการนัดหมาย
    row_appt_details = 8
    ws.row_dimensions[row_appt_details].height = 25
    brown_bottom_border = Border(bottom=Side(border_style="medium", color=brand_brown))
    ws.merge_cells(f'B{row_appt_details}:D{row_appt_details}')
    ws[f'B{row_appt_details}'] = "🗓️ รายละเอียดการนัดหมาย"
    ws[f'B{row_appt_details}'].font = Font(name='Tahoma', size=12, bold=True, color=brand_brown)
    for col in ['B', 'C', 'D']:
        ws[f'{col}{row_appt_details}'].border = brown_bottom_border

    # วันที่และเวลา (ตัวใหญ่สุดเพื่อ UX)
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

    # 10. ส่วนคำแนะนำ
    row_instruction = 14
    ws.row_dimensions[row_instruction].height = 30
    ws.merge_cells(f'B{row_instruction}:D{row_instruction}')
    ws[f'B{row_instruction}'] = "📌 คำแนะนำในการปฏิบัติตัว: "
    ws[f'B{row_instruction}'].font = Font(name='Tahoma', size=12, bold=True, color=brand_brown)
    ws[f'B{row_instruction}'].alignment = Alignment(vertical='center')

    # 11. ส่วน Footer และติดต่อ
    row_footer = 16
    ws.row_dimensions[row_footer].height = 20
    ws.merge_cells(f'B{row_footer}:D{row_footer}')
    ws[f'B{row_footer}'] = "📍 หากต้องการเลื่อนนัด/สอบถามข้อมูลเพิ่มเติม โทร 038-511-123 (กรุณานำยาเดิมมาด้วยทุกครั้ง)"
    ws[f'B{row_footer}'].font = Font(name='Tahoma', size=10, italic=True)
    ws[f'B{row_footer}'].alignment = Alignment(horizontal='center', vertical='center')

    # 12. ตีเส้นกรอบบัตรด้านนอกสุด (เพื่อความสวยงามตอนปริ้น)
    thin_border_side = Side(border_style="thin", color="AAAAAA")
    for row in range(2, 17):
        ws[f'B{row}'].border = Border(left=thin_border_side, top=ws[f'B{row}'].border.top, bottom=ws[f'B{row}'].border.bottom)
        ws[f'D{row}'].border = Border(right=thin_border_side, top=ws[f'D{row}'].border.top, bottom=ws[f'D{row}'].border.bottom)
    for col in ['B', 'C', 'D']:
        ws[f'{col}2'].border = Border(top=thin_border_side, left=ws[f'{col}2'].border.left, right=ws[f'{col}2'].border.right)
        ws[f'{col}16'].border = Border(bottom=thin_border_side, left=ws[f'{col}16'].border.left, right=ws[f'{col}16'].border.right)

    # บันทึกไฟล์
    output_filename = "Template.xlsx"
    wb.save(output_filename)
    print(f"✅ สร้างไฟล์ Template Modern (v2) สีชัดเจนสำเร็จ: {output_filename}")

if __name__ == "__main__":
    build_modern_template_with_logo_v2()
