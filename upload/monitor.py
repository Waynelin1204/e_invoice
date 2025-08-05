import requests

def send_telegram_message(bot_token, chat_id, message):
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }
    response = requests.post(url, data=payload)
    return response.status_code

if __name__ == "__main__":
# 用法示例
    BOT_TOKEN = "7809574209:AAFv-ARQqS0rhxchrs7_QFcdfsvLUC-jyoM"  # 從 BotFather 拿的
    CHAT_ID = "7985487049"  # 或是 -987654321（群組）
    send_telegram_message(BOT_TOKEN, CHAT_ID, "✅ 伺服器狀態正常！")

