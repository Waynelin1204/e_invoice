import os
import xml.etree.ElementTree as ET
import lxml.etree as LET
from lxml import etree
from xml.dom import minidom
from e_invoices.models import NumberDistribution, SystemConfig, CompanyNotificationConfig

def generate_E0402_xml(period):
    # 找出每個 company_identifier 的號碼段資料（假設 company_identifier + period 唯一）
    distributions = NumberDistribution.objects.filter(period=period, status='available')
    sysconf = SystemConfig.objects.first()
    E0402_XSD_path = sysconf.E0402_XSD_path

    with open(E0402_XSD_path, 'rb') as f:
        schema_doc = LET.parse(f)
        schema = LET.XMLSchema(schema_doc)

    if not distributions.exists():
        print("查無資料，不產生 XML。")
        return

    # 對每個不同 company_identifier 建立一個 XML
    company_groups = {}
    for dist in distributions:
        company_identifier = dist.company.company_identifier
        if company_identifier not in company_groups:
            company_groups[company_identifier] = dist  # 只取一筆資料代表該公司

    for company_identifier, dist in company_groups.items():
        ns = "urn:GEINV:eInvoiceMessage:E0402:4.1"  # 正確 namespace
        root = LET.Element("BranchTrackBlank", nsmap={None: ns})  # 正確根元素名稱與 namespace

        main = LET.SubElement(root, "Main")
        LET.SubElement(main, "HeadBan").text = company_identifier
        LET.SubElement(main, "BranchBan").text = company_identifier
        LET.SubElement(main, "InvoiceType").text = dist.invoice_type.zfill(2)
        LET.SubElement(main, "YearMonth").text = period
        LET.SubElement(main, "InvoiceTrack").text = dist.initial_char
        details = LET.SubElement(root, "Details")
        item = LET.SubElement(details, "BranchTrackBlankItem")
        LET.SubElement(item, "InvoiceBeginNo").text = str(dist.current_number).zfill(8)
        LET.SubElement(item, "InvoiceEndNo").text = str(dist.end_number).zfill(8)
        # 美化輸出
        xml_str = LET.tostring(root, encoding='utf-8')
        parsed = minidom.parseString(xml_str)
        pretty_xml = parsed.toprettyxml(indent="  ", encoding='utf-8')

        config = CompanyNotificationConfig.objects.filter(company__company_identifier=company_identifier).first()
        output_dir_E0401 = config.output_dir_E0401

        # Convert XML tree to bytes
        xml_bytes = LET.tostring(root, encoding="utf-8", xml_declaration=True, pretty_print=True)

        # Validate XML against schema
        doc = LET.fromstring(xml_bytes)
        if not schema.validate(doc):
            errors = "\n".join([str(e) for e in schema.error_log])
            raise ValueError(f"XSD validation failed:\n{errors}")

        # Write validated XML to file
        filename = f"F0402_{company_identifier}_{period}.xml"
        full_path = os.path.join(output_dir_E0401, filename)
        with open(full_path, "wb") as f:
            f.write(xml_bytes)
        dist.status = "uploaded"
        dist.save()
        
        # 檔名包含公司統編
        #filename = f"E0401_{company_identifier}_{period}.xml"
        #full_path = os.path.join(output_dir_E0401, filename)

        #with open(full_path, "wb") as f:
        #    f.write(pretty_xml)

        print(f"E0401 XML 已產出：{full_path}")

