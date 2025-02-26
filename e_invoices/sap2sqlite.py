import os
import sqlite3
import json
import pandas as pd
from datetime import datetime

# 讀取 JSON 檔案
json_file_path = os.path.expanduser("/home/pi/Downloads/SAP/SAP_FAGLL03.json")
with open(json_file_path, "r", encoding="utf-8") as file:
    json_data = json.load(file)

# 轉換為 pandas DataFrame
df = pd.DataFrame(json_data)

# 確保數據類型正確
df["Document Number"] = df["Document Number"].astype(int)
df["Amount in Doc. Curr."] = df["Amount in Doc. Curr."].astype(float)
df["Amount in LC"] = df["Amount in LC"].astype(float)
df["Posting Date"] = df["Posting Date"].apply(lambda x:datetime.utcfromtimestamp(x/1000).strftime("%Y-%m-%d"))

# 按 Document Number 分組並進行求和
grouped_df = df.groupby("Document Number", as_index=False).agg({
    "Tax Code": "first",  # 取得第一個值
    "Document type": "first",  # 取得第一個值
    "Posting Date": "first",  # 取得第一個值
    "Document Currency": "first",  # 取得第一個值
    "Amount in Doc. Curr.": "sum",  # 金額求和
    "Local Currency": "first",  # 取得第一個值
    "Amount in LC": "sum",  # 金額求和
    "Reference": "first",  # 取得第一個值
    "Offsetting Account": "first"  # 取得第一個值
})

def calculate_including_tax(row):
	amount = row["Amount in Doc. Curr."]
	if row["Tax Code"] == "A1":
		return round(abs(amount * 1.05),2)
	return round(abs(amount),2)

grouped_df["Including Tax Amount"] = grouped_df.apply(calculate_including_tax, axis=1)

# 連接 SQLite
conn = sqlite3.connect("/home/pi/mydjango/e_invoice/db.sqlite3")
cursor = conn.cursor()

# 創建表格（如果尚未存在）
cursor.execute('''
    CREATE TABLE IF NOT EXISTS e_invoices_sapfagll03 (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        document_number INTEGER,
        tax_code TEXT,
        document_type TEXT,
        posting_date INTEGER,
        document_currency TEXT,
        amount_in_doc_curr REAL,
        local_currency TEXT,
        amount_in_lc REAL,
        reference TEXT,
        offsetting_account TEXT,
        including_tax_amount REAL
    )
''')

# 插入合併後的數據
grouped_data = grouped_df.to_dict(orient="records")
for record in grouped_data:
    cursor.execute('''
        INSERT INTO e_invoices_sapfagll03 (
            document_number,
            tax_code,
            document_type,
            posting_date,
            document_currency,
            amount_in_doc_curr,
            local_currency,
            amount_in_lc,
            reference,
            offsetting_account,
            including_tax_amount
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        record["Document Number"],
        record["Tax Code"],
        record["Document type"],
        record["Posting Date"],
        record["Document Currency"],
        record["Amount in Doc. Curr."],
        record["Local Currency"],
        record["Amount in LC"],
        record["Reference"],
        record["Offsetting Account"],
        record["Including Tax Amount"]
    ))

# 提交更改並關閉連接
conn.commit()
conn.close()

print(f"✅ 成功將合併後的 {len(grouped_data)} 筆數據插入到 SQLite 資料庫！")
