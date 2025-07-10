import os
import xml.etree.ElementTree as ET
from django.db import transaction
from e_invoices.models import NumberDistribution  # 模型名稱建議首字大寫單數形式

def process_all_e0501_xml():
    xml_folder_path = r"C:\Users\waylin\mydjango\e_invoice\download\invoice_no"
    ns = {'e0501': 'urn:GEINV:E0501:4.0'}
    files = [f for f in os.listdir(xml_folder_path) if f.lower().endswith('.xml')]
    
    for filename in files:
        full_path = os.path.join(xml_folder_path, filename)
        try:
            tree = ET.parse(full_path)
            root = tree.getroot()

            # 解析 E0501 內容
            ban = root.find('e0501:Ban', ns).text.strip()
            invoice_type = root.find('e0501:InvoiceType', ns).text.strip()
            period = root.find('e0501:YearMonth', ns).text.strip()
            initial_char = root.find('e0501:InvoiceTrack', ns).text.strip()
            start_number = root.find('e0501:InvoiceBeginNo', ns).text.strip()
            end_number = root.find('e0501:InvoiceEndNo', ns).text.strip()
            invoice_booklet = root.find('e0501:InvoiceBooklet', ns).text.strip()

            print(f"解析結果：")
            print(f"營業人統編: {ban}")
            print(f"發票類別: {invoice_type}")
            print(f"期別: {period}")
            print(f"字軌: {initial_char}")
            print(f"起號: {start_number}")
            print(f"迄號: {end_number}")
            print(f"冊數: {invoice_booklet}")

            with transaction.atomic():
                start_no = int(start_number)
                end_no = int(end_number)

                for num in range(start_no, end_no + 1):
                    inv_num = f"{num:08d}"
                    if not NumberDistribution.objects.filter(
                        company_identifier=ban,
                        invoice_number=inv_num
                    ).exists():
                        NumberDistribution.objects.create(
                            company_identifier=ban,
                            invoice_number=inv_num,
                            invoice_type=invoice_type,
                            initial_char=initial_char,
                            period=period
                        )
                        print(f"已建立發票號碼 {inv_num} 的主檔資料。")
                    else:
                        print(f"發票號碼 {inv_num} 已存在，跳過。")
        except Exception as e:
            print(f"處理檔案 {filename} 時發生錯誤: {e}")
