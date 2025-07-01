import os
import random
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from PyPDF2 import PdfMerger
from decimal import Decimal
output_folder = r"C:\\Users\\waylin\\mydjango\\e_invoice\\print\\"

# 轉換金額為中文大寫
def number_to_chinese(amount_str):
    amount_str = str(amount_str)
    digits = "零壹貳參肆伍陸柒捌玖"
    units = ["", "拾", "佰", "仟"]
    big_units = ["", "萬", "億", "兆"]

    integer_part, dot, decimal_part = amount_str.partition(".")
    integer_part = integer_part.zfill(1)

    result = ""
    int_len = len(integer_part)
    zero = False
    for i in range(int_len):
        num = int(integer_part[i])
        pos = int_len - i - 1
        unit = units[pos % 4]
        big_unit = big_units[pos // 4]
        if num == 0:
            zero = True
        else:
            if zero:
                result += "零"
                zero = False
            result += digits[num] + unit
        if pos % 4 == 0 and pos != 0:
            result += big_unit

    result += "元"

    if decimal_part:
        jiao = int(decimal_part[0]) if len(decimal_part) > 0 else 0
        fen = int(decimal_part[1]) if len(decimal_part) > 1 else 0
        if jiao:
            result += digits[jiao] + "角"
        if fen:
            result += digits[fen] + "分"
        if jiao == 0 and fen == 0:
            result += "整"
    else:
        result += "整"

    return result

    
def cm_to_px(cm, dpi=300):
    return int(cm / 2.54 * dpi)

def get_font(size_cm, bold=False):
    pt = int(size_cm / 2.54 * 300 * 0.75)
    path = r"C:\\Windows\\Fonts\\msjhbd.ttc" if bold else r"C:\\Windows\\Fonts\\msjh.ttc"
    return ImageFont.truetype(path, pt)

def draw_text_centered(text, top_cm, font_cm, bold=False):
        font = get_font(font_cm, bold)
        w, _ = draw.textbbox((0, 0), text, font=font)[2:]
        draw.text(((width_px - w) // 2, cm_to_px(top_cm)), text, font=font, fill='black')

def draw_text_left(text, top_cm, font_cm, left_cm=0.3, bold=False):
        font = get_font(font_cm, bold)
        draw.text((cm_to_px(left_cm), cm_to_px(top_cm)), text, font=font, fill='black')

# 用字數來切換行
# def wrap_text_by_char(text, max_chars_per_line):
#     max_chars_per_line = 26
#     lines = []
#     while len(text) > max_chars_per_line:
#         lines.append(text[:max_chars_per_line])
#         text = text[max_chars_per_line:]
#     lines.append(text)
#     return lines
# def decimal_to_str_trimmed(value):
#     if value is None:
#         return ""
#     normalized = value.normalize()
#     if normalized == normalized.to_integral():
#         return str(normalized.quantize(Decimal(1)))
#     return str(normalized)
# from decimal import Decimal

# def decimal_to_str_trimmed(value):
#     if value is None:
#         return ""
#     if not isinstance(value, Decimal):
#         value = Decimal(value)
#     normalized = value.normalize()
#     if normalized == normalized.to_integral():
#         return str(normalized.quantize(Decimal(1)))
#     return str(normalized)
def decimal_to_str_trimmed(value):
    if value is None:
        return "" 
    if not isinstance(value, Decimal):
        value = Decimal(value)

    normalized = value.normalize()
    if normalized == normalized.to_integral():
        # 無小數點，使用千分位格式
        return "{:,.0f}".format(normalized)
    else:
        # 有小數點，最多保留到實際小數位
        return "{:,.{}f}".format(normalized, -normalized.as_tuple().exponent)
# 用像素寬來切換行

def wrap_text_by_width(text, font, max_width_px):
    lines = []
    current_line = ""
    for char in text:
        test_line = current_line + char
        w = font.getlength(test_line)
        if w <= max_width_px:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = char
    if current_line:
        lines.append(current_line)
    return lines

def draw_text(draw, text, pos_cm, font_cm, bold=False, align="left", page_width_px=0):
    font = get_font(font_cm, bold)
    x, y = map(lambda v: cm_to_px(v), pos_cm)
    if align == "center":
        w, _ = draw.textbbox((0, 0), text, font=font)[2:]
        x = (page_width_px - w) // 2
    draw.text((x, y), text, font=font, fill='black')

# 用字數來切換行
# def draw_wrapped_text(draw, text, x_px, y_px, font, max_chars_per_line, line_spacing=4):
#     lines = wrap_text_by_char(text, max_chars_per_line)
#     for i, line in enumerate(lines):
#         draw.text((x_px, y_px + i * (font.getbbox(line)[3] + line_spacing)), line, font=font, fill="black")

# 用像素寬來切換行
def draw_wrapped_text(draw, text, x_px, y_px, font, max_width_px, line_spacing=4):
    lines = wrap_text_by_width(text, font, max_width_px)
    for i, line in enumerate(lines):
        draw.text((x_px, y_px + i * (font.getbbox(line)[3] + line_spacing)), line, font=font, fill="black")

def draw_table_first_page(allowance, draw, canvas, start_cm, column_widths_cm, headers, data_rows, sales_amount, total_tax_amount, company_name, total_amount, company_identifier, company_address, wrap_text_fn=draw_wrapped_text):
    dpi = 300
    page_width_px = cm_to_px(21.0)
    
    y_offset = 6.8
    y_start = cm_to_px(y_offset)
    x_start = cm_to_px(start_cm[0])

    

    total2_y_start = extra_y_start + extra_height
    draw.rectangle([x_start, total2_y_start, x_start + merge_width, total2_y_start + row_height_total], outline="black",width=3)




    draw_text(draw, f"{allowance.company.company_name}", (0, 1.6), 0.8, align="center", page_width_px=page_width_px)
    draw_text(draw, f"營利事業統一編號: {allowance.buyer_identifier}", (1.3, 5.3), 0.5)
    draw_text(draw, f"原開立銷貨發票單位", (1.3, 5.3), 0.5) 
    draw_text(draw, f"名稱: {allowance.buyer_identifier}", (1.3, 5.3), 0.5)
    draw_text(draw, f"營業所在地址: {allowance.buyer_address}", (1.3, 5.3), 0.5) 
 
    draw_text(draw, "營業人銷貨退回、進貨退出或折讓證明單", (0, 1.6), 0.8)
    draw_text(draw,  f"{allowance.allowance_date.strftime('%Y-%m-%d')}", (0, 3.3), 0.6, align="center", page_width_px=page_width_px)
    draw_text(draw, f"折讓證明單號碼: {allowance.allowance_number}", (1.3, 5.3), 0.5)
    draw_text(draw, f"地址: Taipei", (1.3, 6.0), 0.5)
    # draw_text(draw, "格     式:25", (17.5, 3.9), 0.5)
    # draw_text(draw, f"第1頁/共{(len(data_rows) - 14 + 19) // 20 + 1}頁", (17.2, 6.0), 0.5)
    

    y_offset = 6.8
    y_start = cm_to_px(y_offset)
    x_start = cm_to_px(start_cm[0])
    row_height_header = cm_to_px(0.7)
    row_height_data = cm_to_px(1.2)
    row_height_total = cm_to_px(0.9) # 銷售額合計欄位高度
    extra_height = cm_to_px(1.3) #營業稅欄位高度
    font_header = get_font(0.5, bold=True)
    font_data = get_font(0.5)
    font_total = get_font(0.5, bold=True)
    page_size_limit = 14
    page_data_rows = data_rows[:page_size_limit]
    total_width_px = sum([cm_to_px(w) for w in column_widths_cm])

    # Draw headers
    current_x = x_start
    for width_cm, header in zip(column_widths_cm, headers):
        cell_w = cm_to_px(width_cm)
        w, h = draw.textbbox((0, 0), header, font=font_header)[2:]
        draw.text((current_x + (cell_w - w) // 2, y_start + (row_height_header - h) // 2), header, font=font_header, fill="black")
        draw.rectangle([current_x, y_start, current_x + cell_w, y_start + row_height_header], outline="black",width=3)
        current_x += cell_w

    for i in range(len(column_widths_cm) + 1):
        x = x_start + sum([cm_to_px(w) for w in column_widths_cm[:i]])
        draw.line([x, y_start + row_height_header, x, y_start + row_height_header + len(data_rows) * row_height_data], fill="black",width=3)

    # Draw data rows
    for row_index, row in enumerate(data_rows):
        current_x = x_start
        current_y = y_start + row_height_header + row_index * row_height_data
        for col_index, (col, width_cm) in enumerate(zip(row, column_widths_cm)):
            cell_w = cm_to_px(width_cm)
            w, h = draw.textbbox((0, 0), str(col), font=font_data)[2:]
            if col_index in [1, 2, 3]:
                draw.text((current_x + cell_w - w - cm_to_px(0.1), current_y + (row_height_data - h) // 2), str(col), font=font_data, fill="black")
            else:
                draw.text((current_x + cm_to_px(0.1), current_y + (row_height_data - h) // 2), str(col), font=font_data, fill="black")
            current_x += cell_w
    # 接著處理銷售額合計列與後續資訊，僅在為第一頁時繪製
    # if len(data_rows) <= page_size_limit:
    #     total_y_start = y_start + row_height_header + len(page_data_rows) * row_height_data
    #     merge_width = sum([cm_to_px(w) for w in column_widths_cm[:3]])
    #     cell_w_sales = cm_to_px(column_widths_cm[3])
    #     cell_w_stamp = cm_to_px(column_widths_cm[4])
    #     draw.rectangle([x_start, total_y_start, x_start + merge_width, total_y_start + row_height_total], outline="black", width=3)
    #     draw.text((x_start + cm_to_px(0.1), total_y_start + cm_to_px(0.1)), "銷售額合計", font=font_total, fill="black")
    #     draw.rectangle([x_start + merge_width, total_y_start, x_start + merge_width + cell_w_sales, total_y_start + row_height_total], outline="black", width=3)
    #     w, h = draw.textbbox((0, 0), sales_amount, font=font_total)[2:]
    #     draw.text((x_start + merge_width + cell_w_sales - w - cm_to_px(0.1), total_y_start + cm_to_px(0.1)), sales_amount, font=font_total, fill="black")
    #     draw.rectangle([x_start + merge_width + cell_w_sales, total_y_start, x_start + merge_width + cell_w_sales + cell_w_stamp, total_y_start + row_height_total], outline="black", width=3)
    #     draw.text((x_start + merge_width + cell_w_sales + cm_to_px(0.2), total_y_start + cm_to_px(0.1)), "營業人蓋統一發票專用章", font=font_total, fill="black")
    # 接著處理銷售額合計列與後續資訊，僅在為第一頁時繪製
    if len(data_rows) <= page_size_limit:
        # 銷售額合計列
        total_y_start = y_start + row_height_header + len(data_rows) * row_height_data  # 表頭+明細高度 = total_y_start
        merge_width = sum([cm_to_px(w) for w in column_widths_cm[:3]]) # 前三格的寬度設為merge_width
        cell_w_sales = cm_to_px(column_widths_cm[3]) # sales amount 欄位寬度
        cell_w_stamp = cm_to_px(column_widths_cm[4]) # 營業人蓋統一發票專用章 欄位寬度
        draw.rectangle([x_start, total_y_start, x_start + merge_width, total_y_start + row_height_total], outline="black",width=3)
        draw.text((x_start + cm_to_px(0.1), total_y_start + cm_to_px(0.1)), "銷售額合計", font=font_total, fill="black")
        
        draw.rectangle([x_start + merge_width, total_y_start, x_start + merge_width + cell_w_sales, total_y_start + row_height_total], outline="black",width=3)
        
        #[2:] → 只取 right 和 bottom 的值 , w = right, h = bottom = 靠右對齊、垂直置中
        w, h = draw.textbbox((0, 0), decimal_to_str_trimmed(sales_amount), font=font_total)[2:]
        
        draw.text((x_start + merge_width + cell_w_sales - w - cm_to_px(0.1), total_y_start + cm_to_px(0.1)), decimal_to_str_trimmed(sales_amount), font=font_total, fill="black")
        draw.rectangle([x_start + merge_width + cell_w_sales, total_y_start, x_start + merge_width + cell_w_sales + cell_w_stamp, total_y_start + row_height_total], outline="black",width=3)
        draw.text((x_start + merge_width + cell_w_sales + cm_to_px(0.2), total_y_start + cm_to_px(0.1)), "營業人蓋統一發票專用章", font=font_total, fill="black")

        # 營業稅與賣方欄位
        # extra_y_start = total_y_start + row_height_total # (表頭欄高+明細總欄高)+ 銷售額合計欄高 = extra_y_start
        # merge_extra_width = sum([cm_to_px(w) for w in column_widths_cm[:3]]) # 前三格的寬度設為merge_extra_ width
        # cell_width = merge_extra_width // 7
        # tax_labels = ["營業稅", "應稅", "", "零稅率", "", "免稅", ""]
        # for i in range(8):
        #     x = x_start + i * cell_width
        #     if i < 7:
        #         draw.line([x, extra_y_start, x, extra_y_start + extra_height], fill="black",width=3)
        #     if i < 7 and tax_labels[i]:
        #         w, h = draw.textbbox((0, 0), tax_labels[i], font=font_total)[2:]
        #         draw.text((x + (cell_width - w) // 2, extra_y_start + (extra_height - h) // 2), tax_labels[i], font=font_total, fill="black")
        # draw.line([x_start, extra_y_start, x_start + merge_extra_width, extra_y_start], fill="black",width=3) 
        # draw.line([x_start, extra_y_start + extra_height, x_start + merge_extra_width, extra_y_start + extra_height], fill="black",width=3)
        
        # 稅額區段
        extra_y_start = total_y_start + row_height_total
        merge_extra_width = sum([cm_to_px(w) for w in column_widths_cm[:3]])
        cell_width = merge_extra_width // 7
        tax_labels = ["營業稅", "應稅", "", "零稅率", "", "免稅", ""]

        # 決定要打勾的 index（0-based）
        check_index_map = {"1": 2, "2": 4, "3": 6}
        checked_idx = check_index_map.get(invoice.tax_type)

        for i in range(8):
            x = x_start + i * cell_width
            if i < 7:
                draw.line([x, extra_y_start, x, extra_y_start + extra_height], fill="black", width=3)

            if i < 7 and tax_labels[i]:
                w, h = draw.textbbox((0, 0), tax_labels[i], font=font_total)[2:]
                draw.text((x + (cell_width - w) // 2, extra_y_start + (extra_height - h) // 2), tax_labels[i], font=font_total, fill="black")

            # ✅ 如果當前 index 要打勾
            if i == checked_idx:
                # 畫一個小勾勾，靠近格子中央偏左上
                check_font = get_font(0.5, bold=True)
                check_text = "V"  #或用 "✓"
                w_check, h_check = draw.textbbox((0, 0), check_text, font=check_font)[2:]
                draw.text((x + (cell_width - w_check) // 2, extra_y_start + (extra_height - h_check) // 2), check_text, font=check_font, fill="black")




        # 營業稅額欄
        display_tax_amount = total_tax_amount if invoice.tax_type == "1" else 0
        right_x = x_start + merge_extra_width 
        draw.rectangle([right_x, extra_y_start, right_x + cell_w_sales, extra_y_start + extra_height], outline="black",width=3)
        w, h = draw.textbbox((0, 0), decimal_to_str_trimmed(display_tax_amount), font=font_total)[2:]
        draw.text((right_x + cell_w_sales - w - cm_to_px(0.1), extra_y_start + (extra_height - h) // 2), decimal_to_str_trimmed(display_tax_amount), font=font_total, fill="black")
        
        # # 買方名稱欄
        right_x += cell_w_sales
        draw.line([right_x, extra_y_start, right_x, extra_y_start + extra_height], fill="black", width=3)
        draw.line([right_x + cell_w_stamp, extra_y_start, right_x + cell_w_stamp, extra_y_start + extra_height], fill="black", width=3)
        draw.line([right_x, extra_y_start, right_x + cell_w_stamp, extra_y_start], fill="black", width=3)
        # label = f"賣       方：{company_name}"
        # wrap_text_fn(draw, label, right_x + cm_to_px(0.1), extra_y_start + cm_to_px(0.1), font=font_total, max_width_px=cell_w_stamp - cm_to_px(0.2))

        # 嘗試根據統一編號載入對應圖章圖片
        stamp_dir = r"C:\Users\waylin\mydjango\e_invoice\assets\stamps"
        stamp_filename = f"{invoice.company.company_identifier}.png"
        stamp_image_path = os.path.join(stamp_dir, stamp_filename)

        if os.path.exists(stamp_image_path):
            stamp_img = Image.open(stamp_image_path).convert("RGBA")

            # 原始尺寸（沒用來控制位置，只用來定縮放比例）
            original_w_px = cm_to_px(2.8)
            original_h_px = cm_to_px(2.8)

            # 放大比例
            scale = 1.3
            scaled_w = int(original_w_px * scale)
            scaled_h = int(original_h_px * scale)

            # 放大圖片
            stamp_img_scaled = stamp_img.resize((scaled_w, scaled_h), Image.ANTIALIAS)

            # 固定左上角位置不變
            stamp_pos_x = right_x + cm_to_px(0.1) + cm_to_px(0.5)
            stamp_pos_y = extra_y_start + cm_to_px(0.1)

            # 貼上圖片（右下方展開）
            canvas.paste(stamp_img_scaled, (stamp_pos_x, stamp_pos_y), stamp_img_scaled)

        # else:
        #     # 找不到圖章時顯示備用文字
        #     fallback_label = f"賣       方：{invoice.company.company_name}"
        #     wrap_text_fn(
        #         draw,
        #         fallback_label,
        #         right_x + cm_to_px(0.1),
        #         extra_y_start + cm_to_px(0.1),
        #         font=font_total,
        #         max_width_px=cell_w_stamp - cm_to_px(0.2)
        #     )

        # ➕ 加入總計列
        total2_y_start = extra_y_start + extra_height
        draw.rectangle([x_start, total2_y_start, x_start + merge_width, total2_y_start + row_height_total], outline="black",width=3)
        draw.text((x_start + cm_to_px(0.1), total2_y_start + cm_to_px(0.1)), "總計", font=font_total, fill="black")
        draw.rectangle([x_start + merge_width, total2_y_start, x_start + merge_width + cell_w_sales, total2_y_start + row_height_total], outline="black",width=3)
        w, h = draw.textbbox((0, 0), decimal_to_str_trimmed(total_amount), font=font_total)[2:]
        draw.text((x_start + merge_width + cell_w_sales - w - cm_to_px(0.1), total2_y_start + (row_height_total - h) // 2), decimal_to_str_trimmed(total_amount), font=font_total, fill="black")
        draw.line([x_start + merge_width + 2 * cell_w_sales + cell_w_stamp, total2_y_start, x_start + merge_width + 2 * cell_w_sales + cell_w_stamp, total2_y_start + row_height_total], fill="black", width=3)
        draw.line([x_start + merge_width + cell_w_sales, total2_y_start, x_start + merge_width + cell_w_sales, total2_y_start + row_height_total], fill="black", width=3)
        draw.line([x_start + merge_width + cell_w_sales + cell_w_stamp, total2_y_start, x_start + merge_width + cell_w_sales + cell_w_stamp, total2_y_start + row_height_total], fill="black", width=3)
        # draw.text((x_start + merge_width + cell_w_sales + cm_to_px(0.1), total2_y_start + cm_to_px(0.1)), f"統一編號: {company_identifier}", font=font_total, fill="black")

        # 最底下插入「總計新台幣（中文大寫）」一列（不畫地址上方線條）
        final_y_start = total2_y_start + row_height_total
        final_row_height = cm_to_px(1.6)
        partial_table_width = merge_width + cell_w_sales
        draw.rectangle([x_start, final_y_start, x_start + partial_table_width, final_y_start + final_row_height], outline="black", width=3)
        draw.line([x_start + partial_table_width, final_y_start + final_row_height, x_start + partial_table_width + cell_w_stamp, final_y_start + final_row_height], fill="black", width=3)
        draw.line([x_start + partial_table_width, final_y_start, x_start + partial_table_width, final_y_start + final_row_height], fill="black", width=3)
        draw.line([x_start + partial_table_width + cell_w_stamp, final_y_start, x_start + partial_table_width + cell_w_stamp, final_y_start + final_row_height], fill="black", width=3)
        label = "總計新台幣（中文大寫）"
        w, h = draw.textbbox((0, 0), label, font=font_total)[2:]
        draw.text((x_start + cm_to_px(0.2), final_y_start + (final_row_height - h) // 2), label, font=font_total, fill="black")
        chinese_amount = number_to_chinese(total_amount)
        w_right, h_right = draw.textbbox((0, 0), chinese_amount, font=font_total)[2:]
        draw.text((x_start + partial_table_width - w_right - cm_to_px(0.2), final_y_start + (final_row_height - h_right) // 2), chinese_amount, font=font_total, fill="black")
        # address_label = f"地       址：{company_address}"
        # wrap_text_fn(draw, address_label, x_start + partial_table_width + cm_to_px(0.1), final_y_start + cm_to_px(0.1), font=font_total, max_width_px=cell_w_stamp - cm_to_px(0.2))
    

def draw_table_other_page(invoice, draw, start_cm, column_widths_cm, headers, data_rows,  page_num=2, total_pages=1, wrap_text_fn=draw_wrapped_text):
    page_width_px = cm_to_px(21.0)
    draw_text(draw, f"發票號碼: {invoice.invoice_number}", (1.3, 2.7), 0.5)
    draw_text(draw, {invoice.invoice_date.strftime('%Y-%m-%d')}, (0, 1.6), 0.6, align="center", page_width_px=page_width_px)
    x_start = cm_to_px(start_cm[0])
    y_start = cm_to_px(start_cm[1])
    row_height_header = cm_to_px(0.7)
    row_height_data = cm_to_px(1.2)
    font_header = get_font(0.5, bold=True)
    font_data = get_font(0.5)
    page_size_limit = 20
    page_data_rows = data_rows[:page_size_limit]
    while len(page_data_rows) < page_size_limit:
        page_data_rows.append(["" for _ in column_widths_cm])

    # Draw headers
    current_x = x_start
    for width_cm, header in zip(column_widths_cm, headers):
        cell_w = cm_to_px(width_cm)
        w, h = draw.textbbox((0, 0), header, font=font_header)[2:]
        draw.text((current_x + (cell_w - w) // 2, y_start + (row_height_header - h) // 2), header, font=font_header, fill="black")
        draw.rectangle([current_x, y_start, current_x + cell_w, y_start + row_height_header], outline="black", width=3)
        current_x += cell_w

    for i in range(len(column_widths_cm) + 1):
        x = x_start + sum([cm_to_px(w) for w in column_widths_cm[:i]])
        draw.line([x, y_start + row_height_header, x, y_start + row_height_header + len(page_data_rows) * row_height_data], fill="black", width=3)

    # Draw data rows
    for row_index, row in enumerate(page_data_rows):
        current_x = x_start
        current_y = y_start + row_height_header + row_index * row_height_data
        for col_index, (col, width_cm) in enumerate(zip(row, column_widths_cm)):
            cell_w = cm_to_px(width_cm)
            w, h = draw.textbbox((0, 0), str(col), font=font_data)[2:]
            if col_index in [1, 2, 3]:
                draw.text((current_x + cell_w - w - cm_to_px(0.1), current_y + (row_height_data - h) // 2), str(col), font=font_data, fill="black")
            else:
                draw.text((current_x + cm_to_px(0.1), current_y + (row_height_data - h) // 2), str(col), font=font_data, fill="black")
            current_x += cell_w

    # Draw bottom line of the table
    bottom_y = y_start + row_height_header + len(page_data_rows) * row_height_data
    draw.line([x_start, bottom_y, x_start + sum([cm_to_px(w) for w in column_widths_cm]), bottom_y], fill="black", width=3)

    return data_rows[page_size_limit:]


# ==== 主要流程：繪製與合併 PDF ====
def render_and_merge_invoices(invoice, output_folder, column_widths_cm, headers, all_data_rows,
                               sales_amount, total_tax_amount, company_name, total_amount,
                               company_identifier, company_address, wrap_text_fn=draw_wrapped_text):
    dpi = 300
    page_w, page_h = cm_to_px(21), cm_to_px(29.7)
    page_files = []
    page_num = 1

    # 第一頁最多14筆
    first_page_rows = all_data_rows[:14]
    while len(first_page_rows) < 14:
        first_page_rows.append(["" for _ in column_widths_cm])
    img = Image.new("RGB", (page_w, page_h), "white")
    draw = ImageDraw.Draw(img)
    draw_table_first_page(invoice, draw, img, (1.3, 3.5), column_widths_cm, headers, first_page_rows,
                          sales_amount, total_tax_amount, company_name, total_amount,
                          company_identifier, company_address, wrap_text_fn)
    page1_path = os.path.join(output_folder, f"page{page_num}.pdf")
    img.save(page1_path, "PDF", resolution=dpi)
    page_files.append(page1_path)
    page_num += 1

    # 後續每頁最多20筆
    remaining_rows = all_data_rows[14:]
    while remaining_rows:
        img = Image.new("RGB", (page_w, page_h), "white")
        draw = ImageDraw.Draw(img)
        total_pages = (len(all_data_rows) - 14 + 19) // 20 + 1
        draw_text(draw, f"第{page_num}頁/共{total_pages}頁", (17.2, 2.7), 0.5)
        remaining_rows = draw_table_other_page(draw, (1.3, 3.5), column_widths_cm, headers, remaining_rows, page_num, total_pages)
        page_path = os.path.join(output_folder, f"page{page_num}.pdf")
        img.save(page_path, "PDF", resolution=dpi)
        page_files.append(page_path)
        page_num += 1

    # 合併所有 PDF 頁
    merger = PdfMerger()
    for pdf in page_files:
        merger.append(pdf)
    invoice_filename = f"{invoice.invoice_number}_{invoice.buyer_identifier}_{invoice.invoice_date.strftime('%Y%m%d')}_stamp.pdf"
    merged_path = os.path.join(output_folder, invoice_filename)
    merger.write(merged_path)
    merger.close()
    
    # 刪除中間產出的分頁 PDF
    for pdf in page_files:
        if os.path.exists(pdf):
            os.remove(pdf)

    return merged_path


# def generate_invoice_pdf(invoice_data, output_path):
#     dpi = 300
#     width_cm, height_cm = 21.0, 29.7
#     page_w, page_h = cm_to_px(width_cm, dpi), cm_to_px(height_cm, dpi)
#     img = Image.new("RGB", (page_w, page_h), "white")
#     draw = ImageDraw.Draw(img)

#     draw_text(draw, "電子發票證明聯", (0, 1.6), 0.8, align="center", page_width_px=page_w)
#     draw_text(draw, invoice_data['invoice_date'].strftime('%Y-%m-%d'), (0, 3.3), 0.6, align="center", page_width_px=page_w)
#     draw_text(draw, f"發票號碼: {invoice_data['invoice_number']}", (1.3, 3.9), 0.5)
#     draw_text(draw, f"買方: {invoice_data['buyer_name']}", (1.3, 4.6), 0.5)
#     draw_text(draw, f"統一編號: {invoice_data['buyer_identifier']}", (1.3, 5.3), 0.5)
#     draw_text(draw, f"地址: {invoice_data['buyer_address']}", (1.3, 6.0), 0.5)
#     draw_text(draw, "格     式:25", (17.5, 3.9), 0.5)
#     draw_text(draw, f"第{invoice_data['page_number']}頁/共{invoice_data['total_pages']}頁", (17.2, 6.0), 0.5)

#     column_widths = [7.2, 1.9, 1.9, 2.6, 4.7]
#     headers = ["品名", "數量", "單價", "金額", "備註"]
#     start_table_cm = (1.3, 6.8)
#     sample_items = [
#         [f"商品名稱{i+1}\n編號{i+101}", random.randint(1, 9), f"{random.randint(10, 99)}.00", f"{random.randint(100, 999)}.00", "備註內容"]
#         for i in range(14)
#     ]
#     draw_table_first_page(
#         draw, start_table_cm, column_widths, headers, sample_items,
#         invoice_data.get("sales_amount", ""),
#         invoice_data.get("tax_amount", ""),
#         invoice_data.get("seller_name", ""),
#         invoice_data.get("total_amount", ""),
#         invoice_data.get("seller_identifier", ""),
#         invoice_data.get("seller_address", "")
#     )
#     img.save(output_path, "PDF", resolution=dpi)

# # ✅ 範例資料
# invoice_example = {
#     'invoice_number': 'AA12345678',
#     'invoice_date': datetime(2025, 6, 12),
#     'buyer_name': '王小明',
#     'buyer_identifier': '12345678',
#     'buyer_address': '台北市中山區南京東路三段168號',
#     'page_number': 1,
#     'total_pages': 3,
#     'sales_amount': '12345.00',
#     'tax_amount': '567.89',
#     'total_amount': '12912.89',
#     'seller_name': '測試測試測試測試測試測試測試測試公司',
#     'seller_identifier': '98765432',
#     'seller_address': '台北市大同區重慶北路一段123號'

# }

# output_file = os.path.join(output_folder, "final_invoice_with_total.pdf")
# generate_invoice_pdf(invoice_example, output_file)
# ==== 範例用 PDF 產生器，支援 34 筆資料分頁 ====



def generate_invoice_B2B_format25_pdf_stamp(invoice, output_folder):
    column_widths = [7.2, 1.9, 1.9, 2.6, 4.7]
    headers = ["品名", "數量", "單價", "金額", "備註"]
    # all_items = [
    #     [f"商品名稱{i+1}\n編號{i+101}", random.randint(1, 9), f"{random.randint(10, 99)}.00", f"{random.randint(100, 999)}.00", "備註內容"]
    #     for i in range(40)
    # ]
    # items = []
    # if hasattr(invoice, "items"):
    #     for item in invoice.items.all():
    #         line_unit_price = decimal_to_str_trimmed(item.line_unit_price)
    #         items += [item.line_description, str(item.line_quantity), line_unit_price]

    

    if invoice.tax_type == "1":
        sales_amount = invoice.sales_amount
    elif invoice.tax_type == "2":
        sales_amount = invoice.zerotax_sales_amount
    elif invoice.tax_type == "3":
        sales_amount = invoice.freetax_sales_amount  # ← 應該是 freetax_sales_amount 而不是 freetax_tax_amount？
    else:
        sales_amount = 0  # fallback，避免 None 導致後續報錯

    all_items = []
    if hasattr(invoice, "items"):
        for idx, item in enumerate(invoice.items.all()):
            description = f"{item.line_description}\n編號{idx + 101}"
            quantity = str(item.line_quantity)
            unit_price = decimal_to_str_trimmed(item.line_unit_price)
            # 如果沒有 line_amount 欄位就用下面這行計算
            amount = decimal_to_str_trimmed(item.line_amount)
            remark = "備註內容"
            all_items.append([description, quantity, unit_price, amount, remark])

    print(invoice.tax_type)
    print(invoice.sales_amount)

    return render_and_merge_invoices(
        invoice=invoice,
        output_folder=output_folder,
        column_widths_cm=column_widths,
        headers=headers,
        all_data_rows=all_items,
        sales_amount=sales_amount,
        total_tax_amount=invoice.total_tax_amount,
        company_name=invoice.company.company_name,
        total_amount=invoice.total_amount,
        company_identifier=invoice.company.company_identifier,
        company_address=invoice.company.company_address,
    )
