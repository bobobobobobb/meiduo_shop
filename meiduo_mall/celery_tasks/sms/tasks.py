from celery_tasks.main import app
from libs.yuntongxun.sms import CCP


@app.task
def send_sms(mobile, message):
    CCP().send_template_sms(mobile, [message, 5], 1)

