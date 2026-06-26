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
# 1. ฟังก์ชันสร้างบัตรนัด (HTML) — ดีไซน์ทันสมัย คุมโทนเขียว-น้ำตาล
# ==========================================
def generate_appt_html(data, lang="th"):
    L = {
        "th": {
            "print": "🖨️ ปริ้นบัตรนัด",
            "hosp": "โรงพยาบาลโฮม ฉะเชิงเทรา",
            "sub": "บัตรนัดหมาย | Appointment Card",
            "name": "ชื่อ-สกุล:", "hn": "HN:", "age": "อายุ:", "right": "สิทธิการรักษา:",
            "date": "วันที่นัด", "time": "เวลา", "doctor": "แพทย์:",
            "reason": "เหตุผลการนัด / รายการ:", "care": "📌 คำแนะนำในการปฏิบัติตัว:",
            "charge": "*** เรียกเก็บเงินกับทางโรงพยาบาล",
            "note1": "หากต้องการนัดหมาย / เลื่อนนัด / ยกเลิกนัด กรุณาติดต่อ <b>038-511-123</b>",
            "note2": "กรุณานำยาที่ท่านใช้ประจำมาด้วยทุกครั้งที่มาพบแพทย์",
            "note3": "<b>กรุณายื่นบัตรนัดที่ประชาสัมพันธ์ทุกครั้งที่เข้ารับบริการ</b>",
        },
        "en": {
            "print": "🖨️ Print Appointment Card",
            "hosp": "Home Hospital Chachoengsao",
            "sub": "Appointment Card | บัตรนัดหมาย",
            "name": "Name:", "hn": "HN:", "age": "Age:", "right": "Coverage:",
            "date": "Appointment Date", "time": "Time", "doctor": "Doctor:",
            "reason": "Reason / Service:", "care": "📌 Instructions:",
            "charge": "*** Charge to the hospital",
            "note1": "To make, reschedule or cancel an appointment, please call <b>038-511-123</b>",
            "note2": "Please bring your regular medications to every visit",
            "note3": "<b>Please present this card at the reception on every visit</b>",
        },
    }
    t = L.get(lang, L["th"])
    page_lang = "en" if lang == "en" else "th"

    charge_html = ""
    if data.get("charge_note"):
        charge_html = (
            '<div style="text-align:center; color:#B00020; font-weight:bold; '
            f'margin-top:10px; font-size:13px;">{t["charge"]}</div>'
        )

    html = f"""<!DOCTYPE html><html lang="{page_lang}"><head><meta charset="UTF-8"><style>
        * {{ -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; box-sizing: border-box; }}
        body {{ font-family: 'Tahoma', sans-serif; color:#2b2b2b; margin:0; padding:14px; background:#f4f1ec; }}
        .card {{ max-width:720px; margin:0 auto; background:#fff; border-radius:14px; overflow:hidden; border:1px solid #e3ded6; box-shadow:0 4px 18px rgba(0,0,0,0.06); }}
        .top {{ display:flex; align-items:center; padding:18px 24px 14px 24px; }}
        .top img {{ width:54px; margin-right:14px; }}
        .hosp {{ font-size:20px; font-weight:bold; color:{brand_green}; line-height:1.25; }}
        .sub {{ font-size:13px; color:{brand_brown}; letter-spacing:0.5px; }}
        .accent {{ height:3px; background:linear-gradient(90deg, #cde0d3, #e8dccb); }}
        .body {{ padding:20px 24px 24px 24px; }}
        .grid {{ display:flex; flex-wrap:wrap; }}
        .cell {{ flex:1 1 50%; padding:5px 0; font-size:14px; }}
        .cell.full {{ flex:1 1 100%; }}
        .lbl {{ color:#9a8a74; font-weight:bold; }}
        .val {{ color:#1a1a1a; font-weight:bold; }}
        .appt-box {{ background:#eff5f1; border:1px solid #dbe7df; color:{brand_green}; border-radius:10px; padding:14px 20px; display:flex; justify-content:space-between; align-items:center; margin:16px 0; }}
        .appt-box .k {{ font-size:12px; color:#9a9a9a; margin-bottom:2px; font-weight:normal; }}
        .appt-box .v {{ font-size:19px; font-weight:bold; color:{brand_green}; }}
        .infobox {{ border-left:3px solid #e0d2bd; background:#faf8f4; padding:10px 14px; border-radius:0 8px 8px 0; margin:10px 0; font-size:14px; }}
        .carebox {{ border-left:3px solid #cfe0d4; background:#f3f8f4; padding:10px 14px; border-radius:0 8px 8px 0; margin:10px 0; font-size:14px; }}
        .notes {{ font-size:12px; color:#666; margin-top:18px; border-top:1px dashed #cfc8bd; padding-top:12px; line-height:1.9; }}
        .notes b {{ color:{brand_green}; }}
        .print-btn {{ background:{brand_green}; color:#fff; border:none; padding:11px; cursor:pointer; width:100%; font-size:16px; margin-bottom:14px; font-weight:bold; border-radius:8px; }}
        @media print {{ body {{ background:#fff; padding:0; }} .no-print {{ display:none !important; }} .card {{ box-shadow:none; }} }}
    </style></head><body>
        <button class="no-print print-btn" onclick="window.print()">{t["print"]}</button>
        <div class="card">
            <div class="top">
                <img src="data:image/png;base64,{logo_base64}">
                <div>
                    <div class="hosp">{t["hosp"]}</div>
                    <div class="sub">{t["sub"]}</div>
                </div>
            </div>
            <div class="accent"></div>
            <div class="body">
                <div class="grid">
                    <div class="cell"><span class="lbl">{t["name"]}</span> <span class="val">{data['name']}</span></div>
                    <div class="cell"><span class="lbl">{t["hn"]}</span> <span class="val">{data['hn']}</span></div>
                    <div class="cell"><span class="lbl">{t["age"]}</span> <span class="val">{data['age']}</span></div>
                    <div class="cell"><span class="lbl">{t["right"]}</span> <span class="val">{data['right']}</span></div>
                </div>

                <div class="appt-box">
                    <div><div class="k">{t["date"]}</div><div class="v">{data['appt_date']}</div></div>
                    <div style="text-align:right;"><div class="k">{t["time"]}</div><div class="v">{data['appt_time']}</div></div>
                </div>

                <div class="grid">
                    <div class="cell full"><span class="lbl">{t["doctor"]}</span> <span class="val">{data['doctor']} {data['license']}</span></div>
                </div>

                <div class="infobox"><b style="color:{brand_brown};">{t["reason"]}</b> {data['action']}</div>
                <div class="carebox"><b style="color:{brand_green};">{t["care"]}</b> {data['instruction']}</div>
                {charge_html}

                <div class="notes">
                    • {t["note1"]}<br>
                    • {t["note2"]}<br>
                    • {t["note3"]}
                </div>
            </div>
        </div>
    </body></html>"""
    return base64.b64encode(html.encode("utf-8")).decode("utf-8")


