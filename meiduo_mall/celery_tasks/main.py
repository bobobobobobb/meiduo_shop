from celery import Celery

# 加载django的配置文件
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_mall.settings")

app = Celery('celery_tasks')

# 加载配置文件
app.config_from_object('celery_tasks.config')

# 设置自动监听任务
app.autodiscover_tasks(['celery_tasks.sms'])
