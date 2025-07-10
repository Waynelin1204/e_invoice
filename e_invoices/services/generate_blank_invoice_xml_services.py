import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
from e_invoices.models import NumberDistribution

def generate_e0401_xml(output_path, period):
    # 找出每個 company_identifier 的號碼段資料（假設 company_identifier + period 唯一）
    distributions = NumberDistribution.objects.filter(period=period)

    if not distributions.exists():
        print("查無資料，不產生 XML。")
        return

    # 對每個不同 company_identifier 建立一個 XML
    company_groups = {}
    for dist in distributions:
        company_id = dist.company.company_identifier
        if company_id not in company_groups:
            company_groups[company_id] = dist  # 只取一筆資料代表該公司

    for company_id, dist in company_groups.items():
        ns = "urn:GEINV:eInvoiceMessage:E0401:4.0"
        root = ET.Element("BranchTrackBlank", xmlns=ns)

        main = ET.SubElement(root, "Main")
        ET.SubElement(main, "HeadBan").text = company_id
        ET.SubElement(main, "BranchBan").text = company_id
        ET.SubElement(main, "InvoiceType").text = dist.invoice_type.zfill(2)
        ET.SubElement(main, "YearMonth").text = period
        ET.SubElement(main, "InvoiceTrack").text = dist.initial_char

        details = ET.SubElement(root, "Details")
        item = ET.SubElement(details, "BranchTrackBlankItem")
        ET.SubElement(item, "InvoiceBeginNo").text = str(dist.current_number).zfill(8)
        ET.SubElement(item, "InvoiceEndNo").text = str(dist.end_number).zfill(8)

        # 美化輸出
        xml_str = ET.tostring(root, encoding='utf-8')
        parsed = minidom.parseString(xml_str)
        pretty_xml = parsed.toprettyxml(indent="  ", encoding='utf-8')

        # 檔名包含公司統編
        filename = f"E0401_{company_id}_{period}.xml"
        full_path = os.path.join(output_path, filename)

        with open(full_path, "wb") as f:
            f.write(pretty_xml)

        print(f"E0401 XML 已產出：{full_path}")

