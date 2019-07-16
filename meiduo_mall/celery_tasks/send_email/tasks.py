from celery_tasks.main import app
from django.core.mail import send_mail
from meiduo_mall import settings
from apps.users.utils import generate_active_url


# subject, message, from_email, recipient_list,html_message=None

@app.task
def send_active_email(email, id):
    # subject, 主题
    subject = '美多商场激活邮件'
    #  message,    邮件内容
    message = ''
    #  from_email,  发件人
    from_email = settings.EMAIL_FROM
    #  recipient_list 收件人列表
    recipient_list = [email]

    verify_url = generate_active_url(id)
    html_message = '<p>尊敬的用户您好！</p>' \
                   '<p>感谢您使用美多商城。</p>' \
                   '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                   '<p><a href="%s">%s<a></p>' % (email, verify_url, verify_url)

    send_mail(subject, message, from_email, recipient_list, html_message=html_message)
