import os
import random
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from PyPDF2 import PdfMerger
from decimal import Decimal
output_folder = r"C:\\Users\\waylin\\mydjango\\e_invoice\\print\\"

    
def cm_to_px(cm, dpi=300):
    return int(cm / 2.54 * dpi)

def get_font(size_cm, bold=False):
    pt = int(size_cm / 2.54 * 300 * 0.75)
    path = r"C:\\Windows\\Fonts\\msjhbd.ttc" if bold else r"C:\\Windows\\Fonts\\msjh.ttc"
    return ImageFont.truetype(path, pt)

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

def draw_text(draw, text, pos_cm, font_cm, bold=False, align="left", page_width_px=0,font_name=None):
    if font_name:
        pt = int(font_cm / 2.54 * 300 * 0.75)
        font = ImageFont.truetype(font_name, pt)
    else:
        font = get_font(font_cm, bold)
    # Only use the first two elements for x and y
    x, y = map(lambda v: cm_to_px(v), pos_cm[:2])
    if align == "center":
        w, _ = draw.textbbox((0, 0), text, font=font)[2:]
        x = (page_width_px - w) // 2
    draw.text((x, y), text, font=font, fill='black')


# 用像素寬來切換行
def draw_wrapped_text(draw, text, x_px, y_px, font, max_width_px, line_spacing=4):
    lines = wrap_text_by_width(text, font, max_width_px)
    for i, line in enumerate(lines):
        draw.text((x_px, y_px + i * (font.getbbox(line)[3] + line_spacing)), line, font=font, fill="black")

