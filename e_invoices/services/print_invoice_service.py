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
    
#     # AES 加密 (ECB 模式)
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

    # def aes_encrypt_hex(key: bytes, data: bytes) -> str:
#     cipher = AES.new(key, AES.MODE_ECB)
#     encrypted = cipher.encrypt(pad(data, AES.block_size))
#     return encrypted.hex()

# def generate_code39_data(invoice_date, invoice_number):
#     year = invoice_date.year - 1911
#     month = invoice_date.month
#     period_code = f"{year:03d}{month:02d}" # 5碼期別
#     inv_num = invoice_number.ljust(10, '0')[:10] # 10碼發票號碼
#     #random_code = str(random.randint(0, 9999)).zfill(4) # 4碼隨機碼
#     code39_data = f"{period_code}{inv_num}{random_code}"
#     if len(code39_data) != 19:
#         raise ValueError("Code39條碼長度必須是19碼")
#     return code39_data

# # ====== 產生發票圖 (5.7cm × 9cm) ======
# def generate_invoice_image(invoice, aes_key: bytes):
#     dpi = 300
#     cm_to_px = lambda cm: int(cm / 2.54 * dpi)
#     width_px = cm_to_px(5.7)
#     height_px = cm_to_px(9)

#     img = Image.new('RGB', (width_px, height_px), color='white')
#     draw = ImageDraw.Draw(img)

#     # 字型設定
#     def get_font_by_height_cm(height_cm, bold=False):
#         pt = int(height_cm / 2.54 * dpi * 0.75)
#         font_path = "msjh.ttc" if os.path.exists("msjh.ttc") else r"C:\\Windows\\Fonts\\arialbd.ttf"
#         return ImageFont.truetype(font_path, pt)

#     def draw_centered_text(text, top_cm, font_cm, bold=False):
#         font = get_font_by_height_cm(font_cm, bold)
#         w, _ = draw.textbbox((0, 0), text, font=font)[2:]
#         draw.text(((width_px - w) // 2, cm_to_px(top_cm)), text, font=font, fill='black')

#     def draw_left_text(text, top_cm, font_cm, left_cm=0.3, bold=False):
#         font = get_font_by_height_cm(font_cm, bold)
#         draw.text((cm_to_px(left_cm), cm_to_px(top_cm)), text, font=font, fill='black')

#     # === 資料處理 ===
#     # 日期格式轉民國
#     y = invoice.invoice_date.year - 1911
#     date_code = f"{y:03d}{invoice.invoice_date.month:02d}{invoice.invoice_date.day:02d}"

#     # 統編
#     buyer_identifier = (getattr(invoice, "buyer_identifier", "") or "00000000").ljust(8, '0')[:8]
#     company_identifier = (invoice.company_identifier or "00000000").ljust(8, '0')[:8]

#     # 金額轉16進位
#     sales_hex = f"{int(invoice.sales_amount):X}".rjust(8, '0') if getattr(invoice, "buyer_identifier", "") else "00000000"
#     total_hex = f"{int(invoice.total_amount):X}".rjust(8, '0')

#     # AES 加密
#     raw_encrypt = (random_code + invoice.invoice_number).encode()
#     encrypted_hex = aes_encrypt_hex(aes_key, raw_encrypt)
#     encrypt_part1 = encrypted_hex[:16]
#     encrypt_part2 = encrypted_hex[16:32]

#     # Left QR Code Data
#     left_qr_main = (
#         invoice.invoice_number +
#         date_code +
#         random_code +
#         sales_hex +
#         total_hex +
#         buyer_identifier +
#         company_identifier +
#         encrypt_part1 +
#         encrypt_part2
#     )
#     business_use_area = '*' * 10
#     encoding_param = '1'
#     item_fields = []
#     if hasattr(invoice, "items"):
#         for item in invoice.items.all():
#             item_fields.extend([item.line_description, str(item.line_quantity), str(item.line_unit_price)])
#     items_str = ':'.join(item_fields) + ':'
#     left_qr_data = left_qr_main + ':' + business_use_area + ':' + encoding_param + ':' + items_str

