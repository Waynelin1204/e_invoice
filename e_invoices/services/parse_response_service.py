import os
import xml.etree.ElementTree as ET
from django.db import transaction
from e_invoices.models import TWB2BMainItem

def process_all_processresult_xml():
    xml_folder_path = r"C:\Users\waylin\mydjango\e_invoice\download"
    ns = {'pr': 'urn:GEINV:ProcessResult:4.0'}
    files = [f for f in os.listdir(xml_folder_path) if f.lower().endswith('.xml')]
    for filename in files:
        full_path = os.path.join(xml_folder_path, filename)
        try:
            tree = ET.parse(full_path)
            root = tree.getroot()
            seller_id = root.find('.//pr:RoutingInfo/pr:From/pr:Id', ns).text.strip()
            infos = root.findall('.//pr:Result/pr:Info', ns)

            with transaction.atomic():
                for info in infos:
                    invoice_number = info.find('pr:Parameter0', ns).text.strip()
                    mof_date = info.find('pr:Parameter1', ns).text.strip()
                    mof_response = info.find('pr:Code', ns).text.strip()
                    mof_reason = info.find('pr:Description', ns).text.strip()

                    try:
                        main_item = TWB2BMainItem.objects.get(
                            company_identifier=seller_id,
                            invoice_number=invoice_number
                        )
                        main_item.mof_response = mof_response
                        main_item.mof_reason = mof_reason
                        main_item.mof_date = mof_date
                        main_item.save()
                        print(f"更新發票 {invoice_number}，賣家ID {seller_id}，狀態: {mof_response}，原因: {mof_reason}，日期: {mof_date}")
                    except TWB2BMainItem.DoesNotExist:
                        print(f"找不到發票號碼 {invoice_number} 與賣家ID {seller_id} 的資料，跳過。")
        except Exception as e:
            print(f"處理檔案 {filename} 時發生錯誤: {e}")
