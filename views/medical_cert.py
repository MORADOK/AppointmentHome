import streamlit as st
import base64
from datetime import datetime

from utils import (
    brand_green,
    logo_base64,
    format_thai_date,
)

# ค่าเริ่มต้นข้อมูลแพทย์/โรงพยาบาล (แก้ไขได้)
DEFAULT_DOCTOR = "นพ.อภิสิทธิ์ สื่อประเสริฐสิทธิ์"
DEFAULT_LICENSE = "ว.46208"
DEFAULT_PLACE = "โรงพยาบาลโฮม 149/1 ถ.ฉะเชิงเทรา-บางปะกง ต.หน้าเมือง อ.เมือง จ.ฉะเชิงเทรา 24000"

# ส่วนหัวและท้ายเอกสาร (ใช้ร่วมกันทุกแบบ)
HEADER_HTML = f"""
<div style="display:flex; align-items:center; border-bottom:2px solid {brand_green}; padding-bottom:10px; margin-bottom:15px;">
    <img src="data:image/png;base64,{logo_base64}" style="width:60px; margin-right:15px;">
    <div>
        <div style="font-size:18px; font-weight:bold; color:{brand_green};">โรงพยาบาลโฮม ฉะเชิงเทรา</div>
        <div style="font-size:12px; color:#555;">149/1 ถ.ฉะเชิงเทรา-บางปะกง ต.หน้าเมือง อ.เมือง จ.ฉะเชิงเทรา 24000 | โทร 038-511-123</div>
    </div>
</div>
"""

FOOTER_HTML = """
<div style="display:flex; justify-content:space-between; font-size:11px; color:#555; margin-top:auto; border-top:1px solid #ddd; padding-top:8px;">
    <div><b>โรงพยาบาลโฮม ฉะเชิงเทรา</b><br>149/1 ถ.ฉะเชิงเทรา-บางปะกง ต.หน้าเมือง อ.เมือง จ.ฉะเชิงเทรา 24000<br>Tel. 038-511-123 | E-mail: Hospitalashome@gmail.com</div>
    <div style="text-align:right;"><b>บริษัท สื่อ การแพทย์ จำกัด</b><br>149/1 ถ.ฉะเชิงเทรา-บางปะกง ต.หน้าเมือง<br>อ.เมือง จ.ฉะเชิงเทรา 24000<br>เลขประจำตัวผู้เสียภาษีอากร 0245563001367</div>
</div>
"""


def _wrap_html(title, body):
    """ครอบเนื้อหาด้วย template + ปุ่มปริ้น แล้วคืนค่าเป็น base64"""
    html = f"""<!DOCTYPE html><html lang="th"><head><meta charset="UTF-8"><style>
        * {{ -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }}
        html, body {{ height: 100%; }}
        body {{ font-family: 'Tahoma', sans-serif; color: #222; font-size: 14px; margin: 0; padding: 10px; line-height: 1.7; box-sizing: border-box; }}
        .card {{ max-width: 800px; margin: 0 auto; padding: 25px; background-color: white; min-height: calc(100vh - 20px); display: flex; flex-direction: column; box-sizing: border-box; }}
        .doc-title {{ text-align:center; font-size:20px; font-weight:bold; margin:10px 0 20px 0; }}
        .field {{ margin-bottom:8px; }}
        .dots {{ border-bottom:1px dotted #555; display:inline-block; min-width:120px; }}
        .sign {{ text-align:center; margin-top:35px; }}
        .print-btn {{ background-color: {brand_green}; color:white; border:none; padding:10px; cursor:pointer; width:100%; font-size:16px; margin-bottom:20px; font-weight:bold; }}
        @media print {{ body {{ padding:0; }} .no-print {{ display:none !important; }} }}
    </style></head><body>
        <button class="no-print print-btn" onclick="window.print()">🖨️ ปริ้นใบรับรองแพทย์</button>
        <div class="card">
            {HEADER_HTML}
            <div class="doc-title">{title}</div>
            {body}
            {FOOTER_HTML}
        </div>
    </body></html>"""
    return base64.b64encode(html.encode("utf-8")).decode("utf-8")


