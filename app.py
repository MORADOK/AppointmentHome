import streamlit as st
import openpyxl
from io import BytesIO
import base64
import pandas as pd
from datetime import datetime

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

def get_baht_text(number):
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

def format_thai_date(date_obj):
    if not date_obj: return ""
    thai_months = ["", "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
    return f"{date_obj.day} {thai_months[date_obj.month]} {date_obj.year + 543}"

# ==========================================
# 2. 🤖 ฟังก์ชันสกัดข้อมูลใบเสร็จ (Data Extraction)
# ==========================================
def extract_raw_receipt(uploaded_file):
    wb = openpyxl.load_workbook(uploaded_file, data_only=True)
    ws = wb.active
    
    data = {"name": "", "receipt_no": "", "address": "", "date": "", "items": []}
    
    def val(r, c):
        v = ws.cell(row=r, column=c).value
        return str(v).strip() if v is not None else ""

    for r in range(1, 15):
        row_vals = [val(r, c) for c in range(1, 20)]
        row_str = " ".join(row_vals)
        
        if "ชื่อผู้ป่วย" in row_str and not data["name"]:
            for v in row_vals:
                if "ชื่อผู้ป่วย" in v:
                    data["name"] = v.replace("ชื่อผู้ป่วย", "").replace(":", "").strip()
        
        if "เลขที่" in row_str and "เสียภาษี" not in row_str and not data["receipt_no"]:
            for v in row_vals:
                if "เลขที่" in v:
                    data["receipt_no"] = v.replace("เลขที่", "").replace(":", "").strip()
        
        thai_months = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
        if not data["date"]:
            for v in row_vals:
                if any(m in v for m in thai_months) and "256" in v:
                    data["date"] = v
                    
        if not data["address"]:
            for v in row_vals:
                if ("ต." in v and "อ." in v) or ("ถ." in v) or ("จ." in v):
                    if "โรงพยาบาล" not in v:
                        data["address"] = v

    for r in range(5, 50):
        cell_B = val(r, 2)
        cell_A = val(r, 1)
        item_no = cell_B if cell_B.isdigit() else cell_A
        
        if item_no.isdigit():
            item_name = ""
            for c in range(2, 10):
                v = val(r, c)
                if v and not v.isdigit() and v != "None":
                    item_name = v
                    break
            
            item_price = 0.0
            for c in range(20, 2, -1):
                v_raw = ws.cell(row=r, column=c).value
                if isinstance(v_raw, (int, float)):
                    item_price = float(v_raw)
                    break
                elif isinstance(v_raw, str):
                    try:
                        clean_val = v_raw.replace(",", "")
                        item_price = float(clean_val)
                        if item_price > 0: break
                    except:
                        pass
            
            if item_name:
                data["items"].append({"รายการ": item_name, "ราคา": item_price})

    return data

# ==========================================
# 3. ฟังก์ชัน HTML สำหรับสั่งปริ้น 
# ==========================================
brand_green = "#2C5E3B"
brand_brown = "#8B5A2B"
logo_base64 = get_base64_image("logo.png")

def generate_receipt_html(data):
    items_html = ""
    for i, row in enumerate(data['items']):
        item_name = str(row.get('รายการ', '')).strip()
        item_price = row.get('ราคา', 0.0)
        if item_name:
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
                <div><b>โรงพยาบาลโฮม ฉะเชิงเทรา</b><br>149/1 ถ.ฉะเชิงเทรา-บางปะกง ต.หน้าเมือง อ.เมือง จ.ฉะเชิงเทรา 24000<br>Tel. 038-511-123 | E-mail: Hospitalashome@gmail.com</div>
                <div style="text-align: right;"><b>บริษัท สื่อ การแพทย์ จำกัด</b><br>149/1 ถ.ฉะเชิงเทรา-บางปะกง ต.หน้าเมือง<br>อ.เมือง จ.ฉะเชิงเทรา 24000<br>เลขประจำตัวผู้เสียภาษีอากร 0245563001367</div>
            </div>
        </div>
    </body></html>"""
    return base64.b64encode(html.encode('utf-8')).decode('utf-8')

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
                <div class="row"><div style="color:{brand_green}; font-weight:bold;">วันที่นัด: {data['appt_date']}</div>
                <div style="color:{brand_green}; font-weight:bold;">เวลา: {data['appt_time']}</div></div>
                <div class="row"><div><b>แพทย์:</b> {data['doctor']}</div><div><b>รายการ:</b> {data['action']}</div></div>
                <p style="color:{brand_brown}; font-weight:bold;">📌 คำแนะนำ: <span style="color:#333; font-weight:normal;">{data['instruction']}</span></p>
                <p style="text-align:center; font-size:12px; margin-top:20px;">โทร 038-511-123 (กรุณานำยาเดิมมาด้วยทุกครั้ง)</p>
            </div>
        </div>
    </body></html>"""
    return base64.b64encode(html.encode('utf-8')).decode('utf-8')

# ==========================================
# 4. หน้าจอ UI (Streamlit)
# ==========================================
st.title("🏥 ระบบให้บริการ รพ.โฮม")
st.write("เลือกระบบที่ต้องการใช้งานจากแท็บด้านล่าง")
st.divider()

# แยกระบบด้วยแท็บอย่างชัดเจน
tab1, tab2 = st.tabs(["🧾 ออกใบเสร็จรับเงิน (ดึงข้อมูลอัตโนมัติ)", "🏥 ออกบัตรนัดหมาย (กรอกข้อมูลเอง)"])

# ------------------------------------
# แท็บ 1: ใบเสร็จรับเงิน (ดึงจากไฟล์ 100%)
# ------------------------------------
with tab1:
    st.markdown("### 1️⃣ อัปโหลดไฟล์ใบเสร็จ (Excel)")
    uploaded_receipt = st.file_uploader("ลากไฟล์ Excel ใบเสร็จมาวางที่นี่...", type=["xlsx", "xls"], key="receipt_upload")
    
    ex_data = {"name": "", "receipt_no": "", "address": "", "date": "ไม่ระบุวันที่", "items": []}
    
    if uploaded_receipt:
        try:
            ex_data = extract_raw_receipt(uploaded_receipt)
            st.success(f"✅ ดึงข้อมูลสำเร็จ! พบชื่อ: {ex_data['name']} | วันที่: {ex_data['date']} | พบรายการทั้งหมด {len(ex_data['items'])} รายการ")
        except Exception as e:
            st.error(f"❌ อ่านไฟล์ผิดพลาด: {e}")

    st.markdown("### 2️⃣ ข้อมูลผู้รับเงิน")
    col_rc1, col_rc2 = st.columns(2)
    with col_rc1:
        receiver_name = st.text_input("👤 ชื่อผู้รับเงิน (พนักงาน)", value="นาย มรดก มาลี")
    with col_rc2:
        payment_method = st.selectbox("💳 วิธีการชำระเงิน", ["โอนจ่าย", "เงินสด", "บัตรเครดิต"])
        
    st.write("**ตารางรายการ (ตรวจสอบและแก้ไขราคาได้)**")
    df_items = pd.DataFrame(ex_data["items"]) if ex_data["items"] else pd.DataFrame([{"รายการ": "ไม่มีข้อมูล (กรุณาอัปโหลดไฟล์)", "ราคา": 0.0}])
    
    edited_df = st.data_editor(
        df_items,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "รายการ": st.column_config.TextColumn("ชื่อรายการ", width="large", required=True),
            "ราคา": st.column_config.NumberColumn("ราคา (บาท)", min_value=0.0, format="%.2f")
        }
    )
    
    total_fee = edited_df['ราคา'].sum()
    st.info(f"**💰 รวมเงินทั้งสิ้น: {total_fee:,.2f} บาท** 👉 {get_baht_text(total_fee)}")

    if st.button("✨ สร้างใบเสร็จรับเงิน", type="primary", use_container_width=True):
        if not ex_data['name']:
            st.error("⚠️ กรุณาอัปโหลดไฟล์ Excel ก่อนเพื่อดึงข้อมูลใบเสร็จครับ")
        else:
            data_rec = {
                "name": ex_data["name"], 
                "address": ex_data["address"],
                "receipt_no": ex_data["receipt_no"],
                "date": ex_data["date"], 
                "payment_method": payment_method,
                "receiver": receiver_name,
                "items": edited_df.to_dict('records'),
                "total": total_fee,
                "baht_text": get_baht_text(total_fee)
            }
            iframe_code = f'<iframe src="data:text/html;base64,{generate_receipt_html(data_rec)}" width="100%" height="800" style="border:none;"></iframe>'
            st.markdown(iframe_code, unsafe_allow_html=True)


