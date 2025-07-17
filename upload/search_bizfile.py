
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv

def search_company_names(company_names, output_file="bizfile_results.csv"):
    # 初始化 Chrome 瀏覽器
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get("https://www.bizfile.gov.sg/")

    # 點選 eServices > Buy Information > Business Profile (Free)
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "search-box"))
        )
    except:
        print("❌ 無法加載搜尋框，請確認網頁結構未改變。")
        driver.quit()
        return

    results = []

    for name in company_names:
        try:
            search_box = driver.find_element(By.ID, "search-box")
            search_box.clear()
            search_box.send_keys(name)
            search_box.send_keys(Keys.RETURN)

            # 等待結果載入
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "card-container"))
            )

            # 抓取第一筆結果
            card = driver.find_element(By.CLASS_NAME, "card-container")
            entity_name = card.find_element(By.CLASS_NAME, "entity-name").text
            entity_number = card.find_element(By.CLASS_NAME, "uen").text
            entity_status = card.find_element(By.CLASS_NAME, "status").text

            results.append({
                "search": name,
                "name": entity_name,
                "number": entity_number,
                "status": entity_status
            })

            print(f"✅ 查詢 {name} 成功：{entity_name}")
            time.sleep(3)

        except Exception as e:
            print(f"⚠️ 查詢 {name} 失敗：{e}")
            results.append({"search": name, "name": "", "number": "", "status": ""})
            time.sleep(3)

    driver.quit()

    # 儲存結果為 CSV
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["search", "name", "number", "status"])
        writer.writeheader()
        writer.writerows(results)

    print(f"📄 結果已儲存為 {output_file}")

if __name__ == "__main__":
    sample_companies = [
        "Advantech Co. Singapore Pte Ltd",
        "SingTel",
        "DBS Bank Ltd",
        "Shopee Singapore"
    ]
    search_company_names(sample_companies)
