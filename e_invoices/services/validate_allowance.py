from django.db.models import Sum
from e_invoices.models import TWAllowanceLineItem, TWB2BMainItem
from django.shortcuts import render, redirect, get_object_or_404
from collections import defaultdict
from django.db.models import Sum

def validate_allowance(allowances):
    all_items = TWAllowanceLineItem.objects.filter(linked_invoice__isnull=False)
    invoice_deducted_map = defaultdict(lambda: {'total_deducted_amount': 0, 'total_deducted_tax': 0})
    invoice_map = {}

    # 統計所有發票已折讓金額
    for item in all_items:
        inv = item.linked_invoice
        invoice_number = inv.invoice_number
        invoice_deducted_map[invoice_number]['total_deducted_amount'] += item.line_allowance_amount or 0
        invoice_deducted_map[invoice_number]['total_deducted_tax'] += item.line_allowance_tax or 0
        invoice_map[invoice_number] = inv

    # 找出超額的發票
    overused_invoices = set()
    for invoice_number, deducted in invoice_deducted_map.items():
        invoice = invoice_map[invoice_number]
        original_amount = (
            (invoice.sales_amount or 0) +
            (invoice.zerotax_sales_amount or 0) +
            (invoice.freetax_sales_amount or 0)
        )
        original_tax = invoice.total_tax_amount or 0

        if (
            deducted['total_deducted_amount'] > original_amount or
            deducted['total_deducted_tax'] > original_tax
        ):
            overused_invoices.add(invoice_number)

    invoice_remaining_amounts = {}
    invoice_remaining_taxes = {}

    # 驗證折讓單與明細
    results = []
    for allowance in allowances:
        validated_items = []
        is_allowance_valid = True
        is_valid_amount = True
        is_valid_tax = True

        for item in allowance.items.all():
            invoice = item.linked_invoice
            if not invoice:
                # 無關聯發票，自動視為無效
                validated_items.append({
                    'item': item,
                    'is_valid_amount': False,
                    'is_valid_tax': False,
                    'remaining_allowance_amount': 0,
                    'remaining_allowance_tax': 0,
                })
                is_allowance_valid = False
                is_valid_amount = False
                is_valid_tax = False
                continue

            invoice_number = invoice.invoice_number
            is_item_valid_amount = invoice_number not in overused_invoices
            is_item_valid_tax = invoice_number not in overused_invoices

            if not is_item_valid_amount:
                is_valid_amount = False
            if not is_item_valid_tax:
                is_valid_tax = False
            if not (is_item_valid_amount and is_item_valid_tax):
                is_allowance_valid = False

            deducted = invoice_deducted_map.get(invoice_number, {
                'total_deducted_amount': 0,
                'total_deducted_tax': 0
            })
            original_amount = (
                (invoice.sales_amount or 0) +
                (invoice.zerotax_sales_amount or 0) +
                (invoice.freetax_sales_amount or 0)
            )
            original_tax = invoice.total_tax_amount or 0




            remaining_amount = original_amount - deducted['total_deducted_amount']
            remaining_tax = original_tax - deducted['total_deducted_tax']
            # 放入字典，以 invoice_number 為 key
            invoice_remaining_amounts[invoice_number] = remaining_amount
            invoice_remaining_taxes[invoice_number] = remaining_tax

            validated_items.append({
                'item': item,
                'is_valid_amount': is_item_valid_amount,
                'is_valid_tax': is_item_valid_tax,
                'remaining_allowance_amount': remaining_amount,
                'remaining_allowance_tax': remaining_tax,
            })

        results.append({
            'allowance': allowance,
            'is_allowance_valid': is_allowance_valid,
            'is_valid_amount': is_valid_amount,
            'is_valid_tax': is_valid_tax,
            'validated_items': validated_items,
            'invoice_remaining_amounts': invoice_remaining_amounts,
            'invoice_remaining_taxes': invoice_remaining_taxes,
        })

    return results





# def validate_allowance(allowance):
#     """
#     驗證折讓單及其所有明細項目。
#     如果任何一筆明細項目不通過，整張折讓單被視為不通過。
#     """
#     is_allowance_valid = True  # 預設折讓單為通過
#     validated_items = []
#     is_valid_amount = True
#     is_valid_tax = True

#     for line_item in allowance.items.all():
#         invoice = line_item.linked_invoice  # 關聯的發票

#         if not invoice:
#             # 如果沒有對應的發票，該明細項目不通過
#             validated_items.append({
#                 "item": line_item,
#                 "is_valid_amount": False,
#                 "is_valid_tax": False,
#                 "remaining_allowance_amount": 0,
#                 "remaining_allowance_tax": 0,
#             })
#             is_allowance_valid = False
#             continue

#         # 計算該發票已被折讓的總金額和稅額
#         aggregated_data = invoice.allowance_lineitems.aggregate(
#             total_deducted_amount=Sum('line_allowance_amount'),
#             total_deducted_tax=Sum('line_allowance_tax')
#         )
#         total_deducted_amount = aggregated_data.get('total_deducted_amount') or 0
#         total_deducted_tax = aggregated_data.get('total_deducted_tax') or 0

#         # 計算剩餘可折讓金額和稅額
#         invoice_total_amount = (
#             (invoice.sales_amount or 0)
#             + (invoice.zerotax_sales_amount or 0)
#             + (invoice.freetax_sales_amount or 0)
#         )
#         remaining_allowance_amount = invoice_total_amount - total_deducted_amount
#         remaining_allowance_tax = (invoice.total_tax_amount or 0) - total_deducted_tax

#         # 檢查折讓金額和稅額是否有效
#         item_is_valid_amount = remaining_allowance_amount >= 0
#         item_is_valid_tax = remaining_allowance_tax >= 0

#         # 如果任何一個條件不通過，整張折讓單不通過
#         if not item_is_valid_amount:
#             is_valid_amount = False
#         if not item_is_valid_tax:
#             is_valid_tax = False
#         if not item_is_valid_amount or not item_is_valid_tax:
#             is_allowance_valid = False

#         # 保存每個明細項目的驗證結果
#         validated_items.append({
#             "item": line_item,
#             "is_valid_amount": item_is_valid_amount,
#             "is_valid_tax": item_is_valid_tax,
#             "remaining_allowance_amount": remaining_allowance_amount,
#             "remaining_allowance_tax": remaining_allowance_tax,
#         })


#     return {
#         "is_allowance_valid": is_allowance_valid,
#         "is_valid_amount": is_valid_amount,
#         "is_valid_tax": is_valid_tax,
#         "validated_items": validated_items,
#     }