# ------------------------------------
# แท็บ 2: บัตรนัด (กรอกเองเหมือนเดิม 100%)
# ------------------------------------
with tab2:
    st.markdown("### 1️⃣ ข้อมูลคนไข้")
    col_name, col_hn = st.columns(2)
    with col_name: 
        # ให้กรอกเองเหมือนระบบดั้งเดิม
        appt_name = st.text_input("👤 ชื่อ-นามสกุล", placeholder="เช่น นาย ธนายุทธ วิทยาประเสริฐ")
    with col_hn: 
        appt_hn = st.text_input("🆔 รหัสคนไข้ (HN / CN)", placeholder="เช่น 0007234")
        
    st.markdown("### 2️⃣ รายละเอียดการนัดหมาย")
    appt_type = st.radio("ประเภทนัดหมาย", ["มาติดตามอาการ", "มาเจาะเลือด"], horizontal=True)
    
    col_t1, col_t2 = st.columns(2)
    with col_t1: 
        date_sel = st.date_input("วันที่นัด", value=datetime.today())
        date_th = format_thai_date(date_sel)
    with col_t2: 
        time_sel = st.selectbox("เวลานัด", ["08.00 - 10.00 น.", "10.00 - 12.00 น.", "13.00 - 15.00 น.", "15.00 - 16.30 น."])
    
    col_d1, col_d2 = st.columns(2)
    with col_d1: doc_appt = st.text_input("แพทย์ผู้ตรวจ", value="นพ.อภิสิทธิ์ สื่อประเสริฐสิทธิ์")
    with col_d2: act_appt = st.text_input("รายการตรวจ", value="ตรวจติดตามอาการทั่วไป" if appt_type == "มาติดตามอาการ" else "เจาะเลือด ตรวจสุขภาพ")
    ins_appt = st.text_input("คำแนะนำ", value="รับประทานยาและปฏิบัติตัวตามแพทย์สั่ง" if appt_type == "มาติดตามอาการ" else "งดน้ำ-งดอาหาร 6-8 ชั่วโมงก่อนตรวจ")

    if st.button("✨ สร้างบัตรนัด", type="primary", use_container_width=True):
        if not appt_name or not appt_hn:
            st.warning("⚠️ กรุณากรอก 'ชื่อ-นามสกุล' และ 'HN' ก่อนกดสร้างบัตรนัดครับ")
        else:
            data_appt = {
                "name": appt_name.strip(), 
                "hn": appt_hn.strip(), 
                "type": appt_type, 
                "appt_date": date_th, 
                "appt_time": time_sel, 
                "doctor": doc_appt.strip(), 
                "action": act_appt.strip(), 
                "instruction": ins_appt.strip()
            }
            st.markdown(f'<iframe src="data:text/html;base64,{generate_appt_html(data_appt)}" width="100%" height="500" style="border:none;"></iframe>', unsafe_allow_html=True)