# ==========================================
# 2. หน้าจอ UI
# ==========================================
st.title("🏥 ระบบออกบัตรนัดหมาย รพ.โฮม")

# --- เลือกภาษาบัตรนัด ---
lang_mode = st.radio("🌐 ภาษาบัตรนัด / Card Language", ["ไทย", "English"], horizontal=True)
lang_code = "en" if lang_mode == "English" else "th"

_EN_MONTHS = ["", "January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]
def _fmt_en_date(d):
    """วันที่แบบอังกฤษ ค.ศ. เช่น 26 June 2026"""
    return f"{d.day} {_EN_MONTHS[d.month]} {d.year}"

# ตัวฟอร์แมตวันที่ตามภาษาที่เลือก
_fmt_date = _fmt_en_date if lang_code == "en" else format_thai_date

# --- ส่วนที่ 1: ข้อมูลคนไข้ ---
st.markdown("### 1️⃣ ข้อมูลคนไข้")
col_p1, col_p2 = st.columns(2)
with col_p1:
    patient_name = st.text_input("👤 ชื่อ-นามสกุลคนไข้", placeholder="เช่น นางสมหญิง ใจดี")
with col_p2:
    hn_number = st.text_input("🆔 รหัสคนไข้ (HN)", placeholder="เช่น 00012345")

col_a1, col_a2, col_a3 = st.columns([1, 1, 2])
with col_a1:
    age_year = st.number_input("อายุ (ปี)", min_value=0, max_value=130, value=0, step=1)
with col_a2:
    age_month = st.number_input("อายุ (เดือน)", min_value=0, max_value=11, value=0, step=1)
with col_a3:
    treat_right = st.selectbox(
        "สิทธิการรักษา",
        ["ทั่วไป", "ประกันสังคม", "บัตรทอง (UC)", "ข้าราชการ/เบิกได้", "ประกันชีวิต/บริษัท", "อื่นๆ"],
    )

# รวมข้อความอายุ (ตามภาษา)
if age_year > 0 or age_month > 0:
    if lang_code == "en":
        age_text = f"{age_year} yrs" + (f" {age_month} mos" if age_month > 0 else "")
    else:
        age_text = f"{age_year} ปี" + (f" {age_month} เดือน" if age_month > 0 else "")
else:
    age_text = ""

st.divider()

# --- ส่วนที่ 2: รายละเอียดนัดหมาย ---
st.markdown("### 2️⃣ รายละเอียดการนัดหมาย")
appt_type = st.radio(
    "ประเภทนัดหมาย",
    ["มาติดตามอาการ", "หัตถการ", "นัด Ultrasound"],
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

if appt_type == "หัตถการ":
    proc_type = st.selectbox(
        "🔧 ประเภทหัตถการ",
        ["เจาะเลือด", "ผ่าตัดเล็ก", "ทำแผล", "ทำแผล/ตัดไหม", "นัดพ่นยา"]
    )
    if proc_type == "เจาะเลือด":
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
    elif proc_type == "ผ่าตัดเล็ก":
        default_action = "ผ่าตัดเล็ก (Minor Surgery)"
        default_instruction = "ทำความสะอาดร่างกายก่อนมา งดทาครีม/โลชั่นบริเวณที่ทำหัตถการ และแจ้งประวัติแพ้ยา/โรคประจำตัวกับเจ้าหน้าที่"
    elif proc_type == "ทำแผล":
        default_action = "ทำแผล (Wound Dressing)"
        default_instruction = "รักษาความสะอาดบริเวณแผล ไม่ให้แผลโดนน้ำก่อนมาทำแผล และนำยา/อุปกรณ์เดิม (ถ้ามี) มาด้วย"
    elif proc_type == "ทำแผล/ตัดไหม":
        default_action = "ทำแผล / ตัดไหม (Dressing & Suture Removal)"
        default_instruction = "รักษาความสะอาดบริเวณแผล ไม่ให้แผลโดนน้ำก่อนมา และนำใบนัด/ประวัติการเย็บแผลมาด้วย"
    else:  # นัดพ่นยา
        default_action = "พ่นยา (Nebulization)"
        default_instruction = "มาก่อนเวลานัดเล็กน้อย นำยาพ่น/ยาประจำตัวมาด้วย หากมีอาการหอบเหนื่อยมากขึ้นก่อนวันนัด ให้รีบมาพบแพทย์ทันที"

elif appt_type == "นัด Ultrasound":
    us_type = st.selectbox("🩻 ชนิดการตรวจ Ultrasound", list(US_PREP.keys()))
    default_action = f"Ultrasound {us_type}"
    default_instruction = US_PREP[us_type]["instruction"]
    st.info(f"📋 **การเตรียมตัว:** {default_instruction}")
    st.caption("หมายเหตุ: คำแนะนำเป็นมาตรฐานทั่วไป กรุณาตรวจสอบ/ปรับตามแนวทางของโรงพยาบาลและคำสั่งแพทย์")

# --- คำนวณวันนัดอัตโนมัติ ---
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
    is_range = st.checkbox("นัดเป็นช่วงวัน (เช่น 26-28)")
    if is_range:
        end_date = st.date_input("ถึงวันที่", value=final_date)
        d1, d2 = sorted([final_date, end_date])
        if d1.month == d2.month and d1.year == d2.year:
            _tail = _fmt_date(d2).split(" ", 1)[1]   # เช่น "มิถุนายน 2569" / "June 2026"
            appt_date_str = f"{d1.day}-{d2.day} {_tail}"
        else:
            appt_date_str = f"{_fmt_date(d1)} - {_fmt_date(d2)}"
    else:
        appt_date_str = _fmt_date(final_date)

col_t1, col_t2 = st.columns(2)
with col_t1:
    appt_date_text = st.text_input("รูปแบบวันที่บนบัตร (แก้ไขข้อความได้)", value=appt_date_str)
with col_t2:
    _time_choice = st.selectbox("เวลานัด",
                                ["08.00 - 10.00 น.", "10.00 - 12.00 น.",
                                 "12.15 - 13.00 น.", "13.00 - 15.00 น.", "15.00 - 16.30 น.",
                                 "ระบุเวลา..."])
    if _time_choice == "ระบุเวลา...":
        time_sel = st.text_input("พิมพ์เวลานัดเอง", placeholder="เช่น 09.30 - 11.00 น.")
    else:
        time_sel = _time_choice

st.divider()

# --- ส่วนที่ 3: แพทย์และรายการ ---
st.markdown("### 3️⃣ แพทย์และรายการ")
col_d1, col_d2 = st.columns([3, 1])
with col_d1:
    doc_appt = st.text_input("แพทย์ผู้ตรวจ", value="นพ.อภิสิทธิ์ สื่อประเสริฐสิทธิ์")
with col_d2:
    license_appt = st.text_input("เลขใบอนุญาต", value="ว.46208")

act_appt = st.text_input("เหตุผลการนัด / รายการตรวจ", value=default_action)
ins_appt = st.text_input("คำแนะนำในการปฏิบัติตัว", value=default_instruction)
charge_note = st.checkbox("เรียกเก็บเงินกับทางโรงพยาบาล (แสดงหมายเหตุสีแดงบนบัตร)")

st.divider()

# --- สร้างพรีวิว ---
if st.button("✨ สร้างหน้าพรีวิวสำหรับปริ้นบัตรนัด", type="primary", width="stretch"):
    if not patient_name:
        st.error("⚠️ กรุณากรอกชื่อคนไข้ก่อนครับ")
    else:
        # แปลสิทธิการรักษาเป็นอังกฤษเมื่อเลือกโหมด English
        _RIGHT_EN = {
            "ทั่วไป": "General / Self-pay",
            "ประกันสังคม": "Social Security",
            "บัตรทอง (UC)": "Universal Coverage (UC)",
            "ข้าราชการ/เบิกได้": "Civil Servant (CSMBS)",
            "ประกันชีวิต/บริษัท": "Private Insurance / Company",
            "อื่นๆ": "Other",
        }
        right_val = _RIGHT_EN.get(treat_right, treat_right) if lang_code == "en" else treat_right
        data_appt = {
            "name": patient_name,
            "hn": hn_number,
            "age": age_text,
            "right": right_val,
            "appt_date": appt_date_text,
            "appt_time": time_sel,
            "doctor": doc_appt,
            "license": license_appt,
            "action": act_appt,
            "instruction": ins_appt,
            "charge_note": charge_note,
        }
        st.markdown(
            f'<iframe src="data:text/html;base64,{generate_appt_html(data_appt, lang_code)}" '
            f'width="100%" height="640" style="border:none;"></iframe>',
            unsafe_allow_html=True
        )