def draw_table_first_page(allowance, canvas, draw, start_cm, column_widths_cm, headers, data_rows, total_tax_amount, total_amount, company_name, company_identifier, company_address, wrap_text_fn=draw_wrapped_text):
    dpi = 300
    page_width_px = cm_to_px(21.0)
    y_offset = 1.5
    y_start = cm_to_px(y_offset)
    x_start = cm_to_px(start_cm[0])
    ori_cell_w_1 = cm_to_px(1.6)
    ori_cell_w_2 = cm_to_px(1.8)
    ori_cell_w_3 = cm_to_px(5.5)
    ori_cell_h_1 = cm_to_px(1.5)
    ori_cell_h = 3 * ori_cell_h_1
    font_total = get_font(0.4, bold=True)
    font_header = get_font(0.5, bold=True)
    font_header_1 = get_font(0.4, bold=True)

    #draw_text(draw, "營業人銷貨退回、進貨退出或折讓證明單", (0, 2), 0.8, align="center", page_width_px=page_width_px)
    draw_text(draw, company_name, (0, 0.7), 0.6, align="center", page_width_px=page_width_px, font_name=r"C:\\Windows\\Fonts\\msjhbd.ttc")

    draw.rectangle([x_start, y_start, x_start + ori_cell_w_1, y_start + ori_cell_h], outline="black",width=3)
    draw.text((x_start+ cm_to_px(0.4), y_start+ cm_to_px(1.5)), "原開立\n銷貨發\n票單位", font=font_header_1, fill="black")

    draw.rectangle([x_start + ori_cell_w_1, y_start, x_start + ori_cell_w_1 + ori_cell_w_2 + ori_cell_w_3, y_start + ori_cell_h], outline="black",width=3)
    draw.line([x_start + ori_cell_w_1 + ori_cell_w_2, y_start, x_start + ori_cell_w_1 + ori_cell_w_2, y_start + ori_cell_h], fill="black",width=3) # straight
    draw.text((x_start + ori_cell_w_1 + cm_to_px(0.3), y_start + cm_to_px(0.25)), "營利事業\n統一編號", font=font_header_1, fill="black")
    draw.text((x_start + ori_cell_w_1 + ori_cell_w_2 + cm_to_px(0.2), y_start + cm_to_px(0.25)), company_identifier, font=font_header_1, fill="black")
    draw.text((x_start +  ori_cell_w_1 + ori_cell_w_2 + cm_to_px(6), y_start), "營業人銷貨退回、進貨退出或折讓證明單", font=font_header, fill="black")
    draw.text((x_start +  ori_cell_w_1 + ori_cell_w_2 + cm_to_px(6), y_start + cm_to_px(1)), f"折讓單證明號碼:{allowance.allowance_number}", font=font_header, fill="black")

    draw.line([x_start + ori_cell_w_1 , y_start + ori_cell_h_1, x_start + ori_cell_w_1 + ori_cell_w_2 + ori_cell_w_3, y_start + ori_cell_h_1], fill="black",width=3) # horizon
    draw.text((x_start + ori_cell_w_1 + cm_to_px(0.3), y_start + ori_cell_h_1 + cm_to_px(0.35)), "名       稱", font=font_header_1, fill="black")
    draw.text((x_start + ori_cell_w_1 + ori_cell_w_2 + cm_to_px(0.2), y_start + ori_cell_h_1 + cm_to_px(0.35)), company_name, font=font_header_1, fill="black")

    draw.line([x_start + ori_cell_w_1 , y_start + 2 * ori_cell_h_1, x_start + ori_cell_w_1 + ori_cell_w_2 + ori_cell_w_3, y_start + 2* ori_cell_h_1], fill="black",width=3)
    draw.text((x_start + ori_cell_w_1 + cm_to_px(0.3), y_start + 2 * ori_cell_h_1 + cm_to_px(0.25)), "營業所在\n地       址", font=font_header_1, fill="black")
    draw.text((x_start + ori_cell_w_1 + ori_cell_w_2 + cm_to_px(0.2), y_start + 2*ori_cell_h_1 + cm_to_px(0.25)), company_address, font=font_header_1, fill="black")
    draw.text((x_start + ori_cell_w_1 + ori_cell_w_2 + cm_to_px(13.5), y_start + 2*ori_cell_h_1 + cm_to_px(0.5)), "2025-06-25", font=font_header_1, fill="black")



    #draw_text(draw, f"折讓單號碼{allowance["allowance_number"]}", (6, 4.5), 0.3, align="center", page_width_px=page_width_px)

    #┌---ori_cell_w_1---┬----ori_cell_w_2------┬---ori_cell_w_3----┐
    #│                  │                      │                   │ori_cell_h1
    #│                  ├----------------------┼-------------------┤
    #│                  │                      │                   │ori_cell_h1
    #│                  ├----------------------┼-------------------┤
    #│                  │                      │                   │ori_cell_h1
    #└------------------┴----------------------┴-------------------┘



    y_start_1 = y_start + ori_cell_h
    cell_w_11 = cm_to_px(6.18)
    cell_w_12 = cm_to_px(10.8)
    cell_w_13 = cm_to_px(1.8)
    cell_h_11 = cm_to_px(0.7)

    draw.rectangle([x_start, y_start_1, x_start + cell_w_11 + cell_w_12 + cell_w_13, y_start_1 + cell_h_11], outline="black",width=3)
    draw.line([x_start + cell_w_11, y_start_1, x_start + cell_w_11, y_start_1 + cell_h_11], fill="black",width=3) # straight
    draw.text((x_start + cm_to_px(2), y_start_1 + cm_to_px(0.12)), "開立發票", font=font_header_1, fill="black")

    draw.line([x_start + cell_w_11 + cell_w_12, y_start_1, x_start + cell_w_11 + cell_w_12, y_start_1 + cell_h_11], fill="black",width=3) # straight
    draw.text((x_start + cell_w_11 + cm_to_px(5), y_start_1 + cm_to_px(0.12)), "退貨或折讓內容", font=font_header_1, fill="black")
    draw.text((x_start + cell_w_11 + cell_w_12 + cm_to_px(0.3), y_start_1 + cm_to_px(0.12)), "課稅別(v)", font=font_header_1, fill="black")





    #┌---ori_cell_w_1---┬----ori_cell_w_2------┬---ori_cell_w_3----┐
    #│                  │                      │                   │ori_cell_h1--┐
    #│                  ├----------------------┼-------------------┤             │
    #│                  │                      │                   │ori_cell_h1--┼--ori_cell_h
    #│                  ├----------------------┼-------------------┤             │
    #│                  │                      │                   │ori_cell_h1--┘
    #├------cell_w_11---┴------------┬---------┴-------------------┴----cell_w_12--------------------------------------------------┬--cell_w_13----┐
    #│                               │                                                                                             │               │ cell_h_11
    #├--┬--┬--┬--┬--┬--┬-------------┼-------------------┬----------┬--------┬--------┬------------┬-------------------------------┼----┬---┬------┤

    y_start_2 = y_start_1 + cell_h_11
    cell_w_21 = cm_to_px(0.7)
    cell_w_22 = cell_w_21 + cm_to_px(0.9)
    cell_w_23 = cell_w_22 + cm_to_px(0.7)
    cell_w_24 = cell_w_23 + cm_to_px(0.7)
    cell_w_25 = cell_w_24 + cm_to_px(0.7)
    cell_w_26 = cell_w_25 + cm_to_px(2.5)
    cell_w_27 = cell_w_26 + cm_to_px(3.5)
    cell_w_28 = cell_w_27 + cm_to_px(1.3)
    cell_w_29 = cell_w_28 + cm_to_px(1.5)
    cell_w_210 = cell_w_29 + cm_to_px(2)
    cell_w_211 = cell_w_210 + cm_to_px(2.5)
    cell_w_212 = cell_w_211 + cm_to_px(0.6)
    cell_w_213 = cell_w_212 + cm_to_px(0.6)
    cell_w_214 = cell_w_213 + cm_to_px(0.6)

    cell_h_21= cm_to_px(2.3)

    draw.rectangle([x_start, y_start_2, x_start + cell_w_214, y_start_2 + cell_h_21], outline="black",width=3)
    draw.text((x_start + cm_to_px(0.15), y_start_2 + cm_to_px(0.15)), "一\n般\n/\n特\n種", font=font_header_1, fill="black")

    draw.line([x_start + cell_w_21, y_start_2, x_start + cell_w_21, y_start_2 + cell_h_21], fill="black",width=3) # straight
    draw.text((x_start + cell_w_21 + cm_to_px(0.25), y_start_2 + cm_to_px(1)), "年", font=font_header_1, fill="black")

    draw.line([x_start + cell_w_22, y_start_2, x_start + cell_w_22, y_start_2 + cell_h_21], fill="black",width=3) # straight
    draw.text((x_start + cell_w_22 + cm_to_px(0.17), y_start_2 + cm_to_px(1)), "月", font=font_header_1, fill="black")
    
    draw.line([x_start + cell_w_23, y_start_2, x_start + cell_w_23, y_start_2 + cell_h_21], fill="black",width=3) # straight
    draw.text((x_start + cell_w_23 + cm_to_px(0.17), y_start_2 + cm_to_px(1)), "日", font=font_header_1, fill="black")

    draw.line([x_start + cell_w_24, y_start_2, x_start + cell_w_24, y_start_2 + cell_h_21], fill="black",width=3) # straight
    draw.text((x_start + cell_w_24 + cm_to_px(0.15), y_start_2 + cm_to_px(0.7)), "字\n軌", font=font_header_1, fill="black")

    draw.line([x_start + cell_w_25, y_start_2, x_start + cell_w_25, y_start_2 + cell_h_21], fill="black",width=3) # straight
    draw.text((x_start + cell_w_25 + cm_to_px(1), y_start_2 + cm_to_px(1)), "號碼", font=font_header_1, fill="black")

    draw.line([x_start + cell_w_26, y_start_2, x_start + cell_w_26, y_start_2 + cell_h_21], fill="black",width=3) # straight
    draw.text((x_start + cell_w_26 + cm_to_px(1), y_start_2 + cm_to_px(1)), "品名", font=font_header_1, fill="black")

    draw.line([x_start + cell_w_27, y_start_2, x_start + cell_w_27, y_start_2 + cell_h_21], fill="black",width=3) # straight
    draw.text((x_start + cell_w_27 + cm_to_px(0.25), y_start_2 + cm_to_px(1)), "數量", font=font_header_1, fill="black")

    draw.line([x_start + cell_w_28, y_start_2, x_start + cell_w_28, y_start_2 + cell_h_21], fill="black",width=3) # straight
    draw.text((x_start + cell_w_28 + cm_to_px(0.2), y_start_2 + cm_to_px(1)), "單價", font=font_header_1, fill="black")

    draw.line([x_start + cell_w_29, y_start_2, x_start + cell_w_29, y_start_2 + cell_h_21], fill="black",width=3) # straight
    draw.text((x_start + cell_w_29 + cm_to_px(0.2), y_start_2 + cm_to_px(0.4)), "金額\n(不含稅之\n進貨額)", font=font_header_1, fill="black")

    draw.line([x_start + cell_w_210, y_start_2, x_start + cell_w_210, y_start_2 + cell_h_21], fill="black",width=3) # straight
    draw.text((x_start + cell_w_210 + cm_to_px(0.25), y_start_2 + cm_to_px(1)), "營業稅額", font=font_header_1, fill="black")

    draw.line([x_start + cell_w_211, y_start_2, x_start + cell_w_211, y_start_2 + cell_h_21], fill="black",width=3) # straight
    draw.text((x_start + cell_w_211 + cm_to_px(0.15), y_start_2 + cm_to_px(0.2)), "應\n \n \n \n稅", font=font_header_1, fill="black")

    draw.line([x_start + cell_w_212, y_start_2, x_start + cell_w_212, y_start_2 + cell_h_21], fill="black",width=3) # straight
    draw.text((x_start + cell_w_212 + cm_to_px(0.15), y_start_2 + cm_to_px(0.2)), "零\n \n稅\n \n率", font=font_header_1, fill="black")

    draw.line([x_start + cell_w_213, y_start_2, x_start + cell_w_213, y_start_2 + cell_h_21], fill="black",width=3) # straight
    draw.text((x_start + cell_w_213 + cm_to_px(0.15), y_start_2 + cm_to_px(0.2)), "免\n \n \n \n稅", font=font_header_1, fill="black")

    #┌---ori_cell_w_1---┬----ori_cell_w_2------┬---ori_cell_w_3----┐
    #│                  │                      │                   │ori_cell_h1--┐
    #│                  ├----------------------┼-------------------┤             │
    #│                  │                      │                   │ori_cell_h1--┼--ori_cell_h
    #│                  ├----------------------┼-------------------┤             │
    #│                  │                      │                   │ori_cell_h1--┘
    #├------cell_w_11---┴------------┬---------┴-------------------┴----cell_w_12----------------------┬-------cell_w_13------┐
    #│                               │                                                                 │                      │ cell_h_11
    #├w21┬w22┬w23┬w24┬w25┬---w26-----┼---------w27-------┬----w28---┬---w29----┬---w210 --┬---w211-----┼--w212-┬--w213-┬-w214-┤
    #│   │   │   │   │   │           │                   │          │          │          │            │       │       │      │
    #│   │   │   │   │   │           │                   │          │          │          │            │       │       │      │  cell_h_21
    #│   │   │   │   │   │           │                   │          │          │          │            │       │       │      │
    #└---┴---┴---┴---┴---┴-----------┴-------------------┴----------┴----------┴----------┴------------┴-------┴-------┴------┘

    cell_h_row= cm_to_px(0.7)

    y_start_3 = y_start_2 + cell_h_21
    # 繪製格線
    # draw.rectangle([x_start, y_start_3, x_start + cell_w_214, y_start_3 + cell_h_row], outline="black", width=3)
    # for cell_x in [cell_w_21, cell_w_22, cell_w_23, cell_w_24, cell_w_25, cell_w_26, cell_w_27, cell_w_28, cell_w_29, cell_w_210, cell_w_211, cell_w_212, cell_w_213, cell_w_214]:
    #     draw.line([x_start + cell_x, y_start_2, x_start + cell_x, y_start_2 + cell_h_21], fill="black", width=3)

    # 欄寬與起始 X 計算
    # cell_widths_px = [
    #     cm_to_px(0.5), cm_to_px(0.5), cm_to_px(0.5), cm_to_px(0.5), cm_to_px(0.5),
    #     cm_to_px(2.5), cm_to_px(3.5), cm_to_px(1.3), cm_to_px(1.5), cm_to_px(2),
    #     cm_to_px(2.7), cm_to_px(0.5), cm_to_px(0.5), cm_to_px(0.5)
    # ]

    # x_offsets = [x_start]
    # for w in cell_widths_px[:-1]:
    #     x_offsets.append(x_offsets[-1] + w)

    font_data = get_font(0.5)
    row_height_data = cm_to_px(1)

    #┌---ori_cell_w_1---┬----ori_cell_w_2------┬---ori_cell_w_3----┐
    #│                  │                      │                   │ori_cell_h1--┐
    #│                  ├----------------------┼-------------------┤             │
    #│                  │                      │                   │ori_cell_h1--┼--ori_cell_h
    #│                  ├----------------------┼-------------------┤             │
    #│                  │                      │                   │ori_cell_h1--┘
    #├------cell_w_11---┴------------┬---------┴-------------------┴----cell_w_12----------------------┬-------cell_w_13------┐ --> y_Start_1
    #│                               │                                                                 │                      │ (cell_h_11)
    #├w21┬w22┬w23┬w24┬w25┬---w26-----┼---------w27-------┬----w28---┬---w29----┬---w210 --┬---w211-----┼--w212-┬--w213-┬-w214-┤ --> y_start_2
    #│   │   │   │   │   │           │                   │          │          │          │            │       │       │      │
    #│   │   │   │   │   │           │                   │          │          │          │            │       │       │      │ (cell_h_21)
    #│   │   │   │   │   │           │                   │          │          │          │            │       │       │      │
    #├---┼---┼---┼---┼---┼-----------┼-------------------┼----------┼----------┼----------┼------------┼-------┼-------┼------┤ --> y_start_3
    #│   │   │   │   │   │           │                   │          │          │          │            │       │       │      │ (row_height_data) 
    #├---┼---┼---┼---┼---┼-----------┼-------------------┼----------┼----------┼----------┼------------┼-------┼-------┼------┤   
    #│   │   │   │   │   │           │                   │          │          │          │            │       │       │      │ (row_height_data)
    #├---┼---┼---┼---┼---┼-----------┼-------------------┼----------┼----------┼----------┼------------┼-------┼-------┼------┤

    # Draw data rows

    page_size_limit = 16
    page_data_rows = data_rows[:page_size_limit]
    sales_amount_row_height = cm_to_px(0.7) # 銷售額合計欄位高度
    
    for row_index, row in enumerate(page_data_rows):
        y_top = y_start_3 + row_index * row_height_data
        for col_index, cell_text in enumerate(row):
            x = x_start + sum(cm_to_px(w) for w in column_widths_cm[:col_index])
            width_px = cm_to_px(column_widths_cm[col_index])

            # 畫框線
            draw.rectangle([x, y_top, x + width_px, y_top + row_height_data], outline="black", width=3)

            # 數值欄靠右對齊（第 7~10 欄 index 7~10）
            value_align_right = [7, 8, 9, 10]
            cell_str = str(cell_text)
            w, h = font_data.getbbox(cell_str)[2:]
            if col_index in value_align_right:
                draw.text((x + width_px - w - cm_to_px(0.1), y_top + (row_height_data - h) // 2), cell_str, font=font_header_1, fill="black")
            else:
                draw.text((x + cm_to_px(0.1), y_top + (row_height_data - h) // 2), cell_str, font=font_header_1, fill="black")

    #┌---ori_cell_w_1---┬----ori_cell_w_2------┬---ori_cell_w_3----┐
    #│                  │                      │                   │ori_cell_h1--┐
    #│                  ├----------------------┼-------------------┤             │
    #│                  │                      │                   │ori_cell_h1--┼--ori_cell_h
    #│                  ├----------------------┼-------------------┤             │
    #│                  │                      │                   │ori_cell_h1--┘
    #├------cell_w_11---┴------------┬---------┴-------------------┴----cell_w_12----------------------┬-------cell_w_13------┐ --> y_Start_1
    #│                               │                                                                 │                      │ (cell_h_11)
    #├w21┬w22┬w23┬w24┬w25┬---w26-----┼---------w27-------┬----w28---┬---w29----┬---w210 --┬---w211-----┼--w212-┬--w213-┬-w214-┤ --> y_start_2
    #│   │   │   │   │   │           │                   │          │          │          │            │       │       │      │
    #│   │   │   │   │   │           │                   │          │          │          │            │       │       │      │ (cell_h_21)
    #│   │   │   │   │   │           │                   │          │          │          │            │       │       │      │
    #├---┼---┼---┼---┼---┼-----------┼-------------------┼----------┼----------┼----------┼------------┼-------┼-------┼------┤ --> y_start_3
    #│   │   │   │   │   │           │                   │          │          │          │            │       │       │      │ (row_height_data) 
    #├---┼---┼---┼---┼---┼-----------┼-------------------┼----------┼----------┼----------┼------------┼-------┼-------┼------┤   
    #│   │   │   │   │   │           │                   │          │          │          │            │       │       │      │ (row_height_data)
    #└---┴---┴---┴---┴---┴-----------┴-------------------┴----------┴----------┼----------┼------------┼-------┼-------┼------┤ --> total_y_start
    #│                                                                         │          │            │       │       │      │ (sales_amount_row_height)
    #└-------------------------------------------------------------------------┴----------┴------------┴-------┴-------┴------┘

    total_y_start = y_start_3 + len(data_rows) * row_height_data  # 表頭+明細高度 = total_y_start
    merge_width = sum([cm_to_px(w) for w in column_widths_cm[:9]]) # 前9格的寬度設為merge_width
    cell_w_sales_9 = cm_to_px(column_widths_cm[9]) # sales amount 欄位寬度同第9欄寬度
    cell_w_sales_10 = cm_to_px(column_widths_cm[10]) # sales amount 欄位寬度同第9欄寬度

    draw.rectangle([x_start, total_y_start, x_start + merge_width, total_y_start + sales_amount_row_height], outline="black",width=3)
    draw.text((x_start + cm_to_px(0.1), total_y_start + cm_to_px(0.1)), "合     計", font=font_header_1, fill="black")

    w, h = draw.textbbox((0, 0), decimal_to_str_trimmed(total_amount), font=font_header_1)[2:]
    draw.rectangle([x_start + merge_width, total_y_start, x_start + cell_w_210, total_y_start + sales_amount_row_height], outline="black",width=3)
    draw.text((x_start + merge_width + cell_w_sales_9 - w - cm_to_px(0.1), total_y_start + cm_to_px(0.1)), decimal_to_str_trimmed(total_amount), font=font_header_1, fill="black")
    
    w, h = draw.textbbox((0, 0), decimal_to_str_trimmed(total_tax_amount), font=font_header_1)[2:]
    draw.rectangle([x_start + cell_w_210, total_y_start, x_start + cell_w_211, total_y_start + sales_amount_row_height], outline="black",width=3)
    draw.text((x_start + cell_w_210 + cell_w_sales_10 - w - cm_to_px(0.1), total_y_start + cm_to_px(0.1)), decimal_to_str_trimmed(total_tax_amount), font=font_header_1, fill="black")
    
    draw.rectangle([x_start + cell_w_211, total_y_start, x_start + cell_w_214, total_y_start + sales_amount_row_height], outline="black",width=3)
    draw.text((x_start, total_y_start +  sales_amount_row_height + cm_to_px(0.1)), "本證明單所列或退出或折讓，確屬事實，特此證明。", font=font_header_1, fill="black")
    draw.text((x_start, total_y_start + sales_amount_row_height + cm_to_px(0.6)), "簽收人：", font=font_header_1, fill="black")
    
    draw.rectangle([x_start + cell_w_29 , total_y_start + sales_amount_row_height + cm_to_px(0.1) , x_start + cell_w_214, total_y_start + sales_amount_row_height+ cm_to_px(0.7)], outline="black",width=3)
    draw.text((x_start + cell_w_29 + cm_to_px(0.5), total_y_start +sales_amount_row_height+cm_to_px(0.15)), "進貨營業人(或原買受人)蓋統一發票專用章", font=font_header_1, fill="black")
    
    draw.rectangle([x_start + cell_w_29 , total_y_start + sales_amount_row_height + cm_to_px(0.7) , x_start + cell_w_214, total_y_start + sales_amount_row_height+ cm_to_px(3) ], outline="black",width=3)    
    
    label = f"賣       方：{company_name}"
    wrap_text_fn(draw, label, x_start + merge_width + cm_to_px(0.1), total_y_start + sales_amount_row_height + cm_to_px(1.1), font=font_total, max_width_px=cell_w_214-cell_w_29 - cm_to_px(0.2))    
    
    draw.text((x_start + merge_width + cm_to_px(0.1), total_y_start + sales_amount_row_height + cm_to_px(1.6)+ cm_to_px(0.1)), f"統一編號: {company_identifier}", font=font_total, fill="black")
    
    address_label = f"地       址：{company_address}"
    wrap_text_fn(draw, address_label, x_start + merge_width + cm_to_px(0.1), total_y_start + sales_amount_row_height + cm_to_px(2.1) + cm_to_px(0.2), font=font_total, max_width_px=cell_w_214-cell_w_29 - cm_to_px(0.2))


# def draw_table_other_page(draw, start_cm, column_widths_cm, headers, data_rows,  page_num=2, total_pages=1, wrap_text_fn=draw_wrapped_text):
#     page_width_px = cm_to_px(21.0)
#     draw_text(draw, f"發票號碼: {demo_allowance['invoice_number']}", (1.3, 2.7), 0.5)
#     draw_text(draw, demo_allowance['invoice_date'].strftime('%Y-%m-%d'), (0, 1.6), 0.6, align="center", page_width_px=page_width_px)
#     x_start = cm_to_px(start_cm[0])
#     y_start = cm_to_px(start_cm[1])
#     row_height_header = cm_to_px(0.7)
#     row_height_data = cm_to_px(1.2)
#     font_header = get_font(0.5, bold=True)
#     font_data = get_font(0.5)
#     page_size_limit = 20
#     page_data_rows = data_rows[:page_size_limit]
#     while len(page_data_rows) < page_size_limit:
#         page_data_rows.append(["" for _ in column_widths_cm])

#     # Draw headers
#     current_x = x_start
#     for width_cm, header in zip(column_widths_cm, headers):
#         cell_w = cm_to_px(width_cm)
#         w, h = draw.textbbox((0, 0), header, font=font_header)[2:]
#         draw.text((current_x + (cell_w - w) // 2, y_start + (row_height_header - h) // 2), header, font=font_header, fill="black")
#         draw.rectangle([current_x, y_start, current_x + cell_w, y_start + row_height_header], outline="black", width=3)
#         current_x += cell_w

#     for i in range(len(column_widths_cm) + 1):
#         x = x_start + sum([cm_to_px(w) for w in column_widths_cm[:i]])
#         draw.line([x, y_start + row_height_header, x, y_start + row_height_header + len(page_data_rows) * row_height_data], fill="black", width=3)

#     # Draw data rows
#     for row_index, row in enumerate(page_data_rows):
#         current_x = x_start
#         current_y = y_start + row_height_header + row_index * row_height_data
#         for col_index, (col, width_cm) in enumerate(zip(row, column_widths_cm)):
#             cell_w = cm_to_px(width_cm)
#             w, h = draw.textbbox((0, 0), str(col), font=font_data)[2:]
#             if col_index in [1, 2, 3]:
#                 draw.text((current_x + cell_w - w - cm_to_px(0.1), current_y + (row_height_data - h) // 2), str(col), font=font_data, fill="black")
#             else:
#                 draw.text((current_x + cm_to_px(0.1), current_y + (row_height_data - h) // 2), str(col), font=font_data, fill="black")
#             current_x += cell_w

#     # Draw bottom line of the table
#     bottom_y = y_start + row_height_header + len(page_data_rows) * row_height_data
#     draw.line([x_start, bottom_y, x_start + sum([cm_to_px(w) for w in column_widths_cm]), bottom_y], fill="black", width=3)

#     return data_rows[page_size_limit:]

# ==== 主要流程：繪製與合併 PDF ====
def render_and_merge_invoices(allowance, output_folder, column_widths_cm, headers, all_data_rows,
                               total_amount, total_tax_amount, company_name,
                               company_identifier, company_address,wrap_text_fn=draw_wrapped_text):
    

    dpi = 300
    page_w, page_h = cm_to_px(21), cm_to_px(29.7)
    page_files = []
    page_num = 1

    # 第一頁最多14筆
    first_page_rows = all_data_rows[:16]
    while len(first_page_rows) < 16:
        first_page_rows.append(["" for _ in column_widths_cm])
    img = Image.new("RGB", (page_w, page_h), "white")
    draw = ImageDraw.Draw(img)
    draw_table_first_page(allowance, img, draw, (1.3, 1), column_widths_cm, headers, first_page_rows,
                            total_tax_amount,  total_amount, company_name,
                          company_identifier, company_address, wrap_text_fn)
    # page1_path = os.path.join(output_folder, f"page{page_num}.pdf")
    # img.save(page1_path, "PDF", resolution=dpi)
    #page_files.append(page1_path)
    #page_num += 1

    # 後續每頁最多20筆
    # remaining_rows = all_data_rows[14:]
    # while remaining_rows:
    #     img = Image.new("RGB", (page_w, page_h), "white")
    #     draw = ImageDraw.Draw(img)
    #     total_pages = (len(all_data_rows) - 14 + 19) // 20 + 1
    #     draw_text(draw, f"第{page_num}頁/共{total_pages}頁", (17.2, 2.7), 0.5)
    #     remaining_rows = draw_table_other_page(draw, (1.3, 3.5), column_widths_cm, headers, remaining_rows, page_num, total_pages)
    #     page_path = os.path.join(output_folder, f"page{page_num}.pdf")
    #     img.save(page_path, "PDF", resolution=dpi)
    #     page_files.append(page_path)
    #     page_num += 1

    # # 合併所有 PDF 頁
    # merger = PdfMerger()
    # for pdf in page_files:
    #     merger.append(pdf)
    invoice_filename = f"{allowance.allowance_number}_{allowance.company.company_identifier}_{allowance.allowance_date.strftime('%Y%m%d')}.pdf"
    merged_path = os.path.join(output_folder, invoice_filename)
    # merger.write(merged_path)
    # merger.close()
    
    # # 刪除中間產出的分頁 PDF
    # for pdf in page_files:
    #     if os.path.exists(pdf):
    #         os.remove(pdf)

    # ✅ 存檔：直接以 final name 儲存
    img.save(merged_path, "PDF", resolution=dpi)
    return merged_path


def generate_allowance_pdf(allowance, output_folder):

    column_widths = [0.7, 0.9, 0.7, 0.7, 0.7, 2.5, 3.5, 1.3, 1.5, 2, 2.5, 0.6, 0.6, 0.6]
    headers = ["一\n般\n/\n特\n種", "年", "月", "日", "字\n軌","號碼", "品名", "數量", "單價", "金額\n(不含稅之\n進貨額)", "營業稅額" , "應\n \n \n \n稅" ,"零\n \n稅\n \n率", "免\n \n \n \n稅"]


    all_items = []
    if hasattr(allowance, "items"):
        for idx, item in enumerate(allowance.items.all()):
            type = "一"
            original_invoice_date_year = str(item.line_original_invoice_date.year - 1911)
            original_invoice_date_month = str(item.line_original_invoice_date.month)
            original_invoice_date_day = str(item.line_original_invoice_date.day)
            original_invoice_numbr_alphabet = str(item.line_original_invoice_number)[:2]
            original_invoice_numbr = str(item.line_original_invoice_number)[2:]
            description = f"{item.line_description}"
            quantity = str(item.line_quantity)
            unit_price = decimal_to_str_trimmed(item.line_unit_price)
            # 如果沒有 line_amount 欄位就用下面這行計算
            amount = decimal_to_str_trimmed(item.line_allowance_amount)
            tax = decimal_to_str_trimmed(item.line_allowance_tax)
            tax_type = str(item.line_tax_type)
            if tax_type == "1":
                tax_mark = ["v", "", ""]
            elif tax_type == "2":
                tax_mark = ["", "v", ""]
            elif tax_type == "3":
                tax_mark = ["", "", "v"]
            else:
                tax_mark = ["", "", ""]  # fallback, unexpected tax_type
            all_items.append([type, original_invoice_date_year,original_invoice_date_month ,original_invoice_date_day, original_invoice_numbr_alphabet, original_invoice_numbr, description, quantity, unit_price, amount, tax, *tax_mark])

    return render_and_merge_invoices(
        allowance=allowance,
        output_folder=output_folder,
        column_widths_cm=column_widths,
        headers=headers,
        all_data_rows=all_items,
        total_amount=allowance.allowance_amount,
        total_tax_amount=allowance.allowance_tax,
        company_name=allowance.company.company_name,
        company_identifier=allowance.company.company_identifier,
        company_address=allowance.company.company_address,
    )