def _val(x, default="......................"):
    """แสดงค่าที่กรอก: ตัวหนา สีดำเข้ม บนเส้นจุดไข่ปลา ให้ดูเด่นแตกต่างจากข้อความ template
    ถ้าเว้นว่าง: แสดงเส้นจุดไข่ปลาสีจางไว้เขียนเอง"""
    x = str(x).strip() if x else ""
    if x:
        return (
            f'<span style="font-weight:bold; color:#000; '
            f'border-bottom:1px dotted #555; padding:0 4px;">{x}</span>'
        )
    return f'<span style="color:#999; letter-spacing:1px;">{default}</span>'


# ==========================================
# แบบที่ 1: ใบรับรองแพทย์ทั่วไป
# ==========================================
def html_general(d):
    body = f"""
    <div class="field">แพทย์ผู้ตรวจ <b>{_val(d['doctor'])}</b></div>
    <div class="field">ผู้ประกอบวิชาชีพเวชกรรมใบอนุญาต เลขที่ {_val(d['license'])}</div>
    <div class="field">สถานที่ประกอบวิชาชีพเวชกรรม/สถานที่ปฏิบัติงานประจำ {_val(d['place'])}</div>
    <div style="text-align:center; font-weight:bold; margin:10px 0;">หนังสือรับรองฉบับนี้ ขอรับรองว่า</div>
    <div class="field">ข้าพเจ้าแพทย์ผู้ตรวจผู้มีชื่อข้างต้นนี้ ได้ทำการตรวจร่างกายบุคคลดังต่อไปนี้</div>
    <div class="field">ชื่อ-นามสกุล <b>{_val(d['name'])}</b>&nbsp;&nbsp;&nbsp; อายุ {_val(d['age'], '......')} ปี</div>
    <div class="field">สถานที่อยู่ {_val(d['address'])}</div>
    <div class="field">บัตรประจำตัวประชาชนเลขที่ {_val(d['id_card'])}</div>
    <div class="field">ได้มารับบริการ เมื่อวันที่ {_val(d['visit_date'])}&nbsp;&nbsp; เวลา {_val(d['visit_time'], '..........')} น.</div>
    <div class="field" style="margin-top:10px;">จากการตรวจร่างกายของผู้มีชื่อข้างต้นแล้ว ขอให้ความเห็นดังต่อไปนี้</div>
    <div class="field">วินิจฉัยโรค {_val(d['diagnosis'])}</div>
    <div class="field">สรุปความเห็น {_val(d['opinion'])}</div>
    <div class="field" style="margin-top:15px;">ใบรับรองแพทย์ฉบับนี้ออกให้เมื่อวันที่ {_val(d['issue_date'])}</div>
    <div style="text-align:center; font-weight:bold; margin-top:10px;">ขอรับรองว่าข้อความข้างต้นเป็นความจริง</div>
    <div class="sign">
        <div>ลงชื่อแพทย์ผู้ตรวจ ......................................................</div>
        <div>( {_val(d['doctor'])} )</div>
        <div>{_val(d['license'])}</div>
    </div>
    <div style="text-align:center; font-size:12px; margin-top:15px;">ใบรับรองฉบับนี้ให้ใช้ได้ 1 เดือนนับแต่วันที่ตรวจร่างกาย</div>
    """
    return _wrap_html("ใบรับรองแพทย์", body)


# ==========================================
# ส่วนประวัติสุขภาพ (ส่วนที่ 1) ใช้ร่วมแบบ 5 โรค และขับรถ
# ==========================================
def _history_html(items):
    rows = ""
    for label, has, detail in items:
        mark_no = "☑" if has == "ไม่มี" else "☐"
        mark_yes = "☑" if has == "มี" else "☐"
        rows += f"""<div class="field">{label}
            &nbsp;&nbsp; {mark_no} ไม่มี &nbsp;&nbsp; {mark_yes} มี (ระบุ) {_val(detail, '..........................')}</div>"""
    return rows


