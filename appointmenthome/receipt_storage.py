r"""
receipt_storage.py — บันทึกไฟล์ใบเสร็จ Excel ลงโฟลเดอร์ปลายทาง (ตั้งค่าใน config.py)

ใช้บนเครื่องที่รันแอป (on-premise) ที่เข้าถึงโฟลเดอร์แชร์ \\server\share ได้
"""

from pathlib import Path
from datetime import datetime

import config

# อักขระต้องห้ามในชื่อไฟล์ Windows
_BAD_CHARS = '\\/:*?"<>|'


def _safe_name(text):
    text = str(text or "").strip()
    return "".join(c for c in text if c not in _BAD_CHARS).strip()


def save_receipt_file(receipt_no, file_bytes, patient=""):
    """บันทึกไฟล์ใบเสร็จ Excel ลงโฟลเดอร์ปลายทาง
       - receipt_no : เลขใบเสร็จ เช่น CA690615-01
       - file_bytes : BytesIO หรือ bytes ของไฟล์ .xlsx
       - patient    : ชื่อคนไข้ (ใช้ตั้งชื่อไฟล์)
       คืนค่า (success: bool, path_or_error: str)"""
    try:
        base = Path(config.RECEIPT_SAVE_DIR)
        if getattr(config, "ORGANIZE_BY_DATE", False):
            now = datetime.now()
            base = base / str(now.year + 543) / f"{now.month:02d}"
        base.mkdir(parents=True, exist_ok=True)

        patient_clean = _safe_name(patient)
        fname = f"{_safe_name(receipt_no)}"
        if patient_clean:
            fname += f"_{patient_clean}"
        fname += ".xlsx"

        dest = base / fname
        data = file_bytes.getvalue() if hasattr(file_bytes, "getvalue") else file_bytes
        with open(dest, "wb") as f:
            f.write(data)
        return True, str(dest)
    except Exception as e:
        return False, str(e)