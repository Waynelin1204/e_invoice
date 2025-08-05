import os
import django
import xml.etree.ElementTree as ET
from e_invoices.models import Invoice
from datetime import datetime

# Set the settings module and initialize Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'e_invoice.settinigs'  # Update with your project name
django.setup()

# Define XML namespaces
namespaces = {
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "cac": "urn:pagero:CommonAggregateComponents:1.0",
    "default": "urn:pagero:PageroUniversalFormat:Invoice:1.0"
}

# Path to XML file in Downloads folder
downloads_folder = os.path.expanduser("/home/pi/Downloads")
xml_file_path = os.path.join(downloads_folder, "PUF_singapore_Invoice.xml")  # Replace with actual file name

# Read and parse XML file
with open(xml_file_path, "r", encoding="utf-8") as file:
    xml_data = file.read()

# Parse XML
root = ET.fromstring(xml_data)

# Extract values
document_id = root.find("cbc:ID", namespaces).text  # Invoice ID

# Print extracted data
print(f"Invoice ID: {document_id}")


# Convert issue_date to proper format (YYYY-MM-DD)
formatted_date = datetime.strptime(issue_date, "%Y-%m-%d").date()

# Save data to SQLite using Django ORM
invoice, created = Invoice.objects.get_or_create(
    document_id=document_id,
    defaults={
    }
)

if created:
    print("New record added!")
else:
    print("Record already exists.")