# ==========================================
# แบบที่ 2: ใบรับรองแพทย์ 5 โรค (ก.พ./สมัครงาน)
# ==========================================
def html_5disease(d):
    diseases = f"""
    <div class="field">(1) โรคเรื้อนในระยะติดต่อ หรือในระยะที่ปรากฏอาการเป็นที่รังเกียจแก่สังคม</div>
    <div class="field">(2) วัณโรคในระยะอันตราย</div>
    <div class="field">(3) โรคเท้าช้างในระยะที่ปรากฏอาการเป็นที่รังเกียจแก่สังคม</div>
    <div class="field">(4) โรคติดต่อร้ายแรงหรือโรคเรื้อรังที่ปรากฏอาการเด่นชัดหรือรุนแรงและเป็นอุปสรรคต่อการปฏิบัติหน้าที่ ตามที่ ก.พ. กำหนด</div>
    <div class="field">(5) อื่น ๆ (ถ้ามี) {_val(d['other'], '..........................')}</div>
    """
    body = f"""
    <div style="font-weight:bold; background:#eee; padding:4px 8px; display:inline-block;">ส่วนที่ 1 ของผู้ขอรับใบรับรองสุขภาพ</div>
    <div class="field" style="margin-top:8px;">ข้าพเจ้า {_val(d['name'])}</div>
    <div class="field">สถานที่อยู่ {_val(d['address'])}</div>
    <div class="field">หมายเลขบัตรประจำตัวประชาชน {_val(d['id_card'])}</div>
    <div class="field">ข้าพเจ้าขอใบรับรองสุขภาพ โดยมีประวัติสุขภาพดังนี้</div>
    {_history_html([
        ("1. โรคประจำตัว", d['h_chronic'], d['h_chronic_detail']),
        ("2. อุบัติเหตุ และ ผ่าตัด", d['h_accident'], d['h_accident_detail']),
        ("3. เคยเข้ารับการรักษาในโรงพยาบาล", d['h_admit'], d['h_admit_detail']),
        ("ประวัติอื่นที่สำคัญ", d['h_other'], d['h_other_detail']),
    ])}

    <div style="font-weight:bold; background:#eee; padding:4px 8px; display:inline-block; margin-top:15px;">ส่วนที่ 2 ของแพทย์</div>
    <div class="field" style="margin-top:8px;">สถานที่ตรวจ โรงพยาบาลโฮม ฉะเชิงเทรา</div>
    <div class="field">ข้าพเจ้า นายแพทย์/แพทย์หญิง <b>{_val(d['doctor'])}</b></div>
    <div class="field">ใบอนุญาตประกอบวิชาชีพเวชกรรมเลขที่ {_val(d['license'])}</div>
    <div class="field">ได้ตรวจร่างกาย {_val(d['name'])}</div>
    <div class="field">เมื่อวันที่ {_val(d['exam_date'])} มีรายละเอียดดังนี้</div>
    <div class="field">น้ำหนักตัว {_val(d['weight'], '......')} กก. &nbsp; ความสูง {_val(d['height'], '......')} ซม. &nbsp; ความดันโลหิต {_val(d['bp'], '............')} มม.ปรอท &nbsp; ชีพจร {_val(d['pulse'], '......')} ครั้ง/นาที</div>
    <div class="field">สภาพร่างกายทั่วไปอยู่ในเกณฑ์ <b>{_val(d['condition'], '..........')}</b></div>
    <div class="field" style="margin-top:8px;">ขอรับรองว่า บุคคลดังกล่าว ไม่เป็นผู้มีร่างกายทุพพลภาพจนไม่สามารถปฏิบัติหน้าที่ได้ ไม่ปรากฏอาการของโรคจิตหรือจิตฟั่นเฟือน หรือปัญญาอ่อน ไม่ปรากฏอาการของยาเสพติดให้โทษ และอาการของโรคพิษสุราเรื้อรัง และไม่ปรากฏอาการและอาการแสดงของโรคต่อไปนี้</div>
    {diseases}
    <div class="field" style="margin-top:8px;">สรุปความเห็นและข้อแนะนำของแพทย์ {_val(d['opinion'])}</div>
    <div class="sign">
        <div>ลงชื่อ ...................................................... แพทย์ผู้ตรวจร่างกาย</div>
        <div>( {_val(d['doctor'])} )</div>
        <div>{_val(d['license'])}</div>
    </div>
    """
    return _wrap_html("ใบรับรองแพทย์", body)


