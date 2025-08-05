# e_invoice/celery.py
import os
from celery import Celery

# 設定 Django 預設的 settings 模組
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "e_invoice.settings")

# 建立 Celery app
app = Celery("e_invoice")

# 從 Django settings.py 讀取 CELERY_ 開頭的設定
app.config_from_object("django.conf:settings", namespace="CELERY")

# 自動從已註冊的 Django app 中尋找 tasks.py
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
