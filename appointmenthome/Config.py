# ============================================================
# config.py — ตั้งค่าระบบ (แก้ไขตอนติดตั้งบนเครื่องเซิร์ฟเวอร์)
# ============================================================

# โฟลเดอร์ปลายทางสำหรับบันทึกไฟล์ใบเสร็จ Excel
#   - แนะนำใช้ UNC path เต็ม เช่น   r"\\server\share\Receipts"
#   - หรือ local path เช่น          r"C:\Receipts"
#   * อย่าลืมเครื่องหมาย r หน้าสตริง (raw string) เพื่อให้ \ ทำงานถูกต้อง
RECEIPT_SAVE_DIR = r"\\server\share\Receipts"

# แยกโฟลเดอร์ย่อยตามปี/เดือนอัตโนมัติหรือไม่
#   True  -> \\server\share\Receipts\2569\06\CA690615-01_ชื่อ.xlsx
#   False -> \\server\share\Receipts\CA690615-01_ชื่อ.xlsx
ORGANIZE_BY_DATE = True