import os
import sqlite3
import pandas as pd
import glob

# Path to the folder containing Excel files
downloads_folder = os.path.expanduser("C:/Users/waylin/mydjango/e_invoice/upload")
# Get all .xlsx files in the folder
excel_files = glob.glob(os.path.join(downloads_folder, "*.xlsx"))

# Insert data into a specific table in SQLite database
def insert_data_to_table(parsed_result, table_name, connection):
    """
    將解析後的資料插入指定的 SQLite 資料表中
    :param parsed_result: 要插入的資料，應為列表格式
    :param table_name: 要插入資料的資料表名稱
    :param connection: SQLite 資料庫的連接物件
    """
    with connection.cursor() as cursor:
        if table_name == "twb2bmainitem":
            cursor.execute("""
                INSERT INTO twb2bmainitem (
                    company, company_code, b2b_b2c, sys_number, sys_date, invoice_number, 
                    invoice_date, invoice_time, invoice_period, invoice_type, erp_number, 
                    erp_date, erp_reference, company_identifier, seller_bp_id, tax_identifier, 
                    seller_name, buyer_identifier, buyer_name, buyer_bp_id, buyer_remark, 
                    main_remark, group_mark, donate_mark, customs_clearance_mark, category, 
                    relate_number, bonded_area_confirm, zero_tax_rate_reason, reserved1, 
                    reserved2, sales_amount, freetax_sales_amount, zerotax_sales_amount, tax_type, 
                    tax_rate, total_tax_amount, total_amount, original_currency_amount, exchange_rate, 
                    currency, invoice_status, description, remark, discount_amount, payment_status, 
                    void_status, mof_date, mof_respone, mof_reason, creator, creator_remark)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                parsed_result["company"], parsed_result["company_code"], parsed_result["b2b_b2c"], parsed_result["sys_number"], 
                parsed_result["sys_date"], parsed_result["invoice_number"], parsed_result["invoice_date"], 
                parsed_result["invoice_time"], parsed_result["invoice_period"], parsed_result["invoice_type"], 
                parsed_result["erp_number"], parsed_result["erp_date"], parsed_result["erp_reference"], 
                parsed_result["company_identifier"], parsed_result["seller_bp_id"], parsed_result["tax_identifier"], 
                parsed_result["seller_name"], parsed_result["buyer_identifier"], parsed_result["buyer_name"], 
                parsed_result["buyer_bp_id"], parsed_result["buyer_remark"], parsed_result["main_remark"], 
                parsed_result["group_mark"], parsed_result["donate_mark"], parsed_result["customs_clearance_mark"], 
                parsed_result["category"], parsed_result["relate_number"], parsed_result["bonded_area_confirm"], 
                parsed_result["zero_tax_rate_reason"], parsed_result["reserved1"], parsed_result["reserved2"], 
                parsed_result["sales_amount"], parsed_result["freetax_sales_amount"], parsed_result["zerotax_sales_amount"], 
                parsed_result["tax_type"], parsed_result["tax_rate"], parsed_result["total_tax_amount"], 
                parsed_result["total_amount"], parsed_result["original_currency_amount"], parsed_result["exchange_rate"], 
                parsed_result["currency"], parsed_result["invoice_status"], parsed_result["description"], 
                parsed_result["remark"], parsed_result["discount_amount"], parsed_result["payment_status"], 
                parsed_result["void_status"], parsed_result["mof_date"], parsed_result["mof_respone"], 
                parsed_result["mof_reason"], parsed_result["creator"], parsed_result["creator_remark"]
            ))
        elif table_name == "twb2blineitem":
            cursor.execute("""
                INSERT INTO twb2blineitem (
                    twb2bmainitem_id, line_description, line_tax_type, line_quantity, line_unit, 
                    line_unit_price, line_amount, line_remark, line_sequence_number, 
                    line_relate_number, line_tax_amount, line_sales_amount
                ) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                parsed_result["twb2bmainitem_id"], parsed_result["line_description"], parsed_result["line_tax_type"], 
                parsed_result["line_quantity"], parsed_result["line_unit"], parsed_result["line_unit_price"], 
                parsed_result["line_amount"], parsed_result["line_remark"], parsed_result["line_sequence_number"], 
                parsed_result["line_relate_number"], parsed_result["line_tax_amount"], parsed_result["line_sales_amount"]
            ))
        connection.commit()

# 驗證和處理 Excel 資料
def validate_and_process(df):
    """
    驗證 Excel 資料並處理有效與無效資料
    :param df: 從 Excel 讀取的 DataFrame
    :return: valid_data (有效資料), invalid_data (無效資料)
    """
    valid_data = []  # 儲存符合條件的有效資料
    invalid_data = []  # 儲存不符合條件的無效資料

    for index, row in df.iterrows():
        if row['ERP_number'] in [1, 2]:  # 假設 ERP_number 為 1 或 2 為有效
            valid_data.append(row)
        else:
            invalid_data.append(row)

    # 處理有效資料
    if valid_data:
        valid_df = pd.DataFrame(valid_data)
        grouped_df = valid_df.groupby("ERP_number", as_index=False).agg({
            "ERP_date": "first", 
            "ERP_reference": "first", 
            "seller_tax_id": "first", 
            "seller_bp_id": "first", 
            "buyer_tax_id": "first", 
            "buyer_name": "first"
        })

        valid_parsed_result = grouped_df[["ERP_number", "ERP_year", "ERP_date", "ERP_reference", "invoice_period",
                                          "seller_tax_id", "seller_bp_id", "buyer_tax_id", "buyer_name"]].values.tolist()

        for row in valid_parsed_result:
            if row[0] == 1:
                table_name = "twb2bmainitem"  # 插入主表
            elif row[0] == 2:
                table_name = "twb2blineitem"  # 插入行項表
            insert_data_to_table(row, table_name, conn)

    return valid_data, invalid_data

# 解析和插入 Excel 檔案的資料
def parse_and_insert():
    """
    這個函數負責處理所有的 Excel 檔案，並將資料插入資料庫
    """
    for excel_file_path in excel_files:
        print(f"Processing file: {excel_file_path}")
        df = pd.read_excel(excel_file_path)

        # 檢查是否包含所有必要的欄位
        if not all(col in df.columns for col in required_columns):
            print(f"Missing required columns in file: {excel_file_path}")
            continue

        valid_data, invalid_data = validate_and_process(df)

        # 插入無效資料到錯誤資料表
        if invalid_data:
            for row in invalid_data:
                insert_data_to_table(row[required_columns].tolist(), "error_table", conn)

    print("All data from Excel files have been processed and inserted into the database!")

if __name__ == "__main__":
    conn = sqlite3.connect("C:/Users/waylin/mydjango/e_invoice/db.sqlite3")
    parse_and_insert()
    conn.close()
