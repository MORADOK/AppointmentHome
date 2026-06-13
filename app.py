import streamlit as st
import openpyxl
from io import BytesIO
import base64
from datetime import datetime

# ==========================================
# 0. ตั้งค่าและซ่อนเมนู Streamlit
# ==========================================
st.set_page_config(page_title="ระบบจัดการ รพ.โฮม", page_icon="🏥", layout="centered")

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
# 1. ฟังก์ชันพื้นฐาน
# ==========================================
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    except Exception:
        return "" 

def format_thai_date(date_obj):
    thai_months = ["", "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
    return f"{date_obj.day} {thai_months[date_obj.month]} {date_obj.year + 543}"

# ==========================================
# 2. ฟังก์ชันสร้างหน้าเว็บสำหรับปริ้น (บัตรนัด / ใบรับรองแพทย์ / ใบเสร็จ)
# ==========================================
brand_green = "#2C5E3B"
brand_brown = "#8B5A2B"
logo_base64 = get_base64_image("logo.png")

# 2.1 บัตรนัด (Appointment Card)
def generate_appt_html(data):
    html = f"""<!DOCTYPE html><html lang="th"><head><meta charset="UTF-8"><style>
        * {{ -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }}
        body {{ font-family: 'Tahoma', sans-serif; color: #333; }}
        .card {{ max-width: 600px; margin: 0 auto; border: 1px solid #ddd; padding-bottom: 20px; }}
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

# 2.2 ใบรับรองแพทย์ (Medical Certificate)
def generate_medcert_html(data):
    html = f"""<!DOCTYPE html><html lang="th"><head><meta charset="UTF-8"><style>
        * {{ -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }}
        body {{ font-family: 'Tahoma', sans-serif; color: #333; line-height: 1.6; }}
        .card {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .logo {{ width: 80px; }}
        .title {{ font-size: 24px; font-weight: bold; color: {brand_green}; margin: 10px 0; }}
        .print-btn {{ background-color: {brand_green}; color: white; border: none; padding: 10px; cursor: pointer; width: 100%; font-size: 16px; margin-bottom: 10px; }}
        .sign-area {{ margin-top: 50px; text-align: right; padding-right: 50px; }}
        @media print {{ .no-print {{ display: none !important; }} }}
    </style></head><body>
        <button class="no-print print-btn" onclick="window.print()">🖨️ ปริ้นใบรับรองแพทย์</button>
        <div class="card">
            <div class="header">
                <img src="data:image/png;base64,{logo_base64}" class="logo">
                <div class="title">ใบรับรองแพทย์ (Medical Certificate)</div>
                <div>โรงพยาบาลโฮม ฉะเชิงเทรา</div>
            </div>
            <div>
                <p><b>วันที่ตรวจ:</b> {data['date']}</p>
                <p>ข้าพเจ้า <b>{data['doctor']}</b> แพทย์ผู้ตรวจรักษา</p>
                <p>ได้ทำการตรวจร่างกายผู้ป่วยชื่อ <b>{data['name']}</b> (HN: {data['hn']})</p>
                <p><b>การวินิจฉัยโรค (Diagnosis):</b> {data['diagnosis']}</p>
                <p><b>ความเห็นแพทย์:</b> {data['comment']}</p>
                <p><b>สรุปการพักรักษาตัว:</b> เห็นสมควรให้พักรักษาตัวเป็นเวลา {data['rest_days']} วัน ตั้งแต่วันที่ {data['start_date']} ถึงวันที่ {data['end_date']}</p>
            </div>
            <div class="sign-area">
                <p>ลงชื่อ..........................................................แพทย์ผู้ตรวจ</p>
                <p>({data['doctor']})</p>
            </div>
        </div>
    </body></html>"""
    return base64.b64encode(html.encode('utf-8')).decode('utf-8')

# 2.3 ใบเสร็จรับเงิน (Receipt)
def generate_receipt_html(data):
    html = f"""<!DOCTYPE html><html lang="th"><head><meta charset="UTF-8"><style>
        * {{ -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }}
        body {{ font-family: 'Tahoma', sans-serif; color: #333; }}
        .card {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
        .header {{ text-align: center; border-bottom: 2px solid {brand_green}; padding-bottom: 20px; margin-bottom: 20px; }}
        .logo {{ width: 70px; }}
        .title {{ font-size: 22px; font-weight: bold; color: {brand_green}; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
        th {{ background-color: {brand_green}; color: white; }}
        .total-row {{ font-weight: bold; background-color: #f9f9f9; text-align: right; }}
        .print-btn {{ background-color: {brand_green}; color: white; border: none; padding: 10px; cursor: pointer; width: 100%; font-size: 16px; margin-bottom: 10px; }}
        @media print {{ .no-print {{ display: none !important; }} }}
    </style></head><body>
        <button class="no-print print-btn" onclick="window.print()">🖨️ ปริ้นใบเสร็จรับเงิน</button>
        <div class="card">
            <div class="header">
                <img src="data:image/png;base64,{logo_base64}" class="logo">
                <div class="title">ใบเสร็จรับเงิน / Receipt</div>
                <div>โรงพยาบาลโฮม ฉะเชิงเทรา (149/1 ถ.ฉะเชิงเทรา-บางปะกง อ.เมือง จ.ฉะเชิงเทรา)</div>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <div><b>ชื่อผู้ป่วย:</b> {data['name']} <br><b>HN:</b> {data['hn']}</div>
                <div style="text-align: right;"><b>วันที่:</b> {data['date']}</div>
            </div>
            <table>
                <tr><th>ลำดับ</th><th>รายการ (Description)</th><th style="text-align:right;">จำนวนเงิน (บาท)</th></tr>
                <tr><td>1</td><td>ค่าธรรมเนียมแพทย์</td><td style="text-align:right;">{data['fee_doctor']:,.2f}</td></tr>
                <tr><td>2</td><td>ค่ายาและเวชภัณฑ์</td><td style="text-align:right;">{data['fee_med']:,.2f}</td></tr>
                <tr><td>3</td><td>ค่าบริการทางการแพทย์ / Lab</td><td style="text-align:right;">{data['fee_service']:,.2f}</td></tr>
                <tr class="total-row"><td colspan="2">รวมเงินทั้งสิ้น (Total)</td><td style="text-align:right; color:{brand_brown}; font-size:18px;">{data['total']:,.2f}</td></tr>
            </table>
            <div style="margin-top: 40px; display: flex; justify-content: space-between;">
                <div style="text-align: center;"><p>....................................................</p><p>ผู้จ่ายเงิน</p></div>
                <div style="text-align: center;"><p>....................................................</p><p>ผู้รับเงิน (เจ้าหน้าที่การเงิน)</p></div>
            </div>
        </div>
    </body></html>"""
    return base64.b64encode(html.encode('utf-8')).decode('utf-8')

# ==========================================
# 3. ฟังก์ชันสร้างไฟล์ Excel สำรอง (บัตรนัดเหมือนเดิม)
# ==========================================
def generate_appointment_card(template_path, data):
    wb = openpyxl.load_workbook(template_path)
    sheet = wb.active
    sheet['B6'], sheet['D6'] = f"ชื่อ - สกุล : {data['name']}", f"HN : {data['hn']}"
    sheet['B10'], sheet['D10'] = f"วันที่นัด : {data['appt_date_th']}", f"เวลา : {data['appt_time']}"
    sheet['B12'], sheet['D12'] = f"แพทย์ผู้ตรวจ : {data['doctor']}", f"รายการตรวจ : {data['action']} ({data['type']})"
    sheet['B14'] = f"📌 คำแนะนำในการปฏิบัติตัว : {data['instruction']}"
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output

# ==========================================
# 4. หน้าจอ UI (Streamlit)
# ==========================================
st.title("🏥 ระบบให้บริการ รพ.โฮม")
st.markdown("**ข้อมูลผู้ป่วย (กรอกครั้งเดียว ใช้ได้ทุกระบบ)**")

# --- ข้อมูลหลัก (Shared Data) ---
col_name, col_hn = st.columns(2)
with col_name:
    patient_name = st.text_input("👤 ชื่อ-นามสกุล", placeholder="เช่น นาย สมัคร โชตนา")
with col_hn:
    cn_number = st.text_input("🆔 รหัสคนไข้ (HN / CN)", placeholder="เช่น 0004000")

st.divider()

# --- ระบบแท็บ (Tabs) ---
tab1, tab2, tab3 = st.tabs(["🏥 ออกบัตรนัด", "📝 ออกใบรับรองแพทย์", "🧾 ออกใบเสร็จรับเงิน"])

# ------------------------------------
# แท็บ 1: บัตรนัด
# ------------------------------------
with tab1:
    st.subheader("รายละเอียดการนัดหมาย")
    appt_type = st.radio("ประเภท", ["มาติดตามอาการ", "มาเจาะเลือด"], horizontal=True)
    
    col_d, col_t = st.columns(2)
    with col_d:
        date_sel = st.date_input("วันที่นัด", value=datetime.today())
        date_th = format_thai_date(date_sel)
    with col_t:
        time_sel = st.selectbox("เวลานัด", ["08.00 - 10.00 น.", "10.00 - 12.00 น.", "13.00 - 15.00 น.", "15.00 - 16.30 น."])
    
    col_doc, col_act = st.columns(2)
    with col_doc:
        doc_appt = st.text_input("แพทย์ผู้ตรวจ (บัตรนัด)", value="นพ.อภิสิทธิ์ สื่อประเสริฐสิทธิ์")
    with col_act:
        act_appt = st.text_input("รายการตรวจ", value="ตรวจติดตามอาการทั่วไป" if appt_type == "มาติดตามอาการ" else "เจาะเลือด ตรวจสุขภาพ")
    
    ins_appt = st.text_input("คำแนะนำ", value="รับประทานยาและปฏิบัติตัวตามแพทย์สั่ง" if appt_type == "มาติดตามอาการ" else "งดน้ำ-งดอาหาร 6-8 ชั่วโมงก่อนตรวจ")

    if st.button("✨ ปริ้นบัตรนัด", type="primary", use_container_width=True):
        if not patient_name or not cn_number:
            st.error("กรุณากรอกชื่อและ HN ด้านบนก่อนครับ")
        else:
            data_appt = {"name": patient_name, "hn": cn_number, "type": appt_type, "appt_date_th": date_th, "appt_time": time_sel, "doctor": doc_appt, "action": act_appt, "instruction": ins_appt}
            iframe_code = f'<iframe src="data:text/html;base64,{generate_appt_html(data_appt)}" width="100%" height="500" style="border:none;"></iframe>'
            st.markdown(iframe_code, unsafe_allow_html=True)
            try:
                st.download_button("📥 โหลด Excel บัตรนัด", generate_appointment_card("Template.xlsx", data_appt), f"Appt_{cn_number}.xlsx")
            except: pass

# ------------------------------------
# แท็บ 2: ใบรับรองแพทย์
# ------------------------------------
with tab2:
    st.subheader("รายละเอียดใบรับรองแพทย์")
    date_med_sel = st.date_input("วันที่ออกใบรับรอง", value=datetime.today())
    date_med_th = format_thai_date(date_med_sel)
    
    doc_med = st.text_input("ชื่อแพทย์ผู้ตรวจ", value="นพ.อภิสิทธิ์ สื่อประเสริฐสิทธิ์")
    diagnosis = st.text_area("การวินิจฉัยโรค (Diagnosis)", placeholder="เช่น ไข้หวัดใหญ่ สายพันธุ์ A")
    comment = st.text_area("ความเห็นแพทย์", placeholder="เช่น สมควรได้รับการพักผ่อนและรับประทานยาตามสั่ง")
    
    col_r1, col_r2, col_r3 = st.columns(3)
    with col_r1:
        rest_days = st.number_input("จำนวนวันพัก (วัน)", min_value=0, value=1)
    with col_r2:
        start_date = st.date_input("ตั้งแต่วันที่", value=datetime.today())
    with col_r3:
        end_date = st.date_input("ถึงวันที่", value=datetime.today())

    if st.button("✨ ปริ้นใบรับรองแพทย์", type="primary", use_container_width=True):
        if not patient_name or not cn_number:
            st.error("กรุณากรอกชื่อและ HN ด้านบนก่อนครับ")
        else:
            data_med = {
                "name": patient_name, "hn": cn_number, "date": date_med_th, "doctor": doc_med, 
                "diagnosis": diagnosis, "comment": comment, "rest_days": rest_days, 
                "start_date": format_thai_date(start_date), "end_date": format_thai_date(end_date)
            }
            iframe_code = f'<iframe src="data:text/html;base64,{generate_medcert_html(data_med)}" width="100%" height="600" style="border:none;"></iframe>'
            st.markdown(iframe_code, unsafe_allow_html=True)

# ------------------------------------
# แท็บ 3: ใบเสร็จรับเงิน
# ------------------------------------
with tab3:
    st.subheader("รายละเอียดค่าใช้จ่าย")
    date_rec_th = format_thai_date(datetime.today())
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        fee_doctor = st.number_input("1. ค่าธรรมเนียมแพทย์ (บาท)", min_value=0.0, value=500.0, step=100.0)
        fee_med = st.number_input("2. ค่ายาและเวชภัณฑ์ (บาท)", min_value=0.0, value=1200.0, step=100.0)
    with col_f2:
        fee_service = st.number_input("3. ค่าบริการ/Lab (บาท)", min_value=0.0, value=300.0, step=100.0)
        total_fee = fee_doctor + fee_med + fee_service
        st.info(f"**💰 รวมเงินทั้งสิ้น: {total_fee:,.2f} บาท**")

    if st.button("✨ ปริ้นใบเสร็จรับเงิน", type="primary", use_container_width=True):
        if not patient_name or not cn_number:
            st.error("กรุณากรอกชื่อและ HN ด้านบนก่อนครับ")
        else:
            data_rec = {
                "name": patient_name, "hn": cn_number, "date": date_rec_th,
                "fee_doctor": fee_doctor, "fee_med": fee_med, "fee_service": fee_service, "total": total_fee
            }
            iframe_code = f'<iframe src="data:text/html;base64,{generate_receipt_html(data_rec)}" width="100%" height="600" style="border:none;"></iframe>'
            st.markdown(iframe_code, unsafe_allow_html=True)
