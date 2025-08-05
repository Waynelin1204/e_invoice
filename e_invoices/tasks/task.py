# e_invoices/tasks.py
from celery import shared_task
from e_invoices.services import process_all_E0502_xml  # 放你主邏輯的檔案

@shared_task
def run_e0502_parsing_task():
    process_all_E0502_xml()
    print("E0502 XML 處理完成")
    return "E0502 XML 處理完成"