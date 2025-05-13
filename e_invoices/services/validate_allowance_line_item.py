from django.db.models import Sum
from e_invoices.models import TWAllowanceLineItem, TWB2BMainItem
from django.shortcuts import render, redirect, get_object_or_404

from django.db.models import Sum

def validate_allowance_line_item(line_item):
    """
    驗證折讓單項目，計算相關發票的剩餘可折讓金額和稅額，並檢查是否有效。
    """
    invoice = line_item.linked_invoice  # 關聯的發票

    if not invoice:
        return {
            "is_valid_amount": False,
            "is_valid_tax": False,
            "remaining_allowance_amount": 0,
            "remaining_allowance_tax": 0,
            "total_deducted_amount": 0,
            "total_deducted_tax": 0,
        }

    # 使用反向關聯計算該發票已被折讓的總金額和稅額
    aggregated_data = invoice.allowance_lineitems.aggregate(
        total_deducted_amount=Sum('line_allowance_amount'),
        total_deducted_tax=Sum('line_allowance_tax')
    )
    total_deducted_amount = aggregated_data.get('total_deducted_amount') or 0
    total_deducted_tax = aggregated_data.get('total_deducted_tax') or 0

    # 計算剩餘可折讓金額和稅額
    invoice_total_amount = (
        (invoice.sales_amount or 0)
        + (invoice.zerotax_sales_amount or 0)
        + (invoice.freetax_sales_amount or 0)
    )
    remaining_allowance_amount = max(invoice_total_amount - total_deducted_amount, 0)
    remaining_allowance_tax = max((invoice.total_tax_amount or 0) - total_deducted_tax, 0)

    # 檢查折讓金額和稅額是否有效
    is_valid_amount = line_item.line_allowance_amount <= remaining_allowance_amount
    is_valid_tax = line_item.line_allowance_tax <= remaining_allowance_tax

    return {
        "is_valid_amount": is_valid_amount,
        "is_valid_tax": is_valid_tax,
        "remaining_allowance_amount": remaining_allowance_amount,
        "remaining_allowance_tax": remaining_allowance_tax,
        "total_deducted_amount": total_deducted_amount,
        "total_deducted_tax": total_deducted_tax,
    }