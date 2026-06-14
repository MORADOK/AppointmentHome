import base64

# ==========================================
# ค่าคงที่ (Brand & Style) ที่ใช้ร่วมกันทั้ง 2 page
# ==========================================
brand_green = "#2C5E3B"
brand_brown = "#8B5A2B"

# CSS ซ่อนเมนู Streamlit (White-label App) — เรียกใช้ใน page ด้วย st.markdown(...)
hide_streamlit_style = """
<style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stHeader"] {display: none !important;}
    [data-testid="stDecoration"] {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    [data-testid="stStatusWidget"] {display: none !important; visibility: hidden !important;}
    [data-testid="stAppDeployButton"] {display: none !important;}
    .stDeployButton {display: none !important;}
    .stAppDeployButton {display: none !important;}
    #viewerBadge_container {display: none !important;}
    .viewerBadge_container {display: none !important;}
    [data-testid="viewerBadge"] {display: none !important;}
    .block-container { padding-top: 1rem; padding-bottom: 0rem; }
</style>
"""


# ==========================================
# ฟังก์ชันพื้นฐาน
# ==========================================
def get_base64_image(image_path):
    """อ่านไฟล์รูปแล้วแปลงเป็น base64 string (คืนค่าว่างถ้าหาไฟล์ไม่เจอ)"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    except Exception:
        return ""


def get_baht_text(number):
    """แปลงตัวเลขจำนวนเงินเป็นข้อความภาษาไทย เช่น (ห้าร้อยบาทถ้วน)"""
    number = round(float(number), 2)
    if number == 0:
        return "ศูนย์บาทถ้วน"
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
            if d == 0:
                continue
            if pos == 0 and d == 1 and length > 1:
                res += "เอ็ด"
            elif pos == 1 and d == 1:
                res += "สิบ"
            elif pos == 1 and d == 2:
                res += "ยี่สิบ"
            else:
                res += digits[d] + positions[pos]
        return res

    text = read_num(int_part) + "บาท"
    if dec_part == "00":
        text += "ถ้วน"
    else:
        text += read_num(dec_part) + "สตางค์"
    return f"({text})"


def format_thai_date(date_obj):
    """แปลง date object เป็นข้อความวันที่ภาษาไทย (พ.ศ.) เช่น 14 มิถุนายน 2569"""
    if not date_obj:
        return ""
    thai_months = ["", "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม",
                   "มิถุนายน", "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม",
                   "พฤศจิกายน", "ธันวาคม"]
    return f"{date_obj.day} {thai_months[date_obj.month]} {date_obj.year + 543}"


# ==========================================
# โหลดโลโก้เป็น base64 ครั้งเดียว ใช้ร่วมกันทั้ง 2 page
# ==========================================
logo_base64 = get_base64_image("logo.png")
