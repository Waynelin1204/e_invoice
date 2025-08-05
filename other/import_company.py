import pandas as pd
from e_invoices.models import Company
from django.db import transaction

# 載入 Excel 檔案
df = pd.read_excel('營業人表單.xlsx')

# 將空值轉為 None（避免 NaN 出錯）
df = df.where(pd.notnull(df), None)

with transaction.atomic():
    for _, row in df.iterrows():
        # 當 id 是 NaN 或空時，跳過這一筆
        if pd.isna(row['id']):
            print(f"⚠️ 跳過一筆因 id 為空的資料，資料: {row}")
            continue  # 跳過這一列

        # 嘗試取得 head_company_identifer 關聯對象
        head_company = None
        if row['head_company_identifer_id']:
            try:
                head_company = Company.objects.get(id=row['head_company_identifer_id'])
            except Company.DoesNotExist:
                print(f"❌ 找不到主公司 ID: {row['head_company_identifer_id']}，該筆將略過關聯")

        # 寫入或更新 Company 資料
        try:
            Company.objects.update_or_create(
                id=int(row['id']),  # 確保 id 是數字，防止 NaN 或非數字輸入
                defaults={
                    "company_register_name": row['company_register_name'],
                    "company_identifier": row['company_identifier'],
                    "company_name": row['company_name'],
                    "company_address": row['company_address'],
                    "company_type": row['company_type'],
                    "tax_identifer": row['tax_identifer'],
                    "company_id": row['company_id'],
                    "is_foreign_ecomm": bool(row['is_foreign_ecomm']),
                    "email": row['email'],
                    "reporting_period": row['reporting_period'],
                    "head_company_identifer": head_company
                }
            )
        except Exception as e:
            print(f"❌ 第 {_+2} 行資料處理錯誤：{e}")

print("✅ 公司資料匯入完成！")
