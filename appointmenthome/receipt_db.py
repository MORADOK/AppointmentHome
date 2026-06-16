"""
receipt_db.py — ระบบบันทึก/รันเลขใบเสร็จภายใน (ใช้ SQLite)

รูปแบบเลขใบเสร็จ: {PREFIX}{YYMMDD}-{NN}
  เช่น  CA690615-01
        CA      = รหัสนำหน้า (วิธีชำระ/ประกัน)
        69      = ปี พ.ศ. 2 หลัก (2569)
        06      = เดือน
        15      = วันที่
        01      = ลำดับของใบเสร็จในแต่ละวัน (รีเซ็ตใหม่ทุกวัน)

กันเลขซ้ำเมื่อหลายคนกดพร้อมกัน: threading.Lock + SQLite BEGIN IMMEDIATE

** สำคัญ **
- เก็บไฟล์ DB บนดิสก์ local ของเครื่องที่รันแอป (ไม่ใช่ network share)
- เรียก get_next_receipt_no() เฉพาะตอนบันทึก/ออกใบเสร็จจริง ไม่ใช่ตอนพรีวิว
- ต้องรันแบบ on-premise (ดิสก์ถาวร) ถ้ารันบน Cloud ไฟล์ DB จะถูกรีเซ็ตเมื่อ redeploy
"""

import sqlite3
import threading
from pathlib import Path
from datetime import datetime

# ==========================================
# ตั้งค่า
# ==========================================
DB_PATH = Path(__file__).parent / "data" / "receipts.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# "global"     = ลำดับในวันนับรวมทุกรหัส (CA-01, TT-02, CR-03 ...)
# "per_prefix" = แยกลำดับตามรหัสนำหน้า  (CA-01, CA-02, TT-01, CR-01 ...)
SEQ_SCOPE = "per_prefix"

_lock = threading.Lock()

# รหัสนำหน้าตามวิธีชำระเงิน
PAYMENT_PREFIX = {
    "เงินสด": "CA",
    "โอนจ่าย": "TT",
    "บัตรเครดิต": "CR",
}

# รหัสนำหน้าตามบริษัทประกัน (เคสประกัน)
INSURANCE_PREFIX = {
    "TPA": "TPA",
    "ไทยสมุทร": "OC",
    "ไทยวิวัฒน์": "TVV",
    "เจนเนอราลี่": "GEN",
    "ทิพยประกันภัย": "TIP",
    "เมืองไทยประกันภัย": "MT",
    "Allianz Partners": "AP",
}


# ==========================================
# ฟังก์ชันภายใน
# ==========================================
def _connect():
    conn = sqlite3.connect(str(DB_PATH), timeout=10)
    conn.isolation_level = None
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


def _date_parts():
    now = datetime.now()
    yy = (now.year + 543) % 100   # ปี พ.ศ. 2 หลัก
    return f"{yy:02d}{now.month:02d}{now.day:02d}"   # เช่น 690615


# ==========================================
# ฟังก์ชันใช้งาน
# ==========================================
def init_db():
    """สร้างตารางครั้งแรก (เรียกตอนแอปเริ่มทำงาน)"""
    conn = _connect()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS counters (
                key      TEXT PRIMARY KEY,
                last_no  INTEGER NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS receipts (
                receipt_no TEXT PRIMARY KEY,
                issued_at  TEXT NOT NULL,
                prefix     TEXT,
                patient    TEXT,
                total      REAL,
                payment    TEXT,
                receiver   TEXT
            )
        """)
    finally:
        conn.close()


def get_next_receipt_no(prefix):
    """จองเลขใบเสร็จถัดไปแบบ atomic — รับประกันไม่ซ้ำแม้หลายคนกดพร้อมกัน
       prefix = รหัสนำหน้า เช่น 'CA', 'TT', 'CR', 'TPA' ...
       คืนค่า เช่น 'CA690615-01'  *** เรียกตอนออกใบเสร็จจริงเท่านั้น ***"""
    date_key = _date_parts()
    counter_key = date_key if SEQ_SCOPE == "global" else f"{prefix}-{date_key}"

    with _lock:
        conn = _connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT last_no FROM counters WHERE key=?", (counter_key,)
            ).fetchone()
            new_no = (row[0] if row else 0) + 1
            conn.execute(
                "INSERT INTO counters(key, last_no) VALUES(?,?) "
                "ON CONFLICT(key) DO UPDATE SET last_no=excluded.last_no",
                (counter_key, new_no),
            )
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            raise
        finally:
            conn.close()

    return f"{prefix}{date_key}-{str(new_no).zfill(2)}"


def log_receipt(receipt_no, prefix="", patient="", total=0.0, payment="", receiver=""):
    """บันทึกรายการใบเสร็จที่ออกแล้ว (audit trail)"""
    conn = _connect()
    try:
        conn.execute(
            "INSERT OR IGNORE INTO receipts"
            "(receipt_no, issued_at, prefix, patient, total, payment, receiver) "
            "VALUES(?,?,?,?,?,?,?)",
            (
                receipt_no,
                datetime.now().isoformat(timespec="seconds"),
                prefix,
                patient,
                float(total or 0),
                payment,
                receiver,
            ),
        )
    finally:
        conn.close()


def peek_today_count():
    """ดูจำนวนใบเสร็จที่ออกไปแล้ววันนี้ (ไม่จองเลข)"""
    date_key = _date_parts()
    counter_key = date_key if SEQ_SCOPE == "global" else None
    conn = _connect()
    try:
        if SEQ_SCOPE == "global":
            row = conn.execute(
                "SELECT last_no FROM counters WHERE key=?", (counter_key,)
            ).fetchone()
            return row[0] if row else 0
        # per_prefix: รวมทุก prefix ของวันนี้
        row = conn.execute(
            "SELECT COALESCE(SUM(last_no),0) FROM counters WHERE key LIKE ?",
            (f"%-{date_key}",),
        ).fetchone()
        return row[0] if row else 0
    finally:
        conn.close()


def list_recent(limit=20):
    """ดึงรายการใบเสร็จล่าสุด (ไว้ทำหน้าประวัติ/รายงาน)"""
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT receipt_no, issued_at, patient, total, payment, receiver "
            "FROM receipts ORDER BY issued_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    finally:
        conn.close()
    return rows


def find_today_duplicate(patient, total):
    """ตรวจว่าคนไข้คนนี้ ยอดเท่ากัน ออกใบเสร็จไปแล้ว 'วันนี้' หรือยัง
       คืนเลขใบเสร็จเดิมถ้าเจอ (เช่น 'CA690615-01'), คืน None ถ้ายังไม่มี
       ใช้เตือนกันการออกใบซ้ำโดยไม่ตั้งใจ"""
    date_key = _date_parts()   # YYMMDD ของวันนี้ ซึ่งฝังอยู่ในเลขใบเสร็จ
    patient = str(patient or "").strip()
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT receipt_no FROM receipts "
            "WHERE patient=? AND ABS(total-?)<0.01 AND receipt_no LIKE ? "
            "ORDER BY issued_at DESC LIMIT 1",
            (patient, float(total or 0), f"%{date_key}%"),
        ).fetchone()
    finally:
        conn.close()
    return row[0] if row else None