# ==========================================
# แบบที่ 3: ใบรับรองแพทย์ (ใบอนุญาตขับรถ)
# ==========================================
def html_driving(d):
    diseases = f"""
    <div class="field">(1) โรคเรื้อนในระยะติดต่อ หรือในระยะที่ปรากฏอาการเป็นที่รังเกียจแก่สังคม</div>
    <div class="field">(2) วัณโรคในระยะอันตราย</div>
    <div class="field">(3) โรคเท้าช้างในระยะที่ปรากฏอาการเป็นที่รังเกียจแก่สังคม</div>
    <div class="field">(4) อื่น ๆ (ถ้ามี) {_val(d['other'], '..........................')}</div>
    """
    body = f"""
    <div style="font-weight:bold; background:#eee; padding:4px 8px; display:inline-block;">ส่วนที่ 1 ของผู้ขอรับใบรับรองสุขภาพ</div>
    <div class="field" style="margin-top:8px;">ข้าพเจ้า {_val(d['name'])}</div>
    <div class="field">สถานที่อยู่ {_val(d['address'])}</div>
    <div class="field">หมายเลขบัตรประจำตัวประชาชน {_val(d['id_card'])}</div>
    <div class="field">ข้าพเจ้าขอใบรับรองสุขภาพ โดยมีประวัติสุขภาพดังนี้</div>
    {_history_html([
        ("1. โรคประจำตัว", d['h_chronic'], d['h_chronic_detail']),
        ("2. อุบัติเหตุ และ ผ่าตัด", d['h_accident'], d['h_accident_detail']),
        ("3. เคยเข้ารับการรักษาในโรงพยาบาล", d['h_admit'], d['h_admit_detail']),
        ("4. โรคลมชัก", d['h_epilepsy'], d['h_epilepsy_detail']),
        ("ประวัติอื่นที่สำคัญ", d['h_other'], d['h_other_detail']),
    ])}
    <div class="field" style="font-size:12px; color:#555;">* ในกรณีมีโรคลมชัก ให้แนบประวัติการรักษาจากแพทย์ผู้รักษาว่าท่านปลอดจากอาการชักมากกว่า 1 ปี เพื่ออนุญาตให้ขับรถได้</div>

    <div style="font-weight:bold; background:#eee; padding:4px 8px; display:inline-block; margin-top:15px;">ส่วนที่ 2 ของแพทย์</div>
    <div class="field" style="margin-top:8px;">สถานที่ตรวจ โรงพยาบาลโฮม ฉะเชิงเทรา</div>
    <div class="field">ข้าพเจ้า นายแพทย์/แพทย์หญิง <b>{_val(d['doctor'])}</b></div>
    <div class="field">ใบอนุญาตประกอบวิชาชีพเวชกรรมเลขที่ {_val(d['license'])}</div>
    <div class="field">ได้ตรวจร่างกาย {_val(d['name'])} เมื่อวันที่ {_val(d['exam_date'])} มีรายละเอียดดังนี้</div>
    <div class="field">น้ำหนักตัว {_val(d['weight'], '......')} กก. &nbsp; ความสูง {_val(d['height'], '......')} ซม. &nbsp; ความดันโลหิต {_val(d['bp'], '............')} มม.ปรอท &nbsp; ชีพจร {_val(d['pulse'], '......')} ครั้ง/นาที</div>
    <div class="field">สภาพร่างกายทั่วไปอยู่ในเกณฑ์ <b>{_val(d['condition'], '..........')}</b></div>
    <div class="field" style="margin-top:8px;">ขอรับรองว่า บุคคลดังกล่าว ไม่เป็นผู้มีร่างกายทุพพลภาพจนไม่สามารถปฏิบัติหน้าที่ได้ ไม่ปรากฏอาการของโรคจิตหรือจิตฟั่นเฟือน หรือปัญญาอ่อน ไม่ปรากฏอาการของยาเสพติดให้โทษ และอาการของโรคพิษสุราเรื้อรัง และไม่ปรากฏอาการและอาการแสดงของโรคต่อไปนี้</div>
    {diseases}
    <div class="field" style="margin-top:8px;">สรุปความเห็นและข้อแนะนำของแพทย์ {_val(d['opinion'])}</div>
    <div class="sign">
        <div>ลงชื่อ ...................................................... แพทย์ผู้ตรวจร่างกาย</div>
        <div>( {_val(d['doctor'])} )</div>
        <div>{_val(d['license'])}</div>
    </div>
    """
    return _wrap_html("ใบรับรองแพทย์ทำใบขับขี่", body)


