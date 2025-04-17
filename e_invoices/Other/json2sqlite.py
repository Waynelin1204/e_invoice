import os
import sqlite3
import json
import pandas as pd
import glob

# Path to the folder containing JSON files
downloads_folder = os.path.expanduser("/home/pi/Downloads/Json")
json_files = glob.glob(os.path.join(downloads_folder, "*.json"))  # Get all .json files in the folder

# Function to extract internalId after the 12th character and remove leading zeros
def extract_internal_id(internal_id):
    # From the 12th character onward (index 11)
    substring = internal_id[8:]  # Since indexing starts at 0, 11 is the 12th character
    # Remove leading zeros
    return substring.lstrip('0')

# Connect to SQLite database
conn = sqlite3.connect("/home/pi/mydjango/e_invoice/db.sqlite3")
cursor = conn.cursor()

# Create table if not exists (fixed table name spelling)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS e_invoices_myinvoiceportal (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        submissionUid TEXT,
        longId TEXT,
        internalId TEXT,
        typeName TEXT,
        typeVersionName TEXT,
        issuerTin TEXT,
        issuerName TEXT,
        receiverId TEXT,
        receiverName TEXT,
        dateTimeIssued TEXT,
        dateTimeReceived TEXT,
        dateTimeValidated TEXT,
        totalPayableAmount REAL,
        totalExcludingTax REAL,
        totalDiscount REAL,
        totalNetAmount REAL,
        status TEXT,
        cancelDateTime TEXT,
        rejectRequestDateTime TEXT, 
        documentStatusReason TEXT,
        createdByUserId TEXT
    )
""")
conn.commit()

# Process each JSON file
for json_file_path in json_files:
    print(f"Processing file: {json_file_path}")
    
    # Load JSON data
    with open(json_file_path, "r", encoding="utf-8") as file:
        json_data = json.load(file)

    # Process JSON data (Fixed variable name)
    documents = json_data["documentSummary"]

    # Convert JSON data to pandas DataFrame
    df = pd.DataFrame(documents)

    # Apply the extraction function to internalId column
    df['internalId'] = df['internalId'].apply(extract_internal_id)

    # Insert DataFrame into SQLite
    for index, row in df.iterrows():
        cursor.execute(''' 
            INSERT INTO e_invoices_myinvoiceportal (
                submissionUid, longId, internalId, typeName, typeVersionName, issuerTin, issuerName, receiverId,
                receiverName, dateTimeIssued, dateTimeReceived, dateTimeValidated, totalPayableAmount,
                totalExcludingTax, totalDiscount, totalNetAmount, status, cancelDateTime,
                rejectRequestDateTime, documentStatusReason, createdByUserId
            ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            row["submissionUid"], row["longId"], row["internalId"], row["typeName"],
            row["typeVersionName"], row["issuerTin"], row["issuerName"], row["receiverId"],
            row["receiverName"], row["dateTimeIssued"], row["dateTimeReceived"], row["dateTimeValidated"],
            row["totalPayableAmount"], row["totalExcludingTax"], row["totalDiscount"], row["totalNetAmount"],
            row["status"], row.get("cancelDateTime"), row.get("rejectRequestDateTime"),
            row.get("documentStatusReason"), row["createdByUserId"]
        ))

conn.commit()
conn.close()

print("All data from JSON files have been successfully inserted into the database!")
