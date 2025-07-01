import os
import random
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import qrcode
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from qrcode.constants import ERROR_CORRECT_L
from barcode import Code39
from barcode.writer import ImageWriter
from decimal import Decimal
import io

# def aes_encrypt_hex(key: bytes, data: bytes) -> str:
#     cipher = AES.new(key, AES.MODE_ECB)
#     #padded_data = pad(data.encode(), AES.block_size)
#     #encrypted = cipher.encrypt(padded_data)
#     encrypted = cipher.encrypt(pad(data, AES.block_size))
#     return base64.b64encode(encrypted).decode()
    #return encrypted.hex()

# def aes_encrypt_hex(inv_number: str, random_number: str, key: bytes):
#     # 合併發票號碼 + 隨機碼
#     plain_text = (inv_number + random_number).encode("utf-8")  # 14 bytes

#     cipher = AES.new(key, AES.MODE_ECB)
#     padded_data = pad(plain_text, AES.block_size)
#     encrypted_bytes = cipher.encrypt(padded_data)
    
#     # Base64 編碼
#     encoded = base64.b64encode(encrypted_bytes).decode("utf-8")
    
#     return encoded

def aes_encrypt_hex(hex_key: str, plaintext: str) -> str:
    key = bytes.fromhex(hex_key)
    iv = base64.b64decode("Dt8lyToo17X/XkXaQvihuA==")
    plaintext_bytes = plaintext.encode("cp950")  # 模擬 Encoding.Default
    padded = pad(plaintext_bytes, AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(padded)
    return base64.b64encode(encrypted).decode()

def generate_code39_data(random_code, invoice_date, invoice_number) :
    year = invoice_date.year - 1911
    month = invoice_date.month
    period_code = f"{year:03d}{month:02d}"
    inv_num = invoice_number.ljust(10, '0')[:10]
    code39_data = f"{period_code}{inv_num}{random_code}"
    if len(code39_data) != 19:
        raise ValueError("Code39條碼長度必須是19碼")
    return code39_data

def generate_invoice_a4(invoice, aes_key: bytes, output_dir: str, random_code: str = None):
    dpi = 300
    cm_to_px = lambda cm: int(cm / 2.54 * dpi)
    width_px = cm_to_px(5.7)
    height_px = cm_to_px(9)
    a4_width_px = cm_to_px(21)
    a4_height_px = cm_to_px(29.7)

    # 建立發票圖
    invoice_img = Image.new('RGB', (width_px, height_px), color='white')
    draw = ImageDraw.Draw(invoice_img)


    def decimal_to_str_trimmed(value):
        if value is None:
            return ""
        normalized = value.normalize()
        if normalized == normalized.to_integral():
            return str(normalized.quantize(Decimal(1)))
        return str(normalized)
    
    
    # def get_font(height_cm, bold=True):
    #     pt = int(height_cm / 2.54 * dpi * 0.75)
    #     path = r"C:\Windows\Fonts\msjh.ttc" #"msjh.ttc" if os.path.exists("msjh.ttc") else r"C:\\Windows\\Fonts\\ARLRDBD.TTF"
    #     return ImageFont.truetype(path, pt)
    def get_font(height_cm, bold=True):
        pt = int(height_cm / 2.54 * dpi * 0.75)
        path = r"C:\Windows\Fonts\msjhbd.ttc" #"msjh.ttc" if os.path.exists("msjh.ttc") else r"C:\\Windows\\Fonts\\ARLRDBD.TTF"
        return ImageFont.truetype(path, pt)

    def draw_text_centered(text, top_cm, font_cm, bold=False):
        font = get_font(font_cm, bold)
        w, _ = draw.textbbox((0, 0), text, font=font)[2:]
        draw.text(((width_px - w) // 2, cm_to_px(top_cm)), text, font=font, fill='black')

    def draw_text_left(text, top_cm, font_cm, left_cm=0.3, bold=False):
        font = get_font(font_cm, bold)
        draw.text((cm_to_px(left_cm), cm_to_px(top_cm)), text, font=font, fill='black')

    y = invoice.invoice_date.year - 1911
    date_code = f"{y:03d}{invoice.invoice_date.month:02d}{invoice.invoice_date.day:02d}"
    buyer_id = (getattr(invoice, "buyer_identifier", "") or "00000000").ljust(8, '0')[:8]
    company_id = (invoice.company_identifier or "00000000").ljust(8, '0')[:8]
    sales_hex = f"{int(invoice.sales_amount):X}".rjust(8, '0') if getattr(invoice, "buyer_identifier", "") else "00000000"
    total_hex = f"{int(invoice.total_amount):X}".rjust(8, '0')
    data = invoice.invoice_number + random_code
    encrypted = aes_encrypt_hex(aes_key, data)


    #enc1, enc2 = encrypted[:16], encrypted[16:32]

    # left_main = (
    #     invoice.invoice_number + date_code + random_code +
    #     sales_hex + total_hex + buyer_id + company_id + enc1 + enc2
    # )
        # 基本資料部分
    left_part = (
        invoice.invoice_number + date_code + random_code +
        sales_hex + total_hex + buyer_id + company_id + encrypted +
        ':' + '*' * 10  
    )



    items = []
    if hasattr(invoice, "items"):
        for item in invoice.items.all():
            line_unit_price = decimal_to_str_trimmed(item.line_unit_price)
            items += [item.line_description, str(item.line_quantity), line_unit_price]

    grouped_items = [items[i:i+3] for i in range(0, len(items), 3)]

    max_left_len = 128
    room_for_items = max_left_len - len(left_part)
    left_items = []
    right_items = []
    current_len = 0

    # 計算 group 數量
    group_count = str(len(grouped_items))  # ✅ 重點在這行
    left_part_countinue = f"{left_part}:{group_count}:{group_count}:3:"

    for group in grouped_items:
        group_str = ':'.join(group) + ':'
        if current_len + len(group_str) <= room_for_items:
            left_items.append(group_str)
            current_len += len(group_str)
        else:
            right_items.append(group_str)

    items_str = ':'.join(items) + ':'
    left_qr = left_part_countinue +''.join(left_items)
    right_qr = '**' + ''.join(right_items).rstrip(':')

    def generate_code39_barcode(data, width_px, height_px):
        buffer = io.BytesIO()
        barcode = Code39(data, writer=ImageWriter(), add_checksum=False)
        barcode.write(buffer, options={"module_height": height_px / 10, "module_width": 0.3})
        buffer.seek(0)
        img = Image.open(buffer)

        # 嘗試裁切掉底部文字：抓上面 70-80% 區域（可能需微調）
        width, height = img.size
        cropped_img = img.crop((0, 0, width, int(height * 0.5)))
        new_width = int(cropped_img.width * 0.5)
        new_height = int(cropped_img.height * 1.2)  # 高度比例跟寬度同步

        cropped_img = cropped_img.resize(
            (new_width, new_height),
            Image.Resampling.LANCZOS
        )

        return cropped_img
    


    # 發票基本文字
    draw_text_centered(invoice.company.company_name, 0.7, 0.8, bold=False) #1.3->0.7
    draw_text_centered("電子發票證明聯", 1.8, 1.0, bold=False) #2.2->1.6
    draw_text_centered(f"{y}年{invoice.invoice_date.month:02d}-{invoice.invoice_date.month+1:02d}月", 2.6, 0.8, bold=False) #2.7->2.1
    draw_text_centered(f"{invoice.invoice_number[:2]}-{invoice.invoice_number[2:]}", 3.2, 0.8, bold=False) #3.2->2.6
    draw_text_left(f"{invoice.invoice_date.strftime('%Y-%m-%d')} {invoice.invoice_time}", 3.9, 0.4)
    draw_text_left(f"隨機碼: {random_code}", 4.3, 0.4)

    total_amount = decimal_to_str_trimmed(invoice.total_amount)
    draw_text_left(f"總計: {total_amount}", 4.3, 0.4, left_cm=3.1)

    draw_text_left(f"賣方: {invoice.company.company_identifier}", 4.7, 0.4)
    print(f"invoice_number: {invoice.invoice_number}")
    print(f"date_code: {date_code}")
    print(f"random_code: {random_code}")
    print(f"sales_hex: {sales_hex}")
    print(f"total_hex: {total_hex}")
    print(f"buyer_id: {buyer_id}")
    print(f"company_id: {company_id}")
    print(f"encrypted: {encrypted}")
    print(f"items_str: {items_str}")
    print(f"left_qr: {left_qr}")
    print(f"right_qr: {right_qr}")
    #draw_text_left(f"單號: {invoice.order_number}", 8.6, 0.35)
    

    # 條碼
    # barcode = qrcode.make(generate_code39_data(random_code, invoice.invoice_date, invoice.invoice_number)).resize((width_px - cm_to_px(1), cm_to_px(0.5)))
    # invoice_img.paste(barcode, ((width_px - barcode.width) // 2, cm_to_px(5.1)))
    barcode_data = generate_code39_data(random_code, invoice.invoice_date, invoice.invoice_number)
    barcode_img = generate_code39_barcode(
        barcode_data,
        width_px - cm_to_px(1),
        cm_to_px(0.5)
    )
    invoice_img.paste(barcode_img, ((width_px - barcode_img.width) // 2, cm_to_px(5.1)))

    def generate_qrcode(data):
        qr = qrcode.QRCode(
            version=6,
            error_correction=ERROR_CORRECT_L,
            box_size=10,
            border=4
        )
        qr.add_data(data)
        qr.make(fit=False)  # 不自動調整大小，強制使用 V6
        return qr.make_image(fill_color="black", back_color="white")

    # QRCODEs
    #qr_size = cm_to_px(2.2)
    #invoice_img.paste(generate_qrcode.make(left_qr).resize((qr_size, qr_size)), (cm_to_px(0.5), cm_to_px(6.1)))
    #invoice_img.paste(generate_qrcode.make(right_qr).resize((qr_size, qr_size)), (width_px - qr_size - cm_to_px(0.5), cm_to_px(6.1)))
    qr_size = cm_to_px(2.2)
    left_qr_img = generate_qrcode(left_qr).resize((qr_size, qr_size))
    right_qr_img = generate_qrcode(right_qr).resize((qr_size, qr_size))

    invoice_img.paste(left_qr_img, (cm_to_px(0.5), cm_to_px(6.1)))
    invoice_img.paste(right_qr_img, (width_px - qr_size - cm_to_px(0.5), cm_to_px(6.1)))
    # === 貼上 A4 左上角 ===
    a4_img = Image.new('RGB', (a4_width_px, a4_height_px), color='white')
    a4_draw = ImageDraw.Draw(a4_img)
    left_margin = cm_to_px(1.5)
    top_margin = cm_to_px(2.5)
    a4_img.paste(invoice_img, (left_margin, top_margin))
    a4_draw.rectangle([left_margin, top_margin, left_margin + width_px, top_margin + height_px], outline='black', width=5)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{invoice.invoice_number}_{timestamp}.pdf"
    output_path = os.path.join(output_dir, filename)
    
    if not output_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp','.pdf')):
        output_path += '.pdf'
    # === 儲存圖檔 ===
    a4_img.save(output_path)