# ==========================================
# หน้าจอ UI
# ==========================================
st.title("📄 ระบบออกใบรับรองแพทย์ รพ.โฮม")

st.warning("⚕️ ส่วนวินิจฉัยและความเห็นแพทย์ ต้องให้แพทย์ตรวจและกรอกเอง ระบบเป็นเพียงตัวจัดรูปแบบเอกสารเพื่อพิมพ์")

cert_type = st.selectbox(
    "เลือกประเภทใบรับรองแพทย์",
    ["ใบรับรองแพทย์ทั่วไป", "ใบรับรองแพทย์ 5 โรค (ก.พ./สมัครงาน)", "ใบรับรองแพทย์ทำใบขับขี่"],
)

st.divider()

# --- ข้อมูลผู้ป่วย (ทุกแบบใช้ร่วม) ---
st.markdown("### 1️⃣ ข้อมูลผู้ป่วย")
c1, c2 = st.columns(2)
with c1:
    name = st.text_input("ชื่อ-นามสกุล", placeholder="เช่น นางสมหญิง ใจดี")
    id_card = st.text_input("เลขบัตรประจำตัวประชาชน", placeholder="x-xxxx-xxxxx-xx-x")
with c2:
    age = st.text_input("อายุ (ปี)", placeholder="เช่น 35")
    address = st.text_input("ที่อยู่", placeholder="ที่อยู่ที่ติดต่อได้")

st.divider()

# --- ข้อมูลแพทย์ (ทุกแบบใช้ร่วม) ---
st.markdown("### 2️⃣ ข้อมูลแพทย์ผู้ตรวจ")
d1, d2 = st.columns(2)
with d1:
    doctor = st.text_input("แพทย์ผู้ตรวจ", value=DEFAULT_DOCTOR)
with d2:
    license_no = st.text_input("เลขใบอนุญาต", value=DEFAULT_LICENSE)
place = st.text_input("สถานที่ปฏิบัติงาน", value=DEFAULT_PLACE)

st.divider()

# --- ข้อมูลเฉพาะแต่ละแบบ ---
st.markdown("### 3️⃣ รายละเอียดการตรวจ")

data = {
    "name": name, "id_card": id_card, "age": age, "address": address,
    "doctor": doctor, "license": license_no, "place": place,
}

