import streamlit as st
import openpyxl
from io import BytesIO
import base64
from datetime import datetime
import pandas as pd
import re

# ==========================================
# 0. ตั้งค่าและซ่อนเมนู Streamlit
# ==========================================
st.set_page_config(page_title="ระบบจัดการ รพ.โฮม", page_icon="🏥", layout="wide")

hide_streamlit_style = """
<style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container { padding-top: 1rem; padding-bottom: 0rem; }
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ==========================================
# 1. ฟังก์ชันพื้นฐาน & ตัวแปลงเงินบาท
# ==========================================
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    except Exception:
        return "" 

def format_thai_date(date_obj):
    if not date_obj: return ""
    thai_months = ["", "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
    return f"{date_obj.day} {thai_months[date_obj.month]} {date_obj.year + 543}"

def get_baht_text(number):
    """แปลงตัวเลขเป็นคำอ่านภาษาไทย"""
    number = round(float(number), 2)
    if number == 0: return "ศูนย์บาทถ้วน"
    num_str = f"{number:,.2f}".replace(",", "")
    int_part, dec_part = num_str.split('.')
    digits = ["", "หนึ่ง", "สอง", "สาม", "สี่", "ห้า", "หก", "เจ็ด", "แปด", "เก้า"]
    positions = ["", "สิบ", "ร้อย", "พัน", "หมื่น", "แสน", "ล้าน"]
    
    def read_num(n_str):
        res = ""
        length = len(n_str)
        for i, digit in enumerate(n_str):
            d = int(digit)
            pos = length - i - 1
            if d == 0: continue
            if pos == 0 and d == 1 and length > 1: res += "เอ็ด"
            elif pos == 1 and d == 1: res += "สิบ"
            elif pos == 1 and d == 2: res += "ยี่สิบ"
            else: res += digits[d] + positions[pos]
        return res
        
    text = read_num(int_part) + "บาท"
    if dec_part == "00": text += "ถ้วน"
    else: text += read_num(dec_part) + "สตางค์"
    return f"({text})"

# ==========================================
# 2. 🤖 ฟังก์ชันสกัดข้อมูลจากไฟล์ดิบ (Data Extraction)
# ==========================================
def extract_raw_receipt(uploaded_file):
    """อ่านไฟล์ Excel ดิบ และดึงข้อมูลรายการทั้งหมดออกมา"""
    wb = openpyxl.load_workbook(uploaded_file, data_only=True)
    ws = wb.active
    
    data = {
        "name": "", "receipt_no": "", "address": "", "date": "", "items": []
    }
    
    # 1. ค้นหาข้อมูลส่วนหัว (ค้นหาแบบกวาดทุกเซลล์ใน 10 แถวแรก เพื่อความชัวร์)
    for row in range(1, 11):
        for col in range(1, 15):
            val = str(ws.cell(row=row, column=col).value or "").strip()
            if "ชื่อผู้ป่วย" in val:
                data["name"] = val.replace("ชื่อผู้ป่วย", "").strip()
            elif "เลขที่" in val and "ประจำตัว" not in val: # ดักไว้ไม่ให้ซ้ำกับเลขผู้เสียภาษี
                data["receipt_no"] = val.replace("เลขที่", "").strip()
            
            # ที่อยู่มักจะอยู่ใต้ชื่อ (ดูจากรูปคือแถว 7 คอลัมน์ C)
            if row == 7 and col == 3 and val != "None":
                data["address"] = val
            # วันที่มักจะอยู่แถว 7 ด้านขวา
            if row == 7 and col > 5 and "256" in val:
                data["date"] = val

    # 2. ค้นหารายการยาและค่ารักษา (เริ่มสแกนตั้งแต่แถวที่ 10 ลงไป)
    for row in range(10, 50): # สมมติว่ารายการไม่เกิน 40 บรรทัด
        # คอลัมน์ B คือ ลำดับที่
        item_no = str(ws.cell(row=row, column=2).value or "").strip()
        
        # ถ้าพบลำดับที่เป็นตัวเลข แสดงว่าเป็นบรรทัดรายการ
        if item_no.isdigit():
            # คอลัมน์ C คือ ชื่อรายการ
            item_name = str(ws.cell(row=row, column=3).value or "").strip()
            
            # ค้นหาราคา (เพราะโปรแกรมอาจ Merge cell ไว้ที่คอลัมน์ I, J หรือ K)
            item_price = 0.0
            for col_price in range(8, 15):
                price_val = ws.cell(row=row, column=col_price).value
                if isinstance(price_val, (int, float)):
                    item_price = float(price_val)
                    break
            
            if item_name and item_name != "None":
                data["items"].append({"รายการ": item_name, "ราคา": item_price})
                
    return data

# ==========================================
# 3. ฟังก์ชัน HTML สำหรับสั่งปริ้น (ตัดมาเฉพาะบัตรนัดและใบเสร็จให้สั้นลง)
# ==========================================
brand_green = "#2C5E3B"
brand_brown = "#8B5A2B"
logo_base64 = get_base64_image("logo.png")

def generate_appt_html(data):
    html = f"""<!DOCTYPE html><html lang="th"><head><meta charset="UTF-8"><style>
        * {{ -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }}
        body {{ font-family: 'Tahoma', sans-serif; color: #333; }}
        .card {{ max-width: 600px; margin: 0 auto; border: 1px solid #ddd; padding-bottom: 20px; background-color: white; }}
        .header {{ border-bottom: 2px solid {brand_green}; padding: 15px; display: flex; align-items: center; justify-content: center; margin-bottom: 15px; }}
        .logo {{ width: 60px; margin-right: 15px; }}
        .title {{ font-size: 20px; font-weight: bold; margin: 0; color: {brand_green}; }}
        .subtitle {{ font-size: 14px; margin: 0; color: #555; }}
        .content {{ padding: 0 20px; }}
        .row {{ display: flex; justify-content: space-between; margin-bottom: 10px; }}
        .print-btn {{ background-color: {brand_green}; color: white; border: none; padding: 10px; cursor: pointer; width: 100%; font-size: 16px; margin-bottom: 10px; }}
        @media print {{ .no-print {{ display: none !important; }} .card {{ border: none; }} }}
    </style></head><body>
        <button class="no-print print-btn" onclick="window.print()">🖨️ ปริ้นบัตรนัด</button>
        <div class="card">
            <div class="header"><img src="data:image/png;base64,{logo_base64}" class="logo">
            <div><p class="title">โรงพยาบาลโฮม ฉะเชิงเทรา</p><p class="subtitle">บัตรนัดหมาย | Appointment Card</p></div></div>
            <div class="content">
                <div class="row"><div><b>ชื่อ:</b> {data['name']}</div><div><b>HN:</b> {data['hn']}</div></div>
                <hr>
                <div class="row"><div style="color:{brand_green}; font-weight:bold;">วันที่นัด: {data['appt_date_th']}</div>
                <div style="color:{brand_green}; font-weight:bold;">เวลา: {data['appt_time']}</div></div>
                <div class="row"><div><b>แพทย์:</b> {data['doctor']}</div><div><b>รายการ:</b> {data['action']}</div></div>
                <p style="color:{brand_brown}; font-weight:bold;">📌 คำแนะนำ: <span style="color:#333; font-weight:normal;">{data['instruction']}</span></p>
                <p style="text-align:center; font-size:12px; margin-top:20px;">โทร 038-511-123 (กรุณานำยาเดิมมาด้วยทุกครั้ง)</p>
            </div>
        </div>
    </body></html>"""
    return base64.b64encode(html.encode('utf-8')).decode('utf-8')

def generate_receipt_html(data):
    items_html = ""
    for i, row in enumerate(data['items']):
        item_name = str(row.get('รายการ', '')).strip()
        item_price = row.get('ราคา', 0.0)
        if item_name and not pd.isna(item_name):
            items_html += f"<tr><td style='text-align:left;'>{i+1}</td><td style='text-align:left;'>{item_name}</td><td style='text-align:right;'>{item_price:,.2f}</td></tr>"

    html = f"""<!DOCTYPE html><html lang="th"><head><meta charset="UTF-8"><style>
        body {{ font-family: 'Tahoma', sans-serif; color: #333; font-size: 14px; margin: 0; padding: 10px; }}
        .card {{ max-width: 800px; margin: 0 auto; padding: 20px; background-color: white; }}
        .header-container {{ position: relative; text-align: center; margin-bottom: 30px; }}
        .logo {{ position: absolute; left: 0; top: 0; width: 60px; }}
        .header-text {{ margin-left: 70px; }}
        .title {{ font-size: 18px; font-weight: bold; margin-bottom: 5px; }}
        .subtitle {{ font-size: 12px; margin-bottom: 2px; }}
        .info-row {{ display: flex; justify-content: space-between; margin-bottom: 5px; font-size: 13px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; margin-bottom: 15px; }}
        th, td {{ padding: 8px 5px; }}
        th {{ border-top: 1px solid #000; border-bottom: 1px solid #000; text-align: left; font-weight: bold; }}
        .total-row td {{ border-top: 1px solid #000; border-bottom: 1px solid #000; padding: 15px 5px; }}
        .footer-container {{ display: flex; justify-content: space-between; font-size: 11px; color: #555; margin-top: 50px; }}
        .print-btn {{ background-color: {brand_green}; color: white; border: none; padding: 10px; cursor: pointer; width: 100%; font-size: 16px; margin-bottom: 20px; font-weight:bold; }}
        @media print {{ body {{ padding: 0; }} .no-print {{ display: none !important; }} }}
    </style></head><body>
        <button class="no-print print-btn" onclick="window.print()">🖨️ ปริ้นใบเสร็จรับเงิน</button>
        <div class="card">
            <div class="header-container">
                <img src="data:image/png;base64,{logo_base64}" class="logo">
                <div class="header-text">
                    <div class="title">ใบเสร็จรับเงิน โรงพยาบาลโฮม ฉะเชิงเทรา</div>
                    <div class="subtitle">149/1 ถ.ฉะเชิงเทรา-บางปะกง ต.หน้าเมือง อ.เมือง จ.ฉะเชิงเทรา โทร 038-511-123</div>
                    <div class="subtitle">เลขประจำตัวผู้เสียภาษีอากร 0245563001367</div>
                </div>
            </div>
            <div class="info-row"><div>ชื่อผู้ป่วย <b>{data['name']}</b></div><div>เลขที่ {data['receipt_no']}</div></div>
            <div class="info-row"><div>{data['address']}</div><div>{data['date']}</div></div>
            <table>
                <tr><th style="width: 10%;">ลำดับที่</th><th style="width: 70%;">รายการ</th><th style="width: 20%; text-align:right;">ราคา</th></tr>
                {items_html}
                <tr class="total-row"><td colspan="2"><b>{data['baht_text']}</b></td><td style="text-align:right;"><b>{data['total']:,.2f}</b></td></tr>
            </table>
            <div class="info-row" style="margin-top: 20px;">
                <div><b>ชำระโดย : {data['payment_method']}</b></div>
                <div style="text-align: center; width: 300px;"><p>(........................................................)</p><p><b>{data['receiver']}</b><br>ผู้รับเงิน</p></div>
            </div>
            <div class="footer-container">
                <div><b>โรงพยาบาลโฮม ฉะเชิงเทรา</b><br>149/1 ถ.ฉะเชิงเทรา-บางปะกง ต.หน้าเมือง อ.เมือง จ.ฉะเชิงเทรา 24000<br>Tel. 038-511-123 | E-mail: Hospitalashome@gmail.com<br>Facebook: โรงพยาบาลโฮม ฉะเชิงเทรา</div>
                <div style="text-align: right;"><b>บริษัท สื่อ การแพทย์ จำกัด</b><br>149/1 ถ.ฉะเชิงเทรา-บางปะกง ต.หน้าเมือง<br>อ.เมือง จ.ฉะเชิงเทรา 24000<br>เลขประจำตัวผู้เสียภาษีอากร 0245563001367</div>
            </div>
        </div>
    </body></html>"""
    return base64.b64encode(html.encode('utf-8')).decode('utf-8')

# ==========================================
# 4. หน้าจอ UI (Streamlit)
# ==========================================
st.title("🏥 ระบบให้บริการ รพ.โฮม")
st.markdown("**ข้อมูลผู้ป่วย (พิมพ์เอง หรือดึงอัตโนมัติจากการอัปโหลดใบเสร็จ)**")

col_name, col_hn = st.columns(2)
with col_name: 
    patient_name = st.text_input("👤 ชื่อ-นามสกุลผู้ป่วย", key="ui_name", placeholder="เช่น พระ กฤษณพงษ์ เปรมเจริญ")
with col_hn: 
    cn_number = st.text_input("🆔 รหัสคนไข้ (HN / CN)", key="ui_hn", placeholder="เช่น 0007256")

st.divider()

tab1, tab2 = st.tabs(["🧾 ออกใบเสร็จรับเงิน (ดึงข้อมูลอัตโนมัติ)", "🏥 ออกบัตรนัด"])

# ------------------------------------
# แท็บ 1: ใบเสร็จรับเงิน (Automation)
# ------------------------------------
with tab1:
    st.subheader("🧾 ดึงข้อมูลจากไฟล์ดิบ (Excel)")
    
    # 1. ส่วนอัปโหลดไฟล์
    uploaded_receipt = st.file_uploader("📂 อัปโหลดไฟล์ใบเสร็จจากโปรแกรมหลัก (Excel)", type=["xlsx", "xls"])
    
    # ตั้งค่าตัวแปรเริ่มต้น (Default Values)
    def_receipt_no = "0000000000"
    def_address = "ไม่ระบุที่อยู่"
    def_date = format_thai_date(datetime.today())
    
    default_items = pd.DataFrame([
        {"รายการ": "ค่าตรวจแพทย์ทั่วไป", "ราคา": 500.00},
        {"รายการ": "", "ราคา": 0.00}
    ])
    
    # 2. ถ้ามีการอัปโหลดไฟล์ ให้ดึงข้อมูลมาทับค่า Default ทันที!
    if uploaded_receipt:
        try:
            extracted_data = extract_raw_receipt(uploaded_receipt)
            st.success(f"✅ ดึงข้อมูลสำเร็จ! พบรายการทั้งหมด {len(extracted_data['items'])} รายการ")
            
            # อัปเดตข้อมูลที่ดึงได้
            if extracted_data["name"]: st.info(f"👤 พบชื่อผู้ป่วย: {extracted_data['name']}")
            if extracted_data["receipt_no"]: def_receipt_no = extracted_data["receipt_no"]
            if extracted_data["address"]: def_address = extracted_data["address"]
            if extracted_data["date"]: def_date = extracted_data["date"]
            
            # แปลงรายการยาเป็น DataFrame เพื่อใส่ตาราง
            if len(extracted_data["items"]) > 0:
                default_items = pd.DataFrame(extracted_data["items"])
        except Exception as e:
            st.error(f"❌ เกิดข้อผิดพลาดในการอ่านไฟล์: {e}")

    st.divider()
    
    # 3. ส่วนแสดงฟอร์มให้ตรวจสอบ/แก้ไข
    col_rc1, col_rc2 = st.columns(2)
    with col_rc1:
        receipt_no = st.text_input("เลขที่ใบเสร็จ", value=def_receipt_no)
        address = st.text_area("ที่อยู่ผู้ป่วย", value=def_address, height=68)
    with col_rc2:
        receipt_date_str = st.text_input("วันที่ออกใบเสร็จ", value=def_date)
        payment_method = st.selectbox("ชำระโดย", ["โอนจ่าย", "เงินสด", "บัตรเครดิต"])
        receiver_name = st.text_input("ชื่อผู้รับเงิน", value="นาย มรดก มาลี")
        
    st.write("**📝 ตารางรายการค่ารักษา (ตรวจสอบและแก้ไขได้)**")
    
    # แสดงตารางให้เจ้าหน้าที่ดู (สามารถพิมพ์แก้ไขราคา หรือลบแถวได้)
    edited_df = st.data_editor(
        default_items,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "รายการ": st.column_config.TextColumn("ชื่อรายการ", width="large", required=True),
            "ราคา": st.column_config.NumberColumn("ราคา (บาท)", min_value=0.0, format="%.2f")
        }
    )
    
    # คำนวณยอดรวมอัตโนมัติจากตาราง
    total_fee = edited_df['ราคา'].sum()
    st.info(f"**💰 รวมเงินทั้งสิ้น: {total_fee:,.2f} บาท** 👉 {get_baht_text(total_fee)}")

    if st.button("✨ ปริ้นใบเสร็จรับเงิน", type="primary", use_container_width=True):
        # ถ้าระบบดึงชื่อได้จากไฟล์ Excel ให้ใช้ชื่อนั้น แต่ถ้าไม่มีให้ใช้ที่กรอกด้านบน
        final_name = extracted_data['name'] if uploaded_receipt and extracted_data.get('name') else patient_name
        
        if not final_name:
            st.error("⚠️ ไม่พบชื่อผู้ป่วย กรุณากรอกชื่อด้านบน หรืออัปโหลดไฟล์ที่มีชื่อครับ")
        else:
            items_list = edited_df.to_dict('records')
            data_rec = {
                "name": final_name, 
                "hn": cn_number, # ไฟล์ใบเสร็จดิบไม่มี HN ต้องให้เจ้าหน้าที่กรอกเองด้านบน
                "address": address.strip(),
                "receipt_no": receipt_no,
                "date": receipt_date_str,
                "payment_method": payment_method,
                "receiver": receiver_name,
                "items": items_list,
                "total": total_fee,
                "baht_text": get_baht_text(total_fee)
            }
            iframe_code = f'<iframe src="data:text/html;base64,{generate_receipt_html(data_rec)}" width="100%" height="800" style="border:none;"></iframe>'
            st.markdown(iframe_code, unsafe_allow_html=True)


# ------------------------------------
# แท็บ 2: บัตรนัด
# ------------------------------------
with tab2:
    st.subheader("รายละเอียดการนัดหมาย")
    appt_type = st.radio("ประเภท", ["มาติดตามอาการ", "มาเจาะเลือด"], horizontal=True)
    col_d, col_t = st.columns(2)
    with col_d:
        date_sel = st.date_input("วันที่นัด", value=datetime.today())
        date_th = format_thai_date(date_sel)
    with col_t: time_sel = st.selectbox("เวลานัด", ["08.00 - 10.00 น.", "10.00 - 12.00 น.", "13.00 - 15.00 น.", "15.00 - 16.30 น."])
    
    col_doc, col_act = st.columns(2)
    with col_doc: doc_appt = st.text_input("แพทย์ผู้ตรวจ (บัตรนัด)", value="นพ.อภิสิทธิ์ สื่อประเสริฐสิทธิ์")
    with col_act: act_appt = st.text_input("รายการตรวจ", value="ตรวจติดตามอาการทั่วไป" if appt_type == "มาติดตามอาการ" else "เจาะเลือด ตรวจสุขภาพ")
    ins_appt = st.text_input("คำแนะนำ", value="รับประทานยาและปฏิบัติตัวตามแพทย์สั่ง" if appt_type == "มาติดตามอาการ" else "งดน้ำ-งดอาหาร 6-8 ชั่วโมงก่อนตรวจ")

    if st.button("✨ ปริ้นบัตรนัด", type="primary", use_container_width=True):
        if not patient_name or not cn_number: st.error("กรุณากรอกชื่อและ HN ด้านบนก่อนครับ")
        else:
            data_appt = {"name": patient_name, "hn": cn_number, "type": appt_type, "appt_date_th": date_th, "appt_time": time_sel, "doctor": doc_appt, "action": act_appt, "instruction": ins_appt}
            st.markdown(f'<iframe src="data:text/html;base64,{generate_appt_html(data_appt)}" width="100%" height="500" style="border:none;"></iframe>', unsafe_allow_html=True)