#     # Right QR Code Data
#     right_qr_data = '**' + items_str[len(items_str) // 2:]

#     # Code39 Data
#     code39_data = generate_code39_data(invoice.invoice_date, invoice.invoice_number)

#     # === 畫圖 ===
#     # 公司名稱（1.3cm）
#     draw_centered_text(invoice.company.company_name, top_cm=1.3, font_cm=0.5, bold=True)

#     # 電子發票證明聯（2.2cm）
#     draw_centered_text("電子發票證明聯", top_cm=2.2, font_cm=0.5, bold=True)

#     # 期別（2.7cm）
#     draw_centered_text(f"{y}年01-02月", top_cm=2.7, font_cm=0.5, bold=True)

#     # 發票號碼（3.2cm）
#     draw_centered_text(invoice.invoice_number, top_cm=3.2, font_cm=0.5, bold=True)

#     # 發票時間（3.9cm）
#     draw_left_text(f"{invoice.invoice_date.strftime('%Y-%m-%d')} {invoice.invoice_time}", top_cm=3.9, font_cm=0.4)

#     # 隨機碼與總計（4.3cm）
#     draw_left_text(f"隨機碼: {random_code}", top_cm=4.3, font_cm=0.4)
#     draw_left_text(f"總計: {invoice.total_amount}", top_cm=4.3, font_cm=0.4, left_cm=3.1)

#     # 賣方統編（4.7cm）
#     draw_left_text(f"賣方: {invoice.company_identifier}", top_cm=4.7, font_cm=0.4)

#     # 模擬條碼（5.1cm）
#     mock_barcode = qrcode.make(code39_data).resize((width_px - cm_to_px(1), cm_to_px(0.5)))
#     img.paste(mock_barcode, ((width_px - mock_barcode.width) // 2, cm_to_px(5.1)))

#     # QR Code（6.1cm）
#     qr_size = cm_to_px(2.5)
#     img.paste(qrcode.make(left_qr_data).resize((qr_size, qr_size)),
#     (cm_to_px(0.5), cm_to_px(6.1)))
#     img.paste(qrcode.make(right_qr_data).resize((qr_size, qr_size)),
#     (width_px - qr_size - cm_to_px(0.5), cm_to_px(6.1)))

#     # 單號（約 8.6cm）
#     #draw_left_text(f"單號: {invoice.order_number}", top_cm=8.6, font_cm=0.35)

#     return img

# # ====== 把發票圖貼到 A4 左上角 ======
# def place_invoice_on_a4_left_top(invoice_img):
#     dpi = 300
#     cm_to_px = lambda cm: int(cm / 2.54 * dpi)
#     a4_width_px = cm_to_px(21)
#     a4_height_px = cm_to_px(29.7)

#     a4_img = Image.new('RGB', (a4_width_px, a4_height_px), color='white')
#     draw = ImageDraw.Draw(a4_img)

#     invoice_width_px, invoice_height_px = invoice_img.size

#     # 左上角 (左 1.5cm, 上 2.5cm)
#     left_margin_px = cm_to_px(1.5)
#     top_margin_px = cm_to_px(2.5)

#     a4_img.paste(invoice_img, (left_margin_px, top_margin_px))

#     # 畫邊框
#     draw.rectangle(
#         [left_margin_px, top_margin_px, left_margin_px + invoice_width_px, top_margin_px + invoice_height_px],
#         outline='black', width=5
#     )

#     return a4_img

# 使用方式範例
# invoice = <從你的資料庫抓出來的invoice物件>
# aes_key = b"16byteslongkey!!"
# img = generate_invoice_image(invoice, aes_key)
# a4_img = place_invoice_on_a4_left_top(img)
# a4_img.save("output_invoice.pdf", "PDF", resolution=300.0)