if cert_type == "ใบรับรองแพทย์ทั่วไป":
    today_thai = format_thai_date(datetime.today())
    g1, g2 = st.columns(2)
    with g1:
        data["visit_date"] = st.text_input("วันที่มารับบริการ", value=today_thai)
        data["issue_date"] = st.text_input("วันที่ออกใบรับรอง", value=today_thai)
    with g2:
        data["visit_time"] = st.text_input("เวลา (น.)", placeholder="เช่น 10.30")
    data["diagnosis"] = st.text_area("วินิจฉัยโรค (แพทย์กรอก)", placeholder="เช่น ร่างกายปกติแข็งแรงดี")
    data["opinion"] = st.text_area("สรุปความเห็น (แพทย์กรอก)", placeholder="ความเห็นแพทย์")
    generator = html_general

else:
    # แบบ 5 โรค และ ขับรถ ใช้ฟิลด์เดียวกันส่วนใหญ่
    today_thai = format_thai_date(datetime.today())
    data["exam_date"] = st.text_input("วันที่ตรวจร่างกาย", value=today_thai)

    st.markdown("**ประวัติสุขภาพ (ส่วนที่ 1)**")
    h1, h2 = st.columns(2)
    with h1:
        data["h_chronic"] = st.radio("1. โรคประจำตัว", ["ไม่มี", "มี"], horizontal=True, key="hc")
        data["h_accident"] = st.radio("2. อุบัติเหตุ และ ผ่าตัด", ["ไม่มี", "มี"], horizontal=True, key="ha")
        data["h_admit"] = st.radio("3. เคยเข้ารับการรักษาใน รพ.", ["ไม่มี", "มี"], horizontal=True, key="had")
    with h2:
        data["h_chronic_detail"] = st.text_input("ระบุ (โรคประจำตัว)", key="hcd")
        data["h_accident_detail"] = st.text_input("ระบุ (อุบัติเหตุ/ผ่าตัด)", key="had2")
        data["h_admit_detail"] = st.text_input("ระบุ (เคยรักษา)", key="hadd")

    if cert_type == "ใบรับรองแพทย์ทำใบขับขี่":
        e1, e2 = st.columns(2)
        with e1:
            data["h_epilepsy"] = st.radio("4. โรคลมชัก", ["ไม่มี", "มี"], horizontal=True, key="he")
        with e2:
            data["h_epilepsy_detail"] = st.text_input("ระบุ (โรคลมชัก)", key="hed")

    o1, o2 = st.columns(2)
    with o1:
        data["h_other"] = st.radio("ประวัติอื่นที่สำคัญ", ["ไม่มี", "มี"], horizontal=True, key="ho")
    with o2:
        data["h_other_detail"] = st.text_input("ระบุ (ประวัติอื่น)", key="hod")

    st.markdown("**ผลตรวจร่างกาย (ส่วนที่ 2 — แพทย์กรอก)**")
    v1, v2, v3, v4 = st.columns(4)
    with v1:
        data["weight"] = st.text_input("น้ำหนัก (กก.)")
    with v2:
        data["height"] = st.text_input("ส่วนสูง (ซม.)")
    with v3:
        data["bp"] = st.text_input("ความดัน (มม.ปรอท)")
    with v4:
        data["pulse"] = st.text_input("ชีพจร (ครั้ง/นาที)")
    data["condition"] = st.radio("สภาพร่างกายทั่วไป", ["ปกติ", "ผิดปกติ"], horizontal=True)
    data["other"] = st.text_input("โรคอื่น ๆ (ถ้ามี)")
    data["opinion"] = st.text_area("สรุปความเห็นและข้อแนะนำของแพทย์")

    generator = html_5disease if "5 โรค" in cert_type else html_driving

st.divider()

if st.button("✨ สร้างหน้าพรีวิวสำหรับปริ้นใบรับรองแพทย์", type="primary", width="stretch"):
    if not name.strip():
        st.error("⚠️ กรุณากรอกชื่อ-นามสกุลผู้ป่วยก่อนครับ")
    else:
        b64 = generator(data)
        st.markdown(
            f'<iframe src="data:text/html;base64,{b64}" width="100%" height="900" style="border:none;"></iframe>',
            unsafe_allow_html=True,
        )
