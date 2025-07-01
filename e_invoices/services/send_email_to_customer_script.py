from datetime import datetime, timedelta
from e_invoices.models import TWB2BMainItem
from e_invoices.services import send_invoice_summary_to_customer_email

def auto_send_invoice_summary_email():
    """
    搜尋 TWB2BMainItem 符合條件的資料並自動寄信
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=2)

    # 查詢兩天內 mof_reason = 'S0001' 的主表資料
    queryset = TWB2BMainItem.objects.filter(
        mof_reason="S0001",
        sys_date__range=(start_date, end_date)
    )

    for main in queryset:
        items = main.items.all()
        if not items.exists():
            print(f"ID {main.id} 無明細資料，已跳過")
            continue

        item = items.first()

        # 呼叫寄信函式
        send_invoice_summary_to_customer_email(
            to_email=main.buyer_email,
            buyer_name=main.buyer_name,
            invoice_date=main.invoice_date,
            invoice_time=main.invoice_time if main.invoice_time else '',
            random_code=main.random_code,
            total_amount=main.total_amount,
            buyer_identifier=main.buyer_identifier,
            line_description=item.line_description,
            line_quantity=item.line_quantity,
            unit_price=item.line_unit_price
        )

    print(f"已寄出發票通知給 {main.buyer_email} (Main ID: {main.